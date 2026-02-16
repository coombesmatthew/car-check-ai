"""Tests for the Gumtree scraper, content scorer, pipeline, and endpoints."""

import os
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from urllib.parse import quote

# Set required env vars before any app imports
os.environ.setdefault("DATABASE_URL", "postgresql://test:test@localhost:5432/test")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379")

# Patch cache before importing app
with patch("app.core.cache.CacheService.connect", new_callable=AsyncMock), \
     patch("app.core.cache.CacheService.close", new_callable=AsyncMock), \
     patch("app.core.cache.CacheService.get", new_callable=AsyncMock, return_value=None), \
     patch("app.core.cache.CacheService.set", new_callable=AsyncMock):

    from fastapi.testclient import TestClient
    from app.main import app
    from app.schemas.scraping import GumtreeListing, ContentScore, ScoreFactor
    from app.services.scraping.gumtree_parser import (
        parse_search_page,
        _parse_price,
        _parse_mileage,
        _parse_year,
    )
    from app.services.scraping.content_scorer import (
        score_listing,
        rank_listings,
    )


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


# ---------------------------------------------------------------------------
# Fixture HTML that mimics Gumtree's URL-encoded attribute structure
# ---------------------------------------------------------------------------

MOCK_GUMTREE_HTML = """
<html><body>
<div class="search-results">
""" + quote(
    '{"name":"Vehicle Registration Number","value":"AB12CDE","key":"vrn"}'
    '{"name":"Make","value":"BMW","key":"make"}'
    '{"name":"Model","value":"3 Series","key":"model"}'
    '{"name":"Year","value":"2015","key":"year"}'
    '{"name":"Price","value":"3500","key":"price"}'
    '{"name":"Mileage","value":"85000","key":"mileage"}'
    '{"name":"Seller Type","value":"Private","key":"seller_type"}'
    '<a href="/p/bmw-3-series/1234567890">BMW 3 Series 2015</a>'
) + quote(
    '{"name":"Vehicle Registration Number","value":"XY67FGH","key":"vrn"}'
    '{"name":"Make","value":"Ford","key":"make"}'
    '{"name":"Model","value":"Fiesta","key":"model"}'
    '{"name":"Year","value":"2012","key":"year"}'
    '{"name":"Price","value":"1200","key":"price"}'
    '{"name":"Mileage","value":"120000","key":"mileage"}'
    '{"name":"Seller Type","value":"Trade","key":"seller_type"}'
    '<a href="/p/ford-fiesta/9876543210">Ford Fiesta 2012</a>'
) + """
</div>
</body></html>
"""

# Fixture using REAL Gumtree attribute key names (vehicle_make, vehicle_model, etc.)
# and the real format with vipOrder/unit fields
MOCK_GUMTREE_HTML_REAL = """
<html><body>
<div class="search-results">
""" + quote(
    '{"name":"Make","value":"BMW","key":"vehicle_make","vipOrder":1,"unit":""}'
    '{"name":"Vehicle Registration Number","value":"LL61AGX","key":"vrn","vipOrder":1,"unit":""}'
    '{"name":"Model","value":"1 SERIES","key":"vehicle_model","vipOrder":2,"unit":""}'
    '{"name":"Registration Year","value":"2011","key":"vehicle_registration_year","vipOrder":3,"unit":""}'
    '{"name":"Mileage","value":"95000","key":"vehicle_mileage","vipOrder":4,"unit":"miles"}'
    '{"name":"Price","value":"2495","key":"price","vipOrder":0,"unit":""}'
    '{"name":"Seller Type","value":"Trade","key":"seller_type","vipOrder":5,"unit":""}'
    '<a href="/p/bmw-1-series/1357924680">BMW 1 Series 2011</a>'
) + quote(
    '{"name":"Make","value":"BMW","key":"vehicle_make","vipOrder":1,"unit":""}'
    '{"name":"Vehicle Registration Number","value":"K777NAH","key":"vrn","vipOrder":1,"unit":""}'
    '{"name":"Model","value":"5 SERIES","key":"vehicle_model","vipOrder":2,"unit":""}'
    '{"name":"Registration Year","value":"2008","key":"vehicle_registration_year","vipOrder":3,"unit":""}'
    '{"name":"Mileage","value":"140000","key":"vehicle_mileage","vipOrder":4,"unit":"miles"}'
    '{"name":"Price","value":"1800","key":"price","vipOrder":0,"unit":""}'
    '{"name":"Seller Type","value":"Private","key":"seller_type","vipOrder":5,"unit":""}'
    '<a href="/p/bmw-5-series/2468013579">BMW 5 Series 2008</a>'
) + """
</div>
</body></html>
"""

