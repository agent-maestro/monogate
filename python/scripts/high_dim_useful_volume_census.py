#!/usr/bin/env python
"""Generate a sampled useful-volume census for high-D EML tree space."""

from __future__ import annotations

import argparse
from pathlib import Path

from monogate.high_dimensional import run_useful_volume_census, write_useful_volume_outputs


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--samples", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=20260526)
    parser.add_argument("--max-depth", type=int, default=6)
    parser.add_argument("--tolerance", type=float, default=0.1)
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--json", type=Path, default=Path("reports/high_dim_useful_volume_census_2026_05_26.json"))
    parser.add_argument("--markdown", type=Path, default=Path("reports/high_dim_useful_volume_census_2026_05_26.md"))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    packet = run_useful_volume_census(
        depths=range(1, args.max_depth + 1),
        samples=args.samples,
        seed=args.seed,
        tolerance=args.tolerance,
    )
    write_useful_volume_outputs(packet, args.json, args.markdown)

    if args.strict:
        rows = packet["rows"]
        if not rows:
            raise SystemExit("no census rows produced")
        if packet["boundaries"]["symbolic_usefulness_proof"]:
            raise SystemExit("symbolic proof boundary must be false")
        raw_pi = [r for r in rows if r["distribution"] == "raw_cube" and r["target"] == "pi"]
        if raw_pi[-1]["target_adjacent_fraction"] > raw_pi[0]["target_adjacent_fraction"]:
            raise SystemExit("expected raw pi useful fraction not to grow at max depth")

    print(f"Wrote {args.json}")
    print(f"Wrote {args.markdown}")
    print("HIGH_DIM_USEFUL_VOLUME_CENSUS_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
