# pyright: reportMissingImports=false
from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, HttpUrl


class SourceCitation(BaseModel):
    title: str
    url: HttpUrl


class KnownIssue(BaseModel):
    title: str
    description: str
    typical_symptoms: list[str] = Field(default_factory=list)
    affected_years: list[int] | None = None
    estimated_repair_cost_gbp_range: tuple[int, int] | None = None
    severity: Literal["low", "medium", "high"]
    source_citations: list[SourceCitation] = Field(default_factory=list)


class HeroImage(BaseModel):
    """Hero image sourced from Wikimedia / Wikipedia for SEO pages."""
    url: str
    width: int | None = None
    height: int | None = None
    source_page_url: str | None = None   # Wikipedia article URL
    artist: str | None = None            # stripped author name
    license_short: str | None = None     # e.g. "CC BY-SA 4.0"
    license_url: str | None = None


class KnownIssuesRecord(BaseModel):
    make: str
    model: str
    generation: str | None = None
    years: str
    top_issues: list[KnownIssue]
    overall_reliability_note: str
    last_updated: datetime
    sources: list[SourceCitation] = Field(default_factory=list)
    hero_image: HeroImage | None = None


class ScrapedPage(BaseModel):
    # Pydantic v2 reserves the `model_` prefix on BaseModel — disable protected
    # namespaces so `model_slug` doesn't emit a warning.
    model_config = {"protected_namespaces": ()}

    url: str
    make: str
    model_slug: str
    title: str
    good_points: list[str]
    bad_points: list[str]
    fetched_at: datetime
