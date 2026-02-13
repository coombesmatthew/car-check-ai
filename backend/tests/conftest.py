import os
import pytest
from unittest.mock import AsyncMock, patch

# Set required env vars before any app imports
os.environ.setdefault("DATABASE_URL", "postgresql://test:test@localhost:5432/test")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379")

# Patch cache before importing app to avoid Redis connection on startup
with patch("app.core.cache.CacheService.connect", new_callable=AsyncMock), \
     patch("app.core.cache.CacheService.close", new_callable=AsyncMock), \
     patch("app.core.cache.CacheService.get", new_callable=AsyncMock, return_value=None), \
     patch("app.core.cache.CacheService.set", new_callable=AsyncMock):

    from fastapi.testclient import TestClient
    from app.main import app


@pytest.fixture
def client():
    """FastAPI test client with mocked Redis cache."""
    with TestClient(app) as c:
        yield c
