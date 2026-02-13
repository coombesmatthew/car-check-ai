from typing import Dict, Optional

from app.core.logging import logger

# ULEZ compliance rules (London):
#   Petrol: Euro 4+ (generally vehicles from ~2006 onwards)
#   Diesel: Euro 6+ (generally vehicles from ~2015 onwards)
#   Electric/Hydrogen: Always compliant
#   Hybrids: Follow petrol or diesel rules based on primary fuel

# Euro standard minimum numbers for compliance
ULEZ_PETROL_MIN_EURO = 4
ULEZ_DIESEL_MIN_EURO = 6

# Clean Air Zone classes (UK outside London)
# CAZ A: Buses/coaches/taxis only
# CAZ B: + HGVs
# CAZ C: + LGVs/vans
# CAZ D: + cars (same as ULEZ rules for cars)

EXEMPT_FUEL_TYPES = {"ELECTRICITY", "ELECTRIC", "HYDROGEN"}
PETROL_FUEL_TYPES = {"PETROL"}
DIESEL_FUEL_TYPES = {"DIESEL", "HEAVY OIL"}


def calculate_ulez_compliance(vehicle_data: Optional[Dict]) -> Dict:
    """Calculate ULEZ and Clean Air Zone compliance from DVLA VES data.

    Args:
        vehicle_data: DVLA VES API response dict containing fuelType,
                     euroStatus, etc.

    Returns:
        Dict with compliance status and details.
    """
    if not vehicle_data:
        return {
            "compliant": None,
            "status": "unknown",
            "reason": "No vehicle data available",
            "zones": {},
        }

    fuel_type = (vehicle_data.get("fuelType") or "").upper()
    euro_status = vehicle_data.get("euroStatus") or ""

    # Electric/hydrogen always compliant
    if fuel_type in EXEMPT_FUEL_TYPES:
        return {
            "compliant": True,
            "status": "exempt",
            "reason": f"{fuel_type.title()} vehicles are exempt from all emission zones",
            "zones": {
                "london_ulez": True,
                "london_lez": True,
                "clean_air_zone_d": True,
            },
        }

    # Parse euro standard number from string like "Euro 6" or "EURO 4"
    euro_number = _parse_euro_number(euro_status)

    if euro_number is None:
        # Try to infer from year of manufacture
        year = vehicle_data.get("yearOfManufacture")
        if year:
            euro_number = _estimate_euro_from_year(year, fuel_type)
            inferred = True
        else:
            return {
                "compliant": None,
                "status": "unknown",
                "reason": "Euro standard not available - check with manufacturer",
                "zones": {},
            }
    else:
        inferred = False

    # Determine compliance
    if fuel_type in PETROL_FUEL_TYPES or "PETROL" in fuel_type:
        min_euro = ULEZ_PETROL_MIN_EURO
        compliant = euro_number >= min_euro
    elif fuel_type in DIESEL_FUEL_TYPES or "DIESEL" in fuel_type:
        min_euro = ULEZ_DIESEL_MIN_EURO
        compliant = euro_number >= min_euro
    else:
        # Hybrid or unknown - check both thresholds, use stricter
        if "HYBRID" in fuel_type and "DIESEL" in fuel_type:
            min_euro = ULEZ_DIESEL_MIN_EURO
        else:
            min_euro = ULEZ_PETROL_MIN_EURO
        compliant = euro_number >= min_euro

    status = "compliant" if compliant else "non_compliant"

    reason_parts = [f"{fuel_type.title()} vehicle with Euro {euro_number}"]
    if inferred:
        reason_parts.append("(estimated from year)")
    reason_parts.append(f"- {'meets' if compliant else 'does not meet'} Euro {min_euro} requirement")

    return {
        "compliant": compliant,
        "status": status,
        "reason": " ".join(reason_parts),
        "euro_standard": euro_number,
        "euro_inferred": inferred if euro_number else None,
        "fuel_type": fuel_type,
        "daily_charge": None if compliant else "£12.50 (London ULEZ)",
        "zones": {
            "london_ulez": compliant,
            "london_lez": True,  # LEZ is for HGVs/buses, cars always pass
            "clean_air_zone_d": compliant,
        },
    }


def _parse_euro_number(euro_status: str) -> Optional[int]:
    """Extract the numeric euro standard from strings like 'Euro 6' or 'EURO6D'."""
    if not euro_status:
        return None

    import re
    match = re.search(r"(\d)", euro_status)
    if match:
        return int(match.group(1))
    return None


def _estimate_euro_from_year(year: int, fuel_type: str) -> Optional[int]:
    """Rough estimate of Euro standard from year of manufacture.

    Not definitive - actual Euro standard depends on specific model.
    """
    fuel_upper = fuel_type.upper()
    is_diesel = fuel_upper in DIESEL_FUEL_TYPES or "DIESEL" in fuel_upper

    if is_diesel:
        if year >= 2015:
            return 6
        elif year >= 2009:
            return 5
        elif year >= 2006:
            return 4
        elif year >= 2001:
            return 3
        else:
            return 2
    else:  # Petrol
        if year >= 2011:
            return 6
        elif year >= 2006:
            return 5  # actually Euro 4 started ~2006
        elif year >= 2001:
            return 4
        elif year >= 1997:
            return 3
        else:
            return 2
