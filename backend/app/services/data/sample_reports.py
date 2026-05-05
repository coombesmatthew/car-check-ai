"""Loader for static sample-report fixtures served at /api/v1/checks/sample.

Each variant file is a fully-formed ReportDataResponse payload (the same
shape /api/v1/checks/report/data returns for paid sessions). They are
loaded once at module import and a deep copy is returned per request so
callers cannot mutate the cached dict.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Literal

SampleVariant = Literal["clean", "risks", "ev"]

_FIXTURE_DIR = Path(__file__).parent / "sample_reports"
_FILE_BY_VARIANT: dict[str, str] = {
    "clean": "clean_mini.json",
    "risks": "risks_found.json",
    "ev": "ev_health.json",
}

_CACHE: dict[str, dict] = {}


def _load(variant: str) -> dict | None:
    if variant in _CACHE:
        return _CACHE[variant]
    filename = _FILE_BY_VARIANT.get(variant)
    if not filename:
        return None
    path = _FIXTURE_DIR / filename
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as f:
        _CACHE[variant] = json.load(f)
    return _CACHE[variant]


def get_sample_report(variant: str) -> dict | None:
    """Return a deep copy of the fixture for the given variant, or None."""
    data = _load(variant)
    if data is None:
        return None
    return copy.deepcopy(data)


def available_variants() -> list[str]:
    """Variants that currently have a fixture file on disk."""
    return [v for v in _FILE_BY_VARIANT if (_FIXTURE_DIR / _FILE_BY_VARIANT[v]).exists()]
