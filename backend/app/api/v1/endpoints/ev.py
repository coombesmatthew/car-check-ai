"""EV Health Check API endpoints.

GET  /api/v1/ev/count        - Total EV checks performed
POST /api/v1/ev/check        - Free EV check (validates EV, returns basic data)
POST /api/v1/ev/preview      - Free preview (DVLA + MOT data only)
POST /api/v1/ev/checkout     - Create Stripe checkout for paid EV report
POST /api/v1/ev/fulfil       - Fulfil paid EV report after Stripe payment
POST /api/v1/ev/webhook      - Stripe webhook for EV payments
"""

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional

from app.core.logging import logger
from app.core.cache import cache
from app.schemas.ev import EVCheckRequest, EVCheckResponse, EVCheckoutRequest
from app.services.ev.orchestrator import EVOrchestrator
from app.services.notification.analytics import track_event
from app.services.payment.stripe_service import create_checkout_session, verify_webhook_signature
from app.services.fulfilment import (
    fulfil_report_idempotent,
    get_fulfilment_status,
    handle_webhook,
    trigger_fulfilment_background,
)

router = APIRouter()


EV_SEED_COUNT = 84  # Seed from pre-counter checks


@router.get("/count")
async def get_ev_check_count():
    """Return the total number of EV checks performed."""
    count = await cache.get_counter("ev_checks_total")
    return {"total_checks": count + EV_SEED_COUNT}


@router.post("/check", response_model=EVCheckResponse)
async def ev_check(request: EVCheckRequest):
    """Run a free EV check.

    Validates that the vehicle is electric using DVLA fuelType.
    Returns vehicle identity, MOT summary, mileage analysis, and
    EV classification. Non-EVs get is_electric=False.
    """
    orchestrator = EVOrchestrator()
    try:
        result = await orchestrator.run_ev_check(request.registration)
        if not result.vehicle and not result.mot_summary:
            raise HTTPException(
                status_code=404,
                detail=f"No data found for registration {request.registration}",
            )
        await cache.increment("ev_checks_total")
        # PostHog: free EV search performed. GDPR: registration is hashed.
        track_event(
            event="vehicle_search_performed",
            registration=request.registration,
            properties={
                "surface": "ev",
                "found_data": bool(result.vehicle or result.mot_summary),
                "is_electric": result.is_electric,
                "ev_type": result.ev_type,
            },
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"EV check failed for {request.registration}: {e}")
        raise HTTPException(status_code=500, detail="EV check failed - please try again")
    finally:
        await orchestrator.close()


class EVPreviewResponse(BaseModel):
    registration: str
    ev_check: Optional[EVCheckResponse] = None
    price: str = "£8.99"


@router.post("/preview", response_model=EVPreviewResponse)
async def ev_preview(request: EVCheckRequest):
    """Run a FREE EV data check (DVLA + MOT only).

    The free page shows the raw EV data cards (battery health preview,
    charging estimates, etc.). Non-EVs get rejected with a 400 error.
    """
    orchestrator = EVOrchestrator()
    try:
        result = await orchestrator.run_ev_check(request.registration)

        if not result.is_electric:
            raise HTTPException(
                status_code=400,
                detail="This vehicle is not an electric vehicle. EV reports are only available for electric and plug-in hybrid vehicles.",
            )

        return EVPreviewResponse(
            registration=request.registration,
            ev_check=result,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"EV preview failed for {request.registration}: {e}")
        raise HTTPException(status_code=500, detail="EV preview failed - please try again")
    finally:
        await orchestrator.close()


class EVCheckoutResponse(BaseModel):
    session_id: str
    checkout_url: str


@router.post("/checkout", response_model=EVCheckoutResponse)
async def ev_checkout(request: EVCheckoutRequest):
    """Create a Stripe Checkout Session for a paid EV report."""
    if request.tier not in ("ev", "ev_complete"):
        raise HTTPException(status_code=400, detail="Invalid EV tier. Must be 'ev' or 'ev_complete'.")
    try:
        result = create_checkout_session(
            registration=request.registration,
            email=request.email,
            tier=request.tier,
            listing_price=request.listing_price,
            source=request.source,
            source_slug=request.source_slug,
        )
        return EVCheckoutResponse(**result)
    except RuntimeError as e:
        logger.error(f"Stripe not configured: {e}")
        raise HTTPException(status_code=503, detail="Payment service not available")
    except Exception as e:
        logger.error(f"EV checkout failed for {request.registration}: {e}")
        raise HTTPException(status_code=500, detail="Checkout failed - please try again")


class EVFulfilmentResponse(BaseModel):
    registration: str
    report_ref: str
    email_sent: bool
    verdict: Optional[str] = None
    payment_status: str
    ev_check: Optional[dict] = None


@router.post("/fulfil", response_model=EVFulfilmentResponse)
async def fulfil_ev_report(session_id: str):
    """Fulfil a paid EV report — blocks until complete. Idempotent.

    Kept for back-compat; new frontend should use /fulfil/trigger + /status
    to avoid the 100s gateway timeout.
    """
    try:
        result = await fulfil_report_idempotent(session_id)
        return EVFulfilmentResponse(
            registration=result.registration,
            report_ref=result.report_ref,
            email_sent=result.email_sent,
            verdict=result.verdict,
            payment_status=result.payment_status,
            ev_check=result.check_data,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"EV report fulfilment failed: {e}")
        raise HTTPException(
            status_code=500,
            detail="Report generation failed after payment - please contact support",
        )


@router.post("/fulfil/trigger", status_code=202)
async def trigger_ev_fulfilment(session_id: str):
    """Kick off EV fulfilment in the background. Returns immediately."""
    trigger_fulfilment_background(session_id)
    return {"status": "accepted", "session_id": session_id}


@router.get("/status", response_model=EVFulfilmentResponse)
async def ev_fulfilment_status(session_id: str):
    """Poll for an EV fulfilment result. 202 while pending; 200 with body when done."""
    result = await get_fulfilment_status(session_id)
    if result is None:
        return JSONResponse(
            status_code=202,
            content={"status": "pending", "session_id": session_id},
        )
    return EVFulfilmentResponse(
        registration=result.registration,
        report_ref=result.report_ref,
        email_sent=result.email_sent,
        verdict=result.verdict,
        payment_status=result.payment_status,
        ev_check=result.check_data,
    )


@router.post("/webhook")
async def ev_webhook(request: Request):
    """Handle Stripe webhook events for EV payments."""
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")

    try:
        event = verify_webhook_signature(payload, sig_header)
    except RuntimeError as e:
        logger.error(f"EV webhook secret not configured: {e}")
        raise HTTPException(status_code=500, detail="Webhook not configured")
    except Exception as e:
        logger.warning(f"EV webhook signature verification failed: {e}")
        raise HTTPException(status_code=400, detail="Invalid signature")

    return await handle_webhook(event)
