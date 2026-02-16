"""Schemas for the Gumtree scraper and TikTok content pipeline."""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class GumtreeListing(BaseModel):
    """A single Gumtree car listing with extracted data."""

    listing_id: str = ""
    url: str = ""
    title: str = ""
    vrn: Optional[str] = None
    make: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    price: Optional[int] = Field(None, description="Price in pence")
    mileage: Optional[int] = None
    seller_type: Optional[str] = None
    image_urls: List[str] = []


class ScrapeRequest(BaseModel):
    """Request to scrape Gumtree car listings."""

    query: str = Field(..., min_length=1, max_length=100, description="Search query (e.g. 'bmw', 'ford fiesta')")
    max_price: Optional[int] = Field(None, ge=0, description="Max price in pounds")
    min_price: Optional[int] = Field(None, ge=0, description="Min price in pounds")
    max_pages: int = Field(1, ge=1, le=5, description="Number of pages to scrape (max 5)")


class ScrapeResponse(BaseModel):
    """Response from a scrape-only request."""

    listings: List[GumtreeListing] = []
    total_found: int = 0
    pages_scraped: int = 0
    vrn_count: int = Field(0, description="Number of listings with a VRN extracted")


class ScoreFactor(BaseModel):
    """A single factor contributing to a content score."""

    name: str
    points: int
    detail: str


class ContentScore(BaseModel):
    """A scored listing ready for content creation."""

    listing: GumtreeListing
    total_score: int = 0
    factors: List[ScoreFactor] = []
    check_result: Optional[Dict[str, Any]] = None
    clocking_detected: bool = False


class TikTokScript(BaseModel):
    """A generated TikTok/Reels script for a listing."""

    listing: GumtreeListing
    hook: str = ""
    script: str = ""
    hashtags: List[str] = []
    angle: str = ""
    estimated_duration_seconds: int = 30


class ContentPipelineRequest(BaseModel):
    """Request for the full content pipeline."""

    scrape: ScrapeRequest
    top_n: int = Field(3, ge=1, le=10, description="Number of top listings to generate scripts for")


class ContentPipelineResponse(BaseModel):
    """Response from the full content pipeline."""

    scored_listings: List[ContentScore] = []
    scripts: List[TikTokScript] = []
    total_scraped: int = 0
    total_with_vrn: int = 0
    total_checked: int = 0
    pipeline_duration_seconds: float = 0.0
