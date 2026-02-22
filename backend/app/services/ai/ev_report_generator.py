"""EV-specific AI report generator using Claude.

Generates two types of reports:
1. FREE preview — uses only DVLA + MOT data, with general EV knowledge
2. PAID full report — uses ClearWatt, EV Database, AutoPredict data

Both provide a clear BUY / NEGOTIATE / AVOID verdict.
"""

from datetime import datetime
from typing import Dict, List, Optional

import anthropic

from app.core.config import settings
from app.core.logging import logger


_UPPERCASE_MAKES = {"BMW", "MG", "TVR", "DS", "BYD", "GWM", "JAC", "MAN"}


def _format_make(make: str) -> str:
    """Format make name — keep known acronyms uppercase, title-case the rest."""
    upper = make.upper().strip()
    if upper in _UPPERCASE_MAKES:
        return upper
    return make.title()


# Known EV battery specs for common UK models (used in free preview when no paid data)
EV_KNOWN_SPECS = {
    "TESLA MODEL 3": {"battery_kwh": 60, "official_range_miles": 272, "rapid_kw": 250},
    "TESLA MODEL Y": {"battery_kwh": 75, "official_range_miles": 331, "rapid_kw": 250},
    "TESLA MODEL S": {"battery_kwh": 100, "official_range_miles": 405, "rapid_kw": 250},
    "TESLA MODEL X": {"battery_kwh": 100, "official_range_miles": 348, "rapid_kw": 250},
    "NISSAN LEAF": {"battery_kwh": 40, "official_range_miles": 168, "rapid_kw": 50},
    "VOLKSWAGEN ID.3": {"battery_kwh": 58, "official_range_miles": 263, "rapid_kw": 120},
    "VOLKSWAGEN ID.4": {"battery_kwh": 77, "official_range_miles": 323, "rapid_kw": 135},
    "BMW IX3": {"battery_kwh": 74, "official_range_miles": 285, "rapid_kw": 150},
    "BMW I4": {"battery_kwh": 84, "official_range_miles": 365, "rapid_kw": 200},
    "BMW IX": {"battery_kwh": 105, "official_range_miles": 380, "rapid_kw": 200},
    "HYUNDAI IONIQ 5": {"battery_kwh": 77, "official_range_miles": 315, "rapid_kw": 220},
    "HYUNDAI KONA ELECTRIC": {"battery_kwh": 64, "official_range_miles": 300, "rapid_kw": 77},
    "KIA EV6": {"battery_kwh": 77, "official_range_miles": 328, "rapid_kw": 240},
    "KIA NIRO EV": {"battery_kwh": 65, "official_range_miles": 285, "rapid_kw": 77},
    "MG ZS EV": {"battery_kwh": 51, "official_range_miles": 273, "rapid_kw": 76},
    "MG4 EV": {"battery_kwh": 64, "official_range_miles": 281, "rapid_kw": 135},
    "PEUGEOT E-208": {"battery_kwh": 50, "official_range_miles": 225, "rapid_kw": 100},
    "RENAULT ZOE": {"battery_kwh": 52, "official_range_miles": 245, "rapid_kw": 50},
    "AUDI Q4 E-TRON": {"battery_kwh": 77, "official_range_miles": 316, "rapid_kw": 135},
    "MERCEDES EQA": {"battery_kwh": 67, "official_range_miles": 263, "rapid_kw": 100},
    "MERCEDES EQC": {"battery_kwh": 80, "official_range_miles": 259, "rapid_kw": 110},
    "VAUXHALL CORSA-E": {"battery_kwh": 50, "official_range_miles": 222, "rapid_kw": 100},
    "VAUXHALL MOKKA-E": {"battery_kwh": 50, "official_range_miles": 209, "rapid_kw": 100},
    "MINI ELECTRIC": {"battery_kwh": 33, "official_range_miles": 145, "rapid_kw": 50},
    "FIAT 500 ELECTRIC": {"battery_kwh": 42, "official_range_miles": 199, "rapid_kw": 85},
    "FORD MUSTANG MACH-E": {"battery_kwh": 91, "official_range_miles": 379, "rapid_kw": 150},
    "JAGUAR I-PACE": {"battery_kwh": 90, "official_range_miles": 292, "rapid_kw": 100},
    "PORSCHE TAYCAN": {"battery_kwh": 94, "official_range_miles": 301, "rapid_kw": 270},
    "VOLVO XC40 RECHARGE": {"battery_kwh": 78, "official_range_miles": 260, "rapid_kw": 150},
    "VOLVO EX30": {"battery_kwh": 69, "official_range_miles": 298, "rapid_kw": 153},
    "CUPRA BORN": {"battery_kwh": 58, "official_range_miles": 263, "rapid_kw": 120},
    "SKODA ENYAQ": {"battery_kwh": 77, "official_range_miles": 339, "rapid_kw": 135},
    "BYD ATTO 3": {"battery_kwh": 60, "official_range_miles": 261, "rapid_kw": 88},
}


