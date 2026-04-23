"""
Renders flat structured vehicle report JSON to markdown.

Takes VehicleReport JSON (from Claude) and converts to markdown
suitable for PDF generation. Uses .get() defensively on all dict fields.
"""

from typing import List, Dict, Any
from app.schemas.report_schema import VehicleReport


def _format_currency(pounds: int) -> str:
    """Format pounds as string with thousands separator."""
    return f"£{pounds:,}"


def render_report_to_markdown(report: VehicleReport) -> str:
    """Convert VehicleReport JSON to markdown string."""
    lines = []

    # === SECTION 1: KEY FINDINGS ===
    # Informational — we present facts, buyer decides. No verdict.
    lines.append("## 1. KEY FINDINGS")
    lines.append("")
    for finding in report.key_findings:
        lines.append(f"- {finding}")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Mileage Assessment
    lines.append("### Mileage Assessment")
    lines.append("")
    ma = report.mileage_assessment
    total_mileage = ma.get("total_mileage", "N/A")
    annual_average = ma.get("annual_average", "N/A")
    benchmark_fuel_type = ma.get("benchmark_fuel_type", "N/A")
    benchmark_miles = ma.get("benchmark_typical_miles_per_year", "N/A")
    assessment = ma.get("assessment", "N/A")
    observation = ma.get("observation", "N/A")

    lines.append(f"**Total Mileage:** {total_mileage:,} miles" if isinstance(total_mileage, int) else f"**Total Mileage:** {total_mileage}")
    lines.append(f"**Annual Average:** ~{annual_average:,} miles/year" if isinstance(annual_average, int) else f"**Annual Average:** {annual_average}")
    lines.append("")
    lines.append("**Benchmark Comparison:**")
    lines.append(f"- UK average for {str(benchmark_fuel_type).lower()} cars: {benchmark_miles} miles/year")
    lines.append("")
    lines.append(f"This vehicle's mileage is **{assessment}** for its age and fuel type.")
    lines.append("")
    lines.append(f"**Observation:** {observation}")
    lines.append("")
    lines.append("---")
    lines.append("")


    # MOT History Analysis
    lines.append("### MOT History Analysis")
    lines.append("")
    lines.append("| Metric | Detail | Interpretation |")
    lines.append("|--------|--------|-----------------|")
    for row in report.mot_summary:
        metric = row.get("metric", "")
        detail = row.get("detail", "")
        interpretation = row.get("interpretation", "")
        lines.append(f"| {metric} | {detail} | {interpretation} |")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Recurring Defect Patterns - Table with better formatting
    lines.append("### Recurring Defect Patterns")
    lines.append("")
    if report.defect_patterns:
        lines.append("| Category | Tests | First/Last Seen | Action |")
        lines.append("|----------|-------|-----------------|--------|")
        for pattern in report.defect_patterns:
            category = pattern.get("category", "Unknown")
            flagged_count = pattern.get("flagged_count", 0)
            flagged_dates = pattern.get("flagged_dates", [])
            recommended_action = pattern.get("recommended_action", "")

            # Build First/Last Seen column
            if flagged_dates:
                first_seen = flagged_dates[0]
                last_seen = flagged_dates[-1]
                seen_range = f"{first_seen} → {last_seen}" if first_seen != last_seen else first_seen
            else:
                seen_range = "—"

            # Truncate action for readability
            action_short = recommended_action[:80] + "..." if len(recommended_action) > 80 else recommended_action

            lines.append(f"| **{category}** | {flagged_count} | {seen_range} | {action_short} |")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Test Drive Checklist (NEW)
    if report.test_drive_checklist:
        lines.append("### Test Drive Checklist")
        lines.append("")
        lines.append("| Area | Check | What to Look For |")
        lines.append("|------|-------|-----------------|")
        for item in report.test_drive_checklist:
            area = item.get("area", "")
            check = item.get("check", "")
            what = item.get("what_to_look_for", "")
            lines.append(f"| **{area}** | {check} | {what} |")
        lines.append("")
        lines.append("---")
        lines.append("")

    # Ownership History
    lines.append("### Ownership History")
    lines.append("")
    lines.append(f"**Total Keepers:** {report.total_keepers}")
    lines.append("")
    lines.append(f"**Assessment:** {report.ownership_note}")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Provenance (converted to table for clarity)
    lines.append("### Provenance")
    lines.append("")
    lines.append("| Check | Status | Details |")
    lines.append("|-------|--------|---------|")
    for check in report.provenance:
        check_name = check.get("check", "")
        result = check.get("result", "")
        detail = check.get("detail", "")
        status_icon = "✅" if "Clear" in result or "No" in result else "⚠️" if "Outstanding" in result or "Reported" in result else "❌"
        lines.append(f"| {check_name} | {status_icon} {result} | {detail} |")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Section 2: Value Analysis (page break before)
    lines.append("---")
    lines.append("")
    lines.append("## 2. VALUE ANALYSIS")
    lines.append("")
    lines.append("### Market Valuation Summary")
    lines.append("")
    # Output as HTML grid instead of markdown table for better styling
    vals = report.valuations
    ps = vals.get("private_sale", "—")
    dc = vals.get("dealer_forecourt", "—")
    ti = vals.get("trade_in", "—")
    pe = vals.get("part_exchange", "—")

    ps_str = _format_currency(int(ps)) if isinstance(ps, (int, float)) else str(ps)
    dc_str = _format_currency(int(dc)) if isinstance(dc, (int, float)) else str(dc)
    ti_str = _format_currency(int(ti)) if isinstance(ti, (int, float)) else str(ti)
    pe_str = _format_currency(int(pe)) if isinstance(pe, (int, float)) else str(pe)

    lines.append('<div class="valuation-grid">')
    lines.append(f'<div class="val-cell val-primary"><div class="val-label">Private Sale</div><div class="val-amount">{ps_str}</div></div>')
    lines.append(f'<div class="val-cell val-primary"><div class="val-label">Dealer Forecourt</div><div class="val-amount">{dc_str}</div></div>')
    lines.append(f'<div class="val-cell"><div class="val-label">Trade-in</div><div class="val-amount">{ti_str}</div></div>')
    lines.append(f'<div class="val-cell"><div class="val-label">Part Exchange</div><div class="val-amount">{pe_str}</div></div>')
    lines.append('</div>')
    lines.append("")

    valuation_basis = vals.get("valuation_basis", "Market data (mileage-adjusted)")
    lines.append(f"*Valuation basis: {valuation_basis}*")
    lines.append("")

    lines.append("### Context & Interpretation")
    lines.append("")
    lines.append(report.valuation_context)
    lines.append("")

    lines.append("### Value Influencing Factors")
    lines.append("")
    lines.append("| Factor | Impact | Details |")
    lines.append("|--------|--------|---------|")
    for factor in report.value_factors:
        factor_name = factor.get("factor", "")
        impact = factor.get("impact", "")
        details = factor.get("details", "")
        lines.append(f"| **{factor_name}** | {impact} | {details} |")
    lines.append("")

    lines.append("### Depreciation Trajectory")
    lines.append("")
    lines.append(report.depreciation)
    lines.append("")
    lines.append("---")
    lines.append("")

    # Section 3: Risk Factors (page break before)
    lines.append("---")
    lines.append("")
    lines.append("## 3. RISK FACTORS")
    lines.append("")
    lines.append("### Risk Matrix")
    lines.append("")
    if report.risk_matrix:
        lines.append("| Category | Level | Finding |")
        lines.append("|----------|-------|---------|")
        for row in report.risk_matrix:
            category = row.get("category", "")
            level = row.get("level", "")
            finding = row.get("finding", "")
            lines.append(f"| **{category}** | **{level}** | {finding} |")
    lines.append("")

    lines.append("### Known Issues for This Model")
    lines.append("")
    if report.known_issues:
        lines.append("| Priority | Issue | Details |")
        lines.append("|----------|-------|---------|")
        for issue in report.known_issues:
            priority = issue.get("priority", "")
            issue_name = issue.get("issue", "")
            details = issue.get("details", "")
            lines.append(f"| **{priority}** | {issue_name} | {details} |")
    lines.append("")

    # Recall Status (NEW — closes Section 3)
    if report.recalls:
        lines.append("### Recall Status")
        lines.append("")
        lines.append("| Ref | Description | Status | Action |")
        lines.append("|-----|-------------|--------|--------|")
        for r in report.recalls:
            ref = r.get("recall_ref", "—")
            desc = r.get("description", "")
            status = r.get("status", "")
            action = r.get("action_required", "")
            lines.append(f"| {ref} | {desc} | {status} | {action} |")
        lines.append("")
    else:
        from datetime import date as _date
        verification_date = _date.today().strftime("%d %B %Y")
        lines.append("### Recall Status")
        lines.append("")
        lines.append(f"No open recalls on record for this model. Verified via DVSA database as of {verification_date}. Always verify at [DVSA recalls](https://www.gov.uk/check-vehicle-recall).")
        lines.append("")
    lines.append("---")
    lines.append("")

    # Section 4: Repair Budget (NEW top-level section)
    lines.append("---")
    lines.append("")
    lines.append("## 4. REPAIR BUDGET")
    lines.append("")
    if report.repair_budget:
        lines.append("| Item | Priority | Est. Cost | Notes |")
        lines.append("|------|----------|-----------|--------|")
        total_low = 0
        total_high = 0
        for item in report.repair_budget:
            name = item.get("item", "")
            priority = item.get("priority", "")
            low = item.get("estimated_cost_low", 0)
            high = item.get("estimated_cost_high", 0)
            notes = item.get("notes", "")
            total_low += low if isinstance(low, (int, float)) else 0
            total_high += high if isinstance(high, (int, float)) else 0
            cost_str = f"£{low:,}–£{high:,}" if isinstance(low, (int, float)) and low > 0 else "—"
            lines.append(f"| {name} | {priority} | {cost_str} | {notes} |")
        # Total row with proper HTML formatting to ensure correct alignment
        lines.append(f"| Total | | £{total_low:,}–£{total_high:,} | Estimated repair budget |")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Section 5: Running Costs (NEW top-level section)
    lines.append("---")
    lines.append("")
    lines.append("## 5. RUNNING COSTS")
    lines.append("")
    rc = report.running_costs or {}
    lines.append("| Category | Annual Cost |")
    lines.append("|----------|------------|")
    cost_map = [
        ("Fuel", "fuel_annual"),
        ("Road Tax (VED)", "road_tax"),
        ("Insurance (estimate)", "insurance_estimate"),
        ("Servicing & Maintenance", "servicing_annual"),
    ]
    for label, key in cost_map:
        val = rc.get(key)
        if val is not None:
            lines.append(f"| {label} | £{int(val):,} |")
    total = rc.get("total_annual")
    if total:
        lines.append(f"| **Total (estimated)** | **£{int(total):,}** |")
    notes = rc.get("notes", "")
    if notes:
        lines.append("")
        lines.append(f"*{notes}*")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Section 6: Points To Check — informational, not prescriptive.
    # Presents data-backed items for the buyer to verify in person; we do
    # not tell them what offer to make or when to walk away.
    lines.append("---")
    lines.append("")
    lines.append("## 6. POINTS TO CHECK")
    lines.append("")
    ng = report.negotiation_guidance or {}
    asking_ctx = ng.get("asking_price_context", "")
    leverage = ng.get("key_leverage_points", [])
    walk_away = ng.get("walk_away_triggers", [])

    if asking_ctx:
        lines.append(f"**Market context:** {asking_ctx}")
        lines.append("")
    combined = list(leverage or []) + list(walk_away or [])
    if combined:
        lines.append("**Items worth verifying before purchase:**")
        for item in combined:
            lines.append(f"- {item}")
        lines.append("")
    lines.append("---")
    lines.append("")

    # Data Sources (page break before)
    lines.append("---")
    lines.append("")
    if report.data_sources:
        lines.append("## Data Sources")
        lines.append("")
        lines.append("This report was compiled using the following data sources:\n")
        for i, source in enumerate(report.data_sources, 1):
            # Handle both strings and dict objects
            if isinstance(source, str):
                lines.append(f"{i}. {source}")
            elif isinstance(source, dict):
                name = source.get("name", "Unknown")
                lines.append(f"{i}. {name}")
            else:
                lines.append(f"{i}. {str(source)}")
        lines.append("")

    lines.append(
        "\nDisclaimer: This report is generated by VeriCar using data from DVLA, DVSA, and third-party providers. "
        "The analysis is advisory only. Always arrange a professional vehicle inspection before purchase."
    )

    return "\n".join(lines)
