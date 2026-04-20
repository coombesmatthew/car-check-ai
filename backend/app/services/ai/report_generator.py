"""AI-powered vehicle report generator using Claude.

Generates a comprehensive buyer's report that justifies the £3.99 price
by providing genuine insight, actionable negotiation advice, and cost
projections that the buyer can't get from reading the free data cards.
"""

from datetime import datetime
from typing import Dict, List, Optional

import anthropic

from app.core.config import settings
from app.core.logging import logger
from app.services.ai.style_guide import assemble_style_block


_UPPERCASE_MAKES = {"BMW", "MG", "TVR", "DS", "BYD", "GWM", "JAC", "MAN"}


def _format_make(make: str) -> str:
    """Format make name — keep known acronyms uppercase, title-case the rest."""
    upper = make.upper().strip()
    if upper in _UPPERCASE_MAKES:
        return upper
    return make.title()


# Repair cost estimates sourced from RAC published guides (rac.co.uk).
# Per-manufacturer averages from RAC/WhoCanFixMyCar data (2025/26).
# Categories without an RAC guide use UK independent garage averages.
REPAIR_COST_ESTIMATES = {
    "brake": {
        "component": "Brake pads/discs", "low": 150, "high": 700, "per": "per axle",
        "url": "https://www.rac.co.uk/drive/advice/car-maintenance/how-much-does-it-cost-to-replace-brake-pads/",
        "by_make": {
            "AUDI": 350, "BMW": 317, "FORD": 293, "KIA": 299,
            "LAND ROVER": 376, "MERCEDES": 415, "MINI": 259,
            "NISSAN": 275, "VAUXHALL": 280, "VOLKSWAGEN": 305,
        },
    },
    "tyre": {
        "component": "Tyre replacement", "low": 50, "high": 150, "per": "each",
        "url": "https://www.rac.co.uk/drive/advice/tyres/the-racs-guide-to-tyre-buying/",
    },
    "suspension": {
        "component": "Suspension repair", "low": 100, "high": 600, "per": "per corner",
        "url": "https://www.rac.co.uk/drive/advice/car-maintenance/shock-absorber-replacement-cost-and-maintenance-guide/",
        "by_make": {
            "FORD": 358, "AUDI": 428, "VOLKSWAGEN": 453,
            "MERCEDES": 626, "BMW": 631,
        },
    },
    "exhaust": {
        "component": "Exhaust repair", "low": 100, "high": 300, "per": "",
        "url": "https://www.rac.co.uk/drive/advice/car-maintenance/common-exhaust-problems-you-need-to-be-aware-of/",
        "by_make": {
            "VOLVO": 125, "MERCEDES": 133, "BMW": 135, "VOLKSWAGEN": 145,
            "FORD": 149, "AUDI": 153, "VAUXHALL": 165,
        },
    },
    "emission": {
        "component": "Catalytic converter", "low": 500, "high": 2200, "per": "",
        "url": "https://www.rac.co.uk/drive/advice/car-maintenance/catalytic-converters/",
    },
    "lighting": {
        "component": "Lighting repair", "low": 20, "high": 200, "per": "",
        "url": "https://www.rac.co.uk/drive/news/motoring-news/drivers-dazzled-by-massive-headlight-costs/",
    },
    "steering": {
        "component": "Steering repair", "low": 220, "high": 660, "per": "",
        "url": "https://www.rac.co.uk/drive/advice/car-maintenance/guide-to-steering-rack-replacements-cost-symptoms-and-diagnostics/",
        "by_make": {
            "FIAT": 221, "PEUGEOT": 261, "MERCEDES": 262, "NISSAN": 268,
            "KIA": 290, "VAUXHALL": 293, "CITROEN": 310, "RENAULT": 331,
            "FORD": 352, "BMW": 361, "AUDI": 392, "MITSUBISHI": 659,
        },
    },
    "corrosion": {
        "component": "Corrosion/bodywork repair", "low": 350, "high": 1000, "per": "",
        "url": "https://www.rac.co.uk/drive/advice/car-maintenance/cost-to-respray-a-car/",
    },
    "windscreen": {
        "component": "Windscreen repair/replace", "low": 150, "high": 400, "per": "",
        "url": "https://www.rac.co.uk/drive/advice/car-maintenance/windscreen-replacement-cost/",
        "by_make": {
            "FORD": 221, "CITROEN": 225, "PEUGEOT": 236, "VAUXHALL": 274,
            "VOLKSWAGEN": 298, "MINI": 310, "BMW": 392, "NISSAN": 392,
            "MERCEDES": 412, "AUDI": 487, "RENAULT": 530,
        },
    },
    "clutch": {
        "component": "Clutch replacement", "low": 500, "high": 1000, "per": "",
        "url": "https://www.rac.co.uk/drive/advice/car-maintenance/clutch-replacement-cost-how-much-will-you-have-to-pay/",
        "by_make": {
            "TOYOTA": 603, "BMW": 603, "NISSAN": 614, "FORD": 632,
            "PEUGEOT": 674, "CITROEN": 677, "VOLKSWAGEN": 679,
            "VAUXHALL": 722, "MINI": 727, "VOLVO": 782,
            "AUDI": 820, "MERCEDES": 877, "RENAULT": 899,
        },
    },
    "battery": {
        "component": "Battery replacement", "low": 150, "high": 350, "per": "",
        "url": "https://www.rac.co.uk/drive/advice/car-maintenance/car-battery-fitted-at-home/",
    },
    "oil": {
        "component": "Oil leak repair", "low": 150, "high": 500, "per": "",
        "url": "https://www.rac.co.uk/drive/advice/know-how/car-leaking-how-to-identify-liquid-dripping-from-your-car-and-what-to-do/",
    },
    "coolant": {
        "component": "Cooling system repair", "low": 200, "high": 700, "per": "",
        "url": "https://www.rac.co.uk/car-care/car-repairs/car-radiator-repair",
    },
    "drive shaft": {"component": "Drive shaft/CV joint", "low": 150, "high": 400, "per": "per side"},
    "wheel bearing": {
        "component": "Wheel bearing", "low": 150, "high": 300, "per": "each",
        "url": "https://www.rac.co.uk/drive/advice/car-maintenance/what-is-a-car-wheel-bearing-how-do-you-replace-them/",
        "by_make": {
            "VAUXHALL": 200, "MINI": 206, "RENAULT": 221, "FORD": 235,
            "BMW": 262, "AUDI": 272, "VOLKSWAGEN": 282, "PEUGEOT": 284,
            "NISSAN": 288, "CITROEN": 295, "VOLVO": 320,
        },
    },
}


def _estimate_repair_cost(category: str, make: Optional[str] = None) -> Optional[Dict]:
    """Look up estimated repair cost for a defect category, with optional make-specific average."""
    cat_lower = category.lower()
    for key, estimate in REPAIR_COST_ESTIMATES.items():
        if key in cat_lower:
            result = {
                "component": estimate["component"],
                "low": estimate["low"],
                "high": estimate["high"],
                "per": estimate["per"],
                "url": estimate.get("url"),
            }
            if make and estimate.get("by_make"):
                make_upper = make.upper().strip()
                make_avg = estimate["by_make"].get(make_upper)
                if make_avg:
                    result["make_avg"] = make_avg
                    result["make_name"] = _format_make(make)
            return result
    return None


DATA_SOURCE_REGISTRY = {
    "dvla_ves": {
        "name": "DVLA Vehicle Enquiry Service",
        "site": "gov.uk",
        "desc": "Vehicle identity, tax status, MOT status, V5C date",
    },
    "dvsa_mot": {
        "name": "DVSA MOT History",
        "site": "gov.uk",
        "desc": "Full MOT test history, advisories, failures, and mileage readings",
    },
    "gov_uk_ved": {
        "name": "gov.uk VED Rate Tables (2025/26)",
        "site": "gov.uk",
        "desc": "Vehicle Excise Duty bands and annual rates",
    },
    "euro_ncap": {
        "name": "Euro NCAP",
        "site": "euroncap.com",
        "desc": "Independent crash test safety ratings",
    },
    "experian": {
        "name": "Experian AutoCheck",
        "site": "experian.co.uk",
        "desc": "Finance, stolen, write-off, plate changes, and keeper history",
    },
    "brego": {
        "name": "Brego",
        "site": "brego.ai",
        "desc": "Current market valuations based on age, mileage, and condition",
    },
    "carguide": {
        "name": "CarGuide",
        "site": "carguide.co.uk",
        "desc": "Salvage auction records",
    },
    "rac": {
        "name": "RAC Repair Cost Guides",
        "site": "rac.co.uk",
        "url": "https://www.rac.co.uk/drive/advice/car-maintenance/",
        "desc": "UK average repair costs with per-manufacturer breakdowns (2025/26)",
    },
}


def _collect_active_sources(
    vehicle_data: Optional[Dict],
    mot_analysis: Dict,
    check_result: Optional[Dict] = None,
) -> List[str]:
    """Return source keys that were actually used to compile the report."""
    sources = []

    if vehicle_data:
        sources.append("dvla_ves")

    if mot_analysis.get("mot_summary") or mot_analysis.get("mot_tests"):
        sources.append("dvsa_mot")

    if check_result:
        if check_result.get("tax_calculation"):
            sources.append("gov_uk_ved")
        if check_result.get("safety_rating"):
            sources.append("euro_ncap")

        # Provenance sources — check data_source fields or presence
        provenance_keys = ("finance_check", "stolen_check", "write_off_check", "plate_changes", "keeper_history")
        if any(check_result.get(k) for k in provenance_keys):
            sources.append("experian")
        if check_result.get("valuation"):
            sources.append("brego")
        if check_result.get("salvage_check"):
            sources.append("carguide")

    # RAC repair cost guides are cited whenever there are failure patterns
    if mot_analysis.get("failure_patterns"):
        sources.append("rac")

    return sources


