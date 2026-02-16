"""AI-powered vehicle report generator using Claude."""

from typing import Dict, Optional

import anthropic

from app.core.config import settings
from app.core.logging import logger


REPAIR_COST_ESTIMATES = {
    "brake": {"component": "Brake pads/discs", "low": 100, "high": 350, "per": "per axle"},
    "tyre": {"component": "Tyre replacement", "low": 50, "high": 120, "per": "each"},
    "suspension": {"component": "Suspension repair", "low": 150, "high": 400, "per": "per corner"},
    "exhaust": {"component": "Exhaust repair", "low": 100, "high": 500, "per": ""},
    "emission": {"component": "Emissions system", "low": 200, "high": 1500, "per": ""},
    "lighting": {"component": "Lighting repair", "low": 30, "high": 200, "per": ""},
    "steering": {"component": "Steering repair", "low": 200, "high": 600, "per": ""},
    "corrosion": {"component": "Corrosion treatment", "low": 200, "high": 1000, "per": ""},
    "windscreen": {"component": "Windscreen repair/replace", "low": 50, "high": 400, "per": ""},
}


def _estimate_repair_cost(category: str) -> Optional[Dict]:
    """Look up estimated repair cost for a defect category."""
    cat_lower = category.lower()
    for key, estimate in REPAIR_COST_ESTIMATES.items():
        if key in cat_lower:
            return estimate
    return None


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

## Estimated Repair Costs
For each recurring issue or recent advisory/failure, provide estimated repair cost ranges in GBP. Use realistic UK garage prices:
- Brake pads replacement: £100-£200 per axle
- Brake disc replacement: £150-£350 per axle
- Tyre replacement: £50-£120 each
- Suspension arm/ball joint: £150-£400
- Exhaust repair/replacement: £100-£500
- DPF cleaning/replacement: £300-£1,500
- Clutch replacement: £400-£800
- Steering rack: £300-£600
- Corrosion repair: £200-£1,000+

## 12-Month Cost Forecast
Based on the vehicle's MOT advisory patterns and age, estimate likely maintenance costs for the next 12 months. Include:
- Predicted repairs based on recurring advisories approaching failure
- Annual service cost estimate
- MOT test fee (£54.85)
- Road tax (if available from data)

## Questions to Ask the Seller
Generate 5-7 specific questions based on THIS car's data. Examples:
- If suspension advisory: "Has the suspension been inspected since the last MOT? Have you had quotes for the [specific part]?"
- If recent V5C: "When did you buy the car? Why is the V5C so recent?"
- If high mileage: "What kind of driving has this car done — mostly motorway or urban?"
- If ULEZ non-compliant: "Are you aware this car isn't compliant with [specific zone]?"

## Recommendation
Clear **BUY** / **NEGOTIATE** / **AVOID** verdict with reasoning.

## Negotiation Script
If verdict is NEGOTIATE or BUY with issues:
- Provide a specific step-by-step negotiation approach
- Include exact pound amounts to reference
- Example: "The recurring brake advisories suggest £200-350 in upcoming costs. Combined with the [X], I'd suggest offering £[price - discount] rather than the asking price of £[price]."

Keep the report detailed and actionable (600-1000 words). Be helpful, not alarmist. The buyer is paying for this report — give them genuine value they can't get from reading the free data cards."""


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
        logger.warning("Anthropic API key not configured — using demo report")
        return _generate_demo_report(
            registration, vehicle_data, mot_analysis, ulez_data, listing_price
        )

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
            max_tokens=2048,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_message}],
        )

        report = message.content[0].text
        logger.info(f"AI report generated for {registration} ({message.usage.input_tokens}+{message.usage.output_tokens} tokens)")
        return report

    except anthropic.APIError as e:
        logger.error(f"Anthropic API error: {e}")
        # Fall back to demo report on API errors (e.g. no credits)
        logger.info("Falling back to demo report after API error")
        return _generate_demo_report(
            registration, vehicle_data, mot_analysis, ulez_data, listing_price
        )
    except Exception as e:
        logger.error(f"AI report generation failed: {e}")
        return None


