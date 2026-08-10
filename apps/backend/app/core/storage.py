import logging
import os
from abc import ABC, abstractmethod
from pathlib import Path

import aioboto3

from app.core.config import settings

logger = logging.getLogger(__name__)


class StorageProvider(ABC):
    @abstractmethod
    async def create_upload_url(self, object_key: str, mime_type: str, expires_in: int = 3600) -> str:
        pass

    @abstractmethod
    async def create_download_url(self, object_key: str, expires_in: int = 3600) -> str:
        pass

    @abstractmethod
    async def delete_object(self, object_key: str) -> bool:
        pass


class LocalStorageProvider(StorageProvider):
    """
    Stores files on the local filesystem under settings.LOCAL_STORAGE_DIR.
    Upload/download URLs point to the local FastAPI endpoints at /local-storage/*.
    Only intended for development/testing — never use in production.
    """

    def __init__(self):
        self.base_dir = Path(settings.LOCAL_STORAGE_DIR)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _local_url(self, path: str) -> str:
        # Strip leading slash if present so the URL is clean
        key = path.lstrip("/")
        return f"http://127.0.0.1:8000/local-storage/files/{key}"

    async def create_upload_url(self, object_key: str, mime_type: str, expires_in: int = 3600) -> str:
        # The upload endpoint accepts a PUT with raw bytes
        key = object_key.lstrip("/")
        return f"http://127.0.0.1:8000/local-storage/upload/{key}"

    async def create_download_url(self, object_key: str, expires_in: int = 3600) -> str:
        key = object_key.lstrip("/")
        return f"http://127.0.0.1:8000/local-storage/files/{key}"

    async def delete_object(self, object_key: str) -> bool:
        key = object_key.lstrip("/")
        target = self.base_dir / key
        try:
            if target.exists():
                target.unlink()
            return True
        except Exception as e:
            logger.error(f"LocalStorageProvider: failed to delete {target}: {e}")
            return False

    def local_path(self, object_key: str) -> Path:
        """Resolve the absolute filesystem path for a given object key."""
        key = object_key.lstrip("/")
        return self.base_dir / key


class R2StorageProvider(StorageProvider):
    def __init__(self):
        self.session = aioboto3.Session(
            aws_access_key_id=settings.R2_ACCESS_KEY_ID,
            aws_secret_access_key=settings.R2_SECRET_ACCESS_KEY,
            region_name="auto",
        )
        self.bucket = settings.R2_BUCKET_NAME
        self.endpoint_url = settings.r2_endpoint_url

    async def create_upload_url(self, object_key: str, mime_type: str, expires_in: int = 3600) -> str:
        async with self.session.client("s3", endpoint_url=self.endpoint_url) as client:
            url = await client.generate_presigned_url(
                ClientMethod="put_object",
                Params={
                    "Bucket": self.bucket,
                    "Key": object_key,
                    "ContentType": mime_type,
                },
                ExpiresIn=expires_in,
            )
            return url

    async def create_download_url(self, object_key: str, expires_in: int = 3600) -> str:
        async with self.session.client("s3", endpoint_url=self.endpoint_url) as client:
            url = await client.generate_presigned_url(
                ClientMethod="get_object",
                Params={
                    "Bucket": self.bucket,
                    "Key": object_key,
                },
                ExpiresIn=expires_in,
            )
            return url

    async def delete_object(self, object_key: str) -> bool:
        try:
            async with self.session.client("s3", endpoint_url=self.endpoint_url) as client:
                await client.delete_object(Bucket=self.bucket, Key=object_key)
            return True
        except Exception as e:
            logger.error(f"Failed to delete object {object_key}: {e}")
            return False


def get_storage_provider() -> StorageProvider:
    """
    Factory: return the correct StorageProvider based on STORAGE_PROVIDER env var.
    - "local"  → LocalStorageProvider (dev/test only)
    - "r2"     → R2StorageProvider (production)
    """
    provider = settings.STORAGE_PROVIDER.lower()
    if provider == "local":
        logger.info("StorageProvider: LocalStorageProvider (development mode)")
        return LocalStorageProvider()
    else:
        logger.info("StorageProvider: R2StorageProvider (production mode)")
        return R2StorageProvider()


# Global singleton — selected by configuration
storage: StorageProvider = get_storage_provider()