def _lookup_known_specs(make: Optional[str], model: Optional[str]) -> Optional[Dict]:
    """Lookup known EV specs by make/model."""
    if not make:
        return None
    make_upper = make.upper().strip()
    if model:
        model_upper = model.upper().strip()
        # Try exact match first
        key = f"{make_upper} {model_upper}"
        if key in EV_KNOWN_SPECS:
            return EV_KNOWN_SPECS[key]
        # Try partial match
        for spec_key, specs in EV_KNOWN_SPECS.items():
            if make_upper in spec_key and model_upper in spec_key:
                return specs
    # Try make-only match (return first)
    for spec_key, specs in EV_KNOWN_SPECS.items():
        if spec_key.startswith(make_upper + " "):
            return specs
    return None


# UK average electricity rates (2025/26)
HOME_RATE_PENCE = 24.5  # Ofgem cap rate
RAPID_RATE_PENCE = 65.0  # Average public rapid charger
PETROL_COST_PER_MILE = 15.0  # pence


DATA_SOURCE_REGISTRY = {
    "dvla_ves": {
        "name": "DVLA Vehicle Enquiry Service",
        "site": "gov.uk",
        "desc": "Vehicle identity, tax status, MOT status, fuel type",
    },
    "dvsa_mot": {
        "name": "DVSA MOT History",
        "site": "gov.uk",
        "desc": "Full MOT test history, advisories, failures, and mileage readings",
    },
    "clearwatt": {
        "name": "ClearWatt",
        "site": "clearwatt.co.uk",
        "desc": "Real-world range estimates and battery degradation data",
    },
    "ev_database": {
        "name": "EV Database",
        "site": "ev-database.org",
        "desc": "Comprehensive EV specifications and charging data",
    },
    "autopredict": {
        "name": "AutoPredict",
        "site": "autopredict.co.uk",
        "desc": "AI-predicted vehicle lifespan and remaining value",
    },
}


def _collect_active_sources(
    vehicle_data: Optional[Dict],
    mot_analysis: Optional[Dict],
    ev_check_data: Optional[Dict] = None,
) -> List[str]:
    """Return source keys that were actually used."""
    sources = []
    if vehicle_data:
        sources.append("dvla_ves")
    if mot_analysis and (mot_analysis.get("mot_summary") or mot_analysis.get("mot_tests")):
        sources.append("dvsa_mot")
    if ev_check_data:
        if ev_check_data.get("range_estimate"):
            sources.append("clearwatt")
        if ev_check_data.get("ev_specs"):
            sources.append("ev_database")
        if ev_check_data.get("lifespan_prediction"):
            sources.append("autopredict")
    return sources


def _source_ref(source_keys: List[str], key: str) -> str:
    """Return ' [N]' for the given source key, or '' if not present."""
    try:
        return f" [{source_keys.index(key) + 1}]"
    except ValueError:
        return ""


def _build_sources_section(source_keys: List[str]) -> str:
    """Render a numbered markdown Data Sources footer."""
    lines = [
        "\n---",
        "## Data Sources",
        "This report was compiled using the following data sources:\n",
    ]
    for i, key in enumerate(source_keys, 1):
        src = DATA_SOURCE_REGISTRY.get(key)
        if not src:
            continue
        lines.append(f"{i}. **{src['name']}** ({src['site']}) — {src['desc']}")
    return "\n".join(lines)


# ─── FREE PREVIEW REPORT ────────────────────────────────────────────────

