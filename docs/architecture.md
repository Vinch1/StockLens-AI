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
  ├─ /api/mock/ohlcv/{ticker}
  ├─ /api/providers/status
  ├─ deterministic indicator/scoring services
  ├─ compliance/explanation services
  └─ mock provider abstractions for market, news, fundamentals
```

## Backend communication

The Android app posts `AnalyzeRequest` JSON to `/api/analyze` and renders the structured `AnalyzeResponse`. In emulator development, the default backend base URL is `http://10.0.2.2:8000/`.

## Data model categories

- Request metadata: ticker, asset type, timeframe, horizon, include news, include fundamentals.
- Market bars: timestamp, open, high, low, close, volume.
- Technical analysis: setup label, score, confidence, indicators, support/resistance, evidence, risks.
- News catalysts: title, source, date, URL, summary, sentiment, catalyst type.
- Fundamentals: quality label, score, nullable metrics, summary.
- Overall: educational label, score, confidence, conclusion, disclaimer.

## Provider strategy

Mock providers are deterministic and default-on. Future live providers must be backend-only and configured through environment variables such as `MARKET_DATA_API_KEY`, `NEWS_API_KEY`, and `FUNDAMENTALS_API_KEY`. Provider status must disclose whether data is mock or live.

## Security and privacy principles

- Do not store screenshots by default.
- Do not put provider API keys in Android code/resources.
- Do not log secrets or raw provider credentials.
- Label mock data clearly.
- Keep screenshots assistive only; never infer OHLCV from images for analysis.
