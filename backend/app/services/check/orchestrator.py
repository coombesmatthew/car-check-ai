import asyncio
from datetime import datetime
from typing import Dict, List, Optional

from app.core.logging import logger
from app.services.check.dvla_client import DVLAClient
from app.services.check.ulez import calculate_ulez_compliance
from app.services.mot.client import MOTClient
from app.services.mot.analyzer import MOTAnalyzer
from app.services.data.tax_calculator import calculate_tax
from app.services.data.ncap_ratings import lookup_ncap_rating
from app.services.data.vehicle_stats import calculate_vehicle_stats
from app.core.config import settings
from app.services.data.demo import get_demo_data
from app.services.data.provenance_demo import get_demo_provenance
from app.services.data.oneauto_client import (
    OneAutoClient,
    parse_autocheck,
    parse_valuation,
    parse_salvage,
)
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
    Valuation,
    KeeperHistory,
    HighRiskCheck,
    HighRiskRecord,
    PreviousSearches,
    PreviousSearchRecord,
    SalvageCheck,
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
        self.oneauto_client = OneAutoClient() if settings.ONEAUTO_API_KEY else None

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

        # Fall back to demo data if APIs returned nothing
        if not dvla_data and not mot_data:
            demo = get_demo_data(clean_reg)
            if demo:
                dvla_data, mot_data = demo
                logger.info(f"Using demo data for {clean_reg}")

        # Step 2: Analyze
        mot_analysis = self.mot_analyzer.analyze(mot_data)
        ulez_result = calculate_ulez_compliance(dvla_data)

        # Store raw data for use by AI report generator
        self._raw_dvla_data = dvla_data
        self._raw_mot_analysis = mot_analysis
        self._raw_ulez_data = ulez_result

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

        # Build full MOT test records
        mot_tests = self._build_mot_test_records(mot_analysis.get("mot_tests", []))

        # Calculate tax band
        tax_calculation = self._build_tax_calculation(dvla_data)

        # Look up safety rating
        safety_rating = self._build_safety_rating(dvla_data, mot_analysis.get("mot_summary"))

        # Calculate derived vehicle stats
        raw_tests = mot_analysis.get("raw_tests", [])
        vehicle_stats = self._build_vehicle_stats(
            dvla_data, raw_tests, mot_analysis.get("mileage_timeline", [])
        )

        # Build provenance data (finance, stolen, write-off, plates, valuation)
        current_mileage = None
        if (mot_analysis.get("mot_summary") or {}).get("current_odometer"):
            try:
                current_mileage = int(mot_analysis["mot_summary"]["current_odometer"])
            except (ValueError, TypeError):
                pass
        provenance = await self._build_provenance_data(clean_reg, current_mileage)
        if provenance:
            data_sources.append(provenance.pop("_source", "Provenance Check"))

        response = FreeCheckResponse(
            registration=clean_reg,
            tier="free",
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
            finance_check=provenance.get("finance_check") if provenance else None,
            stolen_check=provenance.get("stolen_check") if provenance else None,
            write_off_check=provenance.get("write_off_check") if provenance else None,
            plate_changes=provenance.get("plate_changes") if provenance else None,
            valuation=provenance.get("valuation") if provenance else None,
            keeper_history=provenance.get("keeper_history") if provenance else None,
            high_risk=provenance.get("high_risk") if provenance else None,
            previous_searches=provenance.get("previous_searches") if provenance else None,
            salvage_check=provenance.get("salvage_check") if provenance else None,
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
        make = None
        model = None
        if dvla_data:
            make = dvla_data.get("make")
        if mot_summary:
            model = mot_summary.get("model")
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

    async def _build_provenance_data(self, registration: str, current_mileage: Optional[int] = None) -> Optional[Dict]:
        """Build provenance data from One Auto API, falling back to demo."""
        # Demo vehicles always use demo data
        if registration.upper().startswith("DEMO"):
            return self._build_provenance_from_raw(
                get_demo_provenance(registration), "Provenance Check (Demo)"
            )

        # Use One Auto API if configured
        if self.oneauto_client:
            try:
                return await self._fetch_oneauto_provenance(registration, current_mileage)
            except Exception as e:
                logger.error(f"One Auto API failed for {registration}: {e}")
                # Fall through to demo fallback

        # Fallback: demo data (returns None for non-demo registrations)
        raw = get_demo_provenance(registration)
        if raw:
            return self._build_provenance_from_raw(raw, "Provenance Check (Demo)")
        return None

    async def _fetch_oneauto_provenance(self, registration: str, current_mileage: Optional[int] = None) -> Optional[Dict]:
        """Fetch real provenance data from One Auto API (Experian + Brego)."""
        autocheck_raw, valuation_raw, salvage_raw = await asyncio.gather(
            self.oneauto_client.get_autocheck(registration),
            self.oneauto_client.get_valuation(registration, current_mileage or 0),
            self.oneauto_client.get_salvage(registration),
            return_exceptions=True,
        )

        if isinstance(autocheck_raw, Exception):
            logger.warning(f"One Auto AutoCheck failed: {autocheck_raw}")
            autocheck_raw = None
        if isinstance(valuation_raw, Exception):
            logger.warning(f"One Auto Brego valuation failed: {valuation_raw}")
            valuation_raw = None
        if isinstance(salvage_raw, Exception):
            logger.warning(f"One Auto CarGuide salvage failed: {salvage_raw}")
            salvage_raw = None

        # AutoCheck returns all Experian data in one response
        parsed = parse_autocheck(autocheck_raw)
        parsed["valuation"] = parse_valuation(valuation_raw, current_mileage or 0)
        parsed["salvage_check"] = parse_salvage(salvage_raw)

        return self._build_provenance_from_raw(parsed, "Experian via One Auto API")

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

        val = raw.get("valuation")
        if val:
            result["valuation"] = Valuation(**val)

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

        return result

    async def close(self):
        tasks = [self.dvla_client.close(), self.mot_client.close()]
        if self.oneauto_client:
            tasks.append(self.oneauto_client.close())
        await asyncio.gather(*tasks)