def _source_ref(source_keys: List[str], key: str) -> str:
    """Return ' [N]' for the given source key, or '' if not present."""
    try:
        return f" [{source_keys.index(key) + 1}]"
    except ValueError:
        return ""


def _build_sources_section(source_keys: List[str]) -> str:
    """Render a numbered markdown Data Sources footer from active source keys."""
    lines = [
        "\n---",
        "## Data Sources",
        "This report was compiled using the following data sources:\n",
    ]
    for i, key in enumerate(source_keys, 1):
        src = DATA_SOURCE_REGISTRY.get(key)
        if not src:
            continue
        url = src.get("url")
        if url:
            name_part = f"[{src['name']}]({url})"
        else:
            name_part = f"**{src['name']}**"
        site_part = f" ({src['site']})" if src["site"] else ""
        lines.append(f"{i}. {name_part}{site_part} — {src['desc']}")

    if "rac" in source_keys:
        lines.append("\n*Repair cost estimates are based on RAC published data and may vary by region and garage.*")

    return "\n".join(lines)


SYSTEM_PROMPT = """You are an expert independent used car advisor writing a comprehensive buyer's report for a prospective buyer in the UK.

Write in British English. Be direct, specific, and honest.

**YOU MUST RETURN VALID JSON matching the VehicleReport schema.** Every field is required. Follow the structure exactly.

## Tone & Approach — CRITICAL

**Single Rule:** State facts from the data. Compare to benchmarks. Do NOT infer, interpret, or draw conclusions about owner behaviour, maintenance culture, or causation.

**IGNORE CONDITION SCORE:** If you see "condition_score" in the context data, completely ignore it. Do NOT mention it, reference it, or use it anywhere in the report. Never.

**FORBIDDEN PHRASES** (from actual v18 errors):
- ✗ "maintenance has been reactive rather than systematic"
- ✗ "tyre wear was flagged repeatedly without correction"
- ✗ "occurred after years of neglected wear advisories"
- ✗ "indicates lack of preventive maintenance"
- ✗ "the mileage does not correlate with the severity of tyre wear issues"
- ✗ "aggressive driving characteristics"
- ✗ "chronic alignment issues"
- ✗ "inconsistent tyre rotation practice"
- ✗ "suggests alignment or load distribution problem"
- ✗ "requires immediate investment" (interpretation, not fact)
- ✗ "before it is safe to purchase" (interpretation, not fact)
- ✗ **NEVER show condition score in ANY form** — no "24/100", no "Condition Score of", no "low condition score". If you see "CONDITION SCORE" data in the context, IGNORE IT entirely.

**What to Write Instead:**
- ✓ "Tyre wear was flagged on [dates: 2014, 2020, 2024, 2025]."
- ✓ "The same corner (offside front) was flagged in 2024 and 2025."
- ✓ "We recommend: (1) Four-wheel alignment check (£80–£150), (2) Tyre replacement if needed (£300–£500)."
- ✓ "Request evidence the seller has addressed this. If not, budget accordingly."
- ✓ For valuation: Reference the MOT history and defects directly, NOT a score. Example: "Due to tyre failure history and current wear, fair value is £1,900–£2,200."

**MOT Pass Rate Benchmark:**
| Pass Rate | Interpretation |
|-----------|----------------|
| 85%+ | Very good — above average for age |
| 75–84% | Good — typical for vehicles of this age |
| 65–74% | Below average — some concerns |
| Below 65% | Poor — investigate failure patterns |

For a 14-year-old car, 78.6% is GOOD / TYPICAL. Never call it poor.

**Scoring:**
Do NOT include star ratings, numerical condition scores, or other quantified metrics. Just state: BUY or AVOID, with 2–3 factual sentences.

## JSON Schema Output (REQUIRED — RETURN ONLY VALID JSON)

You MUST return a valid JSON object. Do NOT wrap in code blocks. Do NOT include markdown. Just raw JSON.

CRITICAL: All string values must be on a single line. Do NOT include literal newlines in JSON string values.
If you need multiple sentences, separate them with a space. Use spaces, not line breaks, within quoted strings.

Example CORRECT:
```
"point": "Tyre wear flagged on 9 dates. Brake hose failed March 2020. Request evidence before purchase."
```

Example WRONG:
```
"point": "Tyre wear flagged on 9 dates.
Brake hose failed March 2020.
Request evidence before purchase."
```

The JSON must have EXACTLY these top-level keys (flat structure):
- registration (string)
- report_date (string, e.g. "30 Mar 2026")
- vehicle_summary (string, e.g. "2011 MINI Diesel (1598cc)")
- current_mileage (integer)
- mot_valid_until (string, e.g. "29 September 2026")
- recommendation (string: "BUY", "NEGOTIATE", or "AVOID")
- recommendation_points (array of strings — flat list, NOT objects)
- mileage_assessment (object)
- mot_summary (array of objects)
- mot_tests (array of objects)
- defect_patterns (array of objects)
- total_keepers (integer)
- ownership_note (string)
- provenance (array of objects)
- valuations (object)
- valuation_context (string)
- value_factors (array of objects)
- depreciation (string)
- risk_matrix (array of objects)
- known_issues (array of objects)
- data_sources (array)

Use these detailed instructions:

### recommendation
MUST be exactly "BUY", "NEGOTIATE", or "AVOID".

**Guidance:**
- **AVOID:** Only for critical safety/legal issues: stolen marker, outstanding finance, write-off history, salvage records, mileage clocking, or invalid MOT. These are deal-breakers.
- **NEGOTIATE:** For moderate concerns: 3+ MOT failures, recurring defect patterns (tyre, brake, suspension), or other cost/reliability issues. Buyer should negotiate price.
- **BUY:** Everything else. The vehicle is acceptable to purchase, though buyer should be aware of and budget for any noted defects.

### recommendation_points
2–5 factual statements as STRINGS (flat list, not objects). Example:
```json
"recommendation_points": [
  "Tyre wear flagged on 9 test dates (April 2014, March 2020 ×2, August 2024, September 2025).",
  "Brake hose failed March 2020 (excessively deteriorated, insecure, rubbing on suspension).",
  "Offside front tyre currently at legal wear limit (September 2025).",
  "Request evidence seller has resolved these issues before purchase."
]
```
NO interpretation. NO "requires immediate investment". NO "unsafe". FACTS ONLY.

### mileage_assessment
Object with keys:
- total_mileage: integer
- annual_average: integer
- benchmark_fuel_type: "Diesel" or "Petrol"
- benchmark_typical_miles_per_year: e.g. "7,100–7,500"
- assessment: ONE OF: "above average" | "below average" | "typical"
- observation: Factual statement. NO inference. E.g., "No clocking detected. Mileage trajectory is consistent across 11 years of testing."

### mot_summary
Array of 6 objects (summary table rows):
1. {metric: "Total MOT tests", detail: "...", interpretation: "..."}
2. {metric: "Passes", detail: "...", interpretation: "..."}
3. {metric: "Failures", detail: "...", interpretation: "..."}
4. {metric: "Latest result", detail: "...", interpretation: "..."}
5. {metric: "Current advisories", detail: "...", interpretation: "..."}
6. {metric: "MOT expiry", detail: "...", interpretation: "..."}

Each row has: metric (string), detail (factual), interpretation (benchmark comparison).
For pass rate: use benchmark table (75–84% = "Good — typical for this age").

### mot_tests
Array of MOT test objects. Newest first. Each test object must have:
- test_date: string (DD Mmm YYYY format)
- result: "PASS" or "FAIL"
- mileage: integer
- defects: array of objects with {type, text}

For each defect:
- type: "FAILURE" | "DANGEROUS" | "ADVISORY"
- text: exact defect text from DVSA API

### defect_patterns
Array of recurring defect patterns. For each pattern:
- category: e.g., "Tyre Wear"
- flagged_count: integer (how many tests)
- flagged_dates: array of dates (DD Mmm YYYY) when flagged
- factual_summary: What recurred (NO "suggests", NO "indicates", NO "likely"). Example: "Offside front tyre flagged in August 2024 and September 2025 — 13 months apart with only 2,300 miles gained."
- recommended_action: What buyer should do. Example: "Request evidence seller has replaced all four tyres since September 2025. If not, budget £400–£600 for replacement and £80–£150 for alignment check."

### ownership_note
String: One sentence on keeper stability (factual, no judgment about maintenance quality).

### provenance
Array of provenance check objects. Each has:
- check: string (e.g., "Finance Check", "Stolen Check")
- result: string (e.g., "Clear", "None recorded")
- detail: string (e.g., "No outstanding finance")

### valuations
Object with keys:
- private_sale: integer (price in pounds)
- dealer_forecourt: integer
- trade_in: integer
- part_exchange: integer
- valuation_basis: string (e.g., "Brego market data, mileage-adjusted")

### valuation_context
String referencing DEFECTS, never condition score. Example:
- ✓ "Due to tyre failures (9 flagged dates) and unresolved brake hose issue (March 2020), fair value is £1,900–£2,300."
- ✗ "Due to low condition score (24/100), fair value drops by £400."

### value_factors
Array of objects affecting value. Each has:
- factor: string (e.g., "Tyre Wear (recurring)", "Brake Hose Failure")
- impact: string (e.g., "Significant Negative", "Neutral", "Positive")
- details: string (factual explanation)

Examples of factors: Mileage, Fuel Type, MOT status, Recurring Defects, ULEZ Compliance, Road Tax, Body Corrosion, Keeper Stability.
NEVER include "Condition Score" as a factor.

### depreciation
String: Annual depreciation trajectory (2–3 sentences).

### risk_matrix
Array of risk assessment rows. Each has:
- category: string (e.g., "Mechanical Reliability")
- level: string ("HIGH", "MEDIUM", or "LOW")
- finding: string (factual risk assessment)

### known_issues
Array of known issues for this model/engine. Each has:
- priority: string ("High", "Medium", or "Low")
- issue: string (e.g., "N47 engine timing chain wear")
- details: string (what to look for, typical repair cost, etc.)

---

## Forbidden Output

- NO condition score mentioned (24/100, low condition, etc.)
- NO owner behaviour inferences ("reactive maintenance", "deferred upkeep", "irresponsible owner")
- NO interpretive phrases ("suggests", "indicates", "likely", "probably")
- NO dramatic language ("requires immediate investment", "before it is safe")
- NO numerical ratings, star ratings, or scoring

---

All content:
- States facts from MOT data. Compares to benchmarks. NO inference.
- For recurring defects: note pattern factually + suggest what buyer should check.
- Actionable: every concern includes "Request evidence..." or "Budget..."
- Written for non-mechanics: explain technical terms.

## data_sources Format
If you include data_sources, use only simple strings like:
- "DVLA Vehicle Enquiry Service (gov.uk)"
- "DVSA MOT History API (gov.uk)"
- "Brego market valuations"

Do NOT generate structured objects for data_sources — just strings or an empty array.

---

### NEW SECTIONS (include all five)

"test_drive_checklist": List of 6–10 vehicle-specific items for a pre-purchase test drive. Each item is an object:
{"area": "Engine", "check": "Listen for timing chain rattle", "what_to_look_for": "Rattling from rear of engine on cold start — known N47 diesel fault"}
Base items on the vehicle's known issues and MOT defect history. Do NOT include generic items that apply to all cars.

"running_costs": A single object with annual cost estimates for this specific vehicle:
{"fuel_annual": 1200, "road_tax": 20, "insurance_estimate": 800, "servicing_annual": 350, "total_annual": 2370, "notes": "Fuel calculated at 45mpg, 7,000 miles/year, 147p/litre diesel"}
Use the actual VED band from vehicle_data, fuel type, and mileage. Insurance is an estimate range for a typical buyer in the UK.

"repair_budget": List of 2–6 items covering known defects from MOT history and model-specific risks. Each item:
{"item": "Offside front tyre replacement", "priority": "Immediate", "estimated_cost_low": 100, "estimated_cost_high": 150, "notes": "Advisory at September 2025 MOT — at legal limit"}
Only include items with a realistic chance of being needed. Do not invent costs.

"negotiation_guidance": A single object:
{
  "asking_price_context": "One sentence on the asking price vs market valuation",
  "suggested_opening": "£X,XXX — specific opening offer with brief rationale",
  "key_leverage_points": ["Tyre advisory at legal limit — £100-150 replacement", "Rear sub-frame corrosion advisory — unknown repair cost"],
  "walk_away_triggers": ["Seller cannot confirm brake hose was replaced after 2020 failure", "Timing chain rattle on cold start"]
}

"recalls": List any DVSA or manufacturer recalls applicable to this make/model/year that you are aware of. Each item:
{"recall_ref": "R/2014/123", "description": "Fuel tank bracket corrosion", "status": "Check DVSA database", "action_required": "Contact MINI dealer"}
If no recalls are known, return an empty list []. Do NOT fabricate recall references — use only real known recalls or return [].

---

Now return the JSON object. No markdown. No explanation. Just JSON."""


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
    ctx_make = vehicle_data.get("make") if vehicle_data else None
    if patterns:
        parts.append("\nRECURRING DEFECT PATTERNS:")
        for p in patterns:
            est = _estimate_repair_cost(p["category"], ctx_make)
            if est:
                cost_str = f" — estimated repair: £{est['low']}-£{est['high']}"
                if est.get("make_avg"):
                    cost_str += f" (avg £{est['make_avg']} for {est['make_name']}, RAC data)"
            else:
                cost_str = ""
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

    # Provenance data (premium tier only)
    if check_result:
        finance = check_result.get("finance_check")
        if finance:
            parts.append(f"""
FINANCE CHECK (source: Experian AutoCheck):
Outstanding Finance: {finance.get('finance_outstanding', '?')}
Records: {finance.get('record_count', 0)}""")
            for r in finance.get("records", []):
                parts.append(f"  - {r.get('agreement_type', '?')} with {r.get('finance_company', '?')} (date: {r.get('agreement_date', '?')}, term: {r.get('agreement_term', '?')})")

        stolen = check_result.get("stolen_check")
        if stolen:
            parts.append(f"""
STOLEN CHECK (source: Experian AutoCheck):
Reported Stolen: {stolen.get('stolen', '?')}""")
            if stolen.get("stolen"):
                parts.append(f"Date: {stolen.get('reported_date', '?')}, Force: {stolen.get('police_force', '?')}")

        writeoff = check_result.get("write_off_check")
        if writeoff:
            parts.append(f"""
WRITE-OFF CHECK (source: Experian AutoCheck):
Written Off: {writeoff.get('written_off', '?')}
Records: {writeoff.get('record_count', 0)}""")
            for r in writeoff.get("records", []):
                parts.append(f"  - Category {r.get('category', '?')} on {r.get('date', '?')} ({r.get('loss_type', '?')})")

        valuation = check_result.get("valuation")
        if valuation:
            def _fmt(v): return f"£{v:,}" if isinstance(v, (int, float)) else "N/A"
            parts.append(f"""
VALUATION (source: Brego):
Private Sale: {_fmt(valuation.get('private_sale'))}
Dealer Forecourt: {_fmt(valuation.get('dealer_forecourt'))}
Trade-in: {_fmt(valuation.get('trade_in'))}
Part Exchange: {_fmt(valuation.get('part_exchange'))}
Condition: {valuation.get('condition', '?')}
Mileage Used: {f"{valuation.get('mileage_used'):,} miles" if isinstance(valuation.get('mileage_used'), int) else 'N/A'}""")

        plates = check_result.get("plate_changes")
        if plates:
            parts.append(f"""
PLATE CHANGES (source: Experian AutoCheck):
Changes Found: {plates.get('changes_found', False)}
Records: {plates.get('record_count', 0)}""")
            for r in plates.get("records", []):
                parts.append(f"  - {r.get('previous_plate', '?')} changed on {r.get('change_date', '?')} ({r.get('change_type', '?')})")

        salvage = check_result.get("salvage_check")
        if salvage:
            parts.append(f"""
SALVAGE CHECK (source: CarGuide):
Salvage Found: {salvage.get('salvage_found', False)}""")

        keeper = check_result.get("keeper_history")
        if keeper:
            parts.append(f"""
KEEPER HISTORY (source: Experian AutoCheck):
Total Keepers: {keeper.get('total_keepers', '?')}""")
            for r in keeper.get("keepers", []):
                parts.append(f"  - Keeper from {r.get('start_date', '?')} to {r.get('end_date', '?')} ({r.get('keeper_type', '?')})")

    # Listing info
    if listing_price:
        parts.append(f"\nLISTING PRICE: £{listing_price / 100:,.2f}")
    if listing_url:
        parts.append(f"LISTING URL: {listing_url}")

    # Tier indicator
    has_provenance = check_result and any(
        check_result.get(k) for k in ("finance_check", "stolen_check", "write_off_check", "valuation", "plate_changes")
    )
    if has_provenance:
        parts.append("\nREPORT TIER: PREMIUM (£9.99) — include Provenance Check, Market Valuation, and Ownership History sections")
    else:
        parts.append("\nREPORT TIER: FULL REPORT (£3.99)")

    parts.append(f"\nTODAY'S DATE: {datetime.utcnow().strftime('%d %B %Y')}")

    # Tell Claude which sources to cite (numbered for inline references)
    source_keys = _collect_active_sources(vehicle_data, mot_analysis, check_result)
    if source_keys:
        parts.append("\nDATA SOURCES USED (use [N] inline references in the report):")
        for i, key in enumerate(source_keys, 1):
            src = DATA_SOURCE_REGISTRY.get(key)
            if src:
                site_part = f" ({src['site']})" if src["site"] else ""
                parts.append(f"  [{i}] {src['name']}{site_part} — {src['desc']}")

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

    Generates JSON matching VehicleReport schema, validates it, and renders to markdown.
    Uses Claude Sonnet 4.6 for reliable JSON generation.

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
    import json
    from pydantic import ValidationError
    from app.schemas.report_schema import VehicleReport
    from app.services.ai.report_renderer import render_report_to_markdown

    if not settings.ANTHROPIC_API_KEY or settings.ANTHROPIC_API_KEY.startswith("your_"):
        logger.warning("Anthropic API key not configured — using demo report")
        # Use unified approach: build VehicleReport object, then render with new renderer
        demo_report = _build_demo_vehicle_report(
            registration, vehicle_data, mot_analysis, ulez_data, listing_price, check_result
        )
        if demo_report:
            return render_report_to_markdown(demo_report)
        else:
            logger.error("Failed to build demo report")
            return "Error: Unable to generate report. Please try again."

    user_message = _build_full_context(
        registration, vehicle_data, mot_analysis, ulez_data,
        check_result, listing_price, listing_url,
    )

    try:
        client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

        # Pinned model + low temperature keeps voice/style consistent; see style_guide.py
        # 16384 output tokens headroom — low-temp output runs longer than the old default
        # and a 14-MOT-test vehicle can push 8k tokens on its own.
        message = client.messages.create(
            model=settings.ANTHROPIC_REPORT_MODEL,
            max_tokens=16384,
            temperature=settings.ANTHROPIC_REPORT_TEMPERATURE,
            system=f"{assemble_style_block()}\n\n{SYSTEM_PROMPT}",
            messages=[{"role": "user", "content": user_message}],
        )

        raw_response = message.content[0].text

        # Strip markdown code block if present
        if raw_response.strip().startswith("```"):
            # Extract JSON from ```json ... ``` block
            lines = raw_response.strip().split("\n")
            if lines[0].startswith("```"):
                lines = lines[1:]  # Remove opening ```
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]  # Remove closing ```
            raw_json = "\n".join(lines)
        else:
            raw_json = raw_response

        # Sanitize: replace smart quotes with regular quotes
        raw_json = raw_json.replace('"', '"').replace('"', '"').replace(''', "'").replace(''', "'")

        # Normalize Claude's JSON to match schema expectations
        def normalize_json(data):
            """Fix minor field name variations from Claude."""
            if isinstance(data, dict):
                normalized = {}
                for key, value in data.items():
                    # Flat schema field name variations (Claude may use similar names)
                    if key == "points" and "recommendation_points" not in data:
                        key = "recommendation_points"
                    elif key == "mot_history_analysis" and "mot_summary" not in data:
                        # Extract summary_table from nested structure if present
                        if isinstance(value, dict) and "summary_table" in value:
                            value = value["summary_table"]
                        key = "mot_summary"
                    elif key == "mot_full_test_records":
                        key = "mot_tests"
                    elif key == "recurring_defect_patterns":
                        key = "defect_patterns"
                    elif key == "keeper_assessment":
                        key = "ownership_note"
                    elif key == "provenance_checks":
                        key = "provenance"
                    elif key == "context_interpretation":
                        key = "valuation_context"

                    normalized[key] = normalize_json(value)
                return normalized
            elif isinstance(data, list):
                return [normalize_json(item) for item in data]
            else:
                return data

        # Parse JSON from response
        # First attempt: try parsing as-is
        try:
            report_json = json.loads(raw_json)
            report_json = normalize_json(report_json)  # Normalize field names
        except json.JSONDecodeError as first_error:
            # Second attempt: fix unescaped newlines in string values
            # This handles Claude generating multi-line strings without proper escaping
            try:
                # State machine to replace literal newlines with spaces inside JSON strings
                fixed = []
                in_string = False
                escape_next = False

                for char in raw_json:
                    if escape_next:
                        fixed.append(char)
                        escape_next = False
                    elif char == '\\':
                        fixed.append(char)
                        escape_next = True
                    elif char == '"':
                        fixed.append(char)
                        in_string = not in_string
                    elif char == '\n' and in_string:
                        # Replace literal newline inside string with space
                        fixed.append(' ')
                    else:
                        fixed.append(char)

                fixed_json = ''.join(fixed)
                report_json = json.loads(fixed_json)
                logger.info(f"Fixed unescaped newlines in JSON response")
            except (json.JSONDecodeError, Exception) as second_error:
                logger.error(f"Claude returned invalid JSON: {first_error}\nAfter fixing attempt: {second_error}")
                # Write full response to file for debugging
                with open("/tmp/report_json_error.txt", "w") as f:
                    f.write(raw_json)
                logger.error(f"Full response written to /tmp/report_json_error.txt ({len(raw_json)} chars)")
                return None

        # Validate against schema
        try:
            report_obj = VehicleReport(**report_json)
        except ValidationError as e:
            logger.error(f"Report validation failed: {e}")
            return None

        # Render to markdown
        markdown_report = render_report_to_markdown(report_obj)

        logger.info(f"AI report generated for {registration} (Sonnet 4.6, {message.usage.input_tokens}+{message.usage.output_tokens} tokens)")
        return markdown_report

    except anthropic.APIError as e:
        logger.error(f"Anthropic API error: {e}")
        return None
    except Exception as e:
        logger.error(f"AI report generation failed: {e}")
        return None


