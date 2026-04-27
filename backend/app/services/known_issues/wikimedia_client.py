# pyright: reportMissingImports=false
# Wikimedia Commons / Wikipedia lead-image fetcher.
# Fully free; we display the image under its CC licence with attribution.
from __future__ import annotations

import asyncio
import re
import urllib.parse
from typing import Any

import httpx

from app.core.logging import logger
from app.services.known_issues.models import HeroImage

USER_AGENT = (
    "VericarBot/0.1 (+https://vericar.co.uk; contact: matthew@vericar.co.uk)"
)
WIKIPEDIA_BASE = "https://en.wikipedia.org"
REQUEST_DELAY = 1.0  # polite throttle between requests
TIMEOUT = 15.0

_IMG_EXT_RE = re.compile(r"\.(jpe?g|png|webp)$", re.IGNORECASE)
_HTML_TAG_RE = re.compile(r"<[^>]+>")


def _strip_html(value: str | None) -> str | None:
    """Strip HTML tags from an extmetadata value; collapse whitespace."""
    if not value:
        return None
    cleaned = _HTML_TAG_RE.sub("", value).strip()
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned or None


def _encode_title(title: str) -> str:
    """Wikipedia expects spaces as underscores, then percent-encode."""
    return urllib.parse.quote(title.replace(" ", "_"), safe="")


def _filename_from_url(image_url: str) -> str | None:
    """Extract a plausible Wikimedia filename from a full-size image URL."""
    try:
        path = urllib.parse.urlparse(image_url).path
        # URL path typically looks like:
        # /wikipedia/commons/a/ab/Ford_Focus_III.jpg  (or thumbnail variants)
        segments = [s for s in path.split("/") if s]
        if not segments:
            return None
        # Prefer a segment that ends with an image extension.
        for seg in reversed(segments):
            decoded = urllib.parse.unquote(seg)
            if _IMG_EXT_RE.search(decoded):
                return decoded
        # Fallback to the last segment.
        return urllib.parse.unquote(segments[-1])
    except Exception:  # noqa: BLE001
        return None


async def _fetch_summary(
    client: httpx.AsyncClient, title: str
) -> dict[str, Any] | None:
    encoded = _encode_title(title)
    url = f"{WIKIPEDIA_BASE}/api/rest_v1/page/summary/{encoded}"
    try:
        resp = await client.get(url)
    except httpx.HTTPError as e:
        logger.warning("Wikipedia summary request failed for %r: %s", title, e)
        return None
    if resp.status_code == 404:
        return None
    if resp.status_code != 200:
        logger.warning(
            "Wikipedia summary returned %s for %r", resp.status_code, title
        )
        return None
    try:
        return resp.json()
    except ValueError:
        return None


async def _fetch_image_metadata(
    client: httpx.AsyncClient, filename: str
) -> dict[str, Any] | None:
    # Strip any leading "File:" prefix; we add it back.
    if filename.lower().startswith("file:"):
        filename = filename[5:]
    params = {
        "action": "query",
        "prop": "imageinfo",
        "iiprop": "url|size|extmetadata",
        "iiextmetadatafilter": "Artist|LicenseShortName|LicenseUrl|Credit",
        "format": "json",
        "titles": f"File:{filename}",
    }
    try:
        resp = await client.get(f"{WIKIPEDIA_BASE}/w/api.php", params=params)
    except httpx.HTTPError as e:
        logger.warning("Wikipedia imageinfo request failed: %s", e)
        return None
    if resp.status_code != 200:
        logger.warning("Wikipedia imageinfo returned %s", resp.status_code)
        return None
    try:
        return resp.json()
    except ValueError:
        return None


def _extract_imageinfo(payload: dict[str, Any]) -> dict[str, Any] | None:
    pages = payload.get("query", {}).get("pages", {})
    for _pid, page in pages.items():
        infos = page.get("imageinfo") or []
        if infos:
            return infos[0]
    return None


def _build_candidates(
    make: str,
    model: str,
    generation: str | None,
    wikipedia_title: str | None,
) -> list[str]:
    """Build an ordered list of Wikipedia article titles to try."""
    candidates: list[str] = []
    if wikipedia_title:
        candidates.append(wikipedia_title)
    # "third" is already an ordinal; gate on presence.
    if generation:
        candidates.append(
            f"{make.title()} {model.title()} ({generation} generation)"
        )
    candidates.append(f"{make.title()} {model.title()}")
    # De-duplicate while preserving order.
    seen: set[str] = set()
    unique: list[str] = []
    for c in candidates:
        if c not in seen:
            unique.append(c)
            seen.add(c)
    return unique


async def fetch_hero_image(
    make: str,
    model: str,
    generation: str | None = None,
    wikipedia_title: str | None = None,
) -> HeroImage | None:
    """Fetch a hero image for a vehicle from Wikipedia / Wikimedia Commons.

    Returns a HeroImage with attribution metadata, or None on any failure.
    Never raises — callers can rely on None as "no image available".
    """
    candidates = _build_candidates(make, model, generation, wikipedia_title)
    headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
    try:
        async with httpx.AsyncClient(
            headers=headers, timeout=TIMEOUT, follow_redirects=True
        ) as client:
            for title in candidates:
                summary = await _fetch_summary(client, title)
                await asyncio.sleep(REQUEST_DELAY)
                if not summary:
                    continue
                original = summary.get("originalimage") or {}
                image_url = original.get("source")
                if not image_url:
                    logger.info(
                        "Wikipedia page %r has no originalimage; skipping",
                        title,
                    )
                    continue
                page_url = (
                    summary.get("content_urls", {})
                    .get("desktop", {})
                    .get("page")
                )
                filename = _filename_from_url(image_url)
                artist = None
                license_short = None
                license_url = None
                width = original.get("width")
                height = original.get("height")
                if filename:
                    meta_payload = await _fetch_image_metadata(
                        client, filename
                    )
                    await asyncio.sleep(REQUEST_DELAY)
                    if meta_payload:
                        info = _extract_imageinfo(meta_payload)
                        if info:
                            # Prefer the canonical URL from imageinfo if present.
                            image_url = info.get("url") or image_url
                            width = info.get("width") or width
                            height = info.get("height") or height
                            ext = info.get("extmetadata") or {}
                            artist = _strip_html(
                                (ext.get("Artist") or {}).get("value")
                            )
                            license_short = _strip_html(
                                (ext.get("LicenseShortName") or {}).get(
                                    "value"
                                )
                            )
                            license_url = _strip_html(
                                (ext.get("LicenseUrl") or {}).get("value")
                            )
                return HeroImage(
                    url=image_url,
                    width=width,
                    height=height,
                    source_page_url=page_url,
                    artist=artist,
                    license_short=license_short,
                    license_url=license_url,
                )
    except Exception as e:  # noqa: BLE001
        logger.warning("fetch_hero_image failed: %s", e)
        return None

    logger.warning(
        "No Wikipedia hero image found for %s %s (generation=%s)",
        make,
        model,
        generation,
    )
    return None
