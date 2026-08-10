from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.db.session import get_db
from app.models.models import User, Upload, UsageRecord
from app.schemas.schemas import UserResponse, UserProfileResponse
from app.api.deps import get_current_user
from app.core.config import settings

router = APIRouter(tags=["users"])


@router.get("/me", response_model=UserProfileResponse)
async def get_profile(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Calculate storage used
    result = await db.execute(
        select(func.coalesce(func.sum(Upload.size), 0))
        .where(Upload.user_id == user.id, Upload.status != "deleted")
    )
    storage_used = result.scalar() or 0

    # Get current month upload count
    from datetime import datetime, timezone
    current_month = datetime.now(timezone.utc).strftime("%Y-%m")
    result = await db.execute(
        select(UsageRecord.upload_count)
        .where(UsageRecord.user_id == user.id, UsageRecord.month == current_month)
    )
    monthly_uploads = result.scalar() or 0

    return UserProfileResponse(
        user=UserResponse.model_validate(user),
        storage_used=storage_used,
        storage_limit=settings.MAX_STORAGE_PER_USER_BYTES,
        monthly_uploads=monthly_uploads,
        monthly_limit=settings.MAX_MONTHLY_UPLOADS,
    )
