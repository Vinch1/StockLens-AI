from __future__ import annotations

import base64
import json
import re
from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable

from app.providers.litellm_logging import suppress_litellm_debug_info, suppress_litellm_optional_dependency_warnings

suppress_litellm_optional_dependency_warnings()

import litellm

suppress_litellm_debug_info(litellm)

_QWEN_OPENAI_COMPATIBLE_BASE_URL = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"


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

    def __init__(self, api_key: str, model: str, provider: str, api_base: str = "") -> None:
        self.api_key = api_key
        self.model = model
        self.provider = provider
        self.api_base = api_base
        if provider == "openai":
            self._litellm_model = model
        elif provider == "anthropic":
            self._litellm_model = f"anthropic/{model}"
        elif provider == "glm":
            self._litellm_model = f"zai/{model}"
            self.api_base = api_base or "https://api.z.ai/api/coding/paas/v4"
        elif provider == "qwen":
            self._litellm_model = f"openai/{model}"
            self.api_base = api_base or _QWEN_OPENAI_COMPATIBLE_BASE_URL
        elif provider == "openrouter":
            self._litellm_model = f"openrouter/{model}"
        else:
            self._litellm_model = model

    async def get_chart_hints(self, image_bytes: bytes) -> ChartVisionHints:
        image_b64 = base64.b64encode(image_bytes).decode("ascii")
        prompt = (
            "You are extracting metadata from a candlestick chart screenshot for a deterministic "
            "computer-vision pipeline. Return exactly one valid JSON object and no Markdown, code fences, "
            "comments, or explanatory text.\n\n"
            "Schema:\n"
            "{\n"
            '  "detected_ticker": string|null,\n'
            '  "detected_timeframe": string|null,\n'
            '  "chart_bounds": [left, top, right, bottom]|null,\n'
            '  "price_axis_labels": [{"value": number, "y": number}]\n'
            "}\n\n"
            "Rules:\n"
            "- Extract only text and geometry visibly present in the image.\n"
            "- Do not infer or invent candle OHLC values, future movement, signals, or missing axis labels.\n"
            "- Use pixel coordinates relative to the original image: x increases left-to-right, y increases top-to-bottom.\n"
            "- chart_bounds should tightly cover the candle plotting area, excluding sidebars, toolbars, and price-label text.\n"
            "- price_axis_labels should include only visible numeric price labels from the y-axis, not candle prices or indicators.\n"
            "- For each price label, y is the vertical center of the visible label text in pixels.\n"
            "- Preserve decimal precision from the label when visible; remove currency symbols and commas.\n"
            "- If fewer than two reliable y-axis labels are visible, return an empty price_axis_labels array.\n"
            "- If ticker or timeframe is ambiguous, use null.\n"
            "- If chart bounds are ambiguous, use null.\n"
            "- Do not add fields outside the schema."
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
        if self.api_base:
            kwargs["api_base"] = self.api_base
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
    if not isinstance(payload, dict):
        return ChartVisionHints()

    labels: list[PriceAxisLabel] = []
    for item in payload.get("price_axis_labels") or []:
        if not isinstance(item, dict):
            continue
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
        detected_ticker=_clean_optional_string(payload.get("detected_ticker")),
        detected_timeframe=_clean_optional_string(payload.get("detected_timeframe")),
        price_axis_labels=labels,
        chart_bounds=parsed_bounds,
    )


def _clean_optional_string(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    cleaned = value.strip()
    return cleaned or None