# HTML with no VRN (tests fallback path)
MOCK_GUMTREE_HTML_NO_VRN = """
<html><body>
<article class="listing-maxi">
  <h2><a href="/p/test-car/111222333" class="listing-link">Test Car Listing</a></h2>
  <strong class="listing-price">£2,500</strong>
  <img src="https://img.gumtree.com/photo.jpg" />
</article>
</body></html>
"""


# ---------------------------------------------------------------------------
# Parser tests
# ---------------------------------------------------------------------------

class TestGumtreeParser:
    def test_parse_search_page_extracts_vrns(self):
        listings = parse_search_page(MOCK_GUMTREE_HTML)
        vrns = [l.vrn for l in listings if l.vrn]
        assert "AB12CDE" in vrns
        assert "XY67FGH" in vrns

    def test_parse_search_page_extracts_make_model(self):
        listings = parse_search_page(MOCK_GUMTREE_HTML)
        bmw = next((l for l in listings if l.vrn == "AB12CDE"), None)
        assert bmw is not None
        assert bmw.make == "BMW"
        assert bmw.model == "3 Series"

    def test_parse_search_page_extracts_price_and_mileage(self):
        listings = parse_search_page(MOCK_GUMTREE_HTML)
        bmw = next((l for l in listings if l.vrn == "AB12CDE"), None)
        assert bmw is not None
        assert bmw.price is not None
        assert bmw.mileage == 85000

    def test_parse_search_page_extracts_year(self):
        listings = parse_search_page(MOCK_GUMTREE_HTML)
        bmw = next((l for l in listings if l.vrn == "AB12CDE"), None)
        assert bmw is not None
        assert bmw.year == 2015

    def test_real_gumtree_format_extracts_vrns(self):
        """Test parsing with real Gumtree attribute keys (vehicle_make, etc.)."""
        listings = parse_search_page(MOCK_GUMTREE_HTML_REAL)
        vrns = [l.vrn for l in listings if l.vrn]
        assert "LL61AGX" in vrns
        assert "K777NAH" in vrns  # private plate format

    def test_real_gumtree_format_extracts_make_model(self):
        listings = parse_search_page(MOCK_GUMTREE_HTML_REAL)
        bmw1 = next((l for l in listings if l.vrn == "LL61AGX"), None)
        assert bmw1 is not None
        assert bmw1.make == "BMW"
        assert bmw1.model == "1 SERIES"
        assert bmw1.year == 2011
        assert bmw1.mileage == 95000

    def test_real_gumtree_format_extracts_price(self):
        listings = parse_search_page(MOCK_GUMTREE_HTML_REAL)
        bmw5 = next((l for l in listings if l.vrn == "K777NAH"), None)
        assert bmw5 is not None
        assert bmw5.price is not None
        assert bmw5.seller_type == "Private"

    def test_parse_search_page_handles_empty_html(self):
        listings = parse_search_page("")
        assert listings == []

    def test_parse_search_page_html_fallback(self):
        listings = parse_search_page(MOCK_GUMTREE_HTML_NO_VRN)
        assert len(listings) >= 1
        assert listings[0].title == "Test Car Listing"
        assert listings[0].listing_id == "111222333"

    def test_fallback_extracts_price(self):
        listings = parse_search_page(MOCK_GUMTREE_HTML_NO_VRN)
        assert len(listings) >= 1
        assert listings[0].price is not None

    def test_fallback_extracts_image(self):
        listings = parse_search_page(MOCK_GUMTREE_HTML_NO_VRN)
        assert len(listings) >= 1
        assert len(listings[0].image_urls) > 0


class TestParserHelpers:
    def test_parse_price_pounds(self):
        assert _parse_price("2500") == 250000
        assert _parse_price("£3,500") == 350000

    def test_parse_price_none(self):
        assert _parse_price("") is None
        assert _parse_price(None) is None

    def test_parse_mileage(self):
        assert _parse_mileage("85000") == 85000
        assert _parse_mileage("85,000 miles") == 85000

    def test_parse_mileage_none(self):
        assert _parse_mileage("") is None
        assert _parse_mileage(None) is None

    def test_parse_year_valid(self):
        assert _parse_year("2015") == 2015
        assert _parse_year("1998") == 1998

    def test_parse_year_invalid(self):
        assert _parse_year("") is None
        assert _parse_year("not_a_year") is None
        assert _parse_year("1800") is None


# ---------------------------------------------------------------------------
# Content scorer tests
# ---------------------------------------------------------------------------