PREVIEW_SYSTEM_PROMPT = """You are VeriCar's EV specialist — an expert in electric vehicle battery health,
range estimation, and total cost of ownership. You write clear, authoritative reports for UK consumers
buying used electric vehicles.

You are writing a FREE preview report based on DVLA and MOT data only. You do NOT have access to
battery health telemetry, real-world range data, or lifespan prediction data — those are in the paid report.

Your job is to:
1. Provide genuine value from the free data (MOT history, mileage, vehicle condition)
2. Apply your EV expertise to interpret what the data means for an EV buyer
3. Make clear what ADDITIONAL insights the paid report (£7.99) would provide

Use UK units (miles, £), reference UK electricity rates, and be specific with numbers.
Keep the tone professional but accessible. Be honest — don't make up data you don't have.

IMPORTANT: Use numbered inline references [1], [2], etc. to cite data sources throughout the report.
Only cite sources listed in the DATA SOURCES USED block. Place each reference after the first mention
of data from that source."""


def _build_preview_context(
    registration: str,
    vehicle_data: Optional[Dict],
    mot_analysis: Optional[Dict],
    ev_check_data: Optional[Dict] = None,
) -> str:
    """Build context for free preview using only DVLA + MOT data."""
    parts = [f"=== EV HEALTH CHECK DATA FOR {registration} ===\n"]

    make = vehicle_data.get("make", "Unknown") if vehicle_data else "Unknown"
    model = None

    # Vehicle identity
    if vehicle_data:
        parts.append(f"""VEHICLE (DVLA):
Make: {vehicle_data.get('make', '?')}
Fuel Type: {vehicle_data.get('fuelType', '?')}
Year: {vehicle_data.get('yearOfManufacture', '?')}
Colour: {vehicle_data.get('colour', '?')}
Engine: {vehicle_data.get('engineCapacity', '?')}cc
Tax Status: {vehicle_data.get('taxStatus', '?')}
MOT Status: {vehicle_data.get('motStatus', '?')}
MOT Expiry: {vehicle_data.get('motExpiryDate', '?')}
V5C Last Issued: {vehicle_data.get('dateOfLastV5CIssued', '?')}
CO2 Emissions: {vehicle_data.get('co2Emissions', '?')} g/km""")

    # MOT summary
    if mot_analysis:
        mot_summary = mot_analysis.get("mot_summary", {})
        model = mot_summary.get("model")
        if mot_summary:
            parts.append(f"""
MOT SUMMARY:
Make/Model: {mot_summary.get('make', '?')} {mot_summary.get('model', '')}
Total Tests: {mot_summary.get('total_tests', 0)}
Passes: {mot_summary.get('total_passes', 0)}
Failures: {mot_summary.get('total_failures', 0)}
Current Mileage: {mot_summary.get('current_odometer', '?')} miles
First Used: {mot_summary.get('first_used_date', '?')}""")

    # Condition score
    condition = None
    if ev_check_data:
        condition = ev_check_data.get("condition_score")
    elif mot_analysis:
        condition = mot_analysis.get("condition_score")
    if condition is not None:
        parts.append(f"\nCONDITION SCORE: {condition}/100")

    # Clocking analysis
    clocking = {}
    if ev_check_data:
        clocking = ev_check_data.get("clocking_analysis") or {}
    elif mot_analysis:
        clocking = mot_analysis.get("clocking_analysis", {})
    parts.append(f"""
MILEAGE ANALYSIS:
Clocking Detected: {clocking.get('clocked', False)}
Risk Level: {clocking.get('risk_level', 'unknown')}""")
    for flag in clocking.get("flags", []):
        parts.append(f"  FLAG [{flag.get('severity', '').upper()}]: {flag.get('detail', '')}")

    # EV type
    if ev_check_data:
        parts.append(f"\nEV TYPE: {ev_check_data.get('ev_type', 'Unknown')}")

    # Full MOT history with defects
    mot_tests = []
    if mot_analysis:
        mot_tests = mot_analysis.get("mot_tests", [])
    elif ev_check_data:
        mot_tests = ev_check_data.get("mot_tests", [])
    if mot_tests:
        parts.append(f"\nFULL MOT HISTORY ({len(mot_tests)} tests, newest first):")
        for test in mot_tests[:10]:
            odo = f"{test.get('odometer', '?'):,} mi" if test.get('odometer') else "? mi"
            parts.append(f"\n  Test #{test.get('test_number', '?')} — {test.get('date', '?')} — {test.get('result', '?')} — {odo}")
            for a in test.get("advisories", []):
                parts.append(f"    ADVISORY: {a.get('text', '')}")
            for f in test.get("failures", []):
                parts.append(f"    FAILURE: {f.get('text', '')}")

    # Mileage timeline
    timeline = []
    if mot_analysis:
        timeline = mot_analysis.get("mileage_timeline", [])
    elif ev_check_data:
        timeline = ev_check_data.get("mileage_timeline", [])
    if timeline:
        parts.append("\nMILEAGE TIMELINE:")
        for r in timeline:
            parts.append(f"  {r.get('date', '?')}: {r.get('miles', 0):,} miles")

    # Failure patterns
    patterns = []
    if mot_analysis:
        patterns = mot_analysis.get("failure_patterns", [])
    elif ev_check_data:
        patterns = ev_check_data.get("failure_patterns", [])
    if patterns:
        parts.append("\nRECURRING DEFECT PATTERNS:")
        for p in patterns:
            parts.append(f"  {p['category']}: {p['occurrences']}x ({p['concern_level']} concern)")

    # Known specs lookup (free, no API cost)
    known_specs = _lookup_known_specs(make, model)
    if known_specs:
        parts.append(f"""
KNOWN MODEL SPECS (public data):
Battery Capacity: {known_specs['battery_kwh']} kWh
Official WLTP Range: {known_specs['official_range_miles']} miles
Max Rapid Charge: {known_specs['rapid_kw']} kW""")

    # Charging cost estimates (calculated, no API needed)
    if known_specs:
        consumption = known_specs["battery_kwh"] / known_specs["official_range_miles"]  # kWh/mile approx
        cost_home = round(consumption * HOME_RATE_PENCE, 1)
        cost_rapid = round(consumption * RAPID_RATE_PENCE, 1)
        annual_home = round(10000 * cost_home / 100)
        annual_rapid = round(10000 * cost_rapid / 100)
        petrol_annual = round(10000 * PETROL_COST_PER_MILE / 100)
        saving = petrol_annual - annual_home
        parts.append(f"""
ESTIMATED CHARGING COSTS (calculated from specs + UK avg rates):
Home rate: {HOME_RATE_PENCE}p/kWh (Ofgem cap)
Rapid rate: {RAPID_RATE_PENCE}p/kWh (UK avg public rapid)
Cost per mile (home): {cost_home}p
Cost per mile (rapid): {cost_rapid}p
Annual cost at 10k miles (home): £{annual_home}
Annual cost at 10k miles (rapid): £{annual_rapid}
vs Petrol saving: £{saving}/year""")

    parts.append(f"\nTODAY'S DATE: {datetime.utcnow().strftime('%d %B %Y')}")

    # Data sources
    source_keys = _collect_active_sources(vehicle_data, mot_analysis, ev_check_data)
    if source_keys:
        parts.append("\nDATA SOURCES USED (use [N] inline references in the report):")
        for i, key in enumerate(source_keys, 1):
            src = DATA_SOURCE_REGISTRY.get(key)
            if src:
                parts.append(f"  [{i}] {src['name']} ({src['site']}) — {src['desc']}")

    parts.append("\n=== END OF DATA ===")
    parts.append("\nWrite an EV buyer's report for this vehicle. This is a FREE preview — the full paid report (£7.99) includes real-world battery telemetry, detailed range scenarios, and AI lifespan prediction.")

    return "\n".join(parts)


