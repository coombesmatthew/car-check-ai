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


def _normalize_text(text: str) -> str:
    """Normalize common text patterns in AI reports."""
    # Convert "If you are BUYING" to "If you are buying"
    text = re.sub(r'\*\*If you are BUYING', r'**If you are buying', text)

    # Clarify Known Issues section header
    text = re.sub(
        r'### Known Issues — ',
        r'### Known Issues for ',
        text
    )
    return text


def _convert_decimal_years(text: str) -> str:
    """Convert decimal years (e.g., 14.94 years) to years + months format."""
    def replace_year(match):
        decimal_years = float(match.group(1))
        years = int(decimal_years)
        months = round((decimal_years % 1) * 12)
        return f"{years} years, {months} months"

    return re.sub(r'(\d+\.\d+)\s+years?', replace_year, text)


def _convert_known_issues_to_table(content: str) -> str:
    """Convert Known Issues format (**PRIORITY — Name** + text) into a 3-column table."""
    # Match pattern: **(HIGH|MEDIUM|LOW) PRIORITY — Issue Name** followed by text
    pattern = r'\*\*((HIGH|MEDIUM|LOW)\s+PRIORITY)\s*—\s*([^*]+)\*\*\s+([^\n]*(?:\n(?!\*\*[HML][A-Z]+ PRIORITY)[^\n]*)*)'

    def has_known_issues_header(text):
        return 'Known Issues for' in text or 'Known Issues —' in text

    if not has_known_issues_header(content):
        return content

    # Find where known issues section starts
    known_issues_match = re.search(r'### Known Issues', content)
    if not known_issues_match:
        return content

    # Get intro paragraph (from section to first proper issue)
    section_start = known_issues_match.start()
    first_issue = re.search(pattern, content[section_start:])

    if not first_issue:
        return content

    # Extract all issues
    issues_text = content[section_start + first_issue.start():]
    matches = list(re.finditer(pattern, issues_text))

    if len(matches) < 1:
        return content

    # Build table with 3 columns
    table_html = '\n\n<table class="data-table" style="font-size: 9pt;"><thead><tr><th style="width:15%">Priority</th><th style="width:25%">Issue</th><th>Details & Action Items</th></tr></thead><tbody>'

    for match in matches:
        priority = match.group(1).strip()  # e.g., "HIGH PRIORITY"
        issue_name = match.group(3).strip()  # Issue name after the em-dash
        issue_text = match.group(4).strip()  # The detailed text
        # Clean up text
        issue_text = re.sub(r'\n+', ' ', issue_text)
        table_html += f'<tr><td><strong>{priority}</strong></td><td><strong>{issue_name}</strong></td><td>{issue_text}</td></tr>'

    table_html += '</tbody></table>'

    # Replace the matched issues with the table
    replacement_start = section_start + first_issue.start()
    replacement_end = replacement_start + matches[-1].end()

    return content[:replacement_start] + table_html + content[replacement_end:]


