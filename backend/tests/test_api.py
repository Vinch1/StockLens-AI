from fastapi.testclient import TestClient

from app.main import app
from app.models import OHLCVBar
from app.services.compliance import contains_forbidden_language, sanitize_or_fallback
from app.services.indicators import compute_indicators, ema_series, rsi
from app.services.scoring import technical_score

client = TestClient(app)


def test_health_contract():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "stocklens-ai-api", "version": "0.1.0"}


def test_analyze_returns_structured_mock_report():
    response = client.post(
        "/api/analyze",
        json={"ticker": "aapl", "asset_type": "stock", "timeframe": "1D", "horizon": "swing", "include_news": True, "include_fundamentals": True},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["ticker"] == "AAPL"
    assert payload["data_mode"] == "mock"
    assert payload["technical"]["indicators"]["sma20"] is not None
    assert payload["technical"]["support_resistance"]["support"]
    assert payload["news"]["items"][0]["source"] == "Mock News"
    assert "not financial advice" in payload["disclaimer"].lower()
    assert "recommendation" in payload["overall"]["educational_conclusion"].lower()


def test_parse_screenshot_requires_confirmation():
    response = client.post("/api/parse-screenshot", json={"filename": "chart.png"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["needs_confirmation"] is True
    assert payload["confidence"] == "low"
    assert "not from the screenshot" in payload["notes"]


def test_mock_ohlcv_endpoint():
    response = client.get("/api/mock/ohlcv/MSFT?timeframe=1W&bars=45")
    assert response.status_code == 200
    payload = response.json()
    assert payload["ticker"] == "MSFT"
    assert payload["timeframe"] == "1W"
    assert len(payload["bars"]) == 45


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
    assert response.json()["data_mode"] == "mock"
