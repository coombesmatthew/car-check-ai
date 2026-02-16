"""Gumtree HTML parser — extracts VRN and listing data from search pages.

Primary strategy: URL-decode the page HTML and regex for structured attribute
blocks containing VRN, Make, Model, Year, Mileage, etc.

Fallback: BeautifulSoup HTML parsing for listing cards.
"""

import re
import json
from typing import List, Optional, Dict
from urllib.parse import unquote

from bs4 import BeautifulSoup

from app.core.logging import logger
from app.schemas.scraping import GumtreeListing


# Regex to find VRN attribute blocks in Gumtree HTML.
# Real Gumtree format: "value":"L66GPW","key":"vrn" (value before key)
# Broad VRN match: 2-7 alphanumeric chars (covers standard + private plates)
VRN_PATTERN = re.compile(
    r'"key"\s*:\s*"vrn"\s*,\s*"value"\s*:\s*"([A-Z0-9]{2,7})"',
    re.IGNORECASE,
)

# Alternative pattern where value comes before key (the more common Gumtree format)
VRN_PATTERN_ALT = re.compile(
    r'"value"\s*:\s*"([A-Z0-9]{2,7})"[^}]*"key"\s*:\s*"vrn"',
    re.IGNORECASE,
)

# Pattern for attribute blocks. Matches both:
#   {"name":"Make","value":"BMW","key":"vehicle_make","vipOrder":1,"unit":""}
#   {"name":"Make","value":"BMW","key":"make"}
ATTRIBUTE_BLOCK_PATTERN = re.compile(
    r'"name"\s*:\s*"([^"]+)"\s*,\s*"value"\s*:\s*"([^"]*?)"\s*,\s*"key"\s*:\s*"([^"]+)"',
)

# Pattern for listing IDs in Gumtree URLs
LISTING_ID_PATTERN = re.compile(r'/p/([^/]+)/(\d+)')

# UK VRN format validator (post-2001 format: AB12CDE)
UK_VRN_REGEX = re.compile(r'^[A-Z]{2}\d{2}[A-Z]{3}$')


def parse_search_page(html: str) -> List[GumtreeListing]:
    """Parse a Gumtree search results page and extract listings with data.

    Args:
        html: Raw HTML of a Gumtree search results page.

    Returns:
        List of GumtreeListing objects, each with as much data as could be extracted.
    """
    # URL-decode the entire HTML to expose embedded JSON
    decoded = unquote(html)

    # Try primary strategy: extract structured attribute blocks
    listings = _extract_from_attributes(decoded)
    if listings:
        logger.info(f"Parsed {len(listings)} listings via attribute extraction")
        return listings

    # Fallback: BeautifulSoup card parsing
    listings = _extract_from_html(html)
    logger.info(f"Parsed {len(listings)} listings via HTML fallback")
    return listings


def _extract_from_attributes(decoded_html: str) -> List[GumtreeListing]:
    """Extract listings from URL-decoded attribute blocks in page HTML."""
    # Find all attribute blocks
    all_blocks = ATTRIBUTE_BLOCK_PATTERN.findall(decoded_html)
    if not all_blocks:
        return []

    # Group attributes by their surrounding context (listing)
    # Strategy: find VRN positions and collect nearby attributes
    vrn_matches = list(VRN_PATTERN.finditer(decoded_html))
    if not vrn_matches:
        vrn_matches = list(VRN_PATTERN_ALT.finditer(decoded_html))

    if not vrn_matches:
        return []

    listings = []
    seen_vrns = set()

    # Build regions: each VRN owns from previous VRN's end to next VRN's start
    vrn_positions = [(m.start(), m.end(), m) for m in vrn_matches]

    for idx, (pos, end, vrn_match) in enumerate(vrn_positions):
        vrn = vrn_match.group(1).upper().replace(" ", "")
        if vrn in seen_vrns:
            continue
        seen_vrns.add(vrn)

        # Window starts after previous VRN's match ends (or 3000 chars before)
        if idx > 0:
            window_start = vrn_positions[idx - 1][1]  # previous VRN's end
        else:
            window_start = max(0, pos - 3000)

        # Window ends at next VRN's match start (or 3000 chars after)
        if idx < len(vrn_positions) - 1:
            window_end = vrn_positions[idx + 1][0]  # next VRN's start
        else:
            window_end = min(len(decoded_html), end + 3000)

        window = decoded_html[window_start:window_end]

        attrs = _parse_attribute_window(window)
        listing = _build_listing_from_attrs(vrn, attrs)

        # Try to extract listing ID and URL from the same window
        id_match = LISTING_ID_PATTERN.search(window)
        if id_match:
            listing.listing_id = id_match.group(2)
            listing.url = f"https://www.gumtree.com/p/{id_match.group(1)}/{id_match.group(2)}"

        listings.append(listing)

    return listings


