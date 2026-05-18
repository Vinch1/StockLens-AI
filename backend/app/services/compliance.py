from __future__ import annotations

FORBIDDEN_TERMS = [
    "buy now",
    "sell now",
    "guaranteed",
    "risk-free",
    "sure profit",
    "this stock will",
    "you should invest",
    "all in",
    "100%",
    "can't lose",
    "secret signal",
]

DISCLAIMER = "Educational information only. Not financial advice. Markets involve risk. Verify all data before making decisions."


def contains_forbidden_language(text: str) -> bool:
    lowered = text.lower()
    return any(term in lowered for term in FORBIDDEN_TERMS)


def sanitize_or_fallback(text: str, fallback: str) -> str:
    return fallback if contains_forbidden_language(text) else text
