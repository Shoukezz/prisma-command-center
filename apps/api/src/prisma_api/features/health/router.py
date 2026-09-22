from fastapi import APIRouter

from prisma_api.core.config import get_settings
from prisma_api.features.health.schemas import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    settings = get_settings()
    return HealthResponse(status="ok", environment=settings.environment)
