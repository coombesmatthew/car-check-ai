"""Unified report fulfilment service.

Handles the complete post-payment flow for ALL paid tiers:
  1. Verify Stripe payment
  2. Run the appropriate check (car or EV orchestrator)
  3. Generate PDF (shared)
  4. Send email (shared)

Endpoints in checks.py and ev.py are thin wrappers around fulfil_report().

Idempotency + async fulfilment:
  fulfil_report_idempotent() caches the result per Stripe session_id in Redis
  for 24h so webhook + frontend can both call it safely. Webhook is the
  primary trigger (Stripe delivers it within seconds); frontend status poll
  is the fallback.
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
from app.services.notification.analytics import (
    EVENT_EMAIL_FAILED,
    EVENT_EMAIL_SENT,
    EVENT_FULFILMENT_COMPLETED,
    EVENT_PAYMENT_RECEIVED,
    track_event,
)
from app.services.notification.discord import alert_email_failure, alert_payment_received
from app.services.notification.email_sender import send_report_email
from app.services.payment.stripe_service import retrieve_session


EV_TIERS = {"ev", "ev_health", "ev_complete"}
FULFIL_RESULT_CACHE_PREFIX = "fulfil_result"
FULFIL_LOCK_CACHE_PREFIX = "fulfil_lock"
FULFIL_RESULT_TTL_SECONDS = 30 * 86400  # 30 days — customers can revisit via email link
FULFIL_LOCK_TTL_SECONDS = 600  # 10 min — enough for the longest AI + PDF run
FULFIL_WAIT_POLL_SECONDS = 2
FULFIL_WAIT_MAX_POLLS = 90  # 90 * 2s = 3 min max concurrent wait


@dataclass
class FulfilmentResult:
    """Standard result returned by fulfil_report() for all tiers."""

    registration: str
    report_ref: str
    email_sent: bool
    verdict: Optional[str]
    payment_status: str
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
    tier = session.get("tier", "premium")

    # 2. Run the appropriate check
    if tier in EV_TIERS:
        check_data = await _run_ev_pipeline(registration, tier)
        ref_prefix = "EV"
    else:
        check_data = await _run_car_pipeline(registration, tier)
        ref_prefix = "CV"

    # 2b. Attach optional listing_price (pence) from the Stripe metadata so
    # the paid report can show "you paid £X vs valuation". Captured from the
    # modal before checkout; absent if user skipped.
    listing_price = session.get("listing_price")
    if listing_price:
        check_data["listing_price"] = listing_price

    # PostHog: payment received + fulfilment computed (separate events because
    # they answer different funnel questions). GDPR: registration is hashed.
    track_event(
        event=EVENT_PAYMENT_RECEIVED,
        registration=registration,
        properties={"tier": tier, "has_listing_price": listing_price is not None},
    )
    track_event(
        event=EVENT_FULFILMENT_COMPLETED,
        registration=registration,
        properties={
            "tier": tier,
            "has_battery_health": bool(check_data.get("battery_health")),
            "has_charging_costs": bool(check_data.get("charging_costs")),
            "has_valuation": bool(check_data.get("valuation")),
            "has_provenance": bool(check_data.get("finance_check") or check_data.get("stolen_check")),
        },
    )

    # 3. Generate report reference
    report_ref = f"{ref_prefix}-{dt.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"

    # 4. Send email — the report lives online for 30 days; no PDF attachment.
    email_sent = await send_report_email(
        to_email=email,
        check_data=check_data,
        report_ref=report_ref,
        session_id=session_id,
    )

    if email_sent:
        logger.info(
            f"{tier.upper()} report fulfilled for {registration} "
            f"(ref: {report_ref}, session: {session_id}, email: True)"
        )
        # Discord celebratory ping. GDPR-safe: tier/reg/ref/session_id only.
        await alert_payment_received(
            tier=tier,
            registration=registration,
            report_ref=report_ref,
            session_id=session_id,
        )
        track_event(
            event=EVENT_EMAIL_SENT,
            registration=registration,
            properties={"tier": tier, "report_ref": report_ref},
        )
    else:
        # Loud, grep-able tag so future failures get caught fast. Customer paid
        # but email didn't land — needs a manual resend via /admin/resend-email.
        logger.error(
            f"EMAIL_DELIVERY_FAILURE | {tier.upper()} report fulfilled for "
            f"{registration} (ref: {report_ref}, session: {session_id}, "
            f"to: {email}) — send_report_email returned False, see preceding "
            f"log line for upstream cause. Use POST /api/v1/admin/resend-email"
            f"?session_id={session_id}&token=..."
        )
        # Discord 🚨 ping for immediate human attention. GDPR-safe — does not
        # include the customer's email address.
        await alert_email_failure(
            tier=tier,
            registration=registration,
            report_ref=report_ref,
            session_id=session_id,
            reason="send_report_email returned False — see preceding log line",
        )
        track_event(
            event=EVENT_EMAIL_FAILED,
            registration=registration,
            properties={"tier": tier, "report_ref": report_ref},
        )

    return FulfilmentResult(
        registration=registration,
        report_ref=report_ref,
        email_sent=email_sent,
        verdict=None,
        payment_status="paid",
        check_data=check_data,
    )


async def _run_ev_pipeline(registration: str, tier: str) -> dict:
    """Run EV orchestrator and return the check data dict."""
    orch_tier = "ev_complete" if tier == "ev_complete" else "ev_health"
    orchestrator = EVOrchestrator()
    try:
        result = await orchestrator.run_ev_check(registration, tier=orch_tier)
        return result.model_dump()
    finally:
        await orchestrator.close()


async def _run_car_pipeline(registration: str, tier: str) -> dict:
    """Run car check orchestrator and return the check data dict."""
    orchestrator = CheckOrchestrator()
    try:
        result = await orchestrator.run_free_check(registration, tier=tier)
        return result.model_dump()
    finally:
        await orchestrator.close()


async def fulfil_report_idempotent(session_id: str) -> FulfilmentResult:
    """Fulfil a report, or return the cached result if already done.

    Safe for both webhook-triggered and frontend-triggered calls. Uses a Redis
    result cache (24h) + a short-lived lock so concurrent callers don't
    double-run the check or send duplicate emails.
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