async def generate_ev_preview_report(
    registration: str,
    vehicle_data: Optional[Dict] = None,
    mot_analysis: Optional[Dict] = None,
    ev_check_data: Optional[Dict] = None,
) -> Optional[str]:
    """Generate a FREE EV preview report using Claude.

    Uses only DVLA + MOT data. No paid API calls needed.
    Teases what the full paid report would include.
    """
    if not settings.ANTHROPIC_API_KEY or settings.ANTHROPIC_API_KEY.startswith("your_"):
        logger.warning("Anthropic API key not configured — using demo EV report")
        return _generate_demo_ev_report(registration, vehicle_data, mot_analysis, ev_check_data)

    context = _build_preview_context(registration, vehicle_data, mot_analysis, ev_check_data)

    user_prompt = f"""Generate a FREE EV Health Check preview report for {registration}.

{context}

Write the report in markdown with these exact sections:

## Should You Buy This EV?
Open with a clear, bold verdict: **BUY**, **NEGOTIATE**, or **AVOID**.
Then 2-3 sentences explaining WHY. Focus on what the MOT and mileage data tells you about
how this EV has been used and maintained.

## The Full Picture
Detailed analysis covering:
- What the MOT history reveals about this EV's condition
- Mileage pattern and what it means for battery wear (higher mileage = more charge cycles)
- Any EV-specific defects (battery cooling, charging port, regen braking issues)
- How the condition score compares to typical EVs of this age

## Charging & Running Costs
Using the specs and UK rates:
- Compare home charging (7kW) vs public rapid charging costs using a markdown table
- Calculate annual running cost at 10,000 miles per year
- Compare to equivalent petrol car (use table)
- Note that EVs have lower maintenance (no oil changes, less brake wear from regen)

## What You'd Learn in the Full Report
List what the paid £7.99 report adds:
- Real-world battery health score and degradation percentage (from telemetry data)
- Range across 27 temperature and driving scenarios
- Detailed battery and charging specifications
- AI-predicted remaining vehicle lifespan
- Full PDF report delivered to your email

Keep it 600-800 words. Every sentence should provide genuine value. Be specific with numbers.
If the car data is clean, say so — but still explain what the paid report would tell you about battery degradation."""

    try:
        client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
        message = await client.messages.create(
            model=settings.ANTHROPIC_MODEL,
            max_tokens=2000,
            system=PREVIEW_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_prompt}],
        )
        report = message.content[0].text

        # Append data sources footer
        source_keys = _collect_active_sources(vehicle_data, mot_analysis, ev_check_data)
        if source_keys:
            report += _build_sources_section(source_keys)

        logger.info(f"EV preview report generated for {registration} ({message.usage.input_tokens}+{message.usage.output_tokens} tokens)")
        return report
    except Exception as e:
        logger.error(f"EV preview report generation failed for {registration}: {e}")
        return _generate_demo_ev_report(registration, vehicle_data, mot_analysis, ev_check_data)


