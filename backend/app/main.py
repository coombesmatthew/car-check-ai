import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

from app.core.config import settings
from app.core.logging import setup_logging
from app.core.cache import cache
from app.core.middleware import SecurityHeadersMiddleware, RateLimitMiddleware
from app.api.v1.router import api_router
from app.models.api_call import purge_expired_response_bodies

# How often to run the PII purge. Hourly is comfortable — the actual work
# is a single UPDATE targeting an indexed column.
_PII_PURGE_INTERVAL_SECONDS = 3600

# Initialize Sentry (optional)
if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        integrations=[FastApiIntegration()],
        traces_sample_rate=0.1,
    )

# Setup logging
setup_logging()


async def _pii_purge_loop():
    """Background task: purge expired PII from api_calls every hour.

    First run is delayed so it doesn't compete with startup. Exceptions are
    swallowed inside purge_expired_response_bodies so the loop never dies.
    """
    while True:
        try:
            await asyncio.sleep(_PII_PURGE_INTERVAL_SECONDS)
            await purge_expired_response_bodies()
        except asyncio.CancelledError:
            raise
        except Exception as e:
            import logging
            logging.getLogger("carcheck").warning(f"PII purge loop iteration failed: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup — Redis is optional, don't crash if unavailable
    try:
        await cache.connect()
    except Exception as e:
        import logging
        logging.getLogger("carcheck").warning(f"Redis connection failed (non-fatal): {e}")

    # One-off PII sweep at startup (catches anything we slept through).
    try:
        await purge_expired_response_bodies()
    except Exception as e:
        import logging
        logging.getLogger("carcheck").warning(f"Startup PII purge failed (non-fatal): {e}")

    # Hourly sweep thereafter.
    purge_task = asyncio.create_task(_pii_purge_loop())

    yield

    # Shutdown
    purge_task.cancel()
    try:
        await purge_task
    except asyncio.CancelledError:
        pass
    try:
        await cache.close()
    except Exception:
        pass


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered used car analysis using UK government data",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan,
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.ALLOWED_ORIGINS.split(",") if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(SecurityHeadersMiddleware)
if not settings.DEBUG:
    app.add_middleware(
        RateLimitMiddleware,
        requests_per_minute=settings.RATE_LIMIT_PER_MINUTE,
        burst=settings.RATE_LIMIT_BURST,
    )

# Include API routers
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    return {
        "message": "Car Check AI API",
        "version": "1.0.0",
        "status": "operational",
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0",
        "service": "car-check-ai",
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An internal error occurred",
            "type": "internal_error",
        },
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )
