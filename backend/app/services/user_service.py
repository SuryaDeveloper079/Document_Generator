from datetime import datetime, timedelta, timezone
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from fastapi import HTTPException, status, Depends
from app.db.database import get_db
from app.models.models import User, RefreshToken
from app.schemas.schemas import UserRegister, UserLogin
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token, get_token_from_request
from app.core.config import settings
import structlog

log = structlog.get_logger()


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def register(self, data: UserRegister) -> User:
        existing = await self.db.execute(
            select(User).where((User.email == data.email) | (User.username == data.username))
        )
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email or username already registered")
        user = User(
            email=data.email,
            username=data.username,
            hashed_password=hash_password(data.password),
            full_name=data.full_name,
        )
        self.db.add(user)
        await self.db.flush()
        return user

    async def login(self, data: UserLogin) -> dict:
        result = await self.db.execute(select(User).where(User.email == data.email))
        user = result.scalar_one_or_none()
        if not user or not user.hashed_password or not verify_password(data.password, user.hashed_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is disabled")
        return await self._issue_tokens(user)

    async def refresh_tokens(self, refresh_token: str) -> dict:
        payload = decode_token(refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")
        result = await self.db.execute(
            select(RefreshToken).where(RefreshToken.token == refresh_token, RefreshToken.revoked == False)
        )
        rt = result.scalar_one_or_none()
        if not rt or rt.expires_at < datetime.now(timezone.utc):
            raise HTTPException(status_code=401, detail="Refresh token expired or revoked")
        rt.revoked = True
        user_result = await self.db.execute(select(User).where(User.id == payload["sub"]))
        user = user_result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return await self._issue_tokens(user)

    async def _issue_tokens(self, user: User) -> dict:
        payload = {"sub": user.id, "email": user.email}
        access = create_access_token(payload)
        refresh = create_refresh_token(payload)
        rt = RefreshToken(
            user_id=user.id,
            token=refresh,
            expires_at=datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        )
        self.db.add(rt)
        return {
            "access_token": access,
            "refresh_token": refresh,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        }

    async def get_current_user(self, token: str) -> User:
        payload = decode_token(token)
        result = await self.db.execute(select(User).where(User.id == payload["sub"]))
        user = result.scalar_one_or_none()
        if not user or not user.is_active:
            raise HTTPException(status_code=401, detail="User not found or inactive")
        return user

    async def check_ai_quota(self, user: User) -> None:
        now = datetime.now(timezone.utc)
        if user.ai_calls_reset_at.date() < now.date():
            await self.db.execute(update(User).where(User.id == user.id).values(ai_calls_today=0, ai_calls_reset_at=now))
            user.ai_calls_today = 0
        limit = 100 if user.plan == "free" else 500
        if user.ai_calls_today >= limit:
            raise HTTPException(status_code=429, detail=f"Daily AI limit ({limit}) reached")

    async def increment_ai_calls(self, user: User) -> None:
        await self.db.execute(update(User).where(User.id == user.id).values(ai_calls_today=User.ai_calls_today + 1))


async def get_current_user(
    token: str = Depends(get_token_from_request),
    db: AsyncSession = Depends(get_db),
) -> User:
    svc = AuthService(db)
    return await svc.get_current_user(token)
