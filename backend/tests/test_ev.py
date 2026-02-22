"""Tests for EV Health Check endpoints and EV detection logic."""

import pytest
from unittest.mock import AsyncMock, patch
from datetime import datetime

from app.schemas.ev import EVCheckResponse
from app.schemas.check import VehicleIdentity, ULEZCompliance
from app.services.ev.orchestrator import classify_ev, EVOrchestrator


# --- EV Detection (unit tests, no mocking needed) ---


class TestClassifyEV:
    def test_electricity_is_bev(self):
        assert classify_ev("ELECTRICITY") == "BEV"

    def test_electricity_lowercase(self):
        assert classify_ev("electricity") == "BEV"

    def test_electricity_mixed_case(self):
        assert classify_ev("Electricity") == "BEV"

    def test_electric_diesel_is_phev(self):
        assert classify_ev("ELECTRIC DIESEL") == "PHEV"

    def test_electric_petrol_is_phev(self):
        assert classify_ev("ELECTRIC PETROL") == "PHEV"

    def test_petrol_is_none(self):
        assert classify_ev("PETROL") is None

    def test_diesel_is_none(self):
        assert classify_ev("DIESEL") is None

    def test_hybrid_electric_is_none(self):
        # Regular hybrid (not plug-in) should not be classified as EV
        assert classify_ev("HYBRID ELECTRIC") is None

    def test_empty_string_is_none(self):
        assert classify_ev("") is None

    def test_none_is_none(self):
        assert classify_ev(None) is None

    def test_whitespace_handling(self):
        assert classify_ev("  ELECTRICITY  ") == "BEV"

    def test_gas_is_none(self):
        assert classify_ev("GAS") is None


# --- EV Check Endpoint Tests ---


@pytest.fixture
def mock_ev_check_response_electric():
    """A realistic EVCheckResponse for an electric vehicle."""
    return EVCheckResponse(
        registration="AB12CDE",
        tier="ev_free",
        is_electric=True,
        ev_type="BEV",
        vehicle=VehicleIdentity(
            registration="AB12CDE",
            make="TESLA",
            colour="WHITE",
            fuel_type="ELECTRICITY",
            year_of_manufacture=2021,
            engine_capacity=None,
            co2_emissions=0,
            tax_status="Taxed",
        ),
        ulez_compliance=ULEZCompliance(
            compliant=True,
            status="compliant",
            reason="Electric vehicle - zero emissions",
            zones={"london_ulez": True},
        ),
        checked_at=datetime(2026, 2, 18, 12, 0, 0),
        data_sources=["DVLA VES API", "DVSA MOT History API"],
    )


@pytest.fixture
def mock_ev_check_response_petrol():
    """A realistic EVCheckResponse for a petrol vehicle (not electric)."""
    return EVCheckResponse(
        registration="XY34FGH",
        tier="ev_free",
        is_electric=False,
        ev_type=None,
        vehicle=VehicleIdentity(
            registration="XY34FGH",
            make="FORD",
            colour="BLUE",
            fuel_type="PETROL",
            year_of_manufacture=2018,
            engine_capacity=1000,
            co2_emissions=120,
        ),
        checked_at=datetime(2026, 2, 18, 12, 0, 0),
        data_sources=["DVLA VES API"],
    )


