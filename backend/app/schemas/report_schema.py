"""
Simplified flat JSON schema for AI-generated vehicle buyer reports.

This schema enforces only critical structure: all sections must be present,
recommendation must be BUY/AVOID. Everything else uses Dict[str, Any] for
flexibility. The renderer handles field-level validation defensively using .get().
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class VehicleReport(BaseModel):
    """
    Flat schema for AI-generated vehicle buyer report.
    Validates that all required sections are present.
    Field-level validation is left to the renderer.
    """

    # --- Metadata ---
    registration: str = Field(..., description="Vehicle registration plate")
    report_date: str = Field(..., description="DD Mmm YYYY")
    vehicle_summary: str = Field(..., description="e.g., '2011 MINI Diesel (1598cc)'")
    current_mileage: int = Field(..., description="Current odometer reading in miles")
    mot_valid_until: str = Field(..., description="MOT expiry date (DD Mmm YYYY)")

    # --- Section 1: Key Findings ---
    # Informational, not prescriptive. Vericar presents facts; buyer decides.
    key_findings: List[str] = Field(
        ...,
        min_length=3,
        max_length=5,
        description="3-5 factual observations from the data. Flat strings, no advice, no BUY/AVOID verdict."
    )

    mileage_assessment: Dict[str, Any] = Field(
        ...,
        description="Mileage analysis: total_mileage, annual_average, benchmark_fuel_type, benchmark_typical_miles_per_year, assessment, observation"
    )

    mot_summary: List[Dict[str, Any]] = Field(
        ...,
        min_items=6,
        description="6-row MOT summary table. Each row: {metric, detail, interpretation}"
    )

    mot_tests: List[Dict[str, Any]] = Field(
        ...,
        min_items=1,
        description="Full MOT test records, newest first. Each test: {test_date, result, mileage, defects}"
    )

    defect_patterns: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Recurring defect patterns. Each pattern: {category, flagged_count, flagged_dates, factual_summary, recommended_action}"
    )

    total_keepers: int = Field(..., description="Number of registered keepers")
    ownership_note: str = Field(
        ...,
        description="One sentence on keeper stability (factual, no judgment about maintenance quality)"
    )

    provenance: List[Dict[str, Any]] = Field(
        ...,
        min_items=4,
        description="Provenance checks: Finance, Stolen, Write-off, Salvage, etc. Each: {check, result, detail}"
    )

    # --- Section 2: Value Analysis ---
    valuations: Dict[str, Any] = Field(
        ...,
        description="Valuation channels. Keys: private_sale, dealer_forecourt, trade_in, part_exchange (values in pounds as int)"
    )

    valuation_context: str = Field(
        ...,
        description="Fair value assessment referencing specific defects, not condition score"
    )

    value_factors: List[Dict[str, Any]] = Field(
        ...,
        min_items=1,
        description="Value factors. Each: {factor, impact, details}"
    )

    depreciation: str = Field(
        ...,
        description="Depreciation trajectory summary (2-3 sentences)"
    )

    # --- Section 3: Risk Factors ---
    risk_matrix: List[Dict[str, Any]] = Field(
        ...,
        min_items=1,
        description="Risk assessment matrix. Each row: {category, level (HIGH/MEDIUM/LOW), finding}"
    )

    known_issues: List[Dict[str, Any]] = Field(
        ...,
        min_items=1,
        description="Known issues for this model/engine. Each: {priority (High/Medium/Low), issue, details}"
    )

    # --- New Sections (Optional) ---
    test_drive_checklist: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Vehicle-specific checks for test drive. Each: {area, check, what_to_look_for}"
    )

    running_costs: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Annual cost estimates: {fuel_annual, road_tax, insurance_estimate, servicing_annual, total_annual, notes}"
    )

    repair_budget: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Cost estimates for known defects. Each: {item, priority, estimated_cost_low, estimated_cost_high, notes}"
    )

    negotiation_guidance: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Negotiation strategy: {asking_price_context, suggested_opening, key_leverage_points (list of strings), walk_away_triggers (list of strings)}"
    )

    recalls: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Known recalls for this model/year. Each: {recall_ref, description, status, action_required}"
    )

    # --- Sources ---
    data_sources: Optional[List[Any]] = Field(
        default_factory=list,
        description="List of sources used (for citations in report)"
    )
