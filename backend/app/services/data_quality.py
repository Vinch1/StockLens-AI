from __future__ import annotations

from app.models import DataQualitySummary, OHLCVBar
from app.services.scoring import clamp


def assess_data_quality(bars: list[OHLCVBar], minimum_bars: int = 200) -> DataQualitySummary:
    warnings: list[str] = []
    score = 100

    if len(bars) < 2:
        return DataQualitySummary(
            score=0,
            status="insufficient",
            bars_count=len(bars),
            latest_timestamp=bars[-1].timestamp if bars else None,
            warnings=["At least two OHLCV bars are required for analysis."],
        )

    if len(bars) < 30:
        score -= 45
        warnings.append("Fewer than 30 bars are available, so indicator coverage is very limited.")
    elif len(bars) < minimum_bars:
        score -= 20
        warnings.append(f"Fewer than {minimum_bars} bars are available, so long-term trend confidence is reduced.")

    bad_price_count = sum(1 for bar in bars if min(bar.open, bar.high, bar.low, bar.close) <= 0)
    if bad_price_count:
        score -= 40
        warnings.append("One or more bars contain non-positive prices.")

    inconsistent_bars = sum(1 for bar in bars if bar.high < max(bar.open, bar.close) or bar.low > min(bar.open, bar.close))
    if inconsistent_bars:
        score -= 30
        warnings.append("One or more bars have inconsistent high/low values.")

    zero_volume_count = sum(1 for bar in bars[-30:] if bar.volume <= 0)
    if zero_volume_count:
        score -= 10
        warnings.append("Recent volume contains zero or missing values.")

    status = "usable"
    score = clamp(score)
    if score < 50:
        status = "insufficient"
    elif score < 75:
        status = "limited"

    return DataQualitySummary(
        score=score,
        status=status,
        bars_count=len(bars),
        latest_timestamp=bars[-1].timestamp,
        warnings=warnings,
    )
