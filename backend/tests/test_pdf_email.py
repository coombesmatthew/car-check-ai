"""Tests for PDF generation and email rendering services."""

from app.services.notification.email_sender import (
    render_report_email,
    _build_checks_summary,
    _score_colour,
)


SAMPLE_CHECK_DATA = {
    "registration": "DEMO1",
    "condition_score": 92,
    "vehicle": {
        "make": "FORD",
        "colour": "BLUE",
        "fuel_type": "PETROL",
        "year_of_manufacture": 2019,
        "mot_status": "Valid",
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


class TestBuildChecksSummary:
    def test_includes_stolen_pass(self):
        items = _build_checks_summary(SAMPLE_CHECK_DATA)
        labels = [i["label"] for i in items]
        assert "Not Stolen" in labels

    def test_includes_finance_pass(self):
        items = _build_checks_summary(SAMPLE_CHECK_DATA)
        labels = [i["label"] for i in items]
        assert "No Finance Outstanding" in labels

    def test_flags_stolen(self):
        data = {**SAMPLE_CHECK_DATA, "stolen_check": {"stolen": True, "data_source": "Demo"}}
        items = _build_checks_summary(data)
        stolen = next(i for i in items if i["label"] == "Reported Stolen")
        assert stolen["status"] == "fail"

    def test_flags_clocking(self):
        data = {
            **SAMPLE_CHECK_DATA,
            "clocking_analysis": {"clocked": True, "risk_level": "high"},
        }
        items = _build_checks_summary(data)
        clocked = next(i for i in items if i["label"] == "Mileage Discrepancy")
        assert clocked["status"] == "fail"


class TestScoreColour:
    def test_green(self):
        assert _score_colour(85) == "#059669"

    def test_amber(self):
        assert _score_colour(60) == "#f59e0b"

    def test_red(self):
        assert _score_colour(30) == "#dc2626"

    def test_none(self):
        assert _score_colour(None) == "#64748b"


class TestRenderReportEmail:
    def test_renders_html(self):
        html = render_report_email(SAMPLE_CHECK_DATA, report_ref="CV-TEST-001")
        assert "VeriCar" in html
        assert "DEMO1" in html
        assert "FORD" in html
        assert "92" in html