class TestEVCheckEndpoint:
    @patch("app.api.v1.endpoints.ev.EVOrchestrator")
    def test_electric_vehicle_returns_is_electric_true(
        self, MockOrchestrator, client, mock_ev_check_response_electric
    ):
        mock_instance = MockOrchestrator.return_value
        mock_instance.run_ev_check = AsyncMock(return_value=mock_ev_check_response_electric)
        mock_instance.close = AsyncMock()

        response = client.post("/api/v1/ev/check", json={"registration": "AB12CDE"})
        assert response.status_code == 200
        data = response.json()
        assert data["is_electric"] is True
        assert data["ev_type"] == "BEV"
        assert data["vehicle"]["fuel_type"] == "ELECTRICITY"

    @patch("app.api.v1.endpoints.ev.EVOrchestrator")
    def test_petrol_vehicle_returns_is_electric_false(
        self, MockOrchestrator, client, mock_ev_check_response_petrol
    ):
        mock_instance = MockOrchestrator.return_value
        mock_instance.run_ev_check = AsyncMock(return_value=mock_ev_check_response_petrol)
        mock_instance.close = AsyncMock()

        response = client.post("/api/v1/ev/check", json={"registration": "XY34FGH"})
        assert response.status_code == 200
        data = response.json()
        assert data["is_electric"] is False
        assert data["ev_type"] is None
        assert data["vehicle"]["fuel_type"] == "PETROL"

    @patch("app.api.v1.endpoints.ev.EVOrchestrator")
    def test_registration_cleaned(
        self, MockOrchestrator, client, mock_ev_check_response_electric
    ):
        mock_instance = MockOrchestrator.return_value
        mock_instance.run_ev_check = AsyncMock(return_value=mock_ev_check_response_electric)
        mock_instance.close = AsyncMock()

        response = client.post("/api/v1/ev/check", json={"registration": "AB12 CDE"})
        assert response.status_code == 200

    def test_empty_registration_returns_422(self, client):
        response = client.post("/api/v1/ev/check", json={"registration": ""})
        assert response.status_code == 422

    def test_too_long_registration_returns_422(self, client):
        response = client.post("/api/v1/ev/check", json={"registration": "ABCDEFGHIJ"})
        assert response.status_code == 422

    @patch("app.api.v1.endpoints.ev.EVOrchestrator")
    def test_no_data_returns_404(self, MockOrchestrator, client):
        mock_response = EVCheckResponse(
            registration="ZZ99ZZZ",
            tier="ev_free",
            is_electric=False,
            vehicle=None,
            mot_summary=None,
            checked_at=datetime(2026, 2, 18),
            data_sources=[],
        )
        mock_instance = MockOrchestrator.return_value
        mock_instance.run_ev_check = AsyncMock(return_value=mock_response)
        mock_instance.close = AsyncMock()

        response = client.post("/api/v1/ev/check", json={"registration": "ZZ99ZZZ"})
        assert response.status_code == 404

    @patch("app.api.v1.endpoints.ev.EVOrchestrator")
    def test_orchestrator_exception_returns_500(self, MockOrchestrator, client):
        mock_instance = MockOrchestrator.return_value
        mock_instance.run_ev_check = AsyncMock(side_effect=Exception("API down"))
        mock_instance.close = AsyncMock()

        response = client.post("/api/v1/ev/check", json={"registration": "AB12CDE"})
        assert response.status_code == 500

    @patch("app.api.v1.endpoints.ev.EVOrchestrator")
    def test_response_has_ev_specific_fields(
        self, MockOrchestrator, client, mock_ev_check_response_electric
    ):
        mock_instance = MockOrchestrator.return_value
        mock_instance.run_ev_check = AsyncMock(return_value=mock_ev_check_response_electric)
        mock_instance.close = AsyncMock()

        response = client.post("/api/v1/ev/check", json={"registration": "AB12CDE"})
        data = response.json()
        # EV-specific fields should exist even if null on free tier
        assert "range_estimate" in data
        assert "ev_specs" in data
        assert "battery_health" in data
        assert "charging_costs" in data
        assert "lifespan_prediction" in data
        assert "range_scenarios" in data


class TestEVSchemas:
    def test_ev_check_request_cleans_registration(self):
        from app.schemas.ev import EVCheckRequest
        req = EVCheckRequest(registration="ab12cde")
        assert req.registration == "AB12CDE"

    def test_ev_check_request_rejects_short(self):
        from app.schemas.ev import EVCheckRequest
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            EVCheckRequest(registration="A")

    def test_ev_check_response_defaults(self):
        resp = EVCheckResponse(registration="AB12CDE")
        assert resp.tier == "ev_free"
        assert resp.is_electric is False
        assert resp.ev_type is None
        assert resp.range_estimate is None
        assert resp.range_scenarios == []
        assert resp.ev_specs is None


