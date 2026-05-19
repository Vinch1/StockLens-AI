from __future__ import annotations

import json
import os
import sys
from typing import Any

import httpx


DEFAULT_BASE_URL = "http://127.0.0.1:8000"


def default_base_url() -> str:
    return os.getenv("STOCKLENS_API_BASE_URL", DEFAULT_BASE_URL)


def request_json(
    method: str,
    path: str,
    *,
    base_url: str,
    timeout: float,
    json_payload: dict[str, Any] | None = None,
) -> int:
    endpoint = f"{base_url.rstrip('/')}/{path.lstrip('/')}"
    print(f"{method.upper()} {endpoint}")

    try:
        response = httpx.request(method, endpoint, json=json_payload, timeout=timeout)
    except httpx.ConnectError:
        print(
            "Could not connect to the backend. Start it with: uv run uvicorn app.main:app --reload",
            file=sys.stderr,
        )
        return 1
    except httpx.HTTPError as exc:
        print(f"Request failed: {exc}", file=sys.stderr)
        return 1

    print(f"Status: {response.status_code}")
    try:
        body: Any = response.json()
    except json.JSONDecodeError:
        print(response.text)
        return 0 if response.is_success else 1

    print(json.dumps(body, indent=2, sort_keys=True))
    return 0 if response.is_success else 1
