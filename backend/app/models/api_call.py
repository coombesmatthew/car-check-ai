"""ApiCall ORM model + record_api_call() helper.

Every outbound paid API call is persisted here so we can:
  1. Diagnose failures (capture status + response body snippet).
  2. Roll up daily/monthly spend per service.
  3. Find which registrations cost the most.

Wired in from `oneauto_client._get()`; extend to Anthropic / Resend later.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, Index, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID

from app.core.logging import logger
from app.models.base import Base


class ApiCall(Base):
    __tablename__ = "api_calls"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    service = Column(String(32), nullable=False, index=True)       # oneauto / anthropic / resend / dvla / mot / stripe
    endpoint = Column(String(256), nullable=False)                 # /experian/autocheck/v3, messages.create, ...
    status_code = Column(Integer)                                  # HTTP status when applicable
    duration_ms = Column(Integer)
    cost_gbp = Column(Numeric(10, 4), default=0)                   # 0 for free services; populated later by billing lookup

    registration = Column(String(16), index=True)                  # VRM if applicable
    tier = Column(String(16))                                      # basic / premium / ev_health / ev_complete / free
    session_id = Column(String(128))                               # Stripe checkout session for cost-per-customer rollup

    error = Column(String(512))                                    # short error summary
    response_body = Column(Text)                                   # first 500 chars of response body on failure

    tokens_in = Column(Integer)                                    # Anthropic only
    tokens_out = Column(Integer)

    __table_args__ = (
        Index("ix_api_calls_service_created_at", "service", "created_at"),
    )


async def record_api_call(
    *,
    service: str,
    endpoint: str,
    status_code: Optional[int] = None,
    duration_ms: Optional[int] = None,
    cost_gbp: Optional[float] = None,
    registration: Optional[str] = None,
    tier: Optional[str] = None,
    session_id: Optional[str] = None,
    error: Optional[str] = None,
    response_body: Optional[str] = None,
    tokens_in: Optional[int] = None,
    tokens_out: Optional[int] = None,
) -> None:
    """Persist a single outbound API call. Never raises — logs and swallows
    any DB error so tracking failure can't break primary requests.

    Kept as a free function (not a service) so call sites stay one-line.
    """
    # Lazy import avoids a top-level dependency on the async engine for
    # call sites that may be imported before settings are available
    # (e.g. tests or management scripts).
    from app.core.db import get_session

    try:
        async with get_session() as session:
            row = ApiCall(
                service=service,
                endpoint=endpoint,
                status_code=status_code,
                duration_ms=duration_ms,
                cost_gbp=cost_gbp if cost_gbp is not None else 0,
                registration=registration.upper() if registration else None,
                tier=tier,
                session_id=session_id,
                error=error[:512] if error else None,
                response_body=response_body,
                tokens_in=tokens_in,
                tokens_out=tokens_out,
            )
            session.add(row)
    except Exception as e:
        logger.warning(f"record_api_call failed ({service} {endpoint}): {e}")
