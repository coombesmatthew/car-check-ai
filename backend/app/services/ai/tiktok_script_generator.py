"""TikTok/Reels script generator using Claude AI with demo fallback.

Legal compliance notes:
- Never accuse a seller of fraud or use the word "clocked" (defamation risk).
- Present MOT mileage data factually: "the records show X" not "this car IS clocked".
- Opinions (overpriced, poor condition) are defensible as honest opinion when the
  factual basis is shown alongside.
- All content must include OGL attribution for DVLA/DVSA data.
"""

import json
from typing import Optional

import anthropic

from app.core.config import settings
from app.core.logging import logger
from app.schemas.scraping import ContentScore, TikTokScript


# Content angles — legally safe names
ANGLES = [
    "mileage_discrepancy",  # was "clocking_expose" — present data, no accusations
    "bargain_hunter",
    "overpriced_alert",
    "high_mileage_hero",
    "mot_horror",
    "hidden_gem",
    "auto",
]

OGL_ATTRIBUTION = "MOT & vehicle data: Open Government Licence v3.0"

SYSTEM_PROMPT = """You are a viral TikTok/Reels content creator specialising in used cars in the UK.
You find interesting, overpriced, or surprisingly good car deals online and create short, punchy scripts.

Your style:
- Attention-grabbing hooks (first 3 seconds are everything)
- Direct, conversational British English
- Mix of curiosity and genuine buyer advice
- Always reference specific data (mileage figures, prices, MOT dates)
- End with a call to action

LEGAL RULES — you MUST follow these:
1. NEVER use the word "clocked", "scam", "scammer", "fraud", or "fraudster".
2. NEVER accuse a seller of dishonesty or criminal conduct.
3. When mileage has decreased between MOT tests, describe it factually:
   "The MOT records show mileage went from X to Y between [date] and [date]."
   Then say "This is a mileage discrepancy that warrants investigation" or similar.
   Let the viewer draw their own conclusions.
4. "Overpriced" and "poor condition" are opinions — always state the factual basis
   (comparable prices, MOT advisory count, condition score).
5. Include this attribution at the end of every script:
   "MOT & vehicle data under Open Government Licence v3.0"

Output ONLY valid JSON with these fields:
{
  "hook": "The opening line (must grab attention in 3 seconds)",
  "script": "Full script for 30-60 second video, including the hook. Use [PAUSE], [CUT TO], [ZOOM] for editing cues.",
  "hashtags": ["list", "of", "relevant", "hashtags"],
  "angle": "one of: mileage_discrepancy, bargain_hunter, overpriced_alert, high_mileage_hero, mot_horror, hidden_gem",
  "estimated_duration_seconds": 30
}"""


async def generate_tiktok_script(
    scored_listing: ContentScore,
    angle: str = "auto",
) -> TikTokScript:
    """Generate a TikTok script for a scored listing.

    Args:
        scored_listing: A ContentScore with listing data and check results.
        angle: Content angle to use, or "auto" to let AI decide.

    Returns:
        TikTokScript with hook, script body, hashtags, and angle.
    """
    if not settings.ANTHROPIC_API_KEY or settings.ANTHROPIC_API_KEY.startswith("your_"):
        logger.warning("Anthropic API key not configured — using demo TikTok script")
        return _generate_demo_script(scored_listing, angle)

    listing = scored_listing.listing
    user_message = _build_context(scored_listing, angle)

    try:
        client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

        message = client.messages.create(
            model=settings.ANTHROPIC_MODEL,
            max_tokens=512,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_message}],
        )

        raw = message.content[0].text
        logger.info(f"TikTok script generated for {listing.vrn} ({message.usage.input_tokens}+{message.usage.output_tokens} tokens)")

        # Parse the JSON response
        data = json.loads(raw)
        return TikTokScript(
            listing=listing,
            hook=data.get("hook", ""),
            script=data.get("script", ""),
            hashtags=data.get("hashtags", []),
            angle=data.get("angle", angle),
            estimated_duration_seconds=data.get("estimated_duration_seconds", 30),
        )

    except anthropic.APIError as e:
        logger.error(f"Anthropic API error generating TikTok script: {e}")
        return _generate_demo_script(scored_listing, angle)
    except (json.JSONDecodeError, KeyError) as e:
        logger.error(f"Failed to parse AI script response: {e}")
        return _generate_demo_script(scored_listing, angle)
    except Exception as e:
        logger.error(f"TikTok script generation failed: {e}")
        return _generate_demo_script(scored_listing, angle)


