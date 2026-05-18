# Roadmap

## Phase 0: Repository Foundation

- Establish documentation for product boundaries, architecture, API contracts, compliance, security, and testing.
- Add environment template, Docker Compose mock profile, and CI hygiene checks.
- Preserve educational-only positioning before implementation expands.

## Phase 1: Mock Prototype

- Implement backend health and mock snapshot endpoints.
- Implement a client view with clear educational-only and mock-mode labels.
- Add deterministic mock fixtures for tests and screenshots.
- Add contract tests for API response shapes.

## Phase 2: Provider Integrations

- Add optional market-data provider integration behind environment flags.
- Add optional AI explanation provider integration with safety wording.
- Add provider attribution and delayed-data labels as required by licenses.
- Expand logs and metrics while preserving redaction requirements.

## Phase 3: Quality and Privacy Hardening

- Add automated secret scanning and dependency checks.
- Add screenshot privacy review steps to release documentation.
- Add structured audit events for mode changes and provider failures.
- Add load and reliability tests for common educational workflows.

## Phase 4: Production Readiness Review

- Conduct legal and compliance review before enabling any production-like financial data workflows.
- Validate provider terms for caching, display, attribution, and redistribution.
- Review privacy policy, retention policy, and incident response plans.
- Confirm the app still does not provide trading, brokerage, or personalized investment advice.
