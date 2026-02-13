import httpx
from typing import Optional, Dict

from app.core.logging import logger
from app.core.config import settings
from app.core.cache import cache


class MOTClient:
    """Client for the DVSA MOT History API.

    API docs: https://dvsa.github.io/mot-history-api-documentation/
    Returns full MOT test history including odometer readings, advisories,
    failures with severity, test dates, and expiry.
    Rate limits: 500k req/day, 15 RPS.
    """

    def __init__(self):
        self.base_url = settings.MOT_API_URL
        self.api_key = settings.MOT_API_KEY
        self.client = httpx.AsyncClient(timeout=30.0)

    async def get_mot_history(self, registration: str) -> Optional[Dict]:
        """Fetch MOT history for a vehicle registration.

        Args:
            registration: Vehicle registration number

        Returns:
            Dict containing MOT history or None if not found.
        """
        clean_reg = registration.upper().replace(" ", "")

        # Check cache first
        cached = await cache.get("mot", clean_reg)
        if cached:
            return cached

        if not self.api_key or self.api_key.startswith("your_"):
            logger.warning("MOT API key not configured, returning None")
            return None

        headers = {
            "x-api-key": self.api_key,
            "Accept": "application/json",
        }

        try:
            logger.info(f"Fetching MOT history for {clean_reg}")

            response = await self.client.get(
                self.base_url,
                params={"registration": clean_reg},
                headers=headers,
            )

            if response.status_code == 404:
                logger.warning(f"Vehicle not found: {clean_reg}")
                return None

            response.raise_for_status()
            data = response.json()

            # Cache for 1 hour
            await cache.set("mot", clean_reg, data, ttl=settings.REDIS_MOT_TTL)

            logger.info(f"Successfully fetched MOT history for {clean_reg}")
            return data

        except httpx.HTTPError as e:
            logger.error(f"Error fetching MOT data: {e}")
            return None

    async def close(self):
        await self.client.aclose()
