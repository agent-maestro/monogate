#!/usr/bin/env python
"""Run a sampled Forge heuristic frontier comparison."""

from __future__ import annotations

import argparse
from pathlib import Path

from monogate.high_dimensional import run_forge_heuristic_frontier_packet, write_heuristic_frontier_outputs


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--json", type=Path, default=Path("reports/forge_heuristic_frontier_2026_05_26.json"))
    parser.add_argument("--markdown", type=Path, default=Path("reports/forge_heuristic_frontier_2026_05_26.md"))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    packet = run_forge_heuristic_frontier_packet()
    write_heuristic_frontier_outputs(packet, args.json, args.markdown)

    if args.strict:
        if not packet["rows"]:
            raise SystemExit("expected heuristic rows")
        if packet["boundaries"]["optimizer_release_claim"]:
            raise SystemExit("optimizer release boundary must be false")
        if packet["boundaries"]["formal_verification_claim"]:
            raise SystemExit("formal verification boundary must be false")

    print(f"Wrote {args.json}")
    print(f"Wrote {args.markdown}")
    print("FORGE_HEURISTIC_FRONTIER_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
