from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.models.models import User, UsageRecord
from app.schemas.schemas import UsageResponse
from app.api.deps import get_current_user

router = APIRouter(tags=["usage"])


@router.get("/usage", response_model=list[UsageResponse])
async def get_usage(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(UsageRecord)
        .where(UsageRecord.user_id == user.id)
        .order_by(UsageRecord.month.desc())
        .limit(12)
    )
    records = result.scalars().all()
    return [UsageResponse.model_validate(r) for r in records]
