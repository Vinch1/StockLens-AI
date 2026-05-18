# Compliance Notes

## Educational-Only Disclaimer

StockLens-AI must consistently communicate that it is for education and research practice only. It must not market itself as an investment advisor, brokerage, signal provider, portfolio manager, or trading system.

Recommended wording:

> StockLens-AI is for education only and does not provide investment, financial, legal, or tax advice. Do your own research and consult qualified professionals before making financial decisions.

## Product Guardrails

- Do not tell users to buy, sell, hold, short, or allocate to specific securities.
- Do not rank securities as objectively best or worst investments.
- Do not guarantee returns or imply predictive certainty.
- Avoid personalized financial recommendations based on age, income, risk tolerance, account balances, location, or holdings.
- Mark model-generated outputs as educational explanations, not professional advice.

## Market Data

- Clearly label delayed, stale, unavailable, or provider-sourced market data.
- Respect provider licenses, attribution requirements, and redistribution limits before enabling real provider data.
- Do not cache provider data beyond permitted terms.

## AI Outputs

- Treat AI responses as generated content that may be incomplete or incorrect.
- Add disclaimers near AI-generated summaries.
- Prefer concept explanations, risk-factor summaries, and data literacy guidance over instructions to trade.

## Analysis Outputs

- Scores are educational research signals, not predictions or rankings.
- Overall labels should describe research context, such as watchlist research candidate, mixed research candidate, needs more confirmation, or high-risk setup.
- Technical, fundamentals, risk, news, and market-context sections should show supporting evidence and limitations rather than conclusions that imply certainty.
- Confidence should decrease when data quality is limited, provider sections are unavailable, volatility is elevated, or signals conflict.

## Screenshots and Demos

- Remove or blur names, emails, account identifiers, portfolio balances, API keys, and prompt content that may identify a user.
- Avoid capturing browser address bars containing tokens or query-string secrets.
- Do not show provider dashboards, account pages, raw API responses, or restricted data displays in public demos.

## Records and Auditability

If regulated or production use is later considered, obtain legal review before adding brokerage integrations, portfolio advice, transaction execution, or persistent user financial profiles.
