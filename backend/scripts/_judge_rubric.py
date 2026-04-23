"""LLM-as-judge rubric for report style scoring.

Kept separate from eval_reports.py so the rubric can evolve without touching
the harness. Any future axes go here.
"""

from __future__ import annotations

from app.services.ai.style_guide import BANNED_PHRASES


AXES = [
    "tone_adherence",
    "structure_completeness",
    "findings_clarity",
    "no_verdict_language",
    "british_english",
    "no_inference_words",
    "length_appropriate",
]


JUDGE_SYSTEM_PROMPT = """You are a style auditor for Vericar buyer's reports.
You do not write reports — you score them against a rubric.
Return ONLY a JSON object matching the exact schema given. No prose, no markdown fences."""


def build_judge_user_prompt(report_markdown: str, tier_label: str, expected_word_range: tuple[int, int]) -> str:
    lo, hi = expected_word_range
    banned_list = ", ".join(f'"{p}"' for p in BANNED_PHRASES)
    return f"""Score this Vericar {tier_label} report on seven axes, 1-5 (5 = perfect).

--- REPORT BEGIN ---
{report_markdown}
--- REPORT END ---

Rubric (all axes 1-5, integer):

1. **tone_adherence**: Direct, specific, honest, no sales spin, no padding, active voice.
2. **structure_completeness**: Report opens with a "Key Findings" section, then flows through body sections, and does not reorder or drop required sections.
3. **findings_clarity**: Key Findings section contains 3-5 factual bullets citing specific numbers/dates/categories from the data. Each bullet is ONE line.
4. **no_verdict_language**: CRITICAL — the report must NOT issue a verdict. Deduct heavily if the text contains "BUY", "NEGOTIATE", "AVOID" (as judgements), "we recommend", "you should", "our verdict", or any prescriptive advice. 5 = zero verdict language; 1 = report opens with a BUY/AVOID stamp.
5. **british_english**: £ not $; UK spellings (colour, tyre, organisation); UK terminology (DVLA, DVSA, ULEZ); no US dates.
6. **no_inference_words**: ZERO occurrences of any banned phrase: {banned_list}. 5 if zero occurrences; subtract 1 per unique offender found (min 1).
7. **length_appropriate**: Word count falls within {lo}-{hi} words.

For each axis also give ONE short sentence of reasoning ("reason_*").

Return ONLY this JSON:
{{
  "tone_adherence": <int 1-5>,
  "reason_tone_adherence": "<one sentence>",
  "structure_completeness": <int 1-5>,
  "reason_structure_completeness": "<one sentence>",
  "findings_clarity": <int 1-5>,
  "reason_findings_clarity": "<one sentence>",
  "no_verdict_language": <int 1-5>,
  "reason_no_verdict_language": "<one sentence>",
  "british_english": <int 1-5>,
  "reason_british_english": "<one sentence>",
  "no_inference_words": <int 1-5>,
  "reason_no_inference_words": "<one sentence>",
  "length_appropriate": <int 1-5>,
  "reason_length_appropriate": "<one sentence>",
  "word_count": <int>,
  "overall_fail_if_any_axis_below_4": <true|false>
}}"""
