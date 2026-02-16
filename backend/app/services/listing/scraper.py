"""
Listing scraper service for Car Check AI.

Scrapes car listing data from supported UK platforms:
- AutoTrader (autotrader.co.uk)
- Gumtree (gumtree.com)
- Facebook Marketplace (facebook.com/marketplace)

Uses httpx + BeautifulSoup for simple HTML scraping. Falls back to
demo mode with realistic mock data when scraping fails (anti-bot, etc.).
"""

import re
import random
import hashlib
from typing import Optional, List
from dataclasses import dataclass, field
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup

from app.core.logging import logger


@dataclass
class ListingData:
    """Structured data extracted from a car listing."""

    url: str
    platform: str  # "autotrader" | "gumtree" | "facebook" | "unknown"
    title: Optional[str] = None
    price_pence: Optional[int] = None
    mileage: Optional[int] = None
    registration: Optional[str] = None
    description: Optional[str] = None
    seller_type: Optional[str] = None  # "private" | "dealer" | "unknown"
    location: Optional[str] = None
    features: List[str] = field(default_factory=list)
    images_count: Optional[int] = None
    scrape_success: bool = False
    scrape_errors: List[str] = field(default_factory=list)
    demo_mode: bool = False

    def to_dict(self) -> dict:
        return {
            "url": self.url,
            "platform": self.platform,
            "title": self.title,
            "price_pence": self.price_pence,
            "mileage": self.mileage,
            "registration": self.registration,
            "description": self.description,
            "seller_type": self.seller_type,
            "location": self.location,
            "features": self.features,
            "images_count": self.images_count,
            "scrape_success": self.scrape_success,
            "scrape_errors": self.scrape_errors,
            "demo_mode": self.demo_mode,
        }


# --- Platform detection ---

PLATFORM_PATTERNS = {
    "autotrader": [
        r"autotrader\.co\.uk",
        r"autotrader\.com",
    ],
    "gumtree": [
        r"gumtree\.com",
    ],
    "facebook": [
        r"facebook\.com/marketplace",
        r"fb\.com/marketplace",
        r"facebook\.com/.*/marketplace",
    ],
}


def detect_platform(url: str) -> str:
    """Detect which platform a listing URL belongs to."""
    for platform, patterns in PLATFORM_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, url, re.IGNORECASE):
                return platform
    return "unknown"


# --- Registration extraction ---

UK_REG_PATTERN = re.compile(
    r"\b([A-Z]{2}\d{2}\s?[A-Z]{3})\b"  # Modern: AB12 CDE
    r"|"
    r"\b([A-Z]\d{1,3}\s?[A-Z]{3})\b"  # Prefix: A123 BCD
    r"|"
    r"\b([A-Z]{3}\s?\d{1,3}[A-Z])\b",  # Suffix: ABC 123D
    re.IGNORECASE,
)


def extract_registration(text: str) -> Optional[str]:
    """Try to extract a UK registration number from text."""
    match = UK_REG_PATTERN.search(text)
    if match:
        reg = match.group(0).replace(" ", "").upper()
        return reg
    return None


# --- Live scrapers ---

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-GB,en;q=0.9",
}