def _make_clearwatt(retention_pct, test_grade=None):
    """Helper to build a ClearWatt-shaped response from a retention percentage."""
    # Use 200 as baseline "when new" midpoint, scale "now" by retention
    new_mid = 200
    now_mid = new_mid * retention_pct / 100
    return {
        "benchmark_real_electric_range_new": {
            "min_range_miles": int(new_mid - 10),
            "max_range_miles": int(new_mid + 10),
        },
        "expected_real_electric_range_now": {
            "min_range_miles": int(now_mid - 10),
            "max_range_miles": int(now_mid + 10),
        },
        "remaining_battery_warranty": {"miles": 50000, "months": 36},
        "battery_health_test_result": {
            "is_record_available": test_grade is not None,
            "test_date": "2025-06-15" if test_grade else None,
            "test_result_grade": test_grade,
        },
        "vehicle_info": {
            "battery_capacity_kwh": 77,
            "usable_battery_capacity_kwh": 74,
        },
    }


class TestBatteryHealth:
    def test_derive_battery_health_excellent(self):
        orch = EVOrchestrator.__new__(EVOrchestrator)
        bh = orch._derive_battery_health(_make_clearwatt(95), {})
        assert bh.score == 95
        assert bh.grade == "A"
        assert bh.degradation_estimate_pct == 5.0

    def test_derive_battery_health_good(self):
        orch = EVOrchestrator.__new__(EVOrchestrator)
        bh = orch._derive_battery_health(_make_clearwatt(82), {})
        assert bh.score == 82
        assert bh.grade == "B"

    def test_derive_battery_health_fair(self):
        orch = EVOrchestrator.__new__(EVOrchestrator)
        bh = orch._derive_battery_health(_make_clearwatt(72), {})
        assert bh.score == 72
        assert bh.grade == "C"

    def test_derive_battery_health_below_average(self):
        orch = EVOrchestrator.__new__(EVOrchestrator)
        bh = orch._derive_battery_health(_make_clearwatt(65), {})
        assert bh.score == 65
        assert bh.grade == "D"

    def test_derive_battery_health_poor(self):
        orch = EVOrchestrator.__new__(EVOrchestrator)
        bh = orch._derive_battery_health(_make_clearwatt(55), {})
        assert bh.score == 55
        assert bh.grade == "F"

    def test_derive_battery_health_no_data(self):
        orch = EVOrchestrator.__new__(EVOrchestrator)
        bh = orch._derive_battery_health(None, {})
        assert bh.score is None
        assert bh.summary == "No battery data available"

    def test_derive_battery_health_clamped(self):
        orch = EVOrchestrator.__new__(EVOrchestrator)
        bh = orch._derive_battery_health(_make_clearwatt(105), {})
        assert bh.score == 100

    def test_derive_battery_health_with_test_grade(self):
        orch = EVOrchestrator.__new__(EVOrchestrator)
        bh = orch._derive_battery_health(_make_clearwatt(90, test_grade="A+"), {})
        assert bh.grade == "A"
        assert bh.test_grade == "A+"
        assert bh.test_date == "2025-06-15"

    def test_derive_battery_health_no_test_grade(self):
        orch = EVOrchestrator.__new__(EVOrchestrator)
        bh = orch._derive_battery_health(_make_clearwatt(85), {})
        assert bh.test_grade is None
        assert bh.test_date is None


