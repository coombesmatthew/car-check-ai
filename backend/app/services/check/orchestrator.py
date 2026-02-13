import asyncio
from datetime import datetime
from typing import Dict, Optional

from app.core.logging import logger
from app.services.check.dvla_client import DVLAClient
from app.services.check.ulez import calculate_ulez_compliance
from app.services.mot.client import MOTClient
from app.services.mot.analyzer import MOTAnalyzer
from app.schemas.check import (
    FreeCheckResponse,
    VehicleIdentity,
    MOTSummary,
    LatestTest,
    ClockingAnalysis,
    ClockingFlag,
    MileageReading,
    FailurePattern,
    ULEZCompliance,
)


class CheckOrchestrator:
    """Coordinates all services to produce a vehicle check.

    Flow for free tier:
      1. Fetch DVLA VES + MOT history in parallel
      2. Run ULEZ calculation + MOT analysis
      3. Assemble response
    """

    def __init__(self):
        self.dvla_client = DVLAClient()
        self.mot_client = MOTClient()
        self.mot_analyzer = MOTAnalyzer()

    async def run_free_check(self, registration: str) -> FreeCheckResponse:
        """Execute a free-tier vehicle check.

        Sources: DVSA MOT API + DVLA VES API only. Zero marginal cost.
        """
        clean_reg = registration.upper().replace(" ", "")
        logger.info(f"Starting free check for {clean_reg}")

        # Step 1: Fetch DVLA + MOT data in parallel
        dvla_data, mot_data = await asyncio.gather(
            self.dvla_client.get_vehicle(clean_reg),
            self.mot_client.get_mot_history(clean_reg),
            return_exceptions=True,
        )

        # Handle exceptions from gather
        if isinstance(dvla_data, Exception):
            logger.error(f"DVLA fetch failed: {dvla_data}")
            dvla_data = None
        if isinstance(mot_data, Exception):
            logger.error(f"MOT fetch failed: {mot_data}")
            mot_data = None

        # Step 2: Analyze
        mot_analysis = self.mot_analyzer.analyze(mot_data)
        ulez_result = calculate_ulez_compliance(dvla_data)

        # Step 3: Assemble response
        data_sources = []
        if dvla_data:
            data_sources.append("DVLA VES API")
        if mot_data:
            data_sources.append("DVSA MOT History API")

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

        response = FreeCheckResponse(
            registration=clean_reg,
            tier="free",
            vehicle=vehicle,
            mot_summary=mot_summary,
            clocking_analysis=clocking,
            condition_score=mot_analysis.get("condition_score"),
            mileage_timeline=mileage_timeline,
            failure_patterns=failure_patterns,
            ulez_compliance=ulez_compliance,
            checked_at=datetime.utcnow(),
            data_sources=data_sources,
        )

        logger.info(f"Free check completed for {clean_reg}")
        return response

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

    async def close(self):
        await asyncio.gather(
            self.dvla_client.close(),
            self.mot_client.close(),
        )