def _build_context(scored_listing: ContentScore, angle: str) -> str:
    """Build the user message context for Claude."""
    listing = scored_listing.listing
    parts = [f"Generate a TikTok script for this online car listing:"]

    parts.append(f"\nListing: {listing.title}")
    if listing.vrn:
        parts.append(f"Registration: {listing.vrn}")
    if listing.make:
        parts.append(f"Make: {listing.make}")
    if listing.model:
        parts.append(f"Model: {listing.model}")
    if listing.year:
        parts.append(f"Year: {listing.year}")
    if listing.price is not None:
        parts.append(f"Price: £{listing.price / 100:,.0f}")
    if listing.mileage is not None:
        parts.append(f"Listed Mileage: {listing.mileage:,} miles")

    parts.append(f"\nContent Score: {scored_listing.total_score}/100")

    if scored_listing.factors:
        parts.append("\nScoring Factors:")
        for f in scored_listing.factors:
            parts.append(f"  - {f.name}: +{f.points}pts — {f.detail}")

    check = scored_listing.check_result
    if check:
        condition = check.get("condition_score")
        if condition is not None:
            parts.append(f"\nMOT Condition Score: {condition}/100")

        clocking = check.get("clocking_analysis") or {}
        if clocking.get("flags"):
            parts.append("\nMileage discrepancies found in MOT history:")
            for flag in clocking.get("flags", []):
                parts.append(f"  - {flag.get('detail', '')}")
            parts.append("(Present these as factual observations, NOT accusations.)")

        patterns = check.get("failure_patterns", [])
        if patterns:
            parts.append("\nRecurring MOT Failures:")
            for p in patterns:
                parts.append(f"  - {p['category']}: {p['occurrences']}x ({p['concern_level']})")

    if angle != "auto":
        parts.append(f"\nUse the '{angle}' angle for this script.")
    else:
        parts.append("\nChoose the most compelling angle based on the data.")

    parts.append("\nRemember: factual language only. No accusations. Let the data speak.")

    return "\n".join(parts)