class TestEVPreviewEndpoint:
    @patch("app.api.v1.endpoints.ev.generate_ev_preview_report", new_callable=AsyncMock)
    @patch("app.api.v1.endpoints.ev.EVOrchestrator")
    def test_preview_returns_report_for_ev(
        self, MockOrchestrator, mock_generate, client, mock_ev_check_response_electric
    ):
        mock_instance = MockOrchestrator.return_value
        mock_instance.run_ev_check = AsyncMock(return_value=mock_ev_check_response_electric)
        mock_instance.close = AsyncMock()
        mock_instance._raw_dvla_data = {"make": "TESLA", "fuelType": "ELECTRICITY"}
        mock_instance._raw_mot_analysis = {}
        mock_generate.return_value = "## Should You Buy This EV?\n**BUY** — Great car."

        response = client.post("/api/v1/ev/preview", json={"registration": "AB12CDE"})
        assert response.status_code == 200
        data = response.json()
        assert data["registration"] == "AB12CDE"
        assert data["ai_report"] is not None
        assert "BUY" in data["ai_report"]
        assert data["price"] == "£7.99"
        assert data["ev_check"] is not None

    @patch("app.api.v1.endpoints.ev.EVOrchestrator")
    def test_preview_rejects_non_ev(
        self, MockOrchestrator, client, mock_ev_check_response_petrol
    ):
        mock_instance = MockOrchestrator.return_value
        mock_instance.run_ev_check = AsyncMock(return_value=mock_ev_check_response_petrol)
        mock_instance.close = AsyncMock()

        response = client.post("/api/v1/ev/preview", json={"registration": "XY34FGH"})
        assert response.status_code == 400
        assert "not an electric vehicle" in response.json()["detail"].lower()

    @patch("app.api.v1.endpoints.ev.EVOrchestrator")
    def test_preview_handles_orchestrator_error(self, MockOrchestrator, client):
        mock_instance = MockOrchestrator.return_value
        mock_instance.run_ev_check = AsyncMock(side_effect=Exception("API down"))
        mock_instance.close = AsyncMock()

        response = client.post("/api/v1/ev/preview", json={"registration": "AB12CDE"})
        assert response.status_code == 500

    def test_preview_empty_reg_returns_422(self, client):
        response = client.post("/api/v1/ev/preview", json={"registration": ""})
        assert response.status_code == 422


class TestEVReportGenerator:
    def test_demo_report_has_key_sections(self):
        from app.services.ai.ev_report_generator import _generate_demo_ev_report
        report = _generate_demo_ev_report(
            registration="AB12CDE",
            vehicle_data={"make": "TESLA", "fuelType": "ELECTRICITY", "yearOfManufacture": 2021},
            mot_analysis={
                "mot_summary": {"total_tests": 3, "total_passes": 3, "total_failures": 0, "current_odometer": "25000", "model": "MODEL 3"},
                "condition_score": 85,
                "clocking_analysis": {"clocked": False, "risk_level": "low"},
            },
        )
        assert "## Should You Buy This EV?" in report
        assert "## The Full Picture" in report
        assert "## Charging & Running Costs" in report
        assert "## What You'd Learn in the Full Report" in report

    def test_demo_report_uses_known_specs(self):
        from app.services.ai.ev_report_generator import _generate_demo_ev_report
        report = _generate_demo_ev_report(
            registration="AB12CDE",
            vehicle_data={"make": "TESLA", "fuelType": "ELECTRICITY", "yearOfManufacture": 2021},
            mot_analysis={
                "mot_summary": {"total_tests": 1, "total_passes": 1, "total_failures": 0, "current_odometer": "10000", "model": "MODEL 3"},
                "condition_score": 90,
                "clocking_analysis": {"clocked": False, "risk_level": "low"},
            },
        )
        # Should include Tesla Model 3 specs
        assert "60" in report  # 60 kWh battery
        assert "272" in report  # 272 mile range

    def test_demo_report_verdict_avoid_when_clocked(self):
        from app.services.ai.ev_report_generator import _generate_demo_ev_report
        report = _generate_demo_ev_report(
            registration="AB12CDE",
            vehicle_data={"make": "NISSAN", "fuelType": "ELECTRICITY", "yearOfManufacture": 2019},
            mot_analysis={
                "mot_summary": {"total_tests": 2, "total_passes": 1, "total_failures": 1, "current_odometer": "30000"},
                "condition_score": 60,
                "clocking_analysis": {"clocked": True, "risk_level": "high", "flags": [{"severity": "high", "detail": "Mileage dropped"}]},
            },
        )
        assert "**AVOID**" in report

    def test_lookup_known_specs_tesla(self):
        from app.services.ai.ev_report_generator import _lookup_known_specs
        specs = _lookup_known_specs("TESLA", "MODEL 3")
        assert specs is not None
        assert specs["battery_kwh"] == 60
        assert specs["official_range_miles"] == 272

    def test_lookup_known_specs_unknown(self):
        from app.services.ai.ev_report_generator import _lookup_known_specs
        specs = _lookup_known_specs("NONEXISTENT", "CAR")
        assert specs is None

    def test_lookup_known_specs_partial_match(self):
        from app.services.ai.ev_report_generator import _lookup_known_specs
        specs = _lookup_known_specs("HYUNDAI", "IONIQ 5")
        assert specs is not None
        assert specs["battery_kwh"] == 77

    def test_demo_report_data_sources(self):
        from app.services.ai.ev_report_generator import _generate_demo_ev_report
        report = _generate_demo_ev_report(
            registration="AB12CDE",
            vehicle_data={"make": "TESLA", "fuelType": "ELECTRICITY", "yearOfManufacture": 2021},
            mot_analysis={
                "mot_summary": {"total_tests": 1, "total_passes": 1, "total_failures": 0},
                "condition_score": 90,
                "clocking_analysis": {"clocked": False, "risk_level": "low"},
            },
        )
        assert "## Data Sources" in report
        assert "DVLA" in report
        assert "DVSA" in report


