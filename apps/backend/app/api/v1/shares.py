from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.models.models import ShareLink, Upload
from app.schemas.schemas import ShareLinkDownloadResponse, ErrorResponse
from app.core.storage import storage

router = APIRouter(tags=["shares"])

@router.get(
    "/shares/{token}/download",
    response_model=ShareLinkDownloadResponse,
    responses={404: {"model": ErrorResponse}, 410: {"model": ErrorResponse}},
)
async def download_share(
    token: str,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ShareLink)
        .join(Upload)
        .where(ShareLink.token == token)
    )
    share = result.scalar_one_or_none()
    
    if not share or not share.is_active:
        raise HTTPException(status_code=404, detail="Share link not found")
        
    if share.expires_at and share.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        raise HTTPException(status_code=410, detail="Share link has expired")
        
    upload = await share.awaitable_attrs.upload
    
    if upload.status != "uploaded":
        raise HTTPException(status_code=404, detail="Upload is not available")
        
    # Increment view count
    share.views += 1
    await db.commit()
    
    # Generate presigned download URL
    download_url = await storage.create_download_url(upload.storage_key)
    
    return ShareLinkDownloadResponse(
        download_url=download_url,
        filename=upload.filename,
        size=upload.size,
        mime_type=upload.mime_type,
    )
