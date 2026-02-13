from typing import List, Dict, Optional
from datetime import datetime

from app.core.logging import logger

# Severity weights for condition scoring (out of 100)
SEVERITY_WEIGHTS = {
    "DANGEROUS": -30,
    "MAJOR": -15,
    "MINOR": -5,
    "ADVISORY": -2,
}

# Average annual mileage in UK is ~7,400 miles
UK_AVG_ANNUAL_MILEAGE = 7400
# Reasonable max annual mileage before flagging
MAX_REASONABLE_ANNUAL_MILEAGE = 30000


class MOTAnalyzer:
    """Analyzes MOT test history for mileage anomalies and vehicle condition."""

    def analyze(self, mot_data: Optional[Dict]) -> Dict:
        """Run full analysis on MOT data.

        Args:
            mot_data: Raw MOT API response (list with vehicle + motTests)

        Returns:
            Dict with clocking_analysis, condition_score, mileage_timeline,
            failure_patterns, and mot_summary.
        """
        if not mot_data:
            return self._empty_result()

        # MOT API returns a list; take first vehicle entry
        vehicle = mot_data[0] if isinstance(mot_data, list) else mot_data
        tests = vehicle.get("motTests", [])

        if not tests:
            return {
                **self._empty_result(),
                "mot_summary": self._build_summary(vehicle, []),
            }

        # Sort tests chronologically (oldest first)
        sorted_tests = sorted(tests, key=lambda t: t.get("completedDate", ""))

        clocking = self._detect_clocking(sorted_tests)
        mileage_timeline = self._build_mileage_timeline(sorted_tests)
        condition_score = self._calculate_condition_score(sorted_tests)
        failure_patterns = self._analyze_failure_patterns(sorted_tests)
        mot_summary = self._build_summary(vehicle, sorted_tests)

        return {
            "clocking_analysis": clocking,
            "condition_score": condition_score,
            "mileage_timeline": mileage_timeline,
            "failure_patterns": failure_patterns,
            "mot_summary": mot_summary,
        }

    def _empty_result(self) -> Dict:
        return {
            "clocking_analysis": {
                "clocked": False,
                "risk_level": "unknown",
                "flags": [],
            },
            "condition_score": None,
            "mileage_timeline": [],
            "failure_patterns": [],
            "mot_summary": None,
        }

    def _detect_clocking(self, tests: List[Dict]) -> Dict:
        """Enhanced mileage anomaly detection.

        Checks for:
        1. Mileage drops between tests
        2. Improbable jumps (>30k miles/year)
        3. Significantly below average mileage (potential rollback)
        4. Inconsistent patterns
        """
        flags = []
        readings = []

        for test in tests:
            odometer = test.get("odometerValue")
            if odometer is None:
                continue
            try:
                miles = int(odometer)
            except (ValueError, TypeError):
                continue
            readings.append({
                "date": test["completedDate"],
                "miles": miles,
                "test_result": test.get("testResult", ""),
            })

        if len(readings) < 2:
            return {
                "clocked": False,
                "risk_level": "unknown",
                "reason": "Insufficient MOT history for mileage analysis",
                "flags": [],
            }

        # Check for mileage drops
        for i in range(len(readings) - 1):
            current = readings[i]
            next_r = readings[i + 1]

            if next_r["miles"] < current["miles"]:
                drop = current["miles"] - next_r["miles"]
                flags.append({
                    "type": "mileage_drop",
                    "severity": "high",
                    "detail": (
                        f"Mileage dropped from {current['miles']:,} to "
                        f"{next_r['miles']:,} ({drop:,} mile drop)"
                    ),
                    "from_date": current["date"],
                    "to_date": next_r["date"],
                    "drop_amount": drop,
                })

        # Check for improbable jumps
        for i in range(len(readings) - 1):
            current = readings[i]
            next_r = readings[i + 1]

            try:
                date_a = datetime.strptime(current["date"][:10], "%Y-%m-%d")
                date_b = datetime.strptime(next_r["date"][:10], "%Y-%m-%d")
            except (ValueError, TypeError):
                continue

            days = (date_b - date_a).days
            if days <= 0:
                continue

            annual_rate = (next_r["miles"] - current["miles"]) / (days / 365.25)
            if annual_rate > MAX_REASONABLE_ANNUAL_MILEAGE:
                flags.append({
                    "type": "improbable_jump",
                    "severity": "medium",
                    "detail": (
                        f"Mileage increased by {next_r['miles'] - current['miles']:,} miles "
                        f"in {days} days (~{annual_rate:,.0f} miles/year annualised)"
                    ),
                    "from_date": current["date"],
                    "to_date": next_r["date"],
                })

        # Check overall average vs UK norms
        if len(readings) >= 2:
            first, last = readings[0], readings[-1]
            try:
                d_first = datetime.strptime(first["date"][:10], "%Y-%m-%d")
                d_last = datetime.strptime(last["date"][:10], "%Y-%m-%d")
                years = (d_last - d_first).days / 365.25
                if years > 0:
                    avg_annual = (last["miles"] - first["miles"]) / years
                    if avg_annual < UK_AVG_ANNUAL_MILEAGE * 0.3 and last["miles"] > 10000:
                        flags.append({
                            "type": "suspiciously_low",
                            "severity": "low",
                            "detail": (
                                f"Average {avg_annual:,.0f} miles/year is well below "
                                f"UK average of {UK_AVG_ANNUAL_MILEAGE:,} miles/year"
                            ),
                        })
            except (ValueError, TypeError):
                pass

        # Determine overall risk
        high_flags = [f for f in flags if f["severity"] == "high"]
        med_flags = [f for f in flags if f["severity"] == "medium"]

        if high_flags:
            risk_level = "high"
            clocked = True
        elif len(med_flags) >= 2:
            risk_level = "medium"
            clocked = False
        elif med_flags or [f for f in flags if f["severity"] == "low"]:
            risk_level = "low"
            clocked = False
        else:
            risk_level = "none"
            clocked = False

        return {
            "clocked": clocked,
            "risk_level": risk_level,
            "flags": flags,
        }

    def _build_mileage_timeline(self, tests: List[Dict]) -> List[Dict]:
        """Extract chronological mileage timeline from MOT tests."""
        timeline = []
        for test in tests:
            odometer = test.get("odometerValue")
            if odometer is None:
                continue
            try:
                miles = int(odometer)
            except (ValueError, TypeError):
                continue
            timeline.append({
                "date": test.get("completedDate", "")[:10],
                "miles": miles,
                "unit": test.get("odometerUnit", "mi"),
            })
        return timeline

    def _calculate_condition_score(self, tests: List[Dict]) -> int:
        """Calculate vehicle condition score (0-100) from MOT defect history.

        Weights: DANGEROUS(-30), MAJOR(-15), MINOR(-5), ADVISORY(-2).
        Only considers defects from the last 3 tests to reflect current condition.
        """
        score = 100
        recent_tests = tests[-3:] if len(tests) >= 3 else tests

        for test in recent_tests:
            defects = test.get("defects", [])
            if not defects:
                # Also check rfrAndComments for older API format
                defects = test.get("rfrAndComments", [])

            for defect in defects:
                severity = defect.get("type", "").upper()
                weight = SEVERITY_WEIGHTS.get(severity, 0)
                score += weight

        return max(0, min(100, score))

    def _analyze_failure_patterns(self, tests: List[Dict]) -> List[Dict]:
        """Identify recurring failure patterns across MOT history."""
        category_counts: Dict[str, int] = {}
        all_defects = []

        for test in tests:
            defects = test.get("defects", []) or test.get("rfrAndComments", [])
            for defect in defects:
                text = defect.get("text", defect.get("comment", ""))
                severity = defect.get("type", "ADVISORY").upper()
                all_defects.append({
                    "text": text,
                    "severity": severity,
                    "date": test.get("completedDate", "")[:10],
                })

                # Simple category extraction from defect text
                text_lower = text.lower()
                for category in [
                    "brake", "tyre", "suspension", "lighting", "exhaust",
                    "steering", "corrosion", "rust", "emission", "windscreen",
                    "seatbelt", "horn", "mirror",
                ]:
                    if category in text_lower:
                        category_counts[category] = category_counts.get(category, 0) + 1
                        break

        patterns = []
        for category, count in sorted(category_counts.items(), key=lambda x: -x[1]):
            if count >= 2:
                patterns.append({
                    "category": category,
                    "occurrences": count,
                    "concern_level": "high" if count >= 4 else "medium" if count >= 2 else "low",
                })

        return patterns

    def _build_summary(self, vehicle: Dict, tests: List[Dict]) -> Dict:
        """Build a concise MOT summary."""
        latest_test = tests[-1] if tests else None

        summary = {
            "total_tests": len(tests),
            "total_passes": sum(1 for t in tests if t.get("testResult") == "PASSED"),
            "total_failures": sum(1 for t in tests if t.get("testResult") == "FAILED"),
            "registration": vehicle.get("registration"),
            "make": vehicle.get("make"),
            "model": vehicle.get("model"),
            "first_used_date": vehicle.get("firstUsedDate"),
        }

        if latest_test:
            summary["latest_test"] = {
                "date": latest_test.get("completedDate", "")[:10],
                "result": latest_test.get("testResult"),
                "odometer": latest_test.get("odometerValue"),
                "expiry_date": latest_test.get("expiryDate"),
            }
            summary["current_odometer"] = latest_test.get("odometerValue")

        return summary
