from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
import re


class FreeCheckRequest(BaseModel):
    """Request schema for a free vehicle check."""

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


class BasicCheckRequest(FreeCheckRequest):
    """Request schema for a basic (paid) vehicle check."""

    email: str = Field(..., description="Email for report delivery")
    listing_url: Optional[str] = Field(None, description="URL of the vehicle listing")
    listing_price: Optional[int] = Field(None, ge=0, description="Listed price in pence")


class MileageReading(BaseModel):
    date: str
    miles: int
    unit: str = "mi"


class ClockingFlag(BaseModel):
    type: str
    severity: str
    detail: str
    from_date: Optional[str] = None
    to_date: Optional[str] = None
    drop_amount: Optional[int] = None


class ClockingAnalysis(BaseModel):
    clocked: bool
    risk_level: str
    reason: Optional[str] = None
    flags: List[ClockingFlag] = []


class FailurePattern(BaseModel):
    category: str
    occurrences: int
    concern_level: str


class LatestTest(BaseModel):
    date: Optional[str] = None
    result: Optional[str] = None
    odometer: Optional[str] = None
    expiry_date: Optional[str] = None


class MOTSummary(BaseModel):
    total_tests: int = 0
    total_passes: int = 0
    total_failures: int = 0
    registration: Optional[str] = None
    make: Optional[str] = None
    model: Optional[str] = None
    first_used_date: Optional[str] = None
    latest_test: Optional[LatestTest] = None
    current_odometer: Optional[str] = None
    has_outstanding_recall: Optional[str] = None  # "Yes", "No", "Unknown", "Unavailable"


class MOTDefect(BaseModel):
    type: str
    text: str


class MOTTestRecord(BaseModel):
    """Individual MOT test record with full details."""
    test_number: int
    test_id: str = ""
    date: str
    result: str
    odometer: Optional[int] = None
    odometer_unit: Optional[str] = "mi"
    expiry_date: Optional[str] = None
    advisories: List[MOTDefect] = []
    failures: List[MOTDefect] = []
    dangerous: List[MOTDefect] = []
    total_defects: int = 0


class ZoneDetail(BaseModel):
    zone_id: str
    name: str
    region: str
    compliant: bool
    charge: str
    cars_affected: bool
    zone_type: str


class ULEZCompliance(BaseModel):
    compliant: Optional[bool] = None
    status: str
    reason: str
    euro_standard: Optional[int] = None
    euro_inferred: Optional[bool] = None
    fuel_type: Optional[str] = None
    daily_charge: Optional[str] = None
    zones: Dict[str, bool] = {}
    zone_details: List[ZoneDetail] = []
    total_zones: Optional[int] = None
    compliant_zones: Optional[int] = None
    non_compliant_zones: Optional[int] = None
    charges_apply_zones: Optional[int] = None


class TaxCalculation(BaseModel):
    """UK Vehicle Excise Duty calculation."""
    band: str
    band_range: str
    co2_emissions: int
    fuel_type: str
    first_year_rate: int
    annual_rate: int
    six_month_rate: float
    monthly_total: float
    is_electric: bool = False
    is_diesel: bool = False


class SafetyRating(BaseModel):
    """Euro NCAP safety rating."""
    source: str = "Euro NCAP"
    make: str
    model: str
    year_range: str
    stars: int
    adult: int
    child: int
    pedestrian: int
    safety_assist: int
    overall: int
    test_year: int


class VehicleStats(BaseModel):
    """Derived vehicle statistics."""
    vehicle_age_years: Optional[int] = None
    year_of_manufacture: Optional[int] = None
    first_registered: Optional[str] = None
    mot_expiry_date: Optional[str] = None
    mot_days_remaining: Optional[int] = None
    mot_status_detail: Optional[str] = None
    tax_due_date: Optional[str] = None
    tax_days_remaining: Optional[int] = None
    tax_status_detail: Optional[str] = None
    v5c_issued_date: Optional[str] = None
    v5c_days_since: Optional[int] = None
    v5c_insight: Optional[str] = None
    estimated_annual_mileage: Optional[int] = None
    total_recorded_mileage: Optional[int] = None
    mileage_readings_count: Optional[int] = None
    mileage_assessment: Optional[str] = None
    total_advisory_items: Optional[int] = None
    total_failure_items: Optional[int] = None
    total_dangerous_items: Optional[int] = None
    total_major_items: Optional[int] = None
    total_minor_items: Optional[int] = None


class FinanceRecord(BaseModel):
    agreement_type: str
    finance_company: str
    agreement_date: Optional[str] = None
    agreement_term: Optional[str] = None
    contact_number: Optional[str] = None


class FinanceCheck(BaseModel):
    finance_outstanding: bool
    record_count: int = 0
    records: List[FinanceRecord] = []
    data_source: str = "Demo"


class StolenCheck(BaseModel):
    stolen: bool
    reported_date: Optional[str] = None
    police_force: Optional[str] = None
    reference: Optional[str] = None
    data_source: str = "Demo"


class WriteOffRecord(BaseModel):
    category: str
    date: str
    loss_type: Optional[str] = None


class WriteOffCheck(BaseModel):
    written_off: bool
    record_count: int = 0
    records: List[WriteOffRecord] = []
    data_source: str = "Demo"


class PlateChangeRecord(BaseModel):
    previous_plate: str
    change_date: str
    change_type: str


class PlateChangeHistory(BaseModel):
    changes_found: bool
    record_count: int = 0
    records: List[PlateChangeRecord] = []
    data_source: str = "Demo"


class Valuation(BaseModel):
    private_sale: Optional[int] = None
    dealer_forecourt: Optional[int] = None
    trade_in: Optional[int] = None
    part_exchange: Optional[int] = None
    valuation_date: str
    mileage_used: Optional[int] = None
    condition: str
    data_source: str = "Demo"


class VehicleIdentity(BaseModel):
    registration: Optional[str] = None
    make: Optional[str] = None
    colour: Optional[str] = None
    fuel_type: Optional[str] = None
    year_of_manufacture: Optional[int] = None
    engine_capacity: Optional[int] = None
    co2_emissions: Optional[int] = None
    euro_status: Optional[str] = None
    tax_status: Optional[str] = None
    tax_due_date: Optional[str] = None
    mot_status: Optional[str] = None
    mot_expiry_date: Optional[str] = None
    date_of_last_v5c_issued: Optional[str] = None
    marked_for_export: Optional[bool] = None
    type_approval: Optional[str] = None
    wheelplan: Optional[str] = None


class FreeCheckResponse(BaseModel):
    """Response schema for a free vehicle check."""

    registration: str
    tier: str = "free"
    vehicle: Optional[VehicleIdentity] = None
    mot_summary: Optional[MOTSummary] = None
    mot_tests: List[MOTTestRecord] = []
    clocking_analysis: Optional[ClockingAnalysis] = None
    condition_score: Optional[int] = None
    mileage_timeline: List[MileageReading] = []
    failure_patterns: List[FailurePattern] = []
    ulez_compliance: Optional[ULEZCompliance] = None
    tax_calculation: Optional[TaxCalculation] = None
    safety_rating: Optional[SafetyRating] = None
    vehicle_stats: Optional[VehicleStats] = None
    finance_check: Optional[FinanceCheck] = None
    stolen_check: Optional[StolenCheck] = None
    write_off_check: Optional[WriteOffCheck] = None
    plate_changes: Optional[PlateChangeHistory] = None
    valuation: Optional[Valuation] = None
    checked_at: datetime = Field(default_factory=datetime.utcnow)
    data_sources: List[str] = []

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}