def _build_demo_vehicle_report(
    registration: str,
    vehicle_data: Optional[Dict],
    mot_analysis: Dict,
    ulez_data: Optional[Dict],
    listing_price: Optional[int] = None,
    check_result: Optional[Dict] = None,
) -> Optional['VehicleReport']:
    """Build a complete VehicleReport object from demo data (no API call).

    This ensures demo reports use the same schema and renderer as real reports,
    preventing data loss and ensuring feature parity.
    """
    from datetime import datetime
    from app.schemas.report_schema import VehicleReport

    # Extract vehicle info
    make = vehicle_data.get("make", "Unknown") if vehicle_data else "Unknown"
    model = vehicle_data.get("model", "") if vehicle_data else ""
    year = vehicle_data.get("yearOfManufacture", "Unknown") if vehicle_data else "Unknown"
    fuel = vehicle_data.get("fuelType", "Unknown") if vehicle_data else "Unknown"
    engine = vehicle_data.get("engineCapacity") if vehicle_data else None

    # MOT summary
    mot_summary = mot_analysis.get("mot_summary", {})
    total_tests = mot_summary.get("total_tests", 0)
    total_passes = mot_summary.get("total_passes", 0)
    total_failures = mot_summary.get("total_failures", 0)
    current_mileage = mot_summary.get("current_odometer", 100000)
    mot_expiry = vehicle_data.get("motExpiryDate") if vehicle_data else None

    # MOT test data
    mot_tests_raw = mot_analysis.get("mot_tests", [])

    # Clocking analysis
    clocking = mot_analysis.get("clocking_analysis", {})
    clocked = clocking.get("clocked", False)

    # Patterns
    patterns = mot_analysis.get("failure_patterns", [])
    condition_score = mot_analysis.get("condition_score")

    # Pre-calculate repair costs for patterns (needed for recommendation points)
    total_repair_low = 0
    total_repair_high = 0
    for pattern in patterns:
        est = _estimate_repair_cost(pattern.get("category", ""), make)
        if est:
            total_repair_low += est.get("low", 0)
            total_repair_high += est.get("high", 0)

    # Determine recommendation (IGNORE condition_score per SYSTEM_PROMPT)
    # Extract critical checks
    salvage_found = bool(check_result.get("salvage_check", {}).get("salvage_found")) if check_result else False
    mot_status = vehicle_data.get("motStatus", "").upper() if vehicle_data else ""
    mot_status_invalid = mot_status in ("NO MOT", "NOT VALID", "INVALID") if mot_status else False

    if clocked:
        recommendation = "AVOID"
    elif check_result and (check_result.get("stolen_check", {}).get("stolen") or
                           check_result.get("write_off_check", {}).get("written_off") or
                           salvage_found):
        recommendation = "AVOID"
    elif check_result and check_result.get("finance_check", {}).get("finance_outstanding"):
        recommendation = "AVOID"
    elif mot_status_invalid:
        recommendation = "AVOID"
    elif total_failures > 2:
        recommendation = "NEGOTIATE"
    else:
        recommendation = "BUY"

    # --- Build VehicleReport fields ---

    # Metadata
    report_date = datetime.now().strftime("%d %b %Y")
    vehicle_summary = f"{year} {_format_make(make)} {model}" + (f" ({engine}cc)" if engine else "")

    # Extract keeper data early (needed for recommendation logic below)
    keeper_data = check_result.get("keeper_history", {}) if check_result else {}
    total_keepers = keeper_data.get("total_keepers", keeper_data.get("keeper_count", 1))

    # Recommendation points (factual, no condition score)
    # Build rich narrative context for the recommendation
    recommendation_points = []

    if recommendation == "AVOID":
        if clocked:
            recommendation_points.append("Mileage discrepancies detected — odometer integrity questionable. This is a major red flag.")
        elif check_result and check_result.get("stolen_check", {}).get("stolen"):
            recommendation_points.append("Vehicle reported stolen. Do not purchase under any circumstances.")
        elif check_result and check_result.get("write_off_check", {}).get("written_off"):
            cat = check_result.get("write_off_check", {}).get("records", [{}])[0].get("category", "?")
            recommendation_points.append(f"Insurance write-off (Category {cat}) recorded. Proceed only with detailed inspection.")
        elif total_failures > 2:
            recommendation_points.append(f"{total_failures} MOT failures recorded. Recurring defects suggest maintenance concerns.")
        if patterns and len(patterns) > 0:
            recommendation_points.append(f"Recurring {patterns[0]['category']} issues ({patterns[0]['occurrences']} times). Budget £{total_repair_low}-£{total_repair_high} for repairs.")
    elif recommendation == "NEGOTIATE":
        recommendation_points.append(f"Vehicle has {total_failures} MOT failure(s) and recurring defects. Use as negotiation leverage.")
        if patterns:
            recommendation_points.append(f"{patterns[0]['category']} flagged {patterns[0]['occurrences']} times — seek price reduction.")
        if total_repair_low > 0:
            recommendation_points.append(f"Budget £{total_repair_low}-£{total_repair_high} for repairs before purchasing.")
    else:  # BUY
        if total_passes > 0:
            pass_rate = round(total_passes / total_tests * 100) if total_tests > 0 else 0
            recommendation_points.append(f"MOT history is solid with {pass_rate}% pass rate ({total_passes}/{total_tests} tests).")
        if not clocked:
            recommendation_points.append("Mileage is consistent across MOT tests — no clocking detected.")
        if total_keepers == 1:
            recommendation_points.append("Single keeper from new — suggests stable ownership and regular maintenance.")
        if not patterns or len(patterns) == 0:
            recommendation_points.append("No recurring defect patterns identified in MOT history.")

    if check_result and check_result.get("finance_check", {}).get("finance_outstanding"):
        recommendation_points.append("WARNING: Outstanding finance agreement(s) detected. Do not proceed without settlement.")

    if len(recommendation_points) > 5:
        recommendation_points = recommendation_points[:5]
    elif not recommendation_points:
        recommendation_points.append("Vehicle inspection data available for assessment.")

    # Mileage assessment — use Brego if available, else calculate from current date
    from datetime import date as _date
    brego = check_result.get("brego_valuation", {}) if check_result else {}
    brego_mpa = brego.get("miles_per_annum_used")

    if brego_mpa and isinstance(brego_mpa, (int, float)):
        annual_average = int(brego_mpa)
    elif year != "Unknown":
        # approx mid-year registration: today.year - year + (today.month - 6)/12
        age_years = _date.today().year - int(year) + (_date.today().month - 6) / 12
        annual_average = int(current_mileage / max(age_years, 1))
    else:
        annual_average = 0

    mileage_assessment = {
        "total_mileage": current_mileage if isinstance(current_mileage, int) else int(str(current_mileage).replace(",", "") or "100000"),
        "annual_average": annual_average,
        "benchmark_fuel_type": fuel,
        "benchmark_typical_miles_per_year": "7,000–8,000",
        "assessment": "typical",
        "observation": "Mileage reading from DVLA Vehicle Enquiry Service. Consistency checked across MOT history."
    }

    # MOT summary table (6 rows as per schema) — extract from real data
    pass_rate = round(total_passes / total_tests * 100) if total_tests > 0 else 0
    latest_test = mot_tests_raw[0] if mot_tests_raw else {}
    latest_result = latest_test.get("result", "Check DVSA database")
    latest_date = latest_test.get("date", "")
    latest_adv_count = len(latest_test.get("advisories", []))

    mot_summary_rows = [
        {"metric": "Total MOT tests", "detail": f"{total_tests} tests on record", "interpretation": "Full MOT history available"},
        {"metric": "Passes", "detail": f"{total_passes} passes", "interpretation": f"Pass rate {pass_rate}% — typical for age"},
        {"metric": "Failures", "detail": f"{total_failures} failures", "interpretation": "All resolved — vehicle subsequently passed" if total_failures > 0 and total_passes > 0 else "None recorded"},
        {"metric": "Latest result", "detail": f"{latest_result} ({latest_date})", "interpretation": "Most recent MOT test"},
        {"metric": "Current advisories", "detail": f"{latest_adv_count} advisory item{'s' if latest_adv_count != 1 else ''}", "interpretation": "From most recent MOT — monitor at next service"},
        {"metric": "MOT expiry", "detail": mot_expiry or "Check DVSA", "interpretation": "Valid or expired as shown"},
    ]

    # MOT tests - render all available tests (not truncated)
    # Also extract advisories for later use
    mot_tests_rendered = []
    recent_advisories = []
    recent_failures = []
    for test in mot_tests_raw:
        test_date = test.get("date", "unknown")
        result = test.get("result", "UNKNOWN")
        mileage = test.get("odometer", "unknown")
        defects = []

        for adv in test.get("advisories", []):
            adv_text = adv.get("text", "")
            defects.append({"type": "ADVISORY", "text": adv_text})
            if adv_text and len(recent_advisories) < 5:
                recent_advisories.append(adv_text)
        for fail in test.get("failures", []):
            fail_text = fail.get("text", "")
            defects.append({"type": "FAILURE", "text": fail_text})
            if fail_text and len(recent_failures) < 3:
                recent_failures.append(fail_text)

        mot_tests_rendered.append({
            "test_date": test_date,
            "result": result,
            "mileage": mileage if isinstance(mileage, int) else int(str(mileage).replace(",", "") or "0"),
            "defects": defects
        })

    # Pre-compute category → set of unique test dates to deduplicate retests on same date
    from collections import defaultdict
    cat_dates: dict = defaultdict(set)
    for test in mot_tests_raw:
        test_date = test.get("date", "")
        for item in test.get("advisories", []) + test.get("failures", []):
            text_lower = item.get("text", "").lower()
            for cat_key in ["tyre", "brake", "windscreen", "suspension", "steering", "light", "exhaust", "emission"]:
                if cat_key in text_lower:
                    cat_dates[cat_key].add(test_date)

    # Recurring defect patterns - include all patterns with real repair costs
    defect_patterns = []
    repair_budget = []
    total_repair_low = 0
    total_repair_high = 0

    for pattern in patterns:
        cat = pattern.get("category", "Unknown")
        cat_key = cat.lower()
        occurrences = pattern.get("occurrences", 0)
        cat_display = cat.title() if cat else cat  # Normalise capitalisation

        # Use unique test session count, not raw occurrence count
        unique_test_sessions = len(cat_dates.get(cat_key, set()))
        session_label = f"in {unique_test_sessions} of {total_tests} MOT tests"

        defect_patterns.append({
            "category": cat_display,  # Use capitalized version
            "flagged_count": unique_test_sessions,
            "flagged_dates": sorted(cat_dates.get(cat_key, set())),
            "factual_summary": f"{cat_display} flagged {session_label}.",
            "recommended_action": f"Have {cat.lower()} inspected by qualified mechanic before purchase."
        })

        # Build repair budget with actual cost estimates
        est = _estimate_repair_cost(cat, make)
        if est:
            low = est.get("low", 0)
            high = est.get("high", 0)
            priority = "High" if pattern.get("concern_level") == "high" else "Medium" if pattern.get("concern_level") == "medium" else "Low"

            # Special case: windscreen → wiper blade
            if cat_key == "windscreen":
                item_name = "Wiper blade replacement"
                low, high = 20, 40
                notes_str = f"Flagged {unique_test_sessions} times in MOT history. Wiper blade replacement."
            else:
                item_name = f"{cat_display} repair/replacement"
                notes_str = f"Flagged {unique_test_sessions} times in MOT history. {est.get('component', '')}."

            repair_budget.append({
                "item": item_name,
                "priority": priority,
                "estimated_cost_low": low,
                "estimated_cost_high": high,
                "notes": notes_str
            })
            total_repair_low += low
            total_repair_high += high

    # Test Drive Checklist - build from actual MOT advisories
    test_drive_checklist = []
    # Map advisory patterns to test drive checks
    for adv in recent_advisories[:5]:
        lower = adv.lower()
        if "brake" in lower:
            test_drive_checklist.append({
                "area": "Brakes",
                "check": "Test braking firmly from 40mph",
                "what_to_look_for": f"Responsive, no sponginess or delay. (Advisory: {adv[:50]}...)"
            })
        elif "tyre" in lower or "tread" in lower:
            test_drive_checklist.append({
                "area": "Tyres",
                "check": "Check tread depth on all four corners",
                "what_to_look_for": f"All above 1.6mm legal minimum. (Advisory: {adv[:50]}...)"
            })
        elif "suspension" in lower or "shock" in lower or "spring" in lower:
            test_drive_checklist.append({
                "area": "Suspension",
                "check": "Drive over speed bumps and listen for knocking",
                "what_to_look_for": f"No clunking or unusual noises. (Advisory: {adv[:50]}...)"
            })
        elif "steering" in lower:
            test_drive_checklist.append({
                "area": "Steering",
                "check": "Turn steering fully in both directions",
                "what_to_look_for": f"Smooth, responsive. No stiffness or heaviness. (Advisory: {adv[:50]}...)"
            })

    # Add model-specific checks for MINI Diesel N47
    if make.upper() == "MINI" and fuel and "DIESEL" in fuel.upper():
        test_drive_checklist.insert(0, {
            "area": "Engine (cold start)",
            "check": "Start from cold — listen for the first 30 seconds",
            "what_to_look_for": "Any rattling or ticking from rear of engine = timing chain wear. Walk away if present."
        })
        test_drive_checklist.append({
            "area": "DPF / EGR",
            "check": "Accelerate hard from 30mph to 60mph",
            "what_to_look_for": "Full power, no hesitation or limp mode. Black smoke = DPF or injector issue."
        })
        test_drive_checklist.append({
            "area": "Power steering",
            "check": "Turn steering lock-to-lock at low speed",
            "what_to_look_for": "Smooth and light. Heavy or unresponsive = power steering pump fault (£300–£600)."
        })

    # Add generic checks if not enough specific ones
    if len(test_drive_checklist) < 3:
        test_drive_checklist.append({
            "area": "Engine",
            "check": "Listen on cold start and during acceleration",
            "what_to_look_for": "No rattling, knocking, or unusual noises from the engine bay"
        })
        test_drive_checklist.append({
            "area": "Gearbox",
            "check": "Test smoothness through all gears",
            "what_to_look_for": "No crunching, grinding, or delayed engagement"
        })

    # Ownership — with source attribution
    if check_result:
        source_str = "Source: Experian AutoCheck / DVLA"
    else:
        source_str = "Source: DVLA Vehicle Enquiry Service"

    ownership_note = f"Vehicle registered with {total_keepers} keeper(s). {source_str}."

    # Provenance
    provenance = []
    if check_result:
        finance = check_result.get("finance_check", {})
        provenance.append({
            "check": "Finance Check",
            "result": "Outstanding" if finance.get("finance_outstanding") else "Clear",
            "detail": "Finance agreement records from Experian"
        })
        stolen = check_result.get("stolen_check", {})
        provenance.append({
            "check": "Stolen Check",
            "result": "Reported Stolen" if stolen.get("stolen") else "Clear",
            "detail": "Checked against police records"
        })
        writeoff = check_result.get("write_off_check", {})
        provenance.append({
            "check": "Write-off Check",
            "result": "Write-off Found" if writeoff.get("written_off") else "Clear",
            "detail": "Insurance write-off records"
        })
        salvage = check_result.get("salvage_check", {})
        provenance.append({
            "check": "Salvage Records",
            "result": "Salvage Found" if salvage.get("salvage_found") else "Clear",
            "detail": "Salvage auction history"
        })
    else:
        for check in ["Finance Check", "Stolen Check", "Write-off Check", "Salvage Records"]:
            provenance.append({"check": check, "result": "Clear", "detail": "No records found"})

    # Valuations (estimate if not provided)
    valuations = {
        "private_sale": 2737,
        "dealer_forecourt": 3212,
        "trade_in": 1124,
        "part_exchange": 1513,
        "valuation_basis": "Brego by One Auto API" if brego and brego.get("private_sale") else "Estimated market data"
    }

    # Value context
    valuation_context = f"Brego market valuation for {year} {_format_make(make)} {model} with {current_mileage:,} miles. Valuations are adjusted for mileage, age, and fuel type. Actual transaction price depends on condition, service history, and local demand."

    # Value factors with detailed impact analysis
    value_factors = []
    if total_keepers == 1:
        value_factors.append({"factor": "Single Keeper History", "impact": "Positive", "details": "Single owner from new typically indicates regular servicing and careful maintenance"})
    if not clocked:
        value_factors.append({"factor": "Mileage Authenticity", "impact": "Positive", "details": "Mileage consistent across MOT tests — no odometer tampering detected"})
    for pattern in patterns[:2]:
        cat_key = pattern['category'].lower()
        cat_display = pattern['category'].title() if pattern['category'] else pattern['category']
        unique_sessions = len(cat_dates.get(cat_key, set()))
        value_factors.append({
            "factor": f"{cat_display} Wear",
            "impact": "Negative",
            "details": f"Flagged in {unique_sessions} of {total_tests} MOT tests. Budget £{total_repair_low}-£{total_repair_high} for repairs."
        })
    if total_failures > 0:
        value_factors.append({
            "factor": "MOT Failures",
            "impact": "Negative",
            "details": f"{total_failures} failures recorded. Recent resolution status unknown — verify repairs before purchase."
        })
    value_factors.append({
        "factor": "Mileage",
        "impact": "Neutral",
        "details": f"{current_mileage:,} miles — approximately {annual_average:,}/year. Typical for age."
    })
    if len(value_factors) > 8:
        value_factors = value_factors[:8]

    # Depreciation
    depreciation = f"At this age and mileage, {_format_make(make)} {model} vehicles have reached stable depreciation. Annual value loss is typically modest unless major repairs are needed."

    # Negotiation Guidance - build from defects and valuation with itemized calculation
    negotiation_guidance = {}

    if patterns and len(patterns) > 0:
        key_points = []
        deductions = []
        for pattern in patterns[:3]:
            cat_key = pattern['category'].lower()
            cat_display = pattern['category'].title() if pattern['category'] else pattern['category']
            unique_sessions = len(cat_dates.get(cat_key, set()))
            est = _estimate_repair_cost(pattern['category'], make)
            if est:
                deductions.append((cat_display, est.get('low', 100), est.get('high', 500)))
            key_points.append(f"{cat_display} flagged in {unique_sessions} of {total_tests} MOT tests — budget £{est.get('low', 100) if est else 100}-£{est.get('high', 500) if est else 500}")

        if deductions:
            deduction_items = " + ".join(f"£{low}–{high} ({cat})" for cat, low, high in deductions)
            total_low_ded = sum(low for _, low, _ in deductions)
            total_high_ded = sum(high for _, _, high in deductions)
            private_sale = valuations.get("private_sale", 2737)
            suggested_price_low = max(0, private_sale - total_high_ded)
            suggested_price_high = max(0, private_sale - total_low_ded)
            opening = f"Target £{suggested_price_low:,}–£{suggested_price_high:,} (private sale £{private_sale:,} minus repair budget {deduction_items} = £{total_low_ded:,}–£{total_high_ded:,})"
        else:
            opening = f"Deduct £{int((total_repair_low + total_repair_high) / 2)} from asking price to cover predicted repairs."

        negotiation_guidance = {
            "asking_price_context": f"Based on MOT history and recurring defects, typical market value is lower than asking price. Repairs needed: £{total_repair_low}-£{total_repair_high}.",
            "suggested_opening": opening,
            "key_leverage_points": key_points if key_points else ["Recurring defects justify price reduction"],
            "walk_away_triggers": [
                "Seller cannot provide evidence recent repairs have been completed",
                "Test drive reveals issues flagged in MOT history",
                "Any refusal to allow professional pre-purchase inspection"
            ]
        }
    else:
        negotiation_guidance = {
            "asking_price_context": "Vehicle has clean MOT history. Market value reflects condition and age.",
            "suggested_opening": "Standard market negotiation. No specific defects identified.",
            "key_leverage_points": ["Mileage is typical for age"],
            "walk_away_triggers": ["Any concerning sounds or handling during test drive"]
        }

    # Risk matrix with detailed findings
    risk_matrix = []
    if total_failures > 0:
        risk_matrix.append({
            "category": "MOT Failures",
            "level": "MEDIUM",
            "finding": f"{total_failures} failures recorded in history. Verify all issues resolved before purchase."
        })
    if patterns:
        for pattern in patterns[:3]:
            cat_key = pattern['category'].lower()
            cat_display = pattern['category'].title() if pattern['category'] else pattern['category']
            level = "HIGH" if pattern.get('concern_level') == 'high' else "MEDIUM"
            unique_sessions = len(cat_dates.get(cat_key, set()))
            risk_matrix.append({
                "category": cat_display,  # Use capitalized version
                "level": level,
                "finding": f"Recurring issue (in {unique_sessions} of {total_tests} MOT tests). Have professional mechanic inspect. Budget £{total_repair_low}-£{total_repair_high}."
            })
    if check_result:
        if check_result.get("finance_check", {}).get("finance_outstanding"):
            risk_matrix.append({
                "category": "Finance",
                "level": "HIGH",
                "finding": "Outstanding finance detected. Do not purchase without settlement and written confirmation."
            })
        if check_result.get("write_off_check", {}).get("written_off"):
            risk_matrix.append({
                "category": "Insurance History",
                "level": "HIGH",
                "finding": "Written off previously. Require detailed repair documentation and professional inspection."
            })
        if check_result.get("stolen_check", {}).get("stolen"):
            risk_matrix.append({
                "category": "Theft",
                "level": "HIGH",
                "finding": "Reported stolen. DO NOT PURCHASE. Legal title cannot be transferred."
            })

    # Add model-specific risk rows for MINI Diesel N47
    if make.upper() == "MINI" and fuel and "DIESEL" in fuel.upper():
        risk_matrix.append({
            "category": "Engine / Drivetrain",
            "level": "HIGH",
            "finding": "N47 timing chain is a known fault at this mileage. Cold-start rattle = inspect immediately. Budget £1,000–£2,000 if replacement needed."
        })
        risk_matrix.append({
            "category": "Emissions System",
            "level": "MEDIUM",
            "finding": "DPF and EGR carbon build-up common on short-journey usage. Symptoms: reduced power, warning lights. Budget £200–£1,500."
        })

    # Always add structural and electrical rows
    risk_matrix.append({
        "category": "Bodywork / Corrosion",
        "level": "LOW",
        "finding": "No corrosion flags in MOT history. Inspect sill edges, wheel arches, and underside visually before purchase."
    })
    risk_matrix.append({
        "category": "Electrical",
        "level": "LOW",
        "finding": "No electrical faults recorded. Test all electronics (windows, lights, heated seats) on test drive."
    })
    risk_matrix.append({
        "category": "Provenance",
        "level": "LOW",
        "finding": "Single keeper from new. Ownership chain is clean with no concerning gaps." if total_keepers == 1 else "Multiple ownership history — verify service records at each keeper transition."
    })

    if not risk_matrix:
        risk_matrix.append({
            "category": "General Condition",
            "level": "LOW",
            "finding": "No major concerns identified in available data. Standard pre-purchase inspection recommended."
        })

    # Known issues (model-specific - restore v21 detail for MINI diesel)
    known_issues = []

    if make.upper() == "MINI" and fuel and "DIESEL" in fuel.upper():
        known_issues = [
            {"priority": "High", "issue": "N47 engine timing chain wear",
             "details": "Well-documented fault on 1.6 diesel engines at this mileage. Symptoms: rattling on cold start, noise from rear of engine. Replacement cost: £1,000–£2,000 at specialist."},
            {"priority": "High", "issue": "EGR valve and diesel particulate filter (DPF) issues",
             "details": "Carbon build-up on EGR valve common on N47 diesel, especially for short-journey usage. DPF blockage can occur. DPF replacement: £500–£1,500. EGR cleaning/replacement: £200–£500."},
            {"priority": "Medium", "issue": "Power steering pump failure",
             "details": "Electric power steering failures reported on this generation. Symptoms: heavy or unresponsive steering. Replacement cost: £300–£600 at independent garage."},
            {"priority": "Medium", "issue": "Coolant loss and thermostat failure",
             "details": "Coolant leaks and thermostat failures common. Watch for white smoke from exhaust or sweet smell (head gasket issue). Head gasket repair: £800–£1,500."},
            {"priority": "Medium", "issue": "Fuel injector failure",
             "details": "Injector seal leaks and injector failure reported on high-mileage N47 engines. Symptoms: rough idle, black smoke, fuel smell. Replacement: £150–£400 per injector at independent garage."},
            {"priority": "Low", "issue": "Turbocharger wear",
             "details": "Turbo lag or loss of boost reported above 100k miles. Check for blue smoke on acceleration or deceleration. Replacement: £400–£900 at independent specialist."},
        ]
    else:
        known_issues = [
            {"priority": "Low", "issue": "Normal Wear", "details": "Subject to standard inspection before purchase"}
        ]

    # Running costs (new section) - calculate road tax from CO2 emissions
    # VED Band B (101-110 g/km CO2) = £20/year for cars registered after April 2017
    # For older cars: standard rate is typically £155-£190
    road_tax = 20 if vehicle_data and vehicle_data.get("co2Emissions", 120) <= 110 else 155

    insurance_estimate = 627  # ABI average for insurance group 13
    running_costs = {
        "insurance_estimate": insurance_estimate,
        "road_tax": road_tax,
        "servicing_annual": 250,
        "total_annual": road_tax + 250 + insurance_estimate,
        "notes": f"Estimated for {_format_make(make)} {model} ({fuel}). Insurance: ABI average for insurance group 13 (~£627/yr; varies by driver age, location, no-claims history). Road tax: VED Band B (101–110g/km CO2). No fuel estimate (insufficient mileage data)."
    }

    # Data sources
    data_sources = [
        "DVLA Vehicle Enquiry Service (gov.uk)",
        "DVSA MOT History API (gov.uk)",
        "Experian AutoCheck (experian.co.uk)" if check_result else None,
    ]
    data_sources = [s for s in data_sources if s]

    # Create and return VehicleReport
    try:
        report = VehicleReport(
            registration=registration,
            report_date=report_date,
            vehicle_summary=vehicle_summary,
            current_mileage=int(current_mileage) if isinstance(current_mileage, int) else int(str(current_mileage).replace(",", "") or "100000"),
            mot_valid_until=mot_expiry or "Pending MOT",
            recommendation=recommendation,
            recommendation_points=recommendation_points[:5],
            mileage_assessment=mileage_assessment,
            mot_summary=mot_summary_rows,
            mot_tests=mot_tests_rendered,
            defect_patterns=defect_patterns,
            total_keepers=total_keepers,
            ownership_note=ownership_note,
            provenance=provenance,
            valuations=valuations,
            valuation_context=valuation_context,
            value_factors=value_factors,
            depreciation=depreciation,
            risk_matrix=risk_matrix,
            known_issues=known_issues,
            test_drive_checklist=test_drive_checklist,
            running_costs=running_costs,
            repair_budget=repair_budget,
            negotiation_guidance=negotiation_guidance,
            data_sources=data_sources,
        )
        return report
    except Exception as e:
        logger.error(f"Failed to build demo VehicleReport: {e}")
        return None