def _generate_demo_ev_report(
    registration: str,
    vehicle_data: Optional[Dict],
    mot_analysis: Optional[Dict],
    ev_check_data: Optional[Dict] = None,
) -> str:
    """Generate a demo EV report when Anthropic API key is not configured."""
    source_keys = _collect_active_sources(vehicle_data, mot_analysis, ev_check_data)
    ref = lambda key: _source_ref(source_keys, key)

    make = vehicle_data.get("make", "Unknown") if vehicle_data else "Unknown"
    year = vehicle_data.get("yearOfManufacture", "Unknown") if vehicle_data else "Unknown"
    fuel = vehicle_data.get("fuelType", "Unknown") if vehicle_data else "Unknown"

    model = ""
    mot_summary = {}
    if mot_analysis:
        mot_summary = mot_analysis.get("mot_summary", {})
        model = mot_summary.get("model", "")

    total_tests = mot_summary.get("total_tests", 0)
    total_passes = mot_summary.get("total_passes", 0)
    total_failures = mot_summary.get("total_failures", 0)
    current_mileage = mot_summary.get("current_odometer", "Unknown")

    condition = None
    clocking = {}
    if ev_check_data:
        condition = ev_check_data.get("condition_score")
        clocking = ev_check_data.get("clocking_analysis") or {}
    elif mot_analysis:
        condition = mot_analysis.get("condition_score")
        clocking = mot_analysis.get("clocking_analysis", {})

    clocked = clocking.get("clocked", False)
    pass_rate = round(total_passes / total_tests * 100) if total_tests > 0 else 0

    known_specs = _lookup_known_specs(make, model)

    # Determine verdict
    if clocked:
        verdict = "AVOID"
    elif condition and condition < 50:
        verdict = "AVOID"
    elif total_failures > 2 or (condition and condition < 70):
        verdict = "NEGOTIATE"
    else:
        verdict = "BUY"

    report = "## Should You Buy This EV?\n"

    if verdict == "BUY":
        report += f"**BUY** — This {year} {_format_make(make)} {model}{ref('dvla_ves')} is a solid choice. "
        if condition and condition >= 80:
            report += f"With a condition score of {condition}/100 and a {pass_rate}% MOT pass rate across {total_tests} tests{ref('dvsa_mot')}, this EV has been well maintained. "
        else:
            report += f"The condition score of {condition}/100 is reasonable for its age. "
        if not clocked:
            report += "Mileage readings are consistent with no signs of tampering.\n"
    elif verdict == "NEGOTIATE":
        report += f"**NEGOTIATE** — This {year} {_format_make(make)} {model}{ref('dvla_ves')} has some issues worth discussing. "
        report += f"A condition score of {condition}/100 and {total_failures} MOT failure(s){ref('dvsa_mot')} give you leverage to negotiate.\n"
    else:
        report += f"**AVOID** — This {year} {_format_make(make)} {model}{ref('dvla_ves')} raises serious concerns. "
        if clocked:
            report += "Mileage discrepancies have been detected — on an EV, this could hide significant battery degradation.\n"
        else:
            report += f"The condition score of {condition}/100 and MOT history suggest this car has not been well maintained.\n"

    # Full Picture
    report += "\n## The Full Picture\n"
    if total_tests > 0:
        report += f"This EV has been through {total_tests} MOT tests{ref('dvsa_mot')}, passing {total_passes} ({pass_rate}%). "

    try:
        miles_int = int(current_mileage) if current_mileage != "Unknown" else None
    except (ValueError, TypeError):
        miles_int = None

    if miles_int and isinstance(year, int):
        age = datetime.utcnow().year - year
        if age > 0:
            annual = miles_int // age
            report += f"At {miles_int:,} miles over {age} years (~{annual:,}/year), "
            if annual < 8000:
                report += "this is low mileage for an EV — fewer charge cycles means the battery should be in good shape. "
            elif annual < 12000:
                report += "this is average mileage. The battery will have experienced normal degradation for its age. "
            else:
                report += "this is above-average mileage. Higher mileage means more charge cycles and potentially more battery degradation — the full report's battery health score would tell you exactly how much. "

    report += "\nEVs generally have fewer MOT issues than petrol/diesel cars — no exhaust, simpler drivetrain, regenerative braking reduces brake wear. "
    report += "Key things to watch for in an EV's MOT history are: tyre wear (EVs are heavier), suspension components, and any warnings related to the high-voltage system.\n"

    # Charging & Running Costs
    report += "\n## Charging & Running Costs\n"
    if known_specs:
        consumption = known_specs["battery_kwh"] / known_specs["official_range_miles"]
        cost_home = round(consumption * HOME_RATE_PENCE, 1)
        cost_rapid = round(consumption * RAPID_RATE_PENCE, 1)
        annual_home = round(10000 * cost_home / 100)
        annual_rapid = round(10000 * cost_rapid / 100)
        petrol_annual = round(10000 * PETROL_COST_PER_MILE / 100)
        saving = petrol_annual - annual_home

        report += f"Based on the {_format_make(make)} {model}'s {known_specs['battery_kwh']} kWh battery and {known_specs['official_range_miles']}-mile WLTP range:\n\n"
        report += "| Charging Method | Cost/Mile | Annual (10k mi) |\n"
        report += "|---|---|---|\n"
        report += f"| Home (7kW, {HOME_RATE_PENCE}p/kWh) | **{cost_home}p** | **£{annual_home}** |\n"
        report += f"| Public Rapid ({RAPID_RATE_PENCE}p/kWh) | **{cost_rapid}p** | **£{annual_rapid}** |\n"
        report += f"| Equivalent Petrol | ~{PETROL_COST_PER_MILE}p | ~£{petrol_annual} |\n"
        report += f"\n**Annual saving vs petrol: ~£{saving}** — this EV will pay back the difference in running costs over time.\n"
        report += f"\nEV maintenance is also cheaper: no oil changes, no exhaust repairs, less brake wear thanks to regenerative braking. Budget around £100-200/year for annual service vs £250-400 for a petrol equivalent.\n"
    else:
        report += "We don't have exact specs for this model in our database, but typical EV running costs are:\n\n"
        report += "| Item | EV | Petrol |\n"
        report += "|---|---|---|\n"
        report += f"| Fuel/Charging per mile | 5-8p (home) | ~{PETROL_COST_PER_MILE}p |\n"
        report += f"| Annual fuel (10k mi) | £500-800 | ~£{round(10000 * PETROL_COST_PER_MILE / 100)} |\n"
        report += "| Annual service | £100-200 | £250-400 |\n"
        report += "| Road tax | £0 (pre-2025 EVs) | £165-590 |\n"

    # What you'd learn
    report += "\n## What You'd Learn in the Full Report\n"
    report += "The free check covers DVLA and MOT data. The **full EV Health Report (£7.99)** adds:\n\n"
    report += "- **Battery Health Score** — actual degradation percentage based on telemetry data, not estimates\n"
    report += "- **Real-World Range** — tested across 27 temperature and driving scenarios (e.g. winter motorway: expect 30-40% less than WLTP)\n"
    report += "- **Detailed Battery Specs** — capacity, charge speeds, charging times for home and rapid\n"
    report += "- **AI Lifespan Prediction** — predicted remaining years and miles based on the vehicle's condition\n"
    report += "- **Expert AI Verdict** — comprehensive written analysis delivered as a PDF to your email\n"
    report += "\nFor a used EV, battery health is the single most important factor. A new battery can cost £5,000-£20,000+ depending on the model — knowing the actual degradation before you buy is worth far more than £7.99.\n"

    # Data Sources
    if source_keys:
        report += _build_sources_section(source_keys)

    return report


