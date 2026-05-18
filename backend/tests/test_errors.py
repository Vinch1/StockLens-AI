from __future__ import annotations

import asyncio

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock

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

        market = AsyncMock()
        market.get_ohlcv.side_effect = ProviderDataError("No data for ticker")
        market.mode = "live"

        providers = Providers(
            market=market,
            news=AsyncMock(),
            fundamentals=AsyncMock(),
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
        from app.services.explanation import get_educational_conclusion

        technical = TechnicalAnalysis(
            setup="bullish",
            score=70,
            confidence="medium",
            indicators=IndicatorSummary(),
            support_resistance=SupportResistance(support=[], resistance=[]),
            evidence=[],
            risks=[],
        )

        failing_provider = AsyncMock()
        failing_provider.mode = "live"
        failing_provider.generate_conclusion.side_effect = RuntimeError("AI down")

        result = asyncio.get_event_loop().run_until_complete(
            get_educational_conclusion(technical, 70, "medium", explanation_provider=failing_provider)
        )
        assert "educational" in result.lower()
        assert "not a recommendation" in result.lower()
