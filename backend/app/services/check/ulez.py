"""UK Clean Air Zone & Emission Zone compliance calculator.

Covers ALL active UK emission zones as of 2025/26:

ENGLAND:
  - London ULEZ (Greater London) — Class D, £12.50/day for cars
  - London LEZ (Greater London) — HGVs/buses only, cars exempt
  - Birmingham CAZ — Class D, £8/day for cars
  - Bristol CAZ — Class D, £9/day for cars
  - Bath CAZ — Class C, commercial only (no car charge)
  - Bradford CAZ — Class C, commercial only
  - Portsmouth CAZ — Class B, commercial only
  - Sheffield CAZ — Class C, commercial only
  - Tyneside CAZ (Newcastle/Gateshead) — Class C, commercial only

SCOTLAND (LEZs — penalty-based, not daily charge):
  - Glasgow LEZ — £60 first offence, doubles per offence (max £480)
  - Edinburgh LEZ — Same penalty structure
  - Aberdeen LEZ — Same penalty structure
  - Dundee LEZ — Same penalty structure

OTHER:
  - Oxford ZEZ (Zero Emission Zone) — £2-£10/day (all non-EVs charged)

Compliance rules:
  Petrol: Euro 4+ (vehicles from ~2006 onwards)
  Diesel: Euro 6+ (vehicles from ~2015 onwards)
  Electric/Hydrogen: Always exempt
  Scotland LEZs: Same Euro standard requirements, penalty not daily charge
  Oxford ZEZ: Only zero-emission vehicles are fully exempt
"""

from typing import Dict, Optional

from app.core.logging import logger

# Euro standard minimums for compliance
PETROL_MIN_EURO = 4
DIESEL_MIN_EURO = 6

EXEMPT_FUEL_TYPES = {"ELECTRICITY", "ELECTRIC", "HYDROGEN"}
PETROL_FUEL_TYPES = {"PETROL"}
DIESEL_FUEL_TYPES = {"DIESEL", "HEAVY OIL"}

