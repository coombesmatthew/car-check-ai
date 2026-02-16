"""Derived vehicle statistics calculator.

Computes useful statistics from existing DVLA + MOT data:
- Vehicle age
- Estimated annual mileage
- Days until MOT/tax expiry
- Total advisories and failures
- V5C ownership insights
"""

from typing import Optional, Dict, List
from datetime import datetime, date


def calculate_vehicle_stats(
    dvla_data: Optional[Dict],
    mot_tests: Optional[List[Dict]],
    mileage_timeline: Optional[List[Dict]],
) -> Dict:
    """Calculate derived statistics from existing data.

    Args:
        dvla_data: Raw DVLA VES response
        mot_tests: Sorted list of MOT test records (oldest first)
        mileage_timeline: Mileage readings [{date, miles, unit}]

    Returns:
        Dict with computed statistics.
    """
    stats: Dict = {}
    today = date.today()

    # Vehicle age
    if dvla_data:
        year = dvla_data.get("yearOfManufacture")
        if year:
            age = today.year - year
            stats["vehicle_age_years"] = age
            stats["year_of_manufacture"] = year

        # First registration date (from month of manufacture)
        month_reg = dvla_data.get("monthOfFirstRegistration")
        if month_reg:
            stats["first_registered"] = month_reg

    # Days until MOT expiry
    if dvla_data:
        mot_expiry = dvla_data.get("motExpiryDate")
        if mot_expiry:
            try:
                expiry = datetime.strptime(mot_expiry, "%Y-%m-%d").date()
                delta = (expiry - today).days
                stats["mot_expiry_date"] = mot_expiry
                stats["mot_days_remaining"] = delta
                if delta < 0:
                    stats["mot_status_detail"] = f"Expired {abs(delta)} days ago"
                elif delta == 0:
                    stats["mot_status_detail"] = "Expires today"
                elif delta <= 30:
                    stats["mot_status_detail"] = f"Expires in {delta} days"
                else:
                    stats["mot_status_detail"] = f"Valid for {delta} days"
            except (ValueError, TypeError):
                pass

    # Days until tax due
    if dvla_data:
        tax_due = dvla_data.get("taxDueDate")
        if tax_due:
            try:
                due = datetime.strptime(tax_due, "%Y-%m-%d").date()
                delta = (due - today).days
                stats["tax_due_date"] = tax_due
                stats["tax_days_remaining"] = delta
                if delta < 0:
                    stats["tax_status_detail"] = f"Expired {abs(delta)} days ago"
                elif delta == 0:
                    stats["tax_status_detail"] = "Due today"
                elif delta <= 30:
                    stats["tax_status_detail"] = f"Due in {delta} days"
                else:
                    stats["tax_status_detail"] = f"Valid for {delta} days"
            except (ValueError, TypeError):
                pass

    # V5C ownership insight
    if dvla_data:
        v5c_date = dvla_data.get("dateOfLastV5CIssued")
        if v5c_date:
            try:
                v5c = datetime.strptime(v5c_date, "%Y-%m-%d").date()
                days_since = (today - v5c).days
                stats["v5c_issued_date"] = v5c_date
                stats["v5c_days_since"] = days_since

                if days_since <= 90:
                    stats["v5c_insight"] = "V5C recently issued — may indicate recent ownership change"
                elif days_since <= 365:
                    stats["v5c_insight"] = f"V5C issued {days_since} days ago"
                else:
                    years = days_since // 365
                    stats["v5c_insight"] = f"V5C issued ~{years} year{'s' if years > 1 else ''} ago"
            except (ValueError, TypeError):
                pass

    # Estimated annual mileage from MOT readings
    if mileage_timeline and len(mileage_timeline) >= 2:
        first = mileage_timeline[0]
        last = mileage_timeline[-1]
        try:
            d_first = datetime.strptime(first["date"][:10], "%Y-%m-%d").date()
            d_last = datetime.strptime(last["date"][:10], "%Y-%m-%d").date()
            years = (d_last - d_first).days / 365.25
            if years > 0:
                total_miles = last["miles"] - first["miles"]
                annual_avg = total_miles / years
                stats["estimated_annual_mileage"] = round(annual_avg)
                stats["total_recorded_mileage"] = last["miles"]
                stats["mileage_readings_count"] = len(mileage_timeline)

                # Compare to UK average (7,400 miles/year)
                if annual_avg < 5000:
                    stats["mileage_assessment"] = "Below average mileage"
                elif annual_avg < 10000:
                    stats["mileage_assessment"] = "Average mileage"
                elif annual_avg < 15000:
                    stats["mileage_assessment"] = "Above average mileage"
                else:
                    stats["mileage_assessment"] = "High mileage"
        except (ValueError, TypeError, KeyError):
            pass

    # MOT defect totals
    if mot_tests:
        total_advisories = 0
        total_failures_items = 0
        total_dangerous = 0
        total_major = 0
        total_minor = 0

        for test in mot_tests:
            defects = test.get("defects", []) or test.get("rfrAndComments", [])
            for defect in defects:
                dtype = defect.get("type", "").upper()
                if dtype == "ADVISORY":
                    total_advisories += 1
                elif dtype == "DANGEROUS":
                    total_dangerous += 1
                elif dtype == "MAJOR":
                    total_major += 1
                elif dtype == "MINOR":
                    total_minor += 1
                total_failures_items += 1 if dtype in ("DANGEROUS", "MAJOR", "MINOR") else 0

        stats["total_advisory_items"] = total_advisories
        stats["total_failure_items"] = total_failures_items
        stats["total_dangerous_items"] = total_dangerous
        stats["total_major_items"] = total_major
        stats["total_minor_items"] = total_minor

    return stats
