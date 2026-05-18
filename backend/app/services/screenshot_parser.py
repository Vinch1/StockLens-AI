from __future__ import annotations


def parse_placeholder(filename: str | None = None) -> dict[str, object]:
    return {
        "detected_ticker": None,
        "detected_timeframe": None,
        "confidence": "low",
        "needs_confirmation": True,
        "notes": "Screenshot parsing is assistive only. Confirm ticker and timeframe before analysis. Price analysis is calculated from configured market data, not from the screenshot image.",
    }
