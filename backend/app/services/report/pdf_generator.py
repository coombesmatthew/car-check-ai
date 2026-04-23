"""PDF report generator using WeasyPrint + Jinja2.

Renders the HTML template with vehicle check data and converts to PDF.
"""

import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from jinja2 import Environment, FileSystemLoader

from app.core.logging import logger

TEMPLATE_DIR = Path(__file__).resolve().parents[3] / "templates" / "pdf"


def _build_checks_summary(check_data: Dict) -> List[Dict]:
    """Build pass/fail checklist items for the PDF At a Glance section."""
    items = []

    stolen = check_data.get("stolen_check")
    if stolen:
        if stolen.get("stolen"):
            items.append({"status": "fail", "icon": "✗", "label": "Reported Stolen",
                          "detail": "Do not purchase — stolen marker on record"})
        else:
            items.append({"status": "pass", "icon": "✓", "label": "Not Stolen",
                          "detail": "Clear"})

    finance = check_data.get("finance_check")
    if finance:
        if finance.get("finance_outstanding"):
            count = finance.get("record_count", 1)
            items.append({"status": "fail", "icon": "✗", "label": "Finance Outstanding",
                          "detail": f"{count} active agreement{'s' if count != 1 else ''} — lender may repossess"})
        else:
            items.append({"status": "pass", "icon": "✓", "label": "No Finance Outstanding",
                          "detail": "Clear — safe to purchase"})

    writeoff = check_data.get("write_off_check")
    if writeoff:
        if writeoff.get("written_off"):
            cats = [r.get("category") for r in writeoff.get("records", []) if r.get("category")]
            cat_str = " / ".join(f"Cat {c}" for c in cats) if cats else "category unknown"
            items.append({"status": "fail", "icon": "✗", "label": "Insurance Write-Off Found",
                          "detail": f"{cat_str} — affects insurance and resale value"})
        else:
            items.append({"status": "pass", "icon": "✓", "label": "No Write-Off History",
                          "detail": "Clear"})

    salvage = check_data.get("salvage_check")
    if salvage:
        if salvage.get("salvage_found"):
            items.append({"status": "warn", "icon": "!", "label": "Salvage Records Found",
                          "detail": "Appears in salvage auction records"})
        else:
            items.append({"status": "pass", "icon": "✓", "label": "No Salvage Records",
                          "detail": "Clear"})

    clocking = check_data.get("clocking_analysis") or {}
    if clocking.get("clocked"):
        items.append({"status": "fail", "icon": "✗", "label": "Mileage Discrepancy",
                      "detail": "Odometer tampering suspected"})
    else:
        items.append({"status": "pass", "icon": "✓", "label": "Mileage Verified",
                      "detail": "No clocking detected"})

    vehicle = check_data.get("vehicle") or {}
    mot_status = vehicle.get("mot_status", "")
    stats = check_data.get("vehicle_stats") or {}
    mot_days = stats.get("mot_days_remaining")
    if mot_status == "Valid":
        if mot_days is not None and mot_days < 60:
            items.append({"status": "warn", "icon": "!", "label": "MOT Valid",
                          "detail": f"Expires in {mot_days} days — use as leverage"})
        else:
            detail = f"{mot_days} days remaining" if mot_days else "Currently valid"
            items.append({"status": "pass", "icon": "✓", "label": "MOT Valid", "detail": detail})
    elif mot_status:
        items.append({"status": "fail", "icon": "✗", "label": "MOT Not Valid",
                      "detail": f"Status: {mot_status}"})

    ulez = check_data.get("ulez_compliance") or {}
    if ulez.get("compliant") is False:
        charge = ulez.get("daily_charge", "charges apply")
        items.append({"status": "warn", "icon": "!", "label": "CAZ Non-Compliant",
                      "detail": f"{charge} in affected UK zones"})
    elif ulez.get("compliant") is True:
        items.append({"status": "pass", "icon": "✓", "label": "All Clean Air Zones Clear",
                      "detail": "Compliant with all UK zones"})

    return items


def generate_pdf(check_data: Dict) -> bytes:
    """Generate a PDF report from check data."""
    try:
        from weasyprint import HTML
    except ImportError:
        logger.error("WeasyPrint not installed — cannot generate PDF")
        raise RuntimeError("PDF generation requires WeasyPrint")

    env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))
    template = env.get_template("report.html")

    vehicle = check_data.get("vehicle") or {}
    mot_summary = check_data.get("mot_summary") or {}
    ulez = check_data.get("ulez_compliance") or {}
    tax = check_data.get("tax_calculation")
    safety = check_data.get("safety_rating")
    stats = check_data.get("vehicle_stats")
    mot_tests = check_data.get("mot_tests", [])
    mileage_timeline = check_data.get("mileage_timeline", [])
    condition_score = check_data.get("condition_score")
    finance = check_data.get("finance_check")
    stolen = check_data.get("stolen_check")
    writeoff = check_data.get("write_off_check")
    plates = check_data.get("plate_changes")
    valuation = check_data.get("valuation")

    battery_health = check_data.get("battery_health")
    range_estimate = check_data.get("range_estimate")
    range_scenarios = check_data.get("range_scenarios", [])
    charging_costs = check_data.get("charging_costs")
    ev_specs = check_data.get("ev_specs")
    lifespan_prediction = check_data.get("lifespan_prediction")

    checks_summary = _build_checks_summary(check_data)

    if condition_score is not None:
        if condition_score >= 80:
            score_class = "score-green"
        elif condition_score >= 50:
            score_class = "score-amber"
        else:
            score_class = "score-red"
    else:
        score_class = ""

    is_ev = battery_health is not None or check_data.get("is_electric")
    ref_prefix = "EV" if is_ev else "CV"
    report_ref = f"{ref_prefix}-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"

    context = {
        "registration": check_data.get("registration", ""),
        "make": vehicle.get("make", mot_summary.get("make", "")),
        "model": mot_summary.get("model", ""),
        "year": vehicle.get("year_of_manufacture", ""),
        "colour": vehicle.get("colour", ""),
        "fuel_type": vehicle.get("fuel_type", ""),
        "condition_score": condition_score,
        "score_class": score_class,
        "checks_summary": checks_summary,
        "generated_date": datetime.utcnow().strftime("%d %B %Y at %H:%M UTC"),
        "report_ref": report_ref,
        "vehicle": vehicle if vehicle else None,
        "tax": tax,
        "mileage_timeline": mileage_timeline,
        "mot_tests": mot_tests,
        "ulez": ulez if ulez else None,
        "safety": safety,
        "stats": stats,
        "finance": finance,
        "stolen": stolen,
        "writeoff": writeoff,
        "plates": plates,
        "valuation": valuation,
        "battery_health": battery_health,
        "range_estimate": range_estimate,
        "range_scenarios": range_scenarios,
        "charging_costs": charging_costs,
        "ev_specs": ev_specs,
        "lifespan_prediction": lifespan_prediction,
    }

    html_content = template.render(**context)

    pdf_bytes = HTML(string=html_content).write_pdf()
    logger.info(f"PDF generated for {check_data.get('registration', '?')} ({len(pdf_bytes)} bytes, ref: {report_ref})")
    return pdf_bytes
