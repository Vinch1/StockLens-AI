from __future__ import annotations

import asyncio
import shutil
from dataclasses import dataclass
from io import BytesIO
from typing import Protocol, runtime_checkable

from PIL import Image

try:
    import pytesseract
    from pytesseract import Output

    _HAS_TESSERACT = True
except ImportError:
    pytesseract = None  # type: ignore[assignment]
    Output = None  # type: ignore[assignment]
    _HAS_TESSERACT = False

_HAS_TESSERACT_BINARY = shutil.which("tesseract") is not None


@dataclass(frozen=True)
class VisionTextBlock:
    text: str
    confidence: float
    left: int
    top: int
    width: int
    height: int


@runtime_checkable
class VisionProvider(Protocol):
    mode: str

    async def detect_text(self, image_bytes: bytes) -> str: ...

    def status(self) -> dict[str, object]: ...


class TesseractVisionProvider:
    mode = "live"

    async def detect_text(self, image_bytes: bytes) -> str:
        return await asyncio.to_thread(self._sync_detect, image_bytes)

    async def detect_text_blocks(self, image_bytes: bytes) -> list[VisionTextBlock]:
        return await asyncio.to_thread(self._sync_detect_blocks, image_bytes)

    @staticmethod
    def _sync_detect(image_bytes: bytes) -> str:
        try:
            if not _HAS_TESSERACT or not _HAS_TESSERACT_BINARY:
                return ""
            image = Image.open(BytesIO(image_bytes))
            return pytesseract.image_to_string(image)
        except Exception:
            return ""

    @staticmethod
    def _sync_detect_blocks(image_bytes: bytes) -> list[VisionTextBlock]:
        try:
            if not _HAS_TESSERACT or not _HAS_TESSERACT_BINARY or Output is None:
                return []
            image = Image.open(BytesIO(image_bytes))
            data = pytesseract.image_to_data(image, output_type=Output.DICT)
            blocks: list[VisionTextBlock] = []
            for index, text in enumerate(data.get("text", [])):
                clean_text = str(text).strip()
                if not clean_text:
                    continue
                try:
                    confidence = float(data["conf"][index])
                except (TypeError, ValueError):
                    confidence = -1.0
                if confidence < 0:
                    continue
                blocks.append(
                    VisionTextBlock(
                        text=clean_text,
                        confidence=confidence,
                        left=int(data["left"][index]),
                        top=int(data["top"][index]),
                        width=int(data["width"][index]),
                        height=int(data["height"][index]),
                    )
                )
            return blocks
        except Exception:
            return []

    def status(self) -> dict[str, object]:
        return {
            "name": "vision",
            "mode": "live",
            "configured": _HAS_TESSERACT and _HAS_TESSERACT_BINARY,
            "message": (
                "Local OCR via Tesseract."
                if _HAS_TESSERACT and _HAS_TESSERACT_BINARY
                else "Tesseract OCR binary is unavailable."
            ),
        }
