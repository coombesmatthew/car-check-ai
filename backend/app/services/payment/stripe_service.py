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
        "amount": 499,
        "name": "VeriCar Report",
        "description": "Full vehicle history with PDF emailed within 60 seconds.",
    },
    "premium": {
        "amount": 999,
        "name": "VeriCar Premium Check",
        "description": "Finance, stolen, write-off, valuation, keeper history. PDF emailed within 60 seconds.",
    },
    "ev": {
        "amount": 899,
        "name": "VeriCar EV Health Check",
        "description": "Battery health, real-world range, charging costs, lifespan. PDF emailed within 60 seconds.",
    },
    "ev_complete": {
        "amount": 1399,
        "name": "VeriCar EV Complete Check",
        "description": "EV health plus finance, stolen, write-off, valuation, keeper history. PDF emailed within 60 seconds.",
    },
}


def create_checkout_session(
    registration: str,
    email: str | None,
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
        tier: "basic" (£4.99), "premium" (£9.99), "ev" (£8.99), or "ev_complete" (£13.99)
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
        if tier in ("ev", "ev_complete"):
            success_url = f"{base_url}/ev/report/success?session_id={{CHECKOUT_SESSION_ID}}"
        else:
            success_url = f"{base_url}/report/success?session_id={{CHECKOUT_SESSION_ID}}"
    if not cancel_url:
        if tier in ("ev", "ev_complete"):
            cancel_url = f"{base_url}/ev/report/cancel"
        else:
            cancel_url = f"{base_url}/report/cancel"

    metadata = {
        "registration": registration,
        "tier": tier,
    }
    if email:
        metadata["email"] = email
    if listing_url:
        metadata["listing_url"] = listing_url
    if listing_price is not None:
        metadata["listing_price"] = str(listing_price)

    session_kwargs = dict(
        # No payment_method_types — Stripe serves every method enabled in the
        # dashboard (Link, Apple Pay via card, Google Pay via card, etc.).
        # Letting the dashboard drive the list means new methods light up
        # without a deploy.
        line_items=[
            {
                "price_data": {
                    "currency": "gbp",
                    "product_data": {
                        # Name kept consistent across checkouts so the bank
                        # statement descriptor reads "VERICAR PREMIUM CHECK",
                        # not a per-plate SKU. Registration moves to the
                        # description line directly below.
                        "name": config["name"],
                        "description": f"Registration: {registration}. {config['description']}",
                    },
                    "unit_amount": config["amount"],
                },
                "quantity": 1,
            }
        ],
        mode="payment",
        success_url=success_url,
        cancel_url=cancel_url,
        metadata=metadata,
        # Shows a "Promotion code" input on the Stripe page. Codes must be
        # created in the Stripe dashboard (Products → Coupons + Promotion codes).
        # Use a 100%-off code for internal end-to-end testing; same mechanism
        # powers future launch/referral discounts.
        allow_promotion_codes=True,
    )
    if email:
        session_kwargs["customer_email"] = email

    session = stripe.checkout.Session.create(**session_kwargs)

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

    session = stripe.checkout.Session.retrieve(session_id, expand=["customer_details"])

    customer_details_email = ""
    if getattr(session, "customer_details", None):
        customer_details_email = session.customer_details.get("email", "") or ""
    resolved_email = (
        session.metadata.get("email")
        or session.customer_email
        or customer_details_email
        or ""
    )

    return {
        "session_id": session.id,
        "payment_status": session.payment_status,
        "registration": session.metadata.get("registration", ""),
        "email": resolved_email,
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
