import asyncio
import base64
from io import BytesIO

from fastapi.testclient import TestClient
from PIL import Image, ImageDraw

from app.main import create_app
from app.models import IndicatorSummary, MarketContextSummary, NewsSummary, OHLCVBar, RiskSummary, SupportResistance, TechnicalAnalysis
from app.providers.chart_metadata_provider import ChartVisionHints, PriceAxisLabel
from app.services.indicators import compute_indicators, ema_series, rsi
from app.services.screenshot_parser import parse_screenshot
from app.services.scoring import overall_score_breakdown, technical_score, technical_score_from_subscores, technical_subscores

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
    assert payload["signal"]["action"] == "insufficient"
    assert payload["extraction"]["candle_count"] == 0
    assert "screenshot image" in payload["notes"]


def test_parse_screenshot_contract_rejects_invalid_base64():
    response = client.post("/api/parse-screenshot", json={"image_base64": "not-valid-base64"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["signal"]["action"] == "insufficient"
    assert payload["candles"] == []
    assert "disc" + "laimer" not in payload


def test_parse_screenshot_extracts_synthetic_candles_and_buy_signal():
    image_base64 = _synthetic_chart_base64(direction="up", candle_count=60)

    class FakeVisionProvider:
        mode = "live"

        async def detect_text(self, image_bytes: bytes) -> str:
            return "NASDAQ: AAPL 1D"

        async def detect_text_blocks(self, image_bytes: bytes):
            return []

        def status(self):
            return {}

    class FakeMetadataProvider:
        mode = "live"

        async def get_chart_hints(self, image_bytes: bytes) -> ChartVisionHints:
            return ChartVisionHints(
                detected_ticker="AAPL",
                detected_timeframe="1D",
                price_axis_labels=[
                    PriceAxisLabel(value=140.0, y=40.0),
                    PriceAxisLabel(value=80.0, y=440.0),
                ],
            )

        def status(self):
            return {}

    result = asyncio.run(
        parse_screenshot(
            image_base64=image_base64,
            vision_provider=FakeVisionProvider(),
            chart_metadata_provider=FakeMetadataProvider(),
        )
    )

    assert result.detected_ticker == "AAPL"
    assert result.detected_timeframe == "1D"
    assert result.needs_confirmation is True
    assert result.extraction.candle_count >= 50
    assert result.signal.action == "buy"
    assert result.signal.confidence in {"medium", "high"}
    assert len(result.candles) == result.extraction.candle_count
    assert result.candles[-1].close > result.candles[0].close


def test_parse_screenshot_extracts_synthetic_sell_signal():
    image_base64 = _synthetic_chart_base64(direction="down", candle_count=60)

    class FakeVisionProvider:
        mode = "live"

        async def detect_text(self, image_bytes: bytes) -> str:
            return "NASDAQ: AAPL 1D"

        async def detect_text_blocks(self, image_bytes: bytes):
            return []

        def status(self):
            return {}

    class FakeMetadataProvider:
        mode = "live"

        async def get_chart_hints(self, image_bytes: bytes) -> ChartVisionHints:
            return ChartVisionHints(
                detected_ticker="AAPL",
                detected_timeframe="1D",
                price_axis_labels=[
                    PriceAxisLabel(value=140.0, y=40.0),
                    PriceAxisLabel(value=80.0, y=440.0),
                ],
            )

        def status(self):
            return {}

    result = asyncio.run(
        parse_screenshot(
            image_base64=image_base64,
            vision_provider=FakeVisionProvider(),
            chart_metadata_provider=FakeMetadataProvider(),
        )
    )

    assert result.extraction.candle_count >= 50
    assert result.signal.action == "sell"
    assert result.candles[-1].close < result.candles[0].close


def test_parse_screenshot_without_axis_calibration_is_insufficient():
    image_base64 = _synthetic_chart_base64(direction="down", candle_count=60)

    class FakeVisionProvider:
        mode = "live"

        async def detect_text(self, image_bytes: bytes) -> str:
            return "NYSE: MSFT 1D"

        async def detect_text_blocks(self, image_bytes: bytes):
            return []

        def status(self):
            return {}

    result = asyncio.run(parse_screenshot(image_base64=image_base64, vision_provider=FakeVisionProvider()))
    assert result.signal.action == "insufficient"
    assert result.extraction.candle_count >= 50
    assert result.candles == []
    assert any("calibration" in warning.lower() for warning in result.extraction.warnings)


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


def test_differential_score_renormalizes_missing_domains_and_penalizes_risk():
    technical = TechnicalAnalysis(
        setup="bullish",
        score=80,
        confidence="medium",
        indicators=IndicatorSummary(),
        support_resistance=SupportResistance(support=[], resistance=[]),
        evidence=[],
        risks=[],
    )
    news = NewsSummary(sentiment="positive", score=20, items=[], summary="Recent news is available.")
    market_context = MarketContextSummary(
        score=60,
        benchmark="SPY",
        relative_strength_20d=2.0,
        relative_strength_60d=None,
        summary="Mixed.",
    )
    risk = RiskSummary(score=70, level="moderate", warnings=[])

    breakdown = overall_score_breakdown(
        technical=technical,
        news=news,
        fundamental_score=90,
        risk=risk,
        market_context=market_context,
        horizon="swing",
        news_available=True,
        fundamentals_available=False,
    )

    assert breakdown.model_version == "diffscore-v1"
    assert breakdown.provider_coverage == 0.75
    assert breakdown.base_score == 74
    assert breakdown.risk_penalty == 6
    assert breakdown.risk_adjusted_score == 68
    assert next(item for item in breakdown.contributions if item.domain == "fundamentals").available is False


def test_provider_status():
    response = client.get("/api/providers/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "providers" in data


def test_live_mode_response_has_new_sections():
    """Verify that with injected providers, core response sections are present."""
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
    assert "disc" + "laimer" not in payload
    assert payload["data_mode"] == "live"
    assert payload["data_quality"]["status"] == "usable"
    assert payload["risk"]["level"] in {"low", "moderate", "elevated", "high"}
    assert payload["market_context"]["benchmark"] == "SPY"
    assert payload["technical"]["trend_score"] is not None
    assert "conclusion" in payload["overall"]
    assert payload["overall"]["score_model_version"] == "diffscore-v1"
    assert payload["overall"]["score_breakdown"]["risk_penalty"] >= 0
    assert "data_quality" in payload
    assert "risk" in payload
    assert "market_context" in payload


def _synthetic_chart_base64(direction: str, candle_count: int) -> str:
    width, height = 800, 500
    left, top, right, bottom = 60, 40, 700, 440
    min_price, max_price = 80.0, 140.0

    def y_for_price(price: float) -> int:
        ratio = (max_price - price) / (max_price - min_price)
        return int(top + ratio * (bottom - top))

    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)
    for y in range(top, bottom + 1, 80):
        draw.line((left, y, right, y), fill=(230, 230, 230), width=1)
    draw.rectangle((left, top, right, bottom), outline=(210, 210, 210), width=1)

    step = (right - left) / candle_count
    for index in range(candle_count):
        trend = index * 0.62
        base = 92 + trend if direction == "up" else 128 - trend
        open_price = base
        close_price = base + 1.8 if direction == "up" else base - 1.8
        high_price = max(open_price, close_price) + 1.2
        low_price = min(open_price, close_price) - 1.1
        center_x = int(left + (index + 0.5) * step)
        body_half_width = max(2, int(step * 0.28))
        color = (38, 166, 154) if close_price >= open_price else (239, 83, 80)
        high_y = y_for_price(high_price)
        low_y = y_for_price(low_price)
        open_y = y_for_price(open_price)
        close_y = y_for_price(close_price)
        body_top = min(open_y, close_y)
        body_bottom = max(open_y, close_y)
        draw.line((center_x, high_y, center_x, low_y), fill=color, width=2)
        draw.rectangle(
            (center_x - body_half_width, body_top, center_x + body_half_width, body_bottom),
            fill=color,
        )

    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("ascii")
