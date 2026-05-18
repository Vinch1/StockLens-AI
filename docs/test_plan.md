# Test Plan

## Goals

- Verify that educational-only positioning appears in user-facing responses.
- Verify mock mode works without secrets or network dependencies.
- Prevent accidental leaks of credentials, account identifiers, and private screenshots.
- Provide CI checks that are useful before backend or Android source exists.

## Test Layers

### Documentation and Hygiene

- Confirm required docs exist.
- Confirm `.env.example` documents safe defaults without real secrets.
- Confirm `.gitignore` excludes local env files, build outputs, IDE state, caches, and screenshots likely to contain private data.

### API Contract Tests

When backend implementation exists, add tests for:

- `GET /health` in mock mode.
- Symbol validation and structured errors.
- Educational disclaimer in snapshot and explanation responses.
- Provider-key absence falling back to mock mode or safe configuration errors.
- Error responses that do not include stack traces or secrets.

### Client Tests

When client implementation exists, add tests for:

- Mock-mode indicator visibility.
- Educational disclaimer visibility.
- Safe rendering of missing, delayed, or mock data.
- Screenshot test fixtures that use synthetic data only.

### Security Tests

- Secret scanning for common key patterns.
- Dependency vulnerability scans once package manifests exist.
- Log redaction tests around headers, environment values, and prompts.

## Manual QA Checklist

1. Start the app with `MOCK_MODE=true` and no provider keys.
2. Confirm health/status reports mock mode.
3. Request a sample stock snapshot.
4. Confirm no response says to buy, sell, or hold.
5. Capture a demo screenshot and verify no secrets or personal data are visible.
6. Review logs for redaction.

## CI Baseline

Until implementation files exist, CI should run lightweight repository hygiene checks that do not require third-party credentials. Future CI can add backend tests, Android linting, and integration tests as source code is added.