class TestContentScorer:
    def _make_listing(self, **kwargs) -> GumtreeListing:
        defaults = {
            "listing_id": "123",
            "title": "Test Car",
            "vrn": "AB12CDE",
            "make": "BMW",
            "model": "3 Series",
            "year": 2015,
            "price": 100000,  # £1,000 in pence
            "mileage": 85000,
        }
        defaults.update(kwargs)
        return GumtreeListing(**defaults)

    def test_score_suspiciously_cheap(self):
        # A 5-year-old car for £500 should trigger price anomaly
        listing = self._make_listing(year=2021, price=50000)
        scored = score_listing(listing, None)
        price_factors = [f for f in scored.factors if f.name == "price_anomaly"]
        assert len(price_factors) == 1
        assert price_factors[0].points > 0

    def test_score_clocking_detected(self):
        listing = self._make_listing()
        check_result = {
            "clocking_analysis": {
                "clocked": True,
                "risk_level": "high",
                "flags": [{"type": "mileage_drop", "severity": "high", "detail": "Mileage dropped"}],
            },
            "condition_score": 50,
            "failure_patterns": [],
        }
        scored = score_listing(listing, check_result)
        assert scored.clocking_detected is True
        clocking_factors = [f for f in scored.factors if f.name == "clocking_detected"]
        assert len(clocking_factors) == 1
        assert clocking_factors[0].points >= 15

    def test_score_poor_condition(self):
        listing = self._make_listing()
        check_result = {
            "clocking_analysis": {"clocked": False, "risk_level": "none", "flags": []},
            "condition_score": 35,
            "failure_patterns": [],
        }
        scored = score_listing(listing, check_result)
        condition_factors = [f for f in scored.factors if f.name == "poor_condition"]
        assert len(condition_factors) == 1
        assert condition_factors[0].points == 15

    def test_score_recurring_failures(self):
        listing = self._make_listing()
        check_result = {
            "clocking_analysis": {"clocked": False, "risk_level": "none", "flags": []},
            "condition_score": 80,
            "failure_patterns": [
                {"category": "brake", "occurrences": 5, "concern_level": "high"},
            ],
        }
        scored = score_listing(listing, check_result)
        failure_factors = [f for f in scored.factors if f.name == "recurring_failures"]
        assert len(failure_factors) == 1
        assert failure_factors[0].points == 10

    def test_score_no_data(self):
        listing = self._make_listing(year=None, price=None, mileage=None)
        scored = score_listing(listing, None)
        assert scored.total_score == 0
        assert scored.factors == []

    def test_rank_listings(self):
        listings = [
            ContentScore(listing=self._make_listing(), total_score=10, factors=[]),
            ContentScore(listing=self._make_listing(), total_score=50, factors=[]),
            ContentScore(listing=self._make_listing(), total_score=30, factors=[]),
        ]
        ranked = rank_listings(listings, top_n=2)
        assert len(ranked) == 2
        assert ranked[0].total_score == 50
        assert ranked[1].total_score == 30

    def test_high_mileage_scores(self):
        # 3x expected mileage for age
        listing = self._make_listing(year=2020, mileage=150000)
        scored = score_listing(listing, None)
        mileage_factors = [f for f in scored.factors if f.name == "mileage_anomaly"]
        assert len(mileage_factors) == 1
        assert mileage_factors[0].points >= 12


# ---------------------------------------------------------------------------
# TikTok script generator tests (demo mode)
# ---------------------------------------------------------------------------

class TestTikTokScriptGenerator:
    @pytest.mark.asyncio
    async def test_demo_script_clocking(self):
        from app.services.ai.tiktok_script_generator import generate_tiktok_script

        listing = GumtreeListing(
            listing_id="123", title="BMW 3 Series", vrn="AB12CDE",
            make="BMW", model="3 Series", year=2015, price=350000, mileage=85000,
        )
        scored = ContentScore(
            listing=listing,
            total_score=45,
            factors=[ScoreFactor(name="clocking_detected", points=30, detail="Mileage clocking detected")],
            clocking_detected=True,
        )
        script = await generate_tiktok_script(scored, angle="auto")
        assert script.angle == "clocking_expose"
        assert "CLOCKED" in script.hook.upper() or "clocked" in script.hook.lower()
        assert len(script.hashtags) > 0

    @pytest.mark.asyncio
    async def test_demo_script_bargain(self):
        from app.services.ai.tiktok_script_generator import generate_tiktok_script

        listing = GumtreeListing(
            listing_id="456", title="Ford Fiesta", vrn="XY67FGH",
            make="Ford", model="Fiesta", year=2018, price=100000, mileage=40000,
        )
        scored = ContentScore(
            listing=listing,
            total_score=25,
            factors=[ScoreFactor(name="price_anomaly", points=25, detail="Suspiciously cheap")],
            clocking_detected=False,
        )
        script = await generate_tiktok_script(scored, angle="bargain_hunter")
        assert script.angle == "bargain_hunter"
        assert script.script != ""
        assert script.hook != ""


