from __future__ import annotations

import re
from dataclasses import dataclass
from io import BytesIO
from statistics import mean

import cv2
import numpy as np
from PIL import Image

from app.models import (
    OHLCVBar,
    ScreenshotCandle,
    ScreenshotExtractionSummary,
    ScreenshotSignal,
)
from app.providers.chart_metadata_provider import ChartVisionHints, PriceAxisLabel
from app.providers.vision_provider import VisionTextBlock
from app.services.indicators import compute_indicators, support_resistance
from app.services.scoring import (
    technical_evidence,
    technical_risks,
    technical_score_from_subscores,
    technical_subscores,
)

_PRICE_LABEL_RE = re.compile(
    r"^\$?\s*([-+]?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?)\s*$"
)

_SCREENSHOT_WARNING = (
    "Screenshot-derived candles are approximate and must be verified against a reliable market data source."
)


@dataclass(frozen=True)
class _PixelCandle:
    center_x: float
    high_y: float
    low_y: float
    body_top_y: float
    body_bottom_y: float
    direction: str
    confidence_score: float


@dataclass(frozen=True)
class _Calibration:
    slope: float
    intercept: float
    confidence: str

    def price_at_y(self, y: float) -> float:
        return (self.slope * y) + self.intercept


def analyze_candlestick_image(
    image_bytes: bytes,
    text_blocks: list[VisionTextBlock] | None = None,
    chart_hints: ChartVisionHints | None = None,
) -> tuple[ScreenshotExtractionSummary, list[ScreenshotCandle], ScreenshotSignal]:
    rgb = _decode_rgb(image_bytes)
    green_mask, red_mask = _candle_color_masks(rgb)
    color_mask = green_mask | red_mask
    pixel_candles = _extract_pixel_candles(color_mask, green_mask, red_mask, rgb.shape[1])
    warnings: list[str] = []

    if not pixel_candles:
        warnings.append("No candlestick bodies or wicks were detected.")
        return _insufficient_result(0, "low", warnings)

    colored_bbox = _mask_bbox(color_mask)
    labels = _price_labels_from_blocks(text_blocks or [], rgb.shape[1], colored_bbox)
    labels.extend((chart_hints or ChartVisionHints()).price_axis_labels)
    calibration, calibration_warning = _build_calibration(labels)
    if calibration_warning:
        warnings.append(calibration_warning)

    if calibration is None:
        warnings.append("Visible numeric price-axis labels or configured VLM axis hints are required.")
        return _insufficient_result(len(pixel_candles), "low", warnings)

    candles = _calibrated_candles(pixel_candles, calibration)
    extraction_confidence = _combine_confidence(
        [candle.confidence_score for candle in pixel_candles],
        calibration.confidence,
    )

    if len(candles) < 30:
        warnings.append("Fewer than 30 candles were extracted, so technical setup analysis is insufficient.")
    if extraction_confidence == "low":
        warnings.append("Candle extraction confidence is low.")

    signal = _signal_from_candles(candles, extraction_confidence, warnings)
    extraction = ScreenshotExtractionSummary(
        candle_count=len(candles),
        calibration_confidence=calibration.confidence,
        warnings=warnings,
    )
    return extraction, candles, signal


def _decode_rgb(image_bytes: bytes) -> np.ndarray:
    try:
        image = Image.open(BytesIO(image_bytes)).convert("RGB")
    except Exception as exc:
        raise ValueError("Invalid image data.") from exc
    width, height = image.size
    if width < 120 or height < 120:
        raise ValueError("Image is too small for candlestick extraction.")
    if width * height > 16_000_000:
        raise ValueError("Image is too large for in-memory screenshot analysis.")
    return np.asarray(image)


