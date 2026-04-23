"""Render EV buyer's report JSON to markdown.

Owns ALL formatting decisions for paid EV reports — table structure, section
headers, bullet layouts, currency/unit formatting. The prompt produces data
only (an EVReport JSON object); this file decides how it reads on the page.

Mirrors report_renderer.py (non-EV) so both tiers feel identical in style.
"""

from __future__ import annotations

from typing import Any, Dict, List

from app.schemas.ev_report_schema import EVReport


def _currency(pounds: Any) -> str:
    if isinstance(pounds, (int, float)) and pounds > 0:
        return f"£{int(pounds):,}"
    return "—"


def _pence(p: Any) -> str:
    if isinstance(p, (int, float)):
        return f"{p:.1f}p"
    return "—"


def _optional_int(v: Any) -> str:
    return f"{int(v):,}" if isinstance(v, (int, float)) else "—"


def render_ev_report_to_markdown(report: EVReport) -> str:
    lines: List[str] = []

    # --- Header ---
    lines.append(f"# VeriCar {report.tier} Check — {report.registration}")
    lines.append(f"### {report.vehicle_summary}")
    lines.append(f"*Report generated: {report.report_date} | Tier: {report.tier}*")
    lines.append("")
    lines.append("---")
    lines.append("")

    # --- Section 1: Key Findings ---
    # Informational — we present facts, buyer decides. No verdict.
    lines.append("## 1. KEY FINDINGS")
    lines.append("")
    for finding in report.key_findings:
        lines.append(f"- {finding}")
    lines.append("")
    lines.append("---")
    lines.append("")

    # --- Section 2: Battery Health ---
    lines.append("## 2. BATTERY HEALTH")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("|---|---|")
    lines.append(f"| Score | **{report.battery_score}/100** (Grade {report.battery_grade}) |")
    lines.append(f"| Degradation | {report.battery_degradation_pct:.1f}% |")
    lines.append(f"| Capacity retained | {100 - report.battery_degradation_pct:.1f}% |")
    lines.append("")
    lines.append(report.battery_summary)
    lines.append("")
    if report.battery_chemistry_note:
        lines.append(report.battery_chemistry_note)
        lines.append("")
    lines.append("---")
    lines.append("")

    # --- Section 3: Range Reality Check ---
    lines.append("## 3. RANGE REALITY CHECK")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("|---|---|")
    lines.append(f"| Official WLTP | {report.range_official_wltp_miles} miles |")
    lines.append(f"| Real-world estimate | **{report.range_realworld_miles} miles** |")
    lines.append(f"| Range retention | {report.range_retention_pct:.1f}% |")
    lines.append("")
    lines.append("### Range by Scenario")
    lines.append("")
    lines.append("| Scenario | Estimated Range | Temperature | Driving Style |")
    lines.append("|---|---|---|---|")
    for s in report.range_scenarios:
        scenario = s.get("scenario", "—")
        miles = s.get("estimated_miles", "—")
        miles_str = f"{miles} miles" if isinstance(miles, (int, float)) else str(miles)
        temp = s.get("temperature_c", "—")
        temp_str = f"{temp}°C" if isinstance(temp, (int, float)) else str(temp)
        style = s.get("driving_style", "—")
        lines.append(f"| {scenario} | {miles_str} | {temp_str} | {style} |")
    lines.append("")
    lines.append(report.range_summary)
    lines.append("")
    lines.append("---")
    lines.append("")

    # --- Section 4: Charging & Running Costs ---
    lines.append("## 4. CHARGING & RUNNING COSTS")
    lines.append("")
    lines.append("### Charging Specifications")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("|---|---|")
    if report.charging_ac_max_kw is not None:
        lines.append(f"| Home AC max | {report.charging_ac_max_kw:g} kW |")
    if report.charging_dc_max_kw is not None:
        lines.append(f"| Public DC max | {report.charging_dc_max_kw:g} kW |")
    if report.charging_home_hours is not None:
        lines.append(f"| Full charge on 7 kW wallbox | {report.charging_home_hours:.1f} hours |")
    if report.charging_rapid_10_80_mins is not None:
        lines.append(f"| Rapid 10–80% | {report.charging_rapid_10_80_mins} minutes |")
    lines.append("")
    lines.append("### Cost Per Mile")
    lines.append("")
    lines.append("| Charging Method | Cost Per Mile |")
    lines.append("|---|---|")
    lines.append(f"| Home (7 kW wallbox) | {_pence(report.cost_per_mile_home_p)} |")
    lines.append(f"| Public rapid DC | {_pence(report.cost_per_mile_rapid_p)} |")
    lines.append("")
    lines.append("### Annual Running Cost at 10,000 Miles")
    lines.append("")
    lines.append("| Scenario | Annual Cost |")
    lines.append("|---|---|")
    lines.append(f"| Charging entirely at home | {_currency(report.annual_cost_home_gbp)} |")
    lines.append(f"| Charging entirely on rapid public chargers | {_currency(report.annual_cost_rapid_gbp)} |")
    if report.vs_petrol_saving_gbp:
        lines.append(f"| Estimated saving vs equivalent petrol car | {_currency(report.vs_petrol_saving_gbp)}/year |")
    lines.append("")
    lines.append(report.cost_summary)
    lines.append("")
    lines.append("---")
    lines.append("")

    # --- Section 5: Ownership Forecast ---
    lines.append("## 5. OWNERSHIP FORECAST")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("|---|---|")
    if report.predicted_remaining_years is not None:
        rng = ""
        if report.predicted_remaining_range_low and report.predicted_remaining_range_high:
            rng = f" (range {report.predicted_remaining_range_low}–{report.predicted_remaining_range_high} years)"
        lines.append(f"| Predicted remaining lifespan | {report.predicted_remaining_years} years{rng} |")
    if report.model_avg_final_miles is not None:
        lines.append(f"| Model average final mileage | {_optional_int(report.model_avg_final_miles)} miles |")
    lines.append("")
    if report.maintenance_items:
        lines.append("**Maintenance items to budget:**")
        lines.append("")
        for item in report.maintenance_items:
            name = item.get("item", "—")
            note = item.get("note", "")
            lines.append(f"- **{name}:** {note}")
        lines.append("")
    lines.append(report.ownership_summary)
    lines.append("")
    lines.append("---")
    lines.append("")

    # --- Section 6 (EV Complete only): Provenance & Valuation ---
    if report.tier == "EV Complete":
        lines.append("## 6. PROVENANCE & VALUATION")
        lines.append("")
        if report.provenance:
            lines.append("### Provenance Checks")
            lines.append("")
            lines.append("| Check | Result | Details |")
            lines.append("|---|---|---|")
            for check in report.provenance:
                name = check.get("check", "")
                result = check.get("result", "")
                detail = check.get("detail", "")
                icon = "✅" if "Clear" in result or "No" in result else "⚠️" if "Outstanding" in result or "Reported" in result else "❌"
                lines.append(f"| {name} | {icon} {result} | {detail} |")
            lines.append("")
        if report.keeper_count is not None:
            lines.append(f"**Registered keepers:** {report.keeper_count}")
            lines.append("")
        if report.valuations:
            lines.append("### Market Valuation")
            lines.append("")
            lines.append("| Channel | Value |")
            lines.append("|---|---|")
            for key, label in [
                ("private_sale", "Private Sale"),
                ("dealer_forecourt", "Dealer Forecourt"),
                ("trade_in", "Trade-in"),
                ("part_exchange", "Part Exchange"),
            ]:
                lines.append(f"| {label} | {_currency(report.valuations.get(key))} |")
            lines.append("")
        if report.valuation_context:
            lines.append(report.valuation_context)
            lines.append("")
        lines.append("---")
        lines.append("")

    # --- Section 7: Negotiation Points ---
    section_num = 7 if report.tier == "EV Complete" else 6
    lines.append(f"## {section_num}. NEGOTIATION POINTS")
    lines.append("")
    for point in report.negotiation_points:
        lines.append(f"- {point}")
    lines.append("")
    lines.append("---")
    lines.append("")

    # --- Data Sources ---
    if report.data_sources:
        lines.append("## Data Sources")
        lines.append("")
        for i, source in enumerate(report.data_sources, 1):
            if isinstance(source, str):
                lines.append(f"{i}. {source}")
            elif isinstance(source, dict):
                lines.append(f"{i}. {source.get('name', 'Unknown')}")
            else:
                lines.append(f"{i}. {source}")
        lines.append("")

    lines.append(
        "\nDisclaimer: This report is generated by VeriCar using data from DVLA, DVSA, and third-party EV telemetry providers. "
        "The analysis is advisory only. Always arrange a professional vehicle inspection before purchase."
    )

    return "\n".join(lines)
