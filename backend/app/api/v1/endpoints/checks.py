from fastapi import APIRouter, HTTPException

from app.core.logging import logger
from app.schemas.check import FreeCheckRequest, FreeCheckResponse
from app.services.check.orchestrator import CheckOrchestrator

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
