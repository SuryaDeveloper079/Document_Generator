from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool
from app.core.config import settings


class Base(DeclarativeBase):
    pass

def create_engine() -> AsyncEngine:
    kwargs: dict = {"echo": settings.DEBUG, "future": True}
    if "neon.tech" in settings.DATABASE_URL:
        kwargs["poolclass"] = NullPool
    else:
        kwargs["pool_size"] = 5
        kwargs["max_overflow"] = 10
        kwargs["pool_pre_ping"] = True
    return create_async_engine(settings.DATABASE_URL, **kwargs)

engine: AsyncEngine = create_engine()

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
