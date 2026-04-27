from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from app.core.logging import logger
from app.services.known_issues.models import KnownIssuesRecord

# This file lives at backend/app/services/known_issues/repo.py
# parents[0] = known_issues, [1] = services, [2] = app, [3] = backend
DATA_DIR = Path(__file__).resolve().parents[3] / "data" / "known_issues"


def _record_path(make: str, model_slug: str) -> Path:
    """Compute the on-disk JSON path for a make/model-slug pair."""
    return DATA_DIR / f"{make.lower()}-{model_slug.lower()}.json"


def save_record(record: KnownIssuesRecord, model_slug: str) -> Path:
    """Persist a KnownIssuesRecord to disk as indented JSON.

    `model_slug` is passed explicitly because KnownIssuesRecord does not store
    the slug form (it stores `model`, which is a human-readable name).
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    path = _record_path(record.make, model_slug)
    path.write_text(record.model_dump_json(indent=2))
    logger.info(f"Saved known-issues record to {path}")
    return path


def load_record(make: str, model_slug: str) -> Optional[KnownIssuesRecord]:
    """Load a previously-saved record. Returns None if missing or invalid."""
    path = _record_path(make, model_slug)
    if not path.exists():
        return None
    try:
        return KnownIssuesRecord.model_validate_json(path.read_text())
    except (json.JSONDecodeError, ValueError) as e:
        logger.error(f"Failed to load known-issues record at {path}: {e}")
        return None
