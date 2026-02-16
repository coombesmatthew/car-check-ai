"""Tests for the ULEZ / Clean Air Zone compliance calculator."""

import pytest
from app.services.check.ulez import (
    calculate_ulez_compliance,
    _parse_euro_number,
    _estimate_euro_from_year,
)


class TestULEZCompliance:
    def test_no_data_returns_unknown(self):
        result = calculate_ulez_compliance(None)
        assert result["compliant"] is None
        assert result["status"] == "unknown"

    def test_electric_always_exempt(self):
        result = calculate_ulez_compliance({"fuelType": "ELECTRICITY"})
        assert result["compliant"] is True
        assert result["status"] == "exempt"
        assert result["zones"]["london_ulez"] is True
        assert result["zones"]["london_lez"] is True
        assert result["zones"]["oxford_zez"] is True
        assert result["total_zones"] == 14
        assert result["compliant_zones"] == 14

    def test_hydrogen_always_exempt(self):
        result = calculate_ulez_compliance({"fuelType": "HYDROGEN"})
        assert result["compliant"] is True
        assert result["status"] == "exempt"
        assert result["compliant_zones"] == 14

    def test_electric_case_insensitive(self):
        result = calculate_ulez_compliance({"fuelType": "Electric"})
        assert result["compliant"] is True

    def test_petrol_euro_4_compliant(self):
        result = calculate_ulez_compliance({
            "fuelType": "PETROL",
            "euroStatus": "Euro 4",
        })
        assert result["euro_standard"] == 4
        # Compliant with main zones (ULEZ, CAZs) but not Oxford ZEZ
        assert result["zones"]["london_ulez"] is True
        assert result["zones"]["birmingham_caz"] is True
        assert result["zones"]["oxford_zez"] is False
        # Overall non-compliant because of Oxford ZEZ
        assert result["compliant"] is False
        assert result["non_compliant_zones"] == 1

    def test_petrol_euro_3_non_compliant(self):
        result = calculate_ulez_compliance({
            "fuelType": "PETROL",
            "euroStatus": "Euro 3",
        })
        assert result["compliant"] is False
        assert result["status"] == "non_compliant"
        assert result["zones"]["london_ulez"] is False
        assert result["non_compliant_zones"] >= 2  # ULEZ + Oxford ZEZ at minimum

    def test_diesel_euro_6_compliant(self):
        result = calculate_ulez_compliance({
            "fuelType": "DIESEL",
            "euroStatus": "Euro 6",
        })
        # Compliant with all zones except Oxford ZEZ
        assert result["zones"]["london_ulez"] is True
        assert result["zones"]["birmingham_caz"] is True
        assert result["zones"]["glasgow_lez"] is True
        assert result["zones"]["oxford_zez"] is False
        assert result["euro_standard"] == 6

    def test_diesel_euro_5_non_compliant(self):
        result = calculate_ulez_compliance({
            "fuelType": "DIESEL",
            "euroStatus": "Euro 5",
        })
        assert result["compliant"] is False
        assert result["zones"]["london_ulez"] is False

    def test_diesel_euro_6d_variant(self):
        result = calculate_ulez_compliance({
            "fuelType": "DIESEL",
            "euroStatus": "EURO6D",
        })
        assert result["euro_standard"] == 6
        assert result["zones"]["london_ulez"] is True
        assert result["zones"]["birmingham_caz"] is True

    def test_lez_always_passes_for_cars(self):
        result = calculate_ulez_compliance({
            "fuelType": "DIESEL",
            "euroStatus": "Euro 3",
        })
        assert result["zones"]["london_lez"] is True  # LEZ is for HGVs

    def test_inferred_from_year_petrol_2012(self):
        result = calculate_ulez_compliance({
            "fuelType": "PETROL",
            "yearOfManufacture": 2012,
        })
        # 2012 petrol = Euro 6, compliant with main zones
        assert result["zones"]["london_ulez"] is True
        assert result["euro_inferred"] is True

    def test_inferred_from_year_diesel_2014(self):
        result = calculate_ulez_compliance({
            "fuelType": "DIESEL",
            "yearOfManufacture": 2014,
        })
        # 2014 diesel = Euro 5, not compliant with ULEZ
        assert result["compliant"] is False
        assert result["zones"]["london_ulez"] is False

    def test_inferred_from_year_diesel_2016(self):
        result = calculate_ulez_compliance({
            "fuelType": "DIESEL",
            "yearOfManufacture": 2016,
        })
        # 2016 diesel = Euro 6, compliant with main zones
        assert result["zones"]["london_ulez"] is True
        assert result["zones"]["birmingham_caz"] is True

    def test_no_euro_no_year_returns_unknown(self):
        result = calculate_ulez_compliance({"fuelType": "PETROL"})
        assert result["compliant"] is None
        assert result["status"] == "unknown"

    def test_heavy_oil_treated_as_diesel(self):
        result = calculate_ulez_compliance({
            "fuelType": "HEAVY OIL",
            "euroStatus": "Euro 6",
        })
        # Should be treated as diesel, compliant with main zones
        assert result["zones"]["london_ulez"] is True
        assert result["zones"]["birmingham_caz"] is True

    def test_zone_details_populated(self):
        result = calculate_ulez_compliance({
            "fuelType": "PETROL",
            "euroStatus": "Euro 4",
        })
        assert len(result["zone_details"]) == 14
        assert result["total_zones"] == 14
        # Check zone detail structure
        zone = result["zone_details"][0]
        assert "zone_id" in zone
        assert "name" in zone
        assert "region" in zone
        assert "compliant" in zone
        assert "charge" in zone

    def test_oxford_zez_only_evs_exempt(self):
        """Oxford ZEZ charges all non-EV vehicles."""
        # Petrol Euro 6 — not exempt from Oxford ZEZ
        result = calculate_ulez_compliance({
            "fuelType": "PETROL",
            "euroStatus": "Euro 6",
        })
        assert result["zones"]["oxford_zez"] is False

        # Electric — exempt from Oxford ZEZ
        result = calculate_ulez_compliance({"fuelType": "ELECTRICITY"})
        assert result["zones"]["oxford_zez"] is True

    def test_scottish_lez_zones(self):
        """Scottish LEZs should be compliant for Euro 4+ petrol and Euro 6+ diesel."""
        result = calculate_ulez_compliance({
            "fuelType": "PETROL",
            "euroStatus": "Euro 4",
        })
        assert result["zones"]["glasgow_lez"] is True
        assert result["zones"]["edinburgh_lez"] is True
        assert result["zones"]["aberdeen_lez"] is True
        assert result["zones"]["dundee_lez"] is True


