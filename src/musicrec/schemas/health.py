"""Health check response schema."""

from datetime import datetime

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Response body for ``GET /api/v1/health``."""

    status: str
    version: str
    environment: str
    timestamp: datetime
