from __future__ import annotations

import asyncio

import pytest
from fastapi.testclient import TestClient

from app.providers.errors import ProviderError, ProviderDataError, ProviderUnavailableError


class TestProviderErrorHierarchy:
    def test_provider_error_is_base(self):
        err = ProviderError("test")
        assert isinstance(err, Exception)

    def test_provider_unavailable_inherits(self):
        err = ProviderUnavailableError("timeout")
        assert isinstance(err, ProviderError)

    def test_provider_data_error_inherits(self):
        err = ProviderDataError("bad data")
        assert isinstance(err, ProviderError)


class TestHTTPErrorHandling:
    def test_provider_error_returns_503(self, client: TestClient):
        """The /api/analyze endpoint should return 503 on ProviderError."""
        from app.main import create_app
        from app.providers.errors import ProviderDataError
        from app.providers import Providers

        app = create_app()

        class FailingMarketProvider:
            mode = "live"

            async def get_ohlcv(self, ticker: str, timeframe: str = "1D", bars: int = 260):
                raise ProviderDataError("No data for ticker")

        providers = Providers(
            market=FailingMarketProvider(),
            news=object(),
            fundamentals=object(),
            explanation=None,
        )
        app.state.providers = providers

        test_client = TestClient(app)
        response = test_client.post(
            "/api/analyze",
            json={"ticker": "INVALID", "asset_type": "stock", "timeframe": "1D", "horizon": "swing"},
        )
        assert response.status_code == 503

    def test_ai_fallback_on_failure(self):
        """When AI explanation provider fails, template fallback is used."""
        from app.models import TechnicalAnalysis, IndicatorSummary, SupportResistance
        from app.services.explanation import get_report_conclusion

        technical = TechnicalAnalysis(
            setup="bullish",
            score=70,
            confidence="medium",
            indicators=IndicatorSummary(),
            support_resistance=SupportResistance(support=[], resistance=[]),
            evidence=[],
            risks=[],
        )

        class FailingExplanationProvider:
            mode = "live"

            async def generate_conclusion(self, *args: object, **kwargs: object) -> str:
                raise RuntimeError("AI down")

        result = asyncio.run(
            get_report_conclusion(technical, 70, "medium", explanation_provider=FailingExplanationProvider())
        )
        assert "constructive research candidate" in result.lower()
        assert "confidence" in result.lower()
