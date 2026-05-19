from __future__ import annotations

import argparse

from request_utils import default_base_url, request_json


def main() -> int:
    parser = argparse.ArgumentParser(description="Request GET /health from a running backend.")
    parser.add_argument(
        "--base-url",
        default=default_base_url(),
        help="Backend base URL. Defaults to http://127.0.0.1:8000 or STOCKLENS_API_BASE_URL.",
    )
    parser.add_argument("--timeout", type=float, default=30.0, help="Request timeout in seconds.")
    args = parser.parse_args()

    return request_json("GET", "/health", base_url=args.base_url, timeout=args.timeout)


if __name__ == "__main__":
    raise SystemExit(main())
