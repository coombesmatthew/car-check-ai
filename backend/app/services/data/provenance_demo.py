"""Demo provenance data for PREMIUM tier features.

Returns finance, stolen, write-off, plate change, and valuation data
for demo vehicles. Will be replaced by UKVD/Experian API calls in production.
"""

from datetime import date
from typing import Dict, Optional


DEMO_PROVENANCE: Dict[str, Dict] = {
    "DEMO1": {
        # 2019 Ford Fiesta — Clean vehicle
        "finance_check": {
            "finance_outstanding": False,
            "record_count": 0,
            "records": [],
            "data_source": "Demo",
        },
        "stolen_check": {
            "stolen": False,
            "reported_date": None,
            "police_force": None,
            "reference": None,
            "data_source": "Demo",
        },
        "write_off_check": {
            "written_off": False,
            "record_count": 0,
            "records": [],
            "data_source": "Demo",
        },
        "plate_changes": {
            "changes_found": False,
            "record_count": 0,
            "records": [],
            "data_source": "Demo",
        },
        "valuation": {
            "private_sale": 8500,
            "dealer_forecourt": 9995,
            "trade_in": 7200,
            "part_exchange": 7500,
            "valuation_date": date.today().isoformat(),
            "mileage_used": 42000,
            "condition": "Good",
            "data_source": "Demo",
        },
    },
    "DEMO2": {
        # 2016 BMW 320D — Dodgy vehicle
        "finance_check": {
            "finance_outstanding": True,
            "record_count": 1,
            "records": [
                {
                    "agreement_type": "PCP",
                    "finance_company": "Black Horse Finance",
                    "agreement_date": "2020-06-15",
                    "agreement_term": "48 months",
                    "contact_number": "0800 123 4567",
                },
            ],
            "data_source": "Demo",
        },
        "stolen_check": {
            "stolen": False,
            "reported_date": None,
            "police_force": None,
            "reference": None,
            "data_source": "Demo",
        },
        "write_off_check": {
            "written_off": True,
            "record_count": 1,
            "records": [
                {
                    "category": "S",
                    "date": "2021-09-12",
                    "loss_type": "Collision",
                },
            ],
            "data_source": "Demo",
        },
        "plate_changes": {
            "changes_found": True,
            "record_count": 1,
            "records": [
                {
                    "previous_plate": "BM16XYZ",
                    "change_date": "2022-03-01",
                    "change_type": "Transfer",
                },
            ],
            "data_source": "Demo",
        },
        "valuation": {
            "private_sale": 6800,
            "dealer_forecourt": 8500,
            "trade_in": 5200,
            "part_exchange": 5800,
            "valuation_date": date.today().isoformat(),
            "mileage_used": 87000,
            "condition": "Average",
            "data_source": "Demo",
        },
    },
    "DEMO3": {
        # 2022 Tesla Model 3 — Clean EV
        "finance_check": {
            "finance_outstanding": True,
            "record_count": 1,
            "records": [
                {
                    "agreement_type": "Lease",
                    "finance_company": "Tesla Finance",
                    "agreement_date": "2022-09-01",
                    "agreement_term": "36 months",
                    "contact_number": "0808 200 8080",
                },
            ],
            "data_source": "Demo",
        },
        "stolen_check": {
            "stolen": False,
            "reported_date": None,
            "police_force": None,
            "reference": None,
            "data_source": "Demo",
        },
        "write_off_check": {
            "written_off": False,
            "record_count": 0,
            "records": [],
            "data_source": "Demo",
        },
        "plate_changes": {
            "changes_found": False,
            "record_count": 0,
            "records": [],
            "data_source": "Demo",
        },
        "valuation": {
            "private_sale": 28500,
            "dealer_forecourt": 31995,
            "trade_in": 25000,
            "part_exchange": 26000,
            "valuation_date": date.today().isoformat(),
            "mileage_used": 18000,
            "condition": "Good",
            "data_source": "Demo",
        },
    },
}


def get_demo_provenance(registration: str) -> Optional[Dict]:
    """Return demo provenance data for a known registration, or None."""
    return DEMO_PROVENANCE.get(registration.upper())
