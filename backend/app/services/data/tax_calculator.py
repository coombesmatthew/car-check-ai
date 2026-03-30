"""UK Vehicle Excise Duty (road tax) calculator.

Calculates tax band and annual cost from CO2 emissions, fuel type, and registration year.

For cars registered on or after 1 April 2017:
  - First-year rates vary by CO2 band
  - Standard rate (year 2+) is flat £190/year for most vehicles

For cars registered before 1 April 2017:
  - Both first-year and standard rates vary by CO2 band
  - Different band structure and rates than post-2017

Source: https://www.gov.uk/vehicle-tax-rate-tables
Rates as of 2025/26 tax year.
"""

from typing import Optional, Dict

# CO2 band boundaries (g/km) and labels — POST-APRIL 2017
CO2_BANDS_POST_2017 = [
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

# CO2 band boundaries — PRE-APRIL 2017 (old system)
CO2_BANDS_PRE_2017 = [
    (0, "A"),
    (100, "B"),
    (120, "C"),
    (150, "D"),
    (170, "E"),
    (190, "F"),
    (225, "G"),
    (255, "H"),
    (float("inf"), "I"),
]

# First-year VED rates by CO2 band (petrol/diesel) — POST-APRIL 2017
# Source: gov.uk vehicle tax rate tables
FIRST_YEAR_RATES_POST_2017 = {
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

# Diesel supplement for first year (POST-2017, diesels not meeting RDE2)
DIESEL_SUPPLEMENT_POST_2017 = {
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

# Standard rates (year 2+) — PRE-APRIL 2017 (varied by CO2 band)
STANDARD_RATES_PRE_2017 = {
    "A": 0,
    "B": 20,
    "C": 30,
    "D": 105,
    "E": 120,
    "F": 145,
    "G": 165,
    "H": 205,
    "I": 230,
}

# Standard rate (year 2 onwards) — POST-APRIL 2017 (flat rate for most cars)
STANDARD_ANNUAL_RATE_POST_2017 = 190
STANDARD_SIX_MONTH_RATE_POST_2017 = 99.75  # 6-month payment (slightly more than half)
STANDARD_MONTHLY_TOTAL_POST_2017 = 199.50  # 12 monthly instalments total

# Electric vehicles
ELECTRIC_ANNUAL_RATE = 0  # Zero until 2025, then £10 rising

# Alternative fuel discount
ALT_FUEL_DISCOUNT = 10  # £10/year discount for hybrid/LPG etc.


def get_co2_band(co2: int, year: Optional[int] = None) -> str:
    """Get the VED band letter for a given CO2 emission value.

    Bands differ based on registration year:
    - Pre-April 2017: older band structure (A-I)
    - Post-April 2017: new band structure (A-M)
    """
    # If year not provided, assume post-2017 (safer for newer vehicles)
    if year is None or year >= 2017:
        bands = CO2_BANDS_POST_2017
        default = "M"
    else:
        bands = CO2_BANDS_PRE_2017
        default = "I"

    for threshold, band in bands:
        if co2 <= threshold:
            return band
    return default


def get_co2_band_range(band: str, year: Optional[int] = None) -> str:
    """Get the CO2 range string for a band."""
    # Pre-2017 ranges
    ranges_pre_2017 = {
        "A": "0 g/km",
        "B": "1-100 g/km",
        "C": "101-120 g/km",
        "D": "121-150 g/km",
        "E": "151-170 g/km",
        "F": "171-190 g/km",
        "G": "191-225 g/km",
        "H": "226-255 g/km",
        "I": "Over 255 g/km",
    }

    # Post-2017 ranges
    ranges_post_2017 = {
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

    if year and year < 2017:
        return ranges_pre_2017.get(band, "Unknown")
    return ranges_post_2017.get(band, "Unknown")


def calculate_tax(
    co2_emissions: Optional[int],
    fuel_type: Optional[str],
    year_of_manufacture: Optional[int] = None,
) -> Optional[Dict]:
    """Calculate UK vehicle tax band and costs.

    Args:
        co2_emissions: CO2 emissions in g/km
        fuel_type: Fuel type string from DVLA (e.g. "PETROL", "DIESEL", "ELECTRIC")
        year_of_manufacture: Year vehicle was manufactured (determines which tax bands to use)

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
            "tax_regime": "Electric",
        }

    # Determine if pre- or post-April 2017 registration
    is_pre_2017 = year_of_manufacture and year_of_manufacture < 2017

    band = get_co2_band(co2_emissions, year_of_manufacture)
    band_range = get_co2_band_range(band, year_of_manufacture)

    is_diesel = "DIESEL" in fuel_upper
    is_hybrid = "HYBRID" in fuel_upper or "PLUG-IN" in fuel_upper

    if is_pre_2017:
        # PRE-APRIL 2017 tax regime: varied first-year and standard rates by CO2 band
        first_year = STANDARD_RATES_PRE_2017.get(band, 0)
        annual = STANDARD_RATES_PRE_2017.get(band, 0)
        tax_regime = "Pre-April 2017"
        six_month = round(annual * 0.5, 2)  # 50% of annual
        monthly_total = round(annual, 2)  # Same as annual (12 instalments)
    else:
        # POST-APRIL 2017 tax regime: first-year rates vary, standard is flat £190
        if is_diesel:
            first_year = DIESEL_SUPPLEMENT_POST_2017.get(band, FIRST_YEAR_RATES_POST_2017.get(band, 0))
        else:
            first_year = FIRST_YEAR_RATES_POST_2017.get(band, 0)

        annual = STANDARD_ANNUAL_RATE_POST_2017
        if is_hybrid or fuel_upper in ("GAS", "LPG", "CNG"):
            annual -= ALT_FUEL_DISCOUNT

        tax_regime = "Post-April 2017"
        six_month = STANDARD_SIX_MONTH_RATE_POST_2017
        monthly_total = STANDARD_MONTHLY_TOTAL_POST_2017

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
        "tax_regime": tax_regime,
        "year_of_manufacture": year_of_manufacture,
    }
