#!/usr/bin/env python3
"""One-off script: fetch full DVSA MOT history for EA11OSE and enrich fixture.

Run once:
    python backend/fetch_ea11_mot.py
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from unittest.mock import AsyncMock

# Load .env from repo root
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, val = line.partition("=")
            os.environ.setdefault(key.strip(), val.strip())

sys.path.insert(0, str(Path(__file__).parent))


async def main():
    # Patch Redis cache to no-op so we don't need Docker running
    mock_cache = AsyncMock()
    mock_cache.get = AsyncMock(return_value=None)
    mock_cache.set = AsyncMock(return_value=None)

    import app.services.mot.client as mot_client_module
    original_cache = mot_client_module.cache
    mot_client_module.cache = mock_cache

    try:
        from app.services.mot.client import MOTClient
        from app.services.mot.analyzer import MOTAnalyzer

        client = MOTClient()
        print("Fetching MOT history for EA11OSE...")
        raw = await client.get_mot_history("EA11OSE")
        await client.close()
    finally:
        mot_client_module.cache = original_cache

    if not raw:
        print("ERROR: No MOT data returned. Check API credentials in .env")
        return

    analyzer = MOTAnalyzer()
    analysis = analyzer.analyze(raw)

    mot_tests = analysis.get("mot_tests", [])
    print(f"✓ Fetched {len(mot_tests)} MOT tests")

    fixture_path = Path(__file__).parent / "fixtures" / "EA11OSE_FULL_CHECK.json"
    with open(fixture_path) as f:
        fixture = json.load(f)

    fixture["mot_tests_full"] = mot_tests
    fixture["mileage_timeline"] = analysis.get("mileage_timeline", [])
    fixture["failure_patterns"] = analysis.get("failure_patterns", [])
    fixture["clocking_analysis"] = analysis.get("clocking_analysis", {})
    fixture["condition_score"] = analysis.get("condition_score")

    with open(fixture_path, "w") as f:
        json.dump(fixture, f, indent=2)

    print(f"✓ Fixture enriched: {fixture_path}")

    # Show a summary
    for test in mot_tests[:3]:
        total = len(test.get("advisories", [])) + len(test.get("failures", []))
        print(f"  {test['date']} {test['result']} {test.get('odometer', '?')} mi — {total} items")
    if len(mot_tests) > 3:
        print(f"  ... and {len(mot_tests) - 3} more tests")


if __name__ == "__main__":
    asyncio.run(main())