async def _scrape_autotrader(url: str, html: str) -> ListingData:
    """Parse an AutoTrader listing page."""
    listing = ListingData(url=url, platform="autotrader")
    soup = BeautifulSoup(html, "html.parser")

    try:
        # Title
        title_el = soup.find("h1")
        if title_el:
            listing.title = title_el.get_text(strip=True)

        # Price
        price_el = soup.find("span", class_=re.compile(r"price", re.I))
        if not price_el:
            price_el = soup.find(attrs={"data-testid": re.compile(r"price", re.I)})
        if price_el:
            price_text = price_el.get_text(strip=True)
            price_match = re.search(r"[\d,]+", price_text.replace(",", ""))
            if price_match:
                listing.price_pence = int(price_match.group().replace(",", "")) * 100

        # Mileage
        for el in soup.find_all(string=re.compile(r"miles", re.I)):
            parent = el.parent
            if parent:
                text = parent.get_text(strip=True)
                mileage_match = re.search(r"([\d,]+)\s*miles", text, re.I)
                if mileage_match:
                    listing.mileage = int(mileage_match.group(1).replace(",", ""))
                    break

        # Seller type
        seller_el = soup.find(string=re.compile(r"private|dealer|trade", re.I))
        if seller_el:
            text = seller_el.lower()
            if "private" in text:
                listing.seller_type = "private"
            elif "dealer" in text or "trade" in text:
                listing.seller_type = "dealer"

        # Description
        desc_el = soup.find(attrs={"data-testid": re.compile(r"description", re.I)})
        if not desc_el:
            desc_el = soup.find(class_=re.compile(r"description", re.I))
        if desc_el:
            listing.description = desc_el.get_text(strip=True)[:2000]

        # Location
        loc_el = soup.find(string=re.compile(r"location|address|postcode", re.I))
        if loc_el and loc_el.parent:
            listing.location = loc_el.parent.get_text(strip=True)[:200]

        # Images count
        images = soup.find_all("img", src=re.compile(r"i\.ebayimg|autotraderimg|img\.autotrader", re.I))
        if images:
            listing.images_count = len(images)

        # Try to find registration in page
        full_text = soup.get_text()
        reg = extract_registration(full_text)
        if reg:
            listing.registration = reg

        # Features/key specs
        spec_items = soup.find_all(attrs={"data-testid": re.compile(r"spec", re.I)})
        for item in spec_items[:20]:
            listing.features.append(item.get_text(strip=True))

        listing.scrape_success = True

    except Exception as e:
        listing.scrape_errors.append(f"AutoTrader parse error: {str(e)}")

    return listing


async def _scrape_gumtree(url: str, html: str) -> ListingData:
    """Parse a Gumtree listing page."""
    listing = ListingData(url=url, platform="gumtree")
    soup = BeautifulSoup(html, "html.parser")

    try:
        # Title
        title_el = soup.find("h1")
        if title_el:
            listing.title = title_el.get_text(strip=True)

        # Price
        price_el = soup.find(class_=re.compile(r"price", re.I))
        if price_el:
            price_text = price_el.get_text(strip=True)
            price_match = re.search(r"[\d,]+", price_text.replace(",", ""))
            if price_match:
                listing.price_pence = int(price_match.group().replace(",", "")) * 100

        # Mileage
        for el in soup.find_all(string=re.compile(r"mileage|miles", re.I)):
            parent = el.parent
            if parent:
                text = parent.get_text(strip=True)
                mileage_match = re.search(r"([\d,]+)\s*miles?", text, re.I)
                if mileage_match:
                    listing.mileage = int(mileage_match.group(1).replace(",", ""))
                    break

        # Seller type - Gumtree distinguishes private & trade
        seller_el = soup.find(string=re.compile(r"private seller|trade seller", re.I))
        if seller_el:
            text = seller_el.lower()
            listing.seller_type = "private" if "private" in text else "dealer"

        # Description
        desc_el = soup.find(class_=re.compile(r"description", re.I))
        if desc_el:
            listing.description = desc_el.get_text(strip=True)[:2000]

        # Location
        loc_el = soup.find(class_=re.compile(r"location", re.I))
        if loc_el:
            listing.location = loc_el.get_text(strip=True)[:200]

        # Images count
        images = soup.find_all("img", src=re.compile(r"i\.ebayimg|img\.gumtree", re.I))
        if images:
            listing.images_count = len(images)

        # Registration
        full_text = soup.get_text()
        reg = extract_registration(full_text)
        if reg:
            listing.registration = reg

        # Features
        feature_els = soup.find_all(class_=re.compile(r"attribute|feature|spec", re.I))
        for item in feature_els[:20]:
            listing.features.append(item.get_text(strip=True))

        listing.scrape_success = True

    except Exception as e:
        listing.scrape_errors.append(f"Gumtree parse error: {str(e)}")

    return listing


