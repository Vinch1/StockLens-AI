from __future__ import annotations

import base64

from app.providers.vision_provider import MockVisionProvider, VisionProvider
from app.services.ticker_extraction import extract_ticker, extract_timeframe

vision_provider: VisionProvider = MockVisionProvider()


def parse_screenshot(
    image_base64: str | None = None,
    filename: str | None = None,
    vision_provider: VisionProvider | None = None,
) -> dict[str, object]:
    if not image_base64:
        return {
            "detected_ticker": None,
            "detected_timeframe": None,
            "confidence": "low",
            "needs_confirmation": True,
            "notes": "Screenshot parsing is assistive only. Confirm ticker and timeframe before analysis. Price analysis is calculated from configured market data, not from the screenshot image.",
        }

    provider = vision_provider or globals()["vision_provider"]

    try:
        image_bytes = base64.b64decode(image_base64)
        text = provider.detect_text(image_bytes)

        ticker = extract_ticker(text)
        timeframe = extract_timeframe(text)
        confidence = "medium" if ticker else "low"

        ticker_note = f"OCR-detected ticker: {ticker}." if ticker else "No ticker detected via OCR."
        timeframe_note = f" OCR-detected timeframe: {timeframe}." if timeframe else ""

        return {
            "detected_ticker": ticker,
            "detected_timeframe": timeframe,
            "confidence": confidence,
            "needs_confirmation": True,
            "notes": f"{ticker_note}{timeframe_note} Please confirm before analysis. Price analysis is calculated from configured market data, not from the screenshot image.",
        }
    except Exception:
        return {
            "detected_ticker": None,
            "detected_timeframe": None,
            "confidence": "low",
            "needs_confirmation": True,
            "notes": "Screenshot parsing is assistive only. Confirm ticker and timeframe before analysis. Price analysis is calculated from configured market data, not from the screenshot image.",
        }
