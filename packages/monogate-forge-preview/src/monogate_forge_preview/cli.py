"""CLI for the local monogate-forge-preview scaffold."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .preview import capabilities, check, emit, packet, write_json


def _targets(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="monogate-forge-preview")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("capabilities")

    emit_parser = sub.add_parser("emit")
    emit_parser.add_argument("source", type=Path)
    emit_parser.add_argument("--target", required=True, choices=["python", "javascript"])
    emit_parser.add_argument("--out", type=Path, required=True)

    check_parser = sub.add_parser("check")
    check_parser.add_argument("source", type=Path)
    check_parser.add_argument("--targets", type=_targets, required=True)
    check_parser.add_argument("--work-dir", type=Path, default=Path("build/monogate-forge-preview"))

    packet_parser = sub.add_parser("packet")
    packet_parser.add_argument("source", type=Path)
    packet_parser.add_argument("--targets", type=_targets, required=True)
    packet_parser.add_argument("--out", type=Path, required=True)
    packet_parser.add_argument("--work-dir", type=Path, default=Path("build/monogate-forge-preview"))

    args = parser.parse_args(argv)

    try:
        if args.command == "capabilities":
            print(json.dumps(capabilities(), indent=2, sort_keys=True))
            return 0
        if args.command == "emit":
            out = emit(args.target, args.source, args.out)
            print(f"wrote {out}")
            return 0
        if args.command == "check":
            result = check(args.source, args.targets, args.work_dir)
            print(json.dumps(result, indent=2, sort_keys=True))
            return 0 if result["status"] == "pass" else 1
        if args.command == "packet":
            result = packet(args.source, args.targets, args.work_dir)
            write_json(result, args.out)
            print(f"wrote {args.out}")
            return 0 if result["status"] == "pass" else 1
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    raise AssertionError(f"unhandled command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
