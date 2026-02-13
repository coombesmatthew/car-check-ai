"""Tests for the CheckOrchestrator service."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime

from app.services.check.orchestrator import CheckOrchestrator


# Realistic mock data matching actual API response shapes

MOCK_DVLA_RESPONSE = {
    "registrationNumber": "AB12CDE",
    "make": "FORD",
    "colour": "BLUE",
    "fuelType": "PETROL",
    "yearOfManufacture": 2018,
    "engineCapacity": 999,
    "co2Emissions": 120,
    "euroStatus": "Euro 6",
    "taxStatus": "Taxed",
    "taxDueDate": "2025-03-01",
    "motStatus": "Valid",
    "motExpiryDate": "2025-06-15",
    "dateOfLastV5CIssued": "2023-05-10",
    "markedForExport": False,
    "typeApproval": "M1",
    "wheelplan": "2 AXLE RIGID BODY",
}

MOCK_MOT_RESPONSE = [{
    "registration": "AB12CDE",
    "make": "FORD",
    "model": "FIESTA",
    "firstUsedDate": "2018.03.15",
    "motTests": [
        {
            "completedDate": "2021-03-20",
            "testResult": "PASSED",
            "odometerValue": "25000",
            "odometerUnit": "mi",
            "expiryDate": "2022-03-19",
            "defects": [],
        },
        {
            "completedDate": "2022-03-18",
            "testResult": "PASSED",
            "odometerValue": "32000",
            "odometerUnit": "mi",
            "expiryDate": "2023-03-17",
            "defects": [
                {"type": "ADVISORY", "text": "Tyre slightly worn on edge"},
            ],
        },
        {
            "completedDate": "2023-03-15",
            "testResult": "PASSED",
            "odometerValue": "39000",
            "odometerUnit": "mi",
            "expiryDate": "2024-03-14",
            "defects": [],
        },
    ],
}]


@pytest.fixture
def mock_cache():
    """Patch the cache module to be a no-op."""
    with patch("app.services.check.dvla_client.cache") as dvla_cache, \
         patch("app.services.mot.client.cache") as mot_cache:
        dvla_cache.get = AsyncMock(return_value=None)
        dvla_cache.set = AsyncMock()
        mot_cache.get = AsyncMock(return_value=None)
        mot_cache.set = AsyncMock()
        yield


@pytest.mark.asyncio
class TestCheckOrchestrator:
    async def test_full_free_check_with_both_apis(self, mock_cache):
        orchestrator = CheckOrchestrator()

        orchestrator.dvla_client.get_vehicle = AsyncMock(return_value=MOCK_DVLA_RESPONSE)
        orchestrator.mot_client.get_mot_history = AsyncMock(return_value=MOCK_MOT_RESPONSE)

        try:
            result = await orchestrator.run_free_check("AB12CDE")

            assert result.registration == "AB12CDE"
            assert result.tier == "free"
            assert result.vehicle is not None
            assert result.vehicle.make == "FORD"
            assert result.vehicle.fuel_type == "PETROL"
            assert result.mot_summary is not None
            assert result.mot_summary.total_tests == 3
            assert result.mot_summary.total_passes == 3
            assert result.clocking_analysis is not None
            assert result.clocking_analysis.clocked is False
            assert result.condition_score is not None
            assert result.ulez_compliance is not None
            assert result.ulez_compliance.compliant is True
            assert len(result.mileage_timeline) == 3
            assert "DVLA VES API" in result.data_sources
            assert "DVSA MOT History API" in result.data_sources
        finally:
            await orchestrator.close()

    async def test_free_check_dvla_only(self, mock_cache):
        orchestrator = CheckOrchestrator()

        orchestrator.dvla_client.get_vehicle = AsyncMock(return_value=MOCK_DVLA_RESPONSE)
        orchestrator.mot_client.get_mot_history = AsyncMock(return_value=None)

        try:
            result = await orchestrator.run_free_check("AB12CDE")

            assert result.vehicle is not None
            assert result.mot_summary is None
            assert result.clocking_analysis.risk_level == "unknown"
            assert "DVLA VES API" in result.data_sources
            assert "DVSA MOT History API" not in result.data_sources
        finally:
            await orchestrator.close()

    async def test_free_check_mot_only(self, mock_cache):
        orchestrator = CheckOrchestrator()

        orchestrator.dvla_client.get_vehicle = AsyncMock(return_value=None)
        orchestrator.mot_client.get_mot_history = AsyncMock(return_value=MOCK_MOT_RESPONSE)

        try:
            result = await orchestrator.run_free_check("AB12CDE")

            assert result.vehicle is None
            assert result.mot_summary is not None
            assert result.ulez_compliance.compliant is None  # No DVLA data for ULEZ
            assert "DVSA MOT History API" in result.data_sources
        finally:
            await orchestrator.close()

    async def test_free_check_both_apis_fail(self, mock_cache):
        orchestrator = CheckOrchestrator()

        orchestrator.dvla_client.get_vehicle = AsyncMock(side_effect=Exception("DVLA down"))
        orchestrator.mot_client.get_mot_history = AsyncMock(side_effect=Exception("MOT down"))

        try:
            result = await orchestrator.run_free_check("AB12CDE")

            assert result.vehicle is None
            assert result.mot_summary is None
            assert len(result.data_sources) == 0
        finally:
            await orchestrator.close()

    async def test_registration_cleaned(self, mock_cache):
        orchestrator = CheckOrchestrator()

        orchestrator.dvla_client.get_vehicle = AsyncMock(return_value=MOCK_DVLA_RESPONSE)
        orchestrator.mot_client.get_mot_history = AsyncMock(return_value=MOCK_MOT_RESPONSE)

        try:
            result = await orchestrator.run_free_check("ab12 cde")

            assert result.registration == "AB12CDE"
            orchestrator.dvla_client.get_vehicle.assert_called_once_with("AB12CDE")
        finally:
            await orchestrator.close()
