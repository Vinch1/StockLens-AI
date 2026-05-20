# StockLens AI API Contract

Provider access is backend-only; the Android client must never call paid market, news, AI, fundamentals, or VLM providers directly.

## `GET /health`

```json
{
  "status": "ok",
  "service": "stocklens-ai-api",
  "version": "0.1.0"
}
```

## `POST /api/analyze`

### Request

```json
{
  "ticker": "AAPL",
  "asset_type": "stock",
  "timeframe": "1D",
  "horizon": "swing",
  "include_news": true,
  "include_fundamentals": true
}
```

Accepted timeframes: `15m`, `1h`, `4h`, `1D`, `1W`. Accepted horizons: `short`, `swing`, `long`.

### Response shape

The response includes ticker metadata, `data_mode`, `price_summary`, `data_quality`, `technical`, `risk`, `news`, `fundamentals`, `market_context`, and `overall`. Technical output includes SMA 20/50/200, EMA 12/26, RSI 14, MACD line/signal/histogram, Bollinger Bands, ATR, volume ratio, support/resistance, evidence, risks, and trend/momentum/structure/volume/volatility sub-scores. Overall output uses `diffscore-v1`, which excludes unavailable scoring domains from the weighted mean and applies risk as a penalty.

```json
{
  "ticker": "AAPL",
  "asset_type": "stock",
  "timeframe": "1D",
  "horizon": "swing",
  "generated_at": "2026-05-18T12:00:00+00:00",
  "data_mode": "live",
  "price_summary": {
    "last_close": 123.45,
    "change_pct": 1.23,
    "volume": 123456789
  },
  "data_quality": {
    "score": 100,
    "status": "usable",
    "bars_count": 260,
    "latest_timestamp": "2026-05-18T00:00:00+00:00",
    "warnings": []
  },
  "technical": {
    "setup": "neutral_to_bullish",
    "score": 68,
    "confidence": "low",
    "indicators": {
      "sma20": 120.1,
      "sma50": 118.2,
      "sma200": 110.5,
      "ema12": 122.4,
      "ema26": 119.8,
      "rsi14": 58.4,
      "macd": 2.1,
      "macd_signal": 1.6,
      "macd_histogram": 0.5,
      "bollinger_upper": 130.0,
      "bollinger_middle": 120.0,
      "bollinger_lower": 110.0,
      "atr14": 3.2,
      "volume_ratio": 1.15
    },
    "support_resistance": {
      "support": [118.0, 114.5],
      "resistance": [126.0, 130.5]
    },
    "evidence": ["Price is above the 20-period and 50-period moving averages."],
    "risks": ["Past performance does not guarantee future results."],
    "trend_score": 74,
    "momentum_score": 62,
    "structure_score": 70,
    "volume_score": 58,
    "volatility_score": 55
  },
  "risk": {
    "score": 82,
    "level": "low",
    "atr_pct": 2.59,
    "realized_volatility_20d": 24.5,
    "realized_volatility_60d": 22.1,
    "max_drawdown_60d": -8.4,
    "average_dollar_volume_20d": 1234567890.0,
    "warnings": []
  },
  "news": {
    "sentiment": "neutral",
    "score": 0,
    "items": [],
    "summary": "News analysis is unavailable: NEWS_API_KEY is required for finnhub"
  },
  "fundamentals": {
    "quality": "unavailable",
    "score": 50,
    "metrics": {
      "revenue_growth": null,
      "earnings_growth": null,
      "free_cash_flow": null,
      "debt_to_equity": null,
      "pe_ratio": null,
      "forward_pe": null,
      "gross_margin": null,
      "operating_margin": null
    },
    "summary": "Fundamental data is unavailable from the configured provider.",
    "growth_score": 50,
    "profitability_score": 50,
    "balance_sheet_score": 50,
    "valuation_score": 50,
    "cash_flow_score": 50
  },
  "market_context": {
    "score": 64,
    "benchmark": "SPY",
    "relative_strength_20d": 3.2,
    "relative_strength_60d": -1.1,
    "summary": "Relative strength versus SPY is mixed."
  },
  "overall": {
    "label": "mixed_research_candidate",
    "score": 63,
    "confidence": "medium",
    "conclusion": "This is a mixed research candidate. The technical setup is neutral to bullish, with medium confidence based on configured data.",
    "score_model_version": "diffscore-v1",
    "score_breakdown": {
      "model_version": "diffscore-v1",
      "base_score": 67,
      "risk_penalty": 3.6,
      "risk_adjusted_score": 63,
      "risk_safety_score": 82,
      "provider_coverage": 0.6,
      "agreement_factor": 0.96,
      "confidence_score": 0.576,
      "contributions": [
        {
          "domain": "technical",
          "score": 68,
          "requested_weight": 0.45,
          "effective_weight": 0.75,
          "contribution": 51.0,
          "available": true,
          "reason": null
        },
        {
          "domain": "fundamentals",
          "score": null,
          "requested_weight": 0.25,
          "effective_weight": 0.0,
          "contribution": 0.0,
          "available": false,
          "reason": "fundamentals data is unavailable or was not requested."
        },
        {
          "domain": "news",
          "score": null,
          "requested_weight": 0.15,
          "effective_weight": 0.0,
          "contribution": 0.0,
          "available": false,
          "reason": "news data is unavailable or was not requested."
        },
        {
          "domain": "market_context",
          "score": 64,
          "requested_weight": 0.15,
          "effective_weight": 0.25,
          "contribution": 16.0,
          "available": true,
          "reason": null
        }
      ]
    }
  }
}
```

`score_breakdown.confidence_score` is `0..1` and maps to `high` at `>= 0.80`, `medium` at `>= 0.55`, and `low` below that.

## `POST /api/parse-screenshot`

Uploads a candlestick screenshot as base64. The backend processes the image in memory, extracts visible ticker/timeframe metadata when possible, reconstructs approximate candles from the screenshot, and returns a chart-derived technical signal. The endpoint does not call yfinance, news, or fundamentals providers.

```json
{
  "filename": "chart.png",
  "image_base64": "iVBORw0KGgo..."
}
```

Response:

```json
{
  "detected_ticker": "AAPL",
  "detected_timeframe": "1D",
  "confidence": "medium",
  "needs_confirmation": true,
  "notes": "Detected ticker: AAPL. Detected timeframe: 1D. Screenshot-derived candles are approximate. Confirm ticker and timeframe, and verify the source chart before using the signal.",
  "extraction": {
    "candle_count": 62,
    "calibration_confidence": "medium",
    "warnings": []
  },
  "candles": [
    {
      "index": 0,
      "timestamp_label": null,
      "open": 178.12,
      "high": 180.22,
      "low": 177.64,
      "close": 179.8,
      "direction": "bullish",
      "confidence": "medium"
    }
  ],
  "signal": {
    "action": "buy",
    "score": 66,
    "confidence": "medium",
    "reasons": [
      "Chart-derived technical score is 66/100.",
      "Price is above the 20-period and 50-period moving averages."
    ],
    "risk_warnings": [
      "Screenshot-derived candles are approximate and must be verified against a reliable market data source."
    ]
  }
}
```

`signal.action` may be `buy`, `sell`, `neutral`, or `insufficient`. The endpoint returns `insufficient` when price-axis calibration fails, fewer than 30 candles are extracted, or extraction confidence is low.

## `GET /api/providers/status`

Returns configured provider modes and whether providers are available. A missing Finnhub key reports the news provider as `unavailable`.

## Security requirements

- API keys are backend-only and supplied through environment variables.
- Screenshot parsing is assistive only and must require user confirmation.
