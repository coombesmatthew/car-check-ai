"""Tests for PDF generation and email rendering services."""

import pytest
from app.services.report.pdf_generator import _parse_ai_sections, _extract_verdict
from app.services.notification.email_sender import (
    render_report_email,
    _build_key_findings,
    _score_colour,
    _verdict_bg,
)

# Sample AI report text
SAMPLE_REPORT = """## Vehicle Summary
This 2019 Ford Fiesta is a **clean vehicle** with 42,000 miles.

## Condition Assessment
The vehicle is in **good condition** with a score of 92/100.

## Mileage Verdict
Mileage readings show a **consistent upward trend**.

## Risk Factors
- No significant risk factors identified

## Recommendation
**BUY** — This vehicle presents well with a clean history.

## Negotiation Points
- Check comparable listings to ensure fair pricing
"""

SAMPLE_CHECK_DATA = {
    "registration": "DEMO1",
    "condition_score": 92,
    "vehicle": {
        "make": "FORD",
        "colour": "BLUE",
        "fuel_type": "PETROL",
        "year_of_manufacture": 2019,
    },
    "mot_summary": {
        "total_tests": 4,
        "total_passes": 4,
        "total_failures": 0,
        "model": "FIESTA",
    },
    "clocking_analysis": {
        "clocked": False,
        "risk_level": "none",
    },
    "ulez_compliance": {
        "compliant": True,
    },
    "failure_patterns": [],
    "finance_check": {
        "finance_outstanding": False,
        "record_count": 0,
        "records": [],
        "data_source": "Demo",
    },
    "stolen_check": {
        "stolen": False,
        "data_source": "Demo",
    },
    "write_off_check": {
        "written_off": False,
        "record_count": 0,
        "records": [],
        "data_source": "Demo",
    },
    "plate_changes": {
        "changes_found": False,
        "record_count": 0,
        "records": [],
        "data_source": "Demo",
    },
    "valuation": {
        "private_sale": 8500,
        "dealer_forecourt": 9995,
        "trade_in": 7200,
        "part_exchange": 7500,
        "valuation_date": "2026-02-13",
        "mileage_used": 42000,
        "condition": "Good",
        "data_source": "Demo",
    },
}


class TestParseAISections:
    def test_parses_sections(self):
        sections = _parse_ai_sections(SAMPLE_REPORT)
        assert len(sections) == 6
        assert sections[0]["title"] == "Vehicle Summary"
        assert sections[1]["title"] == "Condition Assessment"
        assert sections[4]["title"] == "Recommendation"

    def test_converts_bold_to_html(self):
        sections = _parse_ai_sections(SAMPLE_REPORT)
        assert "<strong>" in sections[0]["content"]

    def test_converts_list_items(self):
        sections = _parse_ai_sections(SAMPLE_REPORT)
        # Risk Factors section has bullet points
        risk_section = sections[3]
        assert "<li>" in risk_section["content"]

    def test_empty_returns_empty(self):
        assert _parse_ai_sections("") == []
        assert _parse_ai_sections(None) == []


class TestExtractVerdict:
    def test_extracts_buy(self):
        assert _extract_verdict("**BUY** — Good vehicle") == "BUY"

    def test_extracts_avoid(self):
        assert _extract_verdict("**AVOID** — Stay away") == "AVOID"

    def test_extracts_negotiate(self):
        assert _extract_verdict("**NEGOTIATE** — Room for discount") == "NEGOTIATE"

    def test_none_for_empty(self):
        assert _extract_verdict("") is None
        assert _extract_verdict(None) is None

    def test_none_for_no_verdict(self):
        assert _extract_verdict("This is just a normal report.") is None


class TestBuildKeyFindings:
    def test_good_score(self):
        findings = _build_key_findings(SAMPLE_CHECK_DATA, "BUY")
        texts = [f["text"] for f in findings]
        assert any("92/100" in t for t in texts)
        assert any("Good condition" in t for t in texts)

    def test_clocking_clean(self):
        findings = _build_key_findings(SAMPLE_CHECK_DATA, "BUY")
        texts = [f["text"] for f in findings]
        assert any("no clocking" in t.lower() for t in texts)

    def test_bad_score(self):
        data = {**SAMPLE_CHECK_DATA, "condition_score": 35}
        findings = _build_key_findings(data, "AVOID")
        texts = [f["text"] for f in findings]
        assert any("Poor condition" in t for t in texts)

    def test_clocked_vehicle(self):
        data = {
            **SAMPLE_CHECK_DATA,
            "clocking_analysis": {"clocked": True, "risk_level": "high"},
        }
        findings = _build_key_findings(data, "AVOID")
        texts = [f["text"] for f in findings]
        assert any("clocking" in t.lower() for t in texts)

    def test_capped_at_six(self):
        data = {
            **SAMPLE_CHECK_DATA,
            "failure_patterns": [
                {"category": "brakes", "occurrences": 3},
                {"category": "tyres", "occurrences": 2},
                {"category": "exhaust", "occurrences": 2},
                {"category": "lights", "occurrences": 2},
            ],
        }
        findings = _build_key_findings(data, "NEGOTIATE")
        assert len(findings) <= 6


class TestScoreColour:
    def test_green(self):
        assert _score_colour(85) == "#059669"

    def test_amber(self):
        assert _score_colour(60) == "#f59e0b"

    def test_red(self):
        assert _score_colour(30) == "#dc2626"

    def test_none(self):
        assert _score_colour(None) == "#64748b"


class TestVerdictBg:
    def test_buy(self):
        assert _verdict_bg("BUY") == "#059669"

    def test_avoid(self):
        assert _verdict_bg("AVOID") == "#dc2626"

    def test_negotiate(self):
        assert _verdict_bg("NEGOTIATE") == "#f59e0b"

    def test_none(self):
        assert _verdict_bg(None) == "#64748b"


class TestRenderReportEmail:
    def test_renders_html(self):
        html = render_report_email(SAMPLE_CHECK_DATA, "BUY", "CV-TEST-001")
        assert "VeriCar" in html
        assert "DEMO1" in html
        assert "FORD" in html
        assert "92" in html

    def test_includes_verdict(self):
        html = render_report_email(SAMPLE_CHECK_DATA, "BUY", "CV-TEST-001")
        assert "BUY" in html

    def test_no_verdict(self):
        html = render_report_email(SAMPLE_CHECK_DATA, None, "CV-TEST-001")
        assert "VeriCar" in html
