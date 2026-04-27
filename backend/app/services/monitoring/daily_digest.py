"""Daily Discord digest — one summary message per day at ~09:00 BST.

Pulls three signals for the previous calendar day (UTC):
  1. Paid checks + revenue (Stripe Checkout Session API)
  2. Free check volume delta (Redis counter snapshot day-over-day)
  3. OneAuto API health (api_calls table)

Posts a single Discord message with the rollup. Designed to be triggered
once per day by an external cron hitting POST /admin/run-daily-digest.

Why a snapshot for free-check delta: the cache counters are cumulative.
Each digest run snapshots today's value under
`digest_snapshot:checks_total:YYYY-MM-DD` so tomorrow's run can compute
yesterday's net delta. Day 1 has no baseline so shows the cumulative;
Day 2+ shows clean daily numbers.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import func, select

from app.core.cache import cache
from app.core.config import settings
from app.core.db import get_session
from app.core.logging import logger
from app.models.api_call import ApiCall
from app.services.notification.discord import notify_discord

# Snapshot prefix lets us compute day-over-day deltas on cumulative
# counters without adding any new instrumentation in the hot path.
_SNAPSHOT_PREFIX = "digest_snapshot"
_SNAPSHOT_TTL_SECONDS = 30 * 86400  # keep 30 days of history

# Stripe Checkout Session pricing — same values used by Discord alerts
# elsewhere. Keep in sync with stripe_service.TIER_CONFIG if prices change.
_TIER_LABELS = {
    "premium": "Premium",
    "ev": "EV Health",
    "ev_health": "EV Health",
    "ev_complete": "EV Complete",
    "basic": "Basic",
}


@dataclass
class DigestReport:
    """All numbers needed to render the daily Discord message."""

    period_start_utc: str = ""
    period_end_utc: str = ""

    # Paid (from Stripe)
    paid_count: int = 0
    paid_revenue_pence: int = 0
    paid_by_tier: dict[str, dict[str, int]] = field(default_factory=dict)
    test_paid_count: int = 0  # 100%-off promo sessions (TESTABC123 etc.)

    # Free volume delta (from Redis snapshot)
    free_checks_total_today: int = 0
    free_checks_delta: int | None = None  # None on first run (no baseline)
    ev_checks_total_today: int = 0
    ev_checks_delta: int | None = None

    # OneAuto health (from api_calls)
    oneauto_total_calls: int = 0
    oneauto_error_count: int = 0
    oneauto_endpoints_with_errors: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "period_start_utc": self.period_start_utc,
            "period_end_utc": self.period_end_utc,
            "paid_count": self.paid_count,
            "paid_revenue_pence": self.paid_revenue_pence,
            "paid_revenue_gbp": round(self.paid_revenue_pence / 100, 2),
            "paid_by_tier": self.paid_by_tier,
            "test_paid_count": self.test_paid_count,
            "free_checks_total_today": self.free_checks_total_today,
            "free_checks_delta": self.free_checks_delta,
            "ev_checks_total_today": self.ev_checks_total_today,
            "ev_checks_delta": self.ev_checks_delta,
            "oneauto_total_calls": self.oneauto_total_calls,
            "oneauto_error_count": self.oneauto_error_count,
            "oneauto_endpoints_with_errors": self.oneauto_endpoints_with_errors,
        }


def _yesterday_window_utc() -> tuple[datetime, datetime]:
    """Return [start_of_yesterday_utc, start_of_today_utc).

    Uses calendar days in UTC. The cron fires at 08:00 UTC (≈ 09:00 BST)
    so by then yesterday is fully closed.
    """
    today_utc = datetime.now(timezone.utc).replace(
        hour=0, minute=0, second=0, microsecond=0, tzinfo=None
    )
    yesterday_utc = today_utc - timedelta(days=1)
    return yesterday_utc, today_utc


async def _fetch_paid_metrics(
    period_start: datetime, period_end: datetime
) -> tuple[int, int, dict[str, dict[str, int]], int]:
    """Iterate paid Stripe checkout sessions and roll up by tier.

    Returns:
      (paid_count, paid_revenue_pence, by_tier_dict, test_count)
      by_tier_dict[tier] = {"count": N, "revenue_pence": M}
      test_count = sessions where amount_total == 0 (100%-off promo)
    """
    if not settings.STRIPE_SECRET_KEY:
        return 0, 0, {}, 0

    import stripe as stripe_lib

    from app.services.payment.stripe_service import _init_stripe

    _init_stripe()

    paid_count = 0
    paid_revenue_pence = 0
    test_count = 0
    by_tier: dict[str, dict[str, int]] = {}

    try:
        sessions = stripe_lib.checkout.Session.list(
            created={
                "gte": int(period_start.replace(tzinfo=timezone.utc).timestamp()),
                "lt": int(period_end.replace(tzinfo=timezone.utc).timestamp()),
            },
            limit=100,
            status="complete",
        )
        for s in sessions.auto_paging_iter():
            if s.payment_status != "paid":
                continue
            amount = s.amount_total or 0
            if amount == 0:
                test_count += 1
                continue
            paid_count += 1
            paid_revenue_pence += amount
            tier = (s.metadata or {}).get("tier") or "unknown"
            bucket = by_tier.setdefault(tier, {"count": 0, "revenue_pence": 0})
            bucket["count"] += 1
            bucket["revenue_pence"] += amount
    except Exception as e:
        logger.error(f"Daily digest: Stripe paid metrics fetch failed: {e}")

    return paid_count, paid_revenue_pence, by_tier, test_count


async def _fetch_free_check_deltas(period_start: datetime) -> tuple[int, int | None, int, int | None]:
    """Read today's cumulative counters and compare against yesterday's snapshot.

    Returns: (checks_total_now, checks_delta_or_none, ev_total_now, ev_delta_or_none)

    The delta is None on the first run because no baseline snapshot exists
    yet. Each invocation also stores today's snapshot for tomorrow's delta.
    """
    checks_now = await cache.get_counter("checks_total")
    ev_now = await cache.get_counter("ev_checks_total")

    yday_key = period_start.strftime("%Y-%m-%d")  # snapshot taken at start of yesterday
    today_key = (period_start + timedelta(days=1)).strftime("%Y-%m-%d")

    snap_yesterday = await cache.get(_SNAPSHOT_PREFIX, f"checks_total:{yday_key}")
    snap_yday_ev = await cache.get(_SNAPSHOT_PREFIX, f"ev_checks_total:{yday_key}")

    checks_delta: int | None = None
    ev_delta: int | None = None
    if snap_yesterday and isinstance(snap_yesterday, dict) and "value" in snap_yesterday:
        checks_delta = max(checks_now - int(snap_yesterday["value"]), 0)
    if snap_yday_ev and isinstance(snap_yday_ev, dict) and "value" in snap_yday_ev:
        ev_delta = max(ev_now - int(snap_yday_ev["value"]), 0)

    # Persist today's snapshot for tomorrow's run.
    await cache.set(
        _SNAPSHOT_PREFIX,
        f"checks_total:{today_key}",
        {"value": checks_now, "captured_at": datetime.utcnow().isoformat()},
        ttl=_SNAPSHOT_TTL_SECONDS,
    )
    await cache.set(
        _SNAPSHOT_PREFIX,
        f"ev_checks_total:{today_key}",
        {"value": ev_now, "captured_at": datetime.utcnow().isoformat()},
        ttl=_SNAPSHOT_TTL_SECONDS,
    )

    return checks_now, checks_delta, ev_now, ev_delta


async def _fetch_oneauto_health(
    period_start: datetime, period_end: datetime
) -> tuple[int, int, list[dict[str, Any]]]:
    """Roll up OneAuto api_calls for the window. Lists endpoints with any errors."""
    total = 0
    errors = 0
    endpoints_with_errors: list[dict[str, Any]] = []

    async with get_session() as session:
        stmt = (
            select(
                ApiCall.endpoint,
                func.count().label("total"),
                func.count().filter(ApiCall.status_code >= 400).label("errors"),
            )
            .where(ApiCall.created_at >= period_start)
            .where(ApiCall.created_at < period_end)
            .where(ApiCall.service == "oneauto")
            .group_by(ApiCall.endpoint)
        )
        result = await session.execute(stmt)
        for row in result:
            row_total = int(row.total or 0)
            row_errors = int(row.errors or 0)
            total += row_total
            errors += row_errors
            if row_errors > 0:
                endpoints_with_errors.append(
                    {
                        "endpoint": row.endpoint,
                        "total": row_total,
                        "errors": row_errors,
                        "error_rate_pct": round((row_errors / row_total) * 100, 1)
                        if row_total
                        else 0.0,
                    }
                )

    return total, errors, endpoints_with_errors


def _format_for_discord(report: DigestReport) -> str:
    """Build the Discord message. Concise — fits in one chat-screen view."""
    date_label = report.period_start_utc[:10]  # YYYY-MM-DD
    lines = [f"📊 **VeriCar daily digest — {date_label}**"]

    # --- Revenue & paid ---
    lines.append("")
    revenue_gbp = round(report.paid_revenue_pence / 100, 2)
    if report.paid_count > 0:
        lines.append(f"💰 **Paid:** {report.paid_count} checks · £{revenue_gbp:.2f}")
        for tier, b in sorted(
            report.paid_by_tier.items(), key=lambda x: x[1]["revenue_pence"], reverse=True
        ):
            label = _TIER_LABELS.get(tier, tier)
            tier_rev = round(b["revenue_pence"] / 100, 2)
            lines.append(f"  └ {b['count']}× {label} (£{tier_rev:.2f})")
    else:
        lines.append("💰 **Paid:** 0 checks")
    if report.test_paid_count > 0:
        lines.append(f"  _(plus {report.test_paid_count} internal test session(s))_")

    # --- Free volume ---
    lines.append("")
    if report.free_checks_delta is not None:
        ev_delta_label = (
            f" ({report.ev_checks_delta} EV)" if report.ev_checks_delta else ""
        )
        lines.append(f"🔍 **Free searches:** {report.free_checks_delta}{ev_delta_label}")
    else:
        lines.append(
            f"🔍 **Free searches today (cumulative):** {report.free_checks_total_today} "
            f"(EV: {report.ev_checks_total_today}) — _delta available from tomorrow_"
        )

    # --- API health ---
    lines.append("")
    if report.oneauto_total_calls == 0:
        lines.append("🛰️ **OneAuto:** no calls (no paid traffic)")
    else:
        err_pct = round((report.oneauto_error_count / report.oneauto_total_calls) * 100, 1)
        emoji = "✅" if report.oneauto_error_count == 0 else "⚠️"
        lines.append(
            f"🛰️ **OneAuto:** {report.oneauto_total_calls} calls · "
            f"{emoji} {report.oneauto_error_count} errors ({err_pct}%)"
        )
        for ep in sorted(
            report.oneauto_endpoints_with_errors,
            key=lambda x: x["error_rate_pct"],
            reverse=True,
        )[:5]:
            lines.append(
                f"  └ `{ep['endpoint']}` — {ep['errors']}/{ep['total']} ({ep['error_rate_pct']}%)"
            )

    return "\n".join(lines)


async def run_daily_digest(notify: bool = True) -> DigestReport:
    """Build and (optionally) post the daily digest. Top-level entrypoint."""
    period_start, period_end = _yesterday_window_utc()
    report = DigestReport(
        period_start_utc=period_start.isoformat() + "Z",
        period_end_utc=period_end.isoformat() + "Z",
    )

    paid_count, paid_revenue, by_tier, test_count = await _fetch_paid_metrics(
        period_start, period_end
    )
    report.paid_count = paid_count
    report.paid_revenue_pence = paid_revenue
    report.paid_by_tier = by_tier
    report.test_paid_count = test_count

    (
        checks_now,
        checks_delta,
        ev_now,
        ev_delta,
    ) = await _fetch_free_check_deltas(period_start)
    report.free_checks_total_today = checks_now
    report.free_checks_delta = checks_delta
    report.ev_checks_total_today = ev_now
    report.ev_checks_delta = ev_delta

    total, errors, endpoints = await _fetch_oneauto_health(period_start, period_end)
    report.oneauto_total_calls = total
    report.oneauto_error_count = errors
    report.oneauto_endpoints_with_errors = endpoints

    if notify:
        message = _format_for_discord(report)
        await notify_discord(message)

    return report
