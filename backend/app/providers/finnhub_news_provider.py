from __future__ import annotations

from datetime import UTC, date, datetime, timedelta

import httpx

from app.models import CatalystType, NewsItem, NewsSummary, Sentiment
from app.providers.cache import _news_cache, aget_with_cache
from app.providers.errors import ProviderDataError, ProviderUnavailableError
from app.services.sentiment import classify_sentiment

_FINNHUB_NEWS_URL = "https://finnhub.io/api/v1/company-news"

_CATALYST_MAP: dict[str, CatalystType] = {
    "earnings": "earnings",
    "revenue": "earnings",
    "quarterly": "earnings",
    "upgrade": "analyst_rating",
    "downgrade": "analyst_rating",
    "rating": "analyst_rating",
    "price target": "analyst_rating",
    "guidance": "guidance",
    "forecast": "guidance",
    "outlook": "guidance",
    "fed": "macro",
    "inflation": "macro",
    "interest rate": "macro",
    "gdp": "macro",
    "macro": "macro",
    "acquisition": "m_and_a",
    "merger": "m_and_a",
    "buyout": "m_and_a",
    "deal": "m_and_a",
    "insider": "insider",
    "sec filing": "insider",
    "form 4": "insider",
}


def _infer_catalyst(text: str) -> CatalystType:
    lower = text.lower()
    for keyword, catalyst in _CATALYST_MAP.items():
        if keyword in lower:
            return catalyst
    return "other"


def _timestamp_to_iso(timestamp: int) -> str:
    return datetime.fromtimestamp(timestamp, tz=UTC).isoformat()


class FinnhubNewsProvider:
    mode = "live"

    def __init__(self, api_key: str) -> None:
        self._api_key = api_key
        self._client: httpx.AsyncClient | None = None

    def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(10.0),
                limits=httpx.Limits(max_connections=20, max_keepalive_connections=10),
            )
        return self._client

    async def get_news(self, ticker: str) -> NewsSummary:
        return await aget_with_cache(
            _news_cache,
            ("news", ticker),
            lambda: self._fetch(ticker),
        )

    async def _fetch(self, ticker: str) -> NewsSummary:
        today = date.today()
        from_date = today - timedelta(days=7)
        params = {
            "symbol": ticker,
            "from": from_date.isoformat(),
            "to": today.isoformat(),
        }
        headers = {"X-Finnhub-Token": self._api_key}

        try:
            client = self._get_client()
            response = await client.get(_FINNHUB_NEWS_URL, params=params, headers=headers)
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 429:
                raise ProviderUnavailableError("Finnhub rate limit exceeded") from exc
            raise ProviderDataError(f"Finnhub returned {exc.response.status_code}") from exc
        except httpx.RequestError as exc:
            raise ProviderUnavailableError(f"Finnhub request failed: {exc}") from exc

        articles = response.json()
        if not articles:
            return NewsSummary(
                sentiment="neutral",
                score=0,
                items=[],
                summary=f"No recent news found for {ticker}.",
            )

        top = articles[:5]
        items: list[NewsItem] = []
        for article in top:
            headline = article.get("headline", "")
            summary = article.get("summary") or headline
            combined = f"{headline} {summary}"
            sentiment: Sentiment = classify_sentiment(combined)
            catalyst = _infer_catalyst(combined)
            items.append(
                NewsItem(
                    title=headline,
                    source=article.get("source", ""),
                    published_at=_timestamp_to_iso(article.get("datetime", 0)),
                    url=article.get("url"),
                    sentiment=sentiment,
                    catalyst_type=catalyst,
                    summary=summary,
                )
            )

        pos = sum(1 for i in items if i.sentiment == "positive")
        neg = sum(1 for i in items if i.sentiment == "negative")
        score = max(-50, min(50, pos * 20 - neg * 20))

        if pos > neg:
            overall: Sentiment = "positive"
        elif neg > pos:
            overall = "negative"
        elif pos == 0 and neg == 0:
            overall = "neutral"
        else:
            overall = "mixed"

        return NewsSummary(
            sentiment=overall,
            score=score,
            items=items,
            summary=f"Recent news for {ticker} shows {overall} sentiment.",
        )

    def status(self) -> dict[str, object]:
        return {
            "name": "news",
            "mode": "live",
            "configured": True,
            "message": "Fetching live news from Finnhub.",
        }
