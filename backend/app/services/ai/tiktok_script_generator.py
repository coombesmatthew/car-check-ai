"""TikTok/Reels script generator using Claude AI with demo fallback."""

import json
from typing import Optional

import anthropic

from app.core.config import settings
from app.core.logging import logger
from app.schemas.scraping import ContentScore, TikTokScript


ANGLES = ["clocking_expose", "bargain_hunter", "overpriced_alert", "high_mileage_hero", "mot_horror", "hidden_gem", "auto"]

SYSTEM_PROMPT = """You are a viral TikTok/Reels content creator specialising in used cars in the UK.
You find dodgy, overpriced, or surprisingly good car deals on Gumtree and create short, punchy scripts.

Your style:
- Attention-grabbing hooks (first 3 seconds are everything)
- Direct, conversational British English
- Mix of humour and genuine buyer advice
- Always reference specific data (mileage, price, MOT history)
- End with a call to action

Output ONLY valid JSON with these fields:
{
  "hook": "The opening line (must grab attention in 3 seconds)",
  "script": "Full script for 30-60 second video, including the hook. Use [PAUSE], [CUT TO], [ZOOM] for editing cues.",
  "hashtags": ["list", "of", "relevant", "hashtags"],
  "angle": "one of: clocking_expose, bargain_hunter, overpriced_alert, high_mileage_hero, mot_horror, hidden_gem",
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
    parts = [f"Generate a TikTok script for this Gumtree car listing:"]

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
    parts.append(f"Clocking Detected: {scored_listing.clocking_detected}")

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
        if clocking.get("clocked"):
            parts.append("MILEAGE CLOCKING DETECTED:")
            for flag in clocking.get("flags", []):
                parts.append(f"  - [{flag.get('severity', '').upper()}] {flag.get('detail', '')}")

        patterns = check.get("failure_patterns", [])
        if patterns:
            parts.append("\nRecurring MOT Failures:")
            for p in patterns:
                parts.append(f"  - {p['category']}: {p['occurrences']}x ({p['concern_level']})")

    if angle != "auto":
        parts.append(f"\nUse the '{angle}' angle for this script.")
    else:
        parts.append("\nChoose the most compelling angle based on the data.")

    return "\n".join(parts)


def _generate_demo_script(scored_listing: ContentScore, angle: str) -> TikTokScript:
    """Generate a template-based demo script when API key is unavailable."""
    listing = scored_listing.listing
    make = listing.make or "car"
    model = listing.model or ""
    price_str = f"£{listing.price / 100:,.0f}" if listing.price else "unknown price"
    mileage_str = f"{listing.mileage:,}" if listing.mileage else "unknown"
    year_str = str(listing.year) if listing.year else "unknown year"

    # Auto-detect best angle
    if angle == "auto":
        if scored_listing.clocking_detected:
            angle = "clocking_expose"
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
        "clocking_expose": {
            "hook": f"This {make} on Gumtree has been CLOCKED. Here's the proof.",
            "script": (
                f"This {make} on Gumtree has been CLOCKED. Here's the proof.\n\n"
                f"[CUT TO listing] Listed as a {year_str} {make} {model} for {price_str} "
                f"with {mileage_str} miles.\n\n"
                f"[CUT TO data] But when we ran it through Car Check AI, the MOT history "
                f"shows the mileage actually DROPPED between tests. That's a classic sign "
                f"of odometer tampering.\n\n"
                f"[ZOOM on data] The seller might not even know — but you need to.\n\n"
                f"[CUT TO camera] Run ANY used car through Car Check AI before you buy. "
                f"Link in bio. It's free."
            ),
            "hashtags": ["#carcheckai", "#clockedcar", "#usedcarscam", f"#{make.lower()}", "#gumtree", "#cartok", "#usedcartips"],
        },
        "bargain_hunter": {
            "hook": f"I found a {year_str} {make} for {price_str}. Is it too good to be true?",
            "script": (
                f"I found a {year_str} {make} for {price_str}. Is it too good to be true?\n\n"
                f"[CUT TO listing] {mileage_str} miles, looks decent in the photos.\n\n"
                f"[CUT TO check] We ran the reg through Car Check AI and here's what came back...\n\n"
                f"[PAUSE] The MOT history is actually clean. No clocking, no major failures.\n\n"
                f"[CUT TO camera] At that price, you'd want to check it in person, but "
                f"the data says it could be a genuine bargain.\n\n"
                f"Always check before you buy. Link in bio."
            ),
            "hashtags": ["#carcheckai", "#bargaincar", "#cheapcars", f"#{make.lower()}", "#gumtree", "#cartok", "#usedcardeals"],
        },
        "overpriced_alert": {
            "hook": f"{price_str} for a {year_str} {make}?! Let me check the MOT history...",
            "script": (
                f"{price_str} for a {year_str} {make}?! Let me check the MOT history...\n\n"
                f"[CUT TO listing] The seller's asking top money for this {model}.\n\n"
                f"[CUT TO check] But Car Check AI reveals the condition score is not great "
                f"and there are recurring MOT issues.\n\n"
                f"[ZOOM on data] You'd be paying a premium for a car that needs work.\n\n"
                f"[CUT TO camera] Don't overpay. Check the data first. Link in bio."
            ),
            "hashtags": ["#carcheckai", "#overpriced", "#usedcars", f"#{make.lower()}", "#gumtree", "#cartok", "#dontoverpay"],
        },
        "high_mileage_hero": {
            "hook": f"This {make} has done {mileage_str} miles. Should you avoid it?",
            "script": (
                f"This {make} has done {mileage_str} miles. Should you avoid it?\n\n"
                f"[CUT TO listing] Listed at {price_str}, it's cheap for a reason.\n\n"
                f"[CUT TO check] We ran it through Car Check AI and checked the full MOT history.\n\n"
                f"[PAUSE] High mileage doesn't always mean bad — it depends on the service history.\n\n"
                f"[CUT TO camera] The key is whether the mileage went up consistently "
                f"or if there are gaps. Car Check AI spots all of that for you.\n\n"
                f"Free check — link in bio."
            ),
            "hashtags": ["#carcheckai", "#highmileage", "#usedcars", f"#{make.lower()}", "#gumtree", "#cartok", "#carmileage"],
        },
        "mot_horror": {
            "hook": f"Wait until you see this {make}'s MOT history...",
            "script": (
                f"Wait until you see this {make}'s MOT history...\n\n"
                f"[CUT TO listing] Looks fine in the photos. {year_str}, {price_str}.\n\n"
                f"[CUT TO check] But Car Check AI found MULTIPLE recurring failure patterns.\n\n"
                f"[ZOOM on data] Same issues coming up MOT after MOT. That's expensive.\n\n"
                f"[CUT TO camera] The photos won't tell you this. The MOT data will.\n\n"
                f"Check any car for free. Link in bio."
            ),
            "hashtags": ["#carcheckai", "#motfail", "#usedcars", f"#{make.lower()}", "#gumtree", "#cartok", "#mothistory"],
        },
        "hidden_gem": {
            "hook": f"Is this {year_str} {make} actually a hidden gem?",
            "script": (
                f"Is this {year_str} {make} actually a hidden gem?\n\n"
                f"[CUT TO listing] {price_str}, {mileage_str} miles. Nothing flashy.\n\n"
                f"[CUT TO check] But when we ran it through Car Check AI — clean MOT history, "
                f"no clocking, decent condition score.\n\n"
                f"[PAUSE] Sometimes the boring ones are the best buys.\n\n"
                f"[CUT TO camera] Don't just look at photos — check the data. "
                f"Car Check AI is free. Link in bio."
            ),
            "hashtags": ["#carcheckai", "#hiddengem", "#usedcars", f"#{make.lower()}", "#gumtree", "#cartok", "#bestbuys"],
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
