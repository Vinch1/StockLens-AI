# StockLens AI Architecture

## Overview

StockLens AI is a native Android client plus a Python FastAPI backend. The backend owns market/news/fundamental provider access, deterministic technical analysis, and response shaping. The Android app renders reports and stores only lightweight local preferences/watchlist data.

```text
Android Kotlin/Compose app
  ├─ DataStore: onboarding, settings, local watchlist
  ├─ Retrofit/OkHttp API client
  └─ MVVM screens: onboarding, home, analyze, screenshot confirm, report, watchlist, settings
          |
          | JSON over HTTP
          v
FastAPI backend
  ├─ /health
  ├─ /api/analyze
  ├─ /api/parse-screenshot
  ├─ /api/providers/status
  ├─ deterministic screenshot candle extraction and signal services
  ├─ deterministic indicator/risk/scoring services
  ├─ explanation services
  └─ backend-only provider abstractions for market, news, fundamentals, optional AI explanations, and optional VLM chart metadata
```

## Backend communication

The Android app posts `AnalyzeRequest` JSON to `/api/analyze` and renders the structured `AnalyzeResponse`. It posts base64 screenshot JSON to `/api/parse-screenshot` and renders extracted ticker/timeframe hints, candle count, chart signal, reasons, and warnings. In emulator development, the default backend base URL is `http://10.0.2.2:8000/`.

## Data model categories

- Request metadata: ticker, asset type, timeframe, horizon, include news, include fundamentals.
- Market bars: timestamp, open, high, low, close, volume.
- Data quality: bar count, usable/limited/insufficient status, and warnings.
- Technical analysis: setup label, score, confidence, indicators, trend/momentum/structure/volume/volatility sub-scores, support/resistance, evidence, risks.
- Risk: ATR percentage, realized volatility, recent drawdown, average dollar volume, risk level, and warnings.
- News catalysts: title, source, date, URL, summary, sentiment, catalyst type.
- Fundamentals: quality label, score, growth/profitability/balance-sheet/valuation/cash-flow sub-scores, nullable metrics, summary.
- Market context: benchmark, relative strength windows, context score, summary.
- Overall: horizon-aware label, `diffscore-v1` score, confidence, contribution breakdown, and conclusion.
- Screenshot parse: detected ticker/timeframe, extraction summary, approximate candles, structured signal.

## Provider strategy

Providers are backend-only and configured through environment variables such as `MARKET_DATA_PROVIDER`, `NEWS_PROVIDER`, `NEWS_API_KEY`, `FUNDAMENTALS_PROVIDER`, optional AI settings, and optional `CHART_VISION_*` settings. Chart vision supports Qwen through an OpenAI-compatible endpoint using `CHART_VISION_PROVIDER=qwen`, `CHART_VISION_MODEL=qwen3.6-plus`, and optional `CHART_VISION_BASE_URL`. Provider status must disclose whether each provider is live or unavailable. Missing optional providers should be reflected in the response instead of hidden.

## Analysis strategy

The backend separates stock research into independent, explainable modules. Data quality gates confidence; technical scoring is split into trend, momentum, structure, volume, and volatility; risk is scored separately as a penalty; fundamentals and news are included when requested; and market context compares the stock with SPY when benchmark data is available.

Screenshot analysis is separate from provider-backed analysis. It extracts red/green candle geometry and visible price-axis calibration from the uploaded image, uses OCR/VLM only for metadata and axis hints, reconstructs approximate OHLC candles, and maps existing deterministic technical scoring to a structured `buy`, `sell`, `neutral`, or `insufficient` setup action.

Overall scoring is horizon-aware and availability-aware:

- Short horizon emphasizes technicals, news, and market context, then applies the strongest risk penalty.
- Swing horizon balances technicals with fundamentals, news, and market context, then applies a moderate risk penalty.
- Long horizon emphasizes fundamentals while still considering technical condition, news, and market context, then applies the lightest risk penalty.

`diffscore-v1` computes:

```text
base_score =
  sum(weight[horizon, domain] * available[domain] * domain_score[domain])
  / sum(weight[horizon, domain] * available[domain])

final_score = clamp(round(base_score - lambda[horizon] * (100 - risk_score)), 0, 100)
```

Missing domains do not contribute neutral points; their weights are removed from the weighted mean and reflected in confidence through lower provider coverage. Confidence is based on data quality, provider coverage, and agreement between the available domain scores.

## Security and privacy principles

- Do not store screenshots by default.
- Do not put provider API keys in Android code/resources.
- Do not log secrets or raw provider credentials.
- Keep screenshot-derived candles clearly labeled as approximate and unverified.
