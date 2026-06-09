from functools import lru_cache
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    APP_NAME: str = "AI Doc Generator"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    DATABASE_URL: str
    DATABASE_URL_SYNC: str

    REDIS_URL: str
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str

    ANTHROPIC_API_KEY: str
    CLAUDE_MODEL: str = "claude-sonnet-4-20250514"
    CLAUDE_MAX_TOKENS: int = 4096

    S3_ENDPOINT_URL: Optional[str] = None
    S3_ACCESS_KEY_ID: Optional[str] = None
    S3_SECRET_ACCESS_KEY: Optional[str] = None
    S3_BUCKET_NAME: str = "ai-doc-generator"
    S3_REGION: str = "auto"

    NODE_SERVICE_URL: str = "http://localhost:3001"
    NODE_SERVICE_API_KEY: str = "node-service-internal-key"

    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_AI_PER_DAY: int = 100

    ALLOWED_ORIGINS: str = "http://localhost:3000"

    def get_allowed_origins(self) -> List[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",")]

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"

    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT == "development"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
