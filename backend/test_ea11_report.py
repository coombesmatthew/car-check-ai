#!/usr/bin/env python3
"""Test EA11OSE AI report generation and PDF rendering."""

import json
import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.ai.report_generator import generate_ai_report
from app.core.config import settings
from app.core.logging import logger


async def main():
    """Generate and render a PDF report for EA11OSE."""

    # Load the EA11OSE test data
    fixture_path = Path(__file__).parent / "fixtures" / "EA11OSE_FULL_CHECK.json"
    with open(fixture_path) as f:
        check_data = json.load(f)

    # Prepare data for report generation
    registration = check_data["registration"]
    vehicle_data = {
        "registrationNumber": registration,
        "make": check_data["vehicle_summary"]["make"],
        "model": check_data["vehicle_summary"]["model"],
        "yearOfManufacture": check_data["vehicle_summary"]["year"],
        "fuelType": check_data["vehicle_summary"]["fuel"],
        "co2Emissions": check_data["vehicle_summary"]["co2_emissions_g_km"],
        "engineCapacity": check_data["vehicle_summary"]["engine_cc"],
        "colour": check_data["vehicle_summary"]["colour"],
        "taxStatus": check_data["registration_info"]["tax_status"],
        "taxDueDate": check_data["registration_info"]["tax_due_date"],
        "motStatus": check_data["registration_info"]["mot_status"],
        "motExpiryDate": check_data["registration_info"]["mot_expiry_date"],
    }

    # Simulate MOT analysis
    mot_analysis = {
        "mot_summary": {
            "registration": registration,
            "total_tests": check_data["mot_history"]["total_tests"],
            "total_passes": check_data["mot_history"]["total_passes"],
            "total_failures": check_data["mot_history"]["total_failures"],
            "current_odometer": check_data["mot_history"]["latest_test"]["odometer"],
            "first_used_date": check_data["mot_history"]["first_used_date"],
            "latest_test": check_data["mot_history"]["latest_test"],
        },
        "clocking_analysis": check_data.get("clocking_analysis", {
            "clocked": False,
            "risk_level": "low",
            "reason": "Mileage is below average for age",
        }),
        "mileage_timeline": check_data.get("mileage_timeline", []),
        "failure_patterns": check_data.get("failure_patterns", []),
        "condition_score": check_data.get("condition_score", 80),
        "mot_tests": check_data.get("mot_tests_full", []),
    }

    # Simulate ULEZ data
    ulez_data = {
        "compliant": True,
        "status": "Compliant",
        "reason": f"Euro 5 diesel vehicle: passes ULEZ in all zones",
    }

    # Simulate check result
    check_result = {
        "registration": registration,
        "tier": "premium",
        "vehicle": vehicle_data,
        "mot_summary": mot_analysis["mot_summary"],
        "tax_calculation": {
            "band": "B",
            "band_range": "101-110 g/km",
            "co2_emissions": check_data["vehicle_summary"]["co2_emissions_g_km"],
            "fuel_type": check_data["vehicle_summary"]["fuel"],
            "first_year_rate": 20,
            "annual_rate": 20,
            "six_month_rate": 10.0,
            "monthly_total": 20.0,
            "is_electric": False,
            "is_diesel": True,
            "tax_regime": "Pre-April 2017",
            "year_of_manufacture": check_data["vehicle_summary"]["year"],
        },
        "valuation": {
            "private_sale": check_data["premium_tier_data"]["brego_valuation"]["retail_average"],
            "dealer_forecourt": check_data["premium_tier_data"]["brego_valuation"]["retail_high"],
            "trade_in": check_data["premium_tier_data"]["brego_valuation"]["trade_average"],
            "part_exchange": check_data["premium_tier_data"]["brego_valuation"]["trade_high"],
            "valuation_date": check_data["premium_tier_data"]["brego_valuation"]["valuation_date"],
            "mileage_used": check_data["premium_tier_data"]["brego_valuation"]["current_mileage"],
            "condition": "Mileage-adjusted",
            "data_source": "Brego",
        },
        "keeper_history": {
            "total_keepers": check_data["premium_tier_data"]["experian_autocheck"].get("keeper_count", 1),
            "keepers": [],
        },
    }

    # Generate AI report
    logger.info("Generating AI report for EA11OSE...")
    report_markdown = await generate_ai_report(
        registration=registration,
        vehicle_data=vehicle_data,
        mot_analysis=mot_analysis,
        ulez_data=ulez_data,
        check_result=check_result,
        listing_price=None,
        listing_url=None,
    )

    if not report_markdown:
        logger.error("Failed to generate AI report")
        return

    # Save markdown report
    md_output = Path(__file__).parent / "EA11OSE_REPORT.md"
    with open(md_output, "w") as f:
        f.write(report_markdown)
    logger.info(f"✓ Markdown report saved: {md_output}")

    logger.info("=" * 60)
    logger.info("EA11OSE Report Generated Successfully!")
    logger.info("=" * 60)
    logger.info(f"Markdown: {md_output}")
    logger.info("PDF rendering is handled by generate_ea11_pdf.py")


if __name__ == "__main__":
    asyncio.run(main())
