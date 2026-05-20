# StockLens AI

StockLens AI is a production-minded MVP for a **stock research and risk-analysis assistant**. It helps users review configured market data, technical indicators, news catalysts, long-term fundamental context, and risk factors.

## What is included

- **Backend:** Python FastAPI service with `/health`, `/api/analyze`, `/api/parse-screenshot`, and `/api/providers/status`.
- **Technical analysis:** deterministic SMA, EMA, RSI, MACD, Bollinger Bands, ATR, volume ratio, support/resistance approximations, and trend/momentum/structure/volume/volatility sub-scores.
- **Risk and context:** data-quality checks, ATR percentage, realized volatility, drawdown, liquidity risk, and relative strength versus SPY.
- **Differential horizon-aware scoring:** short, swing, and long horizons use availability-aware technical/fundamental/news/market-context weights, then apply risk as a penalty instead of treating low risk as a bullish signal.
- **Screenshot analysis:** `/api/parse-screenshot` reconstructs approximate candles from visible chart screenshots and returns a technical `buy`, `sell`, `neutral`, or `insufficient` setup signal with reasons and warnings.
- **Providers:** live/delayed market data and fundamentals through yfinance, plus Finnhub news when `NEWS_API_KEY` is configured.
- **Report summaries:** deterministic conclusions with optional backend-only AI summaries.
- **Android skeleton:** native Kotlin + Jetpack Compose, MVVM, Compose Navigation, Retrofit/OkHttp, DataStore, onboarding, manual analysis, screenshot upload and confirmation, report, watchlist, settings/about.
- **Docs:** product spec, architecture, API contract, security/privacy notes, test plan, and roadmap.

## Repository structure

```text
backend/   FastAPI app, providers, deterministic analysis services, tests
android/   Kotlin + Jetpack Compose Android MVP skeleton
docs/      Product, architecture, API, privacy, test, roadmap docs
```

## Run the backend locally

```bash
cd backend
uv sync
uv run uvicorn app.main:app --reload
```

Then open:

- Health: <http://localhost:8000/health>
- OpenAPI docs: <http://localhost:8000/docs>
- Provider status: <http://localhost:8000/api/providers/status>

Example analysis request:

```bash
curl -X POST http://localhost:8000/api/analyze \
  -H 'Content-Type: application/json' \
  -d '{"ticker":"AAPL","asset_type":"stock","timeframe":"1D","horizon":"swing","include_news":true,"include_fundamentals":true}'
```

## Run backend tests

```bash
cd backend
uv run pytest -q
```

## Run live API request scripts

The scripts in `backend/tests/*_request.py` behave like a frontend client: they send HTTP requests to a running backend and print the JSON response.

Start the backend:

```bash
cd backend
uv run uvicorn app.main:app --reload
```

Then run the request scripts from another terminal:

```bash
cd backend
uv run python tests/health_request.py
uv run python tests/providers_status_request.py
uv run python tests/analyze_request.py --ticker AAPL
uv run python tests/parse_screenshot_request.py tests/chart.png
```

For `/api/parse-screenshot`, place a `.png`, `.jpg`, `.jpeg`, or `.webp` chart image in `backend/tests`. If only one image is present, the image path can be omitted.

## Docker Compose

```bash
docker compose up --build backend
```

The backend listens on <http://localhost:8000>.

## Run the Android app

Start the backend first, then open `android/` in Android Studio and run the `app` configuration on an emulator or connected device.

From the command line, build, install, and launch the frontend with:

```bash
cd android
./gradlew :app:assembleDebug
./gradlew :app:installDebug
adb shell am start -n com.stocklens.ai/.MainActivity
```

The Android emulator default backend URL is `http://10.0.2.2:8000/`, which maps to the host machine's `localhost:8000`. For a physical device, run the backend on a reachable host interface and set the app's API base URL to that machine's LAN address, such as `http://192.168.1.10:8000/`.

Keep live provider API keys on the backend only; do not put secrets in Android resources or Kotlin source.

## Live Data Setup

