"""EV Health Check orchestrator.

Coordinates DVLA + MOT + EV-specific API calls to produce an EV check.

Flow for free tier:
  1. Fetch DVLA VES + MOT history in parallel (reuses existing clients)
  2. Validate vehicle is electric via DVLA fuelType
  3. Run MOT analysis + ULEZ calculation
  4. Assemble EV-specific response

Flow for paid tier:
  + ClearWatt battery health + range degradation only
  + Derive battery health score and range estimate

NOTE: Currently only ClearWatt is enabled on the plan.
To get EV specs + charging costs + lifespan prediction, request plan upgrade
to include: EVDB Search + Range/Efficiency + AutoPredict endpoints.
"""

import asyncio
from datetime import datetime
from typing import Dict, List, Optional

from app.core.logging import logger
from app.core.config import settings
from app.services.check.dvla_client import DVLAClient
from app.services.mot.client import MOTClient
from app.services.mot.analyzer import MOTAnalyzer
from app.services.check.ulez import calculate_ulez_compliance
from app.services.data.tax_calculator import calculate_tax
from app.services.data.ncap_ratings import lookup_ncap_rating
from app.services.data.vehicle_stats import calculate_vehicle_stats
from app.services.data.oneauto_client import OneAutoClient
from app.schemas.check import (
    VehicleIdentity,
    MOTSummary,
    LatestTest,
    ClockingAnalysis,
    ClockingFlag,
    MileageReading,
    FailurePattern,
    ULEZCompliance,
    MOTTestRecord,
    MOTDefect,
    TaxCalculation,
    SafetyRating,
    VehicleStats,
    FinanceCheck,
    FinanceRecord,
    StolenCheck,
    WriteOffCheck,
    WriteOffRecord,
    PlateChangeHistory,
    PlateChangeRecord,
    KeeperHistory,
    HighRiskCheck,
    HighRiskRecord,
    PreviousSearches,
    PreviousSearchRecord,
    SalvageCheck,
    ImportStatusCheck,
)
from app.schemas.ev import (
    EVCheckResponse,
    RangeEstimate,
    RangeScenario,
    EVSpecs,
    LifespanPrediction,
    BatteryHealth,
    ChargingCosts,
)


# Fuel types that indicate an electric or plug-in hybrid vehicle
EV_FUEL_TYPES = {"ELECTRICITY"}
PHEV_FUEL_TYPES = {"ELECTRIC DIESEL", "ELECTRIC PETROL"}
ALL_EV_FUEL_TYPES = EV_FUEL_TYPES | PHEV_FUEL_TYPES


def classify_ev(fuel_type: Optional[str]) -> Optional[str]:
    """Classify a DVLA fuelType as BEV, PHEV, or None."""
    if not fuel_type:
        return None
    upper = fuel_type.upper().strip()
    if upper in EV_FUEL_TYPES:
        return "BEV"
    if upper in PHEV_FUEL_TYPES:
        return "PHEV"
    return None


