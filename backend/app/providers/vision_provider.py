from __future__ import annotations

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

    def detect_text(self, image_bytes: bytes) -> str: ...

    def status(self) -> dict[str, object]: ...


class MockVisionProvider:
    mode = "mock"

    def detect_text(self, image_bytes: bytes) -> str:
        return ""

    def status(self) -> dict[str, object]:
        return {
            "name": "vision",
            "mode": "mock",
            "configured": False,
            "message": "OCR not configured.",
        }


class TesseractVisionProvider:
    mode = "live"

    def detect_text(self, image_bytes: bytes) -> str:
        try:
            if not _HAS_TESSERACT:
                return ""
            image = Image.open(BytesIO(image_bytes))
            text = pytesseract.image_to_string(image)
            return text
        except Exception:
            return ""

    def status(self) -> dict[str, object]:
        return {
            "name": "vision",
            "mode": "live",
            "configured": True,
            "message": "Local OCR via Tesseract.",
        }
