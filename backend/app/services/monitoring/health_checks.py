# pyright: reportMissingImports=false
"""Operational health checks — sandbox heartbeats + passive live-traffic analysis.

Designed to be triggered hourly by an external cron (GitHub Actions or
cron-job.org) hitting the /admin/run-health-check endpoint. Returns a
structured report and pings Discord if anything is unhealthy. Zero cost
because:
  - Sandbox calls don't bill (free for monitoring)
  - Live-traffic analysis reads the existing api_calls table, no new
    paid calls made

If you ever migrate to true synthetic monitoring on the live API, just
point SANDBOX_BASE_URL at the live URL — the code is identical.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from typing import Any

import httpx
from sqlalchemy import func, select

from app.core.cache import cache
from app.core.config import settings
from app.core.db import get_session
from app.core.logging import logger
from app.models.api_call import ApiCall
from app.services.notification.discord import notify_discord

SANDBOX_BASE_URL = "https://sandbox.oneautoapi.com"

# Stable test VRM with mileage that's accepted by all sandbox endpoints.
# OneAuto's sandbox returns canned data for any VRM but still validates
# auth and routing — that's what we want for a heartbeat.
TEST_VRM = "AB12CDE"
TEST_MILEAGE = 30000

# OneAuto endpoints we depend on in production. Each is hit in sandbox during
# the heartbeat. Order matches our paid pipeline.
# (Dropped /oneauto/dvlaregionfromvrm/v2 — it isn't called anywhere outside
#  this file, so monitoring it adds noise without protecting any user-facing flow.)
SANDBOX_ENDPOINTS: list[dict[str, Any]] = [
    {
        "name": "ClearWatt — Used EV Range",
        "path": "/clearwatt/expectedrangefromvrm/",
        "params": {
            "vehicle_registration_mark": TEST_VRM,
            "current_mileage": TEST_MILEAGE,
        },
    },
    {
        "name": "EVDB — ID from VRM",
        "path": "/evdatabase/uk/searchfromvrm/",
        "params": {"vehicle_registration_mark": TEST_VRM},
    },
    {
        "name": "Experian AutoCheck v3",
        "path": "/experian/autocheck/v3",
        "params": {"vehicle_registration_mark": TEST_VRM},
    },
    {
        "name": "Brego valuation",
        "path": "/brego/currentandfuturevaluationsfromvrm/v2",
        # Brego requires forecast_date + miles_per_annum (production sends both —
        # see oneauto_client.get_valuation). forecast_date is today, computed at
        # call-time so it stays correct in long-running processes.
        "params": lambda: {
            "vehicle_registration_mark": TEST_VRM,
            "current_mileage": TEST_MILEAGE,
            "forecast_date": date.today().isoformat(),
            "miles_per_annum": 12000,
        },
    },
    {
        "name": "CarGuide salvage",
        "path": "/carguide/salvagecheck/v2",
        "params": {"vehicle_registration_mark": TEST_VRM},
    },
    {
        "name": "AutoPredict — predict",
        "path": "/autopredict/predict/v2",
        "params": {"vehicle_registration_mark": TEST_VRM},
    },
    {
        "name": "AutoPredict — statistics",
        "path": "/autopredict/statistics/v2",
        "params": {"vehicle_registration_mark": TEST_VRM},
    },
]

# Live-traffic analysis thresholds
LIVE_ERROR_RATE_THRESHOLD = 0.30  # >30% error rate over the window → alert
LIVE_WINDOW_MINUTES = 60
LIVE_MIN_SAMPLES = 3  # don't alert on a single failed call


@dataclass
class EndpointResult:
    name: str
    path: str
    healthy: bool
    status_code: int | None = None
    error: str | None = None


@dataclass
class HealthReport:
    sandbox_results: list[EndpointResult] = field(default_factory=list)
    live_traffic_alerts: list[dict[str, Any]] = field(default_factory=list)
    timestamp: str = ""

    @property
    def healthy(self) -> bool:
        sandbox_ok = all(r.healthy for r in self.sandbox_results)
        live_ok = len(self.live_traffic_alerts) == 0
        return sandbox_ok and live_ok

    def to_dict(self) -> dict[str, Any]:
        return {
            "healthy": self.healthy,
            "timestamp": self.timestamp,
            "sandbox": [
                {
                    "name": r.name,
                    "path": r.path,
                    "healthy": r.healthy,
                    "status_code": r.status_code,
                    "error": r.error,
                }
                for r in self.sandbox_results
            ],
            "live_traffic_alerts": self.live_traffic_alerts,
        }


async def _ping_sandbox_endpoint(
    client: httpx.AsyncClient, ep: dict[str, Any]
) -> EndpointResult:
    """Hit one sandbox endpoint. 200 = healthy. Anything else = unhealthy."""
    raw_params = ep["params"]
    params = raw_params() if callable(raw_params) else raw_params
    try:
        resp = await client.get(
            f"{SANDBOX_BASE_URL}{ep['path']}",
            params=params,
            headers={"x-api-key": settings.ONEAUTO_API_KEY},
        )
        # Sandbox typically returns 200 even for canned data. Non-200 means
        # auth, routing, or upstream gateway is broken.
        return EndpointResult(
            name=ep["name"],
            path=ep["path"],
            healthy=resp.status_code == 200,
            status_code=resp.status_code,
            error=None if resp.status_code == 200 else resp.text[:200],
        )
    except Exception as e:
        return EndpointResult(
            name=ep["name"],
            path=ep["path"],
            healthy=False,
            error=str(e)[:200],
        )


async def check_sandbox_endpoints() -> list[EndpointResult]:
    """Hit each critical sandbox endpoint and return per-endpoint health."""
    if not settings.ONEAUTO_API_KEY:
        return [
            EndpointResult(
                name=ep["name"],
                path=ep["path"],
                healthy=False,
                error="ONEAUTO_API_KEY not configured",
            )
            for ep in SANDBOX_ENDPOINTS
        ]

    async with httpx.AsyncClient(timeout=15.0) as client:
        results = []
        for ep in SANDBOX_ENDPOINTS:
            result = await _ping_sandbox_endpoint(client, ep)
            results.append(result)
        return results


async def check_live_traffic_health() -> list[dict[str, Any]]:
    """Read api_calls table to spot live-traffic problems.

    Computes error rate per endpoint over the last LIVE_WINDOW_MINUTES.
    Alerts when:
      - At least LIVE_MIN_SAMPLES calls in the window, AND
      - error rate exceeds LIVE_ERROR_RATE_THRESHOLD

    "Error" means `error IS NOT NULL` on the api_calls row, which covers all
    three failure modes the OneAuto client records:
      - HTTP 4xx/5xx (status_code set, error set)
      - Timeout / network exception (status_code NULL, error set)
      - HTTP 200 with `success: false` body (status_code 200, error set)
    Filtering on status_code >= 400 alone would miss the last two — and the
    last is OneAuto's most common failure shape (rate / plan / no-data limits).

    Free signal — we only see what real customers triggered, no new paid calls.
    """
    # ApiCall.created_at is naive UTC (server_default=now()), so compare with naive UTC.
    cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(minutes=LIVE_WINDOW_MINUTES)
    alerts: list[dict[str, Any]] = []

    async with get_session() as session:
        stmt = (
            select(
                ApiCall.endpoint,
                func.count().label("total"),
                func.count().filter(ApiCall.error.is_not(None)).label("errors"),
            )
            .where(ApiCall.created_at >= cutoff)
            .where(ApiCall.service == "oneauto")
            .group_by(ApiCall.endpoint)
            .having(func.count() >= LIVE_MIN_SAMPLES)
        )
        result = await session.execute(stmt)
        for row in result:
            total = row.total
            errors = row.errors or 0
            if total == 0:
                continue
            rate = errors / total
            if rate >= LIVE_ERROR_RATE_THRESHOLD:
                alerts.append(
                    {
                        "endpoint": row.endpoint,
                        "window_minutes": LIVE_WINDOW_MINUTES,
                        "total_calls": total,
                        "error_count": errors,
                        "error_rate_pct": round(rate * 100, 1),
                    }
                )

    return alerts


async def check_dvla_ves() -> EndpointResult:
    """Hit DVLA VES with the test VRM. Powers the FREE tier's vehicle identity.

    DVLA returns 404 for unknown VRMs — that's still a healthy "API alive" signal,
    so we treat 200 OR 404 as healthy. 401/403/5xx mean we'd lose FREE-tier traffic.
    """
    name = "DVLA VES (FREE-tier identity)"
    path = settings.DVLA_VES_URL
    if not settings.DVLA_VES_API_KEY or settings.DVLA_VES_API_KEY.startswith("your_"):
        return EndpointResult(name=name, path=path, healthy=False, error="DVLA_VES_API_KEY not configured")
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(
                path,
                json={"registrationNumber": TEST_VRM},
                headers={"x-api-key": settings.DVLA_VES_API_KEY, "Content-Type": "application/json"},
            )
        ok = resp.status_code in (200, 404)
        return EndpointResult(
            name=name,
            path=path,
            healthy=ok,
            status_code=resp.status_code,
            error=None if ok else resp.text[:200],
        )
    except Exception as e:
        return EndpointResult(name=name, path=path, healthy=False, error=str(e)[:200])


async def check_mot_oauth() -> EndpointResult:
    """Hit DVSA MOT's OAuth token endpoint. Powers the FREE tier's MOT history.

    Just acquires a token — that proves credentials are alive. We don't make a
    history call to keep the heartbeat free of side effects (and history calls
    are tiny anyway, but logging them as part of monitoring would muddy the
    api_calls table).
    """
    name = "DVSA MOT OAuth (FREE-tier MOT history)"
    path = settings.MOT_TOKEN_URL
    if not settings.MOT_CLIENT_ID or not settings.MOT_CLIENT_SECRET:
        return EndpointResult(name=name, path=path, healthy=False, error="MOT OAuth credentials not configured")
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(
                path,
                data={
                    "grant_type": "client_credentials",
                    "client_id": settings.MOT_CLIENT_ID,
                    "client_secret": settings.MOT_CLIENT_SECRET,
                    "scope": settings.MOT_SCOPE_URL,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
        ok = resp.status_code == 200 and "access_token" in resp.text
        return EndpointResult(
            name=name,
            path=path,
            healthy=ok,
            status_code=resp.status_code,
            error=None if ok else resp.text[:200],
        )
    except Exception as e:
        return EndpointResult(name=name, path=path, healthy=False, error=str(e)[:200])


async def check_stripe() -> EndpointResult:
    """Validate the Stripe API key is alive via Account.retrieve.

    Free, doesn't create or modify anything. Catches revoked / mistyped keys
    before a customer hits checkout and gets a 500.
    """
    import asyncio

    import stripe

    name = "Stripe (payment API key)"
    path = "stripe.Account.retrieve"
    if not settings.STRIPE_SECRET_KEY or settings.STRIPE_SECRET_KEY.startswith("your_"):
        return EndpointResult(name=name, path=path, healthy=False, error="STRIPE_SECRET_KEY not configured")
    try:
        stripe.api_key = settings.STRIPE_SECRET_KEY
        await asyncio.to_thread(stripe.Account.retrieve)
        return EndpointResult(name=name, path=path, healthy=True, status_code=200)
    except Exception as e:
        return EndpointResult(name=name, path=path, healthy=False, error=str(e)[:200])


async def run_health_check(notify_on_failure: bool = True) -> HealthReport:
    """Top-level: run sandbox + live-traffic checks, ping Discord on failure."""
    report = HealthReport(timestamp=datetime.now(timezone.utc).isoformat())
    report.sandbox_results = await check_sandbox_endpoints()
    report.sandbox_results.append(await check_dvla_ves())
    report.sandbox_results.append(await check_mot_oauth())
    report.sandbox_results.append(await check_stripe())
    report.live_traffic_alerts = await check_live_traffic_health()

    if notify_on_failure and not report.healthy:
        await _notify_discord(report)
    elif report.healthy:
        logger.info("Health check passed: all sandbox endpoints + live traffic OK")

    return report


# If the same failure persists, suppress identical alerts for this long.
# 12h = ping at 09:00, suppress, ping again at 21:00 if still broken — enough
# to stay aware without spamming the digest channel every cron tick.
_ALERT_DEDUPE_TTL_SECONDS = 12 * 3600


def _alert_fingerprint(report: HealthReport) -> str:
    """Stable hash of the failure shape so repeat alerts can be deduped.

    Hashes (path, status_code) for failed sandbox endpoints + endpoint name for
    live-traffic alerts. Excludes timestamps and free-text error bodies so a
    persistent failure produces the same fingerprint every cron tick.
    """
    parts: list[str] = []
    for r in sorted(report.sandbox_results, key=lambda x: x.path):
        if not r.healthy:
            parts.append(f"sandbox:{r.path}:{r.status_code}")
    for a in sorted(report.live_traffic_alerts, key=lambda x: x["endpoint"]):
        parts.append(f"live:{a['endpoint']}")
    return hashlib.sha256("|".join(parts).encode()).hexdigest()[:16]


async def _notify_discord(report: HealthReport) -> None:
    """Build and post a Discord alert summarising what's broken.

    Deduplicates: identical failure shapes within the TTL window are silent.
    The first transition into a failure state always pings; persistent failures
    re-ping once the TTL expires.
    """
    fingerprint = _alert_fingerprint(report)
    is_first = await cache.set_nx(
        "health_alert", fingerprint, "1", ttl=_ALERT_DEDUPE_TTL_SECONDS
    )
    if not is_first:
        logger.info(
            f"Health check still failing (fingerprint={fingerprint}); "
            "Discord alert suppressed by dedupe"
        )
        return

    lines = ["🚨 **Health check failed** — see below"]

    failed_sandbox = [r for r in report.sandbox_results if not r.healthy]
    if failed_sandbox:
        lines.append("")
        lines.append("**Sandbox endpoints unhealthy:**")
        for r in failed_sandbox:
            status = f"HTTP {r.status_code}" if r.status_code else "request failed"
            lines.append(f"• `{r.path}` — {status}")
            if r.error:
                lines.append(f"  └ {r.error[:150]}")

    if report.live_traffic_alerts:
        lines.append("")
        lines.append(
            f"**Live traffic error spikes (last {LIVE_WINDOW_MINUTES} min):**"
        )
        for a in report.live_traffic_alerts:
            lines.append(
                f"• `{a['endpoint']}` — {a['error_count']}/{a['total_calls']} "
                f"calls failed ({a['error_rate_pct']}%)"
            )

    await notify_discord("\n".join(lines))
