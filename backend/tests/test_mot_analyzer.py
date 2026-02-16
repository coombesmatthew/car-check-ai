"""Tests for the MOT Analyzer service."""

import pytest
from app.services.mot.analyzer import MOTAnalyzer


@pytest.fixture
def analyzer():
    return MOTAnalyzer()


def _make_test(date, odometer, result="PASSED", defects=None):
    """Helper to build a mock MOT test entry."""
    test = {
        "completedDate": date,
        "odometerValue": str(odometer),
        "odometerUnit": "mi",
        "testResult": result,
    }
    if defects:
        test["defects"] = defects
    return test


def _make_vehicle(tests, registration="AB12CDE", make="FORD", model="FIESTA"):
    """Helper to build a mock MOT API response (list of vehicles)."""
    return [{
        "registration": registration,
        "make": make,
        "model": model,
        "firstUsedDate": "2015.01.01",
        "motTests": tests,
    }]


class TestClockingDetection:
    def test_no_data_returns_unknown(self, analyzer):
        result = analyzer.analyze(None)
        assert result["clocking_analysis"]["risk_level"] == "unknown"
        assert result["clocking_analysis"]["clocked"] is False

    def test_single_test_insufficient_data(self, analyzer):
        tests = [_make_test("2023-01-15", 50000)]
        result = analyzer.analyze(_make_vehicle(tests))
        assert result["clocking_analysis"]["risk_level"] == "unknown"

    def test_normal_mileage_no_flags(self, analyzer):
        tests = [
            _make_test("2020-01-15", 30000),
            _make_test("2021-01-20", 37000),
            _make_test("2022-01-18", 44000),
            _make_test("2023-01-22", 51000),
        ]
        result = analyzer.analyze(_make_vehicle(tests))
        clocking = result["clocking_analysis"]
        assert clocking["clocked"] is False
        assert clocking["risk_level"] == "none"
        assert len(clocking["flags"]) == 0

    def test_mileage_drop_detected(self, analyzer):
        tests = [
            _make_test("2020-01-15", 50000),
            _make_test("2021-01-20", 60000),
            _make_test("2022-01-18", 45000),  # Dropped!
        ]
        result = analyzer.analyze(_make_vehicle(tests))
        clocking = result["clocking_analysis"]
        assert clocking["clocked"] is True
        assert clocking["risk_level"] == "high"
        high_flags = [f for f in clocking["flags"] if f["type"] == "mileage_drop"]
        assert len(high_flags) == 1
        assert high_flags[0]["drop_amount"] == 15000

    def test_improbable_jump_flagged(self, analyzer):
        tests = [
            _make_test("2022-01-15", 30000),
            _make_test("2022-07-15", 60000),  # 60k annualised in 6 months
        ]
        result = analyzer.analyze(_make_vehicle(tests))
        clocking = result["clocking_analysis"]
        flags = [f for f in clocking["flags"] if f["type"] == "improbable_jump"]
        assert len(flags) == 1
        assert flags[0]["severity"] == "medium"

    def test_suspiciously_low_mileage(self, analyzer):
        tests = [
            _make_test("2015-01-15", 10001),
            _make_test("2023-01-15", 11000),  # ~125 miles/year over 8 years
        ]
        result = analyzer.analyze(_make_vehicle(tests))
        clocking = result["clocking_analysis"]
        low_flags = [f for f in clocking["flags"] if f["type"] == "suspiciously_low"]
        assert len(low_flags) == 1

    def test_multiple_medium_flags_gives_medium_risk(self, analyzer):
        tests = [
            _make_test("2020-01-15", 10000),
            _make_test("2020-07-15", 40000),  # improbable jump
            _make_test("2021-01-15", 50000),
            _make_test("2021-07-15", 80000),  # another improbable jump
        ]
        result = analyzer.analyze(_make_vehicle(tests))
        clocking = result["clocking_analysis"]
        assert clocking["risk_level"] == "medium"
        assert clocking["clocked"] is False


