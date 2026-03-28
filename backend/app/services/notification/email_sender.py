"""Email delivery service using Resend API."""

import base64
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from jinja2 import Environment, FileSystemLoader

from app.core.config import settings
from app.core.logging import logger

TEMPLATE_DIR = Path(__file__).resolve().parents[3] / "templates" / "email"


def _build_checks_summary(check_data: Dict) -> List[Dict[str, str]]:
    """Build a pass/fail checklist for the At a Glance section.

    Items are ordered by severity — most critical (stolen, finance, write-off) first.
    Each item has: status, icon, colour, bg, label, detail.
    """
    items = []

    # --- Provenance checks (premium tier) ---

    # Stolen (highest risk — illegal to buy)
    stolen = check_data.get("stolen_check")
    if stolen:
        if stolen.get("stolen"):
            items.append({"status": "fail", "icon": "❌", "colour": "#dc2626", "bg": "#fee2e2",
                          "label": "Reported Stolen",
                          "detail": "Do not purchase — this vehicle has a stolen marker"})
        else:
            items.append({"status": "pass", "icon": "✅", "colour": "#059669", "bg": "#f0fdf4",
                          "label": "Not Stolen", "detail": "Clear — no stolen marker"})

    # Finance (legal ownership risk)
    finance = check_data.get("finance_check")
    if finance:
        if finance.get("finance_outstanding"):
            count = finance.get("record_count", 1)
            items.append({"status": "fail", "icon": "❌", "colour": "#dc2626", "bg": "#fee2e2",
                          "label": "Finance Outstanding",
                          "detail": f"{count} active agreement{'s' if count != 1 else ''} — lender may repossess"})
        else:
            items.append({"status": "pass", "icon": "✅", "colour": "#059669", "bg": "#f0fdf4",
                          "label": "No Finance Outstanding", "detail": "Clear — safe to purchase"})

    # Write-off
    writeoff = check_data.get("write_off_check")
    if writeoff:
        if writeoff.get("written_off"):
            cats = [r.get("category") for r in writeoff.get("records", []) if r.get("category")]
            cat_str = " / ".join(f"Cat {c}" for c in cats) if cats else "category unknown"
            items.append({"status": "fail", "icon": "❌", "colour": "#dc2626", "bg": "#fee2e2",
                          "label": "Insurance Write-Off Found",
                          "detail": f"{cat_str} — affects insurance cost and resale value"})
        else:
            items.append({"status": "pass", "icon": "✅", "colour": "#059669", "bg": "#f0fdf4",
                          "label": "No Write-Off History", "detail": "Clear — not written off"})

    # Salvage
    salvage = check_data.get("salvage_check")
    if salvage:
        if salvage.get("salvage_found"):
            items.append({"status": "warn", "icon": "⚠️", "colour": "#d97706", "bg": "#fffbeb",
                          "label": "Salvage Records Found",
                          "detail": "Vehicle appears in salvage auction records"})
        else:
            items.append({"status": "pass", "icon": "✅", "colour": "#059669", "bg": "#f0fdf4",
                          "label": "No Salvage Records", "detail": "Clear — no auction history"})

    # --- Core checks (all tiers) ---

    # Clocking
    clocking = check_data.get("clocking_analysis") or {}
    if clocking.get("clocked"):
        items.append({"status": "fail", "icon": "❌", "colour": "#dc2626", "bg": "#fee2e2",
                      "label": "Mileage Discrepancy Detected",
                      "detail": "Odometer may have been tampered with"})
    else:
        items.append({"status": "pass", "icon": "✅", "colour": "#059669", "bg": "#f0fdf4",
                      "label": "Mileage Verified", "detail": "Consistent history — no clocking detected"})

    # MOT
    vehicle = check_data.get("vehicle") or {}
    mot_status = vehicle.get("mot_status", "")
    stats = check_data.get("vehicle_stats") or {}
    mot_days = stats.get("mot_days_remaining")
    if mot_status == "Valid":
        if mot_days is not None and mot_days < 60:
            items.append({"status": "warn", "icon": "⚠️", "colour": "#d97706", "bg": "#fffbeb",
                          "label": "MOT Valid",
                          "detail": f"Expires in {mot_days} days — use as negotiation leverage"})
        else:
            detail = f"{mot_days} days remaining" if mot_days else "Currently valid"
            items.append({"status": "pass", "icon": "✅", "colour": "#059669", "bg": "#f0fdf4",
                          "label": "MOT Valid", "detail": detail})
    elif mot_status:
        items.append({"status": "fail", "icon": "❌", "colour": "#dc2626", "bg": "#fee2e2",
                      "label": "MOT Not Valid", "detail": f"Status: {mot_status}"})

    # ULEZ / CAZ
    ulez = check_data.get("ulez_compliance") or {}
    if ulez.get("compliant") is False:
        charge = ulez.get("daily_charge", "charges apply")
        items.append({"status": "warn", "icon": "⚠️", "colour": "#d97706", "bg": "#fffbeb",
                      "label": "CAZ Non-Compliant",
                      "detail": f"{charge} in affected UK zones"})
    elif ulez.get("compliant") is True:
        items.append({"status": "pass", "icon": "✅", "colour": "#059669", "bg": "#f0fdf4",
                      "label": "All Clean Air Zones Clear", "detail": "Compliant with all UK zones"})

    return items


