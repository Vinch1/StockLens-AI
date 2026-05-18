# StockLens AI Product Specification

## Purpose

StockLens AI is an educational stock research and risk-analysis assistant. The MVP helps beginners review a ticker's technical setup, mock/demo news catalysts, placeholder long-term fundamentals, and risk factors without producing investment instructions or guaranteed-return claims.

## Positioning and safety boundaries

- Educational research summaries only; not financial, investment, tax, or legal advice.
- No stock-picking, auto-trading, brokerage connection, portfolio allocation, or individualized recommendations.
- No TradingView scraping and no screenshot-derived OHLCV analysis.
- Mock mode must be visible anywhere demo data, demo headlines, or placeholder fundamentals are shown.
- User-facing conclusions should use terms such as research candidate, watchlist candidate, mixed setup, high-risk setup, or needs more confirmation.

## Core user stories

1. **Manual ticker analysis:** As a learner, I enter ticker, asset type, timeframe, and horizon so I can view an educational report backed by configured market data.
2. **Screenshot-assisted input:** As a learner, I can select a chart screenshot to help identify ticker/timeframe, but I must confirm or edit those fields before analysis.
3. **Analysis report:** As a learner, I can review price summary, trend indicators, support/resistance, evidence, risks, news catalyst context, fundamentals context, and a plain-language educational conclusion.
4. **Watchlist:** As a learner, I can save and remove tickers locally for follow-up research.
5. **Settings/about:** As a learner, I can see backend URL, data mode, privacy notes, and educational-only disclaimers.

## MVP functional requirements

- Backend exposes `/health`, `/api/analyze`, `/api/parse-screenshot`, `/api/mock/ohlcv/{ticker}`, and `/api/providers/status`.
- Backend computes SMA 20/50/200, EMA 12/26, RSI 14, MACD, Bollinger Bands, ATR 14, volume ratio, and support/resistance approximations deterministically.
- Backend applies transparent scoring and confidence rules.
- News and fundamentals providers are abstracted and mock-only by default.
- Android uses Kotlin, Jetpack Compose, MVVM, Compose Navigation, Retrofit/OkHttp, and DataStore.
- Android shows loading, empty, error, mock-mode, and disclaimer states.

## Acceptance criteria

- `GET /health` returns status ok and service/version metadata.
- `POST /api/analyze` returns a structured mock analysis for AAPL without hallucinated live prices or live headlines.
- Forbidden investment-advice phrases are detected by backend tests.
- Screenshot flow states that screenshots are assistive only and requires confirmation.
- Watchlist and onboarding acknowledgment are stored locally on device.
- README documents backend, Android, mock mode, and future backend-only provider keys.

## Out of scope

- Live trading, broker account linking, order placement, or account aggregation.
- Personalized portfolio advice or target allocation guidance.
- Claims of predictive certainty, win rates, or guaranteed performance.
- Client-side API keys or direct Android calls to paid market/news providers.
