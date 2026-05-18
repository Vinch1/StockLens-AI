from __future__ import annotations

from fastapi import FastAPI, HTTPException

from app.models import AnalyzeRequest, ScreenshotParseRequest
from app.providers.mock import fundamentals_provider, market_provider, news_provider
from app.services.analysis_service import analyze_ticker
from app.services.screenshot_parser import parse_placeholder

VERSION = "0.1.0"

app = FastAPI(
    title="StockLens AI API",
    description="Educational stock research and risk-analysis assistant. Not financial advice.",
    version=VERSION,
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "stocklens-ai-api", "version": VERSION}


@app.post("/api/analyze")
def analyze(request: AnalyzeRequest) -> dict[str, object]:
    try:
        return analyze_ticker(request).model_dump()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/parse-screenshot")
def parse_screenshot(request: ScreenshotParseRequest) -> dict[str, object]:
    return parse_placeholder(request.filename)


@app.get("/api/mock/ohlcv/{ticker}")
def mock_ohlcv(ticker: str, timeframe: str = "1D", bars: int = 260) -> dict[str, object]:
    normalized = ticker.strip().upper()
    bounded_bars = max(30, min(bars, 500))
    data = market_provider.get_ohlcv(normalized, timeframe, bounded_bars)
    return {"ticker": normalized, "timeframe": timeframe, "data_mode": "mock", "bars": [bar.model_dump() for bar in data]}


@app.get("/api/providers/status")
def providers_status() -> dict[str, object]:
    providers = [market_provider.status(), news_provider.status(), fundamentals_provider.status()]
    return {"status": "ok", "data_mode": "mock", "providers": providers}
