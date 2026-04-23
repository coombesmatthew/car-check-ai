"""Unified report fulfilment service.

Handles the complete post-payment flow for ALL paid tiers:
  1. Verify Stripe payment
  2. Run the appropriate check (car or EV orchestrator)
  3. Generate AI report (car or EV generator)
  4. Generate PDF (shared)
  5. Send email (shared)

Endpoints in checks.py and ev.py are thin wrappers around fulfil_report().

Idempotency + async fulfilment:
  fulfil_report_idempotent() caches the result per Stripe session_id in Redis
  for 24h so webhook + frontend can both call it safely. Webhook is the
  primary trigger (Stripe delivers it within seconds); frontend status poll
  is the fallback. This avoids the 100s gateway timeout that used to break
  PREMIUM fulfilment, since AI generation can take 2+ minutes.
"""

from __future__ import annotations

import asyncio
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime as dt
from typing import Optional

from app.core.cache import cache
from app.core.logging import logger
from app.services.check.orchestrator import CheckOrchestrator
from app.services.ev.orchestrator import EVOrchestrator
from app.services.ai.report_generator import generate_ai_report
from app.services.ai.ev_report_generator import generate_ev_report
from app.services.report.pdf_generator import generate_pdf, _extract_verdict
from app.services.notification.email_sender import send_report_email
from app.services.payment.stripe_service import retrieve_session


EV_TIERS = {"ev", "ev_health", "ev_complete"}
FULFIL_RESULT_CACHE_PREFIX = "fulfil_result"
FULFIL_LOCK_CACHE_PREFIX = "fulfil_lock"
FULFIL_RESULT_TTL_SECONDS = 86400  # 24h
FULFIL_LOCK_TTL_SECONDS = 600  # 10 min — enough for the longest AI + PDF run
FULFIL_WAIT_POLL_SECONDS = 2
FULFIL_WAIT_MAX_POLLS = 90  # 90 * 2s = 3 min max concurrent wait


@dataclass
class FulfilmentResult:
    """Standard result returned by fulfil_report() for all tiers."""

    registration: str
    report_ref: str
    email_sent: bool
    pdf_size_bytes: int
    verdict: Optional[str]
    payment_status: str
    ai_report: Optional[str]
    check_data: dict


async def fulfil_report(session_id: str) -> FulfilmentResult:
    """Run the full post-payment fulfilment pipeline.

    Routes to the correct orchestrator and AI generator based on the
    tier stored in the Stripe session metadata. Returns a FulfilmentResult
    that the calling endpoint maps to its response model.
    """
    # 1. Verify payment
    session = retrieve_session(session_id)
    if session["payment_status"] != "paid":
        from fastapi import HTTPException

        raise HTTPException(
            status_code=402,
            detail=f"Payment not completed (status: {session['payment_status']})",
        )

    registration = session["registration"]
    email = session["email"]
    tier = session.get("tier", "basic")

    # 2. Run the appropriate check + AI report
    if tier in EV_TIERS:
        check_data, ai_report = await _run_ev_pipeline(registration, tier)
        ref_prefix = "EV"
    else:
        check_data, ai_report = await _run_car_pipeline(registration, tier, session)
        ref_prefix = "CV"

    # 3. Generate PDF (shared for all tiers)
    pdf_bytes = generate_pdf(check_data, ai_report)
    verdict = _extract_verdict(ai_report) if ai_report else None

    # 4. Generate report reference
    report_ref = f"{ref_prefix}-{dt.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"

    # 5. Send email (shared for all tiers)
    email_sent = await send_report_email(
        to_email=email,
        check_data=check_data,
        pdf_bytes=pdf_bytes,
        verdict=verdict,
        report_ref=report_ref,
    )

    logger.info(
        f"{tier.upper()} report fulfilled for {registration} "
        f"(ref: {report_ref}, session: {session_id}, email: {email_sent})"
    )

    return FulfilmentResult(
        registration=registration,
        report_ref=report_ref,
        email_sent=email_sent,
        pdf_size_bytes=len(pdf_bytes),
        verdict=verdict,
        payment_status="paid",
        ai_report=ai_report,
        check_data=check_data,
    )


