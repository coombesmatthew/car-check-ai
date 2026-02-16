"""PDF report generator using WeasyPrint + Jinja2.

Renders the HTML template with vehicle check data and converts to PDF.
"""

import re
import uuid
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Dict, List, Optional

from jinja2 import Environment, FileSystemLoader

from app.core.logging import logger

# Template directory
TEMPLATE_DIR = Path(__file__).resolve().parents[3] / "templates" / "pdf"


def _parse_ai_sections(report_text: str) -> List[Dict[str, str]]:
    """Parse markdown AI report into structured sections."""
    sections = []
    if not report_text:
        return sections

    current_title = None
    current_lines: List[str] = []

    for line in report_text.split("\n"):
        if line.startswith("## "):
            if current_title:
                content = "\n".join(current_lines).strip()
                # Convert markdown bold to HTML
                content = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", content)
                # Convert markdown list items to HTML
                content = re.sub(r"^- (.+)$", r"<li>\1</li>", content, flags=re.MULTILINE)
                if "<li>" in content:
                    content = re.sub(
                        r"((?:<li>.*?</li>\n?)+)",
                        r"<ul>\1</ul>",
                        content,
                        flags=re.DOTALL,
                    )
                # Wrap paragraphs
                paragraphs = content.split("\n\n")
                content = "".join(
                    f"<p>{p.strip()}</p>" if not p.strip().startswith("<") else p
                    for p in paragraphs
                    if p.strip()
                )
                sections.append({"title": current_title, "content": content})
            current_title = line.lstrip("# ").strip()
            current_lines = []
        else:
            current_lines.append(line)

    # Don't forget the last section
    if current_title:
        content = "\n".join(current_lines).strip()
        content = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", content)
        content = re.sub(r"^- (.+)$", r"<li>\1</li>", content, flags=re.MULTILINE)
        if "<li>" in content:
            content = re.sub(
                r"((?:<li>.*?</li>\n?)+)",
                r"<ul>\1</ul>",
                content,
                flags=re.DOTALL,
            )
        paragraphs = content.split("\n\n")
        content = "".join(
            f"<p>{p.strip()}</p>" if not p.strip().startswith("<") else p
            for p in paragraphs
            if p.strip()
        )
        sections.append({"title": current_title, "content": content})

    return sections


def _extract_verdict(report_text: str) -> Optional[str]:
    """Extract BUY/NEGOTIATE/AVOID verdict from report text."""
    if not report_text:
        return None
    upper = report_text.upper()
    if "**AVOID**" in report_text or "AVOID" in upper.split("RECOMMENDATION")[1:2]:
        return "AVOID"
    if "**NEGOTIATE**" in report_text or "NEGOTIATE" in upper.split("RECOMMENDATION")[1:2]:
        return "NEGOTIATE"
    if "**BUY**" in report_text or "BUY" in upper.split("RECOMMENDATION")[1:2]:
        return "BUY"
    return None


def generate_pdf(
    check_data: Dict,
    ai_report: Optional[str] = None,
) -> bytes:
    """Generate a PDF report from check data.

    Args:
        check_data: Serialised FreeCheckResponse dict
        ai_report: Markdown AI report text (optional, for BASIC tier)

    Returns:
        PDF file contents as bytes.
    """
    try:
        from weasyprint import HTML
    except ImportError:
        logger.error("WeasyPrint not installed — cannot generate PDF")
        raise RuntimeError("PDF generation requires WeasyPrint")

    env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))
    template = env.get_template("report.html")

    # Extract data
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

    # Verdict
    verdict = _extract_verdict(ai_report) if ai_report else None
    verdict_class = {
        "BUY": "buy",
        "NEGOTIATE": "negotiate",
        "AVOID": "avoid",
    }.get(verdict, "")

    # Score class
    if condition_score is not None:
        if condition_score >= 80:
            score_class = "score-green"
        elif condition_score >= 50:
            score_class = "score-amber"
        else:
            score_class = "score-red"
    else:
        score_class = ""

    # AI sections
    ai_sections = _parse_ai_sections(ai_report) if ai_report else []

    # Report reference
    report_ref = f"CV-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"

    context = {
        "registration": check_data.get("registration", ""),
        "make": vehicle.get("make", mot_summary.get("make", "")),
        "model": mot_summary.get("model", ""),
        "year": vehicle.get("year_of_manufacture", ""),
        "colour": vehicle.get("colour", ""),
        "fuel_type": vehicle.get("fuel_type", ""),
        "condition_score": condition_score,
        "score_class": score_class,
        "verdict": verdict,
        "verdict_class": verdict_class,
        "generated_date": datetime.utcnow().strftime("%d %B %Y at %H:%M UTC"),
        "report_ref": report_ref,
        "ai_report_sections": ai_sections,
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
    }

    html_content = template.render(**context)

    # Generate PDF
    pdf_bytes = HTML(string=html_content).write_pdf()
    logger.info(f"PDF generated for {check_data.get('registration', '?')} ({len(pdf_bytes)} bytes, ref: {report_ref})")
    return pdf_bytes
