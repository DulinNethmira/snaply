from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


# ── Auth ──
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    token: str


class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8, max_length=128)


# ── User ──
class UserResponse(BaseModel):
    id: str
    email: str
    created_at: datetime

    model_config = {"from_attributes": True}


class UserProfileResponse(BaseModel):
    user: UserResponse
    storage_used: int
    storage_limit: int
    monthly_uploads: int
    monthly_limit: int


# ── Uploads ──
class UploadRequest(BaseModel):
    filename: str = Field(min_length=1, max_length=255)
    size: int = Field(gt=0)
    mime_type: str = Field(min_length=3, max_length=127, pattern=r'^[a-z]+/[a-z0-9.+\-]+$')


class UploadRequestResponse(BaseModel):
    upload_id: str
    upload_url: str


class UploadResponse(BaseModel):
    id: str
    filename: str
    original_filename: str
    size: int
    mime_type: str
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class UploadListResponse(BaseModel):
    items: list[UploadResponse]
    total: int


# ── Shares ──
class ShareLinkResponse(BaseModel):
    id: str
    upload_id: str
    token: str
    expires_at: Optional[datetime]
    views: int
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class ShareLinkDownloadResponse(BaseModel):
    download_url: str
    filename: str
    size: int
    mime_type: str


# ── Usage ──
class UsageResponse(BaseModel):
    month: str
    bytes_uploaded: int
    upload_count: int

    model_config = {"from_attributes": True}


# ── Health ──
class HealthResponse(BaseModel):
    status: str
    version: str = "0.1.0"


# ── Error ──
class ErrorResponse(BaseModel):
    detail: str