async def _scrape_facebook(url: str, html: str) -> ListingData:
    """Parse a Facebook Marketplace listing page.

    Facebook heavily restricts scraping, so this will usually fail
    and fall back to demo mode.
    """
    listing = ListingData(url=url, platform="facebook")
    soup = BeautifulSoup(html, "html.parser")

    try:
        # Title
        title_el = soup.find("h1") or soup.find("title")
        if title_el:
            listing.title = title_el.get_text(strip=True)

        # Price
        price_els = soup.find_all(string=re.compile(r"£[\d,]+", re.I))
        for price_el in price_els:
            price_match = re.search(r"£([\d,]+)", price_el)
            if price_match:
                listing.price_pence = int(price_match.group(1).replace(",", "")) * 100
                break

        # Description
        desc_el = soup.find(attrs={"data-testid": re.compile(r"description", re.I)})
        if desc_el:
            listing.description = desc_el.get_text(strip=True)[:2000]

        # Registration from text
        full_text = soup.get_text()
        reg = extract_registration(full_text)
        if reg:
            listing.registration = reg

        listing.seller_type = "private"  # FB marketplace is predominantly private

        if listing.title or listing.price_pence:
            listing.scrape_success = True

    except Exception as e:
        listing.scrape_errors.append(f"Facebook parse error: {str(e)}")

    return listing


# --- Demo data generator ---

_DEMO_CARS = [
    {
        "title": "2019 Volkswagen Golf 1.5 TSI EVO Match 5dr",
        "price_pence": 1399500,
        "mileage": 42350,
        "description": (
            "Stunning VW Golf in great condition. Full service history, "
            "2 previous owners. Recent MOT with no advisories. Adaptive cruise "
            "control, Apple CarPlay, parking sensors. Well maintained and drives "
            "beautifully. Genuine reason for sale."
        ),
        "seller_type": "dealer",
        "location": "Manchester, M1",
        "features": [
            "1.5 TSI Petrol",
            "Manual",
            "5 doors",
            "Adaptive cruise control",
            "Apple CarPlay",
            "Parking sensors",
            "DAB radio",
            "Bluetooth",
        ],
        "images_count": 24,
        "registration": "WG19 ABF",
    },
    {
        "title": "2020 Ford Focus 1.0 EcoBoost Titanium X 5dr",
        "price_pence": 1549900,
        "mileage": 35800,
        "description": (
            "Top spec Titanium X with heated seats, reversing camera, "
            "and premium sound system. Full Ford service history. One careful "
            "owner from new. MOT until December 2026. Cat N (minor rear "
            "bumper scuff, fully repaired). HPI clear."
        ),
        "seller_type": "private",
        "location": "Birmingham, B15",
        "features": [
            "1.0 EcoBoost Petrol",
            "Automatic",
            "5 doors",
            "Heated seats",
            "Reversing camera",
            "Premium sound system",
            "LED headlights",
            "Keyless entry",
        ],
        "images_count": 18,
        "registration": "FO20 XYZ",
    },
    {
        "title": "2018 BMW 3 Series 320d M Sport 4dr",
        "price_pence": 1899900,
        "mileage": 67200,
        "description": (
            "BMW 320d M Sport in Mineral Grey. Full leather interior, "
            "sat nav, M Sport suspension. Some service history but not "
            "complete. 3 previous owners. Advisory on last MOT for front "
            "brake disc wear. Drives well but will need brakes soon."
        ),
        "seller_type": "dealer",
        "location": "London, E14",
        "features": [
            "2.0d Diesel",
            "Automatic",
            "4 doors",
            "M Sport package",
            "Full leather",
            "Sat nav",
            "Parking sensors",
            "Cruise control",
        ],
        "images_count": 32,
        "registration": "BM18 SPT",
    },
    {
        "title": "2017 Vauxhall Corsa 1.4 SRi VX Line 3dr",
        "price_pence": 699500,
        "mileage": 58400,
        "description": (
            "Sporty looking Corsa in excellent condition for age. 2 owners, "
            "regular servicing. Some stone chips on bonnet. Tyres recently "
            "replaced. Great first car or commuter. Cheap to insure and run."
        ),
        "seller_type": "private",
        "location": "Leeds, LS1",
        "features": [
            "1.4 Petrol",
            "Manual",
            "3 doors",
            "SRi VX Line bodykit",
            "17-inch alloys",
            "Bluetooth",
            "Air conditioning",
        ],
        "images_count": 12,
        "registration": "VX17 CRS",
    },
    {
        "title": "2021 Toyota Yaris 1.5 Hybrid Design 5dr CVT",
        "price_pence": 1699900,
        "mileage": 19800,
        "description": (
            "Practically new Yaris Hybrid with extremely low mileage. "
            "One lady owner, garaged. Full Toyota warranty remaining. "
            "Immaculate inside and out. Incredible fuel economy - "
            "regularly achieves 60+ mpg in town."
        ),
        "seller_type": "dealer",
        "location": "Bristol, BS1",
        "features": [
            "1.5 Hybrid",
            "CVT Automatic",
            "5 doors",
            "Toyota Safety Sense",
            "Reversing camera",
            "Touchscreen infotainment",
            "Climate control",
            "Lane departure warning",
        ],
        "images_count": 28,
        "registration": "TY21 HBD",
    },
]


