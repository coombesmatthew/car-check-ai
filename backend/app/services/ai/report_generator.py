"""AI-powered vehicle report generator using Claude.

Generates a comprehensive buyer's report that justifies the £3.99 price
by providing genuine insight, actionable negotiation advice, and cost
projections that the buyer can't get from reading the free data cards.
"""

import json
from datetime import datetime
from typing import Dict, List, Optional

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
    "clutch": {"component": "Clutch replacement", "low": 400, "high": 800, "per": ""},
    "battery": {"component": "Battery replacement", "low": 80, "high": 200, "per": ""},
    "oil": {"component": "Oil leak repair", "low": 100, "high": 400, "per": ""},
    "coolant": {"component": "Cooling system repair", "low": 100, "high": 500, "per": ""},
    "drive shaft": {"component": "Drive shaft/CV joint", "low": 150, "high": 350, "per": "per side"},
    "wheel bearing": {"component": "Wheel bearing", "low": 120, "high": 300, "per": "each"},
}


def _estimate_repair_cost(category: str) -> Optional[Dict]:
    """Look up estimated repair cost for a defect category."""
    cat_lower = category.lower()
    for key, estimate in REPAIR_COST_ESTIMATES.items():
        if key in cat_lower:
            return estimate
    return None


SYSTEM_PROMPT = """You are an expert independent used car advisor writing a paid buyer's report for a prospective buyer in the UK.
The buyer has paid £3.99 for your expert analysis. They can already see the raw data (MOT results, tax status, mileage chart) for free — your job is to add the insight, interpretation, and actionable advice they CAN'T get from reading data cards.

Write in British English. Use markdown headings (##) and bullet points. Be direct, specific, and honest.

Your report MUST follow this exact structure:

## Should You Buy This Car?
Open with a clear, bold verdict: **BUY**, **NEGOTIATE**, or **AVOID**.
Then 2-3 sentences explaining WHY in plain language a non-expert understands.
This is the most important section — the buyer needs a clear answer.

## The Full Picture
A detailed narrative analysis covering:
- What the MOT history reveals about how this car has been treated
- Specific defect patterns and what they mean for THIS make/model (e.g. "recurring suspension wear is common on Golfs of this age and isn't a red flag, but budget for it")
- Whether the mileage pattern is normal, and what the annual mileage tells you about usage type (motorway cruiser vs city runabout)
- How the condition score of X/100 compares to typical cars of this age and mileage
- Any timing-related concerns (e.g. "the MOT expires in 47 days — use this as leverage")

Be specific to THIS car. Reference actual defect text from the MOT history. Don't just restate numbers.

## What Will It Cost You?
A concrete cost breakdown for the next 12 months:

**Immediate costs (within 30 days):**
- List any advisories likely to become failures at next MOT, with £ estimates
- Factor in anything the buyer will need to fix to pass the next MOT

**Annual running costs:**
- Road tax: use the actual VED band data if available
- Estimated annual service cost for this specific make/model
- Insurance group estimate if you know the model
- ULEZ/CAZ charges if non-compliant

**Predicted repairs (next 12 months):**
- Based on the advisory pattern trajectory, what's likely to need doing?
- Give specific £ ranges for each item using UK independent garage rates

**Total 12-month ownership cost estimate:** £X,XXX - £X,XXX (excluding fuel and insurance)

## Negotiation Playbook
This is where the report pays for itself. Give the buyer a specific, step-by-step script:

1. **Opening line** — What to say when you arrive to view the car
2. **Points to raise** — Specific issues from THIS car's data to mention (reference the exact MOT advisory text)
3. **Your opening offer** — If a listing price is provided, calculate a specific £ figure and explain the logic
4. **Fallback position** — If they won't accept your offer, what's the compromise?
5. **Walk-away point** — At what price does this car stop being worth it?

Use actual quotes the buyer can say. Make them sound natural, not aggressive.

## Test Drive Checklist
5-8 specific things to check on THIS car based on its MOT history and known issues:
- If there are suspension advisories: "Listen for knocking over speed bumps — the [specific component] was flagged"
- If brake wear: "Test braking firmly from 40mph — the brake [pads/discs] were noted as worn"
- Reference the specific defect items from the MOT data

## Red Flags to Watch For
Things the buyer should check that aren't in the data:
- Signs specific to this make/model (known problem areas)
- What to look for on the V5C document
- Questions about service history specific to this car's age/mileage

Keep the report 800-1200 words. Every sentence should provide value the buyer couldn't get from reading the free data cards. If the car is genuinely clean with no issues, say so briefly and focus the report on future maintenance planning and negotiation strategy."""


