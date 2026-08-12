from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status, BackgroundTasks
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
import httpx
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.db.session import get_db
from app.core.security import hash_password, verify_password, create_access_token
from app.core.config import settings
from app.models.models import User, Session, Upload
from app.schemas.schemas import (
    RegisterRequest, LoginRequest, TokenResponse, RefreshRequest,
    PasswordChangeRequest, ErrorResponse,
)
from app.api.deps import get_current_user
from app.core.storage import storage
from app.core.email import send_welcome_email

router = APIRouter(prefix="/auth", tags=["auth"])
limiter = Limiter(key_func=get_remote_address)


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    responses={409: {"model": ErrorResponse}},
)
@limiter.limit("5/minute")
async def register(request: Request, body: RegisterRequest, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    # Check if email already exists
    result = await db.execute(select(User).where(User.email == body.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Email already registered")

    user = User(
        email=body.email,
        password_hash=hash_password(body.password),
    )
    db.add(user)
    await db.flush()

    token = create_access_token(user.id)
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    session = Session(user_id=user.id, token=token, expires_at=expires_at)
    db.add(session)
    await db.commit()

    # Send welcome email asynchronously
    background_tasks.add_task(send_welcome_email, user.email)

    return TokenResponse(access_token=token)


@router.post(
    "/login",
    response_model=TokenResponse,
    responses={401: {"model": ErrorResponse}},
)
@limiter.limit("5/minute")
async def login(request: Request, body: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == body.email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token(user.id)
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    session = Session(user_id=user.id, token=token, expires_at=expires_at)
    db.add(session)
    await db.commit()

    return TokenResponse(access_token=token)


@router.post(
    "/refresh",
    response_model=TokenResponse,
    responses={401: {"model": ErrorResponse}},
)
async def refresh(body: RefreshRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Session).where(Session.token == body.token))
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=401, detail="Invalid session")
    if session.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        await db.delete(session)
        await db.commit()
        raise HTTPException(status_code=401, detail="Session expired")

    # Issue new token
    new_token = create_access_token(session.user_id)
    new_expires = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    # Replace old session (token rotation)
    await db.delete(session)
    new_session = Session(user_id=session.user_id, token=new_token, expires_at=new_expires)
    db.add(new_session)
    await db.commit()

    return TokenResponse(access_token=new_token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await db.execute(delete(Session).where(Session.user_id == user.id))
    await db.commit()


@router.post(
    "/password",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={401: {"model": ErrorResponse}},
)
@limiter.limit("3/minute")
async def change_password(
    request: Request,
    body: PasswordChangeRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not verify_password(body.current_password, user.password_hash):
        raise HTTPException(status_code=401, detail="Current password is incorrect")

    user.password_hash = hash_password(body.new_password)
    # Invalidate all sessions on password change
    await db.execute(delete(Session).where(Session.user_id == user.id))
    await db.commit()


@router.delete("/account", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Delete all R2 objects before removing the user record
    result = await db.execute(
        select(Upload).where(Upload.user_id == user.id, Upload.status != "deleted")
    )
    uploads = result.scalars().all()
    for upload in uploads:
        await storage.delete_object(upload.storage_key)

    await db.delete(user)
    await db.commit()


# --- Google OAuth ---
GOOGLE_AUTHORIZATION_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"

@router.get("/google/login")
async def google_login(request: Request):
    if not settings.GOOGLE_CLIENT_ID:
        raise HTTPException(status_code=500, detail="Google OAuth not configured")
    
    redirect_uri = request.url_for("google_callback")
    scope = "openid email profile"
    
    auth_url = f"{GOOGLE_AUTHORIZATION_URL}?client_id={settings.GOOGLE_CLIENT_ID}&response_type=code&redirect_uri={redirect_uri}&scope={scope}&access_type=offline"
    return RedirectResponse(auth_url)

@router.get("/google/callback")
async def google_callback(request: Request, code: str, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
        raise HTTPException(status_code=500, detail="Google OAuth not configured")
    
    redirect_uri = request.url_for("google_callback")
    
    # Exchange code for token
    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            GOOGLE_TOKEN_URL,
            data={
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": str(redirect_uri),
            }
        )
        if not token_response.is_success:
            raise HTTPException(status_code=400, detail="Failed to get token from Google")
        
        token_data = token_response.json()
        access_token = token_data.get("access_token")
        
        # Get user info
        userinfo_response = await client.get(
            GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {access_token}"}
        )
        if not userinfo_response.is_success:
            raise HTTPException(status_code=400, detail="Failed to get user info from Google")
            
        user_info = userinfo_response.json()
        email = user_info.get("email")
        if not email:
            raise HTTPException(status_code=400, detail="Google account has no email")
            
        # Find or create user
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        
        if not user:
            # Create user (random password since they log in via Google)
            import secrets
            user = User(
                email=email,
                password_hash=hash_password(secrets.token_urlsafe(32)),
            )
            db.add(user)
            await db.flush()
            background_tasks.add_task(send_welcome_email, email)
            
        # Create session
        token = create_access_token(user.id)
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        session = Session(user_id=user.id, token=token, expires_at=expires_at)
        db.add(session)
        await db.commit()
        
        # Redirect to deep link to open the app with the token
        # If deep linking fails, the user will see a fallback page.
        fallback_html = f\"\"\"
        <html>
            <head><title>Snaply Authentication</title></head>
            <body style="font-family: sans-serif; text-align: center; padding-top: 50px; background-color: #070B0F; color: #EEF7FA;">
                <h2>Login Successful!</h2>
                <p>Opening Snaply app...</p>
                <div style="margin-top: 20px; font-size: 14px; color: #9CAAB2;">
                    If the app didn't open automatically, copy this code and paste it into Snaply:
                </div>
                <div style="margin: 20px auto; padding: 10px; background: #0E141B; border: 1px solid #24C8DB; display: inline-block; border-radius: 5px; font-family: monospace;">
                    {token}
                </div>
                <script>
                    window.location.href = 'snaply://auth?token={token}';
                </script>
            </body>
        </html>
        \"\"\"
        from fastapi.responses import HTMLResponse
        return HTMLResponse(content=fallback_html)
