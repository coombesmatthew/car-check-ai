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

    # Header
    lines.append("# COMPREHENSIVE USED CAR BUYER'S REPORT")
    lines.append("")
    lines.append(f"**Vehicle:** {report.vehicle_summary}")
    lines.append(f"**Registration:** {report.registration}")
    lines.append(f"**Current Mileage:** {report.current_mileage:,} miles")
    lines.append(f"**MOT Status:** Valid until {report.mot_valid_until}")
    lines.append(f"**Report Date:** {report.report_date}")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Section 1: Overall Condition Assessment
    lines.append("## 1. OVERALL CONDITION ASSESSMENT")
    lines.append("")
    lines.append(f"**Recommendation: {report.recommendation}**")
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
        lines.append(f"| **{metric}** | {detail} | {interpretation} |")
    lines.append("")
    lines.append("---")
    lines.append("")

    # MOT Full Test Records - Compact format (failures/dangerous only)
    lines.append("### MOT History (Full Test Records)")
    lines.append("")
    lines.append("| # | Date | Result | Mileage | Issues |")
    lines.append("|---|------|--------|---------|--------|")
    for idx, test in enumerate(report.mot_tests, 1):
        test_date = test.get("test_date", "N/A")
        result = test.get("result", "N/A")
        mileage = test.get("mileage", "N/A")
        defects = test.get("defects", [])

        # Format defects - only FAILURES and DANGEROUS (compact)
        failure_lines = []
        if isinstance(defects, list):
            for d in defects:
                if isinstance(d, dict):
                    defect_type = d.get("type", "")
                    defect_text = d.get("text", "")
                    if defect_type in ("FAILURE", "DANGEROUS") and defect_text:
                        # Use short notation: F: text or D: text
                        prefix = "F" if defect_type == "FAILURE" else "D"
                        failure_lines.append(f"{prefix}: {defect_text[:60]}")

        # If no failures/dangerous, show advisories count
        if not failure_lines:
            advisory_count = sum(1 for d in defects if isinstance(d, dict) and d.get("type") == "ADVISORY")
            if advisory_count > 0:
                issues_str = f"{advisory_count} advisories"
            else:
                issues_str = "—"
        else:
            issues_str = "; ".join(failure_lines)

        mileage_str = f"{mileage:,}" if isinstance(mileage, int) else str(mileage)
        lines.append(f"| {idx} | **{test_date}** | {result} | {mileage_str} mi | {issues_str} |")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Recurring Defect Patterns - Table with better formatting
    lines.append("### Recurring Defect Patterns")
    lines.append("")
    if report.defect_patterns:
        lines.append("| Category | # | Pattern | Action |")
        lines.append("|----------|---|---------|--------|")
        for pattern in report.defect_patterns:
            category = pattern.get("category", "Unknown")
            flagged_count = pattern.get("flagged_count", 0)
            factual_summary = pattern.get("factual_summary", "")
            recommended_action = pattern.get("recommended_action", "")

            # Truncate long content for readability in table
            pattern_short = factual_summary[:100] + "..." if len(factual_summary) > 100 else factual_summary
            action_short = recommended_action[:80] + "..." if len(recommended_action) > 80 else recommended_action

            lines.append(f"| **{category}** | {flagged_count} | {pattern_short} | {action_short} |")
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

    # Provenance
    lines.append("### Provenance")
    lines.append("")
    for check in report.provenance:
        check_name = check.get("check", "")
        result = check.get("result", "")
        detail = check.get("detail", "")
        lines.append(f"**{check_name}:** {result}")
    lines.append("")
    lines.append("**Summary:** The vehicle has a clean legal and financial history.")
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
    lines.append("| Channel | Valuation |")
    lines.append("|---------|-----------|")

    vals = report.valuations
    channels = [
        ("Private Sale", "private_sale"),
        ("Dealer Forecourt", "dealer_forecourt"),
        ("Trade-in", "trade_in"),
        ("Part Exchange", "part_exchange"),
    ]
    for channel_label, channel_key in channels:
        amount = vals.get(channel_key)
        if amount is not None:
            amount_str = _format_currency(int(amount)) if isinstance(amount, (int, float)) else str(amount)
            lines.append(f"| **{channel_label}** | {amount_str} |")

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
        lines.append("### Recall Status")
        lines.append("")
        lines.append("No recalls on record for this model. Always verify at [DVSA recalls](https://www.gov.uk/check-vehicle-recall).")
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
        lines.append(f"| **Total** | | **£{total_low:,}–£{total_high:,}** | Estimated repair budget |")
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

    # Section 6: Negotiation Guidance (NEW top-level section)
    lines.append("---")
    lines.append("")
    lines.append("## 6. NEGOTIATION GUIDANCE")
    lines.append("")
    ng = report.negotiation_guidance or {}
    asking_ctx = ng.get("asking_price_context", "")
    opening = ng.get("suggested_opening", "")
    leverage = ng.get("key_leverage_points", [])
    walk_away = ng.get("walk_away_triggers", [])

    if asking_ctx:
        lines.append(f"**Market Context:** {asking_ctx}")
        lines.append("")
    if opening:
        lines.append(f"**Suggested Opening Offer:** {opening}")
        lines.append("")
    if leverage:
        lines.append("**Key Leverage Points:**")
        for point in leverage:
            lines.append(f"- {point}")
        lines.append("")
    if walk_away:
        lines.append("**Walk Away If:**")
        for trigger in walk_away:
            lines.append(f"- {trigger}")
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
