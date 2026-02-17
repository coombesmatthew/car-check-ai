"""One Auto API client for premium vehicle provenance data.

Uses 3 API calls per check:
  1. Experian AutoCheck — finance, stolen, write-off, plates, keepers, high risk
  2. Brego Valuation — current market value
  3. CarGuide Salvage — unrecorded write-off detection

Sandbox: sandbox.oneautoapi.com (free, returns dummy data)
Live: api.oneautoapi.com (requires credit card, returns real data)
"""

import httpx
from datetime import date
from typing import Dict, List, Optional

from app.core.config import settings
from app.core.logging import logger


class OneAutoClient:
    """Async client for One Auto API."""

    def __init__(self):
        base = settings.ONEAUTO_API_URL.rstrip("/")
        self._client = httpx.AsyncClient(
            base_url=base,
            headers={"x-api-key": settings.ONEAUTO_API_KEY},
            timeout=30.0,
        )

    async def _get(self, path: str, params: Dict) -> Optional[Dict]:
        """Make a GET request and return the result dict, or None on failure."""
        try:
            resp = await self._client.get(path, params=params)
            data = resp.json()
            if data.get("success"):
                return data.get("result")
            error = data.get("result", {}).get("error") or data.get("error")
            logger.warning(f"One Auto API error on {path}: {error}")
            return None
        except Exception as e:
            logger.error(f"One Auto API request failed on {path}: {e}")
            return None

    async def get_autocheck(self, registration: str) -> Optional[Dict]:
        """Experian AutoCheck — single call covering finance, stolen, write-off,
        plates, keepers, colour changes, high risk, previous searches, V5C history."""
        return await self._get(
            "/experian/autocheck/v3",
            {"vehicle_registration_mark": registration},
        )

    async def get_valuation(self, registration: str, mileage: int) -> Optional[Dict]:
        """Brego vehicle valuation."""
        return await self._get(
            "/brego/valuationfromvrm/v2",
            {
                "vehicle_registration_mark": registration,
                "current_mileage": mileage,
            },
        )

    async def get_salvage(self, registration: str) -> Optional[Dict]:
        """CarGuide salvage auction check."""
        return await self._get(
            "/carguide/salvagecheck/v2",
            {"vehicle_registration_mark": registration},
        )

    async def close(self):
        await self._client.aclose()


# ---------------------------------------------------------------------------
# Parsers — extract structured data from AutoCheck / Brego / CarGuide
# ---------------------------------------------------------------------------


def parse_autocheck(raw: Optional[Dict]) -> Dict:
    """Parse a single AutoCheck response into all provenance sub-dicts."""
    return {
        "finance_check": _parse_finance(raw),
        "stolen_check": _parse_stolen(raw),
        "write_off_check": _parse_condition(raw),
        "plate_changes": _parse_plate_changes(raw),
        "keeper_history": _parse_keepers(raw),
        "high_risk": _parse_high_risk(raw),
        "previous_searches": _parse_previous_searches(raw),
        "v5c_history": _parse_v5c(raw),
        "vehicle_id": _parse_vehicle_id(raw),
    }


def _parse_finance(raw: Optional[Dict]) -> Dict:
    """Extract finance records from AutoCheck response."""
    if not raw:
        return _empty_finance()

    items = raw.get("finance_data_items") or []
    records = []
    for item in items:
        records.append({
            "agreement_type": item.get("finance_type", "Unknown"),
            "finance_company": item.get("finance_company", "Unknown"),
            "agreement_date": item.get("finance_start_date"),
            "agreement_term": f"{item['finance_term_months']} months" if item.get("finance_term_months") else None,
            "contact_number": item.get("finance_company_contact_number"),
        })

    return {
        "finance_outstanding": len(records) > 0,
        "record_count": len(records),
        "records": records,
        "data_source": "Experian",
    }


def _parse_stolen(raw: Optional[Dict]) -> Dict:
    """Extract stolen status from AutoCheck response."""
    if not raw:
        return _empty_stolen()

    items = raw.get("stolen_vehicle_data_items") or []
    if items:
        item = items[0]
        return {
            "stolen": item.get("is_stolen", False),
            "reported_date": item.get("date_reported"),
            "police_force": item.get("police_force"),
            "reference": item.get("police_force_contact_number"),
            "data_source": "Experian",
        }

    return _empty_stolen()


def _parse_condition(raw: Optional[Dict]) -> Dict:
    """Extract write-off / condition data from AutoCheck response."""
    if not raw:
        return _empty_writeoff()

    items = raw.get("condition_data_items") or []
    records = []
    for item in items:
        records.append({
            "category": item.get("recovered_category", ""),
            "date": item.get("date_of_loss", ""),
            "loss_type": item.get("loss_type") or item.get("cause_of_damage"),
        })

    return {
        "written_off": len(records) > 0,
        "record_count": len(records),
        "records": records,
        "data_source": "Experian",
    }


