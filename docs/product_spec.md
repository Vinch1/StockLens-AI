# StockLens AI Product Specification

## Purpose

StockLens AI is a stock research and risk-analysis assistant. The MVP helps users review a ticker's technical setup, configured news catalysts, long-term fundamentals, and risk factors.

## Product boundaries

- No auto-trading, brokerage connection, order placement, or account aggregation.
- No TradingView scraping. Screenshot-derived candles are approximate technical-analysis inputs and must be clearly labeled as unverified.

## Core user stories

1. **Manual ticker analysis:** As a user, I enter ticker, asset type, timeframe, and horizon so I can view a report backed by configured market data.
2. **Screenshot-assisted input:** As a learner, I can select a candlestick screenshot to extract approximate candles, ticker/timeframe hints, and a chart-derived technical signal, then confirm or edit detected fields before further analysis.
3. **Analysis report:** As a learner, I can review price summary, trend indicators, support/resistance, evidence, risks, news catalyst context, fundamentals context, and a plain-language conclusion.
4. **Watchlist:** As a learner, I can save and remove tickers locally for follow-up research.
5. **Settings/about:** As a learner, I can see backend URL, data mode, and privacy notes.

## MVP functional requirements

- Backend exposes `/health`, `/api/analyze`, `/api/parse-screenshot`, and `/api/providers/status`.
- Backend `/api/parse-screenshot` decodes images in memory, reconstructs visible candlestick OHLC values when price-axis calibration is available, and returns `buy`, `sell`, `neutral`, or `insufficient` technical setup actions with reasons and warnings.
- Backend computes SMA 20/50/200, EMA 12/26, RSI 14, MACD, Bollinger Bands, ATR 14, volume ratio, support/resistance approximations, risk metrics, and relative-strength context deterministically.
- Backend applies transparent `diffscore-v1` horizon-aware scoring and confidence rules.
- Backend includes data-quality, technical, risk, fundamentals, news, market-context, and overall sections in analysis responses, including an overall score breakdown.
- News and fundamentals providers are abstracted and configured only on the backend.
- Android uses Kotlin, Jetpack Compose, MVVM, Compose Navigation, Retrofit/OkHttp, and DataStore.
- Android shows loading, empty, error, and unavailable-provider states.

## Acceptance criteria

- `GET /health` returns status ok and service/version metadata.
- `POST /api/analyze` returns a structured analysis for AAPL using configured backend providers.
- Analysis responses include trend, momentum, structure, volume, volatility, risk, data-quality, fundamentals, news, market-context evidence, and score contribution details where available.
- Screenshot flow uploads an image, shows extracted candle count, signal, reasons, warnings, and requires confirmation of detected ticker/timeframe.
- Watchlist and onboarding acknowledgment are stored locally on device.
- README documents backend, Android, and backend-only provider key setup.

## Out of scope

- Live trading, broker account linking, order placement, or account aggregation.
- Client-side API keys or direct Android calls to paid market/news providers.
- Treating screenshot-derived candle values as verified market data.
