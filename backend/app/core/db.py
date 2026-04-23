"""Async SQLAlchemy session helper.

The backend has been stateless to date — models exist in `app/models/` but
nothing persisted. This module is the first async session layer; it's used
by `api_call.record_api_call()` to persist an audit log of outbound API
calls (One Auto, Anthropic, etc.) for diagnostics and cost tracking.

Keep this simple: one shared engine, one sessionmaker, one `get_session()`
async context manager. Extend later if we need transactional decorators
or per-request scopes.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncIterator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings
from app.core.logging import logger


def _async_dsn(sync_dsn: str) -> str:
    """Convert a sync postgres DSN to asyncpg. Railway provides a
    `postgresql://...` URL; asyncpg needs `postgresql+asyncpg://...`."""
    if sync_dsn.startswith("postgresql+asyncpg://"):
        return sync_dsn
    if sync_dsn.startswith("postgres://"):
        return sync_dsn.replace("postgres://", "postgresql+asyncpg://", 1)
    if sync_dsn.startswith("postgresql://"):
        return sync_dsn.replace("postgresql://", "postgresql+asyncpg://", 1)
    return sync_dsn


_engine = None
_sessionmaker: async_sessionmaker[AsyncSession] | None = None


def _get_sessionmaker() -> async_sessionmaker[AsyncSession]:
    global _engine, _sessionmaker
    if _sessionmaker is None:
        dsn = _async_dsn(settings.DATABASE_URL)
        _engine = create_async_engine(dsn, pool_pre_ping=True, pool_size=5, max_overflow=5)
        _sessionmaker = async_sessionmaker(_engine, expire_on_commit=False)
        logger.info("Async DB sessionmaker initialised")
    return _sessionmaker


@asynccontextmanager
async def get_session() -> AsyncIterator[AsyncSession]:
    """Yield an AsyncSession. Auto-commits on clean exit, rolls back on error."""
    sessionmaker = _get_sessionmaker()
    async with sessionmaker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
