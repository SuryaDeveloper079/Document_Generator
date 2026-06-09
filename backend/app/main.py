from contextlib import asynccontextmanager
import structlog
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from app.core.config import settings
from app.api.v1 import api_router
from app.db.database import init_db

log = structlog.get_logger()
limiter = Limiter(key_func=get_remote_address, default_limits=["60/minute"])


@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("startup", env=settings.ENVIRONMENT, version=settings.APP_VERSION)
    if settings.is_development:
        await init_db()
        log.info("db.tables_created")
    yield
    log.info("shutdown")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered documentation generator using Claude.",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)
app.add_middleware(
    CORSMiddleware,
    # allow_origins=settings.get_allowed_origins(),
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api_router)


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok", "version": settings.APP_VERSION}


@app.get("/", tags=["Root"])
async def root():
    return {"name": settings.APP_NAME, "docs": "/docs"}


# @app.exception_handler(Exception)
# async def global_exception_handler(request: Request, exc: Exception):
#     log.error("unhandled_exception", path=request.url.path, error=str(exc))
#     return JSONResponse(status_code=500, content={"detail": str(exc) if settings.is_development else "Internal server error"})

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    log.error("unhandled_exception", path=request.url.path, error=str(exc))
    response = JSONResponse(
        status_code=500,
        content={"detail": str(exc) if settings.is_development else "Internal server error"}
    )
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response
