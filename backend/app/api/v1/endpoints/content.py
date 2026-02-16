"""API endpoints for the Gumtree scraper and content pipeline."""

from fastapi import APIRouter, HTTPException

from app.core.logging import logger
from app.schemas.scraping import (
    ScrapeRequest,
    ScrapeResponse,
    ContentPipelineRequest,
    ContentPipelineResponse,
)
from app.services.scraping.gumtree_client import GumtreeClient
from app.services.scraping.content_pipeline import ContentPipeline

router = APIRouter()


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
