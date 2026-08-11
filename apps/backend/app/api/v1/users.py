from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.db.session import get_db
from app.models.models import User, Upload, UsageRecord, ShareLink
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


@router.get("/me/shares")
async def get_user_shares(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ShareLink, Upload)
        .join(Upload, ShareLink.upload_id == Upload.id)
        .where(Upload.user_id == user.id, Upload.status != "deleted")
        .order_by(ShareLink.created_at.desc())
        .limit(50)
    )

    shares = []
    for share, upload in result.all():
        shares.append({
            "id": share.id,
            "filename": upload.filename,
            "type": "image" if upload.mime_type.startswith("image/") else "file",
            "size": upload.size,
            "url": f"http://127.0.0.1:8000/s/{share.token}",
            "createdAt": share.created_at.isoformat(),
            "expiresAt": share.expires_at.isoformat() if share.expires_at else None,
            "views": share.views,
            "status": "active" if share.is_active else "deleted",
        })

    return shares
