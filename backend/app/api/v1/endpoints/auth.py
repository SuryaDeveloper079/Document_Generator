from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.schemas.schemas import UserRegister, UserLogin, TokenResponse, RefreshRequest, UserOut, MessageResponse
from app.services.user_service import AuthService, get_current_user
from app.models.models import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(data: UserRegister, db: AsyncSession = Depends(get_db)):
    svc = AuthService(db)
    user = await svc.register(data)
    await db.commit()
    await db.refresh(user)
    return user


@router.post("/login", response_model=TokenResponse)
async def login(data: UserLogin, db: AsyncSession = Depends(get_db)):
    svc = AuthService(db)
    tokens = await svc.login(data)
    await db.commit()
    return tokens


@router.post("/refresh", response_model=TokenResponse)
async def refresh(data: RefreshRequest, db: AsyncSession = Depends(get_db)):
    svc = AuthService(db)
    tokens = await svc.refresh_tokens(data.refresh_token)
    await db.commit()
    return tokens


@router.get("/me", response_model=UserOut)
async def me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/logout", response_model=MessageResponse)
async def logout(current_user: User = Depends(get_current_user)):
    return {"message": "Logged out successfully"}
