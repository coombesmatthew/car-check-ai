"""AI report eval harness.

Generates a buyer's report for each fixture, scores the output against the
rubric with Claude Haiku, and writes markdown + scorecard JSON to
backend/tmp/reports/.

Run locally:
    python -m backend.scripts.eval_reports --all
    python -m backend.scripts.eval_reports --tier non_ev
    python -m backend.scripts.eval_reports --tier ev_complete
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path

import anthropic

# Make "app" importable when run via `python -m backend.scripts.eval_reports`
# or directly. We add the backend dir to sys.path.
BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.core.config import settings  # noqa: E402
from app.services.ai.report_generator import generate_ai_report  # noqa: E402
from app.services.ai.ev_report_generator import generate_ev_report  # noqa: E402

from _judge_rubric import AXES, JUDGE_SYSTEM_PROMPT, build_judge_user_prompt  # noqa: E402


FIXTURES_DIR = BACKEND_DIR / "fixtures"
OUT_DIR = BACKEND_DIR / "tmp" / "reports"

# Haiku 4.5 — cheap and deterministic enough for rubric scoring.
JUDGE_MODEL = "claude-haiku-4-5-20251001"


async def _run_non_ev(timestamp: str) -> tuple[str, str, tuple[int, int]]:
    """Generate the non-EV report from the EA11OSE fixture. Returns (label, md, word_range)."""
    fixture_path = FIXTURES_DIR / "EA11OSE_FULL_CHECK.json"
    data = json.loads(fixture_path.read_text())

    registration = data["registration"]
    vehicle_data = {
        "registrationNumber": registration,
        "make": data["vehicle_summary"]["make"],
        "model": data["vehicle_summary"]["model"],
        "yearOfManufacture": data["vehicle_summary"]["year"],
        "fuelType": data["vehicle_summary"]["fuel"],
        "co2Emissions": data["vehicle_summary"]["co2_emissions_g_km"],
        "engineCapacity": data["vehicle_summary"]["engine_cc"],
        "colour": data["vehicle_summary"]["colour"],
        "taxStatus": data["registration_info"]["tax_status"],
        "taxDueDate": data["registration_info"]["tax_due_date"],
        "motStatus": data["registration_info"]["mot_status"],
        "motExpiryDate": data["registration_info"]["mot_expiry_date"],
    }
    mot_analysis = {
        "mot_summary": {
            "registration": registration,
            "total_tests": data["mot_history"]["total_tests"],
            "total_passes": data["mot_history"]["total_passes"],
            "total_failures": data["mot_history"]["total_failures"],
            "current_odometer": data["mot_history"]["latest_test"]["odometer"],
            "first_used_date": data["mot_history"]["first_used_date"],
            "latest_test": data["mot_history"]["latest_test"],
        },
        "clocking_analysis": data.get("clocking_analysis", {"clocked": False, "risk_level": "low", "reason": ""}),
        "mileage_timeline": data.get("mileage_timeline", []),
        "failure_patterns": data.get("failure_patterns", []),
        "condition_score": data.get("condition_score", 80),
        "mot_tests": data.get("mot_tests_full", []),
    }
    ulez_data = {"compliant": True, "status": "Compliant", "reason": "Euro 5 diesel — passes ULEZ."}
    check_result = {
        "registration": registration,
        "tier": "premium",
        "vehicle": vehicle_data,
        "mot_summary": mot_analysis["mot_summary"],
        "tax_calculation": {
            "band": "B", "band_range": "101-110 g/km",
            "co2_emissions": data["vehicle_summary"]["co2_emissions_g_km"],
            "fuel_type": data["vehicle_summary"]["fuel"],
            "first_year_rate": 20, "annual_rate": 20, "six_month_rate": 10.0, "monthly_total": 20.0,
            "is_electric": False, "is_diesel": True,
            "tax_regime": "Pre-April 2017",
            "year_of_manufacture": data["vehicle_summary"]["year"],
        },
        "valuation": {
            "private_sale": data["premium_tier_data"]["brego_valuation"]["retail_average"],
            "dealer_forecourt": data["premium_tier_data"]["brego_valuation"]["retail_high"],
            "trade_in": data["premium_tier_data"]["brego_valuation"]["trade_average"],
            "part_exchange": data["premium_tier_data"]["brego_valuation"]["trade_high"],
            "valuation_date": data["premium_tier_data"]["brego_valuation"]["valuation_date"],
            "mileage_used": data["premium_tier_data"]["brego_valuation"]["current_mileage"],
            "condition": "Mileage-adjusted",
            "data_source": "Brego",
        },
        "keeper_history": {
            "total_keepers": data["premium_tier_data"]["experian_autocheck"].get("keeper_count", 1),
            "keepers": [],
        },
    }

    print(f"[non_ev] Generating report for {registration}...")
    report = await generate_ai_report(
        registration=registration,
        vehicle_data=vehicle_data,
        mot_analysis=mot_analysis,
        ulez_data=ulez_data,
        check_result=check_result,
    )
    if not report:
        raise RuntimeError("non_ev generation returned None")

    out_path = OUT_DIR / f"non_ev-{registration}-{timestamp}.md"
    out_path.write_text(report)
    print(f"[non_ev] Saved: {out_path}")
    # Non-EV output is table-heavy markdown (structured Pydantic render), so word
    # count sits 2-3× the EV prose target. 1500-4000 is the honest range.
    return ("non_ev", report, (1500, 4000))


async def _run_ev_fixture(timestamp: str, fixture_name: str, label: str) -> tuple[str, str, tuple[int, int]]:
    fixture_path = FIXTURES_DIR / fixture_name
    data = json.loads(fixture_path.read_text())

    print(f"[{label}] Generating report for {data['registration']}...")
    report = await generate_ev_report(
        registration=data["registration"],
        vehicle_data=data["vehicle_data"],
        mot_analysis=data["mot_analysis"],
        ev_check_data=data["ev_check_data"],
    )
    if not report:
        raise RuntimeError(f"{label} generation returned None")

    out_path = OUT_DIR / f"{label}-{data['registration']}-{timestamp}.md"
    out_path.write_text(report)
    print(f"[{label}] Saved: {out_path}")
    return (label, report, (800, 1400))


async def _run_ev_complete(timestamp: str) -> tuple[str, str, tuple[int, int]]:
    return await _run_ev_fixture(timestamp, "EV_TEST_VEHICLE.json", "ev_complete_tesla")


async def _run_ev_leaf(timestamp: str) -> tuple[str, str, tuple[int, int]]:
    return await _run_ev_fixture(timestamp, "EV_TEST_LEAF_2018.json", "ev_complete_leaf")


def _judge(report_markdown: str, tier_label: str, word_range: tuple[int, int]) -> dict:
    """Score a report via the Haiku judge. Returns parsed rubric dict."""
    client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    msg = client.messages.create(
        model=JUDGE_MODEL,
        max_tokens=1200,
        temperature=0,
        system=JUDGE_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": build_judge_user_prompt(report_markdown, tier_label, word_range)}],
    )
    raw = msg.content[0].text.strip()
    # Strip any accidental code fences
    if raw.startswith("```"):
        lines = raw.split("\n")
        raw = "\n".join(line for line in lines if not line.startswith("```"))
    return json.loads(raw)


def _print_scorecard(label: str, scorecard: dict) -> bool:
    """Print scorecard to stdout. Returns True if all axes >= 4."""
    print(f"\n=== {label.upper()} SCORECARD ===")
    all_passed = True
    for axis in AXES:
        score = scorecard.get(axis)
        reason = scorecard.get(f"reason_{axis}", "")
        mark = "OK " if (score or 0) >= 4 else "FAIL"
        if (score or 0) < 4:
            all_passed = False
        print(f"  [{mark}] {axis}: {score}/5 — {reason}")
    wc = scorecard.get("word_count", "?")
    print(f"  word_count: {wc}")
    return all_passed


async def main() -> int:
    parser = argparse.ArgumentParser(description="AI report eval harness")
    parser.add_argument(
        "--tier",
        choices=["non_ev", "ev_complete", "ev_leaf"],
        help="Run a single fixture",
    )
    parser.add_argument("--all", action="store_true", help="Run all fixtures (default)")
    args = parser.parse_args()

    if not settings.ANTHROPIC_API_KEY:
        print("ERROR: ANTHROPIC_API_KEY is not set.")
        return 2

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")

    tiers: list[str] = []
    if args.tier:
        tiers = [args.tier]
    else:
        tiers = ["non_ev", "ev_complete", "ev_leaf"]

    all_pass = True
    for tier in tiers:
        try:
            if tier == "non_ev":
                label, report, word_range = await _run_non_ev(timestamp)
            elif tier == "ev_leaf":
                label, report, word_range = await _run_ev_leaf(timestamp)
            else:
                label, report, word_range = await _run_ev_complete(timestamp)
        except Exception as exc:
            print(f"[{tier}] generation failed: {exc}")
            all_pass = False
            continue

        try:
            scorecard = _judge(report, label, word_range)
        except Exception as exc:
            print(f"[{tier}] judging failed: {exc}")
            all_pass = False
            continue

        scorecard_path = OUT_DIR / f"{label}-{timestamp}.scorecard.json"
        scorecard_path.write_text(json.dumps(scorecard, indent=2))
        print(f"[{tier}] Scorecard: {scorecard_path}")

        passed = _print_scorecard(label, scorecard)
        if not passed:
            all_pass = False

    print("\n" + ("OVERALL: PASS" if all_pass else "OVERALL: FAIL (one or more axes < 4)"))
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
