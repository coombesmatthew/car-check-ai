import json
from typing import Optional

import redis.asyncio as redis

from app.core.config import settings
from app.core.logging import logger


class CacheService:
    """Redis-based caching for external API responses."""

    def __init__(self):
        self._redis: Optional[redis.Redis] = None

    async def connect(self):
        self._redis = redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
        )
        logger.info("Redis cache connected")

    async def close(self):
        if self._redis:
            await self._redis.close()
            logger.info("Redis cache closed")

    def _key(self, prefix: str, identifier: str) -> str:
        return f"carcheck:{prefix}:{identifier.upper().replace(' ', '')}"

    async def get(self, prefix: str, identifier: str) -> Optional[dict]:
        if not self._redis:
            return None
        try:
            data = await self._redis.get(self._key(prefix, identifier))
            if data:
                logger.debug(f"Cache hit: {prefix}:{identifier}")
                return json.loads(data)
        except Exception as e:
            logger.warning(f"Cache read error: {e}")
        return None

    async def set(self, prefix: str, identifier: str, data: dict, ttl: Optional[int] = None):
        if not self._redis:
            return
        ttl = ttl or settings.REDIS_CACHE_TTL
        try:
            await self._redis.set(
                self._key(prefix, identifier),
                json.dumps(data, default=str),
                ex=ttl,
            )
            logger.debug(f"Cache set: {prefix}:{identifier} (TTL={ttl}s)")
        except Exception as e:
            logger.warning(f"Cache write error: {e}")

    async def delete(self, prefix: str, identifier: str):
        if not self._redis:
            return
        try:
            await self._redis.delete(self._key(prefix, identifier))
        except Exception as e:
            logger.warning(f"Cache delete error: {e}")


cache = CacheService()
