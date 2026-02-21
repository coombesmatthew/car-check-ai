"""Pydantic schemas for EV Health Check product."""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
import re


class EVCheckRequest(BaseModel):
    """Request schema for an EV check."""
    registration: str = Field(
        ...,
        min_length=2,
        max_length=8,
        description="UK vehicle registration number",
        examples=["AB12CDE"],
    )

    @field_validator("registration")
    @classmethod
    def clean_registration(cls, v: str) -> str:
        cleaned = re.sub(r"[^A-Za-z0-9]", "", v).upper()
        if len(cleaned) < 2 or len(cleaned) > 8:
            raise ValueError("Invalid registration format")
        return cleaned


class EVCheckoutRequest(BaseModel):
    """Request for EV Stripe checkout."""
    registration: str
    email: str


class RangeEstimate(BaseModel):
    """ClearWatt real-world range estimate — compares range when new vs now."""
    # Range now (at current age/mileage)
    estimated_range_miles: Optional[int] = None  # midpoint of min/max now
    min_range_now_miles: Optional[int] = None
    max_range_now_miles: Optional[int] = None
    # Range when new (benchmark)
    min_range_new_miles: Optional[int] = None
    max_range_new_miles: Optional[int] = None
    # Official specs
    official_range_miles: Optional[int] = None  # WLTP combined
    # Calculated retention
    range_retention_pct: Optional[float] = None
    # Battery warranty
    warranty_miles_remaining: Optional[int] = None
    warranty_months_remaining: Optional[int] = None
    # Battery health test (if available)
    battery_test_available: bool = False
    battery_test_date: Optional[str] = None
    battery_test_grade: Optional[str] = None  # e.g. "A+"
    # Vehicle info from ClearWatt
    battery_capacity_kwh: Optional[float] = None
    usable_battery_capacity_kwh: Optional[float] = None
    data_source: str = "ClearWatt"


class RangeScenario(BaseModel):
    """Range estimate for a specific driving scenario (from EV Database)."""
    scenario: str  # e.g. "Highway Cold", "City Mild", "Combined Warm"
    temperature_c: Optional[int] = None
    estimated_miles: Optional[int] = None
    driving_style: Optional[str] = None  # "highway", "combined", "city"


class EVSpecs(BaseModel):
    """EV Database battery, charging, and vehicle specifications."""
    # Battery
    battery_capacity_kwh: Optional[float] = None
    usable_capacity_kwh: Optional[float] = None
    battery_type: Optional[str] = None  # e.g. "Lithium-ion"
    battery_chemistry: Optional[str] = None  # e.g. "NCM622"
    battery_architecture: Optional[str] = None  # e.g. "400 V"
    battery_weight_kg: Optional[int] = None
    battery_warranty_years: Optional[int] = None
    battery_warranty_miles: Optional[int] = None
    # Charging
    charge_port: Optional[str] = None  # AC port type
    fast_charge_port: Optional[str] = None  # DC port type e.g. "CCS"
    max_dc_charge_kw: Optional[int] = None
    avg_dc_charge_kw: Optional[int] = None
    max_ac_charge_kw: Optional[float] = None
    charge_time_home_mins: Optional[int] = None  # 0-100% on standard charger
    charge_time_rapid_mins: Optional[int] = None  # 10-80% DC fast
    rapid_charge_speed_mph: Optional[int] = None  # miles added per hour
    # Efficiency
    energy_consumption_wh_per_mile: Optional[float] = None
    energy_consumption_mi_per_kwh: Optional[float] = None
    # Range (real-world from EV Database)
    real_range_miles: Optional[int] = None  # EVDB real-world combined
    # Performance
    drivetrain: Optional[str] = None
    motor_power_kw: Optional[int] = None
    motor_power_bhp: Optional[int] = None
    top_speed_mph: Optional[int] = None
    zero_to_sixty_secs: Optional[float] = None
    # Dimensions
    kerb_weight_kg: Optional[int] = None
    boot_capacity_litres: Optional[int] = None
    boot_capacity_max_litres: Optional[int] = None
    frunk_litres: Optional[int] = None
    # Towing
    max_towing_weight_kg: Optional[int] = None
    data_source: str = "EV Database"


class LifespanPrediction(BaseModel):
    """AutoPredict vehicle lifespan prediction."""
    model_config = {"protected_namespaces": ()}

    # Predict endpoint
    predicted_remaining_years: Optional[int] = None
    prediction_range: Optional[str] = None  # e.g. "1-2"
    one_year_survival_pct: Optional[float] = None  # probability of lasting 1yr
    # Statistics endpoint
    model_avg_final_miles: Optional[int] = None
    model_avg_final_age: Optional[int] = None
    manufacturer_avg_final_miles: Optional[int] = None
    manufacturer_avg_final_age: Optional[int] = None
    pct_still_on_road: Optional[float] = None  # % of same model/year still registered
    initially_registered: Optional[int] = None
    currently_licensed: Optional[int] = None
    data_source: str = "AutoPredict"


class BatteryHealth(BaseModel):
    """Derived battery health score combining ClearWatt data."""
    score: Optional[int] = None  # 0-100
    grade: Optional[str] = None  # A-F (or ClearWatt test grade if available)
    degradation_estimate_pct: Optional[float] = None
    summary: Optional[str] = None
    # ClearWatt battery test result (if exists)
    test_grade: Optional[str] = None  # e.g. "A+", from actual battery test
    test_date: Optional[str] = None


class ChargingCosts(BaseModel):
    """Charging cost comparison — uses real pence/mile from EV Database when available."""
    home_cost_per_full_charge: Optional[float] = None
    rapid_cost_per_full_charge: Optional[float] = None
    cost_per_mile_home: Optional[float] = None  # pence
    cost_per_mile_rapid: Optional[float] = None  # pence
    cost_per_mile_public: Optional[float] = None  # pence (public charger rate)
    annual_cost_estimate_home: Optional[float] = None  # £ at 10k miles/yr
    annual_cost_estimate_rapid: Optional[float] = None  # £
    vs_petrol_annual_saving: Optional[float] = None  # £


class EVCheckResponse(BaseModel):
    """Response schema for an EV check."""
    registration: str
    tier: str = "ev_free"
    is_electric: bool = False
    ev_type: Optional[str] = None  # "BEV", "PHEV", or None
    vehicle: Optional[Any] = None  # VehicleIdentity from check schemas
    mot_summary: Optional[Any] = None  # MOTSummary from check schemas
    mot_tests: List[Any] = []
    clocking_analysis: Optional[Any] = None
    condition_score: Optional[int] = None
    mileage_timeline: List[Any] = []
    failure_patterns: List[Any] = []
    ulez_compliance: Optional[Any] = None
    tax_calculation: Optional[Any] = None
    safety_rating: Optional[Any] = None
    vehicle_stats: Optional[Any] = None
    # EV-specific paid data
    range_estimate: Optional[RangeEstimate] = None
    range_scenarios: List[RangeScenario] = []
    ev_specs: Optional[EVSpecs] = None
    lifespan_prediction: Optional[LifespanPrediction] = None
    battery_health: Optional[BatteryHealth] = None
    charging_costs: Optional[ChargingCosts] = None
    # Meta
    checked_at: datetime = Field(default_factory=datetime.utcnow)
    data_sources: List[str] = []

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}