def _generate_demo_report(
    registration: str,
    vehicle_data: Optional[Dict],
    mot_analysis: Dict,
    ulez_data: Optional[Dict],
    listing_price: Optional[int] = None,
) -> str:
    """Generate a realistic demo report when Anthropic API key is not configured."""
    make = vehicle_data.get("make", "Unknown") if vehicle_data else "Unknown"
    colour = vehicle_data.get("colour", "Unknown") if vehicle_data else "Unknown"
    fuel = vehicle_data.get("fuelType", "Unknown") if vehicle_data else "Unknown"
    year = vehicle_data.get("yearOfManufacture", "Unknown") if vehicle_data else "Unknown"
    engine = vehicle_data.get("engineCapacity") if vehicle_data else None
    tax_status = vehicle_data.get("taxStatus", "Unknown") if vehicle_data else "Unknown"

    mot_summary = mot_analysis.get("mot_summary", {})
    total_tests = mot_summary.get("total_tests", 0)
    total_passes = mot_summary.get("total_passes", 0)
    total_failures = mot_summary.get("total_failures", 0)
    current_mileage = mot_summary.get("current_odometer", "Unknown")

    clocking = mot_analysis.get("clocking_analysis", {})
    clocked = clocking.get("clocked", False)
    risk_level = clocking.get("risk_level", "unknown")
    condition = mot_analysis.get("condition_score")
    patterns = mot_analysis.get("failure_patterns", [])

    compliant = ulez_data.get("compliant", None) if ulez_data else None
    ulez_status = ulez_data.get("status", "unknown") if ulez_data else "unknown"
    daily_charge = ulez_data.get("daily_charge") if ulez_data else None

    # Determine verdict
    if clocked:
        verdict = "AVOID"
        verdict_reasoning = "Mileage discrepancies have been detected in this vehicle's history, which is a serious red flag. The risk of hidden mechanical wear from true (higher) mileage makes this vehicle unpredictable to own."
    elif condition and condition < 50:
        verdict = "AVOID"
        verdict_reasoning = "The vehicle's condition score is concerning, with significant MOT issues that suggest expensive repairs ahead."
    elif total_failures > 2 or (condition and condition < 75):
        verdict = "NEGOTIATE"
        verdict_reasoning = "The vehicle has issues that should be reflected in the price. Use the repair cost estimates below as ammunition."
    else:
        verdict = "BUY"
        verdict_reasoning = "This vehicle presents well with a clean history and no major concerns."

    engine_str = f"{engine}cc " if engine else ""

    # --- Build repair cost estimates ---
    repair_lines = []
    total_repair_low = 0
    total_repair_high = 0
    for p in patterns:
        estimate = _estimate_repair_cost(p["category"])
        if estimate:
            repair_lines.append(
                f"- **{estimate['component']}**: £{estimate['low']}-£{estimate['high']}"
                + (f" {estimate['per']}" if estimate['per'] else "")
                + f" — flagged {p['occurrences']} times in MOT history ({p['concern_level']} concern)"
            )
            total_repair_low += estimate["low"]
            total_repair_high += estimate["high"]
        else:
            # Generic estimate for unknown categories
            repair_lines.append(
                f"- **{p['category'].title()} repair**: £100-£400"
                f" — flagged {p['occurrences']} times in MOT history ({p['concern_level']} concern)"
            )
            total_repair_low += 100
            total_repair_high += 400

    # --- Build 12-month cost forecast ---
    service_cost_low = 150
    service_cost_high = 300
    mot_fee = 54.85
    # Estimate annual repairs from patterns approaching failure
    annual_repair_low = int(total_repair_low * 0.6)  # 60% chance of needing repair
    annual_repair_high = int(total_repair_high * 0.8)

    forecast_total_low = service_cost_low + mot_fee + annual_repair_low
    forecast_total_high = service_cost_high + mot_fee + annual_repair_high

    # --- Build seller questions ---
    seller_questions = []
    if clocked:
        seller_questions.append(
            '"Can you provide the full service history with stamped mileage records? '
            'I\'ve noticed discrepancies in the MOT mileage readings."'
        )
    if patterns:
        top_pattern = patterns[0]
        seller_questions.append(
            f'"The MOT history shows recurring {top_pattern["category"]} issues '
            f'({top_pattern["occurrences"]} times). Has any work been done on the '
            f'{top_pattern["category"]} since the last MOT?"'
        )
    if total_failures > 1:
        seller_questions.append(
            f'"The car has failed {total_failures} MOT tests. '
            'Can you tell me what repairs were carried out after each failure?"'
        )
    if current_mileage != "Unknown":
        try:
            miles = int(current_mileage)
            if miles > 80000:
                seller_questions.append(
                    '"With over 80,000 miles on the clock, has the timing belt/chain been replaced? '
                    'What about the clutch?"'
                )
            seller_questions.append(
                f'"What kind of driving has this car mostly done — motorway, urban, or mixed? '
                f'The current mileage of {current_mileage} miles suggests '
                f'{"higher" if miles > 60000 else "moderate"} usage."'
            )
        except (ValueError, TypeError):
            seller_questions.append(
                '"What kind of driving has this car mostly done — motorway, urban, or mixed?"'
            )
    if compliant is False:
        zone_name = "London ULEZ" if ulez_status == "non_compliant" else "UK clean air zones"
        seller_questions.append(
            f'"Are you aware this car isn\'t compliant with {zone_name}? '
            f'Has this affected how you\'ve used it?"'
        )
    if vehicle_data and vehicle_data.get("dateOfLastV5CIssued"):
        seller_questions.append(
            '"When did you purchase this car? I can see the V5C was issued on '
            f'{vehicle_data["dateOfLastV5CIssued"]}. How many previous owners has it had?"'
        )
    # Ensure we have at least 5 questions
    generic_questions = [
        '"Do you have receipts for any recent work — servicing, tyres, brakes?"',
        '"Is there any outstanding finance on the vehicle?"',
        '"Has the car ever been involved in an accident or had bodywork repairs?"',
        '"Why are you selling? How long have you owned it?"',
        '"Are there any known faults or warning lights currently showing?"',
    ]
    for q in generic_questions:
        if len(seller_questions) >= 7:
            break
        if q not in seller_questions:
            seller_questions.append(q)

    # --- Assemble report ---
    report = f"""## Vehicle Summary
This {year} {make.title()} is a {colour.lower()} {engine_str}{fuel.lower()} vehicle currently showing {current_mileage} miles on the clock. It has undergone {total_tests} MOT test{'s' if total_tests != 1 else ''} with a {total_passes}/{total_tests} pass rate, and its overall condition score stands at {condition}/100.

## Condition Assessment
"""
    if condition and condition >= 80:
        report += f"The vehicle is in **good condition** with a score of {condition}/100. "
        if total_failures == 0:
            report += "It has never failed an MOT, which is a positive sign of good maintenance. "
        else:
            report += f"It has had {total_failures} MOT failure{'s' if total_failures != 1 else ''}, but has since passed. "
        report += "Recent MOT tests show only minor advisories, suggesting the car has been reasonably well looked after.\n"
    elif condition and condition >= 50:
        report += f"The vehicle's condition score of {condition}/100 is **moderate**. "
        report += f"With {total_failures} MOT failure{'s' if total_failures != 1 else ''} on record, there are signs of wear that a buyer should factor into their decision. "
        report += "A pre-purchase inspection is recommended.\n"
    else:
        report += f"The condition score of {condition}/100 is **concerning**. "
        report += f"The vehicle has failed {total_failures} MOT test{'s' if total_failures != 1 else ''} and shows signs of significant wear. "
        report += "A thorough independent inspection is essential before purchase.\n"

    report += "\n## Mileage Verdict\n"
    if clocked:
        flags = clocking.get("flags", [])
        report += "**WARNING: Mileage discrepancies detected.** "
        for flag in flags:
            if flag.get("type") == "mileage_drop":
                report += f"The recorded mileage dropped {flag.get('detail', '')}. "
        report += "This is a serious concern — the odometer may have been tampered with. We strongly recommend verifying the mileage through independent service history records before considering this vehicle.\n"
    elif risk_level == "none":
        report += "Mileage readings show a **consistent upward trend** across all MOT records. No anomalies or suspicious patterns detected. The annual mileage appears normal for this type of vehicle.\n"
    elif risk_level == "low":
        report += "Mileage patterns are **generally consistent** but with some minor variations. No serious concerns, though it's worth asking the seller about the vehicle's usage history.\n"
    else:
        report += f"Mileage analysis shows a **{risk_level} risk** level. While not conclusive evidence of clocking, the patterns warrant further investigation.\n"

    report += "\n## Risk Factors\n"
    risk_items = []
    if clocked:
        risk_items.append("Mileage discrepancy detected — potential clocking")
    if total_failures > 2:
        risk_items.append(f"Vehicle has failed {total_failures} MOT tests")
    for p in patterns:
        risk_items.append(f"Recurring {p['category']} issues ({p['occurrences']} times, {p['concern_level']} concern)")
    if compliant is False:
        charge_str = f" (£{daily_charge}/day)" if daily_charge else ""
        risk_items.append(f"Non-compliant with UK clean air zones — daily charges will apply{charge_str}")
    if vehicle_data and vehicle_data.get("markedForExport"):
        risk_items.append("Vehicle is marked for export")

    if not risk_items:
        report += "- No significant risk factors identified\n"
    else:
        for item in risk_items:
            report += f"- {item}\n"

    # --- Estimated Repair Costs ---
    report += "\n## Estimated Repair Costs\n"
    if repair_lines:
        report += "Based on recurring MOT advisories and failure patterns, budget for:\n\n"
        for line in repair_lines:
            report += f"{line}\n"
        report += f"\n**Total potential repair outlay: £{total_repair_low}-£{total_repair_high}**\n"
        report += "\n*Estimates based on typical UK independent garage rates. Dealer prices may be 30-50% higher.*\n"
    else:
        report += "No recurring defect patterns found in the MOT history. Standard maintenance costs should apply.\n"

    # --- 12-Month Cost Forecast ---
    report += "\n## 12-Month Cost Forecast\n"
    report += "Estimated ownership costs for the next 12 months:\n\n"
    report += f"| Item | Low Estimate | High Estimate |\n"
    report += f"|------|-------------|---------------|\n"
    report += f"| Annual service | £{service_cost_low} | £{service_cost_high} |\n"
    report += f"| MOT test fee | £{mot_fee:.2f} | £{mot_fee:.2f} |\n"
    if annual_repair_low > 0 or annual_repair_high > 0:
        report += f"| Predicted repairs (from advisories) | £{annual_repair_low} | £{annual_repair_high} |\n"
    if tax_status and tax_status != "Unknown":
        report += f"| Road tax | Status: {tax_status} | Check GOV.UK |\n"
    if compliant is False and daily_charge:
        report += f"| ULEZ/CAZ charges (if applicable) | £{daily_charge}/day | £{daily_charge}/day |\n"
    report += f"| **Total (excl. fuel & insurance)** | **£{forecast_total_low:,.2f}** | **£{forecast_total_high:,.2f}** |\n"
    report += "\n*This forecast excludes fuel, insurance, and any unexpected mechanical failures.*\n"

    # --- Questions to Ask the Seller ---
    report += "\n## Questions to Ask the Seller\n"
    for i, q in enumerate(seller_questions[:7], 1):
        report += f"{i}. {q}\n"

    # --- Recommendation ---
    report += f"\n## Recommendation\n**{verdict}** — {verdict_reasoning}\n"

    # --- Negotiation Script ---
    report += "\n## Negotiation Script\n"
    if verdict == "AVOID":
        report += "We recommend walking away from this vehicle.\n\n"
        if clocked:
            report += (
                "If you still wish to proceed despite the mileage concerns, you should:\n"
                "1. Demand the full service history with stamped mileage records\n"
                "2. Commission an independent mileage verification (approx. £30-50)\n"
                "3. Factor in the cost of hidden wear from the actual (higher) mileage\n"
            )
            if listing_price:
                heavy_discount = int(listing_price * 0.30 / 100)
                report += f"4. If the seller cannot prove the mileage, offer at least 30% below asking (save ~£{heavy_discount})\n"
        else:
            report += (
                "The vehicle's condition does not justify the risk. If you do proceed:\n"
                "1. Get an independent pre-purchase inspection (£150-250)\n"
                "2. Obtain quotes for all flagged issues before making an offer\n"
            )
            if listing_price:
                heavy_discount = int(listing_price * 0.25 / 100)
                report += f"3. Do not pay more than 75% of the asking price (save ~£{heavy_discount})\n"
    elif verdict == "NEGOTIATE":
        report += "Here's how to approach the negotiation:\n\n"
        report += f"**Step 1 — Establish the issues:**\n"
        report += f'"I\'ve had an independent vehicle check done and there are a few things I\'d like to discuss."\n\n'

        if patterns:
            top = patterns[0]
            estimate = _estimate_repair_cost(top["category"])
            if estimate:
                report += f"**Step 2 — Reference the data:**\n"
                report += (
                    f'"The MOT history shows recurring {top["category"]} issues '
                    f'({top["occurrences"]} times). I\'ve had quotes and I\'m looking at '
                    f'£{estimate["low"]}-£{estimate["high"]} for the {estimate["component"].lower()}."\n\n'
                )

        report += f"**Step 3 — Present your offer:**\n"
        if listing_price:
            discount_amount = total_repair_low + (total_repair_high - total_repair_low) // 2
            discount_amount = max(discount_amount, int(listing_price * 0.05 / 100))  # At least 5%
            offer_price = int(listing_price / 100) - discount_amount
            asking_price = int(listing_price / 100)
            report += (
                f'"Taking into account the £{total_repair_low}-£{total_repair_high} in likely '
                f'repair costs, I\'d like to offer £{offer_price:,} rather than the asking price '
                f'of £{asking_price:,}. That accounts for the work the car needs."\n\n'
            )
        else:
            report += (
                f'"Based on the repair estimates of £{total_repair_low}-£{total_repair_high}, '
                f'I think the price should reflect the work the car needs. '
                f'I\'d suggest reducing the price by at least £{total_repair_low + (total_repair_high - total_repair_low) // 2}."\n\n'
            )

        report += f"**Step 4 — Compromise position:**\n"
        report += '"I understand if you can\'t go that low. Would you consider splitting the difference, '
        report += 'or getting the work done before the sale?"\n'
    else:
        # BUY verdict
        report += "This vehicle has a clean history, so you're negotiating from a position of wanting the car rather than needing a discount. That said:\n\n"
        report += "**Step 1 — Do your research:**\n"
        report += "Check comparable listings on AutoTrader, eBay, and Facebook Marketplace for similar age, mileage, and spec.\n\n"
        report += "**Step 2 — Reference the market:**\n"
        report += '"I\'ve been looking at a few similar cars and the prices range quite a bit. '
        report += 'What\'s the best you can do on the price?"\n\n'
        if patterns:
            top = patterns[0]
            estimate = _estimate_repair_cost(top["category"])
            if estimate:
                report += "**Step 3 — Use minor advisories:**\n"
                report += (
                    f'"I noticed there are {top["category"]} advisories on the last MOT. '
                    f'That\'s potentially £{estimate["low"]}-£{estimate["high"]} down the line. '
                    f'Could you factor that into the price?"\n\n'
                )
        if listing_price:
            modest_discount = max(int(listing_price * 0.05 / 100), 50)
            report += f"A reasonable opening offer would be £{modest_discount} below asking.\n"

    return report
