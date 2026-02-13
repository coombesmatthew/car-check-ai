from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from app.core.logging import logger
from app.schemas.check import FreeCheckRequest, FreeCheckResponse
from app.services.check.orchestrator import CheckOrchestrator
from app.services.ai.report_generator import generate_ai_report

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