def _md_to_html(content: str, citation_urls: Optional[Dict[int, str]] = None) -> str:
    """Convert markdown content block to HTML."""
    # Normalize text patterns first
    content = _normalize_text(content)

    # Convert decimal years to years + months format
    content = _convert_decimal_years(content)

    # Convert known issues to table format
    content = _convert_known_issues_to_table(content)

    # Markdown links [text](url) → clickable link
    content = re.sub(
        r"\[([^\]]+)\]\(([^)]+)\)",
        r'<a href="\2" style="color:#64748b;">\1</a>',
        content,
    )
    # Citation numbers [N] → superscript linked to source URL if known
    def _cite(m: re.Match) -> str:
        n = int(m.group(1))
        url = (citation_urls or {}).get(n, "")
        style = "font-size:7pt;color:#94a3b8;text-decoration:none;"
        if url:
            return f'<a href="{url}" style="{style}"><sup>{n}</sup></a>'
        return f'<sup style="font-size:7pt;color:#94a3b8;">{n}</sup>'

    content = re.sub(r"\[(\d+)\]", _cite, content)
    # Bold
    content = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", content)
    # Italic — avoid matching bold remnants
    content = re.sub(r"(?<!\*)\*(?!\*)(.*?)(?<!\*)\*(?!\*)", r"<em>\1</em>", content)

    # Expand inline tables: AI often outputs entire table on one line.
    # Row boundary is "| |" (pipe-space-pipe).
    content = re.sub(r"\| \|", "|\n|", content)

    # Ensure ### and ## headings always start on their own line.
    # Exclude '#' from the preceding character to avoid splitting '###' into '#' + '## '.
    content = re.sub(r"([^\n#])(#{2,3} )", r"\1\n\2", content)

    lines = content.split("\n")
    output: List[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # H2 subheading (Claude sometimes uses ## inside sections)
        if stripped.startswith("## "):
            heading_text = stripped[3:].strip()
            # Numbered sections (e.g. "1. OVERALL CONDITION ASSESSMENT") → h2 triggers page break
            if re.match(r"^\d+\.", heading_text):
                output.append(f'<h2 style="font-size:13pt;font-weight:700;color:#1e293b;margin:0 0 3mm;">{heading_text}</h2>')
            else:
                output.append(f'<h3 style="font-size:11pt;font-weight:700;color:#1e293b;margin:4mm 0 2mm;">{heading_text}</h3>')
            i += 1

        # H3 subheading
        elif stripped.startswith("### "):
            output.append(f'<h4 style="font-size:10pt;font-weight:700;color:#1e293b;margin:3mm 0 1mm;">{stripped[4:].strip()}</h4>')
            i += 1

        # Horizontal rule — skip (dividers are cosmetic noise in PDF sections)
        elif stripped == "---":
            i += 1

        # Blockquote > "..."
        elif stripped.startswith("> "):
            quote_lines = []
            while i < len(lines) and lines[i].strip().startswith("> "):
                quote_lines.append(lines[i].strip()[2:])
                i += 1
            quote_html = " ".join(quote_lines)
            output.append(f'<blockquote style="margin:2mm 0 2mm 4mm;padding:2mm 3mm;border-left:3px solid #cbd5e1;color:#475569;font-style:italic;">{quote_html}</blockquote>')

        # Pipe table
        elif stripped.startswith("|"):
            table_lines = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                table_lines.append(lines[i])
                i += 1
            if len(table_lines) >= 2:
                html = '<table class="ai-table">'
                first_data_row = True
                for row in table_lines:
                    cells = [c.strip() for c in row.strip().strip("|").split("|")]
                    # skip separator row (---|---)
                    if all(re.match(r"^[-: ]+$", c) for c in cells if c):
                        continue
                    tag = "th" if first_data_row else "td"
                    first_data_row = False

                    # Detect and style Total row specially
                    is_total_row = cells and "Total" in cells[0]
                    if is_total_row:
                        html += '<tr style="background: #f1f5f9; font-weight: 700; border-top: 2px solid #1e293b;">'
                        html += "".join(f"<{tag} style='font-weight:700;'>{c}</{tag}>" for c in cells)
                        html += "</tr>"
                    else:
                        html += "<tr>" + "".join(f"<{tag}>{c}</{tag}>" for c in cells) + "</tr>"
                html += "</table>"
                output.append(html)

        # Numbered list
        elif re.match(r"^\d+\. ", stripped):
            items = []
            while i < len(lines) and re.match(r"^\d+\. ", lines[i].strip()):
                text = re.sub(r"^\d+\. ", "", lines[i].strip())
                items.append(f"<li>{text}</li>")
                i += 1
            output.append("<ol>" + "".join(items) + "</ol>")

        # Unordered list
        elif stripped.startswith("- ") or stripped.startswith("• ") or stripped.startswith("* "):
            items = []
            while i < len(lines):
                s = lines[i].strip()
                if s.startswith("- ") or s.startswith("• ") or s.startswith("* "):
                    items.append(f"<li>{s[2:].strip()}</li>")
                    i += 1
                else:
                    break
            output.append("<ul>" + "".join(items) + "</ul>")

        # Blank line
        elif not stripped:
            i += 1

        # Normal paragraph — collect until blank or block element
        else:
            para_lines = []
            while i < len(lines):
                s = lines[i].strip()
                if not s:
                    break
                if s.startswith(("## ", "### ", "- ", "• ", "* ", "> ", "|")) or re.match(r"^\d+\. ", s) or s == "---":
                    break
                para_lines.append(s)
                i += 1
            if para_lines:
                output.append(f"<p>{' '.join(para_lines)}</p>")

    return "".join(output)


def _extract_citation_urls(report_text: str) -> Dict[int, str]:
    """Build a {citation_number: url} map from the Data Sources section."""
    urls: Dict[int, str] = {}
    in_sources = False
    for line in report_text.split("\n"):
        if line.startswith("## ") and "source" in line.lower():
            in_sources = True
            continue
        if in_sources:
            if line.startswith("## "):
                break
            # "1. [Title](url)"
            m = re.match(r"^(\d+)\.\s+\[([^\]]+)\]\(([^)]+)\)", line)
            if m:
                urls[int(m.group(1))] = m.group(3)
                continue
            # "1. https://..."
            m = re.match(r"^(\d+)\.\s+(https?://\S+)", line)
            if m:
                urls[int(m.group(1))] = m.group(2)
    return urls


def _parse_ai_sections(report_text: str) -> List[Dict[str, str]]:
    """Parse markdown AI report into structured sections.

    Skips vehicle identity headings (e.g., "MINI Cooper D Convertible (2011) — EA11 OSE")
    as these are redundant with cover page and vehicle summary.
    """
    sections = []
    if not report_text:
        return sections

    citation_urls = _extract_citation_urls(report_text)

    current_title = None
    current_lines: List[str] = []

    for line in report_text.split("\n"):
        if line.startswith("## "):
            if current_title and not _is_vehicle_identity_heading(current_title):
                sections.append({"title": current_title, "content": _md_to_html("\n".join(current_lines).strip(), citation_urls)})
            current_title = line.lstrip("# ").strip()
            current_lines = []
        else:
            current_lines.append(line)

    if current_title and not _is_vehicle_identity_heading(current_title):
        sections.append({"title": current_title, "content": _md_to_html("\n".join(current_lines).strip(), citation_urls)})

    return sections


def _is_vehicle_identity_heading(title: str) -> bool:
    """Check if title is a vehicle identity heading (e.g., 'MINI Cooper D Convertible (2011) — EA11 OSE')."""
    # Pattern: Make Model ... (Year) — Registration (with optional space)
    # Contains year in parens and registration after em-dash
    return bool(re.search(r'\(\d{4}\)\s*[—–-]\s*[A-Z0-9\s]{2,9}$', title))


def _extract_verdict(report_text: str) -> Optional[str]:
    """Extract BUY/NEGOTIATE/AVOID verdict from report text.

    Handles both '**AVOID**' (exact) and '**AVOID —...' (with trailing text).
    """
    if not report_text:
        return None
    # Match **VERDICT** or **VERDICT — ...** or **VERDICT: ...** at start of a line
    m = re.search(r"\*\*(AVOID|NEGOTIATE|BUY)[\s*\-—:]", report_text)
    if m:
        return m.group(1)
    # Fallback: bare word in first 500 chars
    snippet = report_text[:500].upper()
    for word in ("AVOID", "NEGOTIATE", "BUY"):
        if word in snippet:
            return word
    return None


def _build_checks_summary(check_data: Dict) -> List[Dict]:
    """Build pass/fail checklist items for the PDF At a Glance section."""
    items = []

    # Stolen
    stolen = check_data.get("stolen_check")
    if stolen:
        if stolen.get("stolen"):
            items.append({"status": "fail", "icon": "✗", "label": "Reported Stolen",
                          "detail": "Do not purchase — stolen marker on record"})
        else:
            items.append({"status": "pass", "icon": "✓", "label": "Not Stolen",
                          "detail": "Clear"})

    # Finance
    finance = check_data.get("finance_check")
    if finance:
        if finance.get("finance_outstanding"):
            count = finance.get("record_count", 1)
            items.append({"status": "fail", "icon": "✗", "label": "Finance Outstanding",
                          "detail": f"{count} active agreement{'s' if count != 1 else ''} — lender may repossess"})
        else:
            items.append({"status": "pass", "icon": "✓", "label": "No Finance Outstanding",
                          "detail": "Clear — safe to purchase"})

    # Write-off
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

    # Salvage
    salvage = check_data.get("salvage_check")
    if salvage:
        if salvage.get("salvage_found"):
            items.append({"status": "warn", "icon": "!", "label": "Salvage Records Found",
                          "detail": "Appears in salvage auction records"})
        else:
            items.append({"status": "pass", "icon": "✓", "label": "No Salvage Records",
                          "detail": "Clear"})

    # Clocking
    clocking = check_data.get("clocking_analysis") or {}
    if clocking.get("clocked"):
        items.append({"status": "fail", "icon": "✗", "label": "Mileage Discrepancy",
                      "detail": "Odometer tampering suspected"})
    else:
        items.append({"status": "pass", "icon": "✓", "label": "Mileage Verified",
                      "detail": "No clocking detected"})

    # MOT
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

    # ULEZ
    ulez = check_data.get("ulez_compliance") or {}
    if ulez.get("compliant") is False:
        charge = ulez.get("daily_charge", "charges apply")
        items.append({"status": "warn", "icon": "!", "label": "CAZ Non-Compliant",
                      "detail": f"{charge} in affected UK zones"})
    elif ulez.get("compliant") is True:
        items.append({"status": "pass", "icon": "✓", "label": "All Clean Air Zones Clear",
                      "detail": "Compliant with all UK zones"})

    return items


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

    # Extract data (shared fields — standard + EV)
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

    # EV-specific fields (present only for EV tier checks)
    battery_health = check_data.get("battery_health")
    range_estimate = check_data.get("range_estimate")
    range_scenarios = check_data.get("range_scenarios", [])
    charging_costs = check_data.get("charging_costs")
    ev_specs = check_data.get("ev_specs")
    lifespan_prediction = check_data.get("lifespan_prediction")

    # Verdict
    verdict = _extract_verdict(ai_report) if ai_report else None
    checks_summary = _build_checks_summary(check_data)
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

    # Report reference (EV prefix for electric vehicles)
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
        "verdict": verdict,
        "verdict_class": verdict_class,
        "checks_summary": checks_summary,
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
        # EV fields (template guards with {% if battery_health %} etc.)
        "battery_health": battery_health,
        "range_estimate": range_estimate,
        "range_scenarios": range_scenarios,
        "charging_costs": charging_costs,
        "ev_specs": ev_specs,
        "lifespan_prediction": lifespan_prediction,
    }

    html_content = template.render(**context)

    # Generate PDF
    pdf_bytes = HTML(string=html_content).write_pdf()
    logger.info(f"PDF generated for {check_data.get('registration', '?')} ({len(pdf_bytes)} bytes, ref: {report_ref})")
    return pdf_bytes