# Zone definitions
# class: A=buses/taxis, B=+HGVs, C=+LGVs/vans, D=+cars
ZONES = {
    # ENGLAND — Daily charge zones
    "london_ulez": {
        "name": "London ULEZ",
        "region": "England",
        "type": "daily_charge",
        "class": "D",
        "cars_affected": True,
        "charge": "£12.50/day",
        "charge_amount": 12.50,
        "petrol_min_euro": 4,
        "diesel_min_euro": 6,
    },
    "london_lez": {
        "name": "London LEZ",
        "region": "England",
        "type": "daily_charge",
        "class": "LEZ",
        "cars_affected": False,
        "charge": "N/A (cars exempt)",
        "charge_amount": 0,
        "petrol_min_euro": 4,
        "diesel_min_euro": 6,
    },
    "birmingham_caz": {
        "name": "Birmingham CAZ",
        "region": "England",
        "type": "daily_charge",
        "class": "D",
        "cars_affected": True,
        "charge": "£8/day",
        "charge_amount": 8.00,
        "petrol_min_euro": 4,
        "diesel_min_euro": 6,
    },
    "bristol_caz": {
        "name": "Bristol CAZ",
        "region": "England",
        "type": "daily_charge",
        "class": "D",
        "cars_affected": True,
        "charge": "£9/day",
        "charge_amount": 9.00,
        "petrol_min_euro": 4,
        "diesel_min_euro": 6,
    },
    "bath_caz": {
        "name": "Bath CAZ",
        "region": "England",
        "type": "daily_charge",
        "class": "C",
        "cars_affected": False,
        "charge": "N/A (cars exempt)",
        "charge_amount": 0,
        "petrol_min_euro": 4,
        "diesel_min_euro": 6,
    },
    "bradford_caz": {
        "name": "Bradford CAZ",
        "region": "England",
        "type": "daily_charge",
        "class": "C",
        "cars_affected": False,
        "charge": "N/A (cars exempt)",
        "charge_amount": 0,
        "petrol_min_euro": 4,
        "diesel_min_euro": 6,
    },
    "portsmouth_caz": {
        "name": "Portsmouth CAZ",
        "region": "England",
        "type": "daily_charge",
        "class": "B",
        "cars_affected": False,
        "charge": "N/A (cars exempt)",
        "charge_amount": 0,
        "petrol_min_euro": 4,
        "diesel_min_euro": 6,
    },
    "sheffield_caz": {
        "name": "Sheffield CAZ",
        "region": "England",
        "type": "daily_charge",
        "class": "C",
        "cars_affected": False,
        "charge": "N/A (cars exempt)",
        "charge_amount": 0,
        "petrol_min_euro": 4,
        "diesel_min_euro": 6,
    },
    "tyneside_caz": {
        "name": "Tyneside CAZ (Newcastle/Gateshead)",
        "region": "England",
        "type": "daily_charge",
        "class": "C",
        "cars_affected": False,
        "charge": "N/A (cars exempt)",
        "charge_amount": 0,
        "petrol_min_euro": 4,
        "diesel_min_euro": 6,
    },
    # SCOTLAND — Penalty-based LEZs
    "glasgow_lez": {
        "name": "Glasgow LEZ",
        "region": "Scotland",
        "type": "penalty",
        "class": "LEZ",
        "cars_affected": True,
        "charge": "£60 first offence (doubles, max £480)",
        "charge_amount": 60.00,
        "petrol_min_euro": 4,
        "diesel_min_euro": 6,
    },
    "edinburgh_lez": {
        "name": "Edinburgh LEZ",
        "region": "Scotland",
        "type": "penalty",
        "class": "LEZ",
        "cars_affected": True,
        "charge": "£60 first offence (doubles, max £480)",
        "charge_amount": 60.00,
        "petrol_min_euro": 4,
        "diesel_min_euro": 6,
    },
    "aberdeen_lez": {
        "name": "Aberdeen LEZ",
        "region": "Scotland",
        "type": "penalty",
        "class": "LEZ",
        "cars_affected": True,
        "charge": "£60 first offence (doubles, max £480)",
        "charge_amount": 60.00,
        "petrol_min_euro": 4,
        "diesel_min_euro": 6,
    },
    "dundee_lez": {
        "name": "Dundee LEZ",
        "region": "Scotland",
        "type": "penalty",
        "class": "LEZ",
        "cars_affected": True,
        "charge": "£60 first offence (doubles, max £480)",
        "charge_amount": 60.00,
        "petrol_min_euro": 4,
        "diesel_min_euro": 6,
    },
    # OXFORD — Zero Emission Zone (charges all non-EVs)
    "oxford_zez": {
        "name": "Oxford ZEZ",
        "region": "England",
        "type": "daily_charge",
        "class": "ZEZ",
        "cars_affected": True,
        "charge": "£4-£10/day (all non-EVs)",
        "charge_amount": 4.00,
        "petrol_min_euro": None,  # No Euro exemption — only EVs exempt
        "diesel_min_euro": None,
    },
}