def _parse_attribute_window(window: str) -> Dict[str, str]:
    """Parse all attribute key-value pairs from a text window."""
    attrs = {}
    for name, value, key in ATTRIBUTE_BLOCK_PATTERN.findall(window):
        attrs[key.lower()] = value
    return attrs


def _build_listing_from_attrs(vrn: str, attrs: Dict[str, str]) -> GumtreeListing:
    """Build a GumtreeListing from extracted attributes.

    Real Gumtree keys: vehicle_make, vehicle_model, vehicle_registration_year,
    vehicle_mileage, price, seller_type. Falls back to shorter key names for
    compatibility with test fixtures.
    """
    price = _parse_price(attrs.get("price", ""))
    mileage = _parse_mileage(
        attrs.get("vehicle_mileage", attrs.get("mileage", ""))
    )
    year = _parse_year(
        attrs.get("vehicle_registration_year", attrs.get("year", attrs.get("vehicle_year", "")))
    )
    make = attrs.get("vehicle_make", attrs.get("make"))
    model = attrs.get("vehicle_model", attrs.get("model"))

    return GumtreeListing(
        vrn=vrn,
        make=make,
        model=model,
        year=year,
        price=price,
        mileage=mileage,
        seller_type=attrs.get("seller_type"),
        title=attrs.get("title", f"{make or ''} {model or ''}".strip()),
    )


def _extract_from_html(html: str) -> List[GumtreeListing]:
    """Fallback: parse listings from HTML using BeautifulSoup."""
    soup = BeautifulSoup(html, "html.parser")
    listings = []

    # Look for listing cards (Gumtree uses article or listing-card elements)
    cards = soup.select("article.listing-maxi, div.listing-maxi, article[data-q='search-result']")
    if not cards:
        # Try broader selectors
        cards = soup.select("article, div.natural")

    for card in cards:
        listing = GumtreeListing()

        # Extract title
        title_el = card.select_one("h2 a, a.listing-link, h2.listing-title")
        if title_el:
            listing.title = title_el.get_text(strip=True)
            href = title_el.get("href", "")
            if href:
                if not href.startswith("http"):
                    href = f"https://www.gumtree.com{href}"
                listing.url = href
                id_match = LISTING_ID_PATTERN.search(href)
                if id_match:
                    listing.listing_id = id_match.group(2)

        # Extract price
        price_el = card.select_one("strong.listing-price, span.listing-price, .ad-price")
        if price_el:
            listing.price = _parse_price(price_el.get_text(strip=True))

        # Try to find VRN in card text (rare in HTML but possible)
        card_text = unquote(str(card))
        vrn_match = VRN_PATTERN.search(card_text) or VRN_PATTERN_ALT.search(card_text)
        if vrn_match:
            listing.vrn = vrn_match.group(1).upper().replace(" ", "")

        # Extract image
        img_el = card.select_one("img")
        if img_el:
            src = img_el.get("src") or img_el.get("data-src", "")
            if src and src.startswith("http"):
                listing.image_urls = [src]

        if listing.title or listing.vrn:
            listings.append(listing)

    return listings


def _parse_price(price_str: str) -> Optional[int]:
    """Parse a price string to pence. Returns None if unparseable."""
    if not price_str:
        return None
    # Remove currency symbols, commas, spaces
    cleaned = re.sub(r'[£$,\s]', '', price_str)
    try:
        # If it looks like it already has pence (e.g. "299900")
        value = float(cleaned)
        if value > 10000:
            # Likely already pence
            return int(value)
        # Otherwise treat as pounds
        return int(value * 100)
    except (ValueError, TypeError):
        return None


def _parse_mileage(mileage_str: str) -> Optional[int]:
    """Parse a mileage string to integer miles."""
    if not mileage_str:
        return None
    cleaned = re.sub(r'[,\s]', '', mileage_str)
    # Remove units like "miles", "mi"
    cleaned = re.sub(r'(miles?|mi)\s*$', '', cleaned, flags=re.IGNORECASE)
    try:
        return int(float(cleaned))
    except (ValueError, TypeError):
        return None


def _parse_year(year_str: str) -> Optional[int]:
    """Parse a year string to integer."""
    if not year_str:
        return None
    try:
        year = int(year_str)
        if 1900 <= year <= 2030:
            return year
    except (ValueError, TypeError):
        pass
    return None
