import logging
from abc import ABC, abstractmethod
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
        if not settings.R2_ACCOUNT_ID:
            # Mock behavior if R2 is not configured
            return f"http://mock.r2/upload/{object_key}"
            
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
        if not settings.R2_ACCOUNT_ID:
            return f"http://mock.r2/download/{object_key}"

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
        if not settings.R2_ACCOUNT_ID:
            return True
            
        try:
            async with self.session.client("s3", endpoint_url=self.endpoint_url) as client:
                await client.delete_object(Bucket=self.bucket, Key=object_key)
            return True
        except Exception as e:
            logger.error(f"Failed to delete object {object_key}: {e}")
            return False


# Global instance
storage = R2StorageProvider()
