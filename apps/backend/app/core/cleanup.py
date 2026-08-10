import asyncio
import logging
from datetime import datetime, timezone
from sqlalchemy import select

from app.db.session import async_session_factory
from app.models.models import ShareLink, Upload
from app.core.storage import storage

logger = logging.getLogger(__name__)

async def cleanup_expired_objects_loop():
    logger.info("Starting background cleanup loop...")
    while True:
        try:
            await asyncio.sleep(60 * 5)  # Check every 5 minutes
            logger.info("Running expired objects cleanup...")
            
            async with async_session_factory() as db:
                # Find expired share links
                now = datetime.now(timezone.utc)
                
                # Fetch shares that are expired but still marked as active
                result = await db.execute(
                    select(ShareLink)
                    .where(ShareLink.is_active)
                    .where(ShareLink.expires_at < now)
                    .limit(100)
                )
                expired_shares = result.scalars().all()
                
                for share in expired_shares:
                    share.is_active = False
                    
                    # Also mark the upload as deleted to free up quota
                    # and delete it from R2 storage
                    upload = await share.awaitable_attrs.upload
                    if upload and upload.status != "deleted":
                        upload.status = "deleted"
                        await storage.delete_object(upload.storage_key)
                        
                if expired_shares:
                    logger.info(f"Cleaned up {len(expired_shares)} expired shares.")
                    await db.commit()
                    
                # Find orphaned uploads (pending for more than 2 hours)
                # This catches uploads that requested a URL but never called /complete
                import datetime as dt
                two_hours_ago_dt = dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=2)
                
                result = await db.execute(
                    select(Upload)
                    .where(Upload.status == "pending")
                    .where(Upload.created_at < two_hours_ago_dt)
                    .limit(100)
                )
                orphaned_uploads = result.scalars().all()
                
                for upload in orphaned_uploads:
                    upload.status = "deleted"
                    # Also attempt to delete from R2 just in case some bytes were uploaded
                    await storage.delete_object(upload.storage_key)
                    
                if orphaned_uploads:
                    logger.info(f"Cleaned up {len(orphaned_uploads)} orphaned uploads.")
                    await db.commit()
                    
        except asyncio.CancelledError:
            logger.info("Cleanup loop cancelled.")
            break
        except Exception as e:
            logger.error(f"Error in cleanup loop: {e}")
