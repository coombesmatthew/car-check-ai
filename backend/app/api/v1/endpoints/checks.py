from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, EmailStr
from typing import Optional

from app.core.logging import logger
from app.core.cache import cache
from app.schemas.check import FreeCheckRequest, FreeCheckResponse
from app.services.check.orchestrator import CheckOrchestrator
from app.services.notification.analytics import track_event
from app.services.payment.stripe_service import create_checkout_session, verify_webhook_signature
from app.services.fulfilment import (
    fulfil_report_idempotent,
    get_fulfilment_status,
    handle_webhook,
    trigger_fulfilment_background,
)

router = APIRouter()


@router.post("/free", response_model=FreeCheckResponse)
async def free_check(request: FreeCheckRequest):
    """Run a free vehicle check using DVLA VES + DVSA MOT data.

    Returns vehicle identity, MOT summary, mileage clocking analysis,
    condition score, ULEZ compliance, and failure patterns.
    Zero cost - no external paid APIs used.
    """
    orchestrator = CheckOrchestrator()
    try:
        result = await orchestrator.run_free_check(request.registration)
        if not result.vehicle and not result.mot_summary:
            raise HTTPException(
                status_code=404,
                detail=f"No data found for registration {request.registration}",
            )
        # Increment check counter (fire-and-forget, don't block response)
        await cache.increment("checks_total")
        # PostHog: free vehicle search performed. GDPR: registration is hashed.
        track_event(
            event="vehicle_search_performed",
            registration=request.registration,
            properties={
                "surface": "car",
                "found_data": bool(result.vehicle or result.mot_summary),
                "is_electric": (result.vehicle.fuel_type or "").upper() in ("ELECTRICITY", "ELECTRIC DIESEL", "ELECTRIC PETROL") if result.vehicle else False,
            },
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Free check failed for {request.registration}: {e}")
        raise HTTPException(status_code=500, detail="Check failed - please try again")
    finally:
        await orchestrator.close()


SEED_COUNT = 1247  # Seed from pre-counter checks during development/testing


@router.get("/count")
async def get_check_count():
    """Return the total number of vehicle checks performed."""
    count = await cache.get_counter("checks_total")
    return {"total_checks": count + SEED_COUNT}


# --- Stripe Payment Flow ---


class CheckoutRequest(BaseModel):
    registration: str
    email: Optional[str] = None  # optional — Stripe collects if absent
    tier: str = "premium"
    listing_url: Optional[str] = None
    listing_price: Optional[int] = None


class CheckoutResponse(BaseModel):
    session_id: str
    checkout_url: str


@router.post("/basic/checkout", response_model=CheckoutResponse)
async def create_basic_checkout(request: CheckoutRequest):
    """Create a Stripe Checkout Session for the Premium tier report.

    Returns a checkout URL that the frontend redirects the customer to.
    """
    tier = request.tier if request.tier == "premium" else "premium"
    try:
        result = create_checkout_session(
            registration=request.registration,
            email=request.email,
            tier=tier,
            listing_url=request.listing_url,
            listing_price=request.listing_price,
        )
        return CheckoutResponse(**result)
    except RuntimeError as e:
        logger.error(f"Stripe not configured: {e}")
        raise HTTPException(status_code=503, detail="Payment service not available")
    except Exception as e:
        logger.error(f"Checkout creation failed for {request.registration}: {e}")
        raise HTTPException(status_code=500, detail="Checkout failed - please try again")


class FulfilmentResponse(BaseModel):
    registration: str
    report_ref: str
    email_sent: bool
    verdict: Optional[str] = None
    payment_status: str


@router.post("/basic/fulfil", response_model=FulfilmentResponse)
async def fulfil_basic_report(session_id: str):
    """Fulfil a BASIC/PREMIUM tier report — blocks until complete.

    Idempotent via session_id cache. Still exposed for back-compat with
    older frontend success pages, but new flow should use /fulfil/trigger
    + /status to avoid the 100s gateway timeout (AI can take 2+ minutes).
    """
    try:
        result = await fulfil_report_idempotent(session_id)
        return FulfilmentResponse(
            registration=result.registration,
            report_ref=result.report_ref,
            email_sent=result.email_sent,
            verdict=result.verdict,
            payment_status=result.payment_status,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Report fulfilment failed: {e}")
        raise HTTPException(
            status_code=500,
            detail="Report generation failed after payment - please contact support",
        )


@router.post("/basic/fulfil/trigger", status_code=202)
async def trigger_basic_fulfilment(session_id: str):
    """Kick off fulfilment in the background and return immediately.

    Idempotent — safe if Stripe webhook has already triggered it. Frontend
    calls this on success page load, then polls /basic/status for the result.
    """
    trigger_fulfilment_background(session_id)
    return {"status": "accepted", "session_id": session_id}


@router.get("/report/data")
async def report_data(session_id: str):
    """Return the full fulfilment payload as JSON so the Next.js /report
    page can render the report natively (with site header/footer/styling).

    Gated by session_id + payment_status; the data lives in the Redis
    fulfil cache (24h TTL).
    """
    result = await get_fulfilment_status(session_id)
    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Report not found. If you just paid, wait a minute and reload.",
        )
    if result.payment_status != "paid":
        raise HTTPException(status_code=402, detail="Payment not completed")

    check = result.check_data or {}
    # is_electric comes from DVLA fuel_type — the truth source that doesn't
    # depend on upstream EV API success. Fall back to checking EV data
    # fields only for legacy cached results pre-dating the is_electric flag.
    is_ev = bool(check.get("is_electric")) or any(
        check.get(k) for k in ("battery_health", "range_estimate", "ev_specs", "charging_costs")
    )
    return {
        "registration": result.registration,
        "report_ref": result.report_ref,
        "tier": "ev" if is_ev else "car",
        "is_ev": is_ev,
        "check_data": check,
    }


@router.get("/report/view", response_class=HTMLResponse)
async def view_report(session_id: str):
    """Render the customer's report as a browser page.

    Gated by session_id (cached fulfilment result lives in Redis for 24h
    alongside the session). Returns the same HTML we email — reusing the
    Jinja template keeps a single source of truth for the report layout.
    """
    from app.services.notification.email_sender import render_report_email

    result = await get_fulfilment_status(session_id)
    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Report not found. If you just paid, wait a minute and reload.",
        )
    if result.payment_status != "paid":
        raise HTTPException(status_code=402, detail="Payment not completed")

    html = render_report_email(
        check_data=result.check_data,
        verdict=None,  # verdicts removed
        report_ref=result.report_ref,
    )
    return HTMLResponse(html)


