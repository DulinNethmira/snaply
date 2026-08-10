import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "Snaply Backend"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = False

    # Environment: "development" or "production"
    SNAPLY_ENV: str = "production"

    # SECURITY: No default — app MUST NOT start without a real secret
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60  # 1 hour; refresh flow extends sessions
    
    # SQLite
    SQLALCHEMY_DATABASE_URI: str = "sqlite+aiosqlite:///./snaply.db"

    # CORS — MUST be explicitly configured; never default to wildcard
    BACKEND_CORS_ORIGINS: List[str] = []

    # Resource Limits for VPS constraints
    MAX_FILE_SIZE_BYTES: int = 100 * 1024 * 1024  # 100MB
    MAX_STORAGE_PER_USER_BYTES: int = 1 * 1024 * 1024 * 1024  # 1GB
    MAX_MONTHLY_UPLOADS: int = 500
    DEFAULT_EXPIRATION_HOURS: int = 24

    # Storage provider: "local" or "r2"
    STORAGE_PROVIDER: str = "r2"

    # Local storage directory (used only when STORAGE_PROVIDER=local)
    LOCAL_STORAGE_DIR: str = "data/storage"

    # Cloudflare R2
    R2_ACCOUNT_ID: str = ""
    R2_ACCESS_KEY_ID: str = ""
    R2_SECRET_ACCESS_KEY: str = ""
    R2_BUCKET_NAME: str = "snaply"

    # Upload security
    ALLOWED_MIME_TYPES: List[str] = [
        "image/png", "image/jpeg", "image/gif", "image/webp",
        "video/mp4", "video/webm",
        "application/pdf",
        "application/zip", "application/x-7z-compressed", "application/gzip",
        "text/plain", "text/csv",
        "application/octet-stream",
    ]
    
    @property
    def r2_endpoint_url(self) -> str:
        return f"https://{self.R2_ACCOUNT_ID}.r2.cloudflarestorage.com"

    model_config = SettingsConfigDict(case_sensitive=True, env_file=".env")

settings = Settings()

