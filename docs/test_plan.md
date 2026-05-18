# Test Plan

## Goals

- Verify that educational-only positioning appears in user-facing responses.
- Verify provider status clearly reports live and unavailable providers.
- Prevent accidental leaks of credentials, account identifiers, and private screenshots.
- Provide CI checks that are useful without committing provider credentials.

## Test Layers

### Documentation and Hygiene

- Confirm required docs exist.
- Confirm `.env.example` documents safe defaults without real secrets.
- Confirm `.gitignore` excludes local env files, build outputs, IDE state, caches, and screenshots likely to contain private data.

### API Contract Tests

When backend implementation exists, add tests for:

- `GET /health`.
- Symbol validation and structured errors.
- Educational disclaimer in snapshot and explanation responses.
- Provider-key absence returning safe unavailable-provider summaries or provider status.
- Analysis responses include `data_quality`, `risk`, `market_context`, technical sub-scores, and fundamentals sub-scores.
- Short, swing, and long horizons use different composite scoring weights.
- Error responses that do not include stack traces or secrets.

### Client Tests

When client implementation exists, add tests for:

- Educational disclaimer visibility.
- Safe rendering of missing, delayed, unavailable, or live provider data.
- Screenshot test fixtures that do not expose secrets or personal data.

### Security Tests

- Secret scanning for common key patterns.
- Dependency vulnerability scans once package manifests exist.
- Log redaction tests around headers, environment values, and prompts.

## Manual QA Checklist

1. Start the backend with `.env` configured for yfinance and, optionally, `NEWS_API_KEY`.
2. Confirm `/api/providers/status` reports market and fundamentals as live and news as live or unavailable.
3. Request a sample stock analysis.
4. Confirm response includes data quality, technical sub-scores, risk, fundamentals, news, market context, and overall sections.
5. Confirm no response says to buy, sell, or hold.
6. Capture a demo screenshot and verify no secrets or personal data are visible.
7. Review logs for redaction.

## CI Baseline

Until implementation files exist, CI should run lightweight repository hygiene checks that do not require third-party credentials. Future CI can add backend tests, Android linting, and integration tests as source code is added.
