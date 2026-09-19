


from fastapi import APIRouter

from app.core.config import get_settings
from app.schemas.system import HealthResponse


router = APIRouter(tags=["System"])

@router.get("/")
async def root():
    return {
        "message":"Smart Travel Agent API is running.",
        "documentation":"/docs"
    }


@router.get("/health", response_model=HealthResponse)
async def health():
    settings = get_settings()

    return HealthResponse(
        status="ok",
        app_name=settings.app_name,
        version=settings.app_version
    )