def _build_full_context(
    registration: str,
    vehicle_data: Optional[Dict],
    mot_analysis: Dict,
    ulez_data: Optional[Dict],
    check_result: Optional[Dict] = None,
    listing_price: Optional[int] = None,
    listing_url: Optional[str] = None,
) -> str:
    """Build comprehensive context string with ALL available data for Claude."""
    parts = [f"=== VEHICLE CHECK DATA FOR {registration} ===\n"]

    # Vehicle identity
    if vehicle_data:
        parts.append(f"""VEHICLE (DVLA):
Make: {vehicle_data.get('make', '?')}
Colour: {vehicle_data.get('colour', '?')}
Fuel: {vehicle_data.get('fuelType', '?')}
Year: {vehicle_data.get('yearOfManufacture', '?')}
Engine: {vehicle_data.get('engineCapacity', '?')}cc
Euro Standard: {vehicle_data.get('euroStatus', '?')}
Tax Status: {vehicle_data.get('taxStatus', '?')}
MOT Status: {vehicle_data.get('motStatus', '?')}
MOT Expiry: {vehicle_data.get('motExpiryDate', '?')}
V5C Last Issued: {vehicle_data.get('dateOfLastV5CIssued', '?')}
Marked for Export: {vehicle_data.get('markedForExport', False)}
CO2 Emissions: {vehicle_data.get('co2Emissions', '?')} g/km
Type Approval: {vehicle_data.get('typeApproval', '?')}""")

    # MOT summary
    mot_summary = mot_analysis.get("mot_summary", {})
    if mot_summary:
        model = mot_summary.get("model", "")
        parts.append(f"""
MOT SUMMARY:
Make/Model: {mot_summary.get('make', '?')} {model}
Total Tests: {mot_summary.get('total_tests', 0)}
Passes: {mot_summary.get('total_passes', 0)}
Failures: {mot_summary.get('total_failures', 0)}
Current Mileage: {mot_summary.get('current_odometer', '?')} miles
First Used: {mot_summary.get('first_used_date', '?')}""")

    # Condition score
    condition = mot_analysis.get("condition_score")
    if condition is not None:
        parts.append(f"\nCONDITION SCORE: {condition}/100")

    # Clocking analysis
    clocking = mot_analysis.get("clocking_analysis", {})
    parts.append(f"""
MILEAGE ANALYSIS:
Clocking Detected: {clocking.get('clocked', False)}
Risk Level: {clocking.get('risk_level', 'unknown')}""")
    for flag in clocking.get("flags", []):
        parts.append(f"  FLAG [{flag.get('severity', '').upper()}]: {flag.get('detail', '')}")

    # Failure patterns
    patterns = mot_analysis.get("failure_patterns", [])
    if patterns:
        parts.append("\nRECURRING DEFECT PATTERNS:")
        for p in patterns:
            est = _estimate_repair_cost(p["category"])
            cost_str = f" — estimated repair: £{est['low']}-£{est['high']}" if est else ""
            parts.append(f"  {p['category']}: {p['occurrences']}x ({p['concern_level']} concern){cost_str}")

    # Full MOT test history with every defect
    mot_tests = mot_analysis.get("mot_tests", [])
    if mot_tests:
        parts.append(f"\nFULL MOT HISTORY ({len(mot_tests)} tests, newest first):")
        for test in mot_tests[:15]:  # Cap at 15 to avoid context overflow
            odo = f"{test.get('odometer', '?'):,} mi" if test.get('odometer') else "? mi"
            parts.append(f"\n  Test #{test.get('test_number', '?')} — {test.get('date', '?')} — {test.get('result', '?')} — {odo}")
            for a in test.get("advisories", []):
                parts.append(f"    ADVISORY: {a.get('text', '')}")
            for f in test.get("failures", []):
                parts.append(f"    FAILURE: {f.get('text', '')}")
            for d in test.get("dangerous", []):
                parts.append(f"    DANGEROUS: {d.get('text', '')}")

    # Mileage timeline
    timeline = mot_analysis.get("mileage_timeline", [])
    if timeline:
        parts.append("\nMILEAGE TIMELINE:")
        for r in timeline:
            parts.append(f"  {r.get('date', '?')}: {r.get('miles', 0):,} miles")

    # ULEZ compliance
    if ulez_data:
        parts.append(f"""
ULEZ/CLEAN AIR ZONES:
Compliant: {ulez_data.get('compliant', '?')}
Status: {ulez_data.get('status', '?')}
Reason: {ulez_data.get('reason', '?')}""")
        if ulez_data.get("daily_charge"):
            parts.append(f"Daily Charge: {ulez_data['daily_charge']}")
        zones = ulez_data.get("zone_details", [])
        non_compliant = [z for z in zones if not z.get("compliant") and z.get("cars_affected")]
        if non_compliant:
            parts.append("Non-compliant zones:")
            for z in non_compliant:
                parts.append(f"  {z.get('name', '?')} ({z.get('region', '?')}): {z.get('charge', '?')}")

    # Additional data from check_result (tax, safety, stats)
    if check_result:
        tax = check_result.get("tax_calculation")
        if tax:
            parts.append(f"""
ROAD TAX (VED):
Band: {tax.get('band', '?')} ({tax.get('band_range', '?')})
Annual Rate: £{tax.get('annual_rate', '?')}
6-Month Rate: £{tax.get('six_month_rate', '?')}
Monthly Equivalent: £{tax.get('monthly_total', '?')}/month
Is Electric: {tax.get('is_electric', False)}""")

        safety = check_result.get("safety_rating")
        if safety:
            parts.append(f"""
SAFETY RATING ({safety.get('source', '?')}):
Stars: {safety.get('stars', '?')}/5 ({safety.get('year_range', '?')})
Adult Protection: {safety.get('adult', '?')}%
Child Protection: {safety.get('child', '?')}%
Pedestrian: {safety.get('pedestrian', '?')}%
Safety Assist: {safety.get('safety_assist', '?')}%""")

        stats = check_result.get("vehicle_stats")
        if stats:
            parts.append(f"""
VEHICLE STATISTICS:
Age: {stats.get('vehicle_age_years', '?')} years
Est. Annual Mileage: {stats.get('estimated_annual_mileage', '?')} miles/year
Mileage Assessment: {stats.get('mileage_assessment', '?')}
MOT Days Remaining: {stats.get('mot_days_remaining', '?')}
Tax Days Remaining: {stats.get('tax_days_remaining', '?')}
V5C Issued: {stats.get('v5c_issued_date', '?')} ({stats.get('v5c_days_since', '?')} days ago)
V5C Insight: {stats.get('v5c_insight', '?')}
Lifetime Advisories: {stats.get('total_advisory_items', '?')}
Lifetime Failures: {stats.get('total_failure_items', '?')}
Lifetime Dangerous Items: {stats.get('total_dangerous_items', '?')}""")

    # Listing info
    if listing_price:
        parts.append(f"\nLISTING PRICE: £{listing_price / 100:,.2f}")
    if listing_url:
        parts.append(f"LISTING URL: {listing_url}")

    parts.append(f"\nTODAY'S DATE: {datetime.utcnow().strftime('%d %B %Y')}")
    parts.append("\n=== END OF DATA ===")
    parts.append("\nPlease write a comprehensive buyer's report for this vehicle.")

    return "\n".join(parts)