# ---------------------------------------------------------------------------
# Pipeline integration tests
# ---------------------------------------------------------------------------

class TestContentPipeline:
    @pytest.mark.asyncio
    async def test_pipeline_with_mocked_services(self):
        from app.services.scraping.content_pipeline import ContentPipeline
        from app.schemas.scraping import ContentPipelineRequest, ScrapeRequest
        from app.schemas.check import FreeCheckResponse

        mock_listings = [
            GumtreeListing(
                listing_id="1", title="BMW 3 Series", vrn="AB12CDE",
                make="BMW", model="3 Series", year=2015, price=350000, mileage=85000,
            ),
            GumtreeListing(
                listing_id="2", title="Ford Fiesta", vrn="XY67FGH",
                make="Ford", model="Fiesta", year=2012, price=120000, mileage=120000,
            ),
        ]

        mock_check = FreeCheckResponse(
            registration="AB12CDE",
            tier="free",
            condition_score=70,
            clocking_analysis=None,
        )

        pipeline = ContentPipeline()
        pipeline.gumtree_client.search_pages = AsyncMock(return_value=mock_listings)
        pipeline.check_orchestrator.run_free_check = AsyncMock(return_value=mock_check)

        request = ContentPipelineRequest(
            scrape=ScrapeRequest(query="bmw", max_price=5000, max_pages=1),
            top_n=2,
        )

        result = await pipeline.run(request)

        assert result.total_scraped == 2
        assert result.total_with_vrn == 2
        assert result.total_checked == 2
        assert len(result.scripts) <= 2
        assert result.pipeline_duration_seconds > 0

    @pytest.mark.asyncio
    async def test_pipeline_handles_check_failure(self):
        from app.services.scraping.content_pipeline import ContentPipeline
        from app.schemas.scraping import ContentPipelineRequest, ScrapeRequest

        mock_listings = [
            GumtreeListing(
                listing_id="1", title="BMW", vrn="AB12CDE",
                make="BMW", year=2015, price=350000,
            ),
        ]

        pipeline = ContentPipeline()
        pipeline.gumtree_client.search_pages = AsyncMock(return_value=mock_listings)
        pipeline.check_orchestrator.run_free_check = AsyncMock(side_effect=Exception("API down"))

        request = ContentPipelineRequest(
            scrape=ScrapeRequest(query="bmw", max_pages=1),
            top_n=1,
        )

        result = await pipeline.run(request)
        # Should still complete despite check failure
        assert result.total_scraped == 1
        assert result.total_checked == 1


# ---------------------------------------------------------------------------
# API endpoint tests
# ---------------------------------------------------------------------------

class TestContentEndpoints:
    @patch("app.api.v1.endpoints.content.GumtreeClient")
    def test_scrape_endpoint(self, MockGumtreeClient, client):
        mock_client = MagicMock()
        mock_client.search_pages = AsyncMock(return_value=[
            GumtreeListing(
                listing_id="1", title="BMW 3 Series", vrn="AB12CDE",
                make="BMW", price=350000,
            ),
        ])
        mock_client.close = AsyncMock()
        MockGumtreeClient.return_value = mock_client

        response = client.post(
            "/api/v1/content/scrape",
            json={"query": "bmw", "max_price": 5000, "max_pages": 1},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total_found"] == 1
        assert data["vrn_count"] == 1
        assert len(data["listings"]) == 1

    @patch("app.api.v1.endpoints.content.ContentPipeline")
    def test_pipeline_endpoint(self, MockPipeline, client):
        from app.schemas.scraping import ContentPipelineResponse

        mock_pipeline = MagicMock()
        mock_pipeline.run = AsyncMock(return_value=ContentPipelineResponse(
            scored_listings=[],
            scripts=[],
            total_scraped=5,
            total_with_vrn=3,
            total_checked=3,
            pipeline_duration_seconds=2.5,
        ))
        mock_pipeline.close = AsyncMock()
        MockPipeline.return_value = mock_pipeline

        response = client.post(
            "/api/v1/content/pipeline",
            json={"scrape": {"query": "ford", "max_pages": 1}, "top_n": 3},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total_scraped"] == 5
        assert data["total_checked"] == 3

    def test_scrape_endpoint_validation(self, client):
        # Missing required query field
        response = client.post(
            "/api/v1/content/scrape",
            json={"max_pages": 1},
        )
        assert response.status_code == 422

    def test_pipeline_endpoint_validation(self, client):
        # max_pages too high
        response = client.post(
            "/api/v1/content/pipeline",
            json={"scrape": {"query": "bmw", "max_pages": 100}, "top_n": 3},
        )
        assert response.status_code == 422
