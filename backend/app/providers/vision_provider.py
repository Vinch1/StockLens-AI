from __future__ import annotations

import asyncio
from io import BytesIO
from typing import Protocol, runtime_checkable

from PIL import Image

try:
    import pytesseract

    _HAS_TESSERACT = True
except ImportError:
    pytesseract = None  # type: ignore[assignment]
    _HAS_TESSERACT = False


@runtime_checkable
class VisionProvider(Protocol):
    mode: str

    async def detect_text(self, image_bytes: bytes) -> str: ...

    def status(self) -> dict[str, object]: ...


class TesseractVisionProvider:
    mode = "live"

    async def detect_text(self, image_bytes: bytes) -> str:
        return await asyncio.to_thread(self._sync_detect, image_bytes)

    @staticmethod
    def _sync_detect(image_bytes: bytes) -> str:
        try:
            if not _HAS_TESSERACT:
                return ""
            image = Image.open(BytesIO(image_bytes))
            return pytesseract.image_to_string(image)
        except Exception:
            return ""

    def status(self) -> dict[str, object]:
        return {
            "name": "vision",
            "mode": "live",
            "configured": True,
            "message": "Local OCR via Tesseract.",
        }
