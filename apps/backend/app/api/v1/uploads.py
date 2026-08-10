import uuid
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.db.session import get_db
from app.models.models import User, Upload, ShareLink, UsageRecord
from app.schemas.schemas import (
    UploadRequest, UploadRequestResponse, UploadResponse, 
    UploadListResponse, ShareLinkResponse, ErrorResponse
)
from app.api.deps import get_current_user
from app.core.config import settings
from app.core.security import sanitize_filename
from app.core.storage import storage

router = APIRouter(tags=["uploads"])


@router.post(
    "/uploads/request",
    response_model=UploadRequestResponse,
    status_code=status.HTTP_201_CREATED,
    responses={400: {"model": ErrorResponse}, 403: {"model": ErrorResponse}},
)
async def request_upload(
    body: UploadRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Validate size
    if body.size > settings.MAX_FILE_SIZE_BYTES:
        raise HTTPException(status_code=400, detail="File size exceeds maximum allowed")

    # Check monthly quota
    current_month = datetime.now(timezone.utc).strftime("%Y-%m")
    usage_result = await db.execute(
        select(UsageRecord).where(UsageRecord.user_id == user.id, UsageRecord.month == current_month)
    )
    usage = usage_result.scalar_one_or_none()
    
    if not usage:
        usage = UsageRecord(user_id=user.id, month=current_month)
        db.add(usage)
        await db.flush()
        
    if usage.upload_count >= settings.MAX_MONTHLY_UPLOADS:
        raise HTTPException(status_code=403, detail="Monthly upload quota exceeded")
        
    # Check storage quota
    storage_result = await db.execute(
        select(func.coalesce(func.sum(Upload.size), 0))
        .where(Upload.user_id == user.id, Upload.status != "deleted")
    )
    storage_used = storage_result.scalar() or 0
    if storage_used + body.size > settings.MAX_STORAGE_PER_USER_BYTES:
        raise HTTPException(status_code=403, detail="Storage quota exceeded")

    # Validate MIME type against allowlist to prevent dangerous file type injection
    if body.mime_type not in settings.ALLOWED_MIME_TYPES:
        raise HTTPException(status_code=400, detail="File type not allowed")

    sanitized_filename = sanitize_filename(body.filename)
    object_id = str(uuid.uuid4())
    storage_key = f"users/{user.id}/objects/{object_id}"

    # Generate presigned URL (short-lived: 5 minutes)
    upload_url = await storage.create_upload_url(storage_key, body.mime_type, expires_in=300)

    upload = Upload(
        user_id=user.id,
        filename=sanitized_filename,
        original_filename=body.filename,
        size=body.size,
        mime_type=body.mime_type,
        storage_key=storage_key,
        status="pending",
    )
    db.add(upload)
    
    # Increment usage count immediately to prevent race condition abuse
    usage.upload_count += 1
    usage.bytes_uploaded += body.size
    
    await db.commit()

    return UploadRequestResponse(upload_id=upload.id, upload_url=upload_url)


@router.post(
    "/uploads/{upload_id}/complete",
    response_model=ShareLinkResponse,
    status_code=status.HTTP_201_CREATED,
    responses={404: {"model": ErrorResponse}, 400: {"model": ErrorResponse}},
)
async def complete_upload(
    upload_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Upload).where(Upload.id == upload_id, Upload.user_id == user.id)
    )
    upload = result.scalar_one_or_none()
    if not upload:
        raise HTTPException(status_code=404, detail="Upload not found")
        
    if upload.status != "pending":
        raise HTTPException(status_code=400, detail="Upload is not pending")

    upload.status = "uploaded"
    
    # Create share link
    token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(hours=settings.DEFAULT_EXPIRATION_HOURS)
    
    share_link = ShareLink(
        upload_id=upload.id,
        token=token,
        expires_at=expires_at,
    )
    db.add(share_link)
    await db.commit()
    
    return ShareLinkResponse.model_validate(share_link)


@router.get("/uploads", response_model=UploadListResponse)
async def list_uploads(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 50,
):
    result = await db.execute(
        select(Upload)
        .where(Upload.user_id == user.id, Upload.status != "deleted")
        .order_by(Upload.created_at.desc())
        .offset(skip)
        .limit(min(limit, 100))  # Clamp to prevent memory exhaustion
    )
    uploads = result.scalars().all()

    count_result = await db.execute(
        select(func.count())
        .select_from(Upload)
        .where(Upload.user_id == user.id, Upload.status != "deleted")
    )
    total = count_result.scalar() or 0

    return UploadListResponse(
        items=[UploadResponse.model_validate(u) for u in uploads],
        total=total,
    )


@router.get(
    "/uploads/{upload_id}",
    response_model=UploadResponse,
    responses={404: {"model": ErrorResponse}},
)
async def get_upload(
    upload_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Upload).where(Upload.id == upload_id, Upload.user_id == user.id)
    )
    upload = result.scalar_one_or_none()
    if not upload:
        raise HTTPException(status_code=404, detail="Upload not found")
    return UploadResponse.model_validate(upload)


@router.delete("/uploads/{upload_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_upload(
    upload_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Upload).where(Upload.id == upload_id, Upload.user_id == user.id)
    )
    upload = result.scalar_one_or_none()
    if not upload:
        raise HTTPException(status_code=404, detail="Upload not found")
    upload.status = "deleted"
    await db.commit()


@router.get(
    "/shares/{share_id}",
    response_model=ShareLinkResponse,
    responses={404: {"model": ErrorResponse}},
)
async def get_share(
    share_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ShareLink)
        .join(Upload)
        .where(ShareLink.id == share_id, Upload.user_id == user.id)
    )
    share = result.scalar_one_or_none()
    if not share:
        raise HTTPException(status_code=404, detail="Share link not found")
    return ShareLinkResponse.model_validate(share)


@router.delete("/shares/{share_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_share(
    share_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ShareLink)
        .join(Upload)
        .where(ShareLink.id == share_id, Upload.user_id == user.id)
    )
    share = result.scalar_one_or_none()
    if not share:
        raise HTTPException(status_code=404, detail="Share link not found")
    share.is_active = False
    await db.commit()
