# StockLens AI Architecture

## Overview

StockLens AI is a native Android client plus a Python FastAPI backend. The backend owns market/news/fundamental provider access, deterministic technical analysis, compliance filtering, and response shaping. The Android app renders reports and stores only lightweight local preferences/watchlist data.

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
  ├─ deterministic indicator/risk/scoring services
  ├─ compliance/explanation services
  └─ backend-only provider abstractions for market, news, fundamentals, and optional AI explanations
```

## Backend communication

The Android app posts `AnalyzeRequest` JSON to `/api/analyze` and renders the structured `AnalyzeResponse`. In emulator development, the default backend base URL is `http://10.0.2.2:8000/`.

## Data model categories

- Request metadata: ticker, asset type, timeframe, horizon, include news, include fundamentals.
- Market bars: timestamp, open, high, low, close, volume.
- Data quality: bar count, usable/limited/insufficient status, and warnings.
- Technical analysis: setup label, score, confidence, indicators, trend/momentum/structure/volume/volatility sub-scores, support/resistance, evidence, risks.
- Risk: ATR percentage, realized volatility, recent drawdown, average dollar volume, risk level, and warnings.
- News catalysts: title, source, date, URL, summary, sentiment, catalyst type.
- Fundamentals: quality label, score, growth/profitability/balance-sheet/valuation/cash-flow sub-scores, nullable metrics, summary.
- Market context: benchmark, relative strength windows, context score, summary.
- Overall: horizon-aware educational label, score, confidence, conclusion, disclaimer.

## Provider strategy

Providers are backend-only and configured through environment variables such as `MARKET_DATA_PROVIDER`, `NEWS_PROVIDER`, `NEWS_API_KEY`, `FUNDAMENTALS_PROVIDER`, and optional AI settings. Provider status must disclose whether each provider is live or unavailable. Missing optional providers should be reflected in the response instead of hidden.

## Analysis strategy

The backend separates stock research into independent, explainable modules. Data quality gates confidence; technical scoring is split into trend, momentum, structure, volume, and volatility; risk is scored separately; fundamentals and news are included when requested; and market context compares the stock with SPY when benchmark data is available.

Overall scoring is horizon-aware:

- Short horizon emphasizes technicals, risk, news, and market context.
- Swing horizon balances technicals with fundamentals, risk, news, and market context.
- Long horizon emphasizes fundamentals while still considering technical condition, risk, news, and market context.

## Security and privacy principles

- Do not store screenshots by default.
- Do not put provider API keys in Android code/resources.
- Do not log secrets or raw provider credentials.
- Keep screenshots assistive only; never infer OHLCV from images for analysis.
