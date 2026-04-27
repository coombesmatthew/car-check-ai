# pyright: reportMissingImports=false
"""API endpoints for the Gumtree scraper, content pipeline, and known-issues SEO lookup."""
from __future__ import annotations

from pathlib import Path
from threading import Lock
from typing import Any

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from app.core.logging import logger
from app.schemas.scraping import (
    ScrapeRequest,
    ScrapeResponse,
    ContentPipelineRequest,
    ContentPipelineResponse,
)
# Optional import — the known-issues feature is being built in parallel
# (services + data files land together). Wrap in try/except so the app
# still boots when only this file's integration is committed; the
# /known-issues endpoints just return 503 until the rest lands.
try:
    from app.services.known_issues.models import KnownIssuesRecord
    KNOWN_ISSUES_AVAILABLE = True
except ImportError:
    KnownIssuesRecord = None  # type: ignore
    KNOWN_ISSUES_AVAILABLE = False
    logger.warning("known_issues module not available — /known-issues endpoints disabled")
from app.services.scraping.gumtree_client import GumtreeClient
from app.services.scraping.content_pipeline import ContentPipeline

router = APIRouter()


# ---------------------------------------------------------------------------
# Known-issues slug resolver: in-memory cache backed by JSON files on disk.
# Cache is invalidated automatically when any source file's mtime advances.
# ---------------------------------------------------------------------------

_DATA_DIR = Path(__file__).resolve().parents[4] / "data" / "known_issues"
_CACHE_LOCK = Lock()
_CACHE: dict[str, Any] = {}  # slug -> record
_CACHE_MTIME: float = 0.0


def _ensure_cache_fresh() -> None:
    """Reload cache if any JSON file in the data dir has changed since last load."""
    global _CACHE_MTIME
    with _CACHE_LOCK:
        if not _DATA_DIR.exists():
            return
        latest = 0.0
        for path in _DATA_DIR.glob("*.json"):
            if path.name.startswith("_"):
                continue  # skip _priority_list.json and similar
            try:
                latest = max(latest, path.stat().st_mtime)
            except OSError:
                continue
        if _CACHE and latest <= _CACHE_MTIME:
            return  # cache is fresh
        new_cache: dict[str, Any] = {}
        for path in _DATA_DIR.glob("*.json"):
            if path.name.startswith("_"):
                continue
            try:
                # Narrow the Optional[KnownIssuesRecord] type for Pyright.
                # We never reach here when the module isn't loaded (gated by
                # KNOWN_ISSUES_AVAILABLE in the calling endpoints), but the
                # static checker doesn't know that without an explicit guard.
                if KnownIssuesRecord is None:
                    return
                record = KnownIssuesRecord.model_validate_json(path.read_text())
                new_cache[path.stem] = record  # filename stem is the slug
            except Exception as e:  # noqa: BLE001 — log and skip malformed files
                logger.warning(f"Skipping malformed known_issues file {path.name}: {e}")
        _CACHE.clear()
        _CACHE.update(new_cache)
        _CACHE_MTIME = latest


def _parse_year_range(years: str) -> tuple[int, int] | None:
    """Parse a year range like '2011-2014' or single year '2013' → (start, end). None if unparseable."""
    s = years.strip()
    if not s:
        return None
    if "-" not in s:
        try:
            single = int(s)
            return (single, single)
        except ValueError:
            return None
    parts = s.split("-")
    if len(parts) != 2:
        return None
    try:
        return (int(parts[0].strip()), int(parts[1].strip()))
    except ValueError:
        return None


@router.get("/known-issues/resolve")
async def resolve_known_issues_slug(make: str, model: str, year: int):
    """Map (make, model, year) → known-issues page slug. 404 if no match."""
    if not KNOWN_ISSUES_AVAILABLE:
        raise HTTPException(status_code=503, detail="Known-issues service not yet deployed")
    _ensure_cache_fresh()
    make_l = make.lower()
    model_l = model.lower()
    for slug, record in _CACHE.items():
        if record.make.lower() != make_l:
            continue
        if record.model.lower() != model_l:
            continue
        rng = _parse_year_range(record.years)
        if rng is None:
            continue
        if rng[0] <= year <= rng[1]:
            return JSONResponse(
                content={
                    "slug": slug,
                    "make": record.make,
                    "model": record.model,
                    "generation": record.generation,
                },
                headers={"Cache-Control": "public, max-age=86400"},
            )
    raise HTTPException(status_code=404, detail="No known-issues page for this vehicle")


@router.get("/known-issues/siblings")
async def list_known_issues_siblings(make: str, exclude: str | None = None):
    """Up to 4 same-make sibling slugs (sorted alphabetically), excluding the given slug."""
    if not KNOWN_ISSUES_AVAILABLE:
        raise HTTPException(status_code=503, detail="Known-issues service not yet deployed")
    _ensure_cache_fresh()
    make_l = make.lower()
    siblings: list[dict] = []
    for slug, record in sorted(_CACHE.items()):
        if record.make.lower() != make_l:
            continue
        if exclude and slug == exclude:
            continue
        siblings.append(
            {
                "slug": slug,
                "make": record.make,
                "model": record.model,
                "generation": record.generation,
                "years": record.years,
            }
        )
        if len(siblings) >= 4:
            break
    return JSONResponse(
        content={"siblings": siblings},
        headers={"Cache-Control": "public, max-age=86400"},
    )


@router.post("/scrape", response_model=ScrapeResponse)
async def scrape_listings(request: ScrapeRequest):
    """Scrape Gumtree for car listings. Returns raw listings with VRNs where available."""
    client = GumtreeClient()
    try:
        listings = await client.search_pages(request)
        vrn_count = sum(1 for l in listings if l.vrn)
        return ScrapeResponse(
            listings=listings,
            total_found=len(listings),
            pages_scraped=request.max_pages,
            vrn_count=vrn_count,
        )
    except Exception as e:
        logger.error(f"Scrape failed: {e}")
        raise HTTPException(status_code=500, detail="Scraping failed - please try again")
    finally:
        await client.close()


@router.post("/pipeline", response_model=ContentPipelineResponse)
async def run_pipeline(request: ContentPipelineRequest):
    """Run the full content pipeline: scrape -> check -> score -> generate scripts."""
    pipeline = ContentPipeline()
    try:
        result = await pipeline.run(request)
        return result
    except Exception as e:
        logger.error(f"Content pipeline failed: {e}")
        raise HTTPException(status_code=500, detail="Pipeline failed - please try again")
    finally:
        await pipeline.close()
