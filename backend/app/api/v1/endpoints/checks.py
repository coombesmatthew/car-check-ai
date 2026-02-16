from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import Response
from pydantic import BaseModel, EmailStr
from typing import Optional, List

from app.core.logging import logger
from app.schemas.check import FreeCheckRequest, FreeCheckResponse, BasicCheckRequest
from app.services.check.orchestrator import CheckOrchestrator
from app.services.ai.report_generator import generate_ai_report
from app.services.report.pdf_generator import generate_pdf, _extract_verdict
from app.services.notification.email_sender import send_report_email
from app.services.payment.stripe_service import create_checkout_session, retrieve_session, verify_webhook_signature
from app.services.listing.scraper import scrape_listing

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
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Free check failed for {request.registration}: {e}")
        raise HTTPException(status_code=500, detail="Check failed - please try again")
    finally:
        await orchestrator.close()


class BasicCheckPreviewRequest(BaseModel):
    registration: str
    listing_url: Optional[str] = None
    listing_price: Optional[int] = None


class BasicCheckPreviewResponse(BaseModel):
    registration: str
    ai_report: Optional[str] = None
    free_check: Optional[FreeCheckResponse] = None
    price: str = "£3.99"


@router.post("/basic/preview", response_model=BasicCheckPreviewResponse)
async def basic_check_preview(request: BasicCheckPreviewRequest):
    """Preview a BASIC check with AI report. Demo endpoint - no payment required.

    This endpoint is for product review only. In production, payment
    will be required before the AI report is generated.
    """
    orchestrator = CheckOrchestrator()
    try:
        # Run the free check first
        free_result = await orchestrator.run_free_check(request.registration)

        # Generate AI report using Claude
        ai_report = await generate_ai_report(
            registration=request.registration,
            vehicle_data=orchestrator._raw_dvla_data if hasattr(orchestrator, '_raw_dvla_data') else None,
            mot_analysis=orchestrator._raw_mot_analysis if hasattr(orchestrator, '_raw_mot_analysis') else {},
            ulez_data=orchestrator._raw_ulez_data if hasattr(orchestrator, '_raw_ulez_data') else None,
            listing_price=request.listing_price,
            listing_url=request.listing_url,
        )

        return BasicCheckPreviewResponse(
            registration=request.registration,
            ai_report=ai_report,
            free_check=free_result,
        )
    except Exception as e:
        logger.error(f"Basic check preview failed for {request.registration}: {e}")
        raise HTTPException(status_code=500, detail="Preview failed - please try again")
    finally:
        await orchestrator.close()


class BasicReportRequest(BaseModel):
    registration: str
    email: str
    listing_url: Optional[str] = None
    listing_price: Optional[int] = None


class BasicReportResponse(BaseModel):
    registration: str
    report_ref: str
    email_sent: bool
    pdf_size_bytes: int
    verdict: Optional[str] = None
    price: str = "£3.99"


@router.post("/basic/report", response_model=BasicReportResponse)
async def generate_basic_report(request: BasicReportRequest):
    """Generate and deliver a BASIC tier report.

    Flow: run free check → generate AI report → build PDF → email to customer.
    In production, this endpoint will require prior Stripe payment.
    Currently operates as a demo with no payment gate.
    """
    orchestrator = CheckOrchestrator()
    try:
        # 1. Run the free check
        free_result = await orchestrator.run_free_check(request.registration)

        # 2. Generate AI report
        ai_report = await generate_ai_report(
            registration=request.registration,
            vehicle_data=orchestrator._raw_dvla_data if hasattr(orchestrator, '_raw_dvla_data') else None,
            mot_analysis=orchestrator._raw_mot_analysis if hasattr(orchestrator, '_raw_mot_analysis') else {},
            ulez_data=orchestrator._raw_ulez_data if hasattr(orchestrator, '_raw_ulez_data') else None,
            listing_price=request.listing_price,
            listing_url=request.listing_url,
        )

        # 3. Build check data dict for PDF/email
        check_data = free_result.model_dump()

        # 4. Generate PDF
        pdf_bytes = generate_pdf(check_data, ai_report)
        verdict = _extract_verdict(ai_report) if ai_report else None

        # 5. Extract report ref from PDF generator (embedded in the PDF)
        import uuid
        from datetime import datetime as dt
        report_ref = f"CV-{dt.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"

        # 6. Send email
        email_sent = await send_report_email(
            to_email=request.email,
            check_data=check_data,
            pdf_bytes=pdf_bytes,
            verdict=verdict,
            report_ref=report_ref,
        )

        logger.info(
            f"BASIC report generated for {request.registration} "
            f"(ref: {report_ref}, pdf: {len(pdf_bytes)} bytes, email: {email_sent})"
        )

        return BasicReportResponse(
            registration=request.registration,
            report_ref=report_ref,
            email_sent=email_sent,
            pdf_size_bytes=len(pdf_bytes),
            verdict=verdict,
        )

    except Exception as e:
        logger.error(f"Basic report failed for {request.registration}: {e}")
        raise HTTPException(status_code=500, detail="Report generation failed - please try again")
    finally:
        await orchestrator.close()


