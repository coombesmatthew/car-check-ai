import time
import httpx
from typing import Optional, Dict

from app.core.logging import logger
from app.core.config import settings
from app.core.cache import cache


class MOTClient:
    """Client for the DVSA MOT History API (new OAuth 2.0 version).

    API: https://history.mot.api.gov.uk
    Auth: OAuth 2.0 client credentials + API key header.
    Rate limits: 500k req/day, 15 RPS.
    """

    def __init__(self):
        self.base_url = settings.MOT_API_URL
        self.api_key = settings.MOT_API_KEY
        self.client_id = settings.MOT_CLIENT_ID
        self.client_secret = settings.MOT_CLIENT_SECRET
        self.token_url = settings.MOT_TOKEN_URL
        self.scope_url = settings.MOT_SCOPE_URL
        self.client = httpx.AsyncClient(timeout=30.0)

        # Token cache
        self._access_token: Optional[str] = None
        self._token_expires_at: float = 0

    async def _get_access_token(self) -> Optional[str]:
        """Acquire OAuth 2.0 access token using client credentials flow.

        Caches token in memory until 60s before expiry.
        """
        # Return cached token if still valid
        if self._access_token and time.time() < self._token_expires_at - 60:
            return self._access_token

        if not self.client_id or not self.client_secret:
            logger.warning("MOT OAuth credentials not configured")
            return None

        try:
            response = await self.client.post(
                self.token_url,
                data={
                    "grant_type": "client_credentials",
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "scope": self.scope_url,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            response.raise_for_status()
            token_data = response.json()

            self._access_token = token_data["access_token"]
            self._token_expires_at = time.time() + token_data.get("expires_in", 3600)

            logger.info("MOT API OAuth token acquired successfully")
            return self._access_token

        except httpx.HTTPError as e:
            logger.error(f"Failed to acquire MOT OAuth token: {e}")
            return None

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

        # Get OAuth token
        token = await self._get_access_token()
        if not token:
            logger.warning("Could not acquire MOT OAuth token, returning None")
            return None

        headers = {
            "Authorization": f"Bearer {token}",
            "x-api-key": self.api_key,
            "Accept": "application/json",
        }

        try:
            logger.info(f"Fetching MOT history for {clean_reg}")

            url = f"{self.base_url}/{clean_reg}"
            response = await self.client.get(url, headers=headers)

            if response.status_code == 404:
                logger.warning(f"Vehicle not found: {clean_reg}")
                return None

            if response.status_code == 401:
                # Token expired mid-flight, clear and retry once
                self._access_token = None
                token = await self._get_access_token()
                if token:
                    headers["Authorization"] = f"Bearer {token}"
                    response = await self.client.get(url, headers=headers)
                    if response.status_code != 200:
                        logger.error(f"MOT API retry failed: {response.status_code}")
                        return None
                else:
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
