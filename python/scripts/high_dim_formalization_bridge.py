#!/usr/bin/env python
"""Emit high-dimensional MachLib/Lean theorem obligation stubs."""

from __future__ import annotations

import argparse
from pathlib import Path

from monogate.high_dimensional import (
    build_high_dim_formalization_bridge,
    write_formalization_bridge_outputs,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--json", type=Path, default=Path("reports/high_dim_formalization_bridge_2026_05_26.json"))
    parser.add_argument("--markdown", type=Path, default=Path("reports/high_dim_formalization_bridge_2026_05_26.md"))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    packet = build_high_dim_formalization_bridge()
    write_formalization_bridge_outputs(packet, args.json, args.markdown)

    if args.strict:
        if packet["obligation_count"] < 4:
            raise SystemExit("expected at least four theorem obligations")
        if packet["boundaries"]["formal_verification_claim"]:
            raise SystemExit("formal verification boundary must be false")
        if any(item["status"] != "stub" for item in packet["obligations"]):
            raise SystemExit("all generated obligations must remain stubs")

    print(f"Wrote {args.json}")
    print(f"Wrote {args.markdown}")
    print("HIGH_DIM_FORMALIZATION_BRIDGE_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
