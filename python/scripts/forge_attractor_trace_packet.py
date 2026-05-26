#!/usr/bin/env python
"""Generate Forge-style optimizer trace packets for high-D EML tree space."""

from __future__ import annotations

import argparse
from pathlib import Path

from monogate.high_dimensional import run_forge_attractor_trace_packet, write_trace_outputs


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--depth", type=int, default=3)
    parser.add_argument("--steps", type=int, default=80)
    parser.add_argument("--seed", type=int, default=20260526)
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--json", type=Path, default=Path("reports/forge_attractor_trace_packet_2026_05_26.json"))
    parser.add_argument("--markdown", type=Path, default=Path("reports/forge_attractor_trace_packet_2026_05_26.md"))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    packet = run_forge_attractor_trace_packet(depth=args.depth, seed=args.seed, steps=args.steps)
    write_trace_outputs(packet, args.json, args.markdown)

    if args.strict:
        regimes = {row["regime"] for row in packet["summary"]}
        expected = {"naive_gradient", "regularized_gradient", "guarded_gradient", "boundary_aware_gradient", "random_search"}
        if regimes != expected:
            raise SystemExit(f"unexpected regimes: {sorted(regimes)}")
        if packet["boundaries"]["optimizer_release_claim"]:
            raise SystemExit("optimizer release claim boundary must be false")

    print(f"Wrote {args.json}")
    print(f"Wrote {args.markdown}")
    print("FORGE_ATTRACTOR_TRACE_PACKET_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
