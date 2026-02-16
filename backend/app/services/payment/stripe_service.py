"""Stripe payment integration for BASIC tier reports."""

import stripe

from app.core.config import settings
from app.core.logging import logger


def _init_stripe():
    """Initialise Stripe with API key."""
    if not settings.STRIPE_SECRET_KEY or settings.STRIPE_SECRET_KEY.startswith("your_"):
        raise RuntimeError("Stripe API key not configured")
    stripe.api_key = settings.STRIPE_SECRET_KEY


def create_checkout_session(
    registration: str,
    email: str,
    listing_url: str | None = None,
    listing_price: int | None = None,
    success_url: str = "http://localhost:3001/report/success?session_id={CHECKOUT_SESSION_ID}",
    cancel_url: str = "http://localhost:3001/report/cancel",
) -> dict:
    """Create a Stripe Checkout Session for a BASIC tier report.

    Args:
        registration: Vehicle registration number
        email: Customer email for receipt + report delivery
        listing_url: Optional listing URL for the AI report
        listing_price: Optional listing price in pence
        success_url: URL to redirect on successful payment
        cancel_url: URL to redirect on cancelled payment

    Returns:
        Dict with session_id and checkout_url.
    """
    _init_stripe()

    metadata = {
        "registration": registration,
        "tier": "basic",
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
                        "name": f"VeriCar Report — {registration}",
                        "description": "AI-powered vehicle buyer's report with condition score, risk assessment, and negotiation points. PDF delivered to your email.",
                    },
                    "unit_amount": 399,  # £3.99 in pence
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
