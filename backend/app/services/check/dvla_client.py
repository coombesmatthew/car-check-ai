import httpx
from typing import Optional, Dict

from app.core.logging import logger
from app.core.config import settings
from app.core.cache import cache


class DVLAClient:
    """Client for the DVLA Vehicle Enquiry Service (VES) API.

    API docs: https://developer-portal.driver-vehicle-licensing.api.gov.uk/
    Returns: taxStatus, motStatus, make, yearOfManufacture, engineCapacity,
             co2Emissions, fuelType, euroStatus, colour, dateOfLastV5CIssued,
             markedForExport, and more.
    """

    def __init__(self):
        self.base_url = settings.DVLA_VES_URL
        self.api_key = settings.DVLA_VES_API_KEY
        self.client = httpx.AsyncClient(timeout=15.0)

    async def get_vehicle(self, registration: str) -> Optional[Dict]:
        """Fetch vehicle details from DVLA VES API.

        Args:
            registration: UK vehicle registration number (e.g. "AB12CDE")

        Returns:
            Dict with vehicle data or None if not found / API unavailable.
        """
        clean_reg = registration.upper().replace(" ", "")

        # Check cache first
        cached = await cache.get("dvla", clean_reg)
        if cached:
            return cached

        if not self.api_key or self.api_key.startswith("your_"):
            logger.warning("DVLA VES API key not configured, returning None")
            return None

        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
        }

        try:
            logger.info(f"Fetching DVLA data for {clean_reg}")
            response = await self.client.post(
                self.base_url,
                json={"registrationNumber": clean_reg},
                headers=headers,
            )

            if response.status_code == 404:
                logger.warning(f"Vehicle not found in DVLA: {clean_reg}")
                return None

            if response.status_code == 429:
                logger.error("DVLA API rate limit exceeded")
                return None

            response.raise_for_status()
            data = response.json()

            # Cache for 24 hours
            await cache.set("dvla", clean_reg, data, ttl=settings.REDIS_DVLA_TTL)

            logger.info(f"Successfully fetched DVLA data for {clean_reg}")
            return data

        except httpx.HTTPError as e:
            logger.error(f"DVLA API error: {e}")
            return None

    async def close(self):
        await self.client.aclose()