class TestEVDBSearch:
    def test_extract_evdb_vehicle_id_best_match(self):
        orch = EVOrchestrator.__new__(EVOrchestrator)
        search_raw = {
            "evdb_results": [
                {"evdb_vehicle_id": 100, "manufacturer_desc": "Tesla", "model_range_desc": "3", "derivative_desc": "LR", "confidence_scoring": {"overall_score": 75}},
                {"evdb_vehicle_id": 200, "manufacturer_desc": "Tesla", "model_range_desc": "3", "derivative_desc": "SR+", "confidence_scoring": {"overall_score": 92}},
            ]
        }
        assert orch._extract_evdb_vehicle_id(search_raw) == 200

    def test_extract_evdb_vehicle_id_single_result(self):
        orch = EVOrchestrator.__new__(EVOrchestrator)
        search_raw = {
            "evdb_results": [
                {"evdb_vehicle_id": 500, "manufacturer_desc": "Hyundai", "model_range_desc": "Ioniq 5", "derivative_desc": "73kWh", "confidence_scoring": {"overall_score": 88}},
            ]
        }
        assert orch._extract_evdb_vehicle_id(search_raw) == 500

    def test_extract_evdb_vehicle_id_empty(self):
        orch = EVOrchestrator.__new__(EVOrchestrator)
        assert orch._extract_evdb_vehicle_id(None) is None
        assert orch._extract_evdb_vehicle_id({}) is None
        assert orch._extract_evdb_vehicle_id({"evdb_results": []}) is None


