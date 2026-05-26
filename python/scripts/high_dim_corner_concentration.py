#!/usr/bin/env python
"""Generate the Monogate high-dimensional corner-concentration probe."""

from __future__ import annotations

import argparse
from pathlib import Path

from monogate.high_dimensional import run_corner_concentration_probe, write_probe_outputs


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--samples", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=20260526)
    parser.add_argument("--max-depth", type=int, default=7)
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--json", type=Path, default=Path("reports/high_dim_corner_concentration_2026_05_26.json"))
    parser.add_argument("--markdown", type=Path, default=Path("reports/high_dim_corner_concentration_2026_05_26.md"))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    packet = run_corner_concentration_probe(
        depths=range(1, args.max_depth + 1),
        samples=args.samples,
        seed=args.seed,
    )
    write_probe_outputs(packet, args.json, args.markdown)

    if args.strict:
        rows = packet["rows"]
        if rows[-1]["hypersphere_cube_ratio"] >= rows[0]["hypersphere_cube_ratio"]:
            raise SystemExit("expected hypersphere/cube ratio to shrink with depth")
        if rows[-1]["boundary_shell_fraction"] <= rows[0]["boundary_shell_fraction"]:
            raise SystemExit("expected boundary shell fraction to grow with depth")
        if not packet["boundaries"]["sampled_evidence_only"]:
            raise SystemExit("sample boundary missing")

    print(f"Wrote {args.json}")
    print(f"Wrote {args.markdown}")
    print("HIGH_DIM_CORNER_CONCENTRATION_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
