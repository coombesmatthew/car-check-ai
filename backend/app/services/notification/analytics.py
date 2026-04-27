"""PostHog server-side event tracking.

Mirrors the frontend `track()` helper at frontend/src/lib/analytics.ts so
both surfaces feed the same project. Server events let us count things the
client can't see (payment confirmations from Stripe webhooks, fulfilment
outcomes, OneAuto cost spend) without trusting client telemetry.

GDPR posture:
  - Plate registrations are PII. Never sent raw — always hashed with a
    server-side pepper into a stable distinct_id.
  - Email addresses, names, IPs, payment details: never sent.
  - Lawful basis: legitimate interest (product analytics + fraud
    prevention). PostHog operates EU-hosted (POSTHOG_HOST default
    eu.i.posthog.com) so transfers stay in-region.
  - The hash is one-way: PostHog cannot recover the original plate even
    if compromised.

Fire-and-forget. Never raises, never blocks the calling code. Events are
batched + async-flushed by the PostHog SDK.
"""
from __future__ import annotations

import hashlib
from typing import Any, Dict, Optional

from app.core.config import settings
from app.core.logging import logger

_posthog_client = None


def _get_client():
    """Lazy-init PostHog client. Returns None if not configured (dev / opt-out)."""
    global _posthog_client
    if not settings.POSTHOG_API_KEY:
        return None
    if _posthog_client is None:
        try:
            from posthog import Posthog

            _posthog_client = Posthog(
                project_api_key=settings.POSTHOG_API_KEY,
                host=settings.POSTHOG_HOST,
                # Don't sync-flush — we never want analytics latency in our
                # request path. SDK batches and flushes on a worker thread.
                sync_mode=False,
            )
        except Exception as e:
            logger.warning(f"PostHog SDK init failed: {e}")
            return None
    return _posthog_client


def hash_registration(reg: Optional[str]) -> str:
    """Stable pseudonymous identifier for a UK registration plate.

    Same plate always hashes to the same distinct_id so a customer's events
    cluster correctly in PostHog without ever exposing the raw plate. Pepper
    is in env so the hash space is project-specific.
    """
    if not reg:
        return "anonymous"
    normalised = reg.upper().replace(" ", "")
    digest = hashlib.sha256(
        f"{settings.POSTHOG_REG_HASH_PEPPER}:{normalised}".encode("utf-8")
    ).hexdigest()
    return f"reg_{digest[:16]}"


def track_event(
    *,
    event: str,
    distinct_id: Optional[str] = None,
    registration: Optional[str] = None,
    properties: Optional[Dict[str, Any]] = None,
) -> None:
    """Send one event to PostHog. Pass either distinct_id explicitly OR a
    registration to be hashed. PII inside `properties` is the caller's
    responsibility — keep emails/names/IPs out.
    """
    client = _get_client()
    if not client:
        return

    if not distinct_id:
        distinct_id = hash_registration(registration)

    try:
        client.capture(
            distinct_id=distinct_id,
            event=event,
            properties={**(properties or {}), "source": "backend"},
        )
    except Exception as e:
        logger.warning(f"PostHog capture failed for event {event}: {e}")


# --- Event constants — keep in sync with frontend lib/analytics.ts ---

EVENT_PAYMENT_RECEIVED = "payment_received"
EVENT_FULFILMENT_COMPLETED = "fulfilment_completed"
EVENT_EMAIL_SENT = "email_sent"
EVENT_EMAIL_FAILED = "email_failed"
EVENT_ADMIN_RESEND_EMAIL = "admin_resend_email"
