# pyright: reportMissingImports=false
"""CLI: scrape HonestJohn "Good & Bad" page for a UK model and synthesise a
known-issues JSON record via Claude. Prototype tool — one model per invocation.

Usage:
    python scripts/build_known_issues.py --make ford --model focus-mk3
    python scripts/build_known_issues.py --make ford --model focus-mk3 --url https://...
    python scripts/build_known_issues.py --make ford --model focus-mk3 --save-html tests/fixtures/focus.html

Note: the `app.*` imports below are resolved at runtime via the sys.path
prepend of `backend/`. Static type-checkers run outside that context, so the
file-level pyright pragma above suppresses the spurious import-not-found
errors.
"""
from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

# Ensure backend/ is on sys.path so `app.*` imports resolve when invoked from anywhere
_BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(_BACKEND_DIR))

from app.core.config import settings  # noqa: E402
from app.core.logging import logger  # noqa: E402
from app.services.known_issues.honestjohn_scraper import fetch_good_and_bad  # noqa: E402
from app.services.known_issues.repo import save_record  # noqa: E402
from app.services.known_issues.synthesiser import synthesise  # noqa: E402
from app.services.known_issues.wikimedia_client import (  # noqa: E402
    fetch_hero_image,
)


# Map "mkN" generation suffix in slugs to the ordinal form Wikipedia uses.
_MK_TO_ORDINAL = {
    "mk1": "first",
    "mk2": "second",
    "mk3": "third",
    "mk4": "fourth",
    "mk5": "fifth",
    "mk6": "sixth",
    "mk7": "seventh",
    "mk8": "eighth",
}


