from fastapi import APIRouter

from app.api.v1.endpoints import admin, checks, content, ev

api_router = APIRouter()
api_router.include_router(checks.router, prefix="/checks", tags=["checks"])
api_router.include_router(content.router, prefix="/content", tags=["content"])
api_router.include_router(ev.router, prefix="/ev", tags=["ev"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