@router.post("/basic/pdf")
async def download_basic_pdf(request: BasicReportRequest):
    """Generate and return a BASIC tier PDF directly.

    Returns the PDF as a downloadable file. Useful for immediate download
    without email delivery.
    """
    orchestrator = CheckOrchestrator()
    try:
        # 1. Run the free check
        free_result = await orchestrator.run_free_check(request.registration)

        # 2. Generate AI report
        ai_report = await generate_ai_report(
            registration=request.registration,
            vehicle_data=orchestrator._raw_dvla_data if hasattr(orchestrator, '_raw_dvla_data') else None,
            mot_analysis=orchestrator._raw_mot_analysis if hasattr(orchestrator, '_raw_mot_analysis') else {},
            ulez_data=orchestrator._raw_ulez_data if hasattr(orchestrator, '_raw_ulez_data') else None,
            listing_price=request.listing_price,
            listing_url=request.listing_url,
        )

        # 3. Generate PDF
        check_data = free_result.model_dump()
        pdf_bytes = generate_pdf(check_data, ai_report)

        logger.info(f"PDF downloaded for {request.registration} ({len(pdf_bytes)} bytes)")

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="VeriCar-{request.registration}.pdf"',
            },
        )

    except Exception as e:
        logger.error(f"PDF generation failed for {request.registration}: {e}")
        raise HTTPException(status_code=500, detail="PDF generation failed - please try again")
    finally:
        await orchestrator.close()


# --- Stripe Payment Flow ---


class CheckoutRequest(BaseModel):
    registration: str
    email: str
    listing_url: Optional[str] = None
    listing_price: Optional[int] = None


class CheckoutResponse(BaseModel):
    session_id: str
    checkout_url: str