def _generate_demo_data(url: str, platform: str) -> ListingData:
    """Generate realistic demo listing data based on the URL.

    Uses a hash of the URL to deterministically select a demo car,
    so the same URL always returns the same data.
    """
    url_hash = int(hashlib.md5(url.encode()).hexdigest(), 16)
    car = _DEMO_CARS[url_hash % len(_DEMO_CARS)]

    return ListingData(
        url=url,
        platform=platform,
        title=car["title"],
        price_pence=car["price_pence"],
        mileage=car["mileage"],
        registration=car["registration"],
        description=car["description"],
        seller_type=car["seller_type"],
        location=car["location"],
        features=car["features"],
        images_count=car["images_count"],
        scrape_success=True,
        scrape_errors=[],
        demo_mode=True,
    )


# --- Main scraper entry point ---

_SCRAPER_MAP = {
    "autotrader": _scrape_autotrader,
    "gumtree": _scrape_gumtree,
    "facebook": _scrape_facebook,
}


async def scrape_listing(url: str) -> ListingData:
    """Scrape a car listing from a supported platform.

    Attempts live scraping first. If that fails (anti-bot measures,
    network errors, etc.), falls back to demo mode with realistic
    mock data.

    Args:
        url: The listing URL to scrape.

    Returns:
        ListingData with extracted fields. Check `demo_mode` flag
        to know if real or simulated data.
    """
    # Validate URL
    try:
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            return ListingData(
                url=url,
                platform="unknown",
                scrape_errors=["Invalid URL format"],
            )
    except Exception:
        return ListingData(
            url=url,
            platform="unknown",
            scrape_errors=["Could not parse URL"],
        )

    platform = detect_platform(url)

    if platform == "unknown":
        return ListingData(
            url=url,
            platform="unknown",
            scrape_errors=[
                "Unsupported platform. Supported: AutoTrader, Gumtree, Facebook Marketplace"
            ],
        )

    # Attempt live scrape
    scraper_fn = _SCRAPER_MAP.get(platform)
    if scraper_fn:
        try:
            async with httpx.AsyncClient(
                headers=HEADERS,
                follow_redirects=True,
                timeout=15.0,
            ) as client:
                response = await client.get(url)
                response.raise_for_status()
                html = response.text

            listing = await scraper_fn(url, html)

            # If we got meaningful data, return it
            if listing.scrape_success and (listing.title or listing.price_pence):
                logger.info(
                    f"Live scrape succeeded for {platform}: {url} "
                    f"(title={listing.title is not None}, price={listing.price_pence is not None})"
                )
                return listing

            # Scraper returned but data was too sparse - fall through to demo
            logger.info(
                f"Live scrape returned sparse data for {platform}: {url}, "
                f"falling back to demo mode"
            )

        except httpx.HTTPStatusError as e:
            logger.warning(
                f"HTTP {e.response.status_code} scraping {platform}: {url}"
            )
        except httpx.TimeoutException:
            logger.warning(f"Timeout scraping {platform}: {url}")
        except Exception as e:
            logger.warning(f"Scrape failed for {platform}: {url} - {str(e)}")

    # Fall back to demo mode
    logger.info(f"Using demo mode for {platform}: {url}")
    demo = _generate_demo_data(url, platform)
    return demo
