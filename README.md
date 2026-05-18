# StockLens AI

StockLens AI is a production-minded MVP for an **educational stock research and risk-analysis assistant**. It helps users review mock or configured stock data, technical indicators, news catalysts, long-term fundamental context, and risk factors without giving stock-picking, auto-trading, or individualized investment advice.

> **Educational information only. Not financial advice.** Markets involve risk. Verify all data before making decisions and consult a qualified professional where appropriate.

## What is included

- **Backend:** Python FastAPI service with `/health`, `/api/analyze`, `/api/parse-screenshot`, `/api/mock/ohlcv/{ticker}`, and `/api/providers/status`.
- **Technical analysis:** deterministic SMA, EMA, RSI, MACD, Bollinger Bands, ATR, volume ratio, and support/resistance approximations.
- **Providers:** mock market data, mock news catalysts, and mock fundamentals by default; provider status clearly labels mock/live readiness.
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

Open `android/` in Android Studio or run from a compatible Android/Gradle environment:

```bash
cd android
./gradlew :app:assembleDebug
```

If `./gradlew` reports that Java/Gradle is unavailable, install Android Studio and use its bundled JDK 17 (or install a local JDK 17 plus Android SDK). The lightweight launcher downloads Gradle 8.14.4 on Unix-like systems when a system Gradle is not already installed.

The Android emulator default backend URL is `http://10.0.2.2:8000/`. Keep live provider API keys on the backend only; do not put secrets in Android resources or Kotlin source.

## Mock mode and future live data

Mock mode is the default and requires no credentials. Mock outputs are clearly labeled as demo data. Future live providers should be enabled only through backend environment variables copied from `.env.example`, for example `MARKET_DATA_API_KEY`, `NEWS_API_KEY`, or `FUNDAMENTALS_API_KEY`.

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