def _parse_plate_changes(raw: Optional[Dict]) -> Dict:
    """Extract plate change history from AutoCheck response."""
    if not raw:
        return _empty_plates()

    items = raw.get("cherished_data_items") or []
    records = []
    for item in items:
        prev = item.get("previous_vehicle_registration_mark", "")
        curr = item.get("current_vehicle_registration_mark", "")
        if prev and curr and prev != curr:
            records.append({
                "previous_plate": prev,
                "change_date": item.get("cherished_plate_transfer_date", ""),
                "change_type": item.get("transfer_type", "Transfer"),
            })

    return {
        "changes_found": len(records) > 0,
        "record_count": len(records),
        "records": records,
        "data_source": "Experian",
    }


def _parse_keepers(raw: Optional[Dict]) -> Dict:
    """Extract keeper change history from AutoCheck response."""
    if not raw:
        return {"keeper_count": None, "last_change_date": None, "data_source": "Experian"}

    items = raw.get("keeper_data_items") or []
    if items:
        item = items[0]
        return {
            "keeper_count": item.get("number_previous_keepers"),
            "last_change_date": item.get("date_of_last_keeper_change"),
            "data_source": "Experian",
        }

    return {"keeper_count": None, "last_change_date": None, "data_source": "Experian"}


def _parse_high_risk(raw: Optional[Dict]) -> Dict:
    """Extract high risk markers from AutoCheck response."""
    if not raw:
        return {"flagged": False, "records": [], "data_source": "Experian"}

    items = raw.get("high_risk_data_items") or []
    records = []
    for item in items:
        records.append({
            "risk_type": item.get("high_risk_type", ""),
            "date": item.get("date_of_interest"),
            "detail": item.get("extra_information"),
            "company": item.get("company_name"),
            "contact": item.get("company_contact_number"),
        })

    return {
        "flagged": len(records) > 0,
        "records": records,
        "data_source": "Experian",
    }


def _parse_previous_searches(raw: Optional[Dict]) -> Dict:
    """Extract previous search history from AutoCheck response."""
    if not raw:
        return {"search_count": 0, "records": [], "data_source": "Experian"}

    items = raw.get("previous_search_items") or []
    records = []
    for item in items:
        records.append({
            "date": item.get("date_of_search"),
            "business_type": item.get("business_type_searching"),
        })

    return {
        "search_count": len(records),
        "records": records,
        "data_source": "Experian",
    }


def _parse_v5c(raw: Optional[Dict]) -> Dict:
    """Extract V5C certificate history from AutoCheck response."""
    if not raw:
        return {"v5c_count": 0, "records": [], "data_source": "Experian"}

    items = raw.get("v5c_data_items") or []
    records = [{"date_issued": item.get("date_v5c_issued")} for item in items]

    return {
        "v5c_count": len(records),
        "records": records,
        "data_source": "Experian",
    }


def _parse_vehicle_id(raw: Optional[Dict]) -> Dict:
    """Extract vehicle identity extras from AutoCheck response."""
    if not raw:
        return {}
    return {
        "vin": raw.get("vehicle_identification_number"),
        "engine_number": raw.get("engine_number"),
        "is_scrapped": raw.get("is_scrapped"),
        "scrapped_date": raw.get("scrapped_date"),
        "is_imported": raw.get("is_imported"),
        "is_exported": raw.get("is_exported"),
        "colour": raw.get("colour"),
        "original_colour": raw.get("original_colour"),
        "number_previous_colours": raw.get("number_previous_colours"),
    }


def parse_valuation(raw: Optional[Dict], mileage: int) -> Dict:
    """Map Brego valuation response to our Valuation schema."""
    if not raw:
        return {
            "private_sale": None,
            "dealer_forecourt": None,
            "trade_in": None,
            "part_exchange": None,
            "valuation_date": date.today().isoformat(),
            "mileage_used": mileage,
            "condition": "Unknown",
            "data_source": "Brego",
        }

    return {
        "private_sale": raw.get("retail_average_valuation"),
        "dealer_forecourt": raw.get("retail_high_valuation"),
        "trade_in": raw.get("trade_average_valuation"),
        "part_exchange": raw.get("trade_high_valuation"),
        "valuation_date": date.today().isoformat(),
        "mileage_used": raw.get("current_mileage", mileage),
        "condition": "Mileage-adjusted",
        "data_source": "Brego",
    }


def parse_salvage(raw: Optional[Dict]) -> Dict:
    """Map CarGuide salvage check response."""
    if not raw:
        return {"salvage_found": False, "data_source": "CarGuide"}

    # CarGuide returns salvage auction records if found
    return {
        "salvage_found": bool(raw.get("salvage_data_items")),
        "records": raw.get("salvage_data_items", []),
        "data_source": "CarGuide",
    }


# ---------------------------------------------------------------------------
# Empty defaults
# ---------------------------------------------------------------------------

def _empty_finance() -> Dict:
    return {"finance_outstanding": False, "record_count": 0, "records": [], "data_source": "Experian"}

def _empty_stolen() -> Dict:
    return {"stolen": False, "reported_date": None, "police_force": None, "reference": None, "data_source": "Experian"}

def _empty_writeoff() -> Dict:
    return {"written_off": False, "record_count": 0, "records": [], "data_source": "Experian"}

def _empty_plates() -> Dict:
    return {"changes_found": False, "record_count": 0, "records": [], "data_source": "Experian"}