def _split_model_slug(model_slug: str) -> tuple[str, str | None]:
    """Split `focus-mk3` into (`focus`, `third`). Returns (slug, None) if no mk."""
    parts = model_slug.rsplit("-", 1)
    if len(parts) == 2 and parts[1].lower() in _MK_TO_ORDINAL:
        return parts[0], _MK_TO_ORDINAL[parts[1].lower()]
    return model_slug, None


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Build a known-issues JSON record for a UK car model by scraping "
            "HonestJohn and synthesising via Claude."
        )
    )
    parser.add_argument("--make", required=True, help="Manufacturer, e.g. 'ford'")
    parser.add_argument("--model", required=True, help="Model slug, e.g. 'focus-mk3'")
    parser.add_argument(
        "--year",
        default=None,
        help="Model year (e.g. '2011'); used by HonestJohn's new /{make}/{model}/{year}/ URL scheme",
    )
    parser.add_argument(
        "--url",
        default=None,
        help="Override the HonestJohn URL (for testing)",
    )
    parser.add_argument(
        "--save-html",
        default=None,
        help="Path to save the raw scraped HTML (for test fixtures)",
    )
    parser.add_argument(
        "--wikipedia-title",
        default=None,
        help=(
            "Exact Wikipedia article title for the hero image fetch, e.g. "
            "'Ford Focus (third generation)'. If omitted, candidates are "
            "built from --make / --model."
        ),
    )
    parser.add_argument(
        "--honestjohn-slug",
        default=None,
        help=(
            "Override the model segment of the HonestJohn URL verbatim. Use "
            "for slugs with chassis-code suffixes the default '-mkN' regex "
            "won't strip, e.g. --model a3-8p --honestjohn-slug a3."
        ),
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


async def _run_scrape(
    make: str,
    model_slug: str,
    override_url: str | None,
    year: str | None,
    honestjohn_slug: str | None = None,
):
    return await fetch_good_and_bad(
        make,
        model_slug,
        override_url=override_url,
        year=year,
        honestjohn_slug=honestjohn_slug,
    )


async def build_one(
    make: str,
    model_slug: str,
    year: int | str | None = None,
    wikipedia_title: str | None = None,
    override_url: str | None = None,
    save_html_path: Path | None = None,
    honestjohn_slug: str | None = None,
) -> tuple[bool, str]:
    """Build a single known-issues record in-process.

    Returns (success, status_message). Does NOT call sys.exit() and does NOT log
    fatal errors — callers (e.g. the batch CLI) decide how to react.

    `honestjohn_slug`, if provided, overrides the model segment of the
    HonestJohn URL — used for entries whose `model_slug` carries chassis-code
    suffixes the scraper's default regex won't strip (e.g. `a3-8p`, `corsa-d`,
    `3-series-e90`).
    """
    make = make.lower()
    model_slug = model_slug.lower()
    year_str = str(year) if year is not None else None

    logger.info(
        "Fetching HonestJohn review for %s / %s (year=%s, hj_slug=%s) ...",
        make,
        model_slug,
        year_str or "-",
        honestjohn_slug or "-",
    )
    page, raw_html = await _run_scrape(
        make, model_slug, override_url, year_str, honestjohn_slug
    )

    # Save HTML fixture if requested, regardless of parse outcome
    if save_html_path and raw_html:
        html_path = Path(save_html_path).resolve()
        html_path.parent.mkdir(parents=True, exist_ok=True)
        html_path.write_text(raw_html, encoding="utf-8")
        logger.info("  saved raw HTML to %s (%d bytes)", html_path, len(raw_html))

    if page is None:
        return False, "scrape failed (no page returned)"

    logger.info("  scraped URL: %s", page.url)
    logger.info("  title: %r", page.title[:80])
    logger.info("  good points: %d", len(page.good_points))
    logger.info("  bad points:  %d", len(page.bad_points))

    if not page.bad_points:
        logger.warning(
            "No bad points extracted — parser may need adjustment, "
            "or page layout changed."
        )
        # Continue anyway — synthesiser will receive empty bullets and may fail gracefully

    logger.info(
        "Synthesising known-issues record via Claude (%s) ...",
        settings.ANTHROPIC_MODEL,
    )
    record = synthesise(page)
    if record is None:
        return False, "synthesis failed (Claude returned no record)"

    logger.info("  synthesised %d top issues", len(record.top_issues))

    # Try to attach a Wikimedia hero image before saving.
    model_part, generation_ordinal = _split_model_slug(model_slug)
    try:
        hero = await fetch_hero_image(
            make=make,
            model=model_part,
            generation=generation_ordinal,
            wikipedia_title=wikipedia_title,
        )
    except Exception as e:  # noqa: BLE001
        logger.warning("Hero image fetch raised unexpectedly: %s", e)
        hero = None
    if hero is not None:
        record.hero_image = hero
        logger.info(
            "  hero image: %s  [%s / %s]",
            hero.url,
            hero.license_short or "unknown licence",
            hero.artist or "unknown artist",
        )
    else:
        logger.info("  hero image: none found")

    out_path = save_record(record, model_slug)
    logger.info("  wrote JSON to %s", out_path)

    titles = ", ".join(i.title for i in record.top_issues)
    logger.info(
        "Summary: %s %s %s (%s) — %d issues: %s",
        record.make,
        record.model,
        record.generation or "",
        record.years,
        len(record.top_issues),
        titles,
    )
    return True, f"✓ {len(record.top_issues)} issues synthesised"


def main() -> int:
    args = _parse_args()

    if not _check_api_key():
        return 2

    save_html_path = Path(args.save_html) if args.save_html else None

    success, msg = asyncio.run(
        build_one(
            make=args.make,
            model_slug=args.model,
            year=args.year,
            wikipedia_title=args.wikipedia_title,
            override_url=args.url,
            save_html_path=save_html_path,
            honestjohn_slug=args.honestjohn_slug,
        )
    )

    if success:
        return 0

    # Translate failure reason back into the historical exit codes.
    if msg.startswith("scrape failed"):
        logger.error("Scrape failed. See logs above.")
        return 3
    if msg.startswith("synthesis failed"):
        logger.error("Synthesis failed. See logs above.")
        return 4
    logger.error("build_one failed: %s", msg)
    return 1


if __name__ == "__main__":
    sys.exit(main())
