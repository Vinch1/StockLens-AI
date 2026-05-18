from __future__ import annotations

import re
from typing import Literal

from app.models import Timeframe

_FALSE_POSITIVES = frozenset(
    {
        "USD",
        "HIGH",
        "LOW",
        "OPEN",
        "CLOSE",
        "VOLUME",
        "PRICE",
        "MARKET",
        "STOCK",
        "INDEX",
        "DATE",
        "TIME",
        "CHART",
    }
)

_EXCHANGE_PREFIX_RE = re.compile(
    r"""(?:NASDAQ|NYSE|AMEX|OTC)\s*[:\s]\s*([A-Z]{1,5})\b""",
    re.IGNORECASE,
)

_LINE_START_RE = re.compile(r"^([A-Z]{1,5})\b", re.MULTILINE)

_NEAR_PRICE_RE = re.compile(r"\$?\d+[\.,]?\d*\s*(?:USD)?\s*")

_TICKER_NEAR_DOLLAR_RE = re.compile(
    r"(?:^|\s)([A-Z]{1,5})\s*(?:\$|\d{1,4}\.\d{2})",
    re.MULTILINE,
)


def extract_ticker(text: str) -> str | None:
    if not text:
        return None

    candidates: list[str] = []

    for match in _EXCHANGE_PREFIX_RE.finditer(text):
        candidate = match.group(1).upper()
        if candidate not in _FALSE_POSITIVES:
            candidates.append(candidate)

    for match in _LINE_START_RE.finditer(text):
        candidate = match.group(1).upper()
        if candidate not in _FALSE_POSITIVES and candidate not in candidates:
            candidates.append(candidate)

    for match in _TICKER_NEAR_DOLLAR_RE.finditer(text):
        candidate = match.group(1).upper()
        if candidate not in _FALSE_POSITIVES and candidate not in candidates:
            candidates.append(candidate)

    return candidates[0] if candidates else None


_VARIATION_MAP: dict[str, str] = {
    "15 min": "15m",
    "15min": "15m",
    "1 hour": "1h",
    "1hour": "1h",
    "4 hour": "4h",
    "4hour": "4h",
    "daily": "1D",
    "1 day": "1D",
    "1day": "1D",
    "weekly": "1W",
    "1 week": "1W",
    "1week": "1W",
}

_CANONICAL_TIMEFRAMES: dict[str, str] = {
    "15m": "15m",
    "1h": "1h",
    "4h": "4h",
    "1d": "1D",
    "1w": "1W",
}

_STANDARD_VALUES = {"15m", "1h", "4h", "1d", "1w"}

_TIMEFRAME_RE = re.compile(
    r"\b(15m|1h|4h|1D|1W|15\s*min|1\s*hour|4\s*hour|daily|1\s*day|weekly|1\s*week)\b",
    re.IGNORECASE,
)


def extract_timeframe(text: str) -> str | None:
    if not text:
        return None

    for match in _TIMEFRAME_RE.finditer(text):
        raw = match.group(1).lower().strip()
        raw_collapsed = re.sub(r"\s+", "", raw)
        if raw_collapsed in _CANONICAL_TIMEFRAMES:
            return _CANONICAL_TIMEFRAMES[raw_collapsed]
        normalized = raw_collapsed.replace("min", " min").replace("hour", " hour").replace("day", " day").replace("week", " week").strip()
        if normalized in _VARIATION_MAP:
            return _VARIATION_MAP[normalized]
        for variant, standard in _VARIATION_MAP.items():
            variant_collapsed = re.sub(r"\s+", "", variant).lower()
            if raw_collapsed == variant_collapsed:
                return standard

    return None
