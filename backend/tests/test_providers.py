from __future__ import annotations

import asyncio

import pytest


class TestProviderFactory:
    def test_yfinance_market_provider_created(self):
        from app.config import Settings
        from app.providers import create_providers

        settings = Settings(MARKET_DATA_PROVIDER="yfinance")
        providers = create_providers(settings)
        assert providers.market.mode == "live"

    def test_default_providers_are_live_or_unavailable_without_news_key(self):
        from app.config import Settings
        from app.providers import create_providers

        settings = Settings()
        providers = create_providers(settings)
        assert providers.market.mode == "live"
        assert providers.news.mode == "unavailable"
        assert providers.fundamentals.mode == "live"

    def test_finnhub_news_provider_created(self):
        from app.config import Settings
        from app.providers import create_providers

        settings = Settings(NEWS_PROVIDER="finnhub", NEWS_API_KEY="test-key")
        providers = create_providers(settings)
        assert providers.news.mode == "live"

    def test_finnhub_without_key_is_unavailable(self):
        from app.config import Settings
        from app.providers import create_providers

        settings = Settings(NEWS_PROVIDER="finnhub", NEWS_API_KEY="")
        providers = create_providers(settings)
        assert providers.news.mode == "unavailable"

    def test_yfinance_fundamentals_provider_created(self):
        from app.config import Settings
        from app.providers import create_providers

        settings = Settings(FUNDAMENTALS_PROVIDER="yfinance")
        providers = create_providers(settings)
        assert providers.fundamentals.mode == "live"

    def test_ai_explanation_provider_created(self):
        from app.config import Settings
        from app.providers import create_providers

        settings = Settings(AI_PROVIDER="openai", AI_API_KEY="test-key", AI_MODEL="gpt-4o-mini")
        providers = create_providers(settings)
        assert providers.explanation is not None
        assert providers.explanation.mode == "live"

    def test_no_ai_key_means_no_explanation(self):
        from app.config import Settings
        from app.providers import create_providers

        settings = Settings(AI_PROVIDER="openai", AI_API_KEY="")
        providers = create_providers(settings)
        assert providers.explanation is None

    def test_unknown_provider_raises(self):
        from app.config import Settings
        from app.providers import create_providers

        settings = Settings(MARKET_DATA_PROVIDER="nonexistent")
        with pytest.raises(ValueError, match="Unknown market data provider"):
            create_providers(settings)


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
        assert call_count == 1

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

    def test_async_cache_stores_and_retrieves(self):
        from app.providers.cache import aget_with_cache

        cache = {}
        call_count = 0

        async def fetcher():
            nonlocal call_count
            call_count += 1
            return "cached_value"

        async def run():
            r1 = await aget_with_cache(cache, ("test", "key"), fetcher, ttl=60)
            r2 = await aget_with_cache(cache, ("test", "key"), fetcher, ttl=60)
            return r1, r2

        r1, r2 = asyncio.run(run())
        assert r1 == "cached_value"
        assert r2 == "cached_value"
        assert call_count == 1


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