_PROCESSED_EVENT_PREFIX = "stripe_event"
_PROCESSED_EVENT_TTL_SECONDS = 7 * 86400  # 7 days — matches Stripe's retry horizon


async def handle_webhook(event: dict) -> dict:
    """Shared webhook handler for all Stripe events.

    Handles five event types beyond plain checkout completion. Each path
    is idempotent via Redis-backed event_id deduplication so Stripe
    retries (which they do aggressively on any non-2xx) don't cause
    duplicate fulfilment, double-pinging Discord, etc.

    Always returns 200 quickly — heavy work (fulfilment, alerts) is
    fired in background tasks so Stripe never times out waiting for us.
    """
    event_id = event.get("id", "unknown")
    event_type = event.get("type", "unknown")

    # Idempotency guard. set_nx returns True only on first sight of this
    # event ID — Stripe retries land on second/Nth sight and short-circuit.
    is_first_sight = await cache.set_nx(
        _PROCESSED_EVENT_PREFIX, event_id, "1", ttl=_PROCESSED_EVENT_TTL_SECONDS
    )
    if not is_first_sight:
        logger.info(f"Webhook duplicate ignored: {event_type} {event_id}")
        return {"received": True, "duplicate": True}

    obj = event.get("data", {}).get("object", {}) or {}
    metadata = obj.get("metadata", {}) or {}

    if event_type == "checkout.session.completed":
        session_id = obj.get("id")
        tier = metadata.get("tier", "unknown")
        reg = metadata.get("registration", "unknown")
        logger.info(
            f"Webhook: checkout.session.completed for {reg} "
            f"(tier: {tier}, session: {session_id}, event: {event_id})"
        )
        if metadata.get("source"):
            logger.info(
                f"SEO-sourced paid conversion: source={metadata.get('source')} "
                f"slug={metadata.get('source_slug')} tier={metadata.get('tier')} "
                f"reg={metadata.get('registration')}"
            )
        if session_id:
            trigger_fulfilment_background(session_id)

    elif event_type == "payment_intent.payment_failed":
        # Card declined / authentication failed / insufficient funds.
        # Useful for spotting fraud + understanding lost revenue.
        amount_pence = obj.get("amount", 0) or 0
        currency = (obj.get("currency") or "gbp").upper()
        decline_code = (obj.get("last_payment_error") or {}).get("decline_code", "unknown")
        decline_reason = (obj.get("last_payment_error") or {}).get("message", "")
        logger.warning(
            f"Webhook: payment_intent.payment_failed amount={currency}{amount_pence/100:.2f} "
            f"reason={decline_code}: {decline_reason[:200]}"
        )
        from app.services.notification.discord import notify_discord
        asyncio.create_task(
            notify_discord(
                f"⚠️ **Payment declined** — {currency} {amount_pence/100:.2f}\n"
                f"Reason: `{decline_code}` · {decline_reason[:300] if decline_reason else 'no detail'}"
            )
        )

    elif event_type == "checkout.session.expired":
        # Customer abandoned checkout (24h timeout). Quiet — no Discord.
        # Tracked in PostHog only so we can analyse abandon rates later.
        tier = metadata.get("tier", "unknown")
        reg = metadata.get("registration", "unknown")
        logger.info(f"Webhook: checkout.session.expired for {reg} (tier: {tier})")
        from app.services.notification.analytics import track_event
        track_event(
            event="checkout_session_expired",
            registration=reg if reg != "unknown" else None,
            properties={"tier": tier},
        )

    elif event_type == "charge.refunded":
        amount_pence = obj.get("amount_refunded", 0) or 0
        currency = (obj.get("currency") or "gbp").upper()
        # Charge.metadata isn't always populated on refund events; fall back
        # to amount-only message.
        logger.info(
            f"Webhook: charge.refunded amount={currency}{amount_pence/100:.2f} (event: {event_id})"
        )
        from app.services.notification.discord import notify_discord
        asyncio.create_task(
            notify_discord(
                f"💸 **Refund issued** — {currency} {amount_pence/100:.2f}"
            )
        )

    elif event_type == "charge.dispute.created":
        # Chargeback. Very high priority — 7-day response window, £15 fee
        # per occurrence. Use @here so the alert is impossible to miss.
        amount_pence = obj.get("amount", 0) or 0
        currency = (obj.get("currency") or "gbp").upper()
        reason = obj.get("reason", "unknown")
        dispute_id = obj.get("id", "unknown")
        logger.error(
            f"Webhook: charge.dispute.created amount={currency}{amount_pence/100:.2f} "
            f"reason={reason} dispute={dispute_id}"
        )
        from app.services.notification.discord import notify_discord
        asyncio.create_task(
            notify_discord(
                f"@here 🚨 **Chargeback opened** — {currency} {amount_pence/100:.2f}\n"
                f"Reason: `{reason}` · Dispute ID: `{dispute_id}`\n"
                f"Respond within 7 days at https://dashboard.stripe.com/disputes/{dispute_id}"
            )
        )

    else:
        # Unhandled event type — log so we know about new Stripe events
        # we might want to act on later.
        logger.info(f"Webhook: unhandled event type {event_type} (event: {event_id})")

    return {"received": True}
