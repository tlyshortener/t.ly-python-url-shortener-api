from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any

from .client import TlyClient
from .endpoints import SUPPORTED_METHODS
from .exceptions import TlyAPIError


def _parse_data(raw: str | None) -> dict[str, Any]:
    if not raw:
        return {}
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise ValueError("--data must be a JSON object")
    return data


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="tly", description="T.LY URL Shortener API CLI")
    parser.add_argument("--token", default=os.getenv("TLY_API_TOKEN"), help="API token")
    parser.add_argument("--base-url", default=os.getenv("TLY_BASE_URL", "https://api.t.ly"))
    parser.add_argument("--timeout", type=float, default=30.0)

    subparsers = parser.add_subparsers(dest="command", required=True)

    shorten = subparsers.add_parser("shorten", help="Create a short link")
    shorten.add_argument("--long-url", required=True)
    shorten.add_argument("--domain")
    shorten.add_argument("--description")
    shorten.add_argument("--expire-at-datetime")
    shorten.add_argument("--public-stats", action="store_true")
    shorten.add_argument("--meta-json")

    expand = subparsers.add_parser("expand", help="Expand a short link")
    expand.add_argument("--short-url", required=True)
    expand.add_argument("--password")

    qr = subparsers.add_parser("qr", help="Get QR code (binary image by default)")
    qr.add_argument("--short-url", required=True)
    qr.add_argument("--output", choices=["image", "base64"], default="image")
    qr.add_argument("--format", choices=["png", "eps"], default="png")
    qr.add_argument("--out", help="Output file path for binary QR image")

    call = subparsers.add_parser("call", help="Call any supported client method")
    call.add_argument("method", choices=SUPPORTED_METHODS)
    call.add_argument("--data", help='JSON object, example: \'{"tag":"fall2026"}\'')

    return parser


def _print_result(result: Any) -> int:
    if isinstance(result, (dict, list)):
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    if isinstance(result, (bytes, bytearray)):
        sys.stdout.buffer.write(result)
        return 0
    print(result)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if not args.token:
        parser.error("Missing token. Provide --token or set TLY_API_TOKEN.")

    try:
        with TlyClient(api_token=args.token, base_url=args.base_url, timeout=args.timeout) as client:
            if args.command == "shorten":
                meta = json.loads(args.meta_json) if args.meta_json else None
                result = client.create_short_link(
                    long_url=args.long_url,
                    domain=args.domain,
                    description=args.description,
                    expire_at_datetime=args.expire_at_datetime,
                    public_stats=True if args.public_stats else None,
                    meta=meta,
                )
                return _print_result(result)

            if args.command == "expand":
                result = client.expand_short_link(short_url=args.short_url, password=args.password)
                return _print_result(result)

            if args.command == "qr":
                result = client.get_qr_code(
                    short_url=args.short_url,
                    output=args.output,
                    fmt=args.format,
                )
                if isinstance(result, bytes):
                    if args.out:
                        with open(args.out, "wb") as f:
                            f.write(result)
                        print(args.out)
                        return 0
                    sys.stdout.buffer.write(result)
                    return 0
                return _print_result(result)

            if args.command == "call":
                payload = _parse_data(args.data)
                method = getattr(client, args.method)
                result = method(**payload)
                return _print_result(result)

            parser.error(f"Unknown command: {args.command}")
            return 2
    except json.JSONDecodeError as exc:
        print(f"Invalid JSON input: {exc}", file=sys.stderr)
        return 2
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    except TlyAPIError as exc:
        print(str(exc), file=sys.stderr)
        if exc.response_body:
            print(exc.response_body, file=sys.stderr)
        return 1
    except Exception as exc:  # noqa: BLE001
        print(f"Unexpected error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