# ─── PAID FULL REPORT ────────────────────────────────────────────────

PAID_SYSTEM_PROMPT = """You are VeriCar's EV specialist — an expert in electric vehicle battery health,
range estimation, and total cost of ownership. You write clear, authoritative reports for UK consumers
buying used electric vehicles.

The buyer has paid £7.99 for this premium EV Health Check report. You have access to battery health
telemetry, real-world range data, detailed EV specifications, and AI lifespan predictions.

Your report must be practical, honest, and focused on what matters most to EV buyers:
1. Is the battery healthy? How much range has been lost?
2. What's the real-world range in different conditions?
3. How much will it cost to charge at home vs public chargers?
4. How long will this vehicle last?

Use UK units (miles, £), reference UK electricity rates, and be specific with numbers.
Keep the tone professional but accessible — avoid jargon.

IMPORTANT: Use numbered inline references [1], [2], etc. to cite data sources.
Use markdown tables for cost comparisons."""


async def generate_ev_report(
    registration: str,
    vehicle_data: Optional[Dict] = None,
    mot_analysis: Optional[Dict] = None,
    ev_check_data: Optional[Dict] = None,
) -> Optional[str]:
    """Generate a PAID full EV report using Claude."""
    if not settings.ANTHROPIC_API_KEY:
        logger.warning("Anthropic API key not configured, skipping EV report")
        return None

    context = _build_ev_context(registration, vehicle_data, mot_analysis, ev_check_data)

    user_prompt = f"""Generate a comprehensive paid EV Health Check report for {registration}.

Here is all the data we have on this vehicle:

{context}

Write the report in markdown with these exact sections:

## Should You Buy This EV?
Open with a clear, bold verdict: **BUY**, **NEGOTIATE**, or **AVOID**.
Then 2-3 sentences explaining WHY in plain language.

## Battery Health Verdict
Rate the battery health and explain what the degradation means in practical terms.
Reference the battery health score and grade. Explain what this means for real-world usage.

## Range Reality Check
Compare the official range vs estimated real-world range.
Use a markdown table showing range in different scenarios (summer city, winter motorway, etc.)
Explain how temperature, driving style, and age affect range.

## Charging & Running Costs
Use markdown tables to compare:
- Home charging (7kW) vs public rapid charging costs
- Annual running cost at 10,000 miles per year
- Comparison to equivalent petrol car

## Ownership Forecast
Based on the vehicle age, mileage, and battery data, predict:
- Expected remaining battery lifespan (years and miles)
- Key maintenance items for EVs
- Whether this is a good time to buy this model

## Negotiation Points
Give the buyer 3-4 specific talking points based on the data to negotiate the price.

## Verdict
Give a clear BUY / NEGOTIATE / AVOID recommendation with 2-3 key reasons.

Keep it 800-1200 words. Be specific with numbers and costs."""

    try:
        client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
        message = await client.messages.create(
            model=settings.ANTHROPIC_MODEL,
            max_tokens=2500,
            system=PAID_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_prompt}],
        )
        report = message.content[0].text

        # Append data sources footer
        source_keys = _collect_active_sources(vehicle_data, mot_analysis, ev_check_data)
        if source_keys:
            report += _build_sources_section(source_keys)

        logger.info(f"EV paid report generated for {registration} ({len(report)} chars)")
        return report
    except Exception as e:
        logger.error(f"EV report generation failed for {registration}: {e}")
        return None