@router.post("/basic/checkout", response_model=CheckoutResponse)
async def create_basic_checkout(request: CheckoutRequest):
    """Create a Stripe Checkout Session for a BASIC tier report.

    Returns a checkout URL that the frontend redirects the customer to.
    On successful payment, Stripe redirects to the success URL with the session ID.
    """
    try:
        result = create_checkout_session(
            registration=request.registration,
            email=request.email,
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
    pdf_size_bytes: int
    verdict: Optional[str] = None
    payment_status: str


@router.post("/basic/fulfil", response_model=FulfilmentResponse)
async def fulfil_basic_report(session_id: str):
    """Fulfil a BASIC tier report after successful Stripe payment.

    Verifies payment, generates the report, and sends the email.
    Called by the frontend after the customer returns from Stripe Checkout.
    """
    # 1. Verify payment with Stripe
    try:
        session = retrieve_session(session_id)
    except Exception as e:
        logger.error(f"Session retrieval failed: {e}")
        raise HTTPException(status_code=400, detail="Invalid payment session")

    if session["payment_status"] != "paid":
        raise HTTPException(
            status_code=402,
            detail=f"Payment not completed (status: {session['payment_status']})",
        )

    registration = session["registration"]
    email = session["email"]
    listing_url = session.get("listing_url")
    listing_price = session.get("listing_price")

    # 2. Generate the report
    orchestrator = CheckOrchestrator()
    try:
        free_result = await orchestrator.run_free_check(registration)

        ai_report = await generate_ai_report(
            registration=registration,
            vehicle_data=orchestrator._raw_dvla_data if hasattr(orchestrator, '_raw_dvla_data') else None,
            mot_analysis=orchestrator._raw_mot_analysis if hasattr(orchestrator, '_raw_mot_analysis') else {},
            ulez_data=orchestrator._raw_ulez_data if hasattr(orchestrator, '_raw_ulez_data') else None,
            listing_price=listing_price,
            listing_url=listing_url,
        )

        check_data = free_result.model_dump()
        pdf_bytes = generate_pdf(check_data, ai_report)
        verdict = _extract_verdict(ai_report) if ai_report else None

        import uuid
        from datetime import datetime as dt
        report_ref = f"CV-{dt.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"

        email_sent = await send_report_email(
            to_email=email,
            check_data=check_data,
            pdf_bytes=pdf_bytes,
            verdict=verdict,
            report_ref=report_ref,
        )

        logger.info(
            f"BASIC report fulfilled for {registration} "
            f"(ref: {report_ref}, session: {session_id}, email: {email_sent})"
        )

        return FulfilmentResponse(
            registration=registration,
            report_ref=report_ref,
            email_sent=email_sent,
            pdf_size_bytes=len(pdf_bytes),
            verdict=verdict,
            payment_status="paid",
        )

    except Exception as e:
        logger.error(f"Report fulfilment failed for {registration}: {e}")
        raise HTTPException(status_code=500, detail="Report generation failed after payment - please contact support")
    finally:
        await orchestrator.close()


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

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        logger.info(
            f"Webhook: checkout.session.completed for "
            f"{session.get('metadata', {}).get('registration', 'unknown')} "
            f"(session: {session.get('id')})"
        )
        # The success page handles fulfilment via /basic/fulfil.
        # This webhook logs the event for monitoring.
        # Future: add idempotent fulfilment here as a fallback.

    return {"received": True}


# --- Listing Check (paste a URL) ---


class ListingCheckRequest(BaseModel):
    url: str
    registration: Optional[str] = None  # override if user provides it


class ListingCheckResponse(BaseModel):
    listing: dict
    free_check: Optional[FreeCheckResponse] = None
    ai_report: Optional[str] = None
    price_assessment: Optional[str] = None  # "overpriced" / "fair" / "good deal" / "unknown"


def _assess_price(listing_price_pence: Optional[int], free_check: Optional[FreeCheckResponse]) -> Optional[str]:
    """Simple price assessment based on listing price vs valuation data.

    Returns 'overpriced', 'fair', 'good deal', or 'unknown'.
    """
    if not listing_price_pence or not free_check:
        return "unknown"

    # If valuation data is available, compare against it
    if free_check.valuation and free_check.valuation.private_sale is not None:
        private_sale_pence = free_check.valuation.private_sale * 100
        ratio = listing_price_pence / private_sale_pence if private_sale_pence > 0 else 1.0

        if ratio > 1.15:
            return "overpriced"
        elif ratio < 0.90:
            return "good deal"
        else:
            return "fair"

    # Without valuation data, we cannot assess
    return "unknown"


@router.post("/listing", response_model=ListingCheckResponse)
async def check_listing(request: ListingCheckRequest):
    """Check a car listing by URL.

    Scrapes the listing, extracts vehicle data, runs a free check
    if registration is available, and generates an AI analysis
    combining listing data with vehicle check data.
    """
    # 1. Scrape the listing URL
    listing_data = await scrape_listing(request.url)

    if not listing_data.scrape_success and listing_data.platform == "unknown":
        raise HTTPException(
            status_code=400,
            detail=(
                "Could not process this URL. "
                "Supported platforms: AutoTrader, Gumtree, Facebook Marketplace."
            ),
        )

    # 2. Determine registration: user-provided takes priority, then scraped
    registration = request.registration
    if registration:
        registration = registration.replace(" ", "").upper()
    elif listing_data.registration:
        registration = listing_data.registration.replace(" ", "").upper()

    # 3. Run the free check if we have a registration
    free_check = None
    orchestrator = None
    if registration:
        orchestrator = CheckOrchestrator()
        try:
            free_check = await orchestrator.run_free_check(registration)
        except Exception as e:
            logger.warning(f"Free check failed for listing reg {registration}: {e}")
            # Non-fatal: we still have listing data
        finally:
            if orchestrator:
                await orchestrator.close()

    # 4. Generate AI report combining listing + vehicle check data
    ai_report = None
    if registration:
        try:
            ai_report = await generate_ai_report(
                registration=registration,
                vehicle_data=orchestrator._raw_dvla_data if orchestrator and hasattr(orchestrator, '_raw_dvla_data') else None,
                mot_analysis=orchestrator._raw_mot_analysis if orchestrator and hasattr(orchestrator, '_raw_mot_analysis') else {},
                ulez_data=orchestrator._raw_ulez_data if orchestrator and hasattr(orchestrator, '_raw_ulez_data') else None,
                listing_price=listing_data.price_pence,
                listing_url=request.url,
            )
        except Exception as e:
            logger.warning(f"AI report generation failed for listing: {e}")
            # Non-fatal

    # 5. Assess price
    price_assessment = _assess_price(listing_data.price_pence, free_check)

    logger.info(
        f"Listing check completed: platform={listing_data.platform}, "
        f"demo={listing_data.demo_mode}, reg={registration}, "
        f"free_check={'yes' if free_check else 'no'}, "
        f"ai_report={'yes' if ai_report else 'no'}, "
        f"price={price_assessment}"
    )

    return ListingCheckResponse(
        listing=listing_data.to_dict(),
        free_check=free_check,
        ai_report=ai_report,
        price_assessment=price_assessment,
    )
