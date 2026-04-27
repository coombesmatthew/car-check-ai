"""Discord webhook notifier for critical ops alerts.

Strict GDPR posture — passes only operational pseudonyms (registration,
session_id, report_ref, tier) and NEVER customer emails, names, or other
direct PII. Lawful basis: legitimate interest (operational debugging +
financial sanity check). Discord operates under the EU-US Data Privacy
Framework so transfers are covered.

Fire-and-forget — never raises, never blocks the calling code.
"""
from __future__ import annotations

from typing import Optional

import httpx

from app.core.config import settings
from app.core.logging import logger

# Public message-builder helpers below produce content that is safe to send;
# all other code should go through these rather than calling notify_discord
# directly so the GDPR boundary is enforced in one place.

_TIMEOUT_SECONDS = 5.0


async def notify_discord(content: str) -> None:
    """Post `content` to the configured Discord webhook. Silent no-op if
    DISCORD_WEBHOOK_URL is unset (disables alerts entirely in dev). Errors
    are logged but never raised — alerting failure must not break the
    primary request."""
    if not settings.DISCORD_WEBHOOK_URL:
        return
    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT_SECONDS) as client:
            resp = await client.post(
                settings.DISCORD_WEBHOOK_URL,
                json={"content": content[:1900]},  # Discord 2000-char hard limit
            )
            if resp.status_code >= 400:
                logger.warning(
                    f"Discord webhook returned {resp.status_code}: {resp.text[:200]}"
                )
    except Exception as e:
        logger.warning(f"Discord webhook failed: {e}")


# --- Builders. Keep PII out of every output. ---


def _site() -> str:
    return settings.SITE_URL.rstrip("/")


async def alert_payment_received(
    *,
    tier: str,
    registration: str,
    report_ref: str,
    session_id: str,
) -> None:
    """Celebratory ping when a paid checkout completes successfully."""
    tier_label = {
        "premium": "Premium £9.99",
        "ev_health": "EV Health £8.99",
        "ev": "EV Health £8.99",
        "ev_complete": "EV Complete £13.99",
    }.get(tier, tier)
    msg = (
        f"💰 **New paid check** — {tier_label}\n"
        f"Reg: `{registration}` · Ref: `{report_ref}`\n"
        f"Report: {_site()}/report?session_id={session_id}"
    )
    await notify_discord(msg)


async def alert_email_failure(
    *,
    tier: str,
    registration: str,
    report_ref: str,
    session_id: str,
    reason: Optional[str] = None,
) -> None:
    """Loud alert when send_report_email returns False after a paid fulfilment."""
    msg = (
        f"🚨 **Email delivery failed** — {tier.upper()}\n"
        f"Reg: `{registration}` · Ref: `{report_ref}`\n"
        f"Reason: {reason or 'unknown — check Railway logs'}\n"
        f"Resend: `POST /api/v1/admin/resend-email?session_id={session_id}&token=…`"
    )
    await notify_discord(msg)
