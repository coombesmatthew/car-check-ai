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
from app.services.monitoring.daily_digest import run_daily_digest
from app.services.monitoring.health_checks import run_health_check
from app.services.notification.discord import notify_discord
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

    # Discord ping closes the loop publicly so anyone watching the channel
    # knows the prior alert was actioned. GDPR: no PII, just identifiers.
    await notify_discord(
        f"✅ **Email resent** — Reg: `{result.registration}` · "
        f"Ref: `{result.report_ref}` · Session: `{session_id}`"
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


@router.get("/ghost-paid-sessions")
async def ghost_paid_sessions(
    token: str = Query(..., description="Admin API token"),
    hours: int = Query(168, ge=1, le=720, description="Look-back window (default 7 days)"),
    min_amount_pence: int = Query(
        100,
        ge=0,
        description="Skip sessions below this amount. Default 100 (£1) — filters out 100%-off TESTABC123 promo sessions. Pass 0 to see all.",
    ),
):
    """List paid Stripe sessions in the look-back window with NO cached
    fulfilment in Redis — i.e. the customer paid but we never delivered.

    Use this after replaying failed Stripe webhook events to spot any
    customer whose payment succeeded but whose report never landed
    (Stewart-style ghosts). Each entry shows the curl-able resend URL.

    By default skips sessions with amount_total < £1 to filter out internal
    test sessions using the TESTABC123 100%-off promo. Pass min_amount_pence=0
    to include those.
    """
    _check_token(token)

    import stripe as stripe_lib

    from app.services.payment.stripe_service import _init_stripe

    _init_stripe()
    cutoff = datetime.utcnow() - timedelta(hours=hours)
    cutoff_unix = int(cutoff.timestamp())

    ghosts: list[dict] = []
    excluded_test_count = 0
    try:
        # Iterate paid checkout sessions in the window
        sessions = stripe_lib.checkout.Session.list(
            created={"gte": cutoff_unix},
            limit=100,
            status="complete",
        )
        for s in sessions.auto_paging_iter():
            if s.payment_status != "paid":
                continue
            cached = await cache.get(FULFIL_RESULT_CACHE_PREFIX, s.id)
            if cached:
                continue
            amount = s.amount_total or 0
            if amount < min_amount_pence:
                excluded_test_count += 1
                continue
            metadata = s.metadata or {}
            ghosts.append({
                "session_id": s.id,
                "registration": metadata.get("registration"),
                "tier": metadata.get("tier"),
                "amount_total_pence": amount,
                "created": datetime.utcfromtimestamp(s.created).isoformat() + "Z",
                "resend_url": (
                    f"POST /api/v1/admin/resend-email?session_id={s.id}&token=…"
                ),
            })
    except Exception as e:
        logger.error(f"ghost-paid-sessions Stripe iteration failed: {e}")
        raise HTTPException(status_code=502, detail=f"Stripe lookup failed: {e}")

    return {
        "hours": hours,
        "min_amount_pence": min_amount_pence,
        "ghost_count": len(ghosts),
        "excluded_below_threshold": excluded_test_count,
        "ghosts": ghosts,
    }


@router.post("/run-health-check")
async def run_health_check_endpoint(
    token: str = Query(..., description="Admin API token"),
    notify: bool = Query(True, description="Ping Discord on failure (default true)"),
):
    """Run sandbox heartbeats + live-traffic analysis. Designed for hourly cron.

    External cron (GitHub Actions / cron-job.org / UptimeRobot) hits this
    endpoint every ~60 min. Returns a structured report; if `notify=true`,
    posts a Discord alert when anything is unhealthy. The endpoint always
    returns 200 with the report — the cron decides what to do based on
    `healthy: true/false` in the JSON.

    Sandbox calls don't bill against the live OneAuto credit, so this
    monitor is free regardless of how often it runs.
    """
    _check_token(token)

    report = await run_health_check(notify_on_failure=notify)
    return report.to_dict()


@router.post("/run-daily-digest")
async def run_daily_digest_endpoint(
    token: str = Query(..., description="Admin API token"),
    notify: bool = Query(True, description="Post the digest to Discord (default true)"),
):
    """Build and post the previous-day digest to Discord. Designed for daily cron.

    GitHub Actions hits this once per day at ~08:00 UTC (≈ 09:00 BST).
    Pulls paid checks + revenue from Stripe, free-check delta from a
    Redis snapshot, and OneAuto error rates from api_calls. Returns the
    structured report; posts to Discord when notify=true.

    Pass notify=false to dry-run from a curl without spamming the channel.
    """
    _check_token(token)

    report = await run_daily_digest(notify=notify)
    return report.to_dict()