class TestConditionScoring:
    def test_clean_history_with_enough_data(self, analyzer):
        """Car with 3+ clean MOTs, normal mileage scores high."""
        tests = [
            _make_test("2020-01-15", 22000),
            _make_test("2021-01-15", 29000),
            _make_test("2022-01-15", 36000),
            _make_test("2023-01-15", 43000),
        ]
        result = analyzer.analyze(_make_vehicle(tests))
        assert result["condition_score"] == 100

    def test_two_clean_tests_capped_at_92(self, analyzer):
        """Only 2 tests means insufficient history; capped at 92."""
        tests = [
            _make_test("2022-01-15", 30000),
            _make_test("2023-01-15", 37000),
        ]
        result = analyzer.analyze(_make_vehicle(tests))
        assert result["condition_score"] == 92

    def test_single_test_capped_at_85(self, analyzer):
        """Only 1 clean test caps at 85 due to limited history."""
        tests = [
            _make_test("2023-01-15", 37000),
        ]
        result = analyzer.analyze(_make_vehicle(tests))
        assert result["condition_score"] == 85

    def test_advisory_on_single_test(self, analyzer):
        """Single test with advisory: -3 deduction, but capped at 85 anyway."""
        tests = [
            _make_test("2023-01-15", 37000, defects=[
                {"type": "ADVISORY", "text": "Tyre slightly worn"},
            ]),
        ]
        result = analyzer.analyze(_make_vehicle(tests))
        # 100 - 3 = 97, but capped at 85 for single test
        assert result["condition_score"] == 85

    def test_major_defect_on_single_test(self, analyzer):
        """Single test with MAJOR defect: -15 defect, -5 mileage factor."""
        tests = [
            _make_test("2023-01-15", 37000, defects=[
                {"type": "MAJOR", "text": "Brake disc worn below minimum"},
            ]),
        ]
        result = analyzer.analyze(_make_vehicle(tests))
        # 100 - 15 (MAJOR) - 5 (37k vs 22.2k expected = 1.67x, >150%) = 80
        # Cap at 85 doesn't help since 80 < 85
        assert result["condition_score"] == 80

    def test_dangerous_defect_heavy_penalty(self, analyzer):
        """Single test with DANGEROUS defect: -25 defect, -5 mileage factor."""
        tests = [
            _make_test("2023-01-15", 37000, defects=[
                {"type": "DANGEROUS", "text": "Steering rack loose"},
            ]),
        ]
        result = analyzer.analyze(_make_vehicle(tests))
        # 100 - 25 (DANGEROUS) - 5 (37k vs 22.2k expected = 1.67x, >150%) = 70
        assert result["condition_score"] == 70

    def test_score_floor_at_zero(self, analyzer):
        """Multiple DANGEROUS defects cannot go below 0."""
        tests = [
            _make_test("2023-01-15", 37000, defects=[
                {"type": "DANGEROUS", "text": "Issue 1"},
                {"type": "DANGEROUS", "text": "Issue 2"},
                {"type": "DANGEROUS", "text": "Issue 3"},
                {"type": "DANGEROUS", "text": "Issue 4"},
            ]),
        ]
        result = analyzer.analyze(_make_vehicle(tests))
        assert result["condition_score"] == 0

    def test_old_defects_still_counted_at_reduced_weight(self, analyzer):
        """Old tests contribute at 30% weight, not ignored entirely."""
        old_test = _make_test("2018-01-15", 10000, defects=[
            {"type": "DANGEROUS", "text": "Old dangerous issue"},
        ])
        recent_tests = [
            _make_test("2021-01-15", 30000),
            _make_test("2022-01-15", 37000),
            _make_test("2023-01-15", 44000),
        ]
        result = analyzer.analyze(_make_vehicle([old_test] + recent_tests))
        # Old DANGEROUS at 30% weight: -25 * 0.3 = -7.5, round(92.5) = 92
        assert result["condition_score"] == 92

    def test_failure_rate_deduction(self, analyzer):
        """Each FAILED test deducts 8 points."""
        tests = [
            _make_test("2020-01-15", 22000, "FAILED", defects=[
                {"type": "MAJOR", "text": "Brake issue"},
            ]),
            _make_test("2020-02-15", 22000),  # retest pass
            _make_test("2021-01-15", 29000),
            _make_test("2022-01-15", 36000),
            _make_test("2023-01-15", 43000),
        ]
        result = analyzer.analyze(_make_vehicle(tests))
        # 100 - (15 * 0.3 for old MAJOR) - 8 (1 failure) = 100 - 4.5 - 8 = 87.5 -> 88
        assert result["condition_score"] == 88

    def test_high_mileage_deduction(self, analyzer):
        """Car with >200% expected mileage gets -10 deduction."""
        # First MOT ~ 3 years old, so estimated age at latest = 3 + 3 = 6 years
        # Expected mileage: 6 * 7400 = 44,400
        # Actual: 100,000 -> ratio = 2.25 -> -10 deduction
        tests = [
            _make_test("2020-01-15", 60000),
            _make_test("2021-01-15", 75000),
            _make_test("2022-01-15", 88000),
            _make_test("2023-01-15", 100000),
        ]
        result = analyzer.analyze(_make_vehicle(tests))
        # 100 - 10 (high mileage) = 90
        assert result["condition_score"] == 90

    def test_advisory_trend_deteriorating(self, analyzer):
        """Increasing advisories over last 3 tests deducts 5 points."""
        tests = [
            _make_test("2020-01-15", 22000, defects=[
                {"type": "ADVISORY", "text": "Slight wear"},
            ]),
            _make_test("2021-01-15", 29000, defects=[
                {"type": "ADVISORY", "text": "Wear A"},
                {"type": "ADVISORY", "text": "Wear B"},
            ]),
            _make_test("2022-01-15", 36000, defects=[
                {"type": "ADVISORY", "text": "Wear A"},
                {"type": "ADVISORY", "text": "Wear B"},
                {"type": "ADVISORY", "text": "Wear C"},
            ]),
        ]
        result = analyzer.analyze(_make_vehicle(tests))
        # Defects: -3*1*0.6 + -3*2*0.8 + -3*3*1.0 = -1.8 -4.8 -9.0 = -15.6
        # Trend: -5 (deteriorating)
        # 100 - 15.6 - 5 = 79.4 -> 79
        assert result["condition_score"] == 79

    def test_advisory_trend_improving(self, analyzer):
        """Decreasing advisories over last 3 tests gives +3 bonus."""
        tests = [
            _make_test("2020-01-15", 22000, defects=[
                {"type": "ADVISORY", "text": "Wear A"},
                {"type": "ADVISORY", "text": "Wear B"},
                {"type": "ADVISORY", "text": "Wear C"},
            ]),
            _make_test("2021-01-15", 29000, defects=[
                {"type": "ADVISORY", "text": "Wear A"},
                {"type": "ADVISORY", "text": "Wear B"},
            ]),
            _make_test("2022-01-15", 36000, defects=[
                {"type": "ADVISORY", "text": "Wear A"},
            ]),
        ]
        result = analyzer.analyze(_make_vehicle(tests))
        # Defects: -3*3*0.6 + -3*2*0.8 + -3*1*1.0 = -5.4 -4.8 -3.0 = -13.2
        # Trend: +3 (improving)
        # 100 - 13.2 + 3 = 89.8 -> 90
        assert result["condition_score"] == 90


