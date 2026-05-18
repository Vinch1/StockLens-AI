# Security and Privacy

## Security Principles

- No secrets in Git.
- Least privilege for any future API keys, service accounts, and CI tokens.
- Redact sensitive values from logs, screenshots, traces, and error messages.
- Treat watchlists, prompts, screenshots, and uploaded files as potentially sensitive user data.

## Environment Variables

Use `.env.example` as the documented template and keep local `.env` files untracked. Required values should have safe defaults where possible.

Live provider configuration must stay on the backend. Do not put provider keys in Android resources, Kotlin source, screenshots, or client logs.

Sensitive examples:

- AI provider keys.
- Market-data provider keys.
- Backend session secrets.
- Database URLs containing usernames or passwords.
- Production endpoint credentials.

## Screenshot Privacy Checklist

Before sharing screenshots or recordings:

1. Use sample symbols and avoid exposing personal watchlists.
2. Confirm no API keys, bearer tokens, account IDs, emails, or personal watchlists are visible.
3. Confirm browser address bars do not expose tokens or private query parameters.
4. Confirm provider dashboards or account pages are not visible.
5. Avoid showing raw provider responses that may be restricted by provider terms.

## Logging Guidance

Log:

- Request IDs.
- Endpoint names.
- Status codes.
- Provider mode (`live` or `unavailable`).
- Timing and coarse error categories.

Do not log:

- Authorization headers.
- Full `.env` values.
- API keys or tokens.
- Raw financial account data.
- Full user prompts unless a redaction layer is in place.

## Dependency Hygiene

- Pin runtime dependencies once implementation begins.
- Use automated dependency scanning in CI where practical.
- Prefer official SDKs and documented provider endpoints.
- Keep generated files, build outputs, and local caches out of Git.

## Incident Response Starting Point

If a secret is committed or exposed:

1. Revoke and rotate the credential immediately.
2. Remove the secret from current code and documentation.
3. Assess whether Git history cleanup is required.
4. Record what was exposed, when, and which systems were reachable.
