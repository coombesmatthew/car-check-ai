"""Euro NCAP safety ratings lookup.

Static lookup table mapping make/model to Euro NCAP crash test results.
Covers the most common UK vehicles. Data sourced from euroncap.com.

For vehicles not in the lookup, returns None (unknown).
This table can be expanded over time or replaced with an API call.
"""

from typing import Optional, Dict

# Format: (make, model_pattern) -> {year_range, stars, scores}
# model_pattern is a lowercase substring match
NCAP_DATABASE = {
    # Ford
    ("FORD", "fiesta"): {
        "year_range": "2017-2023",
        "stars": 5,
        "adult": 87,
        "child": 84,
        "pedestrian": 64,
        "safety_assist": 60,
        "overall": 74,
        "test_year": 2017,
    },
    ("FORD", "focus"): {
        "year_range": "2018-2025",
        "stars": 5,
        "adult": 85,
        "child": 87,
        "pedestrian": 72,
        "safety_assist": 75,
        "overall": 80,
        "test_year": 2018,
    },
    ("FORD", "puma"): {
        "year_range": "2019-2025",
        "stars": 5,
        "adult": 94,
        "child": 84,
        "pedestrian": 77,
        "safety_assist": 74,
        "overall": 82,
        "test_year": 2019,
    },
    ("FORD", "kuga"): {
        "year_range": "2019-2025",
        "stars": 5,
        "adult": 92,
        "child": 86,
        "pedestrian": 82,
        "safety_assist": 73,
        "overall": 83,
        "test_year": 2019,
    },
    # Volkswagen
    ("VOLKSWAGEN", "golf"): {
        "year_range": "2019-2025",
        "stars": 5,
        "adult": 95,
        "child": 89,
        "pedestrian": 76,
        "safety_assist": 78,
        "overall": 85,
        "test_year": 2019,
    },
    ("VOLKSWAGEN", "polo"): {
        "year_range": "2017-2025",
        "stars": 5,
        "adult": 96,
        "child": 85,
        "pedestrian": 76,
        "safety_assist": 59,
        "overall": 79,
        "test_year": 2017,
    },
    ("VOLKSWAGEN", "tiguan"): {
        "year_range": "2016-2025",
        "stars": 5,
        "adult": 96,
        "child": 84,
        "pedestrian": 72,
        "safety_assist": 68,
        "overall": 80,
        "test_year": 2016,
    },
    ("VOLKSWAGEN", "t-roc"): {
        "year_range": "2017-2025",
        "stars": 5,
        "adult": 96,
        "child": 87,
        "pedestrian": 79,
        "safety_assist": 71,
        "overall": 83,
        "test_year": 2017,
    },
    # BMW
    ("BMW", "3 series"): {
        "year_range": "2019-2025",
        "stars": 5,
        "adult": 97,
        "child": 87,
        "pedestrian": 87,
        "safety_assist": 76,
        "overall": 87,
        "test_year": 2019,
    },
    ("BMW", "1 series"): {
        "year_range": "2019-2025",
        "stars": 5,
        "adult": 97,
        "child": 87,
        "pedestrian": 78,
        "safety_assist": 76,
        "overall": 85,
        "test_year": 2019,
    },
    ("BMW", "x3"): {
        "year_range": "2017-2025",
        "stars": 5,
        "adult": 93,
        "child": 84,
        "pedestrian": 73,
        "safety_assist": 59,
        "overall": 77,
        "test_year": 2017,
    },
    # Mercedes-Benz
    ("MERCEDES-BENZ", "a-class"): {
        "year_range": "2018-2025",
        "stars": 5,
        "adult": 96,
        "child": 91,
        "pedestrian": 92,
        "safety_assist": 75,
        "overall": 89,
        "test_year": 2018,
    },
    ("MERCEDES-BENZ", "c-class"): {
        "year_range": "2021-2025",
        "stars": 5,
        "adult": 91,
        "child": 89,
        "pedestrian": 73,
        "safety_assist": 83,
        "overall": 84,
        "test_year": 2022,
    },
    ("MERCEDES-BENZ", "cla"): {
        "year_range": "2019-2025",
        "stars": 5,
        "adult": 96,
        "child": 91,
        "pedestrian": 92,
        "safety_assist": 75,
        "overall": 89,
        "test_year": 2019,
    },
    ("MERCEDES-BENZ", "gla"): {
        "year_range": "2020-2025",
        "stars": 5,
        "adult": 92,
        "child": 89,
        "pedestrian": 71,
        "safety_assist": 78,
        "overall": 83,
        "test_year": 2020,
    },
    # Audi
    ("AUDI", "a3"): {
        "year_range": "2020-2025",
        "stars": 5,
        "adult": 89,
        "child": 86,
        "pedestrian": 73,
        "safety_assist": 78,
        "overall": 82,
        "test_year": 2020,
    },
    ("AUDI", "a4"): {
        "year_range": "2015-2025",
        "stars": 5,
        "adult": 90,
        "child": 87,
        "pedestrian": 75,
        "safety_assist": 75,
        "overall": 82,
        "test_year": 2015,
    },
    ("AUDI", "q3"): {
        "year_range": "2018-2025",
        "stars": 5,
        "adult": 95,
        "child": 86,
        "pedestrian": 76,
        "safety_assist": 85,
        "overall": 86,
        "test_year": 2018,
    },
    # Toyota
    ("TOYOTA", "yaris"): {
        "year_range": "2020-2025",
        "stars": 5,
        "adult": 86,
        "child": 81,
        "pedestrian": 78,
        "safety_assist": 85,
        "overall": 83,
        "test_year": 2020,
    },
    ("TOYOTA", "corolla"): {
        "year_range": "2019-2025",
        "stars": 5,
        "adult": 95,
        "child": 84,
        "pedestrian": 86,
        "safety_assist": 77,
        "overall": 86,
        "test_year": 2019,
    },
    ("TOYOTA", "rav4"): {
        "year_range": "2019-2025",
        "stars": 5,
        "adult": 93,
        "child": 87,
        "pedestrian": 85,
        "safety_assist": 77,
        "overall": 86,
        "test_year": 2019,
    },
    # Vauxhall / Opel
    ("VAUXHALL", "corsa"): {
        "year_range": "2019-2025",
        "stars": 4,
        "adult": 84,
        "child": 86,
        "pedestrian": 66,
        "safety_assist": 56,
        "overall": 73,
        "test_year": 2019,
    },
    ("VAUXHALL", "astra"): {
        "year_range": "2022-2025",
        "stars": 4,
        "adult": 82,
        "child": 81,
        "pedestrian": 64,
        "safety_assist": 69,
        "overall": 74,
        "test_year": 2022,
    },
    ("VAUXHALL", "mokka"): {
        "year_range": "2020-2025",
        "stars": 4,
        "adult": 73,
        "child": 73,
        "pedestrian": 56,
        "safety_assist": 60,
        "overall": 66,
        "test_year": 2021,
    },
    # Nissan
    ("NISSAN", "qashqai"): {
        "year_range": "2021-2025",
        "stars": 5,
        "adult": 91,
        "child": 90,
        "pedestrian": 70,
        "safety_assist": 95,
        "overall": 87,
        "test_year": 2021,
    },
    ("NISSAN", "juke"): {
        "year_range": "2019-2025",
        "stars": 5,
        "adult": 94,
        "child": 85,
        "pedestrian": 81,
        "safety_assist": 71,
        "overall": 83,
        "test_year": 2019,
    },
    # Hyundai
    ("HYUNDAI", "tucson"): {
        "year_range": "2021-2025",
        "stars": 5,
        "adult": 86,
        "child": 87,
        "pedestrian": 63,
        "safety_assist": 88,
        "overall": 81,
        "test_year": 2021,
    },
    ("HYUNDAI", "i10"): {
        "year_range": "2020-2025",
        "stars": 5,
        "adult": 79,
        "child": 79,
        "pedestrian": 70,
        "safety_assist": 64,
        "overall": 73,
        "test_year": 2020,
    },
    ("HYUNDAI", "i20"): {
        "year_range": "2020-2025",
        "stars": 5,
        "adult": 84,
        "child": 80,
        "pedestrian": 65,
        "safety_assist": 72,
        "overall": 75,
        "test_year": 2020,
    },
    # Kia
    ("KIA", "sportage"): {
        "year_range": "2022-2025",
        "stars": 5,
        "adult": 87,
        "child": 86,
        "pedestrian": 66,
        "safety_assist": 89,
        "overall": 82,
        "test_year": 2022,
    },
    ("KIA", "ceed"): {
        "year_range": "2019-2025",
        "stars": 3,
        "adult": 88,
        "child": 79,
        "pedestrian": 67,
        "safety_assist": 44,
        "overall": 70,
        "test_year": 2019,
    },
    # Honda
    ("HONDA", "civic"): {
        "year_range": "2022-2025",
        "stars": 5,
        "adult": 89,
        "child": 83,
        "pedestrian": 76,
        "safety_assist": 83,
        "overall": 83,
        "test_year": 2022,
    },
    ("HONDA", "jazz"): {
        "year_range": "2020-2025",
        "stars": 5,
        "adult": 87,
        "child": 80,
        "pedestrian": 80,
        "safety_assist": 73,
        "overall": 80,
        "test_year": 2020,
    },
    # Peugeot
    ("PEUGEOT", "208"): {
        "year_range": "2019-2025",
        "stars": 4,
        "adult": 91,
        "child": 80,
        "pedestrian": 56,
        "safety_assist": 64,
        "overall": 73,
        "test_year": 2019,
    },
    ("PEUGEOT", "2008"): {
        "year_range": "2019-2025",
        "stars": 4,
        "adult": 91,
        "child": 80,
        "pedestrian": 56,
        "safety_assist": 64,
        "overall": 73,
        "test_year": 2019,
    },
    # Renault
    ("RENAULT", "clio"): {
        "year_range": "2019-2025",
        "stars": 5,
        "adult": 96,
        "child": 89,
        "pedestrian": 72,
        "safety_assist": 75,
        "overall": 83,
        "test_year": 2019,
    },
    # Skoda
    ("SKODA", "octavia"): {
        "year_range": "2020-2025",
        "stars": 5,
        "adult": 92,
        "child": 88,
        "pedestrian": 73,
        "safety_assist": 78,
        "overall": 83,
        "test_year": 2020,
    },
    ("SKODA", "fabia"): {
        "year_range": "2021-2025",
        "stars": 5,
        "adult": 85,
        "child": 81,
        "pedestrian": 70,
        "safety_assist": 71,
        "overall": 77,
        "test_year": 2022,
    },
    # SEAT / Cupra
    ("SEAT", "leon"): {
        "year_range": "2020-2025",
        "stars": 5,
        "adult": 92,
        "child": 88,
        "pedestrian": 71,
        "safety_assist": 80,
        "overall": 83,
        "test_year": 2020,
    },
    # Mazda
    ("MAZDA", "3"): {
        "year_range": "2019-2025",
        "stars": 5,
        "adult": 98,
        "child": 87,
        "pedestrian": 81,
        "safety_assist": 73,
        "overall": 85,
        "test_year": 2019,
    },
    ("MAZDA", "cx-5"): {
        "year_range": "2017-2025",
        "stars": 5,
        "adult": 93,
        "child": 80,
        "pedestrian": 78,
        "safety_assist": 59,
        "overall": 78,
        "test_year": 2017,
    },
    # Volvo
    ("VOLVO", "xc40"): {
        "year_range": "2017-2025",
        "stars": 5,
        "adult": 97,
        "child": 87,
        "pedestrian": 71,
        "safety_assist": 76,
        "overall": 83,
        "test_year": 2018,
    },
    ("VOLVO", "xc60"): {
        "year_range": "2017-2025",
        "stars": 5,
        "adult": 98,
        "child": 87,
        "pedestrian": 76,
        "safety_assist": 95,
        "overall": 89,
        "test_year": 2017,
    },
    # Tesla
    ("TESLA", "model 3"): {
        "year_range": "2019-2025",
        "stars": 5,
        "adult": 96,
        "child": 86,
        "pedestrian": 74,
        "safety_assist": 94,
        "overall": 88,
        "test_year": 2019,
    },
    ("TESLA", "model y"): {
        "year_range": "2022-2025",
        "stars": 5,
        "adult": 97,
        "child": 87,
        "pedestrian": 82,
        "safety_assist": 98,
        "overall": 91,
        "test_year": 2022,
    },
    # Range Rover / Land Rover
    ("LAND ROVER", "range rover evoque"): {
        "year_range": "2019-2025",
        "stars": 5,
        "adult": 94,
        "child": 87,
        "pedestrian": 72,
        "safety_assist": 73,
        "overall": 82,
        "test_year": 2019,
    },
    ("LAND ROVER", "discovery sport"): {
        "year_range": "2017-2025",
        "stars": 5,
        "adult": 93,
        "child": 85,
        "pedestrian": 75,
        "safety_assist": 75,
        "overall": 82,
        "test_year": 2017,
    },
    # MINI
    ("MINI", "mini"): {
        "year_range": "2014-2025",
        "stars": 4,
        "adult": 83,
        "child": 79,
        "pedestrian": 67,
        "safety_assist": 56,
        "overall": 71,
        "test_year": 2014,
    },
}


