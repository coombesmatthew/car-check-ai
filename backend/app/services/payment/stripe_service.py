"""Stripe payment integration for BASIC tier reports."""
from __future__ import annotations

import stripe

from app.core.config import settings
from app.core.logging import logger


def _init_stripe():
    """Initialise Stripe with API key."""
    if not settings.STRIPE_SECRET_KEY or settings.STRIPE_SECRET_KEY.startswith("your_"):
        raise RuntimeError("Stripe API key not configured")
    stripe.api_key = settings.STRIPE_SECRET_KEY


TIER_CONFIG = {
    "basic": {
        "amount": 399,
        "name": "VeriCar Report",
        "description": "AI-powered buyer's report with condition score, risk assessment, and negotiation points. PDF delivered to your email.",
    },
    "premium": {
        "amount": 999,
        "name": "VeriCar Premium Check",
        "description": "Full vehicle history: finance, stolen, write-off, valuation, keeper history, plus AI buyer's report. PDF delivered to your email.",
    },
    "ev": {
        "amount": 799,
        "name": "VeriCar EV Health Check",
        "description": "Battery health score, real-world range estimate, charging costs, lifespan prediction, plus AI report. PDF delivered to your email.",
    },
}


def create_checkout_session(
    registration: str,
    email: str,
    tier: str = "basic",
    listing_url: str | None = None,
    listing_price: int | None = None,
    success_url: str | None = None,
    cancel_url: str | None = None,
) -> dict:
    """Create a Stripe Checkout Session for a paid tier.

    Args:
        registration: Vehicle registration number
        email: Customer email for receipt + report delivery
        tier: "basic" (£3.99), "premium" (£9.99), or "ev" (£7.99)
        listing_url: Optional listing URL for the AI report
        listing_price: Optional listing price in pence
        success_url: URL to redirect on successful payment
        cancel_url: URL to redirect on cancelled payment

    Returns:
        Dict with session_id and checkout_url.
    """
    _init_stripe()

    if tier not in TIER_CONFIG:
        raise ValueError(f"Invalid tier: {tier}. Must be one of: {', '.join(TIER_CONFIG.keys())}")
    config = TIER_CONFIG[tier]

    base_url = settings.SITE_URL.rstrip("/")
    if not success_url:
        if tier == "ev":
            success_url = f"{base_url}/ev/report/success?session_id={{CHECKOUT_SESSION_ID}}"
        else:
            success_url = f"{base_url}/report/success?session_id={{CHECKOUT_SESSION_ID}}"
    if not cancel_url:
        if tier == "ev":
            cancel_url = f"{base_url}/ev/report/cancel"
        else:
            cancel_url = f"{base_url}/report/cancel"

    metadata = {
        "registration": registration,
        "tier": tier,
        "email": email,
    }
    if listing_url:
        metadata["listing_url"] = listing_url
    if listing_price is not None:
        metadata["listing_price"] = str(listing_price)

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[
            {
                "price_data": {
                    "currency": "gbp",
                    "product_data": {
                        "name": f"{config['name']} — {registration}",
                        "description": config["description"],
                    },
                    "unit_amount": config["amount"],
                },
                "quantity": 1,
            }
        ],
        mode="payment",
        customer_email=email,
        success_url=success_url,
        cancel_url=cancel_url,
        metadata=metadata,
    )

    logger.info(f"Checkout session created for {registration} (session: {session.id})")

    return {
        "session_id": session.id,
        "checkout_url": session.url,
    }


def retrieve_session(session_id: str) -> dict:
    """Retrieve a Checkout Session to verify payment status.

    Returns:
        Dict with payment_status, registration, email, and metadata.
    """
    _init_stripe()

    session = stripe.checkout.Session.retrieve(session_id)

    return {
        "session_id": session.id,
        "payment_status": session.payment_status,
        "registration": session.metadata.get("registration", ""),
        "email": session.metadata.get("email", session.customer_email or ""),
        "tier": session.metadata.get("tier", "basic"),
        "listing_url": session.metadata.get("listing_url"),
        "listing_price": int(session.metadata["listing_price"]) if session.metadata.get("listing_price") else None,
        "amount_total": session.amount_total,
        "currency": session.currency,
    }


def verify_webhook_signature(payload: bytes, sig_header: str) -> dict:
    """Verify a Stripe webhook signature and return the event.

    Args:
        payload: Raw request body
        sig_header: Stripe-Signature header value

    Returns:
        Stripe event dict.
    """
    _init_stripe()

    if not settings.STRIPE_WEBHOOK_SECRET:
        raise RuntimeError("Stripe webhook secret not configured")

    event = stripe.Webhook.construct_event(
        payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
    )
    return event
