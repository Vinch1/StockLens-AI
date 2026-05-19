from __future__ import annotations

import argparse
import base64
import mimetypes
import sys
from pathlib import Path

from request_utils import default_base_url, request_json


IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Post a local chart screenshot to /api/parse-screenshot. "
            "Start the backend first, then run this script from backend/."
        )
    )
    parser.add_argument(
        "image",
        nargs="?",
        type=Path,
        help="Image path to upload. If omitted, the first image in the tests folder is used.",
    )
    parser.add_argument(
        "--base-url",
        default=default_base_url(),
        help="Backend base URL. Defaults to http://127.0.0.1:8000 or STOCKLENS_API_BASE_URL.",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=60.0,
        help="Request timeout in seconds.",
    )
    args = parser.parse_args()

    image_path = _resolve_image_path(args.image)
    if image_path is None:
        print(
            "No image found. Place a .png, .jpg, .jpeg, or .webp file in backend/tests, "
            "or pass an explicit image path.",
            file=sys.stderr,
        )
        return 1

    try:
        image_base64 = _encode_image_base64(image_path)
    except OSError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    payload = {
        "filename": image_path.name,
        "image_base64": image_base64,
    }

    print(f"Image: {image_path}")
    return request_json(
        "POST",
        "/api/parse-screenshot",
        base_url=args.base_url,
        timeout=args.timeout,
        json_payload=payload,
    )


def _resolve_image_path(image_arg: Path | None) -> Path | None:
    if image_arg is not None:
        return image_arg.expanduser().resolve()

    tests_dir = Path(__file__).resolve().parent
    images = sorted(
        path for path in tests_dir.iterdir()
        if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS
    )
    return images[0] if images else None


def _encode_image_base64(image_path: Path) -> str:
    if not image_path.is_file():
        raise FileNotFoundError(f"Image file does not exist: {image_path}")

    image_bytes = image_path.read_bytes()
    encoded = base64.b64encode(image_bytes).decode("ascii")
    mime_type = mimetypes.guess_type(image_path.name)[0]
    if mime_type:
        return f"data:{mime_type};base64,{encoded}"
    return encoded


if __name__ == "__main__":
    raise SystemExit(main())