def _score_colour(score: Optional[int]) -> str:
    if score is None:
        return "#64748b"
    if score >= 80:
        return "#059669"
    if score >= 50:
        return "#f59e0b"
    return "#dc2626"


def _verdict_bg(verdict: Optional[str]) -> str:
    return {
        "BUY": "#059669",
        "NEGOTIATE": "#f59e0b",
        "AVOID": "#dc2626",
    }.get(verdict or "", "#64748b")


def render_report_email(
    check_data: Dict,
    verdict: Optional[str] = None,
    report_ref: str = "",
) -> str:
    """Render the report email HTML from template.

    Args:
        check_data: Serialised FreeCheckResponse dict
        verdict: BUY/NEGOTIATE/AVOID or None
        report_ref: Report reference number

    Returns:
        Rendered HTML string.
    """
    env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)), autoescape=True)
    template = env.get_template("report.html")

    vehicle = check_data.get("vehicle") or {}
    mot_summary = check_data.get("mot_summary") or {}

    context = {
        "registration": check_data.get("registration", ""),
        "make": vehicle.get("make", mot_summary.get("make", "")),
        "model": mot_summary.get("model", ""),
        "year": vehicle.get("year_of_manufacture", ""),
        "condition_score": check_data.get("condition_score"),
        "score_colour": _score_colour(check_data.get("condition_score")),
        "verdict": verdict,
        "verdict_bg_colour": _verdict_bg(verdict),
        "checks_summary": _build_checks_summary(check_data),
        "report_ref": report_ref,
        "report_url": "#",  # Placeholder — no web view yet
        "unsubscribe_url": "#",
        "year_now": datetime.utcnow().year,
        # Full data sections
        "vehicle": vehicle if vehicle else None,
        "mot_tests": check_data.get("mot_tests", []),
        "mileage_timeline": check_data.get("mileage_timeline", []),
        "clocking_analysis": check_data.get("clocking_analysis"),
        "failure_patterns": check_data.get("failure_patterns", []),
        "ulez": check_data.get("ulez_compliance") or {},
        "tax": check_data.get("tax_calculation"),
        "safety": check_data.get("safety_rating"),
        "stats": check_data.get("vehicle_stats"),
        # EV sections
        "battery_health": check_data.get("battery_health"),
        "range_estimate": check_data.get("range_estimate"),
        "range_scenarios": check_data.get("range_scenarios", []),
        "charging_costs": check_data.get("charging_costs"),
        "ev_specs": check_data.get("ev_specs"),
        "lifespan_prediction": check_data.get("lifespan_prediction"),
        # Premium sections
        "finance": check_data.get("finance_check"),
        "stolen": check_data.get("stolen_check"),
        "writeoff": check_data.get("write_off_check"),
        "plates": check_data.get("plate_changes"),
        "valuation": check_data.get("valuation"),
        "keeper_history": check_data.get("keeper_history"),
        "salvage": check_data.get("salvage_check"),
        "tier": check_data.get("tier", "free"),
    }

    return template.render(**context)


async def send_report_email(
    to_email: str,
    check_data: Dict,
    pdf_bytes: bytes,
    verdict: Optional[str] = None,
    report_ref: str = "",
) -> bool:
    """Send the vehicle report via Resend with PDF attachment.

    Args:
        to_email: Recipient email address
        check_data: Serialised FreeCheckResponse dict
        pdf_bytes: Generated PDF as bytes
        verdict: BUY/NEGOTIATE/AVOID
        report_ref: Report reference number

    Returns:
        True if sent successfully, False otherwise.
    """
    if not settings.RESEND_API_KEY or settings.RESEND_API_KEY.startswith("your_"):
        logger.warning("Resend API key not configured — email not sent")
        return False

    try:
        import resend

        resend.api_key = settings.RESEND_API_KEY

        registration = check_data.get("registration", "UNKNOWN")
        html_content = render_report_email(check_data, verdict, report_ref)

        filename = f"VeriCar-{registration}-{report_ref}.pdf"

        result = resend.Emails.send({
            "from": settings.FROM_EMAIL,
            "to": [to_email],
            "subject": f"Your VeriCar Report — {registration}",
            "html": html_content,
            "attachments": [
                {
                    "filename": filename,
                    "content": base64.b64encode(pdf_bytes).decode("utf-8"),
                    "content_type": "application/pdf",
                }
            ],
        })

        logger.info(f"Report email sent to {to_email} for {registration} (ref: {report_ref}, id: {result.get('id', '?')})")
        return True

    except Exception as e:
        logger.error(f"Failed to send report email to {to_email}: {e}")
        return False
