from fastapi import APIRouter
from sqlalchemy import text
from app.db.session import async_session_factory
from app.schemas.schemas import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(status="ok")


@router.get("/health/ready", response_model=HealthResponse)
async def health_ready():
    """Deep health check that verifies database connectivity."""
    try:
        async with async_session_factory() as session:
            await session.execute(text("SELECT 1"))
        return HealthResponse(status="ok")
    except Exception:
        return HealthResponse(status="degraded")
