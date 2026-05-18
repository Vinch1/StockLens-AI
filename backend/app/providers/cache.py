from __future__ import annotations

import asyncio
import time
from typing import Any, Awaitable, Callable


_ohlcv_cache: dict[tuple[str, str], tuple[float, Any]] = {}
_news_cache: dict[tuple[str, str], tuple[float, Any]] = {}
_fundamentals_cache: dict[tuple[str, str], tuple[float, Any]] = {}

_DEFAULT_TTL = 300


def get_with_cache(
    cache: dict[tuple[str, str], tuple[float, Any]],
    key: tuple[str, str],
    fetcher: Callable[[], Any],
    ttl: float = _DEFAULT_TTL,
) -> Any:
    now = time.time()
    if key in cache:
        cached_at, cached_val = cache[key]
        if now - cached_at < ttl:
            return cached_val
    value = fetcher()
    cache[key] = (now, value)
    return value


async def aget_with_cache(
    cache: dict[tuple[str, str], tuple[float, Any]],
    key: tuple[str, str],
    fetcher: Callable[[], Awaitable[Any]],
    ttl: float = _DEFAULT_TTL,
) -> Any:
    now = time.time()
    if key in cache:
        cached_at, cached_val = cache[key]
        if now - cached_at < ttl:
            return cached_val
    value = await fetcher()
    cache[key] = (now, value)
    return value