class TestFailurePatterns:
    def test_recurring_brake_issues(self, analyzer):
        tests = [
            _make_test("2020-01-15", 30000, "FAILED", defects=[
                {"type": "MAJOR", "text": "Brake pad worn below minimum"},
            ]),
            _make_test("2021-01-15", 37000, "FAILED", defects=[
                {"type": "MAJOR", "text": "Brake disc corroded"},
            ]),
            _make_test("2022-01-15", 44000, "PASSED", defects=[
                {"type": "ADVISORY", "text": "Brake hose slightly worn"},
            ]),
        ]
        result = analyzer.analyze(_make_vehicle(tests))
        patterns = result["failure_patterns"]
        brake_pattern = next((p for p in patterns if p["category"] == "brake"), None)
        assert brake_pattern is not None
        assert brake_pattern["occurrences"] == 3
        assert brake_pattern["concern_level"] == "medium"

    def test_no_patterns_when_clean(self, analyzer):
        tests = [
            _make_test("2021-01-15", 30000),
            _make_test("2022-01-15", 37000),
        ]
        result = analyzer.analyze(_make_vehicle(tests))
        assert result["failure_patterns"] == []

    def test_high_concern_at_4_plus(self, analyzer):
        tests = [
            _make_test(f"202{i}-01-15", 30000 + i * 7000, defects=[
                {"type": "ADVISORY", "text": "Tyre worn on edge"},
            ])
            for i in range(5)
        ]
        result = analyzer.analyze(_make_vehicle(tests))
        tyre_pattern = next((p for p in result["failure_patterns"] if p["category"] == "tyre"), None)
        assert tyre_pattern is not None
        assert tyre_pattern["concern_level"] == "high"


