#!/usr/bin/env python3
"""Generate EA11OSE PDF report using the professional VeriCar template."""

import json
import sys
from pathlib import Path
from datetime import datetime

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.report.pdf_generator import generate_pdf
from app.core.logging import logger


def main():
    """Generate PDF report for EA11OSE using AI-generated markdown."""

    # Load the EA11OSE test data
    fixture_path = Path(__file__).parent / "fixtures" / "EA11OSE_FULL_CHECK.json"
    with open(fixture_path) as f:
        check_data_fixture = json.load(f)

    # Load the AI-generated markdown report
    report_path = Path(__file__).parent / "EA11OSE_REPORT.md"
    with open(report_path) as f:
        ai_report = f.read()

    # Construct the check_data dict in the format expected by generate_pdf()
    registration = check_data_fixture["registration"]
    vehicle_summary = check_data_fixture["vehicle_summary"]
    registration_info = check_data_fixture["registration_info"]
    mot_history = check_data_fixture["mot_history"]
    brego = check_data_fixture["premium_tier_data"]["brego_valuation"]
    experian = check_data_fixture["premium_tier_data"]["experian_autocheck"]
    carguide = check_data_fixture["premium_tier_data"]["carguide_salvage"]

    # Calculate MOT days remaining
    mot_expiry = datetime.strptime(registration_info["mot_expiry_date"], "%Y-%m-%d")
    today = datetime.today()
    mot_days_remaining = (mot_expiry - today).days

    check_data = {
        "registration": registration,
        "tier": "basic",
        "vehicle": {
            "registration": registration,
            "make": vehicle_summary["make"],
            "model": vehicle_summary["model"],
            "year_of_manufacture": vehicle_summary["year"],
            "fuel_type": vehicle_summary["fuel"],
            "colour": vehicle_summary["colour"],
            "engine_capacity": vehicle_summary["engine_cc"],
            "co2_emissions": vehicle_summary["co2_emissions_g_km"],
            "mot_status": registration_info["mot_status"],
            "tax_status": registration_info["tax_status"],
        },
        "mot_summary": {
            "make": vehicle_summary["make"],
            "model": vehicle_summary["model"],
            "registration": registration,
            "total_tests": mot_history["total_tests"],
            "total_passes": mot_history["total_passes"],
            "total_failures": mot_history["total_failures"],
        },
        "mot_tests": check_data_fixture.get("mot_tests_full", []),
        "clocking_analysis": check_data_fixture.get("clocking_analysis", {
            "clocked": False,
            "risk_level": "low",
        }),
        "condition_score": check_data_fixture.get("condition_score", 80),
        "mileage_timeline": check_data_fixture.get("mileage_timeline", []),
        "failure_patterns": check_data_fixture.get("failure_patterns", []),
        "ulez_compliance": {
            "compliant": True,
            "status": "Compliant",
        },
        "tax_calculation": {
            "annual_rate": 20.0,
        },
        "vehicle_stats": {
            "mot_days_remaining": mot_days_remaining,
            "vehicle_age_years": check_data_fixture["vehicle_stats"]["age_years"],
            "estimated_annual_mileage": check_data_fixture["vehicle_stats"]["annual_mileage_avg"],
            "total_recorded_mileage": check_data_fixture["vehicle_stats"]["total_mileage"],
            "mileage_assessment": check_data_fixture["vehicle_stats"]["mileage_assessment"],
            "mot_status_detail": f"Valid until {registration_info.get('mot_expiry_date')}",
            "tax_status_detail": registration_info.get("tax_status"),
            "total_advisory_items": mot_history["latest_test"]["advisories"],
            "total_failure_items": mot_history["total_failures"],
        },
        # Provenance checks (premium tier - simulated for this test)
        "stolen_check": {
            "stolen": experian.get("stolen", False),
            "record_count": 0,
        },
        "finance_check": {
            "finance_outstanding": experian.get("finance_outstanding", False),
            "record_count": experian.get("finance_records", 0),
        },
        "write_off_check": {
            "written_off": experian.get("write_off", False),
            "records": [],
        },
        "salvage_check": {
            "salvage_found": carguide.get("salvage_found", False),
            "records": [],
        },
        "valuation": {
            "private_sale": brego.get("retail_average"),
            "dealer_forecourt": brego.get("retail_high"),
            "trade_in": brego.get("trade_average"),
            "part_exchange": brego.get("trade_high"),
            "condition": "Mileage-adjusted",
            "mileage_used": brego.get("current_mileage"),
            "valuation_date": brego.get("valuation_date"),
        },
    }

    logger.info(f"Generating PDF report for {registration}...")
    pdf_bytes = generate_pdf(check_data=check_data, ai_report=ai_report)

    # Save PDF with version number
    output_dir = Path(__file__).parent

    # Find next version number
    existing = list(output_dir.glob("EA11OSE_REPORT_v*.pdf"))
    if existing:
        latest_version = max([int(f.stem.split('_v')[-1]) for f in existing if '_v' in f.stem])
        next_version = latest_version + 1
    else:
        next_version = 2

    output_path = output_dir / f"EA11OSE_REPORT_v{next_version}.pdf"
    with open(output_path, "wb") as f:
        f.write(pdf_bytes)

    logger.info(f"✓ PDF report saved: {output_path} ({len(pdf_bytes)} bytes)")
    print(f"✓ PDF report saved: {output_path}")

    # Also copy to Downloads
    downloads_path = Path.home() / "Downloads" / f"EA11OSE_REPORT_v{next_version}.pdf"
    import shutil
    shutil.copy(output_path, downloads_path)
    print(f"✓ Copied to Downloads: {downloads_path}")


if __name__ == "__main__":
    main()
