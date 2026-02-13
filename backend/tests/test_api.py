"""Tests for API endpoints."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime

from app.schemas.check import FreeCheckResponse, VehicleIdentity, ULEZCompliance


@pytest.fixture
def mock_free_check_response():
    """A realistic FreeCheckResponse for mocking the orchestrator."""
    return FreeCheckResponse(
        registration="AB12CDE",
        tier="free",
        vehicle=VehicleIdentity(
            registration="AB12CDE",
            make="FORD",
            colour="BLUE",
            fuel_type="PETROL",
            year_of_manufacture=2018,
            engine_capacity=1000,
            co2_emissions=120,
            euro_status="Euro 6",
            tax_status="Taxed",
            tax_due_date="2025-03-01",
            mot_status="Valid",
            mot_expiry_date="2025-06-15",
        ),
        ulez_compliance=ULEZCompliance(
            compliant=True,
            status="compliant",
            reason="Petrol vehicle with Euro 6 - meets Euro 4 requirement",
            zones={"london_ulez": True, "london_lez": True, "clean_air_zone_d": True},
        ),
        checked_at=datetime(2024, 1, 15, 12, 0, 0),
        data_sources=["DVLA VES API", "DVSA MOT History API"],
    )


class TestFreeCheckEndpoint:
    @patch("app.api.v1.endpoints.checks.CheckOrchestrator")
    def test_valid_registration_returns_200(self, MockOrchestrator, client, mock_free_check_response):
        mock_instance = MockOrchestrator.return_value
        mock_instance.run_free_check = AsyncMock(return_value=mock_free_check_response)
        mock_instance.close = AsyncMock()

        response = client.post(
            "/api/v1/checks/free",
            json={"registration": "AB12CDE"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["registration"] == "AB12CDE"
        assert data["tier"] == "free"
        assert data["vehicle"]["make"] == "FORD"

    @patch("app.api.v1.endpoints.checks.CheckOrchestrator")
    def test_registration_with_spaces_cleaned(self, MockOrchestrator, client, mock_free_check_response):
        mock_instance = MockOrchestrator.return_value
        mock_instance.run_free_check = AsyncMock(return_value=mock_free_check_response)
        mock_instance.close = AsyncMock()

        response = client.post(
            "/api/v1/checks/free",
            json={"registration": "AB12 CDE"},
        )
        assert response.status_code == 200

    def test_empty_registration_returns_422(self, client):
        response = client.post(
            "/api/v1/checks/free",
            json={"registration": ""},
        )
        assert response.status_code == 422

    def test_too_long_registration_returns_422(self, client):
        response = client.post(
            "/api/v1/checks/free",
            json={"registration": "ABCDEFGHIJ"},
        )
        assert response.status_code == 422

    def test_missing_registration_returns_422(self, client):
        response = client.post(
            "/api/v1/checks/free",
            json={},
        )
        assert response.status_code == 422

    @patch("app.api.v1.endpoints.checks.CheckOrchestrator")
    def test_no_data_found_returns_404(self, MockOrchestrator, client):
        empty_response = FreeCheckResponse(
            registration="ZZ99ZZZ",
            tier="free",
            vehicle=None,
            mot_summary=None,
            ulez_compliance=ULEZCompliance(
                compliant=None, status="unknown", reason="No vehicle data available", zones={},
            ),
            checked_at=datetime(2024, 1, 15, 12, 0, 0),
            data_sources=[],
        )
        mock_instance = MockOrchestrator.return_value
        mock_instance.run_free_check = AsyncMock(return_value=empty_response)
        mock_instance.close = AsyncMock()

        response = client.post(
            "/api/v1/checks/free",
            json={"registration": "ZZ99ZZZ"},
        )
        assert response.status_code == 404

    @patch("app.api.v1.endpoints.checks.CheckOrchestrator")
    def test_orchestrator_exception_returns_500(self, MockOrchestrator, client):
        mock_instance = MockOrchestrator.return_value
        mock_instance.run_free_check = AsyncMock(side_effect=RuntimeError("API down"))
        mock_instance.close = AsyncMock()

        response = client.post(
            "/api/v1/checks/free",
            json={"registration": "AB12CDE"},
        )
        assert response.status_code == 500


class TestHealthEndpoint:
    def test_health_returns_200(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_root_returns_200(self, client):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "operational"
