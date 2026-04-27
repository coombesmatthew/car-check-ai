"""Admin endpoints — operational visibility + resend.

All endpoints gated by ADMIN_API_TOKEN env var passed as `?token=...`.
Empty token disables every endpoint (returns 503). Pure ops — no
customer-facing surface.
"""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import select

from app.core.cache import cache
from app.core.config import settings
from app.core.db import get_session
from app.core.logging import logger
from app.models.api_call import ApiCall
from app.services.fulfilment import FULFIL_RESULT_CACHE_PREFIX, FulfilmentResult
from app.services.notification.email_sender import send_report_email
from app.services.payment.stripe_service import retrieve_session

router = APIRouter()


def _check_token(token: str) -> None:
    if not settings.ADMIN_API_TOKEN:
        raise HTTPException(status_code=503, detail="Admin endpoints disabled — set ADMIN_API_TOKEN")
    if token != settings.ADMIN_API_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid admin token")


@router.post("/resend-email")
async def resend_email(
    session_id: str = Query(..., description="Stripe checkout session_id"),
    to_email: Optional[str] = Query(None, description="Override recipient — defaults to Stripe metadata email"),
    token: str = Query(..., description="Admin API token"),
):
    """Re-send the report email for a previously fulfilled session.

    Reads the cached check_data from Redis and pipes it through send_report_email
    again. If Redis has expired the cache (after 30 days), returns 404 and asks
    the caller to re-fulfil via /basic/fulfil/trigger.
    """
    _check_token(token)

    cached = await cache.get(FULFIL_RESULT_CACHE_PREFIX, session_id)
    if not cached:
        raise HTTPException(
            status_code=404,
            detail="No cached fulfilment for that session. Trigger a fresh fulfilment via /basic/fulfil/trigger.",
        )

    result = FulfilmentResult(**cached)
    target_email = to_email
    if not target_email:
        # Recover the original email from Stripe metadata
        try:
            stripe_session = retrieve_session(session_id)
            target_email = stripe_session.get("email")
        except Exception as e:
            logger.error(f"Could not retrieve Stripe session {session_id} for resend: {e}")
            raise HTTPException(status_code=502, detail=f"Stripe lookup failed: {e}")

    if not target_email:
        raise HTTPException(status_code=400, detail="No recipient email — pass ?to_email=...")

    sent = await send_report_email(
        to_email=target_email,
        check_data=result.check_data,
        report_ref=result.report_ref,
        session_id=session_id,
    )

    logger.info(f"ADMIN: resend-email session={session_id} to={target_email} sent={sent}")
    if not sent:
        raise HTTPException(
            status_code=502,
            detail="send_report_email returned False — check Railway logs for the upstream error",
        )

    return {
        "session_id": session_id,
        "to_email": target_email,
        "report_ref": result.report_ref,
        "sent": True,
    }


@router.get("/recent-fulfilments")
async def recent_fulfilments(
    token: str = Query(..., description="Admin API token"),
    hours: int = Query(48, ge=1, le=720, description="Look-back window"),
):
    """List recent paid fulfilments inferred from api_calls activity.

    Postgres api_calls is the durable record of every paid call. Group by
    session_id (when present) to surface anything from the last N hours so we
    can spot silent email failures.
    """
    _check_token(token)

    cutoff = datetime.utcnow() - timedelta(hours=hours)

    async with get_session() as session:
        stmt = (
            select(ApiCall)
            .where(ApiCall.created_at >= cutoff)
            .where(ApiCall.session_id.is_not(None))
            .order_by(ApiCall.created_at.desc())
            .limit(500)
        )
        result_rows = await session.execute(stmt)
        rows = result_rows.scalars().all()

    sessions: dict = {}
    for r in rows:
        sid = r.session_id
        if sid not in sessions:
            sessions[sid] = {
                "session_id": sid,
                "registration": r.registration,
                "tier": r.tier,
                "first_call": r.created_at.isoformat(),
                "last_call": r.created_at.isoformat(),
                "calls": 0,
                "errors": 0,
            }
        s = sessions[sid]
        s["calls"] += 1
        if r.status_code and r.status_code >= 400:
            s["errors"] += 1
        ts = r.created_at.isoformat()
        if ts < s["first_call"]:
            s["first_call"] = ts
        if ts > s["last_call"]:
            s["last_call"] = ts

    return {
        "hours": hours,
        "session_count": len(sessions),
        "sessions": sorted(sessions.values(), key=lambda x: x["last_call"], reverse=True),
    }
