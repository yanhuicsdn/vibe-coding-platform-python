"""
Health check routes
"""

from datetime import datetime

from fastapi import APIRouter

from vibe_coding.models.schema import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        service="backend-controller",
    )