def calculate_ulez_compliance(vehicle_data: Optional[Dict]) -> Dict:
    """Calculate compliance for all UK emission zones.

    Args:
        vehicle_data: DVLA VES API response dict.

    Returns:
        Dict with overall compliance status, zone-by-zone results, and charges.
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
    is_ev = fuel_type in EXEMPT_FUEL_TYPES

    # Electric/hydrogen always compliant everywhere
    if is_ev:
        zone_results = {}
        zone_details = []
        for zone_id, zone in ZONES.items():
            zone_results[zone_id] = True
            zone_details.append({
                "zone_id": zone_id,
                "name": zone["name"],
                "region": zone["region"],
                "compliant": True,
                "charge": "Exempt",
                "cars_affected": zone["cars_affected"],
                "zone_type": zone["type"],
            })

        return {
            "compliant": True,
            "status": "exempt",
            "reason": f"{fuel_type.title()} vehicles are exempt from all UK emission zones",
            "euro_standard": None,
            "euro_inferred": None,
            "fuel_type": fuel_type,
            "daily_charge": None,
            "zones": zone_results,
            "zone_details": zone_details,
            "total_zones": len(ZONES),
            "compliant_zones": len(ZONES),
            "non_compliant_zones": 0,
            "charges_apply_zones": 0,
        }

    # Parse euro standard
    euro_number = _parse_euro_number(euro_status)
    inferred = False

    if euro_number is None:
        year = vehicle_data.get("yearOfManufacture")
        if year:
            euro_number = _estimate_euro_from_year(year, fuel_type)
            inferred = True
        else:
            return {
                "compliant": None,
                "status": "unknown",
                "reason": "Euro standard not available — check with manufacturer",
                "zones": {},
                "zone_details": [],
            }

    # Determine fuel category
    is_diesel = fuel_type in DIESEL_FUEL_TYPES or "DIESEL" in fuel_type
    is_petrol = fuel_type in PETROL_FUEL_TYPES or "PETROL" in fuel_type

    # Check each zone
    zone_results = {}
    zone_details = []
    charges_list = []

    for zone_id, zone in ZONES.items():
        # Oxford ZEZ: only EVs exempt, all others charged
        if zone["class"] == "ZEZ":
            compliant = is_ev  # Already False here (EVs handled above)
            if not zone["cars_affected"]:
                compliant = True
        elif not zone["cars_affected"]:
            # Zone doesn't affect private cars (Class A/B/C)
            compliant = True
        else:
            # Standard Euro check
            if is_diesel:
                min_euro = zone["diesel_min_euro"]
            elif is_petrol:
                min_euro = zone["petrol_min_euro"]
            else:
                # Hybrid or unknown — use stricter diesel threshold if diesel hybrid
                if "DIESEL" in fuel_type:
                    min_euro = zone["diesel_min_euro"]
                else:
                    min_euro = zone["petrol_min_euro"]

            compliant = euro_number >= min_euro if min_euro else False

        zone_results[zone_id] = compliant

        charge_text = "No charge"
        if not compliant and zone["cars_affected"]:
            charge_text = zone["charge"]
            charges_list.append({
                "zone": zone["name"],
                "charge": zone["charge"],
                "amount": zone["charge_amount"],
                "type": zone["type"],
            })

        zone_details.append({
            "zone_id": zone_id,
            "name": zone["name"],
            "region": zone["region"],
            "compliant": compliant,
            "charge": charge_text,
            "cars_affected": zone["cars_affected"],
            "zone_type": zone["type"],
        })

    # Overall compliance = compliant with all zones that affect cars
    car_zones = [z for z in zone_details if z["cars_affected"]]
    all_compliant = all(z["compliant"] for z in car_zones)
    non_compliant_count = sum(1 for z in car_zones if not z["compliant"])
    compliant_count = sum(1 for z in zone_details if z["compliant"])

    status = "compliant" if all_compliant else "non_compliant"

    # Build reason
    reason_parts = [f"{fuel_type.title()} vehicle with Euro {euro_number}"]
    if inferred:
        reason_parts.append("(estimated from year)")

    if all_compliant:
        reason_parts.append(f"— meets emission requirements for all {len(car_zones)} zones affecting cars")
    else:
        reason_parts.append(f"— non-compliant in {non_compliant_count} zone{'s' if non_compliant_count != 1 else ''}")

    # Summarise highest daily charge
    daily_charge = None
    if charges_list:
        daily_charges = [c for c in charges_list if c["type"] == "daily_charge"]
        penalty_charges = [c for c in charges_list if c["type"] == "penalty"]
        charge_parts = []
        if daily_charges:
            highest = max(daily_charges, key=lambda c: c["amount"])
            charge_parts.append(f"£{highest['amount']:.2f}/day ({highest['zone']})")
        if penalty_charges:
            charge_parts.append(f"£60+ penalty (Scottish LEZs)")
        daily_charge = " · ".join(charge_parts)

    return {
        "compliant": all_compliant,
        "status": status,
        "reason": " ".join(reason_parts),
        "euro_standard": euro_number,
        "euro_inferred": inferred if euro_number else None,
        "fuel_type": fuel_type,
        "daily_charge": daily_charge,
        "zones": zone_results,
        "zone_details": zone_details,
        "total_zones": len(ZONES),
        "compliant_zones": compliant_count,
        "non_compliant_zones": non_compliant_count,
        "charges_apply_zones": len(charges_list),
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
    """Rough estimate of Euro standard from year of manufacture."""
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
            return 5
        elif year >= 2001:
            return 4
        elif year >= 1997:
            return 3
        else:
            return 2
