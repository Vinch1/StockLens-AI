from __future__ import annotations

from app.config import Settings


def test_default_config_has_live_providers():
    settings = Settings()
    assert settings.MARKET_DATA_PROVIDER == "yfinance"
    assert settings.FUNDAMENTALS_PROVIDER == "yfinance"
    assert settings.NEWS_PROVIDER == "finnhub"


def test_config_reads_env_vars(monkeypatch):
    monkeypatch.setenv("MARKET_DATA_PROVIDER", "yfinance")
    monkeypatch.setenv("NEWS_PROVIDER", "finnhub")
    monkeypatch.setenv("NEWS_API_KEY", "test-key")
    settings = Settings()
    assert settings.MARKET_DATA_PROVIDER == "yfinance"
    assert settings.NEWS_PROVIDER == "finnhub"
    assert settings.NEWS_API_KEY == "test-key"


def test_cors_origins_parsed():
    settings = Settings(CORS_ORIGINS="http://a.com, http://b.com, ")
    origins = settings.get_cors_origins()
    assert origins == ["http://a.com", "http://b.com"]


def test_empty_api_keys_default_to_blank(monkeypatch):
    monkeypatch.delenv("MARKET_DATA_API_KEY", raising=False)
    monkeypatch.delenv("NEWS_API_KEY", raising=False)
    monkeypatch.delenv("AI_API_KEY", raising=False)
    monkeypatch.delenv("CHART_VISION_API_KEY", raising=False)
    settings = Settings()
    assert settings.MARKET_DATA_API_KEY == ""
    assert settings.NEWS_API_KEY == ""
    assert settings.AI_API_KEY == ""
    assert settings.CHART_VISION_API_KEY == ""
