from fastapi.testclient import TestClient

from app.main import create_app
from app.models import OHLCVBar
from app.services.compliance import contains_forbidden_language, sanitize_or_fallback
from app.services.indicators import compute_indicators, ema_series, rsi
from app.services.scoring import technical_score, technical_score_from_subscores, technical_subscores

app = create_app()
client = TestClient(app)


def test_health_contract():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "stocklens-ai-api", "version": "0.1.0"}


def test_parse_screenshot_requires_confirmation():
    response = client.post("/api/parse-screenshot", json={"filename": "chart.png"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["needs_confirmation"] is True
    assert payload["confidence"] == "low"
    assert "not from the screenshot" in payload["notes"]


def test_indicator_known_values_and_score_bounds():
    closes = [float(value) for value in range(1, 31)]
    bars = [OHLCVBar(timestamp=str(i), open=c - 0.2, high=c + 0.8, low=c - 0.8, close=c, volume=1000 + i) for i, c in enumerate(closes)]
    indicators = compute_indicators(bars)
    assert indicators.sma20 == 20.5
    assert round(ema_series(closes, 12)[-1], 4) == indicators.ema12
    assert rsi(closes) == 100.0
    score = technical_score(indicators, bars[-1].close, bars[-2].close, indicators.volume_ratio)
    assert 0 <= score <= 100
    subscores = technical_subscores(indicators, bars[-1].close, bars[-2].close, __import__("app.services.indicators", fromlist=["support_resistance"]).support_resistance(bars))
    assert set(subscores) == {"trend_score", "momentum_score", "structure_score", "volume_score", "volatility_score"}
    assert 0 <= technical_score_from_subscores(subscores) <= 100


def test_compliance_filter_rejects_forbidden_output():
    assert contains_forbidden_language("Buy now for a guaranteed move")
    fallback = "Educational summary only."
    assert sanitize_or_fallback("You should invest all in", fallback) == fallback


def test_provider_status():
    response = client.get("/api/providers/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "providers" in data


def test_live_mode_response_has_disclaimer_and_new_sections():
    """Verify that with injected providers, disclaimer is always present."""
    from app.models import FundamentalMetrics, FundamentalsSummary, NewsSummary
    from app.providers import Providers

    test_app = create_app()

    bars = []
    for i in range(260):
        open_price = 100 + i * 0.5
        close = 103 + i * 0.5
        bars.append(
            OHLCVBar(
                timestamp=f"2024-01-{i+1:02d}T00:00:00",
                open=open_price,
                high=max(open_price, close) + 2,
                low=min(open_price, close) - 2,
                close=close,
                volume=1000 + i * 100,
            )
        )

    class FixtureMarketProvider:
        mode = "live"

        async def get_ohlcv(self, ticker: str, timeframe: str = "1D", bars_count: int = 260):
            return bars

    class FixtureNewsProvider:
        mode = "live"

        async def get_news(self, ticker: str) -> NewsSummary:
            return NewsSummary(sentiment="neutral", score=0, items=[], summary="No news.")

    class FixtureFundamentalsProvider:
        mode = "live"

        async def get_fundamentals(self, ticker: str) -> FundamentalsSummary:
            return FundamentalsSummary(
                quality="unavailable",
                score=50,
                metrics=FundamentalMetrics(),
                summary="No fundamentals.",
            )

    test_app.state.providers = Providers(
        market=FixtureMarketProvider(),
        news=FixtureNewsProvider(),
        fundamentals=FixtureFundamentalsProvider(),
        explanation=None,
    )

    test_client = TestClient(test_app)
    response = test_client.post(
        "/api/analyze",
        json={"ticker": "AAPL", "asset_type": "stock", "timeframe": "1D", "horizon": "swing"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert "not financial advice" in payload["disclaimer"].lower()
    assert payload["data_mode"] == "live"
    assert payload["data_quality"]["status"] == "usable"
    assert payload["risk"]["level"] in {"low", "moderate", "elevated", "high"}
    assert payload["market_context"]["benchmark"] == "SPY"
    assert payload["technical"]["trend_score"] is not None
    assert "data_quality" in payload
    assert "risk" in payload
    assert "market_context" in payload
