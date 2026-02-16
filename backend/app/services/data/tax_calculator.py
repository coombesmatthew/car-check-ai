"""UK Vehicle Excise Duty (road tax) calculator.

Calculates tax band and annual cost from CO2 emissions and fuel type.
Based on gov.uk VED rates for cars registered after 1 April 2017.
Standard rate (year 2+) is flat £190/year for most vehicles.
First-year rates vary by CO2. We show both.

Source: https://www.gov.uk/vehicle-tax-rate-tables
Rates as of 2025/26 tax year.
"""

from typing import Optional, Dict

# CO2 band boundaries (g/km) and labels
CO2_BANDS = [
    (0, "A"),
    (50, "B"),
    (75, "C"),
    (90, "D"),
    (100, "E"),
    (110, "F"),
    (130, "G"),
    (150, "H"),
    (170, "I"),
    (190, "J"),
    (225, "K"),
    (255, "L"),
    (float("inf"), "M"),
]

# First-year VED rates by CO2 band (petrol/diesel) — 2025/26
# Source: gov.uk vehicle tax rate tables
FIRST_YEAR_RATES = {
    "A": 0,
    "B": 10,
    "C": 30,
    "D": 135,
    "E": 165,
    "F": 185,
    "G": 210,
    "H": 250,
    "I": 295,
    "J": 350,
    "K": 395,
    "L": 650,
    "M": 2745,
}

# Diesel supplement for first year (applies to diesels not meeting RDE2)
DIESEL_SUPPLEMENT = {
    "A": 0,
    "B": 30,
    "C": 135,
    "D": 165,
    "E": 185,
    "F": 210,
    "G": 250,
    "H": 295,
    "I": 350,
    "J": 395,
    "K": 650,
    "L": 2745,
    "M": 2745,
}

# Standard rate (year 2 onwards) — flat rate for most cars
STANDARD_ANNUAL_RATE = 190
STANDARD_SIX_MONTH_RATE = 99.75  # 6-month payment (slightly more than half)
STANDARD_MONTHLY_TOTAL = 199.50  # 12 monthly instalments total

# Electric vehicles
ELECTRIC_ANNUAL_RATE = 0  # Zero until 2025, then £10 rising

# Alternative fuel discount
ALT_FUEL_DISCOUNT = 10  # £10/year discount for hybrid/LPG etc.


def get_co2_band(co2: int) -> str:
    """Get the VED band letter for a given CO2 emission value."""
    for threshold, band in CO2_BANDS:
        if co2 <= threshold:
            return band
    return "M"


def get_co2_band_range(band: str) -> str:
    """Get the CO2 range string for a band."""
    ranges = {
        "A": "0 g/km",
        "B": "1-50 g/km",
        "C": "51-75 g/km",
        "D": "76-90 g/km",
        "E": "91-100 g/km",
        "F": "101-110 g/km",
        "G": "111-130 g/km",
        "H": "131-150 g/km",
        "I": "151-170 g/km",
        "J": "171-190 g/km",
        "K": "191-225 g/km",
        "L": "226-255 g/km",
        "M": "Over 255 g/km",
    }
    return ranges.get(band, "Unknown")


def calculate_tax(
    co2_emissions: Optional[int],
    fuel_type: Optional[str],
) -> Optional[Dict]:
    """Calculate UK vehicle tax band and costs.

    Args:
        co2_emissions: CO2 emissions in g/km
        fuel_type: Fuel type string from DVLA (e.g. "PETROL", "DIESEL", "ELECTRIC")

    Returns:
        Dict with band, rates, and costs, or None if insufficient data.
    """
    if co2_emissions is None:
        return None

    fuel_upper = (fuel_type or "").upper()

    # Electric vehicles
    if fuel_upper in ("ELECTRIC", "ELECTRICITY"):
        return {
            "band": "A",
            "band_range": "0 g/km",
            "co2_emissions": 0,
            "fuel_type": fuel_upper,
            "first_year_rate": 0,
            "annual_rate": ELECTRIC_ANNUAL_RATE,
            "six_month_rate": 0,
            "monthly_total": 0,
            "is_electric": True,
            "is_diesel": False,
        }

    band = get_co2_band(co2_emissions)
    band_range = get_co2_band_range(band)

    is_diesel = "DIESEL" in fuel_upper
    is_hybrid = "HYBRID" in fuel_upper or "PLUG-IN" in fuel_upper

    # First year rate
    if is_diesel:
        first_year = DIESEL_SUPPLEMENT.get(band, FIRST_YEAR_RATES.get(band, 0))
    else:
        first_year = FIRST_YEAR_RATES.get(band, 0)

    # Standard rate (year 2+)
    annual = STANDARD_ANNUAL_RATE
    if is_hybrid or fuel_upper in ("GAS", "LPG", "CNG"):
        annual -= ALT_FUEL_DISCOUNT

    six_month = STANDARD_SIX_MONTH_RATE
    monthly_total = STANDARD_MONTHLY_TOTAL

    return {
        "band": band,
        "band_range": band_range,
        "co2_emissions": co2_emissions,
        "fuel_type": fuel_upper,
        "first_year_rate": first_year,
        "annual_rate": annual,
        "six_month_rate": six_month,
        "monthly_total": monthly_total,
        "is_electric": False,
        "is_diesel": is_diesel,
    }
