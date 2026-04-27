# pyright: reportMissingImports=false
"""Batch build known-issues JSONs for a list of UK car models.

Usage:
    python scripts/batch_build_known_issues.py
    python scripts/batch_build_known_issues.py --list data/known_issues/_priority_list.json
    python scripts/batch_build_known_issues.py --limit 5 --dry-run
    python scripts/batch_build_known_issues.py --resume
"""
from __future__ import annotations

import argparse
import asyncio
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import TextIO

# sys.path setup so `app.*` imports resolve when invoked from anywhere
_BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(_BACKEND_DIR))

from app.core.config import settings  # noqa: E402
from app.core.logging import logger  # noqa: E402
from app.services.known_issues.repo import DATA_DIR  # noqa: E402
from scripts.build_known_issues import build_one  # noqa: E402

DEFAULT_LIST = _BACKEND_DIR / "data" / "known_issues" / "_priority_list.json"
INTER_REQUEST_DELAY = 1.5  # seconds, polite to HonestJohn + Anthropic


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Batch build known-issues JSON records for UK car models from a "
            "priority list. Calls scripts/build_known_issues.build_one() for "
            "each entry."
        )
    )
    parser.add_argument(
        "--list",
        default=str(DEFAULT_LIST),
        help=f"Path to JSON priority list (default: {DEFAULT_LIST})",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Maximum number of entries to process (default: all)",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help=(
            "Skip entries whose JSON already exists with non-empty top_issues. "
            "Stub artefacts (file exists but top_issues is empty) are NOT "
            "skipped — they will be rebuilt."
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Log what would be processed without making network calls or writes.",
    )
    return parser.parse_args()


def _check_api_key() -> bool:
    if not settings.ANTHROPIC_API_KEY or settings.ANTHROPIC_API_KEY.startswith("your_"):
        logger.error(
            "ANTHROPIC_API_KEY is not configured. "
            "Set it in backend/.env or the environment before running this script."
        )
        return False
    return True


def _load_list(path: Path) -> list[dict] | None:
    if not path.exists():
        logger.error("Priority list not found at %s", path)
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        logger.error("Priority list at %s is not valid JSON: %s", path, e)
        return None
    if not isinstance(data, list):
        logger.error("Priority list at %s must be a JSON array.", path)
        return None
    for i, entry in enumerate(data):
        if not isinstance(entry, dict):
            logger.error("Entry #%d is not an object: %r", i, entry)
            return None
        if "make" not in entry or "model_slug" not in entry:
            logger.error(
                "Entry #%d missing required keys 'make'/'model_slug': %r", i, entry
            )
            return None
    return data


def _existing_record_path(make: str, model_slug: str) -> Path:
    return DATA_DIR / f"{make.lower()}-{model_slug.lower()}.json"


def _is_already_built(make: str, model_slug: str) -> bool:
    """Return True iff a JSON file exists AND has non-empty top_issues."""
    path = _existing_record_path(make, model_slug)
    if not path.exists():
        return False
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return False
    top_issues = data.get("top_issues") if isinstance(data, dict) else None
    return isinstance(top_issues, list) and len(top_issues) > 0


def _expected_url(make: str, model_slug: str, year: int | str | None) -> str:
    """Reconstruct the HonestJohn URL we'd hit (mirrors honestjohn_scraper)."""
    base = "https://www.honestjohn.co.uk/carbycar"
    if year is not None:
        return f"{base}/{make.lower()}/{model_slug.lower()}/{year}/"
    return f"{base}/{make.lower()}/{model_slug.lower()}/"


def _open_run_log() -> tuple[Path, TextIO]:
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    path = Path(f"/tmp/batch_run_{ts}.log")  # noqa: S108
    fh = path.open("a", encoding="utf-8", buffering=1)  # line-buffered
    fh.write(f"# batch_build_known_issues run started {ts} UTC\n")
    return path, fh


def _log_line(fh: TextIO, line: str) -> None:
    fh.write(line.rstrip("\n") + "\n")


def main() -> int:
    args = _parse_args()

    list_path = Path(args.list).resolve()
    entries = _load_list(list_path)
    if entries is None:
        return 1

    # Match the existing single-model CLI: bail early if no API key.
    # In dry-run we still want to be useful, so allow missing key there.
    if not args.dry_run and not _check_api_key():
        return 2

    if args.limit is not None:
        entries = entries[: args.limit]

    log_path, log_fh = _open_run_log()
    logger.info("Run log: %s", log_path)
    _log_line(log_fh, f"list={list_path} entries={len(entries)} limit={args.limit} "
                      f"resume={args.resume} dry_run={args.dry_run}")

    succeeded: list[str] = []
    failed: list[tuple[str, str]] = []  # (label, reason)
    skipped: list[str] = []

    try:
        for idx, entry in enumerate(entries, start=1):
            make = entry["make"]
            model_slug = entry["model_slug"]
            year = entry.get("year")
            wiki_title = entry.get("wikipedia_title")
            hj_slug = entry.get("honestjohn_slug")
            label = f"{make} {model_slug}"

            logger.info(
                "[%d/%d] %s (year=%s, hj_slug=%s)",
                idx,
                len(entries),
                label,
                year or "-",
                hj_slug or "-",
            )

            if args.resume and _is_already_built(make, model_slug):
                logger.info("  skipped (already built)")
                _log_line(log_fh, f"[{idx}] SKIP {label}: already built")
                skipped.append(label)
                continue

            if args.dry_run:
                url = _expected_url(make, model_slug, year)
                logger.info(
                    "  dry-run: would fetch %s (wikipedia_title=%r)", url, wiki_title
                )
                _log_line(log_fh, f"[{idx}] DRY {label}: would fetch {url}")
                continue

            try:
                success, msg = asyncio.run(
                    build_one(
                        make=make,
                        model_slug=model_slug,
                        year=year,
                        wikipedia_title=wiki_title,
                        honestjohn_slug=hj_slug,
                    )
                )
            except Exception as e:  # noqa: BLE001
                success = False
                msg = f"unhandled exception: {e!r}"
                logger.warning("  build_one raised: %s", e)

            if success:
                succeeded.append(label)
                logger.info("  %s", msg)
                _log_line(log_fh, f"[{idx}] OK   {label}: {msg}")
            else:
                failed.append((label, msg))
                logger.warning("  failed: %s", msg)
                _log_line(log_fh, f"[{idx}] FAIL {label}: {msg}")

            time.sleep(INTER_REQUEST_DELAY)
    finally:
        # End-of-run summary
        total = len(entries)
        logger.info("=" * 60)
        logger.info("Batch run complete")
        logger.info("  entries:   %d", total)
        logger.info("  succeeded: %d", len(succeeded))
        logger.info("  failed:    %d", len(failed))
        logger.info("  skipped:   %d", len(skipped))
        if failed:
            logger.info("Failures:")
            for label, reason in failed:
                logger.info("  - %s: %s", label, reason)
        _log_line(
            log_fh,
            f"summary entries={total} succeeded={len(succeeded)} "
            f"failed={len(failed)} skipped={len(skipped)}",
        )
        for label, reason in failed:
            _log_line(log_fh, f"failure {label}: {reason}")
        log_fh.close()
        logger.info("Run log saved to %s", log_path)

    # Exit 0 if at least one succeeded, OR all entries were skipped (or dry-run).
    attempted = len(succeeded) + len(failed)
    if attempted == 0:
        # Nothing actually attempted — either all skipped or all dry-run.
        return 0
    if len(succeeded) >= 1:
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
