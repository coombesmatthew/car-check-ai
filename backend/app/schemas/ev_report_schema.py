"""Flat JSON schema for AI-generated EV buyer's reports (paid tier).

Mirrors `report_schema.VehicleReport` for the non-EV flow. Claude returns a
validated JSON object; the EV renderer converts it to markdown. Style lives in
the renderer, content lives in the schema — the prompt produces data only.

Used by both EV Health (£8.99) and EV Complete (£13.99). Complete tier fills
in the optional provenance / valuations / keeper_count fields; Health tier
leaves them empty.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


class EVReport(BaseModel):
    """Flat schema for an AI-generated EV buyer's report."""

    model_config = {"protected_namespaces": ()}

    # --- Metadata ---
    registration: str = Field(..., description="Vehicle registration plate")
    report_date: str = Field(..., description="DD Month YYYY")
    vehicle_summary: str = Field(
        ...,
        description="e.g. '2021 Tesla Model 3 | Pearl White | 42,180 miles'",
    )
    tier: str = Field(
        ...,
        description="'EV Health' or 'EV Complete'",
        pattern="^(EV Health|EV Complete)$",
    )

    # --- Section 1: Key Findings ---
    # Informational, not prescriptive. Vericar presents facts; buyer decides.
    key_findings: List[str] = Field(
        ...,
        min_length=3,
        max_length=5,
        description="3-5 factual observations from the data. No BUY/AVOID verdict, no advice.",
    )

    # --- Section 2: Battery Health ---
    battery_score: int = Field(..., ge=0, le=100, description="Battery health score 0-100")
    battery_grade: str = Field(..., description="A / B / C / D / F")
    battery_degradation_pct: float = Field(..., description="Estimated degradation %")
    battery_summary: str = Field(..., description="Prose paragraph explaining what the score means")
    battery_chemistry_note: Optional[str] = Field(
        default=None,
        description="One paragraph on battery chemistry (LFP vs NMC) and implications for buyer",
    )

    # --- Section 3: Range Reality Check ---
    range_official_wltp_miles: int = Field(..., description="Official WLTP range")
    range_realworld_miles: int = Field(..., description="Real-world estimate")
    range_retention_pct: float = Field(..., description="Range retention vs new %")
    range_scenarios: List[Dict[str, Any]] = Field(
        ...,
        min_length=3,
        description="Scenario table rows: {scenario, estimated_miles, temperature_c, driving_style}",
    )
    range_summary: str = Field(..., description="Prose explaining gap between WLTP and real-world, decision implications")

    # --- Section 4: Charging & Running Costs ---
    charging_ac_max_kw: Optional[float] = Field(default=None)
    charging_dc_max_kw: Optional[float] = Field(default=None)
    charging_home_hours: Optional[float] = Field(default=None, description="Full charge time on 7kW wallbox")
    charging_rapid_10_80_mins: Optional[int] = Field(default=None, description="10-80% DC rapid time")
    cost_per_mile_home_p: Optional[float] = Field(default=None)
    cost_per_mile_rapid_p: Optional[float] = Field(default=None)
    annual_cost_home_gbp: Optional[int] = Field(default=None)
    annual_cost_rapid_gbp: Optional[int] = Field(default=None)
    vs_petrol_saving_gbp: Optional[int] = Field(default=None)
    cost_summary: str = Field(..., description="Prose — running-cost implications for buyer")

    # --- Section 5: Ownership Forecast ---
    predicted_remaining_years: Optional[int] = Field(default=None)
    predicted_remaining_range_low: Optional[int] = Field(default=None)
    predicted_remaining_range_high: Optional[int] = Field(default=None)
    model_avg_final_miles: Optional[int] = Field(default=None)
    maintenance_items: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="EV maintenance items to budget: {item, note}",
    )
    ownership_summary: str = Field(..., description="Prose forecast")

    # --- Section 6 (EV Complete only): Provenance & Value ---
    provenance: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Provenance checks (Complete only): [{check, result, detail}]",
    )
    valuations: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Complete only: {private_sale, dealer_forecourt, trade_in, part_exchange}",
    )
    keeper_count: Optional[int] = Field(default=None, description="Number of registered keepers (Complete only)")
    valuation_context: Optional[str] = Field(default=None, description="Prose interpreting the valuation vs asking price")

    # --- Section 7: Negotiation ---
    negotiation_points: List[str] = Field(
        ...,
        min_length=2,
        max_length=5,
        description="Specific negotiation talking points based on data",
    )

    # --- Sources ---
    data_sources: Optional[List[Any]] = Field(default_factory=list)

    @field_validator("tier")
    @classmethod
    def tier_must_be_valid(cls, v: str) -> str:
        if v not in ("EV Health", "EV Complete"):
            raise ValueError(f"tier must be 'EV Health' or 'EV Complete', got: {v!r}")
        return v
