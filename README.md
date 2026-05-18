# StockLens AI

StockLens AI is a production-minded MVP for an **educational stock research and risk-analysis assistant**. It helps users review configured market data, technical indicators, news catalysts, long-term fundamental context, and risk factors without giving stock-picking, auto-trading, or individualized investment advice.

> **Educational information only. Not financial advice.** Markets involve risk. Verify all data before making decisions and consult a qualified professional where appropriate.

## What is included

- **Backend:** Python FastAPI service with `/health`, `/api/analyze`, `/api/parse-screenshot`, and `/api/providers/status`.
- **Technical analysis:** deterministic SMA, EMA, RSI, MACD, Bollinger Bands, ATR, volume ratio, support/resistance approximations, and trend/momentum/structure/volume/volatility sub-scores.
- **Risk and context:** data-quality checks, ATR percentage, realized volatility, drawdown, liquidity risk, and relative strength versus SPY.
- **Horizon-aware scoring:** short, swing, and long horizons use different technical/fundamental/risk/news/market-context weights.
- **Providers:** live/delayed market data and fundamentals through yfinance, plus Finnhub news when `NEWS_API_KEY` is configured.
- **Compliance controls:** deterministic explanations, forbidden-phrase filtering, visible disclaimers, and no buy/sell command language.
- **Android skeleton:** native Kotlin + Jetpack Compose, MVVM, Compose Navigation, Retrofit/OkHttp, DataStore, onboarding disclaimer, manual analysis, screenshot-confirmation placeholder, report, watchlist, settings/about.
- **Docs:** product spec, architecture, API contract, compliance notes, security/privacy notes, test plan, and roadmap.

## Repository structure

```text
backend/   FastAPI app, providers, deterministic analysis services, tests
android/   Kotlin + Jetpack Compose Android MVP skeleton
docs/      Product, architecture, API, compliance, privacy, test, roadmap docs
```

## Run the backend locally

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
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
pytest -q
```

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

## Analysis method

`/api/analyze` returns a structured educational report. The backend now separates scoring into:

- **Data quality:** usable/limited/insufficient status based on bar count and OHLCV sanity checks.
- **Technical setup:** trend, momentum, price structure, volume confirmation, and volatility sub-scores.
- **Risk:** ATR percentage, realized volatility, recent drawdown, and average dollar volume.
- **Fundamentals:** growth, profitability, balance sheet, valuation, and cash-flow sub-scores when available.
- **News catalysts:** live provider summary, sentiment, and catalyst items when configured.
- **Market context:** relative strength versus SPY over available 20-bar and 60-bar windows.
- **Overall:** horizon-aware composite score, confidence, educational label, and disclaimer.

The report is a research aid only. It does not predict returns, rank investments, or instruct users to buy, sell, hold, short, or allocate capital.

## Documentation

- [Product specification](docs/product_spec.md)
- [Architecture](docs/architecture.md)
- [API contract](docs/api_contract.md)
- [Compliance notes](docs/compliance_notes.md)
- [Security and privacy](docs/security_privacy.md)
- [Test plan](docs/test_plan.md)
- [Roadmap](docs/roadmap.md)

## Safety boundaries

StockLens AI must not place trades, connect brokerage accounts, claim certainty, scrape TradingView, use screenshots as market-data sources, store API keys in client code, hallucinate prices/news, or output investment instructions as commands.
