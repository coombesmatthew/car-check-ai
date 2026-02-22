"""Email delivery service using Resend API."""

import base64
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from jinja2 import Environment, FileSystemLoader

from app.core.config import settings
from app.core.logging import logger

TEMPLATE_DIR = Path(__file__).resolve().parents[3] / "templates" / "email"


def _build_key_findings(check_data: Dict, verdict: Optional[str]) -> List[Dict[str, str]]:
    """Extract key findings from check data for email summary."""
    findings = []

    # Condition score
    score = check_data.get("condition_score")
    if score is not None:
        if score >= 80:
            findings.append({"icon": "&#9989;", "colour": "#059669", "text": f"Condition score: {score}/100 — Good condition"})
        elif score >= 50:
            findings.append({"icon": "&#9888;", "colour": "#f59e0b", "text": f"Condition score: {score}/100 — Some concerns"})
        else:
            findings.append({"icon": "&#10060;", "colour": "#dc2626", "text": f"Condition score: {score}/100 — Poor condition"})

    # Clocking
    clocking = check_data.get("clocking_analysis") or {}
    if clocking.get("clocked"):
        findings.append({"icon": "&#10060;", "colour": "#dc2626", "text": "Mileage discrepancy detected — possible clocking"})
    elif clocking.get("risk_level") == "none":
        findings.append({"icon": "&#9989;", "colour": "#059669", "text": "Mileage history clean — no clocking detected"})

    # MOT summary
    mot = check_data.get("mot_summary") or {}
    total_tests = mot.get("total_tests", 0)
    total_failures = mot.get("total_failures", 0)
    if total_tests > 0:
        if total_failures == 0:
            findings.append({"icon": "&#9989;", "colour": "#059669", "text": f"{total_tests} MOT tests — never failed"})
        else:
            findings.append({"icon": "&#9888;", "colour": "#f59e0b", "text": f"{total_tests} MOT tests — {total_failures} failure{'s' if total_failures != 1 else ''}"})

    # ULEZ
    ulez = check_data.get("ulez_compliance") or {}
    if ulez.get("compliant") is True:
        findings.append({"icon": "&#9989;", "colour": "#059669", "text": "Compliant with all UK clean air zones"})
    elif ulez.get("compliant") is False:
        findings.append({"icon": "&#10060;", "colour": "#dc2626", "text": f"Non-compliant — {ulez.get('daily_charge', 'charges apply')}"})

    # Failure patterns
    patterns = check_data.get("failure_patterns", [])
    for p in patterns[:2]:
        findings.append({"icon": "&#9888;", "colour": "#f59e0b", "text": f"Recurring {p['category']} issues ({p['occurrences']}x)"})

    return findings[:6]  # Cap at 6 findings


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
    env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))
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
        "key_findings": _build_key_findings(check_data, verdict),
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
