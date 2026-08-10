"""
Local storage router — only active when STORAGE_PROVIDER=local.

Provides two endpoints:
  PUT  /local-storage/upload/{path:key}  — receive raw bytes, save to disk
  GET  /local-storage/files/{path:key}   — stream file from disk

These endpoints replace presigned R2 URLs in development/test mode.
The desktop app's Tauri upload command (upload_file_to_r2) performs a raw
HTTP PUT, so it works transparently with either R2 or this local endpoint.
"""
import mimetypes
import os
from pathlib import Path

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse, Response

from app.core.config import settings

router = APIRouter(prefix="/local-storage", tags=["local-storage"])

_storage_base = Path(settings.LOCAL_STORAGE_DIR)


def _resolve(key: str) -> Path:
    """Safely resolve an object key to an absolute path under the storage root."""
    # Prevent path traversal
    storage_base = _storage_base.resolve()
    target = (storage_base / key).resolve()
    if not str(target).startswith(str(storage_base)):
        raise HTTPException(status_code=400, detail="Invalid storage key")
    return target


@router.put("/upload/{key:path}", status_code=200)
async def local_upload(key: str, request: Request):
    """
    Accept a raw PUT upload and save the body to disk.
    The Tauri upload_file_to_r2 command performs a plain HTTP PUT with the
    file bytes as the request body, exactly matching what R2 presigned URLs expect.
    """
    target = _resolve(key)
    target.parent.mkdir(parents=True, exist_ok=True)

    # Write atomically: collect body bytes, then write + rename
    tmp_path = target.with_suffix(target.suffix + ".tmp")
    try:
        body = await request.body()
        tmp_path.write_bytes(body)
        os.replace(tmp_path, target)
    except Exception as e:
        if tmp_path.exists():
            tmp_path.unlink(missing_ok=True)
        raise HTTPException(status_code=500, detail=f"Failed to save file: {e}")

    return Response(status_code=200)


@router.get("/files/{key:path}")
async def local_download(key: str):
    """Stream a stored file back to the caller with the correct MIME type."""
    target = _resolve(key)
    if not target.exists() or not target.is_file():
        raise HTTPException(status_code=404, detail="File not found")

    media_type, _ = mimetypes.guess_type(str(target))
    media_type = media_type or "application/octet-stream"

    return FileResponse(
        path=str(target),
        media_type=media_type,
        filename=target.name,
    )
