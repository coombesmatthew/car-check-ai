# HonestJohn "Good & Bad" scraper.
#
# This is a polite, rate-limited scraper against HonestJohn's publicly visible
# per-model "Good & Bad" pages. The output is not republished verbatim — it is
# transformed via AI synthesis into a structured record (fair-dealing /
# transformative-use posture). Attribution to HonestJohn is preserved in the
# resulting JSON's `source_citations` field. Contact for operator questions:
# matthew@vericar.co.uk.
from __future__ import annotations

import asyncio
import re
from datetime import datetime, timezone
from typing import Optional
from urllib.parse import urljoin  # noqa: F401 — kept for future relative-URL resolution

import httpx
from bs4 import BeautifulSoup

from app.core.logging import logger
from app.services.known_issues.models import ScrapedPage

USER_AGENT = "VericarBot/0.1 (+https://vericar.co.uk; contact: matthew@vericar.co.uk)"
BASE_URL = "https://www.honestjohn.co.uk"
DEFAULT_TIMEOUT = 15.0
REQUEST_DELAY_SECONDS = 1.5


def _build_url(
    make: str,
    model_slug: str,
    year: str | None = None,
    honestjohn_slug: str | None = None,
) -> str:
    """Build a HonestJohn review URL.

    New HJ scheme (post-2025 restructure): /{make}/{model}/{year}/
    Strips generation suffix "-mk\\d+" from model_slug to isolate the model name.
    If `honestjohn_slug` is provided, it overrides the derived model segment
    verbatim — used for entries whose `model_slug` carries chassis codes
    (e.g. `a3-8p`, `corsa-d`, `3-series-e90`) that the regex does not strip.
    If no year is provided, falls back to the make/model index page.
    """
    if honestjohn_slug:
        model = honestjohn_slug.lower()
    else:
        model = re.sub(r"-mk\d+$", "", model_slug, flags=re.IGNORECASE).lower()
    if year:
        return f"{BASE_URL}/{make.lower()}/{model}/{year}/"
    return f"{BASE_URL}/{make.lower()}/{model}/"


def _collect_bullets_after_heading(heading_tag) -> list[str]:
    """Collect bullet-like text associated with a heading.

    Handles three HJ layouts:
      (a) Flat siblings — heading is followed by <p>/<li>/<ul> siblings that
          belong to it, terminated by the next heading.
      (b) Accordion wrapper — heading sits inside
          div.accordion-heading, and the real content lives in the adjacent
          sibling div.accordion-body. We detect this and harvest <p>/<li>
          from that body.
      (c) Fallback wrapper — heading is wrapped in a container with no
          siblings of its own; climb once to the parent and collect from
          the parent's next siblings instead.
    """
    bullets: list[str] = []
    seen: set[str] = set()

    def _push(text: str) -> None:
        text = (text or "").strip()
        if not text:
            return
        if text in seen:
            return
        seen.add(text)
        bullets.append(text)

    def _harvest_from(container) -> None:
        # Grab both <li> and <p> text in document order.
        for node in container.find_all(["li", "p"], recursive=True):
            _push(node.get_text(" ", strip=True))

    # Layout (b): HJ accordion — "What to watch out for" heading lives inside
    # div.accordion-heading, and the content is in the adjacent div.accordion-body.
    accordion_heading = heading_tag.find_parent("div", class_="accordion-heading")
    if accordion_heading is not None:
        body = accordion_heading.find_next_sibling("div", class_="accordion-body")
        if body is not None:
            _harvest_from(body)
            if bullets:
                return bullets

    # Layout (a): flat siblings of the heading itself.
    def _collect_flat(tag) -> None:
        for sibling in tag.find_next_siblings():
            if sibling.name in {"h1", "h2", "h3", "h4"}:
                break
            if sibling.name == "li" or sibling.name == "p":
                _push(sibling.get_text(" ", strip=True))
            elif sibling.name in {"ul", "ol"}:
                for li in sibling.find_all("li"):
                    _push(li.get_text(" ", strip=True))
            else:
                for node in sibling.find_all(["li", "p"], recursive=True):
                    _push(node.get_text(" ", strip=True))

    _collect_flat(heading_tag)
    if bullets:
        return bullets

    # Layout (c): climb one level if the heading has no useful siblings.
    parent = heading_tag.parent
    if parent is not None:
        _collect_flat(parent)

    return bullets


