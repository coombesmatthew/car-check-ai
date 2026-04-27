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

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any

import httpx
from sqlalchemy import func, select

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

# Endpoints we depend on in production. Each is hit in sandbox during
# the heartbeat. Order matches our paid pipeline.
SANDBOX_ENDPOINTS: list[dict[str, Any]] = [
    {
        "name": "DVLA region (cheapest live endpoint)",
        "path": "/oneauto/dvlaregionfromvrm/v2",
        "params": {"vehicle_registration_mark": TEST_VRM},
    },
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
        "params": {
            "vehicle_registration_mark": TEST_VRM,
            "current_mileage": TEST_MILEAGE,
        },
    },
    {
        "name": "CarGuide salvage",
        "path": "/carguide/salvagecheck/v2",
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
    try:
        resp = await client.get(
            f"{SANDBOX_BASE_URL}{ep['path']}",
            params=ep["params"],
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

    Free signal — we only see what real customers triggered, no new paid calls.
    """
    cutoff = datetime.utcnow() - timedelta(minutes=LIVE_WINDOW_MINUTES)
    alerts: list[dict[str, Any]] = []

    async with get_session() as session:
        stmt = (
            select(
                ApiCall.endpoint,
                func.count().label("total"),
                func.count().filter(ApiCall.status_code >= 400).label("errors"),
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


async def run_health_check(notify_on_failure: bool = True) -> HealthReport:
    """Top-level: run sandbox + live-traffic checks, ping Discord on failure."""
    report = HealthReport(timestamp=datetime.utcnow().isoformat())
    report.sandbox_results = await check_sandbox_endpoints()
    report.live_traffic_alerts = await check_live_traffic_health()

    if notify_on_failure and not report.healthy:
        await _notify_discord(report)
    elif report.healthy:
        logger.info("Health check passed: all sandbox endpoints + live traffic OK")

    return report


async def _notify_discord(report: HealthReport) -> None:
    """Build and post a Discord alert summarising what's broken."""
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