def lookup_ncap_rating(
    make: Optional[str],
    model: Optional[str],
) -> Optional[Dict]:
    """Look up Euro NCAP safety rating for a vehicle.

    Args:
        make: Vehicle make (e.g. "FORD")
        model: Vehicle model (e.g. "FIESTA") - can be from DVSA MOT data

    Returns:
        Dict with NCAP rating data or None if not found.
    """
    if not make:
        return None

    make_upper = make.upper().strip()
    model_lower = (model or "").lower().strip()

    # Direct lookup
    for (db_make, db_model_pattern), data in NCAP_DATABASE.items():
        if db_make == make_upper and db_model_pattern in model_lower:
            return {
                "source": "Euro NCAP",
                "make": make_upper,
                "model": model or "Unknown",
                **data,
            }

    # Try partial make match (e.g. "VW" -> "VOLKSWAGEN")
    make_aliases = {
        "VW": "VOLKSWAGEN",
        "MERC": "MERCEDES-BENZ",
        "MERCEDES": "MERCEDES-BENZ",
        "LANDROVER": "LAND ROVER",
    }
    aliased_make = make_aliases.get(make_upper, make_upper)
    if aliased_make != make_upper:
        for (db_make, db_model_pattern), data in NCAP_DATABASE.items():
            if db_make == aliased_make and db_model_pattern in model_lower:
                return {
                    "source": "Euro NCAP",
                    "make": aliased_make,
                    "model": model or "Unknown",
                    **data,
                }

    return None
