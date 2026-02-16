"""Gumtree search client — fetches car listing pages via Playwright headless browser."""

import asyncio
from typing import List, Optional
from urllib.parse import urlencode

from app.core.logging import logger
from app.core.config import settings
from app.core.cache import cache
from app.schemas.scraping import GumtreeListing, ScrapeRequest
from app.services.scraping.gumtree_parser import parse_search_page


GUMTREE_SEARCH_URL = "https://www.gumtree.com/search"

# Minimum HTML size to consider a page loaded (below this is likely a JS challenge page)
MIN_HTML_SIZE = 1024

# JavaScript to mask headless Chromium fingerprint from Kasada bot detection.
# Must run via add_init_script so it executes before any page JS.
STEALTH_JS = """
// Hide webdriver flag
Object.defineProperty(navigator, 'webdriver', { get: () => undefined });

// Realistic plugins array
Object.defineProperty(navigator, 'plugins', {
    get: () => [
        { name: 'Chrome PDF Plugin', filename: 'internal-pdf-viewer' },
        { name: 'Chrome PDF Viewer', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai' },
        { name: 'Native Client', filename: 'internal-nacl-plugin' },
    ],
});

// Realistic languages
Object.defineProperty(navigator, 'languages', { get: () => ['en-GB', 'en-US', 'en'] });

// Chrome runtime object
window.chrome = { runtime: {}, loadTimes: () => ({}) };

// Override permissions query
const originalQuery = window.navigator.permissions.query;
window.navigator.permissions.query = (parameters) =>
    parameters.name === 'notifications'
        ? Promise.resolve({ state: Notification.permission })
        : originalQuery(parameters);
"""


class GumtreeClient:
    """Async client for scraping Gumtree car search pages using Playwright."""

    def __init__(self):
        self._playwright = None
        self._browser = None
        self.delay = settings.GUMTREE_REQUEST_DELAY
        self.cache_ttl = settings.GUMTREE_CACHE_TTL
        self.timeout = settings.GUMTREE_TIMEOUT * 1000  # Playwright uses ms

    async def _ensure_browser(self):
        """Lazy-launch Playwright and Chromium on first use."""
        if self._browser is None:
            from playwright.async_api import async_playwright

            self._playwright = await async_playwright().start()
            self._browser = await self._playwright.chromium.launch(
                headless=True,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                ],
            )
            logger.info("Playwright browser launched")

    def _build_url(
        self,
        query: str,
        max_price: Optional[int],
        min_price: Optional[int],
        page: int,
    ) -> str:
        """Build the Gumtree search URL with query parameters."""
        params = {
            "search_category": "cars",
            "q": query,
            "page": page,
        }
        if max_price is not None:
            params["max_price"] = max_price
        if min_price is not None:
            params["min_price"] = min_price
        return f"{GUMTREE_SEARCH_URL}?{urlencode(params)}"

    async def search(
        self,
        query: str,
        max_price: Optional[int] = None,
        min_price: Optional[int] = None,
        page: int = 1,
    ) -> List[GumtreeListing]:
        """Fetch a single page of Gumtree search results.

        Args:
            query: Search term (e.g. "bmw 3 series")
            max_price: Maximum price in pounds
            min_price: Minimum price in pounds
            page: Page number (1-indexed)

        Returns:
            List of parsed GumtreeListing objects.
        """
        cache_key = f"{query}:{min_price}:{max_price}:{page}"
        cached = await cache.get("gumtree_search", cache_key)
        if cached:
            logger.info(f"Gumtree cache hit for '{query}' page {page}")
            return [GumtreeListing(**item) for item in cached]

        url = self._build_url(query, max_price, min_price, page)

        try:
            await self._ensure_browser()
            logger.info(f"Fetching Gumtree search: '{query}' page {page}")

            context = await self._browser.new_context(
                viewport={"width": 1280, "height": 720},
                user_agent=settings.GUMTREE_USER_AGENT,
                locale="en-GB",
            )
            # Inject stealth scripts before any page JS runs
            await context.add_init_script(STEALTH_JS)
            page_obj = await context.new_page()

            try:
                await page_obj.goto(url, wait_until="domcontentloaded", timeout=self.timeout)

                # Wait for real content — Kasada JS challenge resolves into
                # listing cards.  Try the main listing selector first, fall
                # back to a generous timeout so the JS challenge can execute.
                try:
                    await page_obj.wait_for_selector(
                        'article[data-q="search-result"], .listing-link, [data-q="search-results"]',
                        timeout=15000,
                    )
                except Exception:
                    # Selector didn't appear — give the JS challenge extra
                    # time and check page size afterwards.
                    await page_obj.wait_for_timeout(5000)

                html = await page_obj.content()
            finally:
                await context.close()

            if len(html) < MIN_HTML_SIZE:
                logger.warning(
                    f"Gumtree returned small HTML ({len(html)} bytes) — likely a challenge page"
                )
                return []

            listings = parse_search_page(html)

            # Cache the results
            cache_data = [listing.model_dump() for listing in listings]
            await cache.set("gumtree_search", cache_key, cache_data, ttl=self.cache_ttl)

            logger.info(f"Found {len(listings)} listings for '{query}' page {page}")
            return listings

        except Exception as e:
            logger.error(f"Gumtree fetch error: {e}")
            return []

    async def search_pages(self, request: ScrapeRequest) -> List[GumtreeListing]:
        """Fetch multiple pages of search results with rate-limited delays.

        Args:
            request: ScrapeRequest with query, price filters, and max_pages.

        Returns:
            Combined list of listings from all pages.
        """
        all_listings = []

        for page in range(1, request.max_pages + 1):
            if page > 1:
                await asyncio.sleep(self.delay)

            listings = await self.search(
                query=request.query,
                max_price=request.max_price,
                min_price=request.min_price,
                page=page,
            )
            all_listings.extend(listings)

            # Stop if no results (no more pages)
            if not listings:
                break

        return all_listings

    async def close(self):
        """Close browser and Playwright."""
        if self._browser:
            await self._browser.close()
            self._browser = None
        if self._playwright:
            await self._playwright.stop()
            self._playwright = None
            logger.info("Playwright browser closed")
