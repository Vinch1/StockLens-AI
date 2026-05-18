from fastapi.testclient import TestClient

from app.main import create_app
from app.models import OHLCVBar
from app.services.compliance import contains_forbidden_language, sanitize_or_fallback
from app.services.indicators import compute_indicators, ema_series, rsi
from app.services.scoring import technical_score

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


def test_live_mode_response_has_disclaimer():
    """Verify that with injected providers, disclaimer is always present."""
    from unittest.mock import AsyncMock

    from app.providers import Providers

    test_app = create_app()

    market = AsyncMock()
    bars = [
        OHLCVBar(timestamp=f"2024-01-{i+1:02d}T00:00:00", open=100 + i * 0.5, high=105 + i, low=98 + i, close=103 + i * 0.5, volume=1000 + i * 100)
        for i in range(30)
    ]
    market.get_ohlcv.return_value = bars
    market.mode = "live"

    news = AsyncMock()
    news.get_news.return_value = __import__("app.models", fromlist=["NewsSummary"]).NewsSummary(
        sentiment="neutral", score=0, items=[], summary="No news."
    )

    fundamentals = AsyncMock()
    fundamentals.get_fundamentals.return_value = __import__("app.models", fromlist=["FundamentalsSummary"]).FundamentalsSummary(
        quality="unavailable", score=50, metrics=__import__("app.models", fromlist=["FundamentalMetrics"]).FundamentalMetrics(),
        summary="No fundamentals."
    )

    test_app.state.providers = Providers(
        market=market, news=news, fundamentals=fundamentals, explanation=None
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