def _parse_good_and_bad(html: str, url: str, make: str, model_slug: str) -> ScrapedPage:
    """Parse HonestJohn good-and-bad HTML into a ScrapedPage.

    HonestJohn markup varies page-to-page; use a layered strategy:
      1. Find headings (h2/h3/h4) whose text contains "Good"/"Bad", then collect
         <li>s that follow until the next heading.
      2. Fall back to scanning for any <ul> beneath a heading whose text
         contains the category word.
      3. If still nothing, return an empty list for that category.
    """
    soup = BeautifulSoup(html, "html.parser")

    title_tag = soup.find("title")
    title_text = title_tag.get_text(strip=True) if title_tag else ""

    def find_bullets(keywords: list[str]) -> list[str]:
        # Strategy 1: heading whose text contains any keyword — collect siblings
        for heading in soup.find_all(["h1", "h2", "h3", "h4"]):
            heading_text = heading.get_text(" ", strip=True).lower()
            if any(kw in heading_text for kw in keywords):
                bullets = _collect_bullets_after_heading(heading)
                if bullets:
                    return bullets
        # Strategy 2: any <ul> under such a heading
        for heading in soup.find_all(["h1", "h2", "h3", "h4"]):
            heading_text = heading.get_text(" ", strip=True).lower()
            if any(kw in heading_text for kw in keywords):
                ul = heading.find_next("ul")
                if ul:
                    items = [li.get_text(" ", strip=True) for li in ul.find_all("li")]
                    items = [i for i in items if i]
                    if items:
                        return items
        # Strategy 3: nothing
        return []

    good_points = find_bullets(["good", "verdict"])
    bad_points = find_bullets(["bad", "watch out for"])

    return ScrapedPage(
        url=url,
        make=make,
        model_slug=model_slug,
        title=title_text,
        good_points=good_points,
        bad_points=bad_points,
        fetched_at=datetime.now(timezone.utc),
    )


async def fetch_good_and_bad(
    make: str,
    model_slug: str,
    *,
    override_url: str | None = None,
    year: str | None = None,
    honestjohn_slug: str | None = None,
) -> tuple[Optional[ScrapedPage], Optional[str]]:
    """Fetch and parse HonestJohn's review page for a make/model (+ optional year).

    `honestjohn_slug`, when set, overrides the model segment of the URL verbatim
    (used for entries whose model_slug carries chassis-code suffixes the
    default regex won't strip — e.g. `a3-8p`, `corsa-d`, `3-series-e90`).

    Returns (page, raw_html) so callers can persist the raw HTML as a fixture
    regardless of whether parsing succeeded. On failure returns (None, None).
    """
    url = (
        override_url
        if override_url
        else _build_url(make, model_slug, year=year, honestjohn_slug=honestjohn_slug)
    )
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml",
    }

    try:
        async with httpx.AsyncClient(
            headers=headers,
            timeout=DEFAULT_TIMEOUT,
            follow_redirects=True,
        ) as client:
            response = await client.get(url)
            if response.status_code == 429:
                logger.info(f"HonestJohn 429 for {url}; backing off 5s and retrying once")
                await asyncio.sleep(5.0)
                response = await client.get(url)

            if response.status_code != 200:
                logger.error(
                    f"HonestJohn fetch failed for {url}: status={response.status_code}"
                )
                return (None, None)

            raw_html = response.text
            logger.info(
                f"Fetched HonestJohn page {url} ({len(response.content)} bytes)"
            )
            # Polite delay so chained calls don't hammer the server
            await asyncio.sleep(REQUEST_DELAY_SECONDS)

            page = _parse_good_and_bad(raw_html, url, make, model_slug)
            return (page, raw_html)

    except Exception as e:
        logger.error(f"HonestJohn scrape error for {url}: {e}")
        return (None, None)
