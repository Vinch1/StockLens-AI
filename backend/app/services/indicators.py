from __future__ import annotations

from statistics import mean, pstdev

from app.models import IndicatorSummary, OHLCVBar, SupportResistance


def _round(value: float | None, places: int = 4) -> float | None:
    return None if value is None else round(value, places)


def sma(values: list[float], period: int) -> float | None:
    if len(values) < period:
        return None
    return mean(values[-period:])


def ema_series(values: list[float], period: int) -> list[float]:
    if not values:
        return []
    multiplier = 2 / (period + 1)
    result = [values[0]]
    for value in values[1:]:
        result.append((value * multiplier) + (result[-1] * (1 - multiplier)))
    return result


def rsi(values: list[float], period: int = 14) -> float | None:
    if len(values) <= period:
        return None
    gains: list[float] = []
    losses: list[float] = []
    for current, previous in zip(values[1:], values[:-1]):
        change = current - previous
        gains.append(max(change, 0.0))
        losses.append(abs(min(change, 0.0)))
    avg_gain = mean(gains[-period:])
    avg_loss = mean(losses[-period:])
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def macd(values: list[float]) -> tuple[float | None, float | None, float | None]:
    if len(values) < 26:
        return None, None, None
    ema12 = ema_series(values, 12)
    ema26 = ema_series(values, 26)
    line = [fast - slow for fast, slow in zip(ema12, ema26)]
    signal_series = ema_series(line, 9)
    macd_line = line[-1]
    signal = signal_series[-1]
    return macd_line, signal, macd_line - signal


def bollinger(values: list[float], period: int = 20) -> tuple[float | None, float | None, float | None]:
    if len(values) < period:
        return None, None, None
    window = values[-period:]
    middle = mean(window)
    deviation = pstdev(window)
    return middle + (2 * deviation), middle, middle - (2 * deviation)


def atr(bars: list[OHLCVBar], period: int = 14) -> float | None:
    if len(bars) <= period:
        return None
    ranges: list[float] = []
    for index, bar in enumerate(bars):
        if index == 0:
            ranges.append(bar.high - bar.low)
            continue
        previous_close = bars[index - 1].close
        ranges.append(max(bar.high - bar.low, abs(bar.high - previous_close), abs(bar.low - previous_close)))
    return mean(ranges[-period:])


def volume_ratio(bars: list[OHLCVBar], period: int = 20) -> float | None:
    if len(bars) < period:
        return None
    average_volume = mean(bar.volume for bar in bars[-period:])
    return bars[-1].volume / average_volume if average_volume else None


def support_resistance(bars: list[OHLCVBar], lookback: int = 60) -> SupportResistance:
    if not bars:
        return SupportResistance(support=[], resistance=[])
    window = bars[-lookback:]
    swing_lows: list[float] = []
    swing_highs: list[float] = []
    for index in range(1, len(window) - 1):
        previous_bar, bar, next_bar = window[index - 1], window[index], window[index + 1]
        if bar.low <= previous_bar.low and bar.low <= next_bar.low:
            swing_lows.append(bar.low)
        if bar.high >= previous_bar.high and bar.high >= next_bar.high:
            swing_highs.append(bar.high)
    if not swing_lows:
        swing_lows = [bar.low for bar in window]
    if not swing_highs:
        swing_highs = [bar.high for bar in window]
    current = bars[-1].close
    supports = sorted({round(value, 2) for value in swing_lows if value <= current}, reverse=True)[:2]
    resistances = sorted({round(value, 2) for value in swing_highs if value >= current})[:2]
    if not supports:
        supports = [round(min(bar.low for bar in window), 2)]
    if not resistances:
        resistances = [round(max(bar.high for bar in window), 2)]
    return SupportResistance(support=supports, resistance=resistances)


def compute_indicators(bars: list[OHLCVBar]) -> IndicatorSummary:
    closes = [bar.close for bar in bars]
    ema12_values = ema_series(closes, 12)
    ema26_values = ema_series(closes, 26)
    macd_line, macd_signal, macd_histogram = macd(closes)
    bb_upper, bb_middle, bb_lower = bollinger(closes)
    return IndicatorSummary(
        sma20=_round(sma(closes, 20)),
        sma50=_round(sma(closes, 50)),
        sma200=_round(sma(closes, 200)),
        ema12=_round(ema12_values[-1] if ema12_values else None),
        ema26=_round(ema26_values[-1] if ema26_values else None),
        rsi14=_round(rsi(closes, 14)),
        macd=_round(macd_line),
        macd_signal=_round(macd_signal),
        macd_histogram=_round(macd_histogram),
        bollinger_upper=_round(bb_upper),
        bollinger_middle=_round(bb_middle),
        bollinger_lower=_round(bb_lower),
        atr14=_round(atr(bars, 14)),
        volume_ratio=_round(volume_ratio(bars, 20)),
    )