def _candle_color_masks(rgb: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
    hue = hsv[:, :, 0]
    saturation = hsv[:, :, 1]
    value = hsv[:, :, 2]

    red_hsv = (((hue <= 10) | (hue >= 165)) & (saturation >= 45) & (value >= 45))
    green_hsv = ((hue >= 35) & (hue <= 95) & (saturation >= 35) & (value >= 45))

    r = rgb[:, :, 0].astype(np.int16)
    g = rgb[:, :, 1].astype(np.int16)
    b = rgb[:, :, 2].astype(np.int16)
    red_rgb = (r >= 110) & (r > g + 25) & (r > b + 15)
    green_rgb = (g >= 100) & (g > r + 20) & (g >= b)
    return green_hsv | green_rgb, red_hsv | red_rgb


def _extract_pixel_candles(
    color_mask: np.ndarray,
    green_mask: np.ndarray,
    red_mask: np.ndarray,
    image_width: int,
) -> list[_PixelCandle]:
    column_counts = color_mask.sum(axis=0)
    active_columns = column_counts >= 3
    runs = _contiguous_runs(active_columns)
    candles: list[_PixelCandle] = []
    max_width = max(14, int(image_width * 0.08))

    for x0, x1 in runs:
        width = x1 - x0 + 1
        if width > max_width:
            continue
        region = color_mask[:, x0:x1 + 1]
        ys, xs = np.where(region)
        area = len(ys)
        if area < 6:
            continue

        height = int(ys.max() - ys.min() + 1)
        if height < 4:
            continue

        row_counts = np.bincount(ys, minlength=region.shape[0])
        max_count = int(row_counts.max()) if len(row_counts) else 0
        body_threshold = max(2, int(max_count * 0.55))
        body_ys = np.where(row_counts >= body_threshold)[0]
        if len(body_ys) == 0:
            body_top = float(np.median(ys))
            body_bottom = body_top
        else:
            body_top = float(body_ys.min())
            body_bottom = float(body_ys.max())

        group_green = int(green_mask[:, x0:x1 + 1].sum())
        group_red = int(red_mask[:, x0:x1 + 1].sum())
        if abs(group_green - group_red) <= max(2, area * 0.08):
            direction = "doji"
        else:
            direction = "bullish" if group_green > group_red else "bearish"

        confidence = 0.58
        if width >= 3:
            confidence += 0.10
        if len(body_ys) >= 2:
            confidence += 0.12
        if area >= 18:
            confidence += 0.08
        if height >= 10:
            confidence += 0.07

        candles.append(
            _PixelCandle(
                center_x=float(x0 + xs.mean()),
                high_y=float(ys.min()),
                low_y=float(ys.max()),
                body_top_y=body_top,
                body_bottom_y=body_bottom,
                direction=direction,
                confidence_score=min(confidence, 0.95),
            )
        )

    return sorted(candles, key=lambda candle: candle.center_x)


def _contiguous_runs(values: np.ndarray) -> list[tuple[int, int]]:
    runs: list[tuple[int, int]] = []
    start: int | None = None
    for index, active in enumerate(values):
        if active and start is None:
            start = index
        elif not active and start is not None:
            runs.append((start, index - 1))
            start = None
    if start is not None:
        runs.append((start, len(values) - 1))
    return runs


def _mask_bbox(mask: np.ndarray) -> tuple[int, int, int, int] | None:
    ys, xs = np.where(mask)
    if len(xs) == 0:
        return None
    return int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())


def _price_labels_from_blocks(
    blocks: list[VisionTextBlock],
    image_width: int,
    colored_bbox: tuple[int, int, int, int] | None,
) -> list[PriceAxisLabel]:
    if not blocks or colored_bbox is None:
        return []
    left, top, right, bottom = colored_bbox
    labels: list[tuple[float, PriceAxisLabel]] = []
    for block in blocks:
        match = _PRICE_LABEL_RE.match(block.text.replace(" ", ""))
        if not match:
            continue
        center_y = block.top + (block.height / 2)
        near_chart_y = top - 30 <= center_y <= bottom + 30
        near_price_axis = block.left >= right - 8 or block.left >= image_width * 0.65 or block.left <= left + 8
        if not near_chart_y or not near_price_axis:
            continue
        try:
            value = float(match.group(1).replace(",", ""))
        except ValueError:
            continue
        labels.append((block.confidence, PriceAxisLabel(value=value, y=center_y)))

    deduped: list[PriceAxisLabel] = []
    for _, label in sorted(labels, key=lambda item: item[0], reverse=True):
        if all(abs(label.y - existing.y) > 4 for existing in deduped):
            deduped.append(label)
    return deduped


def _build_calibration(labels: list[PriceAxisLabel]) -> tuple[_Calibration | None, str | None]:
    clean_labels = [
        label for label in labels
        if np.isfinite(label.value) and np.isfinite(label.y)
    ]
    if len(clean_labels) < 2:
        return None, "Price-axis calibration failed because fewer than two numeric labels were found."

    y_values = np.array([label.y for label in clean_labels], dtype=float)
    price_values = np.array([label.value for label in clean_labels], dtype=float)
    if float(y_values.max() - y_values.min()) < 20:
        return None, "Price-axis calibration failed because numeric labels are too close together."

    slope, intercept = np.polyfit(y_values, price_values, 1)
    if slope >= 0:
        return None, "Price-axis calibration failed because price labels do not decrease from top to bottom."

    predicted = (slope * y_values) + intercept
    value_span = max(float(price_values.max() - price_values.min()), 1.0)
    relative_error = float(np.mean(np.abs(predicted - price_values)) / value_span)
    confidence = "medium"
    if len(clean_labels) >= 3 and relative_error < 0.03:
        confidence = "high"
    elif relative_error > 0.08:
        confidence = "low"

    return _Calibration(float(slope), float(intercept), confidence), None


