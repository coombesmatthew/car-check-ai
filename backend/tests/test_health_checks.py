# ruff: noqa: S101
# pyright: reportMissingImports=false
"""Unit tests for the operational health-check module."""
from __future__ import annotations

from datetime import date
from typing import Any, cast
from unittest.mock import AsyncMock, patch

import pytest

from app.services.monitoring.health_checks import (
    SANDBOX_ENDPOINTS,
    EndpointResult,
    HealthReport,
    _alert_fingerprint,
    _notify_discord,
)


def _brego_endpoint() -> dict[str, Any]:
    return next(ep for ep in SANDBOX_ENDPOINTS if "brego" in ep["path"])


def test_brego_sandbox_params_include_all_required_fields():
    """Regression: Brego rejects requests missing forecast_date / miles_per_annum."""
    ep = _brego_endpoint()
    raw = ep["params"]
    resolved = raw() if callable(raw) else raw
    params = cast(dict[str, Any], resolved)

    assert params["vehicle_registration_mark"]
    assert params["current_mileage"]
    assert params["forecast_date"] == date.today().isoformat()
    assert params["miles_per_annum"] >= 1


def test_alert_fingerprint_is_stable_for_identical_failure_shape():
    failed = EndpointResult(
        name="x", path="/foo", healthy=False, status_code=500
    )
    healthy = EndpointResult(
        name="y", path="/bar", healthy=True, status_code=200
    )
    r1 = HealthReport(sandbox_results=[failed, healthy])
    r2 = HealthReport(sandbox_results=[healthy, failed])  # different order

    assert _alert_fingerprint(r1) == _alert_fingerprint(r2)


def test_alert_fingerprint_changes_when_status_code_changes():
    r1 = HealthReport(
        sandbox_results=[
            EndpointResult(name="x", path="/foo", healthy=False, status_code=500),
        ]
    )
    r2 = HealthReport(
        sandbox_results=[
            EndpointResult(name="x", path="/foo", healthy=False, status_code=400),
        ]
    )
    assert _alert_fingerprint(r1) != _alert_fingerprint(r2)


def test_alert_fingerprint_ignores_free_text_error_body():
    """Different upstream error messages for the same status shouldn't bust dedupe."""
    r1 = HealthReport(
        sandbox_results=[
            EndpointResult(
                name="x", path="/foo", healthy=False, status_code=400, error="msg one"
            ),
        ]
    )
    r2 = HealthReport(
        sandbox_results=[
            EndpointResult(
                name="x", path="/foo", healthy=False, status_code=400, error="msg two"
            ),
        ]
    )
    assert _alert_fingerprint(r1) == _alert_fingerprint(r2)


@pytest.mark.asyncio
async def test_notify_discord_suppresses_repeat_alerts():
    """Same fingerprint within TTL → no Discord call."""
    report = HealthReport(
        sandbox_results=[
            EndpointResult(name="x", path="/foo", healthy=False, status_code=500),
        ]
    )
    with (
        patch(
            "app.services.monitoring.health_checks.cache.set_nx",
            new_callable=AsyncMock,
            return_value=False,  # already-set key → suppress
        ),
        patch(
            "app.services.monitoring.health_checks.notify_discord",
            new_callable=AsyncMock,
        ) as mock_notify,
    ):
        await _notify_discord(report)
        mock_notify.assert_not_called()


@pytest.mark.asyncio
async def test_notify_discord_posts_on_first_occurrence():
    report = HealthReport(
        sandbox_results=[
            EndpointResult(name="x", path="/foo", healthy=False, status_code=500),
        ]
    )
    with (
        patch(
            "app.services.monitoring.health_checks.cache.set_nx",
            new_callable=AsyncMock,
            return_value=True,  # newly set → first time
        ),
        patch(
            "app.services.monitoring.health_checks.notify_discord",
            new_callable=AsyncMock,
        ) as mock_notify,
    ):
        await _notify_discord(report)
        mock_notify.assert_called_once()
        body = mock_notify.call_args[0][0]
        assert "Health check failed" in body
        assert "/foo" in body
