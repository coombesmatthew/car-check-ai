# Takes a ScrapedPage and calls Claude to synthesise a structured
# KnownIssuesRecord. Style rules are inlined in SYSTEM_PROMPT; extraction to a
# shared `style_guide` module is future work (no such module exists yet and
# creating one mid-prototype would ripple into other generators).
from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Optional

import anthropic
from pydantic import ValidationError

from app.core.config import settings
from app.core.logging import logger
from app.services.known_issues.models import (
    KnownIssuesRecord,
    ScrapedPage,
    SourceCitation,  # noqa: F401 — re-exported/available for callers
)

TEMPERATURE = 0.2
MAX_TOKENS = 2048

SYSTEM_PROMPT = """You are a UK used-car inspector writing for ordinary buyers. Plain, honest, British English.

TONE RULES (strict):
- No hype, no sensationalism, no clickbait framing.
- No accusatory words: do NOT say "scam", "dodgy", "clocked", "ripped off", "nightmare", "avoid at all costs".
- British English only. Use tyres (not tires), colour (not color), aluminium (not aluminum), kerb (not curb), bonnet (not hood), boot (not trunk), petrol (not gas/gasoline), gearbox (not transmission when you can say gearbox), clutch (not "stick"), number plate (not license plate), windscreen (not windshield).
- No US spellings anywhere (-our not -or, -re not -er where applicable, -ise not -ize).
- No motoring-magazine jargon or hype ("blistering", "punchy", "silky", "world-beating", "legendary").
- Describe problems plainly: "the diesel particulate filter can block", not "plagued by DPF hell".

TASK:
You will be given the raw "Good" and "Bad" bullet lists that HonestJohn publishes about one UK car model (and sometimes one generation of that model). Use those bullets as the primary factual input.

Your job is to produce 3 to 5 CONCRETE, SEO-SEARCHABLE "top issues" that a real used-car buyer might Google before viewing a car. Prefer specific titles over vague ones:

  GOOD title example: "DPF blockages on diesel variants"
  GOOD title example: "DSG gearbox mechatronics failures"
  GOOD title example: "Front lower suspension arm bush wear"
  BAD title example:  "Engine problems"        (too vague)
  BAD title example:  "Reliability concerns"   (not searchable)
  BAD title example:  "Various issues"         (meaningless)

For each issue:
- title: concrete, search-friendly phrase (see examples above).
- description: 2–3 sentences in plain British English explaining what goes wrong and why it matters to a buyer. No hype.
- typical_symptoms: short list of observable symptoms a buyer could spot on a test drive or pre-purchase inspection (e.g. "warning light on dashboard", "whistling noise under acceleration", "judder when pulling away").
- affected_years: a list of years ONLY IF the scraped text is specific about years; otherwise use null. Do not guess.
- estimated_repair_cost_gbp_range: [min_gbp, max_gbp] integers based on general UK independent-garage pricing (typical bands: brakes £150–£500, clutch £500–£1200, DPF £800–£2500, turbo £800–£2000, EGR valve £300–£800, DSG mechatronics £1500–£3000, suspension arms £200–£600, cambelt £400–£800, catalytic converter £400–£1500, alternator £250–£600, water pump £300–£700, dual-mass flywheel £800–£1500). If the issue is hard to price (e.g. a rattle, a minor trim fault) omit the field (null). Do not invent numbers for things you don't know.
- severity: "low" | "medium" | "high". Weight severity by (cost to fix) × (how common) × (safety impact). Brake-related issues skew high; cosmetic issues skew low.
- source_citations: ALWAYS include at least one entry citing the HonestJohn page you were given, using the page title and URL provided in the user message.

Also produce:
- overall_reliability_note: ONE factual sentence summarising the model's reputation. No hype. Example: "Generally a reliable small hatchback, but diesel variants require diligent DPF regeneration and the automatic gearbox can be costly to repair."
- top-level sources: a list containing at least the HonestJohn page used.

OUTPUT FORMAT:
Return JSON only. No markdown fences. No prose before or after the JSON. The JSON must match this schema exactly:

{
  "make": string,
  "model": string,
  "generation": string | null,
  "years": string,              // e.g. "2011-2018"
  "top_issues": [
    {
      "title": string,
      "description": string,
      "typical_symptoms": [string, ...],
      "affected_years": [int, ...] | null,
      "estimated_repair_cost_gbp_range": [int, int] | null,
      "severity": "low" | "medium" | "high",
      "source_citations": [{"title": string, "url": string}, ...]
    }
  ],
  "overall_reliability_note": string,
  "last_updated": string,        // ISO 8601 UTC, e.g. "2026-04-23T12:00:00+00:00"
  "sources": [{"title": string, "url": string}, ...]
}

British English throughout. JSON only."""


def _build_user_message(scraped: ScrapedPage) -> str:
    """Render the scraped page into a concise user message for Claude."""
    today = datetime.now(timezone.utc).date().isoformat()

    def _numbered(items: list[str]) -> str:
        if not items:
            return "(none scraped)"
        return "\n".join(f"{i}. {item}" for i, item in enumerate(items, start=1))

    return (
        f"Source URL: {scraped.url}\n"
        f"Source page title: {scraped.title}\n"
        f"Make: {scraped.make}\n"
        f"Model slug: {scraped.model_slug}\n\n"
        "GOOD points (verbatim from HonestJohn):\n"
        f"{_numbered(scraped.good_points)}\n\n"
        "BAD points (verbatim from HonestJohn):\n"
        f"{_numbered(scraped.bad_points)}\n\n"
        f"Today's date is {today}. Synthesise exactly 3–5 top_issues. "
        "Output JSON only, no markdown fences."
    )


def synthesise(scraped: ScrapedPage) -> Optional[KnownIssuesRecord]:
    """Call Claude to transform a ScrapedPage into a validated KnownIssuesRecord.

    Returns None on config, API, JSON or schema-validation failure (never raises).
    """
    if not settings.ANTHROPIC_API_KEY or settings.ANTHROPIC_API_KEY.startswith("your_"):
        logger.error("ANTHROPIC_API_KEY not configured; cannot synthesise")
        return None

    try:
        client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        message = client.messages.create(
            model=settings.ANTHROPIC_MODEL,
            max_tokens=MAX_TOKENS,
            temperature=TEMPERATURE,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": _build_user_message(scraped)}],
        )
        raw = message.content[0].text
        # Strip markdown fences if Claude wrapped the JSON despite the instruction.
        stripped = raw.strip()
        if stripped.startswith("```"):
            # Drop the opening fence line (```json or ```) and the closing fence.
            lines = stripped.splitlines()
            if lines and lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip().startswith("```"):
                lines = lines[:-1]
            stripped = "\n".join(lines).strip()
        data = json.loads(stripped)

        # Backfill last_updated if the model omitted it
        data.setdefault("last_updated", datetime.now(timezone.utc).isoformat())

        # Ensure top-level sources includes the scraped URL
        sources = data.get("sources") or []
        if not any(str(s.get("url", "")) == scraped.url for s in sources):
            sources.append({"title": scraped.title or scraped.url, "url": scraped.url})
        data["sources"] = sources

        record = KnownIssuesRecord(**data)
        logger.info(
            f"Synthesised {len(record.top_issues)} known issues for "
            f"{record.make} {record.model} {record.generation or ''}".strip()
        )
        return record

    except anthropic.APIError as e:
        logger.error(f"Anthropic API error during known-issues synthesis: {e}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"Claude returned non-JSON for known-issues synthesis: {e}")
        return None
    except ValidationError as e:
        logger.error(f"Claude output failed schema validation: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error during known-issues synthesis: {e}")
        return None