def _build_ev_context(
    registration: str,
    vehicle_data: Optional[Dict],
    mot_analysis: Optional[Dict],
    ev_check_data: Optional[Dict],
) -> str:
    """Build a text context block from all available EV data (paid report)."""
    parts = [f"=== PAID EV HEALTH CHECK DATA FOR {registration} ===\n"]

    if vehicle_data:
        parts.append(f"""VEHICLE (DVLA):
Make: {vehicle_data.get('make', '?')}
Fuel Type: {vehicle_data.get('fuelType', '?')}
Year: {vehicle_data.get('yearOfManufacture', '?')}
Colour: {vehicle_data.get('colour', '?')}""")

    if mot_analysis:
        summary = mot_analysis.get("mot_summary", {})
        if summary:
            parts.append(f"""
MOT SUMMARY:
Make/Model: {summary.get('make', '?')} {summary.get('model', '')}
Total Tests: {summary.get('total_tests', 0)}
Passes: {summary.get('total_passes', 0)}
Failures: {summary.get('total_failures', 0)}
Current Mileage: {summary.get('current_odometer', '?')} miles""")

    if ev_check_data:
        # Battery health
        bh = ev_check_data.get("battery_health")
        if bh and bh.get("score"):
            parts.append(f"""
BATTERY HEALTH (telemetry):
Score: {bh['score']}/100
Grade: {bh.get('grade', 'N/A')}
Degradation: {bh.get('degradation_estimate_pct', 'N/A')}%
Summary: {bh.get('summary', 'N/A')}""")

        # Range
        re_data = ev_check_data.get("range_estimate")
        if re_data:
            parts.append(f"""
RANGE ESTIMATE:
Official WLTP: {re_data.get('official_range_miles', 'N/A')} miles
Real-World Estimate: {re_data.get('estimated_range_miles', 'N/A')} miles
Range Retention: {re_data.get('range_retention_pct', 'N/A')}%
Worst Case: {re_data.get('worst_case_miles', 'N/A')} miles
Best Case: {re_data.get('best_case_miles', 'N/A')} miles""")

        # Scenarios
        scenarios = ev_check_data.get("range_scenarios", [])
        if scenarios:
            parts.append("\nRANGE SCENARIOS:")
            for s in scenarios:
                parts.append(f"  {s.get('scenario', '')}: {s.get('estimated_miles', 'N/A')} mi "
                           f"(temp: {s.get('temperature_c', '?')}°C, style: {s.get('driving_style', '?')})")

        # Specs
        specs = ev_check_data.get("ev_specs")
        if specs:
            parts.append(f"""
EV SPECIFICATIONS:
Battery: {specs.get('battery_capacity_kwh', 'N/A')} kWh total, {specs.get('usable_capacity_kwh', 'N/A')} kWh usable
Type: {specs.get('battery_type', 'N/A')}
DC Max: {specs.get('max_dc_charge_kw', 'N/A')} kW
AC Max: {specs.get('max_ac_charge_kw', 'N/A')} kW
Home (7kW): {specs.get('charge_time_home_hours', 'N/A')} hours
Rapid 10-80%: {specs.get('charge_time_rapid_mins', 'N/A')} mins
Consumption: {specs.get('energy_consumption_kwh_per_mile', 'N/A')} kWh/mile""")

        # Charging costs
        cc = ev_check_data.get("charging_costs")
        if cc:
            parts.append(f"""
CHARGING COSTS:
Home cost/mile: {cc.get('cost_per_mile_home', 'N/A')}p
Rapid cost/mile: {cc.get('cost_per_mile_rapid', 'N/A')}p
Annual home: £{cc.get('annual_cost_estimate_home', 'N/A')}
Annual rapid: £{cc.get('annual_cost_estimate_rapid', 'N/A')}
vs Petrol saving: £{cc.get('vs_petrol_annual_saving', 'N/A')}/year""")

        # Lifespan
        lp = ev_check_data.get("lifespan_prediction")
        if lp:
            parts.append(f"""
LIFESPAN PREDICTION:
Remaining years: {lp.get('predicted_remaining_years', 'N/A')}
Remaining miles: {lp.get('predicted_remaining_miles', 'N/A')}
Condition: {lp.get('overall_condition', 'N/A')}
Risk factors: {', '.join(lp.get('risk_factors', []))}""")

    parts.append(f"\nTODAY'S DATE: {datetime.utcnow().strftime('%d %B %Y')}")

    # Data sources
    source_keys = _collect_active_sources(vehicle_data, mot_analysis, ev_check_data)
    if source_keys:
        parts.append("\nDATA SOURCES USED (use [N] inline references in the report):")
        for i, key in enumerate(source_keys, 1):
            src = DATA_SOURCE_REGISTRY.get(key)
            if src:
                parts.append(f"  [{i}] {src['name']} ({src['site']}) — {src['desc']}")

    parts.append("\n=== END OF DATA ===")
    parts.append("\nREPORT TIER: PAID EV HEALTH CHECK (£7.99)")

    return "\n".join(parts)