class EVOrchestrator:
    """Coordinates all services to produce an EV health check."""

    def __init__(self):
        self.dvla_client = DVLAClient()
        self.mot_client = MOTClient()
        self.mot_analyzer = MOTAnalyzer()
        self.oneauto_client = OneAutoClient() if settings.ONEAUTO_API_KEY else None

    async def run_ev_check(self, registration: str, tier: str = "ev_free") -> EVCheckResponse:
        """Execute an EV check.

        tier="ev_free": DVLA + MOT only (validates EV, shows basic data)
        tier="ev_health": + ClearWatt + Range & Pence Per Mile (battery health + charging costs)
        tier="ev_complete": + AutoCheck + Salvage Check (full vehicle history)
        """
        clean_reg = registration.upper().replace(" ", "")
        logger.info(f"Starting {tier} EV check for {clean_reg}")

        # Step 1: Fetch DVLA + MOT in parallel
        dvla_data, mot_data = await asyncio.gather(
            self.dvla_client.get_vehicle(clean_reg),
            self.mot_client.get_mot_history(clean_reg),
            return_exceptions=True,
        )

        if isinstance(dvla_data, Exception):
            logger.error(f"DVLA fetch failed: {dvla_data}")
            dvla_data = None
        if isinstance(mot_data, Exception):
            logger.error(f"MOT fetch failed: {mot_data}")
            mot_data = None

        # Step 2: Classify EV type from DVLA fuel type
        fuel_type = dvla_data.get("fuelType") if dvla_data else None
        ev_type = classify_ev(fuel_type)
        is_electric = ev_type is not None

        # Step 3: Analyze MOT data
        mot_analysis = self.mot_analyzer.analyze(mot_data)
        ulez_result = calculate_ulez_compliance(dvla_data)

        # Store raw data for downstream parsers
        self._raw_dvla_data = dvla_data
        self._raw_mot_analysis = mot_analysis
        self._raw_ulez_data = ulez_result

        # Step 4: Build data sources list
        data_sources = []
        if dvla_data:
            data_sources.append("DVLA VES API")
        if mot_data:
            data_sources.append("DVSA MOT History API")

        # Step 5: Build base vehicle data (same as car check)
        vehicle = self._build_vehicle_identity(dvla_data)
        mot_summary = self._build_mot_summary(mot_analysis.get("mot_summary"))
        clocking = self._build_clocking_analysis(mot_analysis.get("clocking_analysis"))
        mileage_timeline = [
            MileageReading(**r) for r in mot_analysis.get("mileage_timeline", [])
        ]
        failure_patterns = [
            FailurePattern(**p) for p in mot_analysis.get("failure_patterns", [])
        ]
        ulez_compliance = ULEZCompliance(**ulez_result)
        mot_tests = self._build_mot_test_records(mot_analysis.get("mot_tests", []))
        tax_calculation = self._build_tax_calculation(dvla_data)
        safety_rating = self._build_safety_rating(dvla_data, mot_analysis.get("mot_summary"))
        raw_tests = mot_analysis.get("raw_tests", [])
        vehicle_stats = self._build_vehicle_stats(
            dvla_data, raw_tests, mot_analysis.get("mileage_timeline", [])
        )

        # Step 6: Paid tiers — fetch EV-specific and/or provenance data
        range_estimate = None
        range_scenarios = []
        battery_health = None
        charging_costs = None

        # EV Health data (both ev_health and ev_complete tiers)
        if tier in ("ev_health", "ev_complete") and is_electric and self.oneauto_client:
            ev_data = await self._fetch_ev_data(clean_reg)
            if ev_data:
                range_estimate = ev_data.get("range_estimate")
                range_scenarios = ev_data.get("range_scenarios", [])
                battery_health = ev_data.get("battery_health")
                charging_costs = ev_data.get("charging_costs")
                if range_estimate:
                    data_sources.append("ClearWatt")

        # Vehicle history data (ev_complete tier only)
        provenance = None
        current_mileage = None
        if tier == "ev_complete" and self.oneauto_client:
            if (mot_analysis.get("mot_summary") or {}).get("current_odometer"):
                try:
                    current_mileage = int(mot_analysis["mot_summary"]["current_odometer"])
                except (ValueError, TypeError):
                    pass
            provenance = await self._fetch_provenance_data(clean_reg, current_mileage)
            if provenance:
                data_sources.append(provenance.pop("_source", "Provenance Check"))

        response = EVCheckResponse(
            registration=clean_reg,
            tier=tier,
            is_electric=is_electric,
            ev_type=ev_type,
            vehicle=vehicle,
            mot_summary=mot_summary,
            mot_tests=mot_tests,
            clocking_analysis=clocking,
            condition_score=mot_analysis.get("condition_score"),
            mileage_timeline=mileage_timeline,
            failure_patterns=failure_patterns,
            ulez_compliance=ulez_compliance,
            tax_calculation=tax_calculation,
            safety_rating=safety_rating,
            vehicle_stats=vehicle_stats,
            range_estimate=range_estimate,
            range_scenarios=range_scenarios,
            battery_health=battery_health,
            charging_costs=charging_costs,
            finance_check=provenance.get("finance_check") if provenance else None,
            stolen_check=provenance.get("stolen_check") if provenance else None,
            write_off_check=provenance.get("write_off_check") if provenance else None,
            plate_changes=provenance.get("plate_changes") if provenance else None,
            keeper_history=provenance.get("keeper_history") if provenance else None,
            high_risk=provenance.get("high_risk") if provenance else None,
            previous_searches=provenance.get("previous_searches") if provenance else None,
            salvage_check=provenance.get("salvage_check") if provenance else None,
            import_status=self._build_import_status(provenance, dvla_data),
            valuation=provenance.get("valuation") if provenance else None,
            checked_at=datetime.utcnow(),
            data_sources=data_sources,
        )

        logger.info(f"EV check completed for {clean_reg} (electric={is_electric}, type={ev_type})")
        return response

    def _get_current_mileage(self) -> Optional[int]:
        """Get current mileage from MOT data for ClearWatt API."""
        if not self._raw_mot_analysis:
            return None
        summary = self._raw_mot_analysis.get("mot_summary")
        if summary and summary.get("current_odometer"):
            try:
                return int(summary["current_odometer"])
            except (ValueError, TypeError):
                pass
        timeline = self._raw_mot_analysis.get("mileage_timeline", [])
        if timeline:
            return timeline[-1].get("miles")
        return None

    async def _fetch_ev_data(self, registration: str) -> Optional[Dict]:
        """Fetch ClearWatt battery health + Range & Pence Per Mile charging costs.

        NOTE: Currently only ClearWatt and Range & Pence Per Mile are enabled on the plan.
        To enable additional specs, request plan upgrade to include:
        EVDB Search + Range/Efficiency + AutoPredict.
        """
        try:
            mileage = self._get_current_mileage()
            if not mileage:
                logger.warning(f"Cannot fetch ClearWatt without mileage for {registration}")
                return None

            # Fetch both ClearWatt and Range & Pence Per Mile in parallel
            clearwatt_raw = await self.oneauto_client.get_clearwatt(registration, mileage)
            ppm_raw = await self.oneauto_client.get_evdb_pence_per_mile(registration)

            return self._parse_ev_data(clearwatt_raw=clearwatt_raw, ppm_raw=ppm_raw)

        except Exception as e:
            logger.error(f"EV data fetch failed: {e}")
            return None

    async def _fetch_provenance_data(self, registration: str, current_mileage: Optional[int] = None) -> Optional[Dict]:
        """Fetch AutoCheck + Brego valuation + Salvage Check for vehicle history."""
        try:
            # Fetch AutoCheck first (need registration_date for Brego)
            autocheck_raw = await self.oneauto_client.get_autocheck(registration)

            if isinstance(autocheck_raw, Exception):
                logger.warning(f"One Auto AutoCheck failed: {autocheck_raw}")
                autocheck_raw = None

            # Extract registration date for Brego valuation
            registration_date = None
            if isinstance(autocheck_raw, dict) and autocheck_raw.get("registration_date"):
                registration_date = autocheck_raw["registration_date"]

            # Fetch valuation + salvage in parallel
            valuation_raw, salvage_raw = await asyncio.gather(
                self.oneauto_client.get_valuation(registration, current_mileage or 0, registration_date),
                self.oneauto_client.get_salvage(registration),
                return_exceptions=True,
            )

            if isinstance(valuation_raw, Exception):
                logger.warning(f"One Auto Brego valuation failed: {valuation_raw}")
                valuation_raw = None
            if isinstance(salvage_raw, Exception):
                logger.warning(f"One Auto Salvage check failed: {salvage_raw}")
                salvage_raw = None

            from app.services.data.oneauto_client import parse_autocheck, parse_salvage, parse_valuation

            parsed = parse_autocheck(autocheck_raw)
            parsed["valuation"] = parse_valuation(valuation_raw, current_mileage or 0)
            parsed["salvage_check"] = parse_salvage(salvage_raw)

            return self._build_provenance_from_raw(parsed, "Experian via One Auto API")

        except Exception as e:
            logger.error(f"Provenance data fetch failed: {e}")
            return None

    def _build_provenance_from_raw(self, raw: Optional[Dict], source: str) -> Optional[Dict]:
        """Convert raw provenance dict into typed schema objects."""
        if not raw:
            return None

        result = {"_source": source}

        fc = raw.get("finance_check")
        if fc:
            records = [FinanceRecord(**r) for r in fc.get("records", [])]
            result["finance_check"] = FinanceCheck(
                finance_outstanding=fc["finance_outstanding"],
                record_count=fc.get("record_count", 0),
                records=records,
                data_source=fc.get("data_source", source),
            )

        sc = raw.get("stolen_check")
        if sc:
            result["stolen_check"] = StolenCheck(**sc)

        wc = raw.get("write_off_check")
        if wc:
            records = [WriteOffRecord(**r) for r in wc.get("records", [])]
            result["write_off_check"] = WriteOffCheck(
                written_off=wc["written_off"],
                record_count=wc.get("record_count", 0),
                records=records,
                data_source=wc.get("data_source", source),
            )

        pc = raw.get("plate_changes")
        if pc:
            records = [PlateChangeRecord(**r) for r in pc.get("records", [])]
            result["plate_changes"] = PlateChangeHistory(
                changes_found=pc["changes_found"],
                record_count=pc.get("record_count", 0),
                records=records,
                data_source=pc.get("data_source", source),
            )

        kh = raw.get("keeper_history")
        if kh:
            result["keeper_history"] = KeeperHistory(**kh)

        hr = raw.get("high_risk")
        if hr:
            records = [HighRiskRecord(**r) for r in hr.get("records", [])]
            result["high_risk"] = HighRiskCheck(
                flagged=hr.get("flagged", False),
                records=records,
                data_source=hr.get("data_source", source),
            )

        ps = raw.get("previous_searches")
        if ps:
            records = [PreviousSearchRecord(**r) for r in ps.get("records", [])]
            result["previous_searches"] = PreviousSearches(
                search_count=ps.get("search_count", 0),
                records=records,
                data_source=ps.get("data_source", source),
            )

        sv = raw.get("salvage_check")
        if sv:
            result["salvage_check"] = SalvageCheck(
                salvage_found=sv.get("salvage_found", False),
                records=sv.get("records", []),
                data_source=sv.get("data_source", "CarGuide"),
            )

        val = raw.get("valuation")
        if val:
            from app.schemas.check import Valuation
            result["valuation"] = Valuation(**val)

        return result

    def _parse_ev_data(
        self,
        clearwatt_raw: Optional[Dict],
        ppm_raw: Optional[Dict] = None,
    ) -> Dict:
        """Parse ClearWatt + Range & Pence Per Mile data into typed schema objects."""
        result = {}

        # --- ClearWatt: battery health + range degradation ---
        if clearwatt_raw:
            vehicle_info = clearwatt_raw.get("vehicle_info", {})
            range_new = clearwatt_raw.get("benchmark_real_electric_range_new", {})
            range_now = clearwatt_raw.get("expected_real_electric_range_now", {})
            warranty = clearwatt_raw.get("remaining_battery_warranty", {})
            battery_test = clearwatt_raw.get("battery_health_test_result", {})

            min_now = range_now.get("min_range_miles")
            max_now = range_now.get("max_range_miles")
            min_new = range_new.get("min_range_miles")
            max_new = range_new.get("max_range_miles")

            # Calculate estimated range as midpoint of now range
            estimated = round((min_now + max_now) / 2) if min_now and max_now else None

            # Calculate retention: midpoint_now / midpoint_new * 100
            retention = None
            if min_now and max_now and min_new and max_new:
                mid_now = (min_now + max_now) / 2
                mid_new = (min_new + max_new) / 2
                if mid_new > 0:
                    retention = round(mid_now / mid_new * 100, 1)

            result["range_estimate"] = RangeEstimate(
                estimated_range_miles=estimated,
                min_range_now_miles=min_now,
                max_range_now_miles=max_now,
                min_range_new_miles=min_new,
                max_range_new_miles=max_new,
                official_range_miles=vehicle_info.get("wltp_pure_electric_range_combined_miles_test_energy_low"),
                range_retention_pct=retention,
                warranty_miles_remaining=warranty.get("miles"),
                warranty_months_remaining=warranty.get("months"),
                battery_test_available=battery_test.get("is_record_available", False),
                battery_test_date=battery_test.get("test_date"),
                battery_test_grade=battery_test.get("test_result_grade"),
                battery_capacity_kwh=vehicle_info.get("battery_capacity_kwh"),
                usable_battery_capacity_kwh=vehicle_info.get("usable_battery_capacity_kwh"),
            )

        # --- Range scenarios from Range & Pence Per Mile (9 weather/driving combos) ---
        if ppm_raw:
            range_from_ppm = ppm_raw.get("range_data", {})
            scenarios = []
            scenario_map = [
                ("Highway Cold (-10°C)", -10, "highway", "evdb_real_electric_range_highway_cold_miles"),
                ("Combined Cold (-10°C)", -10, "combined", "evdb_real_electric_range_combined_cold_miles"),
                ("City Cold (-10°C)", -10, "city", "evdb_real_electric_range_city_cold_miles"),
                ("Highway Mild (10°C)", 10, "highway", "evdb_real_electric_range_highway_mild_miles"),
                ("Combined Mild (10°C)", 10, "combined", "evdb_real_electric_range_combined_mild_miles"),
                ("City Mild (10°C)", 10, "city", "evdb_real_electric_range_city_mild_miles"),
                ("Highway Warm (23°C)", 23, "highway", "evdb_real_electric_range_highway_warm_miles"),
                ("Combined Warm (23°C)", 23, "combined", "evdb_real_electric_range_combined_warm_miles"),
                ("City Warm (23°C)", 23, "city", "evdb_real_electric_range_city_warm_miles"),
            ]
            for name, temp, style, key in scenario_map:
                miles = range_from_ppm.get(key)
                if miles is not None:
                    scenarios.append(RangeScenario(
                        scenario=name,
                        temperature_c=temp,
                        estimated_miles=miles,
                        driving_style=style,
                    ))
            if scenarios:
                result["range_scenarios"] = scenarios

        # --- Charging costs from Range & Pence Per Mile ---
        if ppm_raw:
            result["charging_costs"] = self._calculate_charging_costs_from_ppm(ppm_raw)

        # --- Derive battery health from ClearWatt ---
        result["battery_health"] = self._derive_battery_health(clearwatt_raw)

        return result

    def _calculate_charging_costs_from_ppm(self, ppm_raw: Dict) -> ChargingCosts:
        """Calculate charging costs from Range & Pence Per Mile data."""
        PETROL_PPM = 15.0  # pence per mile for avg petrol car
        ANNUAL_MILES = 10000

        # Use combined mild pence per mile (most representative UK condition)
        ppm_data = ppm_raw.get("pence_per_mile_data", {})
        combined_mild = ppm_data.get("pence_per_mile_combined_mild", {})

        cpm_home = combined_mild.get("domestic_standard")  # standard home tariff
        cpm_cheap = combined_mild.get("domestic_cheap")  # cheap tariff
        cpm_public = combined_mild.get("public_charger")  # public charger

        # Unit costs for full charge calculation
        unit_costs = ppm_raw.get("unit_costs", {})
        electric_details = unit_costs.get("pence_per_kwh_electric_details", {})
        home_rate_ppk = electric_details.get("domestic_standard", 34)
        cheap_rate_ppk = electric_details.get("domestic_cheap", 7.5)
        public_rate_ppk = electric_details.get("public_charger", 85)

        # Estimate annual costs
        annual_home = round(cpm_home * ANNUAL_MILES / 100, 2) if cpm_home else None
        annual_cheap = round(cpm_cheap * ANNUAL_MILES / 100, 2) if cpm_cheap else None
        annual_public = round(cpm_public * ANNUAL_MILES / 100, 2) if cpm_public else None

        petrol_annual = PETROL_PPM * ANNUAL_MILES / 100
        saving = round(petrol_annual - annual_home, 2) if annual_home else None

        return ChargingCosts(
            home_cost_per_full_charge=None,  # PPM doesn't provide battery capacity
            rapid_cost_per_full_charge=None,
            cost_per_mile_home=cpm_home,
            cost_per_mile_rapid=cpm_public,  # public = rapid
            cost_per_mile_public=cpm_public,
            annual_cost_estimate_home=annual_home,
            annual_cost_estimate_rapid=annual_public,
            vs_petrol_annual_saving=saving,
        )

    def _derive_battery_health(
        self,
        clearwatt_raw: Optional[Dict],
    ) -> BatteryHealth:
        """Derive battery health score from ClearWatt range data."""
        if not clearwatt_raw:
            return BatteryHealth(summary="No battery data available")

        range_new = clearwatt_raw.get("benchmark_real_electric_range_new", {})
        range_now = clearwatt_raw.get("expected_real_electric_range_now", {})
        battery_test = clearwatt_raw.get("battery_health_test_result", {})

        min_now = range_now.get("min_range_miles")
        max_now = range_now.get("max_range_miles")
        min_new = range_new.get("min_range_miles")
        max_new = range_new.get("max_range_miles")

        # Calculate retention percentage
        retention = None
        if min_now and max_now and min_new and max_new:
            mid_now = (min_now + max_now) / 2
            mid_new = (min_new + max_new) / 2
            if mid_new > 0:
                retention = mid_now / mid_new * 100

        if retention is None:
            return BatteryHealth(summary="Insufficient range data for health assessment")

        # Score: retention percentage mapped to 0-100
        score = min(100, max(0, int(retention)))

        # Grade based on retention
        if score >= 90:
            grade = "A"
            summary = "Excellent battery health — minimal degradation detected"
        elif score >= 80:
            grade = "B"
            summary = "Good battery health — normal age-related degradation"
        elif score >= 70:
            grade = "C"
            summary = "Fair battery health — moderate degradation, still serviceable"
        elif score >= 60:
            grade = "D"
            summary = "Below average — significant degradation, reduced range expected"
        else:
            grade = "F"
            summary = "Poor battery health — substantial degradation, replacement may be needed"

        degradation = round(100.0 - retention, 1)

        # Use ClearWatt battery test grade if available
        test_grade = battery_test.get("test_result_grade") if battery_test.get("is_record_available") else None
        test_date = battery_test.get("test_date") if battery_test.get("is_record_available") else None

        return BatteryHealth(
            score=score,
            grade=grade,
            degradation_estimate_pct=degradation,
            summary=summary,
            test_grade=test_grade,
            test_date=test_date,
        )

    # NOTE: Charging cost calculation methods removed — EV Database endpoints not enabled on plan.
    # To re-enable: request plan upgrade to include EVDB Range, Efficiency, and Pence Per Mile endpoints.

    def _calculate_charging_costs_from_evdb(self, ppm_raw: Dict, evdb_data: Dict) -> ChargingCosts:
        """Calculate charging costs using real EV Database pence per mile data."""
        PETROL_PPM = 15.0  # pence per mile for avg petrol car
        ANNUAL_MILES = 10000

        # Use combined mild pence per mile (most representative UK condition)
        ppm_data = ppm_raw.get("pence_per_mile_data", {})
        combined_mild = ppm_data.get("pence_per_mile_combined_mild", {})

        cpm_home = combined_mild.get("domestic_standard")  # standard home tariff
        cpm_rapid = None  # EVDB doesn't have a "rapid" rate — use public charger
        cpm_public = combined_mild.get("public_charger")

        # Get usable capacity for full charge cost calculation
        unit_costs = ppm_raw.get("unit_costs", {})
        electric_details = unit_costs.get("pence_per_kwh_electric_details", {})
        home_rate_ppk = electric_details.get("domestic_standard", 24.5)
        rapid_rate_ppk = electric_details.get("public_charger", 65.0)

        # Get usable kWh from range/efficiency data
        range_raw = evdb_data.get("range")
        usable_kwh = None
        if range_raw:
            battery = range_raw.get("battery", {})
            usable_kwh = battery.get("battery_capacity_usable_kwh")

        home_full = round(usable_kwh * home_rate_ppk / 100, 2) if usable_kwh else None
        rapid_full = round(usable_kwh * rapid_rate_ppk / 100, 2) if usable_kwh else None

        annual_home = round(cpm_home * ANNUAL_MILES / 100, 2) if cpm_home else None
        annual_rapid = round(cpm_public * ANNUAL_MILES / 100, 2) if cpm_public else None

        petrol_annual = PETROL_PPM * ANNUAL_MILES / 100
        saving = round(petrol_annual - annual_home, 2) if annual_home else None

        return ChargingCosts(
            home_cost_per_full_charge=home_full,
            rapid_cost_per_full_charge=rapid_full,
            cost_per_mile_home=cpm_home,
            cost_per_mile_rapid=cpm_rapid,
            cost_per_mile_public=cpm_public,
            annual_cost_estimate_home=annual_home,
            annual_cost_estimate_rapid=annual_rapid,
            vs_petrol_annual_saving=saving,
        )

    def _calculate_charging_costs_from_specs(
        self, range_raw: Optional[Dict], onboard_raw: Optional[Dict]
    ) -> ChargingCosts:
        """Fallback: estimate charging costs from specs when pence per mile endpoint failed."""
        HOME_RATE_PPK = 24.5
        RAPID_RATE_PPK = 65.0
        PETROL_PPM = 15.0
        ANNUAL_MILES = 10000

        usable_kwh = None
        consumption_wh = None
        if range_raw:
            battery = range_raw.get("battery", {})
            efficiency = range_raw.get("efficiency", {})
            usable_kwh = battery.get("battery_capacity_usable_kwh")
            consumption_wh = efficiency.get("real_electric_consumption_watt_hours_per_mile")

        home_full = round(usable_kwh * HOME_RATE_PPK / 100, 2) if usable_kwh else None
        rapid_full = round(usable_kwh * RAPID_RATE_PPK / 100, 2) if usable_kwh else None

        cpm_home = round(consumption_wh / 1000 * HOME_RATE_PPK, 2) if consumption_wh else None
        cpm_rapid = round(consumption_wh / 1000 * RAPID_RATE_PPK, 2) if consumption_wh else None

        annual_home = round(cpm_home * ANNUAL_MILES / 100, 2) if cpm_home else None
        annual_rapid = round(cpm_rapid * ANNUAL_MILES / 100, 2) if cpm_rapid else None

        petrol_annual = PETROL_PPM * ANNUAL_MILES / 100
        saving = round(petrol_annual - annual_home, 2) if annual_home else None

        return ChargingCosts(
            home_cost_per_full_charge=home_full,
            rapid_cost_per_full_charge=rapid_full,
            cost_per_mile_home=cpm_home,
            cost_per_mile_rapid=cpm_rapid,
            annual_cost_estimate_home=annual_home,
            annual_cost_estimate_rapid=annual_rapid,
            vs_petrol_annual_saving=saving,
        )

    # --- Builder methods (mirrors CheckOrchestrator exactly) ---

    def _build_import_status(
        self,
        provenance: Optional[Dict],
        dvla_data: Optional[Dict],
    ) -> Optional[ImportStatusCheck]:
        """Merge AutoCheck is_imported/is_exported with DVLA marked_for_export.

        Returns None if neither source has data so the UI hides the card.
        """
        autocheck = provenance.get("import_status") if provenance else None
        dvla_export = bool(dvla_data.get("markedForExport")) if dvla_data else False

        if not autocheck and not dvla_data:
            return None

        return ImportStatusCheck(
            is_imported=bool(autocheck.get("is_imported")) if autocheck else False,
            is_exported=bool(autocheck.get("is_exported")) if autocheck else False,
            marked_for_export=dvla_export,
            data_source="Experian + DVLA" if autocheck else "DVLA",
        )

    def _build_vehicle_identity(self, dvla_data: Optional[Dict]) -> Optional[VehicleIdentity]:
        if not dvla_data:
            return None
        return VehicleIdentity(
            registration=dvla_data.get("registrationNumber"),
            make=dvla_data.get("make"),
            colour=dvla_data.get("colour"),
            fuel_type=dvla_data.get("fuelType"),
            year_of_manufacture=dvla_data.get("yearOfManufacture"),
            engine_capacity=dvla_data.get("engineCapacity"),
            co2_emissions=dvla_data.get("co2Emissions"),
            euro_status=dvla_data.get("euroStatus"),
            tax_status=dvla_data.get("taxStatus"),
            tax_due_date=dvla_data.get("taxDueDate"),
            mot_status=dvla_data.get("motStatus"),
            mot_expiry_date=dvla_data.get("motExpiryDate"),
            date_of_last_v5c_issued=dvla_data.get("dateOfLastV5CIssued"),
            marked_for_export=dvla_data.get("markedForExport"),
            type_approval=dvla_data.get("typeApproval"),
            wheelplan=dvla_data.get("wheelplan"),
        )

    def _build_mot_summary(self, summary_data: Optional[Dict]) -> Optional[MOTSummary]:
        if not summary_data:
            return None
        latest = summary_data.get("latest_test")
        latest_test = LatestTest(**latest) if latest else None
        return MOTSummary(
            total_tests=summary_data.get("total_tests", 0),
            total_passes=summary_data.get("total_passes", 0),
            total_failures=summary_data.get("total_failures", 0),
            registration=summary_data.get("registration"),
            make=summary_data.get("make"),
            model=summary_data.get("model"),
            first_used_date=summary_data.get("first_used_date"),
            latest_test=latest_test,
            current_odometer=summary_data.get("current_odometer"),
            has_outstanding_recall=summary_data.get("has_outstanding_recall"),
        )

    def _build_clocking_analysis(self, clocking_data: Optional[Dict]) -> Optional[ClockingAnalysis]:
        if not clocking_data:
            return None
        flags = [ClockingFlag(**f) for f in clocking_data.get("flags", [])]
        return ClockingAnalysis(
            clocked=clocking_data.get("clocked", False),
            risk_level=clocking_data.get("risk_level", "unknown"),
            reason=clocking_data.get("reason"),
            flags=flags,
        )

    def _build_mot_test_records(self, tests_data: List[Dict]) -> List[MOTTestRecord]:
        records = []
        for t in tests_data:
            advisories = [MOTDefect(**a) for a in t.get("advisories", [])]
            failures = [MOTDefect(**f) for f in t.get("failures", [])]
            dangerous = [MOTDefect(**d) for d in t.get("dangerous", [])]
            records.append(MOTTestRecord(
                test_number=t.get("test_number", 0),
                test_id=t.get("test_id", ""),
                date=t.get("date", ""),
                result=t.get("result", ""),
                odometer=t.get("odometer"),
                odometer_unit=t.get("odometer_unit", "mi"),
                expiry_date=t.get("expiry_date"),
                advisories=advisories,
                failures=failures,
                dangerous=dangerous,
                total_defects=t.get("total_defects", 0),
            ))
        return records

    def _build_tax_calculation(self, dvla_data: Optional[Dict]) -> Optional[TaxCalculation]:
        if not dvla_data:
            return None
        result = calculate_tax(
            dvla_data.get("co2Emissions"),
            dvla_data.get("fuelType"),
        )
        if not result:
            return None
        return TaxCalculation(**result)

    def _build_safety_rating(self, dvla_data: Optional[Dict], mot_summary: Optional[Dict]) -> Optional[SafetyRating]:
        make = dvla_data.get("make") if dvla_data else None
        model = mot_summary.get("model") if mot_summary else None
        if not make or not model:
            return None
        result = lookup_ncap_rating(make, model)
        if not result:
            return None
        return SafetyRating(**result)

    def _build_vehicle_stats(
        self,
        dvla_data: Optional[Dict],
        raw_tests: List[Dict],
        mileage_timeline: List[Dict],
    ) -> Optional[VehicleStats]:
        stats = calculate_vehicle_stats(dvla_data, raw_tests, mileage_timeline)
        if not stats:
            return None
        return VehicleStats(**stats)

    async def close(self):
        tasks = [self.dvla_client.close(), self.mot_client.close()]
        if self.oneauto_client:
            tasks.append(self.oneauto_client.close())
        await asyncio.gather(*tasks)
