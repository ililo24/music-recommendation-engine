"""Health check router (API v1)."""

from datetime import datetime, timezone

from fastapi import APIRouter

from musicrec.api.deps import SettingsDep
from musicrec.schemas.health import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check(settings: SettingsDep) -> HealthResponse:
    """Liveness probe returning basic application info."""
    return HealthResponse(
        status="ok",
        version=settings.app_version,
        environment=settings.environment,
        timestamp=datetime.now(timezone.utc),
    )