def _calibrated_candles(pixel_candles: list[_PixelCandle], calibration: _Calibration) -> list[ScreenshotCandle]:
    calibration_score = _confidence_score(calibration.confidence)
    candles: list[ScreenshotCandle] = []
    for index, candle in enumerate(pixel_candles):
        high = calibration.price_at_y(candle.high_y)
        low = calibration.price_at_y(candle.low_y)
        if candle.direction == "bullish":
            open_price = calibration.price_at_y(candle.body_bottom_y)
            close_price = calibration.price_at_y(candle.body_top_y)
        elif candle.direction == "bearish":
            open_price = calibration.price_at_y(candle.body_top_y)
            close_price = calibration.price_at_y(candle.body_bottom_y)
        else:
            midpoint = (candle.body_top_y + candle.body_bottom_y) / 2
            open_price = calibration.price_at_y(midpoint)
            close_price = open_price

        confidence = _confidence_label(min(candle.confidence_score, calibration_score))
        candles.append(
            ScreenshotCandle(
                index=index,
                open=round(open_price, 4),
                high=round(max(high, open_price, close_price), 4),
                low=round(min(low, open_price, close_price), 4),
                close=round(close_price, 4),
                direction=candle.direction,  # type: ignore[arg-type]
                confidence=confidence,
            )
        )
    return candles


def _signal_from_candles(
    candles: list[ScreenshotCandle],
    extraction_confidence: str,
    extraction_warnings: list[str],
) -> ScreenshotSignal:
    base_warning = [_SCREENSHOT_WARNING]
    if len(candles) < 30 or extraction_confidence == "low":
        reasons = ["Candlestick extraction was not strong enough to produce a chart-derived signal."]
        return ScreenshotSignal(
            action="insufficient",
            score=0,
            confidence="low",
            reasons=reasons,
            risk_warnings=[*base_warning, *extraction_warnings],
        )

    bars = [
        OHLCVBar(
            timestamp=str(candle.index),
            open=candle.open,
            high=candle.high,
            low=candle.low,
            close=candle.close,
            volume=0,
        )
        for candle in candles
    ]
    indicators = compute_indicators(bars)
    levels = support_resistance(bars)
    subscores = technical_subscores(indicators, bars[-1].close, bars[-2].close, levels)
    score = technical_score_from_subscores(subscores)

    if score >= 63:
        action = "buy"
    elif score <= 42:
        action = "sell"
    else:
        action = "neutral"

    reasons = [
        f"Chart-derived technical score is {score}/100.",
        *technical_evidence(indicators, bars[-1].close)[:4],
    ]
    risk_warnings = [
        *base_warning,
        *technical_risks(indicators, bars[-1].close)[:4],
        *extraction_warnings,
    ]
    return ScreenshotSignal(
        action=action,  # type: ignore[arg-type]
        score=score,
        confidence=extraction_confidence,
        reasons=reasons,
        risk_warnings=risk_warnings,
    )


def _combine_confidence(candle_scores: list[float], calibration_confidence: str) -> str:
    if not candle_scores:
        return "low"
    combined = min(mean(candle_scores), _confidence_score(calibration_confidence))
    return _confidence_label(combined)


def _confidence_score(confidence: str) -> float:
    return {"high": 0.9, "medium": 0.7, "low": 0.35}.get(confidence, 0.35)


def _confidence_label(score: float) -> str:
    if score >= 0.78:
        return "high"
    if score >= 0.55:
        return "medium"
    return "low"


def _insufficient_result(
    candle_count: int,
    calibration_confidence: str,
    warnings: list[str],
) -> tuple[ScreenshotExtractionSummary, list[ScreenshotCandle], ScreenshotSignal]:
    extraction = ScreenshotExtractionSummary(
        candle_count=candle_count,
        calibration_confidence=calibration_confidence,
        warnings=warnings,
    )
    signal = ScreenshotSignal(
        action="insufficient",
        score=0,
        confidence="low",
        reasons=["Candlestick extraction was not strong enough to produce a chart-derived signal."],
        risk_warnings=[_SCREENSHOT_WARNING, *warnings],
    )
    return extraction, [], signal