class TestMileageTimeline:
    def test_timeline_built_correctly(self, analyzer):
        tests = [
            _make_test("2021-01-15", 30000),
            _make_test("2022-01-15", 37000),
            _make_test("2023-01-15", 44000),
        ]
        result = analyzer.analyze(_make_vehicle(tests))
        timeline = result["mileage_timeline"]
        assert len(timeline) == 3
        assert timeline[0]["date"] == "2021-01-15"
        assert timeline[0]["miles"] == 30000
        assert timeline[2]["miles"] == 44000

    def test_timeline_skips_missing_odometer(self, analyzer):
        tests = [
            _make_test("2021-01-15", 30000),
            {"completedDate": "2022-01-15", "testResult": "PASSED"},  # No odometer
            _make_test("2023-01-15", 44000),
        ]
        result = analyzer.analyze(_make_vehicle(tests))
        assert len(result["mileage_timeline"]) == 2


class TestMOTSummary:
    def test_summary_counts(self, analyzer):
        tests = [
            _make_test("2020-01-15", 30000, "PASSED"),
            _make_test("2021-01-15", 37000, "FAILED"),
            _make_test("2021-02-01", 37050, "PASSED"),
            _make_test("2022-01-15", 44000, "PASSED"),
        ]
        result = analyzer.analyze(_make_vehicle(tests, make="BMW", model="320D"))
        summary = result["mot_summary"]
        assert summary["total_tests"] == 4
        assert summary["total_passes"] == 3
        assert summary["total_failures"] == 1
        assert summary["make"] == "BMW"
        assert summary["model"] == "320D"

    def test_summary_latest_test(self, analyzer):
        tests = [
            _make_test("2022-01-15", 44000, "PASSED"),
            _make_test("2023-06-20", 51000, "PASSED"),
        ]
        tests[-1]["expiryDate"] = "2024-06-19"
        result = analyzer.analyze(_make_vehicle(tests))
        summary = result["mot_summary"]
        assert summary["latest_test"]["date"] == "2023-06-20"
        assert summary["latest_test"]["result"] == "PASSED"
        assert summary["current_odometer"] == "51000"

    def test_no_tests_still_returns_summary(self, analyzer):
        data = [{"registration": "AB12CDE", "make": "FORD", "model": "FOCUS", "motTests": []}]
        result = analyzer.analyze(data)
        assert result["mot_summary"]["total_tests"] == 0
        assert result["mot_summary"]["make"] == "FORD"
