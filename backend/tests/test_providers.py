from __future__ import annotations

import pytest

from app.models import FundamentalMetrics, FundamentalsSummary, NewsSummary, OHLCVBar
from app.providers.mock import (
    MockFundamentalsProvider,
    MockMarketDataProvider,
    MockNewsProvider,
)


class TestMockProviderProtocols:
    def test_mock_market_provider_has_get_ohlcv(self):
        provider = MockMarketDataProvider()
        bars = provider.get_ohlcv("AAPL", "1D", 30)
        assert isinstance(bars, list)
        assert all(isinstance(b, OHLCVBar) for b in bars)
        assert provider.mode == "mock"

    def test_mock_news_provider_has_get_news(self):
        provider = MockNewsProvider()
        result = provider.get_news("AAPL")
        assert isinstance(result, NewsSummary)
        assert provider.mode == "mock"

    def test_mock_fundamentals_provider_has_get_fundamentals(self):
        provider = MockFundamentalsProvider()
        result = provider.get_fundamentals("AAPL")
        assert isinstance(result, FundamentalsSummary)
        assert provider.mode == "mock"

    def test_all_mock_providers_have_status(self):
        for provider in [MockMarketDataProvider(), MockNewsProvider(), MockFundamentalsProvider()]:
            status = provider.status()
            assert "name" in status
            assert "mode" in status
            assert status["mode"] == "mock"


class TestProviderFactory:
    def test_mock_mode_returns_mock_providers(self):
        from app.config import Settings
        from app.providers import create_providers

        settings = Settings(MOCK_MODE=True)
        providers = create_providers(settings)
        assert providers.market.mode == "mock"
        assert providers.news.mode == "mock"
        assert providers.fundamentals.mode == "mock"
        assert providers.explanation is None

    def test_mock_mode_overrides_individual_settings(self):
        from app.config import Settings
        from app.providers import create_providers

        settings = Settings(MOCK_MODE=True, MARKET_DATA_PROVIDER="yfinance")
        providers = create_providers(settings)
        assert providers.market.mode == "mock"

    def test_live_mode_with_mock_fallback(self):
        from app.config import Settings
        from app.providers import create_providers

        settings = Settings(MOCK_MODE=False)
        providers = create_providers(settings)
        assert providers.market.mode == "mock"
        assert providers.news.mode == "mock"

    def test_yfinance_market_provider_created(self):
        from app.config import Settings
        from app.providers import create_providers

        settings = Settings(MOCK_MODE=False, MARKET_DATA_PROVIDER="yfinance")
        providers = create_providers(settings)
        assert providers.market.mode == "live"

    def test_finnhub_news_provider_created(self):
        from app.config import Settings
        from app.providers import create_providers

        settings = Settings(MOCK_MODE=False, NEWS_PROVIDER="finnhub", NEWS_API_KEY="test-key")
        providers = create_providers(settings)
        assert providers.news.mode == "live"

    def test_yfinance_fundamentals_provider_created(self):
        from app.config import Settings
        from app.providers import create_providers

        settings = Settings(MOCK_MODE=False, FUNDAMENTALS_PROVIDER="yfinance")
        providers = create_providers(settings)
        assert providers.fundamentals.mode == "live"

    def test_ai_explanation_provider_created(self):
        from app.config import Settings
        from app.providers import create_providers

        settings = Settings(MOCK_MODE=False, AI_PROVIDER="openai", AI_API_KEY="test-key", AI_MODEL="gpt-4o-mini")
        providers = create_providers(settings)
        assert providers.explanation is not None
        assert providers.explanation.mode == "live"

    def test_no_ai_key_means_no_explanation(self):
        from app.config import Settings
        from app.providers import create_providers

        settings = Settings(MOCK_MODE=False, AI_PROVIDER="openai", AI_API_KEY="")
        providers = create_providers(settings)
        assert providers.explanation is None


class TestCache:
    def test_cache_stores_and_retrieves(self):
        from app.providers.cache import get_with_cache

        cache = {}
        call_count = 0

        def fetcher():
            nonlocal call_count
            call_count += 1
            return "cached_value"

        result1 = get_with_cache(cache, ("test", "key"), fetcher, ttl=60)
        assert result1 == "cached_value"
        assert call_count == 1

        result2 = get_with_cache(cache, ("test", "key"), fetcher, ttl=60)
        assert result2 == "cached_value"
        assert call_count == 1  # Not called again

    def test_cache_expires(self):
        import time
        from app.providers.cache import get_with_cache

        cache = {}
        call_count = 0

        def fetcher():
            nonlocal call_count
            call_count += 1
            return f"value_{call_count}"

        get_with_cache(cache, ("test", "key"), fetcher, ttl=0)
        time.sleep(0.01)
        get_with_cache(cache, ("test", "key"), fetcher, ttl=0)
        assert call_count == 2


class TestSentimentClassifier:
    def test_positive_sentiment(self):
        from app.services.sentiment import classify_sentiment

        assert classify_sentiment("Company reports record high revenue growth and profit surge") == "positive"

    def test_negative_sentiment(self):
        from app.services.sentiment import classify_sentiment

        assert classify_sentiment("Stock plunge amid weak earnings and bearish downgrade") == "negative"

    def test_neutral_sentiment(self):
        from app.services.sentiment import classify_sentiment

        assert classify_sentiment("Company announces quarterly update") == "neutral"


class TestTickerExtraction:
    def test_extracts_exchange_prefixed_ticker(self):
        from app.services.ticker_extraction import extract_ticker

        assert extract_ticker("NASDAQ: AAPL Daily Chart") == "AAPL"

    def test_extracts_ticker_after_exchange_keyword(self):
        from app.services.ticker_extraction import extract_ticker

        result = extract_ticker("Apple Inc (NASDAQ) AAPL $175.00")
        assert result == "AAPL"

    def test_returns_none_for_no_ticker(self):
        from app.services.ticker_extraction import extract_ticker

        assert extract_ticker("just some random text without tickers") is None

    def test_filters_false_positives(self):
        from app.services.ticker_extraction import extract_ticker

        assert extract_ticker("HIGH LOW OPEN CLOSE VOLUME") is None


class TestTimeframeExtraction:
    def test_extracts_standard_timeframe(self):
        from app.services.ticker_extraction import extract_timeframe

        assert extract_timeframe("Chart timeframe: 1D") == "1D"

    def test_extracts_weekly(self):
        from app.services.ticker_extraction import extract_timeframe

        assert extract_timeframe("Weekly chart 1W") == "1W"

    def test_returns_none_for_no_match(self):
        from app.services.ticker_extraction import extract_timeframe

        assert extract_timeframe("no timeframe here") is None
