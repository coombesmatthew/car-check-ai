"""Content pipeline orchestrator — scrape -> check -> score -> generate scripts.

Coordinates the full flow from Gumtree scraping through Car Check AI
analysis to TikTok script generation.
"""

import asyncio
import time
from typing import List

from app.core.logging import logger
from app.schemas.scraping import (
    ContentPipelineRequest,
    ContentPipelineResponse,
    ContentScore,
    ScrapeRequest,
    TikTokScript,
)
from app.services.scraping.gumtree_client import GumtreeClient
from app.services.scraping.content_scorer import score_listing, rank_listings
from app.services.check.orchestrator import CheckOrchestrator
from app.services.ai.tiktok_script_generator import generate_tiktok_script


class ContentPipeline:
    """Orchestrates the full content creation pipeline."""

    def __init__(self):
        self.gumtree_client = GumtreeClient()
        self.check_orchestrator = CheckOrchestrator()

    async def run(self, request: ContentPipelineRequest) -> ContentPipelineResponse:
        """Execute the full pipeline: scrape -> check -> score -> generate scripts.

        Args:
            request: ContentPipelineRequest with scrape params and top_n.

        Returns:
            ContentPipelineResponse with scored listings and generated scripts.
        """
        start = time.time()

        # Step 1: Scrape Gumtree
        logger.info(f"Pipeline starting: query='{request.scrape.query}', top_n={request.top_n}")
        all_listings = await self.gumtree_client.search_pages(request.scrape)
        logger.info(f"Scraped {len(all_listings)} total listings")

        # Step 2: Filter to listings with VRNs
        vrn_listings = [l for l in all_listings if l.vrn]
        logger.info(f"{len(vrn_listings)} listings have VRNs")

        # Step 3: Run free checks on VRN listings (sequential, rate-limited)
        scored_listings: List[ContentScore] = []
        checked_count = 0

        for listing in vrn_listings:
            check_result = await self._run_check(listing.vrn)
            checked_count += 1

            check_dict = check_result.model_dump() if check_result else None
            scored = score_listing(listing, check_dict)
            scored_listings.append(scored)

            # Small delay between checks to avoid hammering APIs
            if checked_count < len(vrn_listings):
                await asyncio.sleep(0.5)

        # Also score listings without VRNs (no check data, lower scores)
        for listing in all_listings:
            if not listing.vrn:
                scored = score_listing(listing, None)
                scored_listings.append(scored)

        # Step 4: Rank by score
        top_listings = rank_listings(scored_listings, request.top_n)
        logger.info(f"Top {len(top_listings)} listings selected (scores: {[s.total_score for s in top_listings]})")

        # Step 5: Generate TikTok scripts for top listings
        scripts: List[TikTokScript] = []
        for scored in top_listings:
            script = await generate_tiktok_script(scored)
            scripts.append(script)

        duration = time.time() - start
        logger.info(f"Pipeline completed in {duration:.1f}s — {len(scripts)} scripts generated")

        return ContentPipelineResponse(
            scored_listings=[s for s in scored_listings if s.total_score > 0],
            scripts=scripts,
            total_scraped=len(all_listings),
            total_with_vrn=len(vrn_listings),
            total_checked=checked_count,
            pipeline_duration_seconds=round(duration, 2),
        )

    async def _run_check(self, vrn: str):
        """Run a free check for a VRN, returning the result or None on failure."""
        try:
            result = await self.check_orchestrator.run_free_check(vrn)
            return result
        except Exception as e:
            logger.warning(f"Check failed for {vrn}: {e}")
            return None

    async def close(self):
        await asyncio.gather(
            self.gumtree_client.close(),
            self.check_orchestrator.close(),
        )