async def _run_ev_pipeline(registration: str, tier: str) -> tuple[dict, str | None]:
    """Run EV orchestrator + EV AI report generator."""
    orch_tier = "ev_complete" if tier == "ev_complete" else "ev_health"
    orchestrator = EVOrchestrator()
    try:
        result = await orchestrator.run_ev_check(registration, tier=orch_tier)
        check_data = result.model_dump()

        ai_report = await generate_ev_report(
            registration=registration,
            vehicle_data=getattr(orchestrator, "_raw_dvla_data", None),
            mot_analysis=getattr(orchestrator, "_raw_mot_analysis", {}),
            ev_check_data=check_data,
        )
        return check_data, ai_report
    finally:
        await orchestrator.close()


async def _run_car_pipeline(
    registration: str, tier: str, session: dict
) -> tuple[dict, str | None]:
    """Run car check orchestrator + car AI report generator."""
    orchestrator = CheckOrchestrator()
    try:
        result = await orchestrator.run_free_check(registration, tier=tier)
        check_data = result.model_dump()

        ai_report = await generate_ai_report(
            registration=registration,
            vehicle_data=getattr(orchestrator, "_raw_dvla_data", None),
            mot_analysis=getattr(orchestrator, "_raw_mot_analysis", {}),
            ulez_data=getattr(orchestrator, "_raw_ulez_data", None),
            listing_price=session.get("listing_price"),
            listing_url=session.get("listing_url"),
            check_result=check_data,
        )
        return check_data, ai_report
    finally:
        await orchestrator.close()


async def fulfil_report_idempotent(session_id: str) -> FulfilmentResult:
    """Fulfil a report, or return the cached result if already done.

    Safe for both webhook-triggered and frontend-triggered calls. Uses a Redis
    result cache (24h) + a short-lived lock so concurrent callers don't
    double-generate the AI report or send duplicate emails.
    """
    # 1. Fast path — already fulfilled?
    cached = await cache.get(FULFIL_RESULT_CACHE_PREFIX, session_id)
    if cached:
        logger.info(f"Fulfilment cache hit for session {session_id}")
        return FulfilmentResult(**cached)

    # 2. Try to become the fulfilment leader
    lock_acquired = await cache.set_nx(
        FULFIL_LOCK_CACHE_PREFIX, session_id, "1", ttl=FULFIL_LOCK_TTL_SECONDS
    )

    if not lock_acquired:
        # Another call is fulfilling — wait for its result
        logger.info(f"Waiting for concurrent fulfilment of session {session_id}")
        for _ in range(FULFIL_WAIT_MAX_POLLS):
            await asyncio.sleep(FULFIL_WAIT_POLL_SECONDS)
            cached = await cache.get(FULFIL_RESULT_CACHE_PREFIX, session_id)
            if cached:
                return FulfilmentResult(**cached)
        raise RuntimeError(
            f"Fulfilment for {session_id} timed out waiting for concurrent process"
        )

    # 3. We hold the lock — run fulfilment
    try:
        result = await fulfil_report(session_id)
        await cache.set(
            FULFIL_RESULT_CACHE_PREFIX,
            session_id,
            asdict(result),
            ttl=FULFIL_RESULT_TTL_SECONDS,
        )
        return result
    finally:
        await cache.delete(FULFIL_LOCK_CACHE_PREFIX, session_id)


async def get_fulfilment_status(session_id: str) -> Optional[FulfilmentResult]:
    """Return cached fulfilment result for a session, or None if not yet done."""
    cached = await cache.get(FULFIL_RESULT_CACHE_PREFIX, session_id)
    if cached:
        return FulfilmentResult(**cached)
    return None


def trigger_fulfilment_background(session_id: str) -> None:
    """Fire-and-forget fulfilment task. Used by webhook + frontend trigger.

    Idempotent via fulfil_report_idempotent — repeated calls are no-ops.
    """
    async def _runner():
        try:
            await fulfil_report_idempotent(session_id)
            logger.info(f"Background fulfilment completed for session {session_id}")
        except Exception as e:
            logger.error(f"Background fulfilment failed for session {session_id}: {e}")

    asyncio.create_task(_runner())


def handle_webhook(event: dict) -> dict:
    """Shared webhook handler for all tier payments.

    On checkout.session.completed, triggers fulfilment in the background
    (idempotent; safe if frontend also triggers). Both checks.py and ev.py
    route their webhook events here.
    """
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        session_id = session.get("id")
        tier = session.get("metadata", {}).get("tier", "unknown")
        reg = session.get("metadata", {}).get("registration", "unknown")
        logger.info(
            f"Webhook: checkout.session.completed for {reg} "
            f"(tier: {tier}, session: {session_id})"
        )
        if session_id:
            trigger_fulfilment_background(session_id)

    return {"received": True}
