from __future__ import annotations

import base64
from binascii import Error as Base64Error

from app.models import (
    ScreenshotExtractionSummary,
    ScreenshotParseResponse,
    ScreenshotSignal,
)
from app.providers.chart_metadata_provider import ChartMetadataProvider, ChartVisionHints
from app.providers.vision_provider import TesseractVisionProvider, VisionProvider
from app.services.candlestick_extractor import analyze_candlestick_image
from app.services.ticker_extraction import extract_ticker, extract_timeframe

vision_provider: VisionProvider = TesseractVisionProvider()

_NO_IMAGE_NOTE = (
    "No screenshot image was provided. Upload a visible candlestick screenshot to extract approximate candles."
)
_ANALYSIS_NOTE = (
    "Screenshot-derived candles are approximate. Confirm ticker and timeframe, and verify the source chart before using the signal."
)


async def parse_screenshot(
    image_base64: str | None = None,
    filename: str | None = None,
    vision_provider: VisionProvider | None = None,
    chart_metadata_provider: ChartMetadataProvider | None = None,
) -> ScreenshotParseResponse:
    if not image_base64:
        return _placeholder_response(_NO_IMAGE_NOTE)

    provider = vision_provider or globals()["vision_provider"]

    try:
        image_bytes = _decode_image_base64(image_base64)
        text = await provider.detect_text(image_bytes)
        hints = ChartVisionHints()
        if chart_metadata_provider is not None:
            hints = await chart_metadata_provider.get_chart_hints(image_bytes)

        ticker = extract_ticker(text) or hints.detected_ticker
        timeframe = extract_timeframe(text) or hints.detected_timeframe
        text_blocks = []
        if hasattr(provider, "detect_text_blocks"):
            text_blocks = await provider.detect_text_blocks(image_bytes)  # type: ignore[attr-defined]

        extraction, candles, signal = analyze_candlestick_image(
            image_bytes,
            text_blocks=text_blocks,
            chart_hints=hints,
        )
        conf = _top_level_confidence(ticker, extraction.calibration_confidence, signal.confidence, candles)
        ticker_note = f"Detected ticker: {ticker}." if ticker else "No ticker detected."
        timeframe_note = f" Detected timeframe: {timeframe}." if timeframe else ""
        return ScreenshotParseResponse(
            detected_ticker=ticker,
            detected_timeframe=timeframe,
            confidence=conf,
            needs_confirmation=True,
            notes=f"{ticker_note}{timeframe_note} {_ANALYSIS_NOTE}",
            extraction=extraction,
            candles=candles,
            signal=signal,
        )
    except (Base64Error, ValueError) as exc:
        return _placeholder_response(str(exc))
    except Exception:
        return _placeholder_response("Screenshot parsing failed. Try a clearer image with visible candles and price labels.")


def _decode_image_base64(image_base64: str) -> bytes:
    payload = image_base64.split(",", 1)[1] if "," in image_base64 and "base64" in image_base64[:64] else image_base64
    return base64.b64decode(payload, validate=True)


def _placeholder_response(notes: str) -> ScreenshotParseResponse:
    extraction = ScreenshotExtractionSummary(
        candle_count=0,
        calibration_confidence="low",
        warnings=[notes],
    )
    signal = ScreenshotSignal(
        action="insufficient",
        score=0,
        confidence="low",
        reasons=["No reliable candlestick signal could be produced from the screenshot."],
        risk_warnings=[notes],
    )
    return ScreenshotParseResponse(
        detected_ticker=None,
        detected_timeframe=None,
        confidence="low",
        needs_confirmation=True,
        notes=notes,
        extraction=extraction,
        candles=[],
        signal=signal,
    )


def _top_level_confidence(
    ticker: str | None,
    calibration_confidence: str,
    signal_confidence: str,
    candles: list[object],
) -> str:
    if ticker and calibration_confidence == "high" and signal_confidence == "high":
        return "high"
    if ticker or candles or signal_confidence == "medium":
        return "medium"
    return "low"
