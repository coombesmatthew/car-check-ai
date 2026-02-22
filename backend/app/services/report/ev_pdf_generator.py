"""EV-specific PDF report generator.

Generates a green-branded PDF for EV Health Check reports.
Reuses the same WeasyPrint + Jinja2 approach as the car check PDF.
"""

import re
import uuid
from datetime import datetime
from typing import Dict, List, Optional

from app.core.logging import logger


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
            current_title = line.lstrip("# ").strip()
            current_lines = []
        else:
            current_lines.append(line)

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


def extract_ev_verdict(report_text: Optional[str]) -> Optional[str]:
    """Extract BUY/NEGOTIATE/AVOID verdict from the AI report."""
    if not report_text:
        return None
    for keyword in ("BUY", "NEGOTIATE", "AVOID"):
        if keyword in report_text.upper():
            return keyword
    return None


def generate_ev_pdf(check_data: Dict, ai_report: Optional[str] = None) -> bytes:
    """Generate an EV Health Check PDF report.

    Uses an inline HTML template with green EV branding.
    Returns raw PDF bytes.
    """
    try:
        from weasyprint import HTML
    except ImportError:
        logger.warning("WeasyPrint not installed, generating placeholder PDF")
        return _placeholder_pdf(check_data, ai_report)

    report_ref = f"EV-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
    ai_sections = _parse_ai_sections(ai_report) if ai_report else []
    verdict = extract_ev_verdict(ai_report)

    vehicle = check_data.get("vehicle") or {}
    battery_health = check_data.get("battery_health") or {}
    range_estimate = check_data.get("range_estimate") or {}
    ev_specs = check_data.get("ev_specs") or {}
    charging_costs = check_data.get("charging_costs") or {}

    html_content = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
           color: #1e293b; margin: 0; padding: 40px; font-size: 11px; line-height: 1.5; }}
    .header {{ background: linear-gradient(135deg, #059669, #10b981);
               color: white; padding: 24px; border-radius: 8px; margin-bottom: 24px; }}
    .header h1 {{ margin: 0; font-size: 22px; }}
    .header p {{ margin: 4px 0 0; opacity: 0.9; font-size: 12px; }}
    .meta {{ display: flex; gap: 32px; margin-top: 12px; font-size: 10px; opacity: 0.85; }}
    .badge {{ display: inline-block; padding: 4px 12px; border-radius: 20px;
              font-weight: 700; font-size: 11px; }}
    .badge-buy {{ background: #d1fae5; color: #065f46; }}
    .badge-negotiate {{ background: #fef3c7; color: #92400e; }}
    .badge-avoid {{ background: #fee2e2; color: #991b1b; }}
    .card {{ border: 1px solid #e2e8f0; border-radius: 8px; padding: 16px;
             margin-bottom: 16px; page-break-inside: avoid; }}
    .card h2 {{ font-size: 14px; margin: 0 0 12px; color: #059669; }}
    .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }}
    .kv {{ display: flex; justify-content: space-between; padding: 4px 0;
           border-bottom: 1px solid #f1f5f9; }}
    .kv .label {{ color: #64748b; }}
    .kv .value {{ font-weight: 600; }}
    .section {{ margin-bottom: 20px; page-break-inside: avoid; }}
    .section h2 {{ font-size: 14px; color: #059669; border-bottom: 2px solid #10b981;
                   padding-bottom: 4px; margin-bottom: 8px; }}
    .section p {{ margin: 6px 0; }}
    .section ul {{ margin: 6px 0; padding-left: 20px; }}
    .section li {{ margin: 3px 0; }}
    .footer {{ text-align: center; color: #94a3b8; font-size: 9px;
               margin-top: 32px; padding-top: 16px; border-top: 1px solid #e2e8f0; }}
</style>
</head>
<body>
    <div class="header">
        <h1>VeriCar EV Health Check</h1>
        <p>{vehicle.get('make', '')} — {vehicle.get('registration', check_data.get('registration', ''))}
           — {vehicle.get('year_of_manufacture', '')}</p>
        <div class="meta">
            <span>Ref: {report_ref}</span>
            <span>Generated: {datetime.utcnow().strftime('%d %B %Y')}</span>
            {'<span class="badge badge-' + verdict.lower() + '">' + verdict + '</span>' if verdict else ''}
        </div>
    </div>

    <div class="card">
        <h2>Battery Health</h2>
        <div class="grid">
            <div class="kv"><span class="label">Health Score</span>
                <span class="value">{battery_health.get('score', 'N/A')}/100 ({battery_health.get('grade', 'N/A')})</span></div>
            <div class="kv"><span class="label">Degradation</span>
                <span class="value">{battery_health.get('degradation_estimate_pct', 'N/A')}%</span></div>
            <div class="kv"><span class="label">Real-World Range</span>
                <span class="value">{range_estimate.get('estimated_range_miles', 'N/A')} miles</span></div>
            <div class="kv"><span class="label">Official Range</span>
                <span class="value">{range_estimate.get('official_range_miles', 'N/A')} miles</span></div>
        </div>
    </div>

    <div class="card">
        <h2>Specifications</h2>
        <div class="grid">
            <div class="kv"><span class="label">Battery Capacity</span>
                <span class="value">{ev_specs.get('battery_capacity_kwh', 'N/A')} kWh</span></div>
            <div class="kv"><span class="label">Usable Capacity</span>
                <span class="value">{ev_specs.get('usable_capacity_kwh', 'N/A')} kWh</span></div>
            <div class="kv"><span class="label">Max DC Charge</span>
                <span class="value">{ev_specs.get('max_dc_charge_kw', 'N/A')} kW</span></div>
            <div class="kv"><span class="label">Home Charge (7kW)</span>
                <span class="value">{ev_specs.get('charge_time_home_hours', 'N/A')} hours</span></div>
            <div class="kv"><span class="label">Rapid 10-80%</span>
                <span class="value">{ev_specs.get('charge_time_rapid_mins', 'N/A')} mins</span></div>
            <div class="kv"><span class="label">Consumption</span>
                <span class="value">{ev_specs.get('energy_consumption_kwh_per_mile', 'N/A')} kWh/mile</span></div>
        </div>
    </div>

    <div class="card">
        <h2>Charging Costs (10,000 miles/year)</h2>
        <div class="grid">
            <div class="kv"><span class="label">Home Annual Cost</span>
                <span class="value">£{charging_costs.get('annual_cost_estimate_home', 'N/A')}</span></div>
            <div class="kv"><span class="label">Rapid Annual Cost</span>
                <span class="value">£{charging_costs.get('annual_cost_estimate_rapid', 'N/A')}</span></div>
            <div class="kv"><span class="label">vs Petrol Saving</span>
                <span class="value">£{charging_costs.get('vs_petrol_annual_saving', 'N/A')}/year</span></div>
            <div class="kv"><span class="label">Cost Per Mile (Home)</span>
                <span class="value">{charging_costs.get('cost_per_mile_home', 'N/A')}p</span></div>
        </div>
    </div>

    {''.join(f'<div class="section"><h2>{s["title"]}</h2>{s["content"]}</div>' for s in ai_sections)}

    <div class="footer">
        <p>VeriCar EV Health Check — {report_ref} — Generated {datetime.utcnow().strftime('%d/%m/%Y %H:%M')} UTC</p>
        <p>Data sources: DVLA VES, DVSA MOT, ClearWatt, EV Database, AutoPredict</p>
        <p>This report is for informational purposes only. Always arrange a physical inspection before purchase.</p>
    </div>
</body>
</html>"""

    try:
        pdf_bytes = HTML(string=html_content).write_pdf()
        logger.info(f"EV PDF generated for {check_data.get('registration', '')} ({len(pdf_bytes)} bytes)")
        return pdf_bytes
    except Exception as e:
        logger.error(f"EV PDF generation failed: {e}")
        return _placeholder_pdf(check_data, ai_report)


def _placeholder_pdf(check_data: Dict, ai_report: Optional[str] = None) -> bytes:
    """Generate a minimal text-based PDF when WeasyPrint is unavailable."""
    content = f"VeriCar EV Health Check — {check_data.get('registration', 'Unknown')}\n\n"
    if ai_report:
        content += ai_report
    return content.encode("utf-8")