async def generate_ai_report(
    registration: str,
    vehicle_data: Optional[Dict],
    mot_analysis: Dict,
    ulez_data: Optional[Dict],
    listing_price: Optional[int] = None,
    listing_url: Optional[str] = None,
    check_result: Optional[Dict] = None,
) -> Optional[str]:
    """Generate an AI buyer's report using Claude.

    Args:
        registration: Vehicle registration number
        vehicle_data: DVLA VES API response
        mot_analysis: Analyzed MOT data (from MOTAnalyzer)
        ulez_data: ULEZ compliance data
        listing_price: Listed price in pence (optional)
        listing_url: URL of the listing (optional)
        check_result: Full serialised FreeCheckResponse dict (for tax, safety, stats)

    Returns:
        Markdown-formatted report string, or None if generation fails.
    """
    if not settings.ANTHROPIC_API_KEY or settings.ANTHROPIC_API_KEY.startswith("your_"):
        logger.warning("Anthropic API key not configured — using demo report")
        return _generate_demo_report(
            registration, vehicle_data, mot_analysis, ulez_data, listing_price
        )

    user_message = _build_full_context(
        registration, vehicle_data, mot_analysis, ulez_data,
        check_result, listing_price, listing_url,
    )

    try:
        client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

        message = client.messages.create(
            model=settings.ANTHROPIC_MODEL,
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_message}],
        )

        report = message.content[0].text
        logger.info(f"AI report generated for {registration} ({message.usage.input_tokens}+{message.usage.output_tokens} tokens)")
        return report

    except anthropic.APIError as e:
        logger.error(f"Anthropic API error: {e}")
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
    mot_expiry = vehicle_data.get("motExpiryDate") if vehicle_data else None

    mot_summary = mot_analysis.get("mot_summary", {})
    total_tests = mot_summary.get("total_tests", 0)
    total_passes = mot_summary.get("total_passes", 0)
    total_failures = mot_summary.get("total_failures", 0)
    current_mileage = mot_summary.get("current_odometer", "Unknown")
    model = mot_summary.get("model", "")

    clocking = mot_analysis.get("clocking_analysis", {})
    clocked = clocking.get("clocked", False)
    risk_level = clocking.get("risk_level", "unknown")
    condition = mot_analysis.get("condition_score")
    patterns = mot_analysis.get("failure_patterns", [])
    mot_tests = mot_analysis.get("mot_tests", [])

    compliant = ulez_data.get("compliant", None) if ulez_data else None
    daily_charge = ulez_data.get("daily_charge") if ulez_data else None

    # Determine verdict
    if clocked:
        verdict = "AVOID"
    elif condition and condition < 50:
        verdict = "AVOID"
    elif total_failures > 2 or (condition and condition < 70):
        verdict = "NEGOTIATE"
    else:
        verdict = "BUY"

    engine_str = f"{engine}cc " if engine else ""
    pass_rate = round(total_passes / total_tests * 100) if total_tests > 0 else 0

    # Calculate MOT days remaining
    mot_days = None
    if mot_expiry:
        try:
            exp = datetime.strptime(mot_expiry, "%Y-%m-%d")
            mot_days = (exp - datetime.utcnow()).days
        except ValueError:
            pass

    # Collect recent advisories for specificity
    recent_advisories = []
    recent_failures = []
    for test in mot_tests[:3]:
        for a in test.get("advisories", []):
            if a.get("text") and a["text"] not in recent_advisories:
                recent_advisories.append(a["text"])
        for f in test.get("failures", []):
            if f.get("text") and f["text"] not in recent_failures:
                recent_failures.append(f["text"])

    # Build repair estimates
    repair_items = []
    total_repair_low = 0
    total_repair_high = 0
    for p in patterns:
        est = _estimate_repair_cost(p["category"])
        if est:
            repair_items.append((p, est))
            total_repair_low += est["low"]
            total_repair_high += est["high"]

    # Annual costs
    service_low, service_high = 150, 300
    mot_fee = 54.85
    annual_repair_low = int(total_repair_low * 0.6)
    annual_repair_high = int(total_repair_high * 0.8)

    # --- Build the report ---
    report = f"## Should You Buy This Car?\n"

    if verdict == "BUY":
        report += f"**BUY** — This {year} {make.title()} {model} is a solid choice. "
        if condition and condition >= 80:
            report += f"With a condition score of {condition}/100 and a {pass_rate}% MOT pass rate across {total_tests} tests, this car has been well looked after. "
        else:
            report += f"The condition score of {condition}/100 is reasonable for its age. "
        if not clocked:
            report += "Mileage readings are consistent with no signs of tampering. "
        if total_failures == 0:
            report += "The fact it has never failed an MOT is a strong indicator of careful ownership.\n"
        else:
            report += f"The {total_failures} MOT failure{'s' if total_failures != 1 else ''} {'are' if total_failures > 1 else 'is'} minor and {'were' if total_failures > 1 else 'was'} promptly resolved.\n"
    elif verdict == "NEGOTIATE":
        report += f"**NEGOTIATE** — This {year} {make.title()} {model} is worth considering, but the data gives you leverage to negotiate the price down. "
        if patterns:
            report += f"Recurring {patterns[0]['category']} issues ({patterns[0]['occurrences']} times in MOT history) and "
        report += f"a condition score of {condition}/100 mean you should factor in upcoming repair costs before agreeing on a price.\n"
    else:
        report += f"**AVOID** — This {year} {make.title()} {model} raises serious concerns. "
        if clocked:
            report += "Mileage discrepancies have been detected, which is a major red flag. The odometer may have been tampered with, meaning hidden mechanical wear that will cost you in the long run.\n"
        else:
            report += f"With a condition score of just {condition}/100 and {total_failures} MOT failures, the risk of expensive repairs outweighs the potential value.\n"

    # --- The Full Picture ---
    report += f"\n## The Full Picture\n"

    # MOT narrative
    if total_tests > 0:
        report += f"This car has been through {total_tests} MOT tests since first registration, passing {total_passes} ({pass_rate}%). "

    # Interpret the advisory pattern
    if recent_advisories:
        report += f"The most recent MOTs have flagged:\n\n"
        for adv in recent_advisories[:5]:
            report += f"- *\"{adv}\"*\n"
        report += "\n"

        if patterns:
            top = patterns[0]
            est = _estimate_repair_cost(top["category"])
            report += f"The recurring theme is **{top['category']}** issues, which have appeared {top['occurrences']} times. "
            if top["concern_level"] == "low":
                report += f"For a {make.title()} {model} of this age, this is fairly typical wear-and-tear rather than a sign of neglect. "
            elif top["concern_level"] == "medium":
                report += "This is worth investigating — it could indicate the car has been driven hard or maintenance has been deferred. "
            else:
                report += "This is concerning and suggests either heavy use, deferred maintenance, or a deeper underlying problem. "
            if est:
                report += f"Budget £{est['low']}-£{est['high']} {est['per']} to address this.\n"
    elif total_tests > 0:
        report += "The MOT history is remarkably clean with no recurring issues — a good sign of careful ownership.\n"

    # Mileage narrative
    report += "\n"
    try:
        miles_int = int(current_mileage) if current_mileage != "Unknown" else None
    except (ValueError, TypeError):
        miles_int = None

    if clocked:
        report += "**Mileage Warning:** The recorded mileage has gone *backwards* between MOT tests. This is a strong indicator of odometer tampering (clocking). "
        for flag in clocking.get("flags", []):
            if flag.get("detail"):
                report += f"{flag['detail']}. "
        report += "You should demand full service history with stamped mileage records, or walk away.\n"
    elif miles_int:
        age = datetime.utcnow().year - year if isinstance(year, int) else None
        if age and age > 0:
            annual = miles_int // age
            if annual < 6000:
                report += f"At {miles_int:,} miles over {age} years (~{annual:,}/year), this is a **low-mileage** car. That's a positive — it's likely been used for short local trips. Check for signs of short-journey wear (battery condition, exhaust corrosion).\n"
            elif annual < 12000:
                report += f"At {miles_int:,} miles over {age} years (~{annual:,}/year), this is **average mileage** for a UK car. Nothing to worry about here.\n"
            else:
                report += f"At {miles_int:,} miles over {age} years (~{annual:,}/year), this is **above-average mileage**. Not necessarily a problem — high-mileage motorway cars can be mechanically sound — but factor in earlier replacement of wear items (clutch, timing belt, suspension bushes).\n"

    # MOT timing
    if mot_days is not None:
        if mot_days < 60:
            report += f"\nThe MOT expires in **{mot_days} days** — this is useful negotiating leverage. The seller needs to either MOT it before sale or discount the price to account for the risk of failure.\n"
        elif mot_days > 300:
            report += f"\nThe MOT isn't due for another {mot_days} days — that's a reassuring amount of runway.\n"

    # --- What Will It Cost You? ---
    report += "\n## What Will It Cost You?\n"

    report += "\n**Immediate costs (within 30 days):**\n"
    if recent_advisories:
        urgent_found = False
        for adv in recent_advisories[:3]:
            adv_lower = adv.lower()
            for key, est in REPAIR_COST_ESTIMATES.items():
                if key in adv_lower:
                    report += f"- {adv} → **£{est['low']}-£{est['high']}** {est['per']}\n"
                    urgent_found = True
                    break
        if not urgent_found:
            report += "- No urgent repairs needed based on the latest MOT\n"
    else:
        report += "- No advisories flagged — no immediate work needed\n"

    report += "\n**Annual running costs:**\n"
    report += f"- Annual service ({make.title()} {model}): **£{service_low}-£{service_high}**\n"
    report += f"- MOT test fee: **£{mot_fee:.2f}**\n"
    if tax_status and tax_status != "Unknown":
        report += f"- Road tax: Status is *{tax_status}*\n"
    if compliant is False and daily_charge:
        report += f"- ULEZ/CAZ daily charges: **{daily_charge}** (if driving in clean air zones)\n"

    if repair_items:
        report += "\n**Predicted repairs (next 12 months):**\n"
        for p, est in repair_items:
            report += f"- {est['component']}: **£{est['low']}-£{est['high']}** {est['per']} (flagged {p['occurrences']}x in MOT history)\n"

    total_low = service_low + int(mot_fee) + annual_repair_low
    total_high = service_high + int(mot_fee) + annual_repair_high
    report += f"\n**Total 12-month ownership estimate: £{total_low:,} - £{total_high:,}** *(excluding fuel and insurance)*\n"

    # --- Negotiation Playbook ---
    report += "\n## Negotiation Playbook\n"

    if verdict == "AVOID":
        report += "We recommend walking away. If you still want to proceed:\n\n"
        if clocked:
            report += "1. **Opening line:** *\"I've had an independent data check done and I need to discuss the mileage history before we go any further.\"*\n"
            report += "2. **Point to raise:** *\"The MOT records show the mileage went backwards between tests. Can you explain this? Do you have service records that verify the true mileage?\"*\n"
            if listing_price:
                discount = int(listing_price * 0.30 / 100)
                offer = int(listing_price / 100) - discount
                report += f"3. **If they can't explain it:** Offer no more than **£{offer:,}** (30% below asking) — or walk away\n"
            report += "4. **Walk-away point:** If they can't produce stamped service history confirming the mileage, do not buy this car\n"
        else:
            report += "1. **Opening line:** *\"I like the car but the data check has flagged some issues I need to factor into my offer.\"*\n"
            if listing_price:
                discount = int(listing_price * 0.25 / 100)
                offer = int(listing_price / 100) - discount
                report += f"2. **Your offer:** **£{offer:,}** (25% below asking to cover risk and repair costs)\n"
            report += f"3. **Walk-away point:** With £{total_repair_low}-£{total_repair_high} in likely repairs, anything above 80% of asking price is overpaying\n"
    elif verdict == "NEGOTIATE":
        report += "You have genuine leverage here. Use it:\n\n"
        report += "1. **Opening line:** *\"I've done a full vehicle check and I'm interested, but there are a few things in the history I'd like to discuss.\"*\n\n"

        if patterns:
            top = patterns[0]
            est = _estimate_repair_cost(top["category"])
            if est:
                report += f"2. **Key point:** *\"The MOT history shows recurring {top['category']} issues — {top['occurrences']} times across the tests. I've looked into it and I'm expecting £{est['low']}-£{est['high']} to sort that out. Can we factor that into the price?\"*\n\n"

        if listing_price:
            discount_amount = max(total_repair_low + (total_repair_high - total_repair_low) // 2, int(listing_price * 0.05 / 100))
            offer = int(listing_price / 100) - discount_amount
            asking = int(listing_price / 100)
            report += f"3. **Your opening offer:** **£{offer:,}** (£{discount_amount:,} below the asking price of £{asking:,})\n\n"
            compromise = int(listing_price / 100) - discount_amount // 2
            report += f"4. **Fallback:** *\"I understand you might not be able to go that low. Would £{compromise:,} work if we split the difference?\"*\n\n"
            walk_away = int(listing_price / 100) - max(int(discount_amount * 0.3), 50)
            report += f"5. **Walk-away point:** Don't pay more than **£{walk_away:,}**\n"
        else:
            report += f"3. **Your offer:** Deduct **£{total_repair_low + (total_repair_high - total_repair_low) // 2:,}** from the asking price to cover predicted repair costs\n\n"
            report += "4. **Fallback:** Offer to split the difference, or ask the seller to get the work done before sale\n"
    else:
        report += "This car checks out well, so you're negotiating from a position of *wanting* it rather than *needing* a discount. But there's always room:\n\n"
        report += "1. **Opening line:** *\"I've been looking at a few options and had checks done on all of them. What's the best you can do on the price?\"*\n\n"
        if patterns and repair_items:
            top_p, top_est = repair_items[0]
            report += f"2. **Mild leverage:** *\"The check flagged some {top_p['category']} wear — I'll need to budget £{top_est['low']}-£{top_est['high']} for that. Could you knock something off to cover it?\"*\n\n"
        if mot_days is not None and mot_days < 90:
            report += f"3. **MOT leverage:** *\"The MOT is due in {mot_days} days. Would you be willing to put a fresh MOT on it before I buy?\"*\n\n"
        if listing_price:
            modest = max(int(listing_price * 0.05 / 100), 100)
            offer = int(listing_price / 100) - modest
            report += f"4. **Opening offer:** **£{offer:,}** (£{modest:,} below asking — a reasonable starting point)\n"
        report += "\n5. **Walk-away mindset:** There's always another car. Don't overpay just because the check is clean.\n"

    # --- Test Drive Checklist ---
    report += "\n## Test Drive Checklist\n"
    report += "Based on this car's specific history, check these during your test drive:\n\n"

    checklist = []
    for adv_text in recent_advisories[:4]:
        lower = adv_text.lower()
        if "brake" in lower:
            checklist.append(f"Test braking firmly from 40mph — *\"{adv_text}\"* was flagged on the MOT")
        elif "suspension" in lower or "shock" in lower or "spring" in lower:
            checklist.append(f"Drive over speed bumps and listen for knocking — *\"{adv_text}\"* was noted")
        elif "tyre" in lower:
            checklist.append(f"Check tread depth on all four corners — *\"{adv_text}\"* was advisory")
        elif "steering" in lower:
            checklist.append(f"Turn the steering fully in both directions at low speed — *\"{adv_text}\"* was flagged")
        elif "exhaust" in lower or "emission" in lower:
            checklist.append(f"Look for blue/white smoke on startup and under acceleration — *\"{adv_text}\"* was noted")
        elif "corrosion" in lower:
            checklist.append(f"Inspect the body panels and sills for rust — *\"{adv_text}\"* was flagged")

    if not checklist:
        checklist.append("Start the engine from cold — listen for unusual noises in the first 30 seconds")
        checklist.append("Check all dashboard warning lights clear after ignition")

    checklist.extend([
        "Check the gearbox is smooth through all gears — any crunching indicates wear",
        "Test the air conditioning — a failing compressor can cost £400+",
        "Check the V5C matches the seller's ID and address",
    ])

    if miles_int and miles_int > 70000:
        checklist.append("Ask about timing belt/chain — replacement is typically due every 60-80k miles (£400-800)")

    for item in checklist[:8]:
        report += f"- {item}\n"

    # --- Red Flags ---
    report += "\n## Red Flags to Watch For\n"
    report += f"Things to verify in person that the data can't tell you:\n\n"
    report += "- **Service history:** Ask for the stamped service book. Gaps in servicing are a concern at any mileage\n"
    report += "- **V5C document:** Check the name and address match the seller. If they say \"I'm selling for a friend,\" proceed with extreme caution\n"

    if vehicle_data and vehicle_data.get("dateOfLastV5CIssued"):
        v5c_date = vehicle_data["dateOfLastV5CIssued"]
        report += f"- **V5C timing:** The V5C was last issued on {v5c_date}. If this doesn't match when the seller says they bought it, ask why\n"

    report += "- **Payment:** Never pay cash without a receipt. Bank transfer is safest — you have a paper trail\n"
    report += f"- **HPI check:** Consider a full HPI/provenance check (finance, stolen, write-off) for complete peace of mind — our Premium Check covers this for £9.99\n"

    return report