class TestParseEVData:
    def test_parse_clearwatt_range_estimate(self):
        orch = EVOrchestrator.__new__(EVOrchestrator)
        clearwatt = {
            "vehicle_info": {
                "battery_capacity_kwh": 77,
                "usable_battery_capacity_kwh": 74,
                "wltp_pure_electric_range_combined_miles_test_energy_low": 303,
            },
            "remaining_battery_warranty": {"miles": 62000, "months": 48},
            "benchmark_real_electric_range_new": {"min_range_miles": 220, "max_range_miles": 240},
            "expected_real_electric_range_now": {"min_range_miles": 195, "max_range_miles": 215},
            "battery_health_test_result": {"is_record_available": True, "test_date": "2025-01-10", "test_result_grade": "A"},
        }
        result = orch._parse_ev_data(clearwatt, None, None, None, {})
        re = result["range_estimate"]
        assert re.estimated_range_miles == 205  # midpoint of 195-215
        assert re.min_range_now_miles == 195
        assert re.max_range_now_miles == 215
        assert re.min_range_new_miles == 220
        assert re.max_range_new_miles == 240
        assert re.official_range_miles == 303
        assert re.warranty_miles_remaining == 62000
        assert re.battery_test_available is True
        assert re.battery_test_grade == "A"
        assert re.range_retention_pct is not None
        assert 88 < re.range_retention_pct < 90  # ~89.1%

    def test_parse_autopredict(self):
        orch = EVOrchestrator.__new__(EVOrchestrator)
        predict = {"years_left_prediction": 8, "prediction_string": "8-10", "one_year_prediction": 0.95}
        stats = {
            "averages_data": {"model_average_final_miles": 150000, "model_average_final_age": 15, "manufacturer_average_final_miles": 140000, "manufacturer_average_final_age": 14},
            "number_left_data": {"manufacturer_model_year_percentage_left": 92, "manufacturer_model_year_initially_registered": 5000, "manufacturer_model_year_currently_licensed": 4600},
        }
        result = orch._parse_ev_data(None, predict, stats, None, {})
        lp = result["lifespan_prediction"]
        assert lp.predicted_remaining_years == 8
        assert lp.prediction_range == "8-10"
        assert lp.one_year_survival_pct == 0.95
        assert lp.model_avg_final_miles == 150000
        assert lp.pct_still_on_road == 92

    def test_parse_evdb_range_scenarios(self):
        orch = EVOrchestrator.__new__(EVOrchestrator)
        ppm = {
            "range_data": {
                "evdb_real_electric_range_highway_cold_miles": 150,
                "evdb_real_electric_range_combined_cold_miles": 180,
                "evdb_real_electric_range_city_cold_miles": 210,
                "evdb_real_electric_range_highway_mild_miles": 200,
                "evdb_real_electric_range_combined_mild_miles": 230,
                "evdb_real_electric_range_city_mild_miles": 270,
                "evdb_real_electric_range_highway_warm_miles": 190,
                "evdb_real_electric_range_combined_warm_miles": 220,
                "evdb_real_electric_range_city_warm_miles": 260,
            },
            "pence_per_mile_data": {"pence_per_mile_combined_mild": {"domestic_standard": 5.0, "public_charger": 12.0}},
            "unit_costs": {"pence_per_kwh_electric_details": {"domestic_standard": 24.5, "public_charger": 65.0}},
        }
        result = orch._parse_ev_data(None, None, None, None, {"pence_per_mile": ppm})
        scenarios = result["range_scenarios"]
        assert len(scenarios) == 9
        # Check cold highway is worst
        assert scenarios[0].estimated_miles == 150
        assert scenarios[0].temperature_c == -10
        assert scenarios[0].driving_style == "highway"


class TestChargingCosts:
    def test_calculate_charging_costs_from_evdb(self):
        orch = EVOrchestrator.__new__(EVOrchestrator)
        ppm_raw = {
            "pence_per_mile_data": {
                "pence_per_mile_combined_mild": {
                    "domestic_standard": 5.2,
                    "public_charger": 13.0,
                },
            },
            "unit_costs": {
                "pence_per_kwh_electric_details": {
                    "domestic_standard": 24.5,
                    "public_charger": 65.0,
                },
            },
        }
        evdb_data = {
            "range": {
                "battery": {"battery_capacity_usable_kwh": 60},
            },
        }
        costs = orch._calculate_charging_costs_from_evdb(ppm_raw, evdb_data)
        assert costs.home_cost_per_full_charge is not None
        assert costs.rapid_cost_per_full_charge is not None
        assert costs.cost_per_mile_home == 5.2
        assert costs.cost_per_mile_public == 13.0
        assert costs.vs_petrol_annual_saving is not None

    def test_calculate_charging_costs_from_specs_fallback(self):
        orch = EVOrchestrator.__new__(EVOrchestrator)
        range_raw = {
            "battery": {"battery_capacity_usable_kwh": 60},
            "efficiency": {"real_electric_consumption_watt_hours_per_mile": 300},
        }
        costs = orch._calculate_charging_costs_from_specs(range_raw, None)
        assert costs.home_cost_per_full_charge is not None
        assert costs.cost_per_mile_home is not None
        # Home should be cheaper than rapid
        assert costs.cost_per_mile_home < costs.cost_per_mile_rapid

    def test_calculate_charging_costs_no_data(self):
        orch = EVOrchestrator.__new__(EVOrchestrator)
        costs = orch._calculate_charging_costs_from_specs(None, None)
        assert costs.home_cost_per_full_charge is None
        assert costs.cost_per_mile_home is None
