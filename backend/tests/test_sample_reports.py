"""Tests for the public /api/v1/checks/sample endpoint and fixture validity.

These tests guarantee:
  1. The endpoint serves clean and risks variants without auth.
  2. The fixtures parse cleanly into the FreeCheckResponse Pydantic schema —
     so any future schema field that's missing from a fixture fails CI fast.
  3. The MINI fixture is properly scrubbed (no real customer reg).
"""
# ruff: noqa: S101, ANN001, ANN201, D103, INP001, E501

from __future__ import annotations

from pathlib import Path

from app.schemas.check import FreeCheckResponse
from app.schemas.ev import EVCheckResponse
from app.services.data.sample_reports import (
    available_variants,
    get_sample_report,
)

_FIXTURE_DIR = Path(__file__).parent.parent / "app" / "services" / "data" / "sample_reports"


def test_sample_endpoint_clean_returns_populated_report(client):
    res = client.get("/api/v1/checks/sample?variant=clean")
    assert res.status_code == 200, res.text
    data = res.json()
    assert data["registration"] == "SAMPLE1"
    assert data["is_ev"] is False
    assert len(data["check_data"]["mot_tests"]) >= 10
    assert data["check_data"]["valuation"]["private_sale"] > 0


def test_sample_endpoint_risks_flags_finance_and_writeoff(client):
    res = client.get("/api/v1/checks/sample?variant=risks")
    assert res.status_code == 200, res.text
    cd = res.json()["check_data"]
    assert cd["finance_check"]["finance_outstanding"] is True
    assert cd["write_off_check"]["written_off"] is True
    assert cd["write_off_check"]["records"][0]["category"] == "S"
    assert cd["clocking_analysis"]["clocked"] is True
    assert cd["plate_changes"]["changes_found"] is True


def test_sample_endpoint_unknown_variant_400(client):
    res = client.get("/api/v1/checks/sample?variant=nope")
    assert res.status_code == 400


def test_sample_endpoint_default_variant_is_clean(client):
    res = client.get("/api/v1/checks/sample")
    assert res.status_code == 200
    assert res.json()["registration"] == "SAMPLE1"


def test_sample_returns_deep_copies():
    """Mutating one returned dict must not affect the next caller."""
    a = get_sample_report("clean")
    assert a is not None
    a["check_data"]["registration"] = "MUTATED"
    b = get_sample_report("clean")
    assert b is not None
    assert b["check_data"]["registration"] == "SAMPLE1"


def test_clean_fixture_does_not_leak_real_vrm():
    raw = (_FIXTURE_DIR / "clean_mini.json").read_text()
    assert "EA11OSE" not in raw, "Real customer VRM leaked into clean fixture"
    assert "CV-20260427-949F0344" not in raw, "Real report_ref leaked"


def test_fixtures_parse_into_pydantic_schema():
    """Catches schema drift — if a required field is added, fixtures missing
    it will fail here before they reach a customer."""
    for variant in ("clean", "risks"):
        data = get_sample_report(variant)
        assert data is not None, f"Fixture {variant} missing"
        FreeCheckResponse.model_validate(data["check_data"])

    ev = get_sample_report("ev")
    if ev is not None:
        EVCheckResponse.model_validate(ev["check_data"])


def test_ev_sample_has_battery_and_range_data(client):
    res = client.get("/api/v1/checks/sample?variant=ev")
    if res.status_code == 404:
        return
    assert res.status_code == 200, res.text
    data = res.json()
    assert data["is_ev"] is True
    cd = data["check_data"]
    assert cd["battery_health"]["score"] is not None
    assert cd["range_estimate"]["estimated_range_miles"] > 0
    assert cd["charging_costs"]["vs_petrol_annual_saving"] is not None


def test_available_variants_at_minimum():
    variants = available_variants()
    assert "clean" in variants
    assert "risks" in variants
