from __future__ import annotations

from typing import Literal

_POSITIVE_KEYWORDS = (
    "surge", "rally", "beat", "exceed", "growth", "profit", "gain",
    "bullish", "upgrade", "outperform", "strong", "record high",
    "breakthrough", "soar", "jump", "rise", "climb",
)

_NEGATIVE_KEYWORDS = (
    "drop", "fall", "decline", "loss", "miss", "cut", "bearish",
    "downgrade", "weak", "plunge", "crash", "slide", "tumble",
    "slump", "risk", "concern", "warning", "lawsuit", "fine", "penalty",
)


def classify_sentiment(text: str) -> Literal["positive", "negative", "neutral"]:
    lower = text.lower()
    positive = sum(1 for kw in _POSITIVE_KEYWORDS if kw in lower)
    negative = sum(1 for kw in _NEGATIVE_KEYWORDS if kw in lower)
    if positive > negative:
        return "positive"
    if negative > positive:
        return "negative"
    return "neutral"
