"""One Auto API client for premium vehicle provenance data.

Uses 3 API calls per check:
  1. Experian AutoCheck — finance, stolen, write-off, plates, keepers, high risk
  2. Brego Valuation — current market value
  3. CarGuide Salvage — unrecorded write-off detection

Sandbox: sandbox.oneautoapi.com (free, returns dummy data)
Live: api.oneautoapi.com (requires credit card, returns real data)
"""

import httpx
from datetime import date, datetime
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
        """Make a GET request and return the result dict, or None on failure.

        Every call is logged + persisted to the api_calls table so we can
        diagnose 403s (One Auto's body is where the actionable message lives).
        """
        import time
        from app.models.api_call import record_api_call

        start = time.perf_counter()
        status_code: Optional[int] = None
        error_msg: Optional[str] = None
        body_snippet: Optional[str] = None
        result: Optional[Dict] = None

        try:
            resp = await self._client.get(path, params=params)
            status_code = resp.status_code
            # Store the full response in the DB (capped at 50 KB for safety).
            # Keep the Railway log line short — full body is queryable later.
            body_snippet = resp.text[:50_000] if resp.text else None

            if resp.status_code != 200:
                error_msg = f"HTTP {resp.status_code}: {resp.text[:200]}"
                logger.error(f"One Auto {path} HTTP {resp.status_code}: {resp.text[:500]}")
                return None

            try:
                data = resp.json()
            except Exception as e:
                error_msg = f"Invalid JSON response: {e}"
                logger.error(f"One Auto {path} invalid JSON: {resp.text[:500]}")
                return None

            if data.get("success"):
                result = data.get("result")
                return result

            error_msg = data.get("result", {}).get("error") or data.get("error") or "unspecified error"
            logger.warning(f"One Auto API error on {path}: {error_msg}")
            return None

        except Exception as e:
            error_msg = str(e)
            logger.error(f"One Auto API request failed on {path}: {e}")
            return None
        finally:
            duration_ms = int((time.perf_counter() - start) * 1000)
            registration = params.get("vehicle_registration_mark") if params else None
            try:
                await record_api_call(
                    service="oneauto",
                    endpoint=path,
                    status_code=status_code,
                    duration_ms=duration_ms,
                    registration=registration,
                    error=error_msg,
                    response_body=body_snippet,
                )
            except Exception as e:
                # Never let tracking failure break the primary call
                logger.warning(f"Failed to record api_call: {e}")

    async def get_autocheck(self, registration: str) -> Optional[Dict]:
        """Experian AutoCheck — single call covering finance, stolen, write-off,
        plates, keepers, colour changes, high risk, previous searches, V5C history."""
        return await self._get(
            "/experian/autocheck/v3",
            {"vehicle_registration_mark": registration},
        )

    async def get_valuation(self, registration: str, mileage: int, registration_date: Optional[str] = None) -> Optional[Dict]:
        """Brego current & future valuations.

        Required params: vehicle_registration_mark, current_mileage, forecast_date, miles_per_annum
        Endpoint: /brego/currentandfuturevaluationsfromvrm/v2 (current + future valuations enabled on plan)
        Note: /brego/valuationfromvrm/v2 is deprecated — use currentandfuture endpoint instead.

        miles_per_annum: Calculated from registration_date to today. If not provided, defaults to 12000.
        Returns: retail_low/average/high, trade_low/average/high valuations in GBP.
        """
        # Calculate average miles per year from registration to today
        miles_per_annum = 12000  # Default fallback
        if registration_date:
            try:
                reg_date = datetime.fromisoformat(registration_date).date()
                today = date.today()
                years_owned = (today - reg_date).days / 365.25
                if years_owned > 0:
                    miles_per_annum = max(1, int(mileage / years_owned))  # Ensure >= 1
            except (ValueError, ZeroDivisionError):
                pass  # Fall back to 12000

        return await self._get(
            "/brego/currentandfuturevaluationsfromvrm/v2",
            {
                "vehicle_registration_mark": registration,
                "current_mileage": mileage,
                "forecast_date": date.today().isoformat(),
                "miles_per_annum": miles_per_annum,
            },
        )

    async def get_salvage(self, registration: str) -> Optional[Dict]:
        """CarGuide salvage auction check."""
        return await self._get(
            "/carguide/salvagecheck/v2",
            {"vehicle_registration_mark": registration},
        )

    # --- EV-specific endpoints ---

    async def get_clearwatt(self, registration: str, mileage: int) -> Optional[Dict]:
        """ClearWatt expected range from VRM — battery health + range degradation."""
        return await self._get(
            "/clearwatt/expectedrangefromvrm/",
            {"vehicle_registration_mark": registration, "current_mileage": mileage},
        )

    async def get_autopredict_predict(self, registration: str) -> Optional[Dict]:
        """AutoPredict predict — years remaining on road."""
        return await self._get(
            "/autopredict/predict/v2",
            {"vehicle_registration_mark": registration},
        )

    async def get_autopredict_statistics(self, registration: str) -> Optional[Dict]:
        """AutoPredict statistics — manufacturer/model survival data."""
        return await self._get(
            "/autopredict/statistics/v2",
            {"vehicle_registration_mark": registration},
        )

    async def get_evdb_search(self, registration: str) -> Optional[Dict]:
        """EV Database VRM search — returns evdb_vehicle_id + confidence scoring."""
        return await self._get(
            "/evdatabase/uk/searchfromvrm/",
            {"vehicle_registration_mark": registration},
        )

    async def get_evdb_coredata(self, vehicle_id: int) -> Optional[Dict]:
        """EV Database core data — battery size, availability, fuel type."""
        return await self._get(
            "/evdatabase/uk/car/coredata/",
            {"evdb_vehicle_id": vehicle_id},
        )

    async def get_evdb_range_efficiency(self, vehicle_id: int) -> Optional[Dict]:
        """EV Database range, efficiency & battery — real-world range + specs."""
        return await self._get(
            "/evdatabase/uk/car/rangeefficiencybattery/",
            {"evdb_vehicle_id": vehicle_id},
        )

    async def get_evdb_fast_charging(self, vehicle_id: int) -> Optional[Dict]:
        """EV Database fast charging — DC charge times + speeds."""
        return await self._get(
            "/evdatabase/uk/car/fastcharging/",
            {"evdb_vehicle_id": vehicle_id},
        )

    async def get_evdb_onboard_charging(self, vehicle_id: int) -> Optional[Dict]:
        """EV Database onboard charging — home charge times + speeds."""
        return await self._get(
            "/evdatabase/uk/car/onboardcharging/",
            {"evdb_vehicle_id": vehicle_id},
        )

    async def get_evdb_pence_per_mile(self, vehicle_id: int) -> Optional[Dict]:
        """EV Database pence per mile — running costs + range by weather/driving."""
        return await self._get(
            "/evdatabase/uk/car/pencepermile/",
            {"evdb_vehicle_id": vehicle_id},
        )

    async def get_evdb_vehicle_data(self, vehicle_id: int) -> Optional[Dict]:
        """EV Database vehicle data — dimensions, performance, safety."""
        return await self._get(
            "/evdatabase/uk/car/vehicledata/",
            {"evdb_vehicle_id": vehicle_id},
        )

    async def get_global_image_search(
        self,
        manufacturer_desc: str,
        model_range_desc: str,
        manufactured_year: int,
    ) -> Optional[Dict]:
        """Global image search — returns available images by angle and colour options.

        Returns: Dict with 'images' (8 angles) and 'color_list' available colours.
        """
        return await self._get(
            "/vehicleimagery/imagesearch/",
            {
                "manufacturer_desc": manufacturer_desc,
                "model_range_desc": model_range_desc,
                "manufactured_year": manufactured_year,
            },
        )

    async def close(self):
        await self._client.aclose()


