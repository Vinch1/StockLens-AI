from __future__ import annotations

import base64
import json
import re
from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable

import litellm


@dataclass(frozen=True)
class PriceAxisLabel:
    value: float
    y: float


@dataclass(frozen=True)
class ChartVisionHints:
    detected_ticker: str | None = None
    detected_timeframe: str | None = None
    price_axis_labels: list[PriceAxisLabel] = field(default_factory=list)
    chart_bounds: tuple[int, int, int, int] | None = None


@runtime_checkable
class ChartMetadataProvider(Protocol):
    mode: str

    async def get_chart_hints(self, image_bytes: bytes) -> ChartVisionHints: ...

    def status(self) -> dict[str, object]: ...


class VLMChartMetadataProvider:
    mode = "live"

    def __init__(self, api_key: str, model: str, provider: str) -> None:
        self.api_key = api_key
        self.model = model
        self.provider = provider
        if provider == "openai":
            self._litellm_model = model
        elif provider == "anthropic":
            self._litellm_model = f"anthropic/{model}"
        elif provider == "glm":
            self._litellm_model = f"zai/{model}"
            self._api_base = "https://api.z.ai/api/coding/paas/v4"
        elif provider == "openrouter":
            self._litellm_model = f"openrouter/{model}"
        else:
            self._litellm_model = model

    async def get_chart_hints(self, image_bytes: bytes) -> ChartVisionHints:
        image_b64 = base64.b64encode(image_bytes).decode("ascii")
        prompt = (
            "Return JSON only. Inspect this candlestick chart screenshot and extract only metadata "
            "that is visibly printed in the image. Do not infer or invent candle OHLC values. "
            "Allowed fields: detected_ticker string/null, detected_timeframe string/null, "
            "chart_bounds [left, top, right, bottom] or null, and price_axis_labels as an array "
            "of {value:number,y:number} for visible price-axis labels with their approximate y pixel. "
            "If uncertain, return null or an empty array."
        )
        kwargs: dict[str, object] = {
            "model": self._litellm_model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/png;base64,{image_b64}"},
                        },
                    ],
                }
            ],
            "max_tokens": 500,
            "temperature": 0,
            "api_key": self.api_key,
        }
        if self.provider == "glm":
            kwargs["api_base"] = self._api_base
        try:
            response = await litellm.acompletion(**kwargs)
            content = response.choices[0].message.content or "{}"
            return _parse_hints_json(content)
        except Exception:
            return ChartVisionHints()

    def status(self) -> dict[str, object]:
        return {
            "name": "chart_vision",
            "mode": "live",
            "configured": True,
            "message": f"VLM chart metadata via {self.provider} ({self.model}).",
        }


def _parse_hints_json(content: str) -> ChartVisionHints:
    match = re.search(r"\{.*\}", content, flags=re.DOTALL)
    if not match:
        return ChartVisionHints()
    try:
        payload = json.loads(match.group(0))
    except json.JSONDecodeError:
        return ChartVisionHints()

    labels: list[PriceAxisLabel] = []
    for item in payload.get("price_axis_labels") or []:
        try:
            labels.append(PriceAxisLabel(value=float(item["value"]), y=float(item["y"])))
        except (TypeError, ValueError, KeyError):
            continue

    bounds = payload.get("chart_bounds")
    parsed_bounds: tuple[int, int, int, int] | None = None
    if isinstance(bounds, list | tuple) and len(bounds) == 4:
        try:
            parsed_bounds = tuple(int(value) for value in bounds)  # type: ignore[assignment]
        except (TypeError, ValueError):
            parsed_bounds = None

    return ChartVisionHints(
        detected_ticker=payload.get("detected_ticker"),
        detected_timeframe=payload.get("detected_timeframe"),
        price_axis_labels=labels,
        chart_bounds=parsed_bounds,
    )
