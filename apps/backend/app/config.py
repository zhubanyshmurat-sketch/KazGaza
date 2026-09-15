from functools import lru_cache
from typing import Annotated, List

from pydantic import field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # App
    ENV: str = "production"
    DEBUG: bool = False
    SECRET_KEY: str
    API_V1_PREFIX: str = "/api/v1"

    # Database
    DATABASE_URL: str

    # Redis
    REDIS_URL: str = "redis://redis:6379/0"

    # JWT
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 14
    COOKIE_SECURE: bool = True
    COOKIE_DOMAIN: str | None = None

    # Telegram
    BOT_TOKEN: str
    BOT_INTERNAL_TOKEN: str  # shared secret used by the bot service to call backend

    # CORS
    # NoDecode: these are plain comma-separated strings in .env (not JSON),
    # so pydantic-settings must not try to JSON-decode them itself — the
    # field_validator below does the comma-splitting instead.
    CORS_ORIGINS: Annotated[List[str], NoDecode] = ["http://localhost:3000"]

    # Uploads
    UPLOAD_DIR: str = "/app/storage/uploads"
    MAX_UPLOAD_MB: int = 10
    ALLOWED_IMAGE_MIME: Annotated[List[str], NoDecode] = ["image/jpeg", "image/png", "image/webp"]
    PUBLIC_MEDIA_BASE_URL: str = "/media"

    # Rate limiting
    RATE_LIMIT_DEFAULT: str = "100/minute"
    RATE_LIMIT_LOGIN: str = "10/minute"
    RATE_LIMIT_BOT: str = "60/minute"

    @field_validator("CORS_ORIGINS", "ALLOWED_IMAGE_MIME", mode="before")
    @classmethod
    def _split_csv(cls, v):
        if isinstance(v, str):
            return [item.strip() for item in v.split(",") if item.strip()]
        return v


@lru_cache
def get_settings() -> Settings:
    return Settings()
