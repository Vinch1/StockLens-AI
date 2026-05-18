from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    APP_ENV: str = "local"
    LOG_LEVEL: str = "info"
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:8080"

    MARKET_DATA_PROVIDER: str = "yfinance"
    MARKET_DATA_API_KEY: str = ""
    MARKET_DATA_BASE_URL: str = ""

    NEWS_PROVIDER: str = "finnhub"
    NEWS_API_KEY: str = ""

    FUNDAMENTALS_PROVIDER: str = "yfinance"
    FUNDAMENTALS_API_KEY: str = ""

    AI_PROVIDER: str = ""
    AI_API_KEY: str = ""
    AI_MODEL: str = "gpt-4o-mini"

    VISION_PROVIDER: str = "tesseract"

    def get_cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
