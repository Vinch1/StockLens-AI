from __future__ import annotations

import argparse

from request_utils import default_base_url, request_json


def main() -> int:
    parser = argparse.ArgumentParser(description="Post a sample analysis request to /api/analyze.")
    parser.add_argument("--ticker", default="AAPL", help="Ticker symbol to analyze.")
    parser.add_argument("--asset-type", default="stock", choices=["stock", "etf"], help="Asset type.")
    parser.add_argument("--timeframe", default="1D", choices=["15m", "1h", "4h", "1D", "1W"], help="Timeframe.")
    parser.add_argument("--horizon", default="swing", choices=["short", "swing", "long"], help="Analysis horizon.")
    parser.add_argument(
        "--include-news",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Include news in the analysis request.",
    )
    parser.add_argument(
        "--include-fundamentals",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Include fundamentals in the analysis request.",
    )
    parser.add_argument(
        "--base-url",
        default=default_base_url(),
        help="Backend base URL. Defaults to http://127.0.0.1:8000 or STOCKLENS_API_BASE_URL.",
    )
    parser.add_argument("--timeout", type=float, default=120.0, help="Request timeout in seconds.")
    args = parser.parse_args()

    payload = {
        "ticker": args.ticker,
        "asset_type": args.asset_type,
        "timeframe": args.timeframe,
        "horizon": args.horizon,
        "include_news": args.include_news,
        "include_fundamentals": args.include_fundamentals,
    }
    return request_json("POST", "/api/analyze", base_url=args.base_url, timeout=args.timeout, json_payload=payload)


if __name__ == "__main__":
    raise SystemExit(main())