# ---------------------------------------------------------------------------
# Parsers — extract structured data from AutoCheck / Brego / CarGuide
# ---------------------------------------------------------------------------


def parse_autocheck(raw: Optional[Dict], current_registration: str = "") -> Optional[Dict]:
    """Parse a single AutoCheck response into all provenance sub-dicts.

    Returns None when the upstream call failed so the email/PDF omit the
    provenance section entirely rather than asserting a false "Clear".
    `current_registration` is used by plate-change filtering to drop
    self-referential audit rows.
    """
    if raw is None:
        return None
    return {
        "finance_check": _parse_finance(raw),
        "stolen_check": _parse_stolen(raw),
        "write_off_check": _parse_condition(raw),
        "plate_changes": _parse_plate_changes(raw, current_registration),
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


def _parse_plate_changes(raw: Optional[Dict], current_registration: str = "") -> Dict:
    """Extract plate change history from AutoCheck response.

    Experian's `cherished_data_items` includes non-transfer audit rows
    (type "Marker", "Data Move", etc.) that aren't real plate changes.
    Filter those out so the customer only sees genuine transfers.

    Args:
        current_registration: the VRM this check was run for. Used to drop
            self-referential rows (Experian sometimes lists the current
            plate as a historical "previous plate" — not an actual change).
    """
    if not raw:
        return _empty_plates()

    # "Marker" rows are Experian's retrospective flag on the OTHER side of a
    # transfer — e.g. when M8OOF is put on the car, a "Marker" row is also
    # added pointing back at the original plate. Dropping these avoids
    # duplicate rows. "Data Move" entries DO represent genuine transfers
    # (confirmed against real KM55OVR data — M8OOF → KM55OVR in 2015).
    IGNORED_TYPES = {"Marker", ""}
    current = (current_registration or "").upper().replace(" ", "")

    items = raw.get("cherished_data_items") or []
    records = []
    for item in items:
        prev = item.get("previous_vehicle_registration_mark", "") or ""
        curr = item.get("current_vehicle_registration_mark", "") or ""
        transfer_type = item.get("transfer_type", "Transfer") or ""
        prev_norm = prev.upper().replace(" ", "")

        if not prev or not curr or prev == curr:
            continue
        if current and prev_norm == current:
            # Current plate showing up as a "previous" plate — not a transfer
            continue
        if transfer_type in IGNORED_TYPES:
            continue

        records.append({
            "previous_plate": prev,
            "change_date": item.get("cherished_plate_transfer_date", ""),
            "change_type": transfer_type,
        })

    return {
        "changes_found": len(records) > 0,
        "record_count": len(records),
        "records": records,
        "data_source": "Experian",
    }


_MONTHS_SHORT = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
_KEEPER_ORDINAL = {1: "First Owner", 2: "Second Owner", 3: "Third Owner",
                   4: "Fourth Owner", 5: "Fifth Owner", 6: "Sixth Owner",
                   7: "Seventh Owner", 8: "Eighth Owner", 9: "Ninth Owner"}


def _keeper_label(n: int) -> str:
    return _KEEPER_ORDINAL.get(n, f"Keeper {n}")


def _date_display(iso: Optional[str]) -> Optional[str]:
    """ISO '2020-12-09' → '9 Dec 2020'. Passes through None."""
    if not iso:
        return None
    try:
        d = date.fromisoformat(iso)
    except (ValueError, TypeError):
        return iso
    return f"{d.day} {_MONTHS_SHORT[d.month - 1]} {d.year}"


def _tenure_display(start_iso: Optional[str], end_iso: Optional[str]) -> str:
    """Return '5 years · 4 months' / '9 months' / '12 days' between two ISO dates.
    If end is None, use today (current keeper's tenure).
    """
    if not start_iso:
        return ""
    try:
        start = date.fromisoformat(start_iso)
    except (ValueError, TypeError):
        return ""
    end = date.fromisoformat(end_iso) if end_iso else date.today()
    if end < start:
        return ""

    years = end.year - start.year
    months = end.month - start.month
    days = end.day - start.day
    if days < 0:
        months -= 1
    if months < 0:
        years -= 1
        months += 12

    parts: List[str] = []
    if years:
        parts.append(f"{years} year{'s' if years != 1 else ''}")
    if months:
        parts.append(f"{months} month{'s' if months != 1 else ''}")
    if not parts:
        total_days = (end - start).days
        parts.append(f"{total_days} day{'s' if total_days != 1 else ''}")
    return " · ".join(parts)


def _parse_keepers(raw: Optional[Dict]) -> Dict:
    """Extract keeper change history from AutoCheck response.

    AutoCheck returns a list of keeper-change events (one per change). Each
    row carries the date the keeper changed. Combined with the vehicle's
    first_registration_date (top-level), we can reconstruct each keeper's
    tenure: keeper 1 = first registration → change 1, keeper 2 = change 1
    → change 2, etc. Current keeper's end is None (tenure runs to today).
    """
    if not raw:
        return {
            "keeper_count": None,
            "last_change_date": None,
            "keepers": [],
            "data_source": "Experian",
        }

    items = raw.get("keeper_data_items") or []
    first_reg = raw.get("first_registration_date") or raw.get("registration_date")

    # Sort change events oldest → newest
    change_dates = sorted(
        [it.get("date_of_last_keeper_change") for it in items if it.get("date_of_last_keeper_change")]
    )

    keepers: List[Dict] = []
    total_keepers = len(change_dates) + 1 if change_dates else 1
    for i in range(total_keepers):
        start = first_reg if i == 0 else change_dates[i - 1]
        end = change_dates[i] if i < len(change_dates) else None
        keepers.append({
            "keeper_number": i + 1,
            "start_date": start,
            "end_date": end,
            "is_current": end is None,
            "start_display": _date_display(start),
            "end_display": _date_display(end),
            "tenure_display": _tenure_display(start, end),
            "label": _keeper_label(i + 1),
        })

    # Reverse: current keeper first — matches how the email renders.
    keepers.reverse()

    return {
        "keeper_count": total_keepers,
        "last_change_date": change_dates[-1] if change_dates else None,
        "keepers": keepers,
        "data_source": "Experian",
    }


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


def parse_valuation(raw: Optional[Dict], mileage: int) -> Optional[Dict]:
    """Map Brego valuation response to our Valuation schema.

    Brego's /brego/currentandfuturevaluationsfromvrm/v2 nests the numeric
    figures inside a `valuations` array. Pre-v2 endpoints returned them at
    the top level — support both shapes defensively.
    """
    if raw is None:
        return None

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

    val_row = raw
    if isinstance(raw.get("valuations"), list) and raw["valuations"]:
        val_row = raw["valuations"][0]

    return {
        "private_sale": val_row.get("retail_average_valuation"),
        "dealer_forecourt": val_row.get("retail_high_valuation"),
        "trade_in": val_row.get("trade_average_valuation"),
        "part_exchange": val_row.get("trade_high_valuation"),
        "valuation_date": date.today().isoformat(),
        "mileage_used": val_row.get("current_mileage", mileage),
        "condition": "Mileage-adjusted",
        "data_source": "Brego",
    }


def parse_salvage(raw: Optional[Dict]) -> Optional[Dict]:
    """Map CarGuide salvage check response. None if upstream call failed."""
    if raw is None:
        return None

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
