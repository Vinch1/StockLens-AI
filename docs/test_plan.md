# Test Plan

## Goals

- Verify provider status clearly reports live and unavailable providers.
- Prevent accidental leaks of credentials, account identifiers, and private screenshots.
- Provide CI checks that are useful without committing provider credentials.

## Test Layers

### Documentation and Hygiene

- Confirm required docs exist.
- Confirm `.env.example` documents safe defaults without real secrets.
- Confirm `.gitignore` excludes local env files, build outputs, IDE state, caches, and screenshots likely to contain private data.

### API Contract Tests

Automated pytest coverage should verify:

- `GET /health`.
- Symbol validation and structured errors.
- Provider-key absence returning safe unavailable-provider summaries or provider status.
- Analysis responses include `data_quality`, `risk`, `market_context`, technical sub-scores, and fundamentals sub-scores.
- Screenshot parsing returns extraction summary, candles, and structured signal.
- Synthetic candlestick screenshots reconstruct known OHLC values within tolerance and produce expected setup actions.
- Missing price axis, invalid base64, cropped charts, too few candles, and low-confidence extraction return `insufficient`.
- Short, swing, and long horizons use different composite scoring weights.
- Error responses that do not include stack traces or secrets.

### Live API Request Scripts

The `backend/tests/*_request.py` scripts act like a frontend client: they send real HTTP requests to a running backend with `httpx` and print the JSON response. These scripts are for local manual checks and are intentionally separate from pytest unit tests.

Start the backend first:

```bash
cd backend
uv run uvicorn app.main:app --reload
```

Then run one or more request scripts from another terminal:

```bash
cd backend
uv run python tests/health_request.py
uv run python tests/providers_status_request.py
uv run python tests/analyze_request.py --ticker AAPL --timeframe 1D --horizon swing
uv run python tests/parse_screenshot_request.py tests/chart.png
```

For screenshot parsing, place a `.png`, `.jpg`, `.jpeg`, or `.webp` chart image in `backend/tests`. If only one image is present, the screenshot script can be run without an image argument:

```bash
uv run python tests/parse_screenshot_request.py
```

All request scripts default to `http://127.0.0.1:8000`. Override this with `--base-url` or `STOCKLENS_API_BASE_URL`:

```bash
STOCKLENS_API_BASE_URL=http://localhost:8000 uv run python tests/analyze_request.py
```

### Client Tests

When client implementation exists, add tests for:

- Safe rendering of missing, delayed, unavailable, or live provider data.
- Screenshot upload, loading, signal rendering, warning, and insufficient states.
- Screenshot test fixtures that do not expose secrets or personal data.

### Security Tests

- Secret scanning for common key patterns.
- Dependency vulnerability scans once package manifests exist.
- Log redaction tests around headers, environment values, and prompts.

## Manual QA Checklist

1. Start the backend with `.env` configured for yfinance and, optionally, `NEWS_API_KEY`.
2. Run `uv run python tests/health_request.py` and confirm the service responds with `status: ok`.
3. Run `uv run python tests/providers_status_request.py` and confirm market and fundamentals are live and news is live or unavailable.
4. Run `uv run python tests/analyze_request.py --ticker AAPL` and confirm a sample stock analysis response.
5. Confirm the analysis response includes data quality, technical sub-scores, risk, fundamentals, news, market context, and overall sections.
6. Place a clear candlestick screenshot in `backend/tests`, then run `uv run python tests/parse_screenshot_request.py tests/<image-name>`.
7. Confirm the screenshot response shows candle count, signal, reasons, and warnings.
8. Capture a demo screenshot and verify no secrets or personal data are visible.
9. Review logs for redaction.

## CI Baseline

CI should run automated backend tests that do not require third-party credentials:

```bash
cd backend
uv run pytest -q
```

The live request scripts are not CI tests because they require a running backend and may depend on local provider configuration.
