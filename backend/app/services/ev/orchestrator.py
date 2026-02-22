"""EV Health Check orchestrator.

Coordinates DVLA + MOT + EV-specific API calls to produce an EV check.

Flow for free tier:
  1. Fetch DVLA VES + MOT history in parallel (reuses existing clients)
  2. Validate vehicle is electric via DVLA fuelType
  3. Run MOT analysis + ULEZ calculation
  4. Assemble EV-specific response

Flow for paid tier:
  + ClearWatt range + EV Database specs + AutoPredict lifespan in parallel
  + Derive battery health score + charging costs
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
        tier="ev_paid": + ClearWatt + EV Database + AutoPredict
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

        # Store raw data for AI report generator
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

        # Step 6: Paid tier — fetch EV-specific data
        range_estimate = None
        range_scenarios = []
        ev_specs = None
        lifespan_prediction = None
        battery_health = None
        charging_costs = None

        if tier == "ev_paid" and is_electric and self.oneauto_client:
            ev_data = await self._fetch_ev_data(clean_reg)
            if ev_data:
                range_estimate = ev_data.get("range_estimate")
                range_scenarios = ev_data.get("range_scenarios", [])
                ev_specs = ev_data.get("ev_specs")
                lifespan_prediction = ev_data.get("lifespan_prediction")
                battery_health = ev_data.get("battery_health")
                charging_costs = ev_data.get("charging_costs")
                if range_estimate:
                    data_sources.append("ClearWatt")
                if ev_specs:
                    data_sources.append("EV Database")
                if lifespan_prediction:
                    data_sources.append("AutoPredict")

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
            ev_specs=ev_specs,
            lifespan_prediction=lifespan_prediction,
            battery_health=battery_health,
            charging_costs=charging_costs,
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
        """Fetch ClearWatt + EV Database + AutoPredict.

        Two-phase approach:
          Phase 1 (parallel): ClearWatt + AutoPredict (predict + stats) + EVDB VRM search
          Phase 2 (parallel, needs evdb_vehicle_id): EVDB data endpoints
        """
        try:
            mileage = self._get_current_mileage()

            # Phase 1: All VRM-based calls in parallel
            tasks = {
                "autopredict_predict": self.oneauto_client.get_autopredict_predict(registration),
                "autopredict_stats": self.oneauto_client.get_autopredict_statistics(registration),
                "evdb_search": self.oneauto_client.get_evdb_search(registration),
            }
            # ClearWatt requires mileage — skip if unavailable
            if mileage:
                tasks["clearwatt"] = self.oneauto_client.get_clearwatt(registration, mileage)

            keys = list(tasks.keys())
            results = await asyncio.gather(*tasks.values(), return_exceptions=True)
            phase1 = {}
            for key, result in zip(keys, results):
                if isinstance(result, Exception):
                    logger.warning(f"{key} failed: {result}")
                    phase1[key] = None
                else:
                    phase1[key] = result

            # Phase 2: EVDB data endpoints (need evdb_vehicle_id from search)
            evdb_data = {}
            evdb_vehicle_id = self._extract_evdb_vehicle_id(phase1.get("evdb_search"))
            if evdb_vehicle_id:
                evdb_tasks = {
                    "range": self.oneauto_client.get_evdb_range_efficiency(evdb_vehicle_id),
                    "fast_charging": self.oneauto_client.get_evdb_fast_charging(evdb_vehicle_id),
                    "onboard_charging": self.oneauto_client.get_evdb_onboard_charging(evdb_vehicle_id),
                    "pence_per_mile": self.oneauto_client.get_evdb_pence_per_mile(evdb_vehicle_id),
                    "vehicle_data": self.oneauto_client.get_evdb_vehicle_data(evdb_vehicle_id),
                }
                evdb_keys = list(evdb_tasks.keys())
                evdb_results = await asyncio.gather(*evdb_tasks.values(), return_exceptions=True)
                for key, result in zip(evdb_keys, evdb_results):
                    if isinstance(result, Exception):
                        logger.warning(f"EVDB {key} failed: {result}")
                        evdb_data[key] = None
                    else:
                        evdb_data[key] = result

            return self._parse_ev_data(
                clearwatt_raw=phase1.get("clearwatt"),
                autopredict_predict_raw=phase1.get("autopredict_predict"),
                autopredict_stats_raw=phase1.get("autopredict_stats"),
                evdb_search_raw=phase1.get("evdb_search"),
                evdb_data=evdb_data,
            )
        except Exception as e:
            logger.error(f"EV data fetch failed: {e}")
            return None

    def _extract_evdb_vehicle_id(self, search_raw: Optional[Dict]) -> Optional[int]:
        """Extract the best-matching evdb_vehicle_id from EVDB search results."""
        if not search_raw:
            return None
        results = search_raw.get("evdb_results", [])
        if not results:
            return None
        # Pick the result with highest overall confidence score
        best = max(results, key=lambda r: (r.get("confidence_scoring", {}).get("overall_score", 0)))
        vehicle_id = best.get("evdb_vehicle_id")
        if vehicle_id:
            logger.info(
                f"EVDB matched vehicle_id={vehicle_id} "
                f"({best.get('manufacturer_desc')} {best.get('model_range_desc')} {best.get('derivative_desc')}, "
                f"confidence={best.get('confidence_scoring', {}).get('overall_score')})"
            )
        return vehicle_id

    def _parse_ev_data(
        self,
        clearwatt_raw: Optional[Dict],
        autopredict_predict_raw: Optional[Dict],
        autopredict_stats_raw: Optional[Dict],
        evdb_search_raw: Optional[Dict],
        evdb_data: Dict,
    ) -> Dict:
        """Parse real One Auto API responses into typed schema objects."""
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

        # --- EV Database: specs, range scenarios, charging ---
        evdb_range = evdb_data.get("range")
        evdb_fast = evdb_data.get("fast_charging")
        evdb_onboard = evdb_data.get("onboard_charging")
        evdb_ppm = evdb_data.get("pence_per_mile")
        evdb_vehicle = evdb_data.get("vehicle_data")

        if any([evdb_range, evdb_fast, evdb_onboard, evdb_vehicle]):
            range_data = (evdb_range or {}).get("range", {})
            efficiency_data = (evdb_range or {}).get("efficiency", {})
            battery_data = (evdb_range or {}).get("battery", {})
            performance_data = (evdb_vehicle or {}).get("drivetrain_performance", {})
            dimensions_data = (evdb_vehicle or {}).get("dimensions_weights", {})

            result["ev_specs"] = EVSpecs(
                # Battery
                battery_capacity_kwh=battery_data.get("battery_capacity_kwh") if battery_data else None,
                usable_capacity_kwh=battery_data.get("battery_capacity_usable_kwh") if battery_data else None,
                battery_type=battery_data.get("battery_type"),
                battery_chemistry=battery_data.get("battery_chemistry"),
                battery_architecture=battery_data.get("battery_architecture"),
                battery_weight_kg=battery_data.get("battery_weight_kg"),
                battery_warranty_years=battery_data.get("battery_warranty_years"),
                battery_warranty_miles=battery_data.get("battery_warranty_mileage"),
                # Charging
                charge_port=(evdb_onboard or {}).get("charge_port_type"),
                fast_charge_port=(evdb_fast or {}).get("fast_charger_port_type"),
                max_dc_charge_kw=(evdb_fast or {}).get("fast_charger_max_power_kw"),
                avg_dc_charge_kw=(evdb_fast or {}).get("fast_charger_average_power_kw"),
                max_ac_charge_kw=(evdb_onboard or {}).get("standard_onboard_charger_max_power_kw"),
                charge_time_home_mins=(evdb_onboard or {}).get("standard_onboard_charger_chargetime_0to100_percent_minutes"),
                charge_time_rapid_mins=(evdb_fast or {}).get("fast_charger_chargetime_10to80_percent_mins"),
                rapid_charge_speed_mph=(evdb_fast or {}).get("fast_charger_chargespeed_10to80_percent_mph"),
                # Efficiency
                energy_consumption_wh_per_mile=efficiency_data.get("real_electric_consumption_watt_hours_per_mile"),
                energy_consumption_mi_per_kwh=efficiency_data.get("real_electric_consumption_miles_per_kwh"),
                # Range
                real_range_miles=range_data.get("evdb_real_electric_range_miles"),
                # Performance
                drivetrain=performance_data.get("drivetrain_desc"),
                motor_power_kw=performance_data.get("drivetrain_power_kw"),
                motor_power_bhp=performance_data.get("drivetrain_power_bhp"),
                top_speed_mph=performance_data.get("top_speed_mph"),
                zero_to_sixty_secs=performance_data.get("acceleration_0to62_mph_seconds"),
                # Dimensions
                kerb_weight_kg=dimensions_data.get("vehicleweight_kg"),
                boot_capacity_litres=dimensions_data.get("bootspace_min_litres"),
                boot_capacity_max_litres=dimensions_data.get("bootspace_max_litres"),
                frunk_litres=dimensions_data.get("bootspace_front_trunk_litres"),
                max_towing_weight_kg=dimensions_data.get("max_braked_towing_weight_kg"),
            )

        # --- Build range scenarios from EV Database pence per mile (9 weather/driving combos) ---
        if evdb_ppm:
            range_from_ppm = evdb_ppm.get("range_data", {})
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

        # --- Charging costs from EV Database pence per mile ---
        if evdb_ppm:
            result["charging_costs"] = self._calculate_charging_costs_from_evdb(evdb_ppm, evdb_data)
        elif any([evdb_range, evdb_onboard]):
            # Fallback: estimate from specs if ppm endpoint failed
            result["charging_costs"] = self._calculate_charging_costs_from_specs(evdb_range, evdb_onboard)

        # --- AutoPredict: lifespan prediction ---
        predict = autopredict_predict_raw
        stats = autopredict_stats_raw
        if predict or stats:
            averages = (stats or {}).get("averages_data", {})
            number_left = (stats or {}).get("number_left_data", {})
            result["lifespan_prediction"] = LifespanPrediction(
                predicted_remaining_years=(predict or {}).get("years_left_prediction"),
                prediction_range=(predict or {}).get("prediction_string"),
                one_year_survival_pct=(predict or {}).get("one_year_prediction"),
                model_avg_final_miles=averages.get("model_average_final_miles"),
                model_avg_final_age=averages.get("model_average_final_age"),
                manufacturer_avg_final_miles=averages.get("manufacturer_average_final_miles"),
                manufacturer_avg_final_age=averages.get("manufacturer_average_final_age"),
                pct_still_on_road=number_left.get("manufacturer_model_year_percentage_left"),
                initially_registered=number_left.get("manufacturer_model_year_initially_registered"),
                currently_licensed=number_left.get("manufacturer_model_year_currently_licensed"),
            )

        # --- Derive battery health ---
        result["battery_health"] = self._derive_battery_health(clearwatt_raw, evdb_data)

        return result

    def _derive_battery_health(
        self,
        clearwatt_raw: Optional[Dict],
        evdb_data: Dict,
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