The backend is configured for real provider integrations by default. yfinance supplies market data and fundamentals without an API key. Finnhub news requires `NEWS_API_KEY`; if the key is absent, the news provider is reported as unavailable and analysis continues with a neutral unavailable-news summary.

Create a local environment file:

```bash
cp .env.example .env
```

Then set:

```env
MARKET_DATA_PROVIDER=yfinance
NEWS_PROVIDER=finnhub
NEWS_API_KEY=your_finnhub_key
FUNDAMENTALS_PROVIDER=yfinance
```

Optional AI explanations require backend-only AI settings such as `AI_PROVIDER=openai`, `AI_API_KEY=...`, and `AI_MODEL=...`. Do not put provider keys in Android resources or Kotlin source.

Optional VLM-assisted chart metadata uses `CHART_VISION_PROVIDER`, `CHART_VISION_API_KEY`, `CHART_VISION_MODEL`, and optional `CHART_VISION_BASE_URL`. The VLM may help identify visible ticker/timeframe, chart bounds, and price-axis labels, but candle OHLC reconstruction and signal scoring remain deterministic. For Qwen Cloud:

```env
CHART_VISION_PROVIDER=qwen
CHART_VISION_API_KEY=your_qwen_key
CHART_VISION_MODEL=qwen3.6-plus
CHART_VISION_BASE_URL=
```

Leave `CHART_VISION_BASE_URL` blank to use `https://dashscope-intl.aliyuncs.com/compatible-mode/v1`; set it explicitly for another OpenAI-compatible Qwen endpoint.

## Analysis method

`/api/analyze` returns a structured report. The backend now separates scoring into:

- **Data quality:** usable/limited/insufficient status based on bar count and OHLCV sanity checks.
- **Technical setup:** trend, momentum, price structure, volume confirmation, and volatility sub-scores.
- **Risk:** ATR percentage, realized volatility, recent drawdown, and average dollar volume.
- **Fundamentals:** growth, profitability, balance sheet, valuation, and cash-flow sub-scores when available.
- **News catalysts:** live provider summary, sentiment, and catalyst items when configured.
- **Market context:** relative strength versus SPY over available 20-bar and 60-bar windows.
- **Overall:** `diffscore-v1` availability-aware composite score, risk penalty, confidence, label, contribution breakdown, and conclusion.

`diffscore-v1` uses the following deterministic formula:

```text
base_score =
  sum(weight[horizon, domain] * available[domain] * domain_score[domain])
  / sum(weight[horizon, domain] * available[domain])

risk_penalty = lambda[horizon] * (100 - risk_safety_score)

final_score = clamp(round(base_score - risk_penalty), 0, 100)
```

News still arrives from the provider as `-50..50` sentiment and is shifted to `0..100` before scoring. Missing or unrequested news/fundamentals and unavailable benchmark context are excluded from the weighted mean rather than filled with neutral `50`s. Confidence is a trust metric:

```text
confidence_score =
  (data_quality_score / 100) * provider_coverage * agreement_factor
```

`provider_coverage` is the share of requested scoring weight backed by available data, and `agreement_factor` falls as available domain scores diverge.

The report is a research aid only. It does not predict returns, rank investments, or instruct users to buy, sell, hold, short, or allocate capital.

`/api/parse-screenshot` is separate from `/api/analyze`: it processes an uploaded candlestick screenshot in memory, reconstructs approximate candle OHLC values from visible pixels and price-axis calibration, and returns a chart-derived technical signal. It does not call yfinance, news, or fundamentals providers. If the chart lacks visible price labels, has too few candles, or extraction confidence is low, the signal is `insufficient`.

## Documentation

- [Product specification](docs/product_spec.md)
- [Architecture](docs/architecture.md)
- [API contract](docs/api_contract.md)
- [Security and privacy](docs/security_privacy.md)
- [Test plan](docs/test_plan.md)
- [Roadmap](docs/roadmap.md)

## Safety boundaries

StockLens AI must not place trades, connect brokerage accounts, scrape TradingView, treat screenshot-derived candles as verified market data, store API keys in client code, or hallucinate prices/news.
