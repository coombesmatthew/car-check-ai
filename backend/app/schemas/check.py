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


class ULEZCompliance(BaseModel):
    compliant: Optional[bool] = None
    status: str
    reason: str
    euro_standard: Optional[int] = None
    euro_inferred: Optional[bool] = None
    fuel_type: Optional[str] = None
    daily_charge: Optional[str] = None
    zones: Dict[str, bool] = {}


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
    clocking_analysis: Optional[ClockingAnalysis] = None
    condition_score: Optional[int] = None
    mileage_timeline: List[MileageReading] = []
    failure_patterns: List[FailurePattern] = []
    ulez_compliance: Optional[ULEZCompliance] = None
    checked_at: datetime = Field(default_factory=datetime.utcnow)
    data_sources: List[str] = []

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}
