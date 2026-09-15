from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    BOT_TOKEN: str
    BACKEND_API_URL: str = "http://backend:8000/api/v1"
    BOT_INTERNAL_TOKEN: str
    REDIS_URL: str = "redis://redis:6379/1"
    DEBUG: bool = False
    EMERGENCY_HOTLINE_FALLBACK: str = "104"


@lru_cache
def get_settings() -> Settings:
    return Settings()
