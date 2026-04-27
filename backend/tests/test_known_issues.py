# ruff: noqa: S101
# pyright: reportMissingImports=false
"""Tests for the known_issues service: parser, synthesiser, and repo round-trip.

The parser test relies on a real HonestJohn HTML capture that Wave 2 will
generate. Until that fixture exists, the parser test is skipped gracefully.

`S101` (assert used) is suppressed file-wide; pytest relies on assert.
`reportMissingImports` is disabled because the pre-commit hook runs pyright
against a temp copy of this file without the project's PYTHONPATH / venv.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Ensure required env vars exist before app imports (mirrors conftest.py).
os.environ.setdefault("DATABASE_URL", "postgresql://test:test@localhost:5432/test")
os.environ.setdefault("SECRET_KEY", "test-secret-key-xxx")

from app.core.config import settings
from app.services.known_issues import repo as repo_module
from app.services.known_issues.honestjohn_scraper import _parse_good_and_bad
from app.services.known_issues.models import (
    KnownIssue,
    KnownIssuesRecord,
    ScrapedPage,
    SourceCitation,
)
from app.services.known_issues.synthesiser import synthesise


FIXTURE_PATH = (
    Path(__file__).resolve().parent / "fixtures" / "honestjohn_focus_mk3.html"
)


CANNED_SYNTHESISER_JSON = {
    "make": "Ford",
    "model": "Focus",
    "generation": "Mk3",
    "years": "2011-2018",
    "top_issues": [
        {
            "title": "DPF blockages on diesel variants",
            "description": (
                "Short urban journeys can prevent DPF regeneration, leading to "
                "blocked filters that trigger warning lights and limp mode."
            ),
            "typical_symptoms": [
                "DPF warning light on dash",
                "reduced power (limp mode)",
                "excessive fuel use",
            ],
            "affected_years": [2011, 2012, 2013, 2014],
            "estimated_repair_cost_gbp_range": [800, 2500],
            "severity": "high",
            "source_citations": [
                {
                    "title": "HonestJohn Ford Focus 2011 Good & Bad",
                    "url": "https://www.honestjohn.co.uk/carbycar/ford/focus-2011/good-and-bad/",
                }
            ],
        },
        {
            "title": "Powershift dual-clutch transmission shudder",
            "description": (
                "The dry-clutch PowerShift gearbox is known for shuddering and "
                "jerky take-offs, particularly in traffic."
            ),
            "typical_symptoms": [
                "shuddering on pull-away",
                "jerky gear changes",
                "transmission warning",
            ],
            "affected_years": None,
            "estimated_repair_cost_gbp_range": [1500, 3000],
            "severity": "high",
            "source_citations": [
                {
                    "title": "HonestJohn Ford Focus 2011 Good & Bad",
                    "url": "https://www.honestjohn.co.uk/carbycar/ford/focus-2011/good-and-bad/",
                }
            ],
        },
        {
            "title": "Water ingress into front footwells",
            "description": (
                "Blocked pollen-filter drains allow rainwater into the cabin, "
                "soaking carpets and damaging electrics."
            ),
            "typical_symptoms": [
                "damp carpet in driver or passenger footwell",
                "musty smell",
                "electrical faults",
            ],
            "affected_years": None,
            "estimated_repair_cost_gbp_range": [150, 600],
            "severity": "medium",
            "source_citations": [
                {
                    "title": "HonestJohn Ford Focus 2011 Good & Bad",
                    "url": "https://www.honestjohn.co.uk/carbycar/ford/focus-2011/good-and-bad/",
                }
            ],
        },
    ],
    "overall_reliability_note": (
        "Broadly sound mechanically, but avoid the PowerShift automatic and "
        "watch for cabin water ingress."
    ),
    "last_updated": "2026-04-23T00:00:00+00:00",
    "sources": [
        {
            "title": "HonestJohn Ford Focus 2011 Good & Bad",
            "url": "https://www.honestjohn.co.uk/carbycar/ford/focus-2011/good-and-bad/",
        }
    ],
}


def _make_scraped_page() -> ScrapedPage:
    return ScrapedPage(
        url="https://www.honestjohn.co.uk/carbycar/ford/focus-2011/good-and-bad/",
        make="ford",
        model_slug="focus-mk3",
        title="Ford Focus 2011 - Good & Bad - Honest John",
        good_points=["Well-sorted chassis", "Composed ride"],
        bad_points=[
            "DPF issues on diesels",
            "PowerShift transmission shudders",
            "Water ingress into footwells",
        ],
        fetched_at=datetime.now(timezone.utc),
    )


# ---------------------------------------------------------------------------
# 1. Parser
# ---------------------------------------------------------------------------


def test_parser_extracts_bad_points():
    """Parse a real HonestJohn HTML capture; skip until Wave 2 captures it."""
    if not FIXTURE_PATH.exists():
        pytest.skip(
            "fixture not yet captured; run backend/scripts/build_known_issues.py "
            "to generate it"
        )

    html = FIXTURE_PATH.read_text(encoding="utf-8")
    url = "https://www.honestjohn.co.uk/carbycar/ford/focus-2011/good-and-bad/"
    result = _parse_good_and_bad(html, url=url, make="ford", model_slug="focus-mk3")

    assert isinstance(result, ScrapedPage)
    assert result.title, "expected non-empty title from HonestJohn HTML"
    assert len(result.bad_points) >= 3, (
        f"expected >=3 bad_points, got {len(result.bad_points)}: {result.bad_points}"
    )
    assert result.url == url


# ---------------------------------------------------------------------------
# 2. Synthesiser happy path
# ---------------------------------------------------------------------------


@patch("app.services.known_issues.synthesiser.anthropic.Anthropic")
def test_synthesiser_returns_valid_record(mock_anthropic_class, monkeypatch):
    monkeypatch.setattr(settings, "ANTHROPIC_API_KEY", "sk-ant-test-key")

    mock_message = MagicMock()
    mock_message.content = [MagicMock(text=json.dumps(CANNED_SYNTHESISER_JSON))]
    mock_client = MagicMock()
    mock_client.messages.create.return_value = mock_message
    mock_anthropic_class.return_value = mock_client

    scraped = _make_scraped_page()
    result = synthesise(scraped)

    assert result is not None, "synthesise() returned None on valid canned input"
    assert isinstance(result, KnownIssuesRecord)
    assert result.make == "Ford"
    assert len(result.top_issues) == 3
    assert result.top_issues[0].severity == "high"

    # Verify the exact call parameters to Claude
    mock_client.messages.create.assert_called_once()
    call_kwargs = mock_client.messages.create.call_args.kwargs
    assert call_kwargs["model"] == settings.ANTHROPIC_MODEL
    assert call_kwargs["temperature"] == 0.2
    assert call_kwargs["max_tokens"] == 2048
    assert "messages" in call_kwargs
    assert "system" in call_kwargs


# ---------------------------------------------------------------------------
# 3. Synthesiser handles malformed JSON
# ---------------------------------------------------------------------------


@patch("app.services.known_issues.synthesiser.anthropic.Anthropic")
def test_synthesiser_handles_bad_json(mock_anthropic_class, monkeypatch):
    monkeypatch.setattr(settings, "ANTHROPIC_API_KEY", "sk-ant-test-key")

    mock_message = MagicMock()
    mock_message.content = [MagicMock(text="this is not json {{{ ")]
    mock_client = MagicMock()
    mock_client.messages.create.return_value = mock_message
    mock_anthropic_class.return_value = mock_client

    result = synthesise(_make_scraped_page())
    assert result is None


# ---------------------------------------------------------------------------
# 4. Synthesiser refuses when API key missing
# ---------------------------------------------------------------------------


def test_synthesiser_refuses_without_api_key(monkeypatch):
    monkeypatch.setattr(settings, "ANTHROPIC_API_KEY", "")
    result = synthesise(_make_scraped_page())
    assert result is None


# ---------------------------------------------------------------------------
# 5. Repo round-trip
# ---------------------------------------------------------------------------


def test_repo_round_trip(tmp_path, monkeypatch):
    monkeypatch.setattr(repo_module, "DATA_DIR", tmp_path)

    record = KnownIssuesRecord(
        make="Ford",
        model="Focus",
        generation="Mk3",
        years="2011-2018",
        top_issues=[
            KnownIssue(
                title="DPF blockages",
                description="Short journeys prevent regen.",
                typical_symptoms=["limp mode"],
                affected_years=[2011, 2012],
                estimated_repair_cost_gbp_range=(800, 2500),
                severity="high",
                source_citations=[
                    SourceCitation(
                        title="HJ Focus", url="https://example.test/focus"
                    )
                ],
            )
        ],
        overall_reliability_note="Broadly sound.",
        last_updated=datetime(2026, 4, 23, tzinfo=timezone.utc),
        sources=[
            SourceCitation(title="HJ Focus", url="https://example.test/focus")
        ],
    )

    path = repo_module.save_record(record, "focus-mk3")
    assert path.exists()
    assert path.parent == tmp_path

    loaded = repo_module.load_record("Ford", "focus-mk3")
    assert loaded is not None
    assert loaded.make == "Ford"
    assert loaded.top_issues[0].title == "DPF blockages"
