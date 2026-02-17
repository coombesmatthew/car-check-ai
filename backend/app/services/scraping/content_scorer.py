"""Content scorer — ranks Gumtree listings by how interesting they are for social content.

Pure logic, no external dependencies. Scoring factors (0-100 scale):
  - Price anomaly: suspiciously cheap/expensive for age (+0-25)
  - Mileage anomaly: too high or suspiciously low for age (+0-20)
  - Mileage discrepancy detected (+0-30)
  - Poor condition score from MOT (+0-15)
  - Recurring MOT failure patterns (+0-10)
"""

from typing import List, Dict, Any, Optional
from datetime import datetime

from app.core.logging import logger
from app.schemas.scraping import GumtreeListing, ContentScore, ScoreFactor


# Average UK used car price by approximate age (rough guide, pounds)
AVG_PRICE_BY_AGE = {
    1: 20000, 2: 17000, 3: 14000, 4: 11000, 5: 9000,
    6: 7000, 7: 5500, 8: 4500, 9: 3500, 10: 3000,
    15: 2000, 20: 1500,
}

# UK average annual mileage
UK_AVG_ANNUAL_MILEAGE = 7400


def score_listing(
    listing: GumtreeListing,
    check_result: Optional[Dict[str, Any]] = None,
) -> ContentScore:
    """Score a single listing for content interest.

    Args:
        listing: The Gumtree listing to score.
        check_result: Optional FreeCheckResponse as dict from Car Check AI.

    Returns:
        ContentScore with total score, breakdown factors, and check data.
    """
    factors = []
    clocking_detected = False

    # Factor 1: Price anomaly (0-25 points)
    price_score = _score_price_anomaly(listing)
    if price_score:
        factors.append(price_score)

    # Factor 2: Mileage anomaly (0-20 points)
    mileage_score = _score_mileage_anomaly(listing)
    if mileage_score:
        factors.append(mileage_score)

    if check_result:
        # Factor 3: Clocking detected (0-30 points)
        clocking = check_result.get("clocking_analysis")
        if clocking and clocking.get("clocked"):
            clocking_detected = True
            flags = clocking.get("flags", [])
            points = min(30, 15 + len(flags) * 5)
            factors.append(ScoreFactor(
                name="clocking_detected",
                points=points,
                detail=f"Mileage clocking detected with {len(flags)} flag(s) — {clocking.get('risk_level', 'high')} risk",
            ))

        # Factor 4: Poor condition (0-15 points)
        condition = check_result.get("condition_score")
        if condition is not None:
            if condition < 40:
                factors.append(ScoreFactor(
                    name="poor_condition",
                    points=15,
                    detail=f"Very poor condition score: {condition}/100",
                ))
            elif condition < 60:
                factors.append(ScoreFactor(
                    name="poor_condition",
                    points=10,
                    detail=f"Below-average condition score: {condition}/100",
                ))
            elif condition < 75:
                factors.append(ScoreFactor(
                    name="moderate_condition",
                    points=5,
                    detail=f"Moderate condition score: {condition}/100",
                ))

        # Factor 5: Failure patterns (0-10 points)
        patterns = check_result.get("failure_patterns", [])
        if patterns:
            high_concern = [p for p in patterns if p.get("concern_level") == "high"]
            if high_concern:
                factors.append(ScoreFactor(
                    name="recurring_failures",
                    points=10,
                    detail=f"{len(high_concern)} recurring high-concern failure pattern(s): {', '.join(p['category'] for p in high_concern)}",
                ))
            elif len(patterns) >= 2:
                factors.append(ScoreFactor(
                    name="recurring_failures",
                    points=5,
                    detail=f"{len(patterns)} recurring failure pattern(s)",
                ))

    total_score = sum(f.points for f in factors)

    return ContentScore(
        listing=listing,
        total_score=total_score,
        factors=factors,
        check_result=check_result,
        clocking_detected=clocking_detected,
    )


def rank_listings(
    scored: List[ContentScore],
    top_n: int = 5,
) -> List[ContentScore]:
    """Rank scored listings by total score and return top N.

    Args:
        scored: List of ContentScore objects.
        top_n: Number of top results to return.

    Returns:
        Top N listings sorted by score descending.
    """
    sorted_listings = sorted(scored, key=lambda s: s.total_score, reverse=True)
    return sorted_listings[:top_n]


def _score_price_anomaly(listing: GumtreeListing) -> Optional[ScoreFactor]:
    """Score based on how abnormal the price is for the car's age."""
    if listing.price is None or listing.year is None:
        return None

    price_pounds = listing.price / 100
    current_year = datetime.now().year
    age = current_year - listing.year

    if age < 1:
        return None

    # Find expected price for age
    expected = None
    for age_bracket in sorted(AVG_PRICE_BY_AGE.keys()):
        if age <= age_bracket:
            expected = AVG_PRICE_BY_AGE[age_bracket]
            break
    if expected is None:
        expected = 1000  # Very old cars

    ratio = price_pounds / expected if expected > 0 else 0

    if ratio < 0.3:
        return ScoreFactor(
            name="price_anomaly",
            points=25,
            detail=f"Suspiciously cheap: £{price_pounds:,.0f} vs ~£{expected:,} expected for a {age}-year-old car",
        )
    elif ratio < 0.5:
        return ScoreFactor(
            name="price_anomaly",
            points=15,
            detail=f"Very cheap: £{price_pounds:,.0f} vs ~£{expected:,} expected for a {age}-year-old car",
        )
    elif ratio > 2.0:
        return ScoreFactor(
            name="price_anomaly",
            points=20,
            detail=f"Overpriced: £{price_pounds:,.0f} vs ~£{expected:,} expected for a {age}-year-old car",
        )
    elif ratio > 1.5:
        return ScoreFactor(
            name="price_anomaly",
            points=10,
            detail=f"Above average price: £{price_pounds:,.0f} vs ~£{expected:,} expected",
        )

    return None


def _score_mileage_anomaly(listing: GumtreeListing) -> Optional[ScoreFactor]:
    """Score based on how abnormal the listed mileage is for the car's age."""
    if listing.mileage is None or listing.year is None:
        return None

    current_year = datetime.now().year
    age = current_year - listing.year

    if age < 1:
        return None

    expected_mileage = age * UK_AVG_ANNUAL_MILEAGE
    actual = listing.mileage

    if expected_mileage == 0:
        return None

    ratio = actual / expected_mileage

    if ratio > 3.0:
        return ScoreFactor(
            name="mileage_anomaly",
            points=20,
            detail=f"Extremely high mileage: {actual:,} vs ~{expected_mileage:,} expected for age",
        )
    elif ratio > 2.0:
        return ScoreFactor(
            name="mileage_anomaly",
            points=12,
            detail=f"High mileage: {actual:,} vs ~{expected_mileage:,} expected for age",
        )
    elif ratio < 0.2 and actual > 5000:
        return ScoreFactor(
            name="mileage_anomaly",
            points=15,
            detail=f"Suspiciously low mileage: {actual:,} vs ~{expected_mileage:,} expected — possible rollback?",
        )
    elif ratio < 0.4:
        return ScoreFactor(
            name="mileage_anomaly",
            points=8,
            detail=f"Below-average mileage: {actual:,} vs ~{expected_mileage:,} expected",
        )

    return None
