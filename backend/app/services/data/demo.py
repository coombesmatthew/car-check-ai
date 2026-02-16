"""Demo data for testing the UI without live API keys.

Provides realistic DVLA + MOT responses for a set of sample vehicles.
Use registration DEMO1 through DEMO3 or any realistic UK reg to trigger demo mode.
"""

from typing import Optional, Dict, List, Tuple


# --- DEMO VEHICLES ---

DEMO_VEHICLES: Dict[str, Tuple[Dict, List]] = {
    # =========================================================================
    # DEMO1: Clean 2019 Ford Fiesta — low mileage, no issues
    # =========================================================================
    "DEMO1": (
        {
            "registrationNumber": "DEMO1",
            "make": "FORD",
            "colour": "BLUE",
            "fuelType": "PETROL",
            "yearOfManufacture": 2019,
            "engineCapacity": 999,
            "co2Emissions": 120,
            "euroStatus": "Euro 6",
            "taxStatus": "Taxed",
            "taxDueDate": "2026-08-01",
            "motStatus": "Valid",
            "motExpiryDate": "2026-09-15",
            "dateOfLastV5CIssued": "2023-06-10",
            "markedForExport": False,
            "typeApproval": "M1",
            "wheelplan": "2 AXLE RIGID BODY",
            "monthOfFirstRegistration": "2019-03",
        },
        [
            {
                "registration": "DEMO1",
                "make": "FORD",
                "model": "FIESTA",
                "firstUsedDate": "2019.03.15",
                "motTests": [
                    {
                        "completedDate": "2022-09-20",
                        "testResult": "PASSED",
                        "odometerValue": "18500",
                        "odometerUnit": "mi",
                        "motTestNumber": "100001",
                        "expiryDate": "2023-09-19",
                        "defects": [
                            {"type": "ADVISORY", "text": "Front brake disc worn but above legal limit"},
                        ],
                    },
                    {
                        "completedDate": "2023-09-18",
                        "testResult": "PASSED",
                        "odometerValue": "25200",
                        "odometerUnit": "mi",
                        "motTestNumber": "100002",
                        "expiryDate": "2024-09-17",
                        "defects": [
                            {"type": "ADVISORY", "text": "Nearside front tyre slightly worn"},
                        ],
                    },
                    {
                        "completedDate": "2024-09-15",
                        "testResult": "PASSED",
                        "odometerValue": "32100",
                        "odometerUnit": "mi",
                        "motTestNumber": "100003",
                        "expiryDate": "2025-09-14",
                        "defects": [],
                    },
                    {
                        "completedDate": "2025-09-12",
                        "testResult": "PASSED",
                        "odometerValue": "39400",
                        "odometerUnit": "mi",
                        "motTestNumber": "100004",
                        "expiryDate": "2026-09-11",
                        "defects": [
                            {"type": "ADVISORY", "text": "Rear brake pads wearing but above legal limit"},
                        ],
                    },
                ],
            }
        ],
    ),

    # =========================================================================
    # DEMO2: Dodgy 2016 BMW 3 Series — clocked mileage, failures
    # =========================================================================
    "DEMO2": (
        {
            "registrationNumber": "DEMO2",
            "make": "BMW",
            "colour": "BLACK",
            "fuelType": "DIESEL",
            "yearOfManufacture": 2016,
            "engineCapacity": 1995,
            "co2Emissions": 124,
            "euroStatus": "Euro 6",
            "taxStatus": "Taxed",
            "taxDueDate": "2026-04-01",
            "motStatus": "Valid",
            "motExpiryDate": "2026-06-20",
            "dateOfLastV5CIssued": "2025-11-05",
            "markedForExport": False,
            "typeApproval": "M1",
            "wheelplan": "2 AXLE RIGID BODY",
            "monthOfFirstRegistration": "2016-06",
        },
        [
            {
                "registration": "DEMO2",
                "make": "BMW",
                "model": "320D",
                "firstUsedDate": "2016.06.20",
                "motTests": [
                    {
                        "completedDate": "2019-06-18",
                        "testResult": "PASSED",
                        "odometerValue": "35200",
                        "odometerUnit": "mi",
                        "motTestNumber": "200001",
                        "expiryDate": "2020-06-17",
                        "defects": [
                            {"type": "ADVISORY", "text": "Offside rear tyre slightly worn"},
                        ],
                    },
                    {
                        "completedDate": "2020-06-15",
                        "testResult": "FAILED",
                        "odometerValue": "58700",
                        "odometerUnit": "mi",
                        "motTestNumber": "200002",
                        "defects": [
                            {"type": "MAJOR", "text": "Nearside front brake disc excessively worn"},
                            {"type": "MAJOR", "text": "Offside rear tyre below minimum tread depth"},
                            {"type": "ADVISORY", "text": "Exhaust has minor leak"},
                        ],
                    },
                    {
                        "completedDate": "2020-06-22",
                        "testResult": "PASSED",
                        "odometerValue": "58750",
                        "odometerUnit": "mi",
                        "motTestNumber": "200003",
                        "expiryDate": "2021-06-21",
                        "defects": [
                            {"type": "ADVISORY", "text": "Exhaust has minor leak"},
                        ],
                    },
                    {
                        "completedDate": "2021-06-19",
                        "testResult": "PASSED",
                        "odometerValue": "72100",
                        "odometerUnit": "mi",
                        "motTestNumber": "200004",
                        "expiryDate": "2022-06-18",
                        "defects": [
                            {"type": "ADVISORY", "text": "Offside front suspension arm ball joint worn but not excessively"},
                            {"type": "ADVISORY", "text": "Exhaust has minor leak"},
                        ],
                    },
                    {
                        "completedDate": "2022-06-16",
                        "testResult": "PASSED",
                        "odometerValue": "85400",
                        "odometerUnit": "mi",
                        "motTestNumber": "200005",
                        "expiryDate": "2023-06-15",
                        "defects": [
                            {"type": "ADVISORY", "text": "Nearside rear brake pad wearing thin"},
                            {"type": "ADVISORY", "text": "Suspension arm corroded"},
                        ],
                    },
                    {
                        "completedDate": "2023-06-14",
                        "testResult": "PASSED",
                        "odometerValue": "62000",
                        "odometerUnit": "mi",
                        "motTestNumber": "200006",
                        "expiryDate": "2024-06-13",
                        "defects": [
                            {"type": "ADVISORY", "text": "Offside rear brake disc worn but above legal limit"},
                        ],
                    },
                    {
                        "completedDate": "2024-06-12",
                        "testResult": "FAILED",
                        "odometerValue": "68500",
                        "odometerUnit": "mi",
                        "motTestNumber": "200007",
                        "defects": [
                            {"type": "MAJOR", "text": "Nearside front tyre has ply exposed"},
                            {"type": "MINOR", "text": "Offside headlamp aim too high"},
                        ],
                    },
                    {
                        "completedDate": "2024-06-18",
                        "testResult": "PASSED",
                        "odometerValue": "68550",
                        "odometerUnit": "mi",
                        "motTestNumber": "200008",
                        "expiryDate": "2025-06-17",
                        "defects": [],
                    },
                    {
                        "completedDate": "2025-06-15",
                        "testResult": "PASSED",
                        "odometerValue": "74200",
                        "odometerUnit": "mi",
                        "motTestNumber": "200009",
                        "expiryDate": "2026-06-14",
                        "defects": [
                            {"type": "ADVISORY", "text": "Exhaust corroded"},
                            {"type": "ADVISORY", "text": "Nearside rear suspension arm corroded"},
                        ],
                    },
                ],
            }
        ],
    ),

    # =========================================================================
    # DEMO3: Electric 2022 Tesla Model 3 — clean, no emissions
    # =========================================================================
    "DEMO3": (
        {
            "registrationNumber": "DEMO3",
            "make": "TESLA",
            "colour": "WHITE",
            "fuelType": "ELECTRICITY",
            "yearOfManufacture": 2022,
            "engineCapacity": 0,
            "co2Emissions": 0,
            "euroStatus": None,
            "taxStatus": "Taxed",
            "taxDueDate": "2026-12-01",
            "motStatus": "Valid",
            "motExpiryDate": "2026-10-05",
            "dateOfLastV5CIssued": "2022-04-20",
            "markedForExport": False,
            "typeApproval": "M1",
            "wheelplan": "2 AXLE RIGID BODY",
            "monthOfFirstRegistration": "2022-04",
        },
        [
            {
                "registration": "DEMO3",
                "make": "TESLA",
                "model": "MODEL 3",
                "firstUsedDate": "2022.04.20",
                "motTests": [
                    {
                        "completedDate": "2025-04-18",
                        "testResult": "PASSED",
                        "odometerValue": "28500",
                        "odometerUnit": "mi",
                        "motTestNumber": "300001",
                        "expiryDate": "2026-04-17",
                        "defects": [],
                    },
                    {
                        "completedDate": "2025-10-02",
                        "testResult": "PASSED",
                        "odometerValue": "34200",
                        "odometerUnit": "mi",
                        "motTestNumber": "300002",
                        "expiryDate": "2026-10-01",
                        "defects": [
                            {"type": "ADVISORY", "text": "Nearside front tyre slightly worn on inner edge"},
                        ],
                    },
                ],
            }
        ],
    ),

    # =========================================================================
    # HJ18KLM: High-mileage 2018 VW Golf diesel, lots of advisories,
    # borderline ULEZ (Euro 6 diesel = compliant but high emissions)
    # =========================================================================
    "HJ18KLM": (
        {
            "registrationNumber": "HJ18KLM",
            "make": "VOLKSWAGEN",
            "colour": "GREY",
            "fuelType": "DIESEL",
            "yearOfManufacture": 2018,
            "engineCapacity": 1598,
            "co2Emissions": 116,
            "euroStatus": "Euro 6",
            "taxStatus": "Taxed",
            "taxDueDate": "2026-05-01",
            "motStatus": "Valid",
            "motExpiryDate": "2026-07-22",
            "dateOfLastV5CIssued": "2024-01-15",
            "markedForExport": False,
            "typeApproval": "M1",
            "wheelplan": "2 AXLE RIGID BODY",
            "monthOfFirstRegistration": "2018-03",
        },
        [
            {
                "registration": "HJ18KLM",
                "make": "VOLKSWAGEN",
                "model": "GOLF",
                "firstUsedDate": "2018.03.22",
                "motTests": [
                    {
                        "completedDate": "2021-03-20",
                        "testResult": "PASSED",
                        "odometerValue": "48200",
                        "odometerUnit": "mi",
                        "motTestNumber": "400001",
                        "expiryDate": "2022-03-19",
                        "defects": [
                            {"type": "ADVISORY", "text": "Nearside front tyre worn close to legal limit"},
                            {"type": "ADVISORY", "text": "Offside front tyre worn close to legal limit"},
                        ],
                    },
                    {
                        "completedDate": "2022-03-18",
                        "testResult": "PASSED",
                        "odometerValue": "64800",
                        "odometerUnit": "mi",
                        "motTestNumber": "400002",
                        "expiryDate": "2023-03-17",
                        "defects": [
                            {"type": "ADVISORY", "text": "Offside rear brake disc worn but above legal limit"},
                            {"type": "ADVISORY", "text": "Nearside rear brake disc worn but above legal limit"},
                            {"type": "ADVISORY", "text": "Front windscreen has minor damage within driver's line of vision"},
                        ],
                    },
                    {
                        "completedDate": "2023-03-15",
                        "testResult": "PASSED",
                        "odometerValue": "81300",
                        "odometerUnit": "mi",
                        "motTestNumber": "400003",
                        "expiryDate": "2024-03-14",
                        "defects": [
                            {"type": "ADVISORY", "text": "Nearside front anti-roll bar linkage ball joint has slight play"},
                            {"type": "ADVISORY", "text": "Offside front anti-roll bar linkage ball joint has slight play"},
                            {"type": "ADVISORY", "text": "Exhaust mounting corroded"},
                            {"type": "ADVISORY", "text": "Nearside rear tyre worn close to legal limit"},
                        ],
                    },
                    {
                        "completedDate": "2024-03-12",
                        "testResult": "FAILED",
                        "odometerValue": "97500",
                        "odometerUnit": "mi",
                        "motTestNumber": "400004",
                        "defects": [
                            {"type": "MAJOR", "text": "Offside front tyre tread depth below requirements"},
                            {"type": "ADVISORY", "text": "Nearside front suspension spring corroded"},
                            {"type": "ADVISORY", "text": "Offside front suspension spring corroded"},
                            {"type": "ADVISORY", "text": "Rear exhaust section corroded"},
                        ],
                    },
                    {
                        "completedDate": "2024-03-15",
                        "testResult": "PASSED",
                        "odometerValue": "97510",
                        "odometerUnit": "mi",
                        "motTestNumber": "400005",
                        "expiryDate": "2025-03-14",
                        "defects": [
                            {"type": "ADVISORY", "text": "Nearside front suspension spring corroded"},
                            {"type": "ADVISORY", "text": "Offside front suspension spring corroded"},
                            {"type": "ADVISORY", "text": "Rear exhaust section corroded"},
                        ],
                    },
                    {
                        "completedDate": "2025-07-20",
                        "testResult": "PASSED",
                        "odometerValue": "112800",
                        "odometerUnit": "mi",
                        "motTestNumber": "400006",
                        "expiryDate": "2026-07-19",
                        "defects": [
                            {"type": "ADVISORY", "text": "Nearside front suspension spring corroded"},
                            {"type": "ADVISORY", "text": "Offside front suspension spring corroded"},
                            {"type": "ADVISORY", "text": "Rear exhaust has minor leak"},
                            {"type": "ADVISORY", "text": "Offside rear brake disc worn but above legal limit"},
                            {"type": "ADVISORY", "text": "Both front anti-roll bar linkage ball joints worn but not excessively"},
                        ],
                    },
                ],
            }
        ],
    ),

    # =========================================================================
    # KN20ABC: 2020 Toyota Yaris hybrid, very clean
    # =========================================================================
    "KN20ABC": (
        {
            "registrationNumber": "KN20ABC",
            "make": "TOYOTA",
            "colour": "RED",
            "fuelType": "PETROL/ELECTRIC HYBRID",
            "yearOfManufacture": 2020,
            "engineCapacity": 1490,
            "co2Emissions": 64,
            "euroStatus": "Euro 6",
            "taxStatus": "Taxed",
            "taxDueDate": "2026-09-01",
            "motStatus": "Valid",
            "motExpiryDate": "2026-08-10",
            "dateOfLastV5CIssued": "2020-09-05",
            "markedForExport": False,
            "typeApproval": "M1",
            "wheelplan": "2 AXLE RIGID BODY",
            "monthOfFirstRegistration": "2020-09",
        },
        [
            {
                "registration": "KN20ABC",
                "make": "TOYOTA",
                "model": "YARIS",
                "firstUsedDate": "2020.09.05",
                "motTests": [
                    {
                        "completedDate": "2023-09-03",
                        "testResult": "PASSED",
                        "odometerValue": "18200",
                        "odometerUnit": "mi",
                        "motTestNumber": "500001",
                        "expiryDate": "2024-09-02",
                        "defects": [],
                    },
                    {
                        "completedDate": "2024-08-28",
                        "testResult": "PASSED",
                        "odometerValue": "24600",
                        "odometerUnit": "mi",
                        "motTestNumber": "500002",
                        "expiryDate": "2025-08-27",
                        "defects": [],
                    },
                    {
                        "completedDate": "2025-08-12",
                        "testResult": "PASSED",
                        "odometerValue": "31100",
                        "odometerUnit": "mi",
                        "motTestNumber": "500003",
                        "expiryDate": "2026-08-11",
                        "defects": [
                            {"type": "ADVISORY", "text": "Nearside rear tyre slightly worn on outer edge"},
                        ],
                    },
                ],
            }
        ],
    ),

    # =========================================================================
    # LP15DEF: 2015 Audi A3 diesel, Euro 5, ULEZ non-compliant, exhaust issues
    # =========================================================================
    "LP15DEF": (
        {
            "registrationNumber": "LP15DEF",
            "make": "AUDI",
            "colour": "SILVER",
            "fuelType": "DIESEL",
            "yearOfManufacture": 2015,
            "engineCapacity": 1968,
            "co2Emissions": 109,
            "euroStatus": "Euro 5",
            "taxStatus": "Taxed",
            "taxDueDate": "2026-03-01",
            "motStatus": "Valid",
            "motExpiryDate": "2026-05-18",
            "dateOfLastV5CIssued": "2022-08-14",
            "markedForExport": False,
            "typeApproval": "M1",
            "wheelplan": "2 AXLE RIGID BODY",
            "monthOfFirstRegistration": "2015-06",
        },
        [
            {
                "registration": "LP15DEF",
                "make": "AUDI",
                "model": "A3",
                "firstUsedDate": "2015.06.18",
                "motTests": [
                    {
                        "completedDate": "2018-06-15",
                        "testResult": "PASSED",
                        "odometerValue": "32100",
                        "odometerUnit": "mi",
                        "motTestNumber": "600001",
                        "expiryDate": "2019-06-14",
                        "defects": [
                            {"type": "ADVISORY", "text": "Offside rear tyre slightly worn"},
                        ],
                    },
                    {
                        "completedDate": "2019-06-12",
                        "testResult": "PASSED",
                        "odometerValue": "45600",
                        "odometerUnit": "mi",
                        "motTestNumber": "600002",
                        "expiryDate": "2020-06-11",
                        "defects": [
                            {"type": "ADVISORY", "text": "Exhaust mounting slightly deteriorated"},
                            {"type": "ADVISORY", "text": "Nearside front brake disc worn but above legal limit"},
                        ],
                    },
                    {
                        "completedDate": "2020-06-09",
                        "testResult": "PASSED",
                        "odometerValue": "56200",
                        "odometerUnit": "mi",
                        "motTestNumber": "600003",
                        "expiryDate": "2021-06-08",
                        "defects": [
                            {"type": "ADVISORY", "text": "Offside front brake disc worn but above legal limit"},
                            {"type": "ADVISORY", "text": "Exhaust has minor leak at manifold joint"},
                        ],
                    },
                    {
                        "completedDate": "2021-06-07",
                        "testResult": "FAILED",
                        "odometerValue": "67800",
                        "odometerUnit": "mi",
                        "motTestNumber": "600004",
                        "defects": [
                            {"type": "MAJOR", "text": "Exhaust Lambda reading after catalyst not within limits"},
                            {"type": "MAJOR", "text": "Exhaust emissions carbon monoxide content at idle exceeds default limits"},
                            {"type": "ADVISORY", "text": "Offside rear brake disc worn but above legal limit"},
                        ],
                    },
                    {
                        "completedDate": "2021-06-14",
                        "testResult": "PASSED",
                        "odometerValue": "67820",
                        "odometerUnit": "mi",
                        "motTestNumber": "600005",
                        "expiryDate": "2022-06-13",
                        "defects": [
                            {"type": "ADVISORY", "text": "Offside rear brake disc worn but above legal limit"},
                        ],
                    },
                    {
                        "completedDate": "2022-06-10",
                        "testResult": "PASSED",
                        "odometerValue": "76300",
                        "odometerUnit": "mi",
                        "motTestNumber": "600006",
                        "expiryDate": "2023-06-09",
                        "defects": [
                            {"type": "ADVISORY", "text": "Exhaust mounting corroded"},
                            {"type": "ADVISORY", "text": "Nearside front suspension arm ball joint worn but not excessively"},
                        ],
                    },
                    {
                        "completedDate": "2023-06-08",
                        "testResult": "PASSED",
                        "odometerValue": "84100",
                        "odometerUnit": "mi",
                        "motTestNumber": "600007",
                        "expiryDate": "2024-06-07",
                        "defects": [
                            {"type": "ADVISORY", "text": "Exhaust corroded and deteriorated"},
                            {"type": "ADVISORY", "text": "Nearside rear coil spring corroded"},
                        ],
                    },
                    {
                        "completedDate": "2024-06-05",
                        "testResult": "FAILED",
                        "odometerValue": "91500",
                        "odometerUnit": "mi",
                        "motTestNumber": "600008",
                        "defects": [
                            {"type": "MAJOR", "text": "Exhaust emissions carbon monoxide content at idle exceeds default limits"},
                            {"type": "ADVISORY", "text": "Exhaust system corroded and deteriorated"},
                            {"type": "MINOR", "text": "Nearside front position lamp not working"},
                        ],
                    },
                    {
                        "completedDate": "2024-06-10",
                        "testResult": "PASSED",
                        "odometerValue": "91520",
                        "odometerUnit": "mi",
                        "motTestNumber": "600009",
                        "expiryDate": "2025-06-09",
                        "defects": [
                            {"type": "ADVISORY", "text": "Exhaust system corroded and deteriorated"},
                        ],
                    },
                    {
                        "completedDate": "2025-05-16",
                        "testResult": "PASSED",
                        "odometerValue": "98200",
                        "odometerUnit": "mi",
                        "motTestNumber": "600010",
                        "expiryDate": "2026-05-15",
                        "defects": [
                            {"type": "ADVISORY", "text": "Exhaust system has deteriorated"},
                            {"type": "ADVISORY", "text": "Nearside rear coil spring corroded"},
                            {"type": "ADVISORY", "text": "Offside rear coil spring corroded"},
                        ],
                    },
                ],
            }
        ],
    ),

    # =========================================================================
    # MR67GHI: 2017 Vauxhall Corsa petrol, multiple failures, brake/tyre patterns
    # =========================================================================
    "MR67GHI": (
        {
            "registrationNumber": "MR67GHI",
            "make": "VAUXHALL",
            "colour": "WHITE",
            "fuelType": "PETROL",
            "yearOfManufacture": 2017,
            "engineCapacity": 1398,
            "co2Emissions": 129,
            "euroStatus": "Euro 6",
            "taxStatus": "Taxed",
            "taxDueDate": "2026-11-01",
            "motStatus": "Valid",
            "motExpiryDate": "2026-04-08",
            "dateOfLastV5CIssued": "2023-02-18",
            "markedForExport": False,
            "typeApproval": "M1",
            "wheelplan": "2 AXLE RIGID BODY",
            "monthOfFirstRegistration": "2017-09",
        },
        [
            {
                "registration": "MR67GHI",
                "make": "VAUXHALL",
                "model": "CORSA",
                "firstUsedDate": "2017.09.14",
                "motTests": [
                    {
                        "completedDate": "2020-09-10",
                        "testResult": "FAILED",
                        "odometerValue": "29800",
                        "odometerUnit": "mi",
                        "motTestNumber": "700001",
                        "defects": [
                            {"type": "MAJOR", "text": "Nearside front tyre tread depth below requirements"},
                            {"type": "MAJOR", "text": "Offside front tyre tread depth below requirements"},
                            {"type": "ADVISORY", "text": "Nearside front brake disc worn but above legal limit"},
                        ],
                    },
                    {
                        "completedDate": "2020-09-14",
                        "testResult": "PASSED",
                        "odometerValue": "29810",
                        "odometerUnit": "mi",
                        "motTestNumber": "700002",
                        "expiryDate": "2021-09-13",
                        "defects": [
                            {"type": "ADVISORY", "text": "Nearside front brake disc worn but above legal limit"},
                        ],
                    },
                    {
                        "completedDate": "2021-09-11",
                        "testResult": "FAILED",
                        "odometerValue": "41200",
                        "odometerUnit": "mi",
                        "motTestNumber": "700003",
                        "defects": [
                            {"type": "MAJOR", "text": "Nearside front brake disc excessively worn"},
                            {"type": "MAJOR", "text": "Offside front brake disc excessively worn"},
                            {"type": "ADVISORY", "text": "Nearside rear tyre worn close to legal limit"},
                        ],
                    },
                    {
                        "completedDate": "2021-09-16",
                        "testResult": "PASSED",
                        "odometerValue": "41220",
                        "odometerUnit": "mi",
                        "motTestNumber": "700004",
                        "expiryDate": "2022-09-15",
                        "defects": [
                            {"type": "ADVISORY", "text": "Nearside rear tyre worn close to legal limit"},
                        ],
                    },
                    {
                        "completedDate": "2022-09-13",
                        "testResult": "PASSED",
                        "odometerValue": "52600",
                        "odometerUnit": "mi",
                        "motTestNumber": "700005",
                        "expiryDate": "2023-09-12",
                        "defects": [
                            {"type": "ADVISORY", "text": "Offside rear tyre worn close to legal limit"},
                            {"type": "ADVISORY", "text": "Nearside rear brake pad wearing thin"},
                        ],
                    },
                    {
                        "completedDate": "2023-09-10",
                        "testResult": "FAILED",
                        "odometerValue": "63100",
                        "odometerUnit": "mi",
                        "motTestNumber": "700006",
                        "defects": [
                            {"type": "MAJOR", "text": "Offside rear tyre has ply or cords exposed"},
                            {"type": "MAJOR", "text": "Nearside rear brake pad below minimum thickness"},
                            {"type": "ADVISORY", "text": "Offside front brake disc worn but above legal limit"},
                        ],
                    },
                    {
                        "completedDate": "2023-09-14",
                        "testResult": "PASSED",
                        "odometerValue": "63120",
                        "odometerUnit": "mi",
                        "motTestNumber": "700007",
                        "expiryDate": "2024-09-13",
                        "defects": [
                            {"type": "ADVISORY", "text": "Offside front brake disc worn but above legal limit"},
                        ],
                    },
                    {
                        "completedDate": "2024-09-11",
                        "testResult": "FAILED",
                        "odometerValue": "74500",
                        "odometerUnit": "mi",
                        "motTestNumber": "700008",
                        "defects": [
                            {"type": "MAJOR", "text": "Nearside front tyre tread depth below requirements"},
                            {"type": "MINOR", "text": "Offside rear registration plate lamp not working"},
                        ],
                    },
                    {
                        "completedDate": "2024-09-15",
                        "testResult": "PASSED",
                        "odometerValue": "74520",
                        "odometerUnit": "mi",
                        "motTestNumber": "700009",
                        "expiryDate": "2025-09-14",
                        "defects": [],
                    },
                    {
                        "completedDate": "2025-04-06",
                        "testResult": "PASSED",
                        "odometerValue": "80100",
                        "odometerUnit": "mi",
                        "motTestNumber": "700010",
                        "expiryDate": "2026-04-05",
                        "defects": [
                            {"type": "ADVISORY", "text": "Nearside front tyre worn close to legal limit"},
                            {"type": "ADVISORY", "text": "Offside front brake disc worn but above legal limit"},
                        ],
                    },
                ],
            }
        ],
    ),

    # =========================================================================
    # NT12JKL: 2012 Honda Civic, old but well maintained, high mileage consistent
    # =========================================================================
    "NT12JKL": (
        {
            "registrationNumber": "NT12JKL",
            "make": "HONDA",
            "colour": "SILVER",
            "fuelType": "PETROL",
            "yearOfManufacture": 2012,
            "engineCapacity": 1798,
            "co2Emissions": 150,
            "euroStatus": "Euro 5",
            "taxStatus": "Taxed",
            "taxDueDate": "2026-06-01",
            "motStatus": "Valid",
            "motExpiryDate": "2026-03-20",
            "dateOfLastV5CIssued": "2019-04-22",
            "markedForExport": False,
            "typeApproval": "M1",
            "wheelplan": "2 AXLE RIGID BODY",
            "monthOfFirstRegistration": "2012-03",
        },
        [
            {
                "registration": "NT12JKL",
                "make": "HONDA",
                "model": "CIVIC",
                "firstUsedDate": "2012.03.15",
                "motTests": [
                    {
                        "completedDate": "2015-03-12",
                        "testResult": "PASSED",
                        "odometerValue": "31200",
                        "odometerUnit": "mi",
                        "motTestNumber": "800001",
                        "expiryDate": "2016-03-11",
                        "defects": [],
                    },
                    {
                        "completedDate": "2016-03-10",
                        "testResult": "PASSED",
                        "odometerValue": "42800",
                        "odometerUnit": "mi",
                        "motTestNumber": "800002",
                        "expiryDate": "2017-03-09",
                        "defects": [
                            {"type": "ADVISORY", "text": "Nearside front tyre slightly worn"},
                        ],
                    },
                    {
                        "completedDate": "2017-03-08",
                        "testResult": "PASSED",
                        "odometerValue": "54300",
                        "odometerUnit": "mi",
                        "motTestNumber": "800003",
                        "expiryDate": "2018-03-07",
                        "defects": [
                            {"type": "ADVISORY", "text": "Offside rear brake pad wearing thin but above legal limit"},
                        ],
                    },
                    {
                        "completedDate": "2018-03-06",
                        "testResult": "PASSED",
                        "odometerValue": "65700",
                        "odometerUnit": "mi",
                        "motTestNumber": "800004",
                        "expiryDate": "2019-03-05",
                        "defects": [
                            {"type": "ADVISORY", "text": "Front windscreen has minor damage but not within driver's line of vision"},
                        ],
                    },
                    {
                        "completedDate": "2019-03-04",
                        "testResult": "PASSED",
                        "odometerValue": "77100",
                        "odometerUnit": "mi",
                        "motTestNumber": "800005",
                        "expiryDate": "2020-03-03",
                        "defects": [
                            {"type": "ADVISORY", "text": "Nearside rear tyre worn close to legal limit"},
                        ],
                    },
                    {
                        "completedDate": "2020-03-02",
                        "testResult": "PASSED",
                        "odometerValue": "88400",
                        "odometerUnit": "mi",
                        "motTestNumber": "800006",
                        "expiryDate": "2021-03-01",
                        "defects": [
                            {"type": "ADVISORY", "text": "Offside front suspension arm ball joint worn but not excessively"},
                        ],
                    },
                    {
                        "completedDate": "2021-02-26",
                        "testResult": "PASSED",
                        "odometerValue": "96200",
                        "odometerUnit": "mi",
                        "motTestNumber": "800007",
                        "expiryDate": "2022-02-25",
                        "defects": [
                            {"type": "ADVISORY", "text": "Offside front suspension arm ball joint worn but not excessively"},
                            {"type": "ADVISORY", "text": "Exhaust mounting slightly deteriorated"},
                        ],
                    },
                    {
                        "completedDate": "2022-02-24",
                        "testResult": "PASSED",
                        "odometerValue": "107500",
                        "odometerUnit": "mi",
                        "motTestNumber": "800008",
                        "expiryDate": "2023-02-23",
                        "defects": [
                            {"type": "ADVISORY", "text": "Nearside front brake disc worn but above legal limit"},
                            {"type": "ADVISORY", "text": "Exhaust mounting slightly deteriorated"},
                        ],
                    },
                    {
                        "completedDate": "2023-02-22",
                        "testResult": "PASSED",
                        "odometerValue": "118900",
                        "odometerUnit": "mi",
                        "motTestNumber": "800009",
                        "expiryDate": "2024-02-21",
                        "defects": [
                            {"type": "ADVISORY", "text": "Nearside front brake disc worn but above legal limit"},
                            {"type": "ADVISORY", "text": "Offside rear brake disc worn but above legal limit"},
                        ],
                    },
                    {
                        "completedDate": "2024-02-20",
                        "testResult": "PASSED",
                        "odometerValue": "130200",
                        "odometerUnit": "mi",
                        "motTestNumber": "800010",
                        "expiryDate": "2025-02-19",
                        "defects": [
                            {"type": "ADVISORY", "text": "Offside rear shock absorber has light misting of oil"},
                            {"type": "ADVISORY", "text": "Both rear brake discs worn but above legal limit"},
                        ],
                    },
                    {
                        "completedDate": "2025-03-18",
                        "testResult": "PASSED",
                        "odometerValue": "141600",
                        "odometerUnit": "mi",
                        "motTestNumber": "800011",
                        "expiryDate": "2026-03-17",
                        "defects": [
                            {"type": "ADVISORY", "text": "Offside rear shock absorber has light misting of oil"},
                            {"type": "ADVISORY", "text": "Nearside rear coil spring corroded"},
                            {"type": "ADVISORY", "text": "Exhaust corroded but no leak"},
                        ],
                    },
                ],
            }
        ],
    ),

    # =========================================================================
    # PW21MNO: 2021 Mercedes A-Class, low mileage, one MOT, minimal history
    # =========================================================================
    "PW21MNO": (
        {
            "registrationNumber": "PW21MNO",
            "make": "MERCEDES-BENZ",
            "colour": "BLACK",
            "fuelType": "PETROL",
            "yearOfManufacture": 2021,
            "engineCapacity": 1332,
            "co2Emissions": 135,
            "euroStatus": "Euro 6",
            "taxStatus": "Taxed",
            "taxDueDate": "2026-07-01",
            "motStatus": "Valid",
            "motExpiryDate": "2026-05-12",
            "dateOfLastV5CIssued": "2021-06-10",
            "markedForExport": False,
            "typeApproval": "M1",
            "wheelplan": "2 AXLE RIGID BODY",
            "monthOfFirstRegistration": "2021-06",
        },
        [
            {
                "registration": "PW21MNO",
                "make": "MERCEDES-BENZ",
                "model": "A 200",
                "firstUsedDate": "2021.06.10",
                "motTests": [
                    {
                        "completedDate": "2024-06-08",
                        "testResult": "PASSED",
                        "odometerValue": "12400",
                        "odometerUnit": "mi",
                        "motTestNumber": "900001",
                        "expiryDate": "2025-06-07",
                        "defects": [],
                    },
                    {
                        "completedDate": "2025-05-14",
                        "testResult": "PASSED",
                        "odometerValue": "18100",
                        "odometerUnit": "mi",
                        "motTestNumber": "900002",
                        "expiryDate": "2026-05-13",
                        "defects": [
                            {"type": "ADVISORY", "text": "Offside front tyre slightly worn on inner edge"},
                        ],
                    },
                ],
            }
        ],
    ),

    # =========================================================================
    # RX14PQR: 2014 Nissan Qashqai diesel, suspension pattern, moderate mileage
    # =========================================================================
    "RX14PQR": (
        {
            "registrationNumber": "RX14PQR",
            "make": "NISSAN",
            "colour": "BROWN",
            "fuelType": "DIESEL",
            "yearOfManufacture": 2014,
            "engineCapacity": 1461,
            "co2Emissions": 99,
            "euroStatus": "Euro 5",
            "taxStatus": "Taxed",
            "taxDueDate": "2026-04-01",
            "motStatus": "Valid",
            "motExpiryDate": "2026-08-30",
            "dateOfLastV5CIssued": "2021-11-03",
            "markedForExport": False,
            "typeApproval": "M1",
            "wheelplan": "2 AXLE RIGID BODY",
            "monthOfFirstRegistration": "2014-09",
        },
        [
            {
                "registration": "RX14PQR",
                "make": "NISSAN",
                "model": "QASHQAI",
                "firstUsedDate": "2014.09.20",
                "motTests": [
                    {
                        "completedDate": "2017-09-18",
                        "testResult": "PASSED",
                        "odometerValue": "28500",
                        "odometerUnit": "mi",
                        "motTestNumber": "1000001",
                        "expiryDate": "2018-09-17",
                        "defects": [],
                    },
                    {
                        "completedDate": "2018-09-15",
                        "testResult": "PASSED",
                        "odometerValue": "39800",
                        "odometerUnit": "mi",
                        "motTestNumber": "1000002",
                        "expiryDate": "2019-09-14",
                        "defects": [
                            {"type": "ADVISORY", "text": "Nearside front suspension arm ball joint worn but not excessively"},
                        ],
                    },
                    {
                        "completedDate": "2019-09-12",
                        "testResult": "PASSED",
                        "odometerValue": "50200",
                        "odometerUnit": "mi",
                        "motTestNumber": "1000003",
                        "expiryDate": "2020-09-11",
                        "defects": [
                            {"type": "ADVISORY", "text": "Nearside front suspension arm ball joint worn but not excessively"},
                            {"type": "ADVISORY", "text": "Offside front suspension arm ball joint worn but not excessively"},
                        ],
                    },
                    {
                        "completedDate": "2020-09-09",
                        "testResult": "FAILED",
                        "odometerValue": "60100",
                        "odometerUnit": "mi",
                        "motTestNumber": "1000004",
                        "defects": [
                            {"type": "MAJOR", "text": "Nearside front lower suspension arm ball joint excessively worn"},
                            {"type": "ADVISORY", "text": "Offside front suspension arm ball joint worn but not excessively"},
                            {"type": "ADVISORY", "text": "Nearside rear shock absorber has light misting of oil"},
                        ],
                    },
                    {
                        "completedDate": "2020-09-14",
                        "testResult": "PASSED",
                        "odometerValue": "60120",
                        "odometerUnit": "mi",
                        "motTestNumber": "1000005",
                        "expiryDate": "2021-09-13",
                        "defects": [
                            {"type": "ADVISORY", "text": "Offside front suspension arm ball joint worn but not excessively"},
                            {"type": "ADVISORY", "text": "Nearside rear shock absorber has light misting of oil"},
                        ],
                    },
                    {
                        "completedDate": "2021-09-11",
                        "testResult": "PASSED",
                        "odometerValue": "70500",
                        "odometerUnit": "mi",
                        "motTestNumber": "1000006",
                        "expiryDate": "2022-09-10",
                        "defects": [
                            {"type": "ADVISORY", "text": "Offside front lower suspension arm ball joint worn but not excessively"},
                            {"type": "ADVISORY", "text": "Nearside rear shock absorber has slight leak"},
                        ],
                    },
                    {
                        "completedDate": "2022-09-08",
                        "testResult": "FAILED",
                        "odometerValue": "80800",
                        "odometerUnit": "mi",
                        "motTestNumber": "1000007",
                        "defects": [
                            {"type": "MAJOR", "text": "Offside front lower suspension arm ball joint excessively worn"},
                            {"type": "MAJOR", "text": "Nearside rear shock absorber leaking"},
                        ],
                    },
                    {
                        "completedDate": "2022-09-13",
                        "testResult": "PASSED",
                        "odometerValue": "80830",
                        "odometerUnit": "mi",
                        "motTestNumber": "1000008",
                        "expiryDate": "2023-09-12",
                        "defects": [
                            {"type": "ADVISORY", "text": "Offside rear shock absorber has light misting of oil"},
                        ],
                    },
                    {
                        "completedDate": "2023-09-10",
                        "testResult": "PASSED",
                        "odometerValue": "91200",
                        "odometerUnit": "mi",
                        "motTestNumber": "1000009",
                        "expiryDate": "2024-09-09",
                        "defects": [
                            {"type": "ADVISORY", "text": "Nearside front anti-roll bar linkage ball joint has slight play"},
                            {"type": "ADVISORY", "text": "Offside rear shock absorber has light misting of oil"},
                        ],
                    },
                    {
                        "completedDate": "2024-09-06",
                        "testResult": "PASSED",
                        "odometerValue": "101500",
                        "odometerUnit": "mi",
                        "motTestNumber": "1000010",
                        "expiryDate": "2025-09-05",
                        "defects": [
                            {"type": "ADVISORY", "text": "Nearside front anti-roll bar linkage ball joint has slight play"},
                            {"type": "ADVISORY", "text": "Offside front anti-roll bar linkage ball joint has slight play"},
                        ],
                    },
                    {
                        "completedDate": "2025-08-28",
                        "testResult": "PASSED",
                        "odometerValue": "111800",
                        "odometerUnit": "mi",
                        "motTestNumber": "1000011",
                        "expiryDate": "2026-08-27",
                        "defects": [
                            {"type": "ADVISORY", "text": "Both front anti-roll bar linkage ball joints worn but not excessively"},
                            {"type": "ADVISORY", "text": "Nearside rear coil spring corroded"},
                        ],
                    },
                ],
            }
        ],
    ),

    # =========================================================================
    # SY19STU: 2019 Kia Sportage petrol, clocked (subtle small mileage drop)
    # =========================================================================
    "SY19STU": (
        {
            "registrationNumber": "SY19STU",
            "make": "KIA",
            "colour": "RED",
            "fuelType": "PETROL",
            "yearOfManufacture": 2019,
            "engineCapacity": 1591,
            "co2Emissions": 158,
            "euroStatus": "Euro 6",
            "taxStatus": "Taxed",
            "taxDueDate": "2026-10-01",
            "motStatus": "Valid",
            "motExpiryDate": "2026-07-15",
            "dateOfLastV5CIssued": "2025-03-20",
            "markedForExport": False,
            "typeApproval": "M1",
            "wheelplan": "2 AXLE RIGID BODY",
            "monthOfFirstRegistration": "2019-05",
        },
        [
            {
                "registration": "SY19STU",
                "make": "KIA",
                "model": "SPORTAGE",
                "firstUsedDate": "2019.05.10",
                "motTests": [
                    {
                        "completedDate": "2022-05-08",
                        "testResult": "PASSED",
                        "odometerValue": "36200",
                        "odometerUnit": "mi",
                        "motTestNumber": "1100001",
                        "expiryDate": "2023-05-07",
                        "defects": [
                            {"type": "ADVISORY", "text": "Offside rear tyre slightly worn"},
                        ],
                    },
                    {
                        "completedDate": "2023-05-05",
                        "testResult": "PASSED",
                        "odometerValue": "48700",
                        "odometerUnit": "mi",
                        "motTestNumber": "1100002",
                        "expiryDate": "2024-05-04",
                        "defects": [
                            {"type": "ADVISORY", "text": "Nearside front brake disc worn but above legal limit"},
                        ],
                    },
                    {
                        "completedDate": "2024-05-02",
                        "testResult": "PASSED",
                        "odometerValue": "61400",
                        "odometerUnit": "mi",
                        "motTestNumber": "1100003",
                        "expiryDate": "2025-05-01",
                        "defects": [
                            {"type": "ADVISORY", "text": "Nearside front brake disc worn but above legal limit"},
                            {"type": "ADVISORY", "text": "Offside front brake disc worn but above legal limit"},
                        ],
                    },
                    {
                        "completedDate": "2025-07-13",
                        "testResult": "PASSED",
                        "odometerValue": "54800",
                        "odometerUnit": "mi",
                        "motTestNumber": "1100004",
                        "expiryDate": "2026-07-12",
                        "defects": [
                            {"type": "ADVISORY", "text": "Offside rear tyre slightly worn on outer edge"},
                        ],
                    },
                ],
            }
        ],
    ),

    # =========================================================================
    # TB66VWX: 2016 Range Rover Evoque diesel, expensive repair pattern
    # (brakes, suspension, exhaust all recurring)
    # =========================================================================
    "TB66VWX": (
        {
            "registrationNumber": "TB66VWX",
            "make": "LAND ROVER",
            "colour": "BLACK",
            "fuelType": "DIESEL",
            "yearOfManufacture": 2016,
            "engineCapacity": 1999,
            "co2Emissions": 139,
            "euroStatus": "Euro 6",
            "taxStatus": "Taxed",
            "taxDueDate": "2026-02-01",
            "motStatus": "Valid",
            "motExpiryDate": "2026-01-22",
            "dateOfLastV5CIssued": "2024-07-18",
            "markedForExport": False,
            "typeApproval": "M1",
            "wheelplan": "2 AXLE RIGID BODY",
            "monthOfFirstRegistration": "2016-09",
        },
        [
            {
                "registration": "TB66VWX",
                "make": "LAND ROVER",
                "model": "RANGE ROVER EVOQUE",
                "firstUsedDate": "2016.09.25",
                "motTests": [
                    {
                        "completedDate": "2019-09-23",
                        "testResult": "PASSED",
                        "odometerValue": "28400",
                        "odometerUnit": "mi",
                        "motTestNumber": "1200001",
                        "expiryDate": "2020-09-22",
                        "defects": [
                            {"type": "ADVISORY", "text": "Nearside front brake disc worn but above legal limit"},
                            {"type": "ADVISORY", "text": "Offside front brake disc worn but above legal limit"},
                        ],
                    },
                    {
                        "completedDate": "2020-09-20",
                        "testResult": "FAILED",
                        "odometerValue": "41200",
                        "odometerUnit": "mi",
                        "motTestNumber": "1200002",
                        "defects": [
                            {"type": "MAJOR", "text": "Nearside front brake disc excessively worn"},
                            {"type": "MAJOR", "text": "Offside front brake disc excessively worn"},
                            {"type": "ADVISORY", "text": "Nearside front suspension arm ball joint worn but not excessively"},
                            {"type": "ADVISORY", "text": "Exhaust mounting corroded"},
                        ],
                    },
                    {
                        "completedDate": "2020-09-25",
                        "testResult": "PASSED",
                        "odometerValue": "41230",
                        "odometerUnit": "mi",
                        "motTestNumber": "1200003",
                        "expiryDate": "2021-09-24",
                        "defects": [
                            {"type": "ADVISORY", "text": "Nearside front suspension arm ball joint worn but not excessively"},
                            {"type": "ADVISORY", "text": "Exhaust mounting corroded"},
                        ],
                    },
                    {
                        "completedDate": "2021-09-22",
                        "testResult": "FAILED",
                        "odometerValue": "53600",
                        "odometerUnit": "mi",
                        "motTestNumber": "1200004",
                        "defects": [
                            {"type": "MAJOR", "text": "Nearside front lower suspension arm ball joint excessively worn"},
                            {"type": "MAJOR", "text": "Exhaust has a major leak of exhaust gases"},
                            {"type": "ADVISORY", "text": "Offside front suspension arm ball joint worn but not excessively"},
                            {"type": "ADVISORY", "text": "Nearside rear brake disc worn but above legal limit"},
                        ],
                    },
                    {
                        "completedDate": "2021-09-28",
                        "testResult": "PASSED",
                        "odometerValue": "53630",
                        "odometerUnit": "mi",
                        "motTestNumber": "1200005",
                        "expiryDate": "2022-09-27",
                        "defects": [
                            {"type": "ADVISORY", "text": "Offside front suspension arm ball joint worn but not excessively"},
                            {"type": "ADVISORY", "text": "Nearside rear brake disc worn but above legal limit"},
                        ],
                    },
                    {
                        "completedDate": "2022-09-25",
                        "testResult": "FAILED",
                        "odometerValue": "65800",
                        "odometerUnit": "mi",
                        "motTestNumber": "1200006",
                        "defects": [
                            {"type": "MAJOR", "text": "Nearside rear brake disc excessively worn"},
                            {"type": "MAJOR", "text": "Offside rear brake disc excessively worn"},
                            {"type": "MAJOR", "text": "Offside front lower suspension arm ball joint excessively worn"},
                            {"type": "ADVISORY", "text": "Exhaust corroded"},
                        ],
                    },
                    {
                        "completedDate": "2022-10-01",
                        "testResult": "PASSED",
                        "odometerValue": "65830",
                        "odometerUnit": "mi",
                        "motTestNumber": "1200007",
                        "expiryDate": "2023-09-30",
                        "defects": [
                            {"type": "ADVISORY", "text": "Exhaust corroded"},
                        ],
                    },
                    {
                        "completedDate": "2023-09-28",
                        "testResult": "PASSED",
                        "odometerValue": "76200",
                        "odometerUnit": "mi",
                        "motTestNumber": "1200008",
                        "expiryDate": "2024-09-27",
                        "defects": [
                            {"type": "ADVISORY", "text": "Nearside front brake disc worn but above legal limit"},
                            {"type": "ADVISORY", "text": "Offside front brake disc worn but above legal limit"},
                            {"type": "ADVISORY", "text": "Exhaust corroded and deteriorated"},
                            {"type": "ADVISORY", "text": "Nearside rear coil spring corroded"},
                        ],
                    },
                    {
                        "completedDate": "2024-09-25",
                        "testResult": "FAILED",
                        "odometerValue": "87500",
                        "odometerUnit": "mi",
                        "motTestNumber": "1200009",
                        "defects": [
                            {"type": "MAJOR", "text": "Nearside front brake disc excessively worn"},
                            {"type": "MAJOR", "text": "Exhaust has a major leak of exhaust gases"},
                            {"type": "ADVISORY", "text": "Nearside rear coil spring corroded"},
                            {"type": "ADVISORY", "text": "Offside rear coil spring corroded"},
                        ],
                    },
                    {
                        "completedDate": "2024-10-02",
                        "testResult": "PASSED",
                        "odometerValue": "87530",
                        "odometerUnit": "mi",
                        "motTestNumber": "1200010",
                        "expiryDate": "2025-10-01",
                        "defects": [
                            {"type": "ADVISORY", "text": "Nearside rear coil spring corroded"},
                            {"type": "ADVISORY", "text": "Offside rear coil spring corroded"},
                        ],
                    },
                    {
                        "completedDate": "2025-01-20",
                        "testResult": "PASSED",
                        "odometerValue": "92100",
                        "odometerUnit": "mi",
                        "motTestNumber": "1200011",
                        "expiryDate": "2026-01-19",
                        "defects": [
                            {"type": "ADVISORY", "text": "Both front brake discs worn but above legal limit"},
                            {"type": "ADVISORY", "text": "Offside front suspension arm ball joint worn but not excessively"},
                            {"type": "ADVISORY", "text": "Exhaust corroded"},
                            {"type": "ADVISORY", "text": "Nearside rear coil spring corroded"},
                            {"type": "ADVISORY", "text": "Offside rear coil spring corroded"},
                        ],
                    },
                ],
            }
        ],
    ),

    # =========================================================================
    # UC22YZA: 2022 Hyundai Ioniq 5 electric, clean, no emissions
    # =========================================================================
    "UC22YZA": (
        {
            "registrationNumber": "UC22YZA",
            "make": "HYUNDAI",
            "colour": "GREEN",
            "fuelType": "ELECTRICITY",
            "yearOfManufacture": 2022,
            "engineCapacity": 0,
            "co2Emissions": 0,
            "euroStatus": None,
            "taxStatus": "Taxed",
            "taxDueDate": "2026-11-01",
            "motStatus": "Valid",
            "motExpiryDate": "2026-08-20",
            "dateOfLastV5CIssued": "2022-08-15",
            "markedForExport": False,
            "typeApproval": "M1",
            "wheelplan": "2 AXLE RIGID BODY",
            "monthOfFirstRegistration": "2022-08",
        },
        [
            {
                "registration": "UC22YZA",
                "make": "HYUNDAI",
                "model": "IONIQ 5",
                "firstUsedDate": "2022.08.15",
                "motTests": [
                    {
                        "completedDate": "2025-08-13",
                        "testResult": "PASSED",
                        "odometerValue": "22100",
                        "odometerUnit": "mi",
                        "motTestNumber": "1300001",
                        "expiryDate": "2026-08-12",
                        "defects": [],
                    },
                ],
            }
        ],
    ),

    # =========================================================================
    # VD17BCD: 2017 Peugeot 308 diesel, DPF and emission issues
    # =========================================================================
    "VD17BCD": (
        {
            "registrationNumber": "VD17BCD",
            "make": "PEUGEOT",
            "colour": "BLUE",
            "fuelType": "DIESEL",
            "yearOfManufacture": 2017,
            "engineCapacity": 1560,
            "co2Emissions": 100,
            "euroStatus": "Euro 6",
            "taxStatus": "Taxed",
            "taxDueDate": "2026-06-01",
            "motStatus": "Valid",
            "motExpiryDate": "2026-04-25",
            "dateOfLastV5CIssued": "2023-05-08",
            "markedForExport": False,
            "typeApproval": "M1",
            "wheelplan": "2 AXLE RIGID BODY",
            "monthOfFirstRegistration": "2017-03",
        },
        [
            {
                "registration": "VD17BCD",
                "make": "PEUGEOT",
                "model": "308",
                "firstUsedDate": "2017.03.25",
                "motTests": [
                    {
                        "completedDate": "2020-03-23",
                        "testResult": "PASSED",
                        "odometerValue": "24600",
                        "odometerUnit": "mi",
                        "motTestNumber": "1400001",
                        "expiryDate": "2021-03-22",
                        "defects": [],
                    },
                    {
                        "completedDate": "2021-03-20",
                        "testResult": "PASSED",
                        "odometerValue": "32100",
                        "odometerUnit": "mi",
                        "motTestNumber": "1400002",
                        "expiryDate": "2022-03-19",
                        "defects": [
                            {"type": "ADVISORY", "text": "Nearside front tyre worn close to legal limit"},
                        ],
                    },
                    {
                        "completedDate": "2022-03-17",
                        "testResult": "FAILED",
                        "odometerValue": "41800",
                        "odometerUnit": "mi",
                        "motTestNumber": "1400003",
                        "defects": [
                            {"type": "MAJOR", "text": "Exhaust emissions carbon monoxide content at idle exceeds default limits"},
                            {"type": "MAJOR", "text": "Diesel particulate filter missing where one was fitted as standard"},
                            {"type": "ADVISORY", "text": "Engine malfunction indicator lamp illuminated"},
                        ],
                    },
                    {
                        "completedDate": "2022-03-24",
                        "testResult": "PASSED",
                        "odometerValue": "41830",
                        "odometerUnit": "mi",
                        "motTestNumber": "1400004",
                        "expiryDate": "2023-03-23",
                        "defects": [
                            {"type": "ADVISORY", "text": "Engine malfunction indicator lamp illuminated"},
                        ],
                    },
                    {
                        "completedDate": "2023-03-21",
                        "testResult": "PASSED",
                        "odometerValue": "50200",
                        "odometerUnit": "mi",
                        "motTestNumber": "1400005",
                        "expiryDate": "2024-03-20",
                        "defects": [
                            {"type": "ADVISORY", "text": "Offside rear brake disc worn but above legal limit"},
                            {"type": "ADVISORY", "text": "Exhaust system corroded"},
                        ],
                    },
                    {
                        "completedDate": "2024-03-18",
                        "testResult": "FAILED",
                        "odometerValue": "58600",
                        "odometerUnit": "mi",
                        "motTestNumber": "1400006",
                        "defects": [
                            {"type": "MAJOR", "text": "Exhaust emissions Lambda reading after catalyst not within limits"},
                            {"type": "ADVISORY", "text": "Exhaust system corroded and deteriorated"},
                            {"type": "ADVISORY", "text": "Engine malfunction indicator lamp illuminated"},
                        ],
                    },
                    {
                        "completedDate": "2024-03-25",
                        "testResult": "PASSED",
                        "odometerValue": "58630",
                        "odometerUnit": "mi",
                        "motTestNumber": "1400007",
                        "expiryDate": "2025-03-24",
                        "defects": [
                            {"type": "ADVISORY", "text": "Exhaust system corroded and deteriorated"},
                        ],
                    },
                    {
                        "completedDate": "2025-04-23",
                        "testResult": "PASSED",
                        "odometerValue": "66100",
                        "odometerUnit": "mi",
                        "motTestNumber": "1400008",
                        "expiryDate": "2026-04-22",
                        "defects": [
                            {"type": "ADVISORY", "text": "Exhaust system corroded"},
                            {"type": "ADVISORY", "text": "Nearside rear coil spring corroded"},
                        ],
                    },
                ],
            }
        ],
    ),

    # =========================================================================
    # WE13EFG: 2013 Mini Cooper petrol, lots of character
    # (many advisories but passes), fun car
    # =========================================================================
    "WE13EFG": (
        {
            "registrationNumber": "WE13EFG",
            "make": "MINI",
            "colour": "GREEN",
            "fuelType": "PETROL",
            "yearOfManufacture": 2013,
            "engineCapacity": 1598,
            "co2Emissions": 136,
            "euroStatus": "Euro 5",
            "taxStatus": "Taxed",
            "taxDueDate": "2026-05-01",
            "motStatus": "Valid",
            "motExpiryDate": "2026-06-10",
            "dateOfLastV5CIssued": "2020-09-12",
            "markedForExport": False,
            "typeApproval": "M1",
            "wheelplan": "2 AXLE RIGID BODY",
            "monthOfFirstRegistration": "2013-06",
        },
        [
            {
                "registration": "WE13EFG",
                "make": "MINI",
                "model": "COOPER",
                "firstUsedDate": "2013.06.20",
                "motTests": [
                    {
                        "completedDate": "2016-06-18",
                        "testResult": "PASSED",
                        "odometerValue": "28400",
                        "odometerUnit": "mi",
                        "motTestNumber": "1500001",
                        "expiryDate": "2017-06-17",
                        "defects": [
                            {"type": "ADVISORY", "text": "Nearside front tyre slightly worn"},
                        ],
                    },
                    {
                        "completedDate": "2017-06-15",
                        "testResult": "PASSED",
                        "odometerValue": "39200",
                        "odometerUnit": "mi",
                        "motTestNumber": "1500002",
                        "expiryDate": "2018-06-14",
                        "defects": [
                            {"type": "ADVISORY", "text": "Offside front brake disc worn but above legal limit"},
                            {"type": "ADVISORY", "text": "Oil leak from engine but not excessive"},
                        ],
                    },
                    {
                        "completedDate": "2018-06-12",
                        "testResult": "PASSED",
                        "odometerValue": "50600",
                        "odometerUnit": "mi",
                        "motTestNumber": "1500003",
                        "expiryDate": "2019-06-11",
                        "defects": [
                            {"type": "ADVISORY", "text": "Oil leak from engine but not excessive"},
                            {"type": "ADVISORY", "text": "Nearside rear brake pad wearing thin but above legal limit"},
                            {"type": "ADVISORY", "text": "Front windscreen has minor damage"},
                        ],
                    },
                    {
                        "completedDate": "2019-06-10",
                        "testResult": "PASSED",
                        "odometerValue": "61800",
                        "odometerUnit": "mi",
                        "motTestNumber": "1500004",
                        "expiryDate": "2020-06-09",
                        "defects": [
                            {"type": "ADVISORY", "text": "Oil leak from engine but not excessive"},
                            {"type": "ADVISORY", "text": "Offside front suspension arm ball joint worn but not excessively"},
                            {"type": "ADVISORY", "text": "Exhaust mounting corroded"},
                        ],
                    },
                    {
                        "completedDate": "2020-06-08",
                        "testResult": "PASSED",
                        "odometerValue": "68200",
                        "odometerUnit": "mi",
                        "motTestNumber": "1500005",
                        "expiryDate": "2021-06-07",
                        "defects": [
                            {"type": "ADVISORY", "text": "Oil leak from engine but not excessive"},
                            {"type": "ADVISORY", "text": "Offside front suspension arm ball joint worn but not excessively"},
                            {"type": "ADVISORY", "text": "Nearside front suspension arm ball joint worn but not excessively"},
                            {"type": "ADVISORY", "text": "Exhaust mounting corroded"},
                        ],
                    },
                    {
                        "completedDate": "2021-06-05",
                        "testResult": "PASSED",
                        "odometerValue": "74500",
                        "odometerUnit": "mi",
                        "motTestNumber": "1500006",
                        "expiryDate": "2022-06-04",
                        "defects": [
                            {"type": "ADVISORY", "text": "Oil leak from engine but not excessive"},
                            {"type": "ADVISORY", "text": "Both front suspension arm ball joints worn but not excessively"},
                            {"type": "ADVISORY", "text": "Exhaust mounting corroded"},
                            {"type": "ADVISORY", "text": "Nearside front brake disc worn but above legal limit"},
                        ],
                    },
                    {
                        "completedDate": "2022-06-02",
                        "testResult": "PASSED",
                        "odometerValue": "81200",
                        "odometerUnit": "mi",
                        "motTestNumber": "1500007",
                        "expiryDate": "2023-06-01",
                        "defects": [
                            {"type": "ADVISORY", "text": "Oil leak from engine but not excessive"},
                            {"type": "ADVISORY", "text": "Both front suspension arm ball joints worn but not excessively"},
                            {"type": "ADVISORY", "text": "Offside rear shock absorber has light misting of oil"},
                            {"type": "ADVISORY", "text": "Exhaust corroded but no leak"},
                        ],
                    },
                    {
                        "completedDate": "2023-05-30",
                        "testResult": "PASSED",
                        "odometerValue": "87800",
                        "odometerUnit": "mi",
                        "motTestNumber": "1500008",
                        "expiryDate": "2024-05-29",
                        "defects": [
                            {"type": "ADVISORY", "text": "Oil leak from engine but not excessive"},
                            {"type": "ADVISORY", "text": "Both front suspension arm ball joints worn but not excessively"},
                            {"type": "ADVISORY", "text": "Offside rear shock absorber has light misting of oil"},
                            {"type": "ADVISORY", "text": "Exhaust corroded but no leak"},
                            {"type": "ADVISORY", "text": "Nearside rear tyre worn close to legal limit"},
                        ],
                    },
                    {
                        "completedDate": "2024-05-27",
                        "testResult": "PASSED",
                        "odometerValue": "93500",
                        "odometerUnit": "mi",
                        "motTestNumber": "1500009",
                        "expiryDate": "2025-05-26",
                        "defects": [
                            {"type": "ADVISORY", "text": "Oil leak from engine but not excessive"},
                            {"type": "ADVISORY", "text": "Both front suspension arm ball joints worn but not excessively"},
                            {"type": "ADVISORY", "text": "Exhaust corroded"},
                            {"type": "ADVISORY", "text": "Nearside rear coil spring corroded"},
                        ],
                    },
                    {
                        "completedDate": "2025-06-08",
                        "testResult": "PASSED",
                        "odometerValue": "99100",
                        "odometerUnit": "mi",
                        "motTestNumber": "1500010",
                        "expiryDate": "2026-06-07",
                        "defects": [
                            {"type": "ADVISORY", "text": "Oil leak from engine but not excessive"},
                            {"type": "ADVISORY", "text": "Both front suspension arm ball joints worn but not excessively"},
                            {"type": "ADVISORY", "text": "Exhaust corroded and deteriorated"},
                            {"type": "ADVISORY", "text": "Nearside rear coil spring corroded"},
                            {"type": "ADVISORY", "text": "Offside rear coil spring corroded"},
                        ],
                    },
                ],
            }
        ],
    ),

    # =========================================================================
    # XF20HIJ: 2020 Skoda Octavia petrol, fleet car, very consistent high mileage
    # =========================================================================
    "XF20HIJ": (
        {
            "registrationNumber": "XF20HIJ",
            "make": "SKODA",
            "colour": "GREY",
            "fuelType": "PETROL",
            "yearOfManufacture": 2020,
            "engineCapacity": 1498,
            "co2Emissions": 125,
            "euroStatus": "Euro 6",
            "taxStatus": "Taxed",
            "taxDueDate": "2026-03-01",
            "motStatus": "Valid",
            "motExpiryDate": "2026-03-18",
            "dateOfLastV5CIssued": "2024-11-22",
            "markedForExport": False,
            "typeApproval": "M1",
            "wheelplan": "2 AXLE RIGID BODY",
            "monthOfFirstRegistration": "2020-03",
        },
        [
            {
                "registration": "XF20HIJ",
                "make": "SKODA",
                "model": "OCTAVIA",
                "firstUsedDate": "2020.03.12",
                "motTests": [
                    {
                        "completedDate": "2023-03-10",
                        "testResult": "PASSED",
                        "odometerValue": "62400",
                        "odometerUnit": "mi",
                        "motTestNumber": "1600001",
                        "expiryDate": "2024-03-09",
                        "defects": [
                            {"type": "ADVISORY", "text": "Nearside front tyre worn close to legal limit"},
                            {"type": "ADVISORY", "text": "Offside front tyre worn close to legal limit"},
                        ],
                    },
                    {
                        "completedDate": "2024-03-07",
                        "testResult": "PASSED",
                        "odometerValue": "84200",
                        "odometerUnit": "mi",
                        "motTestNumber": "1600002",
                        "expiryDate": "2025-03-06",
                        "defects": [
                            {"type": "ADVISORY", "text": "Nearside front brake disc worn but above legal limit"},
                            {"type": "ADVISORY", "text": "Offside front brake disc worn but above legal limit"},
                            {"type": "ADVISORY", "text": "Both front tyres worn close to legal limit"},
                        ],
                    },
                    {
                        "completedDate": "2025-03-16",
                        "testResult": "PASSED",
                        "odometerValue": "106800",
                        "odometerUnit": "mi",
                        "motTestNumber": "1600003",
                        "expiryDate": "2026-03-15",
                        "defects": [
                            {"type": "ADVISORY", "text": "Nearside front brake disc worn but above legal limit"},
                            {"type": "ADVISORY", "text": "Offside front brake disc worn but above legal limit"},
                            {"type": "ADVISORY", "text": "Nearside front tyre worn close to legal limit"},
                        ],
                    },
                ],
            }
        ],
    ),

    # =========================================================================
    # YG16KLN: 2016 Mazda CX-5 diesel, recent V5C reissue (suspicious),
    # moderate issues
    # =========================================================================
    "YG16KLN": (
        {
            "registrationNumber": "YG16KLN",
            "make": "MAZDA",
            "colour": "RED",
            "fuelType": "DIESEL",
            "yearOfManufacture": 2016,
            "engineCapacity": 2191,
            "co2Emissions": 139,
            "euroStatus": "Euro 6",
            "taxStatus": "Taxed",
            "taxDueDate": "2026-08-01",
            "motStatus": "Valid",
            "motExpiryDate": "2026-05-28",
            "dateOfLastV5CIssued": "2025-12-02",
            "markedForExport": False,
            "typeApproval": "M1",
            "wheelplan": "2 AXLE RIGID BODY",
            "monthOfFirstRegistration": "2016-06",
        },
        [
            {
                "registration": "YG16KLN",
                "make": "MAZDA",
                "model": "CX-5",
                "firstUsedDate": "2016.06.15",
                "motTests": [
                    {
                        "completedDate": "2019-06-13",
                        "testResult": "PASSED",
                        "odometerValue": "31200",
                        "odometerUnit": "mi",
                        "motTestNumber": "1700001",
                        "expiryDate": "2020-06-12",
                        "defects": [],
                    },
                    {
                        "completedDate": "2020-06-10",
                        "testResult": "PASSED",
                        "odometerValue": "43500",
                        "odometerUnit": "mi",
                        "motTestNumber": "1700002",
                        "expiryDate": "2021-06-09",
                        "defects": [
                            {"type": "ADVISORY", "text": "Offside front brake disc worn but above legal limit"},
                        ],
                    },
                    {
                        "completedDate": "2021-06-07",
                        "testResult": "PASSED",
                        "odometerValue": "55800",
                        "odometerUnit": "mi",
                        "motTestNumber": "1700003",
                        "expiryDate": "2022-06-06",
                        "defects": [
                            {"type": "ADVISORY", "text": "Offside front brake disc worn but above legal limit"},
                            {"type": "ADVISORY", "text": "Nearside front brake disc worn but above legal limit"},
                        ],
                    },
                    {
                        "completedDate": "2022-06-04",
                        "testResult": "FAILED",
                        "odometerValue": "67200",
                        "odometerUnit": "mi",
                        "motTestNumber": "1700004",
                        "defects": [
                            {"type": "MAJOR", "text": "Offside front brake disc excessively worn"},
                            {"type": "ADVISORY", "text": "Nearside front brake disc worn but above legal limit"},
                            {"type": "ADVISORY", "text": "Exhaust mounting corroded"},
                        ],
                    },
                    {
                        "completedDate": "2022-06-08",
                        "testResult": "PASSED",
                        "odometerValue": "67220",
                        "odometerUnit": "mi",
                        "motTestNumber": "1700005",
                        "expiryDate": "2023-06-07",
                        "defects": [
                            {"type": "ADVISORY", "text": "Nearside front brake disc worn but above legal limit"},
                            {"type": "ADVISORY", "text": "Exhaust mounting corroded"},
                        ],
                    },
                    {
                        "completedDate": "2023-06-05",
                        "testResult": "PASSED",
                        "odometerValue": "78500",
                        "odometerUnit": "mi",
                        "motTestNumber": "1700006",
                        "expiryDate": "2024-06-04",
                        "defects": [
                            {"type": "ADVISORY", "text": "Exhaust corroded"},
                            {"type": "ADVISORY", "text": "Nearside rear shock absorber has light misting of oil"},
                        ],
                    },
                    {
                        "completedDate": "2024-06-02",
                        "testResult": "PASSED",
                        "odometerValue": "89800",
                        "odometerUnit": "mi",
                        "motTestNumber": "1700007",
                        "expiryDate": "2025-06-01",
                        "defects": [
                            {"type": "ADVISORY", "text": "Exhaust corroded and deteriorated"},
                            {"type": "ADVISORY", "text": "Nearside rear coil spring corroded"},
                        ],
                    },
                    {
                        "completedDate": "2025-05-26",
                        "testResult": "PASSED",
                        "odometerValue": "101200",
                        "odometerUnit": "mi",
                        "motTestNumber": "1700008",
                        "expiryDate": "2026-05-25",
                        "defects": [
                            {"type": "ADVISORY", "text": "Exhaust corroded and deteriorated"},
                            {"type": "ADVISORY", "text": "Nearside rear coil spring corroded"},
                            {"type": "ADVISORY", "text": "Offside rear coil spring corroded"},
                        ],
                    },
                ],
            }
        ],
    ),

    # =========================================================================
    # ZH69OPQ: 2019 Seat Leon petrol, very clean, low owner count feel
    # =========================================================================
    "ZH69OPQ": (
        {
            "registrationNumber": "ZH69OPQ",
            "make": "SEAT",
            "colour": "WHITE",
            "fuelType": "PETROL",
            "yearOfManufacture": 2019,
            "engineCapacity": 1498,
            "co2Emissions": 120,
            "euroStatus": "Euro 6",
            "taxStatus": "Taxed",
            "taxDueDate": "2026-12-01",
            "motStatus": "Valid",
            "motExpiryDate": "2026-11-05",
            "dateOfLastV5CIssued": "2021-02-14",
            "markedForExport": False,
            "typeApproval": "M1",
            "wheelplan": "2 AXLE RIGID BODY",
            "monthOfFirstRegistration": "2019-09",
        },
        [
            {
                "registration": "ZH69OPQ",
                "make": "SEAT",
                "model": "LEON",
                "firstUsedDate": "2019.09.18",
                "motTests": [
                    {
                        "completedDate": "2022-09-16",
                        "testResult": "PASSED",
                        "odometerValue": "19800",
                        "odometerUnit": "mi",
                        "motTestNumber": "1800001",
                        "expiryDate": "2023-09-15",
                        "defects": [],
                    },
                    {
                        "completedDate": "2023-09-13",
                        "testResult": "PASSED",
                        "odometerValue": "27400",
                        "odometerUnit": "mi",
                        "motTestNumber": "1800002",
                        "expiryDate": "2024-09-12",
                        "defects": [],
                    },
                    {
                        "completedDate": "2024-09-10",
                        "testResult": "PASSED",
                        "odometerValue": "35100",
                        "odometerUnit": "mi",
                        "motTestNumber": "1800003",
                        "expiryDate": "2025-09-09",
                        "defects": [
                            {"type": "ADVISORY", "text": "Nearside front tyre slightly worn on outer edge"},
                        ],
                    },
                    {
                        "completedDate": "2025-11-03",
                        "testResult": "PASSED",
                        "odometerValue": "43600",
                        "odometerUnit": "mi",
                        "motTestNumber": "1800004",
                        "expiryDate": "2026-11-02",
                        "defects": [],
                    },
                ],
            }
        ],
    ),

    # =========================================================================
    # AJ11RST: 2011 Ford Focus diesel, old workhorse, passed every MOT
    # with advisories
    # =========================================================================
    "AJ11RST": (
        {
            "registrationNumber": "AJ11RST",
            "make": "FORD",
            "colour": "SILVER",
            "fuelType": "DIESEL",
            "yearOfManufacture": 2011,
            "engineCapacity": 1560,
            "co2Emissions": 109,
            "euroStatus": "Euro 5",
            "taxStatus": "Taxed",
            "taxDueDate": "2026-07-01",
            "motStatus": "Valid",
            "motExpiryDate": "2026-02-28",
            "dateOfLastV5CIssued": "2018-10-30",
            "markedForExport": False,
            "typeApproval": "M1",
            "wheelplan": "2 AXLE RIGID BODY",
            "monthOfFirstRegistration": "2011-03",
        },
        [
            {
                "registration": "AJ11RST",
                "make": "FORD",
                "model": "FOCUS",
                "firstUsedDate": "2011.03.20",
                "motTests": [
                    {
                        "completedDate": "2014-03-18",
                        "testResult": "PASSED",
                        "odometerValue": "36200",
                        "odometerUnit": "mi",
                        "motTestNumber": "1900001",
                        "expiryDate": "2015-03-17",
                        "defects": [
                            {"type": "ADVISORY", "text": "Offside rear tyre slightly worn"},
                        ],
                    },
                    {
                        "completedDate": "2015-03-16",
                        "testResult": "PASSED",
                        "odometerValue": "48500",
                        "odometerUnit": "mi",
                        "motTestNumber": "1900002",
                        "expiryDate": "2016-03-15",
                        "defects": [
                            {"type": "ADVISORY", "text": "Nearside front brake disc worn but above legal limit"},
                        ],
                    },
                    {
                        "completedDate": "2016-03-14",
                        "testResult": "PASSED",
                        "odometerValue": "60100",
                        "odometerUnit": "mi",
                        "motTestNumber": "1900003",
                        "expiryDate": "2017-03-13",
                        "defects": [
                            {"type": "ADVISORY", "text": "Nearside front brake disc worn but above legal limit"},
                            {"type": "ADVISORY", "text": "Exhaust mounting slightly deteriorated"},
                        ],
                    },
                    {
                        "completedDate": "2017-03-12",
                        "testResult": "PASSED",
                        "odometerValue": "71800",
                        "odometerUnit": "mi",
                        "motTestNumber": "1900004",
                        "expiryDate": "2018-03-11",
                        "defects": [
                            {"type": "ADVISORY", "text": "Both front brake discs worn but above legal limit"},
                            {"type": "ADVISORY", "text": "Exhaust mounting corroded"},
                        ],
                    },
                    {
                        "completedDate": "2018-03-10",
                        "testResult": "PASSED",
                        "odometerValue": "83200",
                        "odometerUnit": "mi",
                        "motTestNumber": "1900005",
                        "expiryDate": "2019-03-09",
                        "defects": [
                            {"type": "ADVISORY", "text": "Offside front suspension arm ball joint worn but not excessively"},
                            {"type": "ADVISORY", "text": "Exhaust mounting corroded"},
                        ],
                    },
                    {
                        "completedDate": "2019-03-08",
                        "testResult": "PASSED",
                        "odometerValue": "94600",
                        "odometerUnit": "mi",
                        "motTestNumber": "1900006",
                        "expiryDate": "2020-03-07",
                        "defects": [
                            {"type": "ADVISORY", "text": "Offside front suspension arm ball joint worn but not excessively"},
                            {"type": "ADVISORY", "text": "Nearside front suspension arm ball joint worn but not excessively"},
                            {"type": "ADVISORY", "text": "Exhaust corroded"},
                        ],
                    },
                    {
                        "completedDate": "2020-03-05",
                        "testResult": "PASSED",
                        "odometerValue": "105800",
                        "odometerUnit": "mi",
                        "motTestNumber": "1900007",
                        "expiryDate": "2021-03-04",
                        "defects": [
                            {"type": "ADVISORY", "text": "Both front suspension arm ball joints worn but not excessively"},
                            {"type": "ADVISORY", "text": "Exhaust corroded"},
                            {"type": "ADVISORY", "text": "Nearside rear coil spring corroded"},
                        ],
                    },
                    {
                        "completedDate": "2021-03-03",
                        "testResult": "PASSED",
                        "odometerValue": "114200",
                        "odometerUnit": "mi",
                        "motTestNumber": "1900008",
                        "expiryDate": "2022-03-02",
                        "defects": [
                            {"type": "ADVISORY", "text": "Both front suspension arm ball joints worn but not excessively"},
                            {"type": "ADVISORY", "text": "Exhaust corroded and deteriorated"},
                            {"type": "ADVISORY", "text": "Nearside rear coil spring corroded"},
                            {"type": "ADVISORY", "text": "Offside rear coil spring corroded"},
                        ],
                    },
                    {
                        "completedDate": "2022-03-01",
                        "testResult": "PASSED",
                        "odometerValue": "122500",
                        "odometerUnit": "mi",
                        "motTestNumber": "1900009",
                        "expiryDate": "2023-02-28",
                        "defects": [
                            {"type": "ADVISORY", "text": "Both front suspension arm ball joints worn but not excessively"},
                            {"type": "ADVISORY", "text": "Exhaust corroded and deteriorated"},
                            {"type": "ADVISORY", "text": "Both rear coil springs corroded"},
                        ],
                    },
                    {
                        "completedDate": "2023-02-27",
                        "testResult": "PASSED",
                        "odometerValue": "130100",
                        "odometerUnit": "mi",
                        "motTestNumber": "1900010",
                        "expiryDate": "2024-02-26",
                        "defects": [
                            {"type": "ADVISORY", "text": "Both front suspension arm ball joints worn but not excessively"},
                            {"type": "ADVISORY", "text": "Exhaust corroded and deteriorated"},
                            {"type": "ADVISORY", "text": "Both rear coil springs corroded"},
                            {"type": "ADVISORY", "text": "Offside rear shock absorber has light misting of oil"},
                        ],
                    },
                    {
                        "completedDate": "2024-02-25",
                        "testResult": "PASSED",
                        "odometerValue": "137800",
                        "odometerUnit": "mi",
                        "motTestNumber": "1900011",
                        "expiryDate": "2025-02-24",
                        "defects": [
                            {"type": "ADVISORY", "text": "Both front suspension arm ball joints worn but not excessively"},
                            {"type": "ADVISORY", "text": "Exhaust corroded and deteriorated"},
                            {"type": "ADVISORY", "text": "Both rear coil springs corroded"},
                            {"type": "ADVISORY", "text": "Offside rear shock absorber has light misting of oil"},
                            {"type": "ADVISORY", "text": "Nearside rear brake disc worn but above legal limit"},
                        ],
                    },
                    {
                        "completedDate": "2025-02-26",
                        "testResult": "PASSED",
                        "odometerValue": "145200",
                        "odometerUnit": "mi",
                        "motTestNumber": "1900012",
                        "expiryDate": "2026-02-25",
                        "defects": [
                            {"type": "ADVISORY", "text": "Both front suspension arm ball joints worn but not excessively"},
                            {"type": "ADVISORY", "text": "Exhaust corroded and deteriorated"},
                            {"type": "ADVISORY", "text": "Both rear coil springs corroded"},
                            {"type": "ADVISORY", "text": "Offside rear shock absorber has light misting of oil"},
                            {"type": "ADVISORY", "text": "Both rear brake discs worn but above legal limit"},
                        ],
                    },
                ],
            }
        ],
    ),

    # =========================================================================
    # BK23UVW: 2023 MG4 electric, brand new, only 1 MOT
    # =========================================================================
    "BK23UVW": (
        {
            "registrationNumber": "BK23UVW",
            "make": "MG",
            "colour": "BLUE",
            "fuelType": "ELECTRICITY",
            "yearOfManufacture": 2023,
            "engineCapacity": 0,
            "co2Emissions": 0,
            "euroStatus": None,
            "taxStatus": "Taxed",
            "taxDueDate": "2026-09-01",
            "motStatus": "Valid",
            "motExpiryDate": "2026-09-22",
            "dateOfLastV5CIssued": "2023-09-10",
            "markedForExport": False,
            "typeApproval": "M1",
            "wheelplan": "2 AXLE RIGID BODY",
            "monthOfFirstRegistration": "2023-09",
        },
        [
            {
                "registration": "BK23UVW",
                "make": "MG",
                "model": "MG4",
                "firstUsedDate": "2023.09.10",
                "motTests": [
                    {
                        "completedDate": "2025-09-20",
                        "testResult": "PASSED",
                        "odometerValue": "14200",
                        "odometerUnit": "mi",
                        "motTestNumber": "2000001",
                        "expiryDate": "2026-09-19",
                        "defects": [],
                    },
                ],
            }
        ],
    ),

    # =========================================================================
    # CL65XYZ: 2015 Jaguar XE diesel, premium but troubled
    # (multiple failures, corrosion)
    # =========================================================================
    "CL65XYZ": (
        {
            "registrationNumber": "CL65XYZ",
            "make": "JAGUAR",
            "colour": "GREY",
            "fuelType": "DIESEL",
            "yearOfManufacture": 2015,
            "engineCapacity": 1999,
            "co2Emissions": 109,
            "euroStatus": "Euro 6",
            "taxStatus": "Taxed",
            "taxDueDate": "2026-01-01",
            "motStatus": "Valid",
            "motExpiryDate": "2026-03-15",
            "dateOfLastV5CIssued": "2024-05-14",
            "markedForExport": False,
            "typeApproval": "M1",
            "wheelplan": "2 AXLE RIGID BODY",
            "monthOfFirstRegistration": "2015-09",
        },
        [
            {
                "registration": "CL65XYZ",
                "make": "JAGUAR",
                "model": "XE",
                "firstUsedDate": "2015.09.28",
                "motTests": [
                    {
                        "completedDate": "2018-09-26",
                        "testResult": "PASSED",
                        "odometerValue": "34500",
                        "odometerUnit": "mi",
                        "motTestNumber": "2100001",
                        "expiryDate": "2019-09-25",
                        "defects": [
                            {"type": "ADVISORY", "text": "Nearside front brake disc worn but above legal limit"},
                        ],
                    },
                    {
                        "completedDate": "2019-09-23",
                        "testResult": "FAILED",
                        "odometerValue": "48200",
                        "odometerUnit": "mi",
                        "motTestNumber": "2100002",
                        "defects": [
                            {"type": "MAJOR", "text": "Nearside front brake disc excessively worn"},
                            {"type": "MAJOR", "text": "Offside front brake disc excessively worn"},
                            {"type": "ADVISORY", "text": "Offside front suspension arm corroded"},
                        ],
                    },
                    {
                        "completedDate": "2019-09-28",
                        "testResult": "PASSED",
                        "odometerValue": "48220",
                        "odometerUnit": "mi",
                        "motTestNumber": "2100003",
                        "expiryDate": "2020-09-27",
                        "defects": [
                            {"type": "ADVISORY", "text": "Offside front suspension arm corroded"},
                        ],
                    },
                    {
                        "completedDate": "2020-09-25",
                        "testResult": "PASSED",
                        "odometerValue": "58600",
                        "odometerUnit": "mi",
                        "motTestNumber": "2100004",
                        "expiryDate": "2021-09-24",
                        "defects": [
                            {"type": "ADVISORY", "text": "Offside front suspension arm corroded"},
                            {"type": "ADVISORY", "text": "Nearside front suspension arm corroded"},
                            {"type": "ADVISORY", "text": "Exhaust mounting corroded"},
                        ],
                    },
                    {
                        "completedDate": "2021-09-22",
                        "testResult": "FAILED",
                        "odometerValue": "68500",
                        "odometerUnit": "mi",
                        "motTestNumber": "2100005",
                        "defects": [
                            {"type": "MAJOR", "text": "Nearside front lower suspension arm excessively corroded"},
                            {"type": "MAJOR", "text": "Offside rear brake disc excessively worn"},
                            {"type": "ADVISORY", "text": "Offside front lower suspension arm corroded"},
                            {"type": "ADVISORY", "text": "Exhaust corroded"},
                        ],
                    },
                    {
                        "completedDate": "2021-09-29",
                        "testResult": "PASSED",
                        "odometerValue": "68530",
                        "odometerUnit": "mi",
                        "motTestNumber": "2100006",
                        "expiryDate": "2022-09-28",
                        "defects": [
                            {"type": "ADVISORY", "text": "Offside front lower suspension arm corroded"},
                            {"type": "ADVISORY", "text": "Exhaust corroded"},
                        ],
                    },
                    {
                        "completedDate": "2022-09-26",
                        "testResult": "FAILED",
                        "odometerValue": "78100",
                        "odometerUnit": "mi",
                        "motTestNumber": "2100007",
                        "defects": [
                            {"type": "MAJOR", "text": "Offside front lower suspension arm excessively corroded"},
                            {"type": "MAJOR", "text": "Nearside rear subframe corroded to the extent that the structural integrity is significantly reduced"},
                            {"type": "ADVISORY", "text": "Exhaust corroded and deteriorated"},
                        ],
                    },
                    {
                        "completedDate": "2022-10-04",
                        "testResult": "PASSED",
                        "odometerValue": "78130",
                        "odometerUnit": "mi",
                        "motTestNumber": "2100008",
                        "expiryDate": "2023-10-03",
                        "defects": [
                            {"type": "ADVISORY", "text": "Exhaust corroded and deteriorated"},
                        ],
                    },
                    {
                        "completedDate": "2023-10-01",
                        "testResult": "PASSED",
                        "odometerValue": "87400",
                        "odometerUnit": "mi",
                        "motTestNumber": "2100009",
                        "expiryDate": "2024-09-30",
                        "defects": [
                            {"type": "ADVISORY", "text": "Nearside front suspension arm corroded"},
                            {"type": "ADVISORY", "text": "Exhaust corroded and deteriorated"},
                            {"type": "ADVISORY", "text": "Nearside rear brake disc worn but above legal limit"},
                        ],
                    },
                    {
                        "completedDate": "2024-09-28",
                        "testResult": "FAILED",
                        "odometerValue": "96200",
                        "odometerUnit": "mi",
                        "motTestNumber": "2100010",
                        "defects": [
                            {"type": "MAJOR", "text": "Nearside front lower suspension arm excessively corroded"},
                            {"type": "MAJOR", "text": "Exhaust has a major leak of exhaust gases"},
                            {"type": "ADVISORY", "text": "Nearside rear brake disc worn but above legal limit"},
                            {"type": "ADVISORY", "text": "Offside rear brake disc worn but above legal limit"},
                        ],
                    },
                    {
                        "completedDate": "2024-10-05",
                        "testResult": "PASSED",
                        "odometerValue": "96230",
                        "odometerUnit": "mi",
                        "motTestNumber": "2100011",
                        "expiryDate": "2025-10-04",
                        "defects": [
                            {"type": "ADVISORY", "text": "Nearside rear brake disc worn but above legal limit"},
                            {"type": "ADVISORY", "text": "Offside rear brake disc worn but above legal limit"},
                        ],
                    },
                    {
                        "completedDate": "2025-03-13",
                        "testResult": "PASSED",
                        "odometerValue": "101800",
                        "odometerUnit": "mi",
                        "motTestNumber": "2100012",
                        "expiryDate": "2026-03-12",
                        "defects": [
                            {"type": "ADVISORY", "text": "Both rear brake discs worn but above legal limit"},
                            {"type": "ADVISORY", "text": "Nearside front suspension arm corroded"},
                            {"type": "ADVISORY", "text": "Exhaust corroded"},
                        ],
                    },
                ],
            }
        ],
    ),

    # =========================================================================
    # DM08ABC: 2008 Toyota Corolla petrol, Euro 4, borderline ULEZ,
    # ancient but reliable
    # =========================================================================
    "DM08ABC": (
        {
            "registrationNumber": "DM08ABC",
            "make": "TOYOTA",
            "colour": "SILVER",
            "fuelType": "PETROL",
            "yearOfManufacture": 2008,
            "engineCapacity": 1598,
            "co2Emissions": 163,
            "euroStatus": "Euro 4",
            "taxStatus": "Taxed",
            "taxDueDate": "2026-04-01",
            "motStatus": "Valid",
            "motExpiryDate": "2026-05-10",
            "dateOfLastV5CIssued": "2016-03-22",
            "markedForExport": False,
            "typeApproval": "M1",
            "wheelplan": "2 AXLE RIGID BODY",
            "monthOfFirstRegistration": "2008-06",
        },
        [
            {
                "registration": "DM08ABC",
                "make": "TOYOTA",
                "model": "COROLLA",
                "firstUsedDate": "2008.06.15",
                "motTests": [
                    {
                        "completedDate": "2011-06-13",
                        "testResult": "PASSED",
                        "odometerValue": "28500",
                        "odometerUnit": "mi",
                        "motTestNumber": "2200001",
                        "expiryDate": "2012-06-12",
                        "defects": [],
                    },
                    {
                        "completedDate": "2012-06-10",
                        "testResult": "PASSED",
                        "odometerValue": "38200",
                        "odometerUnit": "mi",
                        "motTestNumber": "2200002",
                        "expiryDate": "2013-06-09",
                        "defects": [
                            {"type": "ADVISORY", "text": "Nearside front tyre slightly worn"},
                        ],
                    },
                    {
                        "completedDate": "2013-06-07",
                        "testResult": "PASSED",
                        "odometerValue": "47800",
                        "odometerUnit": "mi",
                        "motTestNumber": "2200003",
                        "expiryDate": "2014-06-06",
                        "defects": [
                            {"type": "ADVISORY", "text": "Offside rear brake pad wearing thin but above legal limit"},
                        ],
                    },
                    {
                        "completedDate": "2014-06-05",
                        "testResult": "PASSED",
                        "odometerValue": "57100",
                        "odometerUnit": "mi",
                        "motTestNumber": "2200004",
                        "expiryDate": "2015-06-04",
                        "defects": [
                            {"type": "ADVISORY", "text": "Offside front brake disc worn but above legal limit"},
                        ],
                    },
                    {
                        "completedDate": "2015-06-03",
                        "testResult": "PASSED",
                        "odometerValue": "66400",
                        "odometerUnit": "mi",
                        "motTestNumber": "2200005",
                        "expiryDate": "2016-06-02",
                        "defects": [
                            {"type": "ADVISORY", "text": "Offside front brake disc worn but above legal limit"},
                            {"type": "ADVISORY", "text": "Nearside front brake disc worn but above legal limit"},
                        ],
                    },
                    {
                        "completedDate": "2016-06-01",
                        "testResult": "PASSED",
                        "odometerValue": "75200",
                        "odometerUnit": "mi",
                        "motTestNumber": "2200006",
                        "expiryDate": "2017-05-31",
                        "defects": [
                            {"type": "ADVISORY", "text": "Exhaust mounting slightly deteriorated"},
                        ],
                    },
                    {
                        "completedDate": "2017-05-30",
                        "testResult": "PASSED",
                        "odometerValue": "83800",
                        "odometerUnit": "mi",
                        "motTestNumber": "2200007",
                        "expiryDate": "2018-05-29",
                        "defects": [
                            {"type": "ADVISORY", "text": "Exhaust mounting corroded"},
                            {"type": "ADVISORY", "text": "Nearside rear tyre worn close to legal limit"},
                        ],
                    },
                    {
                        "completedDate": "2018-05-28",
                        "testResult": "PASSED",
                        "odometerValue": "92100",
                        "odometerUnit": "mi",
                        "motTestNumber": "2200008",
                        "expiryDate": "2019-05-27",
                        "defects": [
                            {"type": "ADVISORY", "text": "Exhaust mounting corroded"},
                            {"type": "ADVISORY", "text": "Offside front suspension arm ball joint worn but not excessively"},
                        ],
                    },
                    {
                        "completedDate": "2019-05-26",
                        "testResult": "PASSED",
                        "odometerValue": "100500",
                        "odometerUnit": "mi",
                        "motTestNumber": "2200009",
                        "expiryDate": "2020-05-25",
                        "defects": [
                            {"type": "ADVISORY", "text": "Exhaust corroded"},
                            {"type": "ADVISORY", "text": "Offside front suspension arm ball joint worn but not excessively"},
                        ],
                    },
                    {
                        "completedDate": "2020-05-24",
                        "testResult": "PASSED",
                        "odometerValue": "107200",
                        "odometerUnit": "mi",
                        "motTestNumber": "2200010",
                        "expiryDate": "2021-05-23",
                        "defects": [
                            {"type": "ADVISORY", "text": "Exhaust corroded"},
                            {"type": "ADVISORY", "text": "Both front suspension arm ball joints worn but not excessively"},
                            {"type": "ADVISORY", "text": "Nearside rear coil spring corroded"},
                        ],
                    },
                    {
                        "completedDate": "2021-05-22",
                        "testResult": "PASSED",
                        "odometerValue": "113800",
                        "odometerUnit": "mi",
                        "motTestNumber": "2200011",
                        "expiryDate": "2022-05-21",
                        "defects": [
                            {"type": "ADVISORY", "text": "Exhaust corroded and deteriorated"},
                            {"type": "ADVISORY", "text": "Both front suspension arm ball joints worn but not excessively"},
                            {"type": "ADVISORY", "text": "Both rear coil springs corroded"},
                        ],
                    },
                    {
                        "completedDate": "2022-05-20",
                        "testResult": "PASSED",
                        "odometerValue": "120400",
                        "odometerUnit": "mi",
                        "motTestNumber": "2200012",
                        "expiryDate": "2023-05-19",
                        "defects": [
                            {"type": "ADVISORY", "text": "Exhaust corroded and deteriorated"},
                            {"type": "ADVISORY", "text": "Both front suspension arm ball joints worn but not excessively"},
                            {"type": "ADVISORY", "text": "Both rear coil springs corroded"},
                            {"type": "ADVISORY", "text": "Offside rear shock absorber has light misting of oil"},
                        ],
                    },
                    {
                        "completedDate": "2023-05-18",
                        "testResult": "PASSED",
                        "odometerValue": "126500",
                        "odometerUnit": "mi",
                        "motTestNumber": "2200013",
                        "expiryDate": "2024-05-17",
                        "defects": [
                            {"type": "ADVISORY", "text": "Exhaust corroded and deteriorated"},
                            {"type": "ADVISORY", "text": "Both front suspension arm ball joints worn but not excessively"},
                            {"type": "ADVISORY", "text": "Both rear coil springs corroded"},
                            {"type": "ADVISORY", "text": "Offside rear shock absorber has light misting of oil"},
                        ],
                    },
                    {
                        "completedDate": "2024-05-15",
                        "testResult": "PASSED",
                        "odometerValue": "132100",
                        "odometerUnit": "mi",
                        "motTestNumber": "2200014",
                        "expiryDate": "2025-05-14",
                        "defects": [
                            {"type": "ADVISORY", "text": "Exhaust corroded and deteriorated"},
                            {"type": "ADVISORY", "text": "Both front suspension arm ball joints worn but not excessively"},
                            {"type": "ADVISORY", "text": "Both rear coil springs corroded"},
                            {"type": "ADVISORY", "text": "Both rear shock absorbers have light misting of oil"},
                        ],
                    },
                    {
                        "completedDate": "2025-05-08",
                        "testResult": "PASSED",
                        "odometerValue": "137800",
                        "odometerUnit": "mi",
                        "motTestNumber": "2200015",
                        "expiryDate": "2026-05-07",
                        "defects": [
                            {"type": "ADVISORY", "text": "Exhaust corroded and deteriorated"},
                            {"type": "ADVISORY", "text": "Both front suspension arm ball joints worn but not excessively"},
                            {"type": "ADVISORY", "text": "Both rear coil springs corroded"},
                            {"type": "ADVISORY", "text": "Both rear shock absorbers have light misting of oil"},
                            {"type": "ADVISORY", "text": "Nearside front tyre worn close to legal limit"},
                        ],
                    },
                ],
            }
        ],
    ),
}


def get_demo_data(registration: str) -> Optional[Tuple[Dict, List]]:
    """Return demo DVLA + MOT data for a registration, or None if not a demo reg."""
    return DEMO_VEHICLES.get(registration.upper().strip())
