"""One Auto API client for premium vehicle provenance data.

Provides access to Experian checks (finance, stolen, write-off, plates, mileage)
and Brego valuations through a single API integration.

Sandbox: sandbox.oneautoapi.com (free, returns dummy data)
Live: api.oneautoapi.com (requires credit card, returns real data)
"""

import httpx
from datetime import date
from typing import Dict, Optional

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

    async def get_finance(self, registration: str) -> Optional[Dict]:
        """Experian finance records check."""
        return await self._get(
            "/experian/financerecords/v3",
            {"vehicle_registration_mark": registration},
        )

    async def get_stolen(self, registration: str) -> Optional[Dict]:
        """Experian stolen vehicle check."""
        return await self._get(
            "/experian/stolenvehiclecheck/v3",
            {"vehicle_registration_mark": registration},
        )

    async def get_condition(self, registration: str) -> Optional[Dict]:
        """Experian condition check (write-off / MIAFTR data)."""
        return await self._get(
            "/experian/conditioncheck/v3",
            {"vehicle_registration_mark": registration},
        )

    async def get_plate_changes(self, registration: str) -> Optional[Dict]:
        """Experian plate change history."""
        return await self._get(
            "/experian/platechanges/v3",
            {"vehicle_registration_mark": registration},
        )

    async def get_mileage(self, registration: str) -> Optional[Dict]:
        """Experian mileage observations from trusted sources."""
        return await self._get(
            "/experian/mileagecheck/v3",
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


def parse_finance(raw: Optional[Dict]) -> Dict:
    """Map One Auto finance response to our FinanceCheck schema."""
    if not raw:
        return {
            "finance_outstanding": False,
            "record_count": 0,
            "records": [],
            "data_source": "Experian",
        }

    items = raw.get("finance_data_items", [])
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


def parse_stolen(raw: Optional[Dict]) -> Dict:
    """Map One Auto stolen response to our StolenCheck schema."""
    if not raw:
        return {
            "stolen": False,
            "reported_date": None,
            "police_force": None,
            "reference": None,
            "data_source": "Experian",
        }

    items = raw.get("stolen_vehicle_data_items", [])
    if items:
        item = items[0]
        return {
            "stolen": item.get("is_stolen", False),
            "reported_date": item.get("date_reported"),
            "police_force": item.get("police_force"),
            "reference": item.get("police_force_contact_number"),
            "data_source": "Experian",
        }

    return {
        "stolen": False,
        "reported_date": None,
        "police_force": None,
        "reference": None,
        "data_source": "Experian",
    }


def parse_condition(raw: Optional[Dict]) -> Dict:
    """Map One Auto condition/write-off response to our WriteOffCheck schema."""
    if not raw:
        return {
            "written_off": False,
            "record_count": 0,
            "records": [],
            "data_source": "Experian",
        }

    items = raw.get("condition_data_items", [])
    records = []
    for item in items:
        category = item.get("recovered_category", "")
        if category:
            records.append({
                "category": category,
                "date": item.get("date_of_loss", ""),
                "loss_type": item.get("loss_type"),
            })

    return {
        "written_off": len(records) > 0,
        "record_count": len(records),
        "records": records,
        "data_source": "Experian",
    }


def parse_plate_changes(raw: Optional[Dict]) -> Dict:
    """Map One Auto plate changes response to our PlateChangeHistory schema."""
    if not raw:
        return {
            "changes_found": False,
            "record_count": 0,
            "records": [],
            "data_source": "Experian",
        }

    items = raw.get("cherished_data_items", [])
    records = []
    for item in items:
        prev = item.get("previous_vehicle_registration_mark", "")
        curr = item.get("current_vehicle_registration_mark", "")
        # Only include if there's an actual plate change
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