@router.get("/basic/status", response_model=FulfilmentResponse)
async def basic_fulfilment_status(session_id: str):
    """Poll for a fulfilment result.

    Returns the FulfilmentResponse if done. Returns 202 with a simple
    payload if still in progress — frontend should keep polling.
    """
    result = await get_fulfilment_status(session_id)
    if result is None:
        return JSONResponse(
            status_code=202,
            content={"status": "pending", "session_id": session_id},
        )
    return FulfilmentResponse(
        registration=result.registration,
        report_ref=result.report_ref,
        email_sent=result.email_sent,
        verdict=result.verdict,
        payment_status=result.payment_status,
    )


# --- Stripe Webhook ---


@router.post("/basic/webhook")
async def stripe_webhook(request: Request):
    """Handle Stripe webhook events.

    Stripe sends events here when payments complete, fail, etc.
    This is a backup for the redirect-based fulfilment flow.
    """
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")

    try:
        event = verify_webhook_signature(payload, sig_header)
    except RuntimeError as e:
        logger.error(f"Webhook secret not configured: {e}")
        raise HTTPException(status_code=500, detail="Webhook not configured")
    except Exception as e:
        logger.warning(f"Webhook signature verification failed: {e}")
        raise HTTPException(status_code=400, detail="Invalid signature")

    return handle_webhook(event)


# --- Lead Capture ---


class LeadCaptureRequest(BaseModel):
    email: EmailStr
    registration: str


@router.post("/leads", status_code=201)
async def capture_lead(request: LeadCaptureRequest):
    """Capture an email lead from a free check user."""
    import datetime
    entry = f"{request.email}|{request.registration.upper()}|{datetime.datetime.utcnow().isoformat()}"
    await cache.list_push("leads", entry)
    logger.info(f"Lead captured: {request.email} for {request.registration.upper()}")
    return {"ok": True}