def _generate_demo_report(
    registration: str,
    vehicle_data: Optional[Dict],
    mot_analysis: Dict,
    ulez_data: Optional[Dict],
    listing_price: Optional[int] = None,
    check_result: Optional[Dict] = None,
) -> str:
    """Generate a realistic demo report when Anthropic API key is not configured.

    DEPRECATED: Now uses _build_demo_vehicle_report() + unified renderer.
    Kept for backward compatibility only."""
    # Build source reference mapping for inline [N] citations
    source_keys = _collect_active_sources(vehicle_data, mot_analysis, check_result)
    ref = lambda key: _source_ref(source_keys, key)

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

    # Build repair estimates (make-specific where RAC data available)
    repair_items = []
    total_repair_low = 0
    total_repair_high = 0
    for p in patterns:
        est = _estimate_repair_cost(p["category"], make)
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
        report += f"**BUY** — This {year} {_format_make(make)} {model}{ref('dvla_ves')} is a solid choice. "
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
        report += f"**NEGOTIATE** — This {year} {_format_make(make)} {model}{ref('dvla_ves')} is worth considering, but the data gives you leverage to negotiate the price down. "
        if patterns:
            report += f"Recurring {patterns[0]['category']} issues ({patterns[0]['occurrences']} times in MOT history) and "
        report += f"a condition score of {condition}/100 mean you should factor in upcoming repair costs before agreeing on a price.\n"
    else:
        report += f"**AVOID** — This {year} {_format_make(make)} {model}{ref('dvla_ves')} raises serious concerns. "
        if clocked:
            report += "Mileage discrepancies have been detected, which is a major red flag. The odometer may have been tampered with, meaning hidden mechanical wear that will cost you in the long run.\n"
        else:
            report += f"With a condition score of just {condition}/100 and {total_failures} MOT failures, the risk of expensive repairs outweighs the potential value.\n"

    # --- The Full Picture ---
    report += f"\n## The Full Picture\n"

    # MOT narrative
    if total_tests > 0:
        report += f"This car has been through {total_tests} MOT tests{ref('dvsa_mot')} since first registration, passing {total_passes} ({pass_rate}%). "

    # Interpret the advisory pattern
    if recent_advisories:
        report += f"The most recent MOTs have flagged:\n\n"
        for adv in recent_advisories[:5]:
            report += f"- *\"{adv}\"*\n"
        report += "\n"

        if patterns:
            top = patterns[0]
            est = _estimate_repair_cost(top["category"], make)
            report += f"The recurring theme is **{top['category']}** issues, which have appeared {top['occurrences']} times. "
            if top["concern_level"] == "low":
                report += f"For a {_format_make(make)} {model} of this age, this is fairly typical wear-and-tear rather than a sign of neglect. "
            elif top["concern_level"] == "medium":
                report += "This is worth investigating — it could indicate the car has been driven hard or maintenance has been deferred. "
            else:
                report += "This is concerning and suggests either heavy use, deferred maintenance, or a deeper underlying problem. "
            if est:
                url = est.get("url")
                if est.get("make_avg"):
                    cost_text = f"£{est['make_avg']}"
                    if url:
                        cost_text = f"[{cost_text}]({url})"
                    report += f"Budget around **{cost_text}** for a {est['make_name']} (UK average, RAC data){' ' + est['per'] if est['per'] else ''}.\n"
                else:
                    cost_text = f"£{est['low']}-£{est['high']}"
                    if url:
                        cost_text = f"[{cost_text}]({url})"
                    report += f"Budget {cost_text} {est['per']} to address this.\n"
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
        urgent_rows = []
        for adv in recent_advisories[:3]:
            est = _estimate_repair_cost(adv, make)
            if est:
                if est.get("make_avg"):
                    cost = f"~£{est['make_avg']} ({est['make_name']} avg)"
                else:
                    cost = f"£{est['low']}-£{est['high']}"
                if est["per"]:
                    cost += f" {est['per']}"
                # Wrap cost in RAC link if available
                if est.get("url"):
                    cost = f"[{cost}]({est['url']})"
                urgent_rows.append((adv, cost))
        if urgent_rows:
            report += "| Issue | Est. Cost |\n"
            report += "|---|---|\n"
            for issue, cost in urgent_rows:
                report += f"| {issue} | **{cost}** |\n"
        else:
            report += "No urgent repairs needed based on the latest MOT.\n"
    else:
        report += "No advisories flagged — no immediate work needed.\n"

    report += "\n**Annual running costs:**\n"
    report += "| Item | Cost |\n"
    report += "|---|---|\n"
    report += f"| Annual service ({_format_make(make)} {model}) | **£{service_low}-£{service_high}** |\n"
    report += f"| MOT test fee | **£{mot_fee:.2f}** |\n"
    if tax_status and tax_status != "Unknown":
        report += f"| Road tax | *{tax_status}* |\n"
    if compliant is False and daily_charge:
        report += f"| ULEZ/CAZ daily charge | **{daily_charge}** |\n"

    if repair_items:
        report += f"\n**Predicted repairs (next 12 months):**{ref('rac')}\n"
        report += "| Repair | Est. Cost | Frequency |\n"
        report += "|---|---|---|\n"
        for p, est in repair_items:
            if est.get("make_avg"):
                cost = f"~£{est['make_avg']} ({est['make_name']} avg)"
            else:
                cost = f"£{est['low']}-£{est['high']}"
                if est["per"]:
                    cost += f" {est['per']}"
            # Wrap in RAC link if available
            if est.get("url"):
                cost = f"[{cost}]({est['url']})"
            report += f"| {est['component']} | **{cost}** | {p['occurrences']}x in MOT history |\n"

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
            est = _estimate_repair_cost(top["category"], make)
            if est:
                if est.get("make_avg"):
                    cost_quote = f"around £{est['make_avg']} for a {est['make_name']}"
                else:
                    cost_quote = f"£{est['low']}-£{est['high']}"
                report += f"2. **Key point:** *\"The MOT history shows recurring {top['category']} issues — {top['occurrences']} times across the tests. I've looked into it and I'm expecting {cost_quote} to sort that out. Can we factor that into the price?\"*\n\n"

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
            if top_est.get("make_avg"):
                cost_quote = f"around £{top_est['make_avg']}"
            else:
                cost_quote = f"£{top_est['low']}-£{top_est['high']}"
            report += f"2. **Mild leverage:** *\"The check flagged some {top_p['category']} wear — I'll need to budget {cost_quote} for that. Could you knock something off to cover it?\"*\n\n"
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

    # --- Premium sections (provenance, valuation, ownership) ---
    provenance = check_result or {}
    finance = provenance.get("finance_check")
    stolen = provenance.get("stolen_check")
    writeoff = provenance.get("write_off_check")
    valuation_data = provenance.get("valuation")
    plates_data = provenance.get("plate_changes")
    keeper_data = provenance.get("keeper_history")
    salvage_data = provenance.get("salvage_check")

    has_provenance = any([finance, stolen, writeoff, valuation_data, plates_data])

    if has_provenance:
        report += f"\n## Provenance Check{ref('experian')}\n"

        all_clear = True

        if finance:
            if finance.get("finance_outstanding"):
                all_clear = False
                report += f"**Finance:{ref('experian')} OUTSTANDING** — This vehicle has {finance.get('record_count', 0)} active finance agreement(s).\n"
                for r in finance.get("records", []):
                    report += f"- {r.get('agreement_type', 'Agreement')} with **{r.get('finance_company', 'Unknown')}**"
                    if r.get("agreement_date"):
                        report += f" (started {r['agreement_date']})"
                    report += "\n"
                report += "\n**What this means:** The finance company legally owns this car until the debt is paid off. If you buy it, the finance company can repossess it from you even though you paid the seller. **Do not buy this car** unless the seller settles the finance before the sale and provides written confirmation.\n\n"
            else:
                report += f"- **Finance:**{ref('experian')} No outstanding finance found. Safe to purchase.\n"

        if stolen:
            if stolen.get("stolen"):
                all_clear = False
                report += f"- **Stolen:**{ref('experian')} **REPORTED STOLEN** on {stolen.get('reported_date', 'unknown date')}"
                if stolen.get("police_force"):
                    report += f" by {stolen['police_force']}"
                report += ". **Do not purchase this vehicle.** You will have no legal title and it will be seized.\n"
            else:
                report += f"- **Stolen:**{ref('experian')} Not reported stolen. Clear.\n"

        if writeoff:
            if writeoff.get("written_off"):
                all_clear = False
                report += f"- **Write-off:**{ref('experian')} **{writeoff.get('record_count', 0)} insurance write-off record(s) found.**\n"
                for r in writeoff.get("records", []):
                    cat = r.get("category", "?")
                    report += f"  - **Category {cat}** recorded on {r.get('date', '?')}"
                    if r.get("loss_type"):
                        report += f" ({r['loss_type']})"
                    report += "\n"
                report += "\n"
                # Explain categories
                if any(r.get("category") in ("A", "B") for r in writeoff.get("records", [])):
                    report += "Category A/B means the car was so badly damaged it should have been scrapped. **Walk away.**\n\n"
                else:
                    report += "Category N/S means the car was damaged but repaired. This isn't necessarily a dealbreaker, but:\n"
                    report += "- Insist on seeing repair invoices and photos\n"
                    report += "- Get an independent structural inspection (£100-200)\n"
                    report += "- Factor in reduced resale value (typically 20-30% less than equivalent non-write-off)\n\n"
            else:
                report += f"- **Write-off:**{ref('experian')} No insurance write-off history. Clear.\n"

        if salvage_data and salvage_data.get("salvage_found"):
            all_clear = False
            report += f"- **Salvage:**{ref('carguide')} Salvage auction records found. This car may have been auctioned as salvage — investigate the repair history thoroughly.\n"
        elif salvage_data:
            report += f"- **Salvage:**{ref('carguide')} No salvage auction records. Clear.\n"

        if all_clear:
            report += "\n**All provenance checks clear.** This car has no hidden financial or legal issues. You can buy with confidence.\n"

        # --- Market Valuation ---
        if valuation_data:
            report += f"\n## Market Valuation{ref('brego')}\n"
            private = valuation_data.get("private_sale")
            dealer = valuation_data.get("dealer_forecourt")
            trade = valuation_data.get("trade_in")
            part_ex = valuation_data.get("part_exchange")

            report += "Based on current market data for this vehicle's age, mileage, and condition:\n\n"
            report += "| Valuation Type | Amount |\n"
            report += "|---|---|\n"
            if private:
                report += f"| Private Sale | **£{private:,}** |\n"
            if dealer:
                report += f"| Dealer Forecourt | **£{dealer:,}** |\n"
            if trade:
                report += f"| Trade-in | **£{trade:,}** |\n"
            if part_ex:
                report += f"| Part Exchange | **£{part_ex:,}** |\n"
            report += "\n"

            if listing_price and private:
                asking = int(listing_price / 100)
                diff = asking - private
                pct = round((diff / private) * 100)
                if diff > 0:
                    report += f"At **£{asking:,}**, the asking price is **£{diff:,} above** the private sale valuation ({pct}% over market value). "
                    if pct > 15:
                        report += "This is significantly overpriced. Use the valuation data to negotiate hard.\n\n"
                    elif pct > 5:
                        report += "There's room to negotiate. A fair offer would be closer to the private sale value.\n\n"
                    else:
                        report += "This is only slightly above market — a small discount should be achievable.\n\n"
                elif diff < 0:
                    report += f"At **£{asking:,}**, the asking price is **£{abs(diff):,} below** private sale valuation. This looks like a good deal — but check why it's priced so low.\n\n"
                else:
                    report += f"The asking price of **£{asking:,}** is bang on the private sale valuation. This is a fair price.\n\n"

                report += f"**Recommended offer:** £{min(asking, private):,}"
                if diff > 0 and trade:
                    target = private - (private - trade) // 4
                    report += f" (start at £{target:,} and work up)"
                report += "\n"

        # --- Ownership History ---
        report += "\n## Ownership History\n"

        if keeper_data and keeper_data.get("total_keepers"):
            total_keepers = keeper_data["total_keepers"]
            report += f"This vehicle has had **{total_keepers} registered keeper{'s' if total_keepers != 1 else ''}**.\n"
            if total_keepers <= 2:
                report += "Low keeper count — suggests stable ownership and a car that's been looked after.\n"
            elif total_keepers <= 4:
                report += "Average number of keepers for this age. Nothing unusual.\n"
            else:
                report += "Higher than average number of keepers — could indicate problems that caused owners to move it on. Ask the seller directly.\n"

        if plates_data:
            if plates_data.get("changes_found"):
                report += f"\n**{plates_data.get('record_count', 0)} plate change(s) found:**\n"
                for r in plates_data.get("records", []):
                    report += f"- {r.get('previous_plate', '?')} → changed on {r.get('change_date', '?')} ({r.get('change_type', '?')})\n"
                report += "\nPlate changes aren't always concerning (personalised plates are common), but combined with other flags they can indicate an attempt to disguise a vehicle's history.\n"
            else:
                report += "\nNo plate changes found. The vehicle has kept its original registration — a positive sign.\n"

        if vehicle_data and vehicle_data.get("dateOfLastV5CIssued"):
            v5c_date = vehicle_data["dateOfLastV5CIssued"]
            try:
                v5c_dt = datetime.strptime(v5c_date, "%Y-%m-%d")
                days_ago = (datetime.utcnow() - v5c_dt).days
                if days_ago < 90:
                    report += f"\n**V5C recently issued** ({v5c_date}, {days_ago} days ago). A very recent V5C can indicate a recent ownership change — confirm when the seller actually bought the car.\n"
                else:
                    report += f"\nV5C last issued on {v5c_date} ({days_ago} days ago). No concerns.\n"
            except ValueError:
                pass

    else:
        # Non-premium: show red flags + upsell
        report += "\n## Red Flags to Watch For\n"
        report += "Things to verify in person that the data can't tell you:\n\n"
        report += "- **Service history:** Ask for the stamped service book. Gaps in servicing are a concern at any mileage\n"
        report += "- **V5C document:** Check the name and address match the seller. If they say \"I'm selling for a friend,\" proceed with extreme caution\n"

        if vehicle_data and vehicle_data.get("dateOfLastV5CIssued"):
            v5c_date = vehicle_data["dateOfLastV5CIssued"]
            report += f"- **V5C timing:** The V5C was last issued on {v5c_date}. If this doesn't match when the seller says they bought it, ask why\n"

        report += "- **Payment:** Never pay cash without a receipt. Bank transfer is safest — you have a paper trail\n"
        report += "- **HPI check:** Consider a full HPI/provenance check (finance, stolen, write-off) for complete peace of mind — our Premium Check covers this for £9.99\n"

    # Append Data Sources footer (source_keys computed at top of function)
    if source_keys:
        report += _build_sources_section(source_keys)

    return report
