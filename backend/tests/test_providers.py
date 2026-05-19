from __future__ import annotations

import asyncio
import logging

import pytest


class TestProviderFactory:
    def test_yfinance_market_provider_created(self):
        from app.config import Settings
        from app.providers import create_providers

        settings = Settings(MARKET_DATA_PROVIDER="yfinance")
        providers = create_providers(settings)
        assert providers.market.mode == "live"

    def test_default_providers_are_live_or_unavailable_without_news_key(self, monkeypatch):
        from app.config import Settings
        from app.providers import create_providers

        monkeypatch.delenv("NEWS_API_KEY", raising=False)
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

    def test_qwen_chart_vision_provider_created(self):
        from app.config import Settings
        from app.providers import create_providers

        settings = Settings(
            CHART_VISION_PROVIDER="qwen",
            CHART_VISION_API_KEY="test-key",
            CHART_VISION_MODEL="qwen3.6-plus",
        )
        providers = create_providers(settings)

        assert providers.chart_vision is not None
        assert providers.chart_vision.mode == "live"
        assert "qwen" in providers.chart_vision.status()["message"]

    def test_qwen_chart_vision_provider_uses_openai_compatible_base_url(self):
        from app.providers.chart_metadata_provider import VLMChartMetadataProvider

        provider = VLMChartMetadataProvider(
            api_key="test-key",
            model="qwen3.6-plus",
            provider="qwen",
        )

        assert provider._litellm_model == "openai/qwen3.6-plus"
        assert provider.api_base == "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"

    def test_qwen_chart_vision_provider_allows_base_url_override(self):
        from app.providers.chart_metadata_provider import VLMChartMetadataProvider

        provider = VLMChartMetadataProvider(
            api_key="test-key",
            model="qwen3-vl-flash",
            provider="qwen",
            api_base="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )

        assert provider._litellm_model == "openai/qwen3-vl-flash"
        assert provider.api_base == "https://dashscope.aliyuncs.com/compatible-mode/v1"

    def test_unknown_provider_raises(self):
        from app.config import Settings
        from app.providers import create_providers

        settings = Settings(MARKET_DATA_PROVIDER="nonexistent")
        with pytest.raises(ValueError, match="Unknown market data provider"):
            create_providers(settings)


class TestChartMetadataParsing:
    def test_parse_hints_json_tolerates_fenced_json_and_filters_bad_values(self):
        from app.providers.chart_metadata_provider import _parse_hints_json

        hints = _parse_hints_json(
            """
            ```json
            {
              "detected_ticker": " AAPL ",
              "detected_timeframe": " 1D ",
              "chart_bounds": ["10", 20.8, 300, 400],
              "price_axis_labels": [
                {"value": "180.50", "y": "42"},
                {"value": "$bad", "y": 80},
                {"value": 170, "y": null},
                "ignore me"
              ],
              "extra": "ignored"
            }
            ```
            """
        )

        assert hints.detected_ticker == "AAPL"
        assert hints.detected_timeframe == "1D"
        assert hints.chart_bounds == (10, 20, 300, 400)
        assert len(hints.price_axis_labels) == 1
        assert hints.price_axis_labels[0].value == 180.5
        assert hints.price_axis_labels[0].y == 42

    def test_parse_hints_json_rejects_invalid_shapes_without_crashing(self):
        from app.providers.chart_metadata_provider import _parse_hints_json

        hints = _parse_hints_json(
            """
            {
              "detected_ticker": 123,
              "detected_timeframe": [],
              "chart_bounds": ["left", 20, 300],
              "price_axis_labels": [{"value": "bad", "y": "also bad"}]
            }
            """
        )

        assert hints.detected_ticker is None
        assert hints.detected_timeframe is None
        assert hints.chart_bounds is None
        assert hints.price_axis_labels == []


class TestLiteLLMLogging:
    def test_suppresses_only_optional_aws_dependency_warnings(self):
        from app.providers.litellm_logging import suppress_litellm_optional_dependency_warnings

        logger = logging.getLogger("LiteLLM")
        suppress_litellm_optional_dependency_warnings()
        filter_count = sum(1 for log_filter in logger.filters if getattr(log_filter, "_stocklens_filter", False))

        suppress_litellm_optional_dependency_warnings()

        assert sum(1 for log_filter in logger.filters if getattr(log_filter, "_stocklens_filter", False)) == filter_count

        log_filter = next(log_filter for log_filter in logger.filters if getattr(log_filter, "_stocklens_filter", False))
        bedrock_record = logging.LogRecord(
            name="LiteLLM",
            level=logging.WARNING,
            pathname="common_utils.py",
            lineno=979,
            msg="litellm: could not pre-load bedrock-runtime response stream shape",
            args=(),
            exc_info=None,
        )
        other_record = logging.LogRecord(
            name="LiteLLM",
            level=logging.WARNING,
            pathname="provider.py",
            lineno=1,
            msg="litellm: real provider warning",
            args=(),
            exc_info=None,
        )

        assert not log_filter.filter(bedrock_record)
        assert log_filter.filter(other_record)


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