class TestParseEuroNumber:
    def test_euro_4(self):
        assert _parse_euro_number("Euro 4") == 4

    def test_euro_6d(self):
        assert _parse_euro_number("EURO6D") == 6

    def test_euro_3_lowercase(self):
        assert _parse_euro_number("euro 3") == 3

    def test_empty_string(self):
        assert _parse_euro_number("") is None

    def test_none(self):
        assert _parse_euro_number(None) is None

    def test_no_number(self):
        assert _parse_euro_number("Euro") is None


class TestEstimateEuroFromYear:
    def test_petrol_2012_euro_6(self):
        assert _estimate_euro_from_year(2012, "PETROL") == 6

    def test_petrol_2007_euro_5(self):
        assert _estimate_euro_from_year(2007, "PETROL") == 5

    def test_petrol_2003_euro_4(self):
        assert _estimate_euro_from_year(2003, "PETROL") == 4

    def test_diesel_2016_euro_6(self):
        assert _estimate_euro_from_year(2016, "DIESEL") == 6

    def test_diesel_2012_euro_5(self):
        assert _estimate_euro_from_year(2012, "DIESEL") == 5

    def test_diesel_2007_euro_4(self):
        assert _estimate_euro_from_year(2007, "DIESEL") == 4

    def test_old_petrol_1995(self):
        assert _estimate_euro_from_year(1995, "PETROL") == 2

    def test_old_diesel_1999(self):
        assert _estimate_euro_from_year(1999, "DIESEL") == 2