def _generate_demo_script(scored_listing: ContentScore, angle: str) -> TikTokScript:
    """Generate a template-based demo script when API key is unavailable."""
    listing = scored_listing.listing
    make = listing.make or "car"
    model = listing.model or ""
    price_str = f"£{listing.price / 100:,.0f}" if listing.price else "unknown price"
    mileage_str = f"{listing.mileage:,}" if listing.mileage else "unknown"
    year_str = str(listing.year) if listing.year else "unknown year"

    # Build mileage discrepancy detail from flags if available
    discrepancy_detail = ""
    check = scored_listing.check_result or {}
    clocking = check.get("clocking_analysis") or {}
    flags = clocking.get("flags", [])
    if flags:
        for flag in flags:
            if flag.get("type") == "mileage_drop":
                discrepancy_detail = flag.get("detail", "")
                break
        if not discrepancy_detail:
            discrepancy_detail = flags[0].get("detail", "")

    # Auto-detect best angle
    if angle == "auto":
        if flags:
            angle = "mileage_discrepancy"
        elif any(f.name == "price_anomaly" and f.points >= 20 for f in scored_listing.factors):
            if any("cheap" in f.detail.lower() for f in scored_listing.factors):
                angle = "bargain_hunter"
            else:
                angle = "overpriced_alert"
        elif any(f.name == "mileage_anomaly" and f.points >= 15 for f in scored_listing.factors):
            angle = "high_mileage_hero"
        elif any(f.name == "recurring_failures" for f in scored_listing.factors):
            angle = "mot_horror"
        else:
            angle = "hidden_gem"

    scripts = {
        "mileage_discrepancy": {
            "hook": f"This {make}'s MOT history doesn't add up. Look at the mileage.",
            "script": (
                f"This {make}'s MOT history doesn't add up. Look at the mileage.\n\n"
                f"[CUT TO listing] Listed as a {year_str} {make} {model} for {price_str} "
                f"with {mileage_str} miles.\n\n"
                f"[CUT TO data] But when we checked the MOT records, "
                f"{'the data shows: ' + discrepancy_detail + '.' if discrepancy_detail else 'the recorded mileage actually goes DOWN between tests.'}\n\n"
                f"[ZOOM on data] That's a significant mileage discrepancy. "
                f"There could be an innocent explanation — instrument cluster swap, "
                f"recording error — but it absolutely needs investigating before you buy.\n\n"
                f"[CUT TO camera] Always check the MOT history before buying a used car. "
                f"VeriCar does it for free. Link in bio.\n\n"
                f"[TEXT] {OGL_ATTRIBUTION}"
            ),
            "hashtags": [
                "#vericar", "#usedcars", "#mileagecheck", f"#{make.lower()}",
                "#cartok", "#usedcartips", "#buyerbeware", "#motcheck",
            ],
        },
        "bargain_hunter": {
            "hook": f"I found a {year_str} {make} for {price_str}. Is it too good to be true?",
            "script": (
                f"I found a {year_str} {make} for {price_str}. Is it too good to be true?\n\n"
                f"[CUT TO listing] {mileage_str} miles, looks decent in the photos.\n\n"
                f"[CUT TO check] So we ran the reg through VeriCar and here's what came back...\n\n"
                f"[PAUSE] The MOT history is actually clean. No mileage discrepancies, "
                f"no major failure patterns.\n\n"
                f"[CUT TO camera] At that price, you'd still want to see it in person, but "
                f"the data checks out. Could be a genuine bargain.\n\n"
                f"Always check before you buy. VeriCar is free. Link in bio.\n\n"
                f"[TEXT] {OGL_ATTRIBUTION}"
            ),
            "hashtags": [
                "#vericar", "#bargaincar", "#cheapcars", f"#{make.lower()}",
                "#cartok", "#usedcardeals", "#mothistory",
            ],
        },
        "overpriced_alert": {
            "hook": f"{price_str} for a {year_str} {make}?! Let me check the MOT history...",
            "script": (
                f"{price_str} for a {year_str} {make}?! Let me check the MOT history...\n\n"
                f"[CUT TO listing] The seller's asking top money for this {model}.\n\n"
                f"[CUT TO check] VeriCar pulled the full MOT history and the condition "
                f"score isn't great — recurring advisories on the same components, "
                f"MOT after MOT.\n\n"
                f"[ZOOM on data] In my opinion, you'd be paying a premium for a car "
                f"that the MOT data suggests needs work.\n\n"
                f"[CUT TO camera] Don't just look at photos. Check the data first. "
                f"VeriCar is free. Link in bio.\n\n"
                f"[TEXT] {OGL_ATTRIBUTION}"
            ),
            "hashtags": [
                "#vericar", "#overpriced", "#usedcars", f"#{make.lower()}",
                "#cartok", "#dontoverpay", "#mothistory",
            ],
        },
        "high_mileage_hero": {
            "hook": f"This {make} has done {mileage_str} miles. Should you run?",
            "script": (
                f"This {make} has done {mileage_str} miles. Should you run?\n\n"
                f"[CUT TO listing] Listed at {price_str} — it's priced for the mileage.\n\n"
                f"[CUT TO check] We ran it through VeriCar to check the full MOT history.\n\n"
                f"[PAUSE] Here's the thing — high mileage doesn't always mean bad. "
                f"What matters is whether the mileage went up consistently and "
                f"what the MOT advisories look like.\n\n"
                f"[CUT TO camera] VeriCar analyses all of that for you instantly. "
                f"Free check — link in bio.\n\n"
                f"[TEXT] {OGL_ATTRIBUTION}"
            ),
            "hashtags": [
                "#vericar", "#highmileage", "#usedcars", f"#{make.lower()}",
                "#cartok", "#carmileage", "#motcheck",
            ],
        },
        "mot_horror": {
            "hook": f"Wait until you see this {make}'s MOT history...",
            "script": (
                f"Wait until you see this {make}'s MOT history...\n\n"
                f"[CUT TO listing] Looks fine in the photos. {year_str}, {price_str}.\n\n"
                f"[CUT TO check] But VeriCar found the same components failing MOT "
                f"after MOT — brakes, suspension, the lot.\n\n"
                f"[ZOOM on data] The condition score is {check.get('condition_score', 'low') if check else 'low'}. "
                f"That's based on the actual MOT records, not my opinion.\n\n"
                f"[CUT TO camera] The photos won't tell you this. The MOT data will.\n\n"
                f"Check any car for free at VeriCar. Link in bio.\n\n"
                f"[TEXT] {OGL_ATTRIBUTION}"
            ),
            "hashtags": [
                "#vericar", "#motfail", "#usedcars", f"#{make.lower()}",
                "#cartok", "#mothistory", "#carbuying",
            ],
        },
        "hidden_gem": {
            "hook": f"Is this {year_str} {make} actually a hidden gem?",
            "script": (
                f"Is this {year_str} {make} actually a hidden gem?\n\n"
                f"[CUT TO listing] {price_str}, {mileage_str} miles. Nothing flashy.\n\n"
                f"[CUT TO check] But when we ran it through VeriCar — clean MOT history, "
                f"no mileage discrepancies, decent condition score.\n\n"
                f"[PAUSE] Sometimes the boring-looking ones are the best buys.\n\n"
                f"[CUT TO camera] Don't just scroll past. Check the data. "
                f"VeriCar is free. Link in bio.\n\n"
                f"[TEXT] {OGL_ATTRIBUTION}"
            ),
            "hashtags": [
                "#vericar", "#hiddengem", "#usedcars", f"#{make.lower()}",
                "#cartok", "#bestbuys", "#motcheck",
            ],
        },
    }

    script_data = scripts.get(angle, scripts["hidden_gem"])

    return TikTokScript(
        listing=listing,
        hook=script_data["hook"],
        script=script_data["script"],
        hashtags=script_data["hashtags"],
        angle=angle,
        estimated_duration_seconds=35,
    )
