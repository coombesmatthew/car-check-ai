"""AI-powered vehicle report generator using Claude."""

from typing import Dict, Optional

import anthropic

from app.core.config import settings
from app.core.logging import logger


SYSTEM_PROMPT = """You are an expert used car analyst writing a report for a prospective buyer in the UK.
You have access to official DVLA and DVSA MOT data for the vehicle.

Write a clear, honest, and actionable buyer's report. Be direct about risks.
Use British English. Format with markdown headings and bullet points.

Structure your report as:
## Vehicle Summary
Brief 2-3 sentence overview of the vehicle.

## Condition Assessment
Analysis of the vehicle's current condition based on MOT history and defects.

## Mileage Verdict
Assessment of mileage patterns - whether they look normal, suspicious, or concerning.

## Risk Factors
Bullet list of specific concerns a buyer should be aware of.

## Recommendation
Clear buy/negotiate/avoid recommendation with reasoning.

## Negotiation Points
If applicable, specific points the buyer could use to negotiate on price.

Keep the report concise (300-500 words). Be helpful, not alarmist."""


async def generate_ai_report(
    registration: str,
    vehicle_data: Optional[Dict],
    mot_analysis: Dict,
    ulez_data: Optional[Dict],
    listing_price: Optional[int] = None,
    listing_url: Optional[str] = None,
) -> Optional[str]:
    """Generate an AI buyer's report using Claude.

    Args:
        registration: Vehicle registration number
        vehicle_data: DVLA VES API response
        mot_analysis: Analyzed MOT data (from MOTAnalyzer)
        ulez_data: ULEZ compliance data
        listing_price: Listed price in pence (optional)
        listing_url: URL of the listing (optional)

    Returns:
        Markdown-formatted report string, or None if generation fails.
    """
    if not settings.ANTHROPIC_API_KEY or settings.ANTHROPIC_API_KEY.startswith("your_"):
        logger.warning("Anthropic API key not configured")
        return None

    # Build the data context for Claude
    context_parts = [f"Vehicle Registration: {registration}"]

    if vehicle_data:
        context_parts.append(f"""
Vehicle Details (DVLA):
- Make: {vehicle_data.get('make', 'Unknown')}
- Colour: {vehicle_data.get('colour', 'Unknown')}
- Fuel Type: {vehicle_data.get('fuelType', 'Unknown')}
- Year: {vehicle_data.get('yearOfManufacture', 'Unknown')}
- Engine: {vehicle_data.get('engineCapacity', 'Unknown')}cc
- Euro Standard: {vehicle_data.get('euroStatus', 'Unknown')}
- Tax Status: {vehicle_data.get('taxStatus', 'Unknown')}
- MOT Status: {vehicle_data.get('motStatus', 'Unknown')}
- MOT Expiry: {vehicle_data.get('motExpiryDate', 'Unknown')}""")

    mot_summary = mot_analysis.get("mot_summary")
    if mot_summary:
        context_parts.append(f"""
MOT History Summary:
- Total Tests: {mot_summary.get('total_tests', 0)}
- Passes: {mot_summary.get('total_passes', 0)}
- Failures: {mot_summary.get('total_failures', 0)}
- Current Mileage: {mot_summary.get('current_odometer', 'Unknown')} miles""")

        latest = mot_summary.get("latest_test")
        if latest:
            context_parts.append(f"- Latest Test: {latest.get('date')} - {latest.get('result')}")

    clocking = mot_analysis.get("clocking_analysis", {})
    context_parts.append(f"""
Mileage Analysis:
- Clocking Detected: {clocking.get('clocked', False)}
- Risk Level: {clocking.get('risk_level', 'unknown')}""")

    flags = clocking.get("flags", [])
    if flags:
        context_parts.append("- Flags:")
        for flag in flags:
            context_parts.append(f"  - [{flag.get('severity', '').upper()}] {flag.get('detail', '')}")

    condition = mot_analysis.get("condition_score")
    if condition is not None:
        context_parts.append(f"\nCondition Score: {condition}/100")

    patterns = mot_analysis.get("failure_patterns", [])
    if patterns:
        context_parts.append("\nRecurring Failure Patterns:")
        for p in patterns:
            context_parts.append(f"  - {p['category']}: {p['occurrences']}x ({p['concern_level']} concern)")

    if ulez_data:
        context_parts.append(f"""
ULEZ Compliance:
- Status: {ulez_data.get('status', 'unknown')}
- Compliant: {ulez_data.get('compliant', 'Unknown')}""")
        if ulez_data.get("daily_charge"):
            context_parts.append(f"- Daily Charge: {ulez_data['daily_charge']}")

    if listing_price:
        context_parts.append(f"\nListing Price: £{listing_price / 100:,.2f}")
    if listing_url:
        context_parts.append(f"Listing URL: {listing_url}")

    user_message = "\n".join(context_parts)
    user_message += "\n\nPlease write a buyer's report for this vehicle based on the data above."

    try:
        client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

        message = client.messages.create(
            model=settings.ANTHROPIC_MODEL,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_message}],
        )

        report = message.content[0].text
        logger.info(f"AI report generated for {registration} ({message.usage.input_tokens}+{message.usage.output_tokens} tokens)")
        return report

    except anthropic.APIError as e:
        logger.error(f"Anthropic API error: {e}")
        return None
    except Exception as e:
        logger.error(f"AI report generation failed: {e}")
        return None
