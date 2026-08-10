import os
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.models.models import ShareLink, Upload
from app.core.storage import storage
from app.core.security import verify_password

# share_pages.py lives at app/api/v1/ — go up 3 levels to reach app/
TEMPLATES_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "templates"
)
templates = Jinja2Templates(directory=TEMPLATES_DIR)

router = APIRouter()


def _human_size(size_bytes: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def _file_type(mime: str) -> str:
    if mime.startswith("image/"):
        return "image"
    if mime.startswith("video/"):
        return "video"
    if mime.startswith("text/") or mime in (
        "application/json",
        "application/xml",
        "application/javascript",
    ):
        return "text"
    return "generic"


async def _get_share_and_upload(token: str, db: AsyncSession):
    """Fetch share + upload or return (None, None, error_context)."""
    result = await db.execute(
        select(ShareLink).join(Upload).where(ShareLink.token == token)
    )
    share = result.scalar_one_or_none()

    if not share or not share.is_active:
        return None, None, {
            "icon": "🔍",
            "title": "Not Found",
            "message": "This share link doesn't exist or has been revoked.",
        }

    if share.expires_at:
        exp = share.expires_at
        if exp.tzinfo is None:
            exp = exp.replace(tzinfo=timezone.utc)
        if exp < datetime.now(timezone.utc):
            return None, None, {
                "icon": "⏰",
                "title": "Link Expired",
                "message": "This share link has expired and is no longer available.",
            }

    upload = await share.awaitable_attrs.upload

    if upload.status != "uploaded":
        return None, None, {
            "icon": "🚫",
            "title": "Unavailable",
            "message": "This file is no longer available.",
        }

    return share, upload, None


@router.get("/s/{token}", response_class=HTMLResponse)
async def share_page(
    request: Request,
    token: str,
    db: AsyncSession = Depends(get_db),
):
    share, upload, error_ctx = await _get_share_and_upload(token, db)

    if error_ctx:
        return templates.TemplateResponse(
            request, "error.html", error_ctx, status_code=404
        )

    # Password check
    if share.password_hash:
        return templates.TemplateResponse(
            request, "password.html", {"token": token, "error": None}
        )

    return await _render_share(request, share, upload, db)


@router.post("/s/{token}", response_class=HTMLResponse)
async def share_page_password(
    request: Request,
    token: str,
    password: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    share, upload, error_ctx = await _get_share_and_upload(token, db)

    if error_ctx:
        return templates.TemplateResponse(
            request, "error.html", error_ctx, status_code=404
        )

    if not share.password_hash or not verify_password(password, share.password_hash):
        return templates.TemplateResponse(
            request, "password.html", {"token": token, "error": "Incorrect password."}
        )

    return await _render_share(request, share, upload, db)


async def _render_share(
    request: Request,
    share: ShareLink,
    upload: Upload,
    db: AsyncSession,
):
    share.views += 1
    await db.commit()

    file_type = _file_type(upload.mime_type)
    download_url = await storage.create_download_url(upload.storage_key)

    # For images and videos, the media URL is the same presigned URL
    media_url = download_url if file_type in ("image", "video") else None
    preview_url = download_url if file_type == "image" else None

    # For text, we don't inline it from R2 in this phase (would require fetching)
    text_content = None

    expires_at_str = None
    if share.expires_at:
        exp = share.expires_at
        if exp.tzinfo is None:
            exp = exp.replace(tzinfo=timezone.utc)
        expires_at_str = exp.strftime("%b %d, %Y at %H:%M UTC")

    return templates.TemplateResponse(
        request,
        "share.html",
        {
            "filename": upload.filename,
            "mime_type": upload.mime_type,
            "file_type": file_type,
            "file_size_human": _human_size(upload.size),
            "download_url": download_url,
            "media_url": media_url,
            "preview_url": preview_url,
            "text_content": text_content,
            "expires_at": expires_at_str,
        },
    )
