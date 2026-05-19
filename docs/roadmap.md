# Roadmap

## Phase 0: Repository Foundation

- Establish documentation for product boundaries, architecture, API contracts, security, and testing.
- Add environment template, Docker Compose backend service, and CI hygiene checks.
- Preserve provider and privacy boundaries before implementation expands.

## Phase 1: Live Provider Prototype

- Implement backend health and analysis endpoints.
- Implement a client view with clear unavailable-provider labels.
- Add deterministic in-memory test fixtures that are not exposed as product data.
- Add contract tests for API response shapes.
- Add data-quality, technical sub-score, risk, market-context, and horizon-aware composite scoring.

## Phase 2: Provider Integrations

- Improve market-data provider reliability and attribution.
- Add optional AI explanation provider integration with safety wording.
- Add provider attribution and delayed-data labels as required by licenses.
- Expand logs and metrics while preserving redaction requirements.

## Phase 3: Quality and Privacy Hardening

- Add automated secret scanning and dependency checks.
- Add screenshot privacy review steps to release documentation.
- Add structured audit events for mode changes and provider failures.
- Add load and reliability tests for common workflows.

## Phase 4: Production Readiness Review

- Review production readiness before enabling any production-like financial data workflows.
- Validate provider terms for caching, display, attribution, and redistribution.
- Review privacy policy, retention policy, and incident response plans.
- Confirm the app still does not place trades or connect brokerage accounts.
