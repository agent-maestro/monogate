"""
monogate.frontiers.attractor_identity
=======================================
Experiment 4: What is the phantom attractor at ~3.169642?

When training a depth-3 EML tree toward π with gradient descent, runs
converge to ~3.1696 instead of π. This script investigates what that
constant IS.

Usage::

    cd python
    python -m monogate.frontiers.attractor_identity \\
        --n-seeds 40 --output results/attractor_investigation.json

Requirements: mpmath (``pip install mpmath``); torch for gradient collection.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import time
from typing import Any

# ── Constants database ────────────────────────────────────────────────────────

def _build_constants() -> dict:
    """Return ~80 candidate constants as a dict name → mpmath.mpf."""
    try:
        import mpmath as mp
        mp.mp.dps = 80
    except ImportError:
        return {}

    e  = mp.e
    pi = mp.pi
    phi = (1 + mp.sqrt(5)) / 2

    return {
        # Transcendental basics
        "pi":             pi,
        "e":              e,
        "phi (golden)":   phi,
        "sqrt(2)":        mp.sqrt(2),
        "sqrt(3)":        mp.sqrt(3),
        "sqrt(5)":        mp.sqrt(5),
        "sqrt(6)":        mp.sqrt(6),
        "sqrt(7)":        mp.sqrt(7),
        "sqrt(10)":       mp.sqrt(10),
        "sqrt(pi)":       mp.sqrt(pi),
        "sqrt(e)":        mp.sqrt(e),
        "cbrt(pi)":       mp.cbrt(pi),
        "cbrt(e)":        mp.cbrt(e),
        "cbrt(30)":       mp.cbrt(30),
        "pi^(2/3)":       pi ** (mp.mpf(2) / 3),
        "e^(2/3)":        e  ** (mp.mpf(2) / 3),
        # Logarithms
        "ln(2)":          mp.log(2),
        "ln(3)":          mp.log(3),
        "ln(5)":          mp.log(5),
        "ln(10)":         mp.log(10),
        "ln(24)":         mp.log(24),
        "ln(25)":         mp.log(25),
        "ln(23)":         mp.log(23),
        "ln(pi)":         mp.log(pi),
        "ln(e^2)":        mp.mpf(2),
        "2*ln(sqrt(e))":  mp.log(e),
        # Combinations near 3.17
        "pi - 1/e":             pi - 1/e,
        "e + 0.45":             e + mp.mpf("0.45"),
        "e + 9/20":             e + mp.mpf(9) / 20,
        "e + ln(1.2)":          e + mp.log(mp.mpf("1.2")),
        "3 + ln(1.2)":          mp.mpf(3) + mp.log(mp.mpf("1.2")),
        "3 + 1/6":              mp.mpf(3) + mp.mpf(1) / 6,
        "3 + sqrt(2)/10":       mp.mpf(3) + mp.sqrt(2) / 10,
        "pi - arcsin(1/e)":     pi - mp.asin(1/e),
        "2*arctan(2)":          2 * mp.atan(2),
        "tan(1)":               mp.tan(1),
        "arctan(e)":            mp.atan(e),
        # Powers
        "2^(5/3)":              mp.power(2, mp.mpf(5) / 3),
        "2^(3/2)":              mp.power(2, mp.mpf(3) / 2),
        "e^(1/e)":              mp.power(e, 1/e),
        "3^(1/e)":              mp.power(3, 1/e),
        "10^(1/2)":             mp.sqrt(10),
        "pi^(1/2)":             mp.sqrt(pi),
        "pi^(1/3)":             mp.power(pi, mp.mpf(1) / 3),
        "e^(e-2)":              mp.exp(e - 2),
        "exp(1) - 1/e":         e - 1/e,
        "exp(1) + 1/exp(2)":    e + mp.exp(-2),
        # Special functions
        "Gamma(5/2)":           mp.gamma(mp.mpf(5) / 2),
        "Gamma(3/2)":           mp.gamma(mp.mpf(3) / 2),
        "zeta(2)":              mp.zeta(2),
        "zeta(3)":              mp.zeta(3),
        "zeta(3)/zeta(2)":      mp.zeta(3) / mp.zeta(2),
        "Catalan":              mp.catalan,
        "Euler-Mascheroni":     mp.euler,
        "2*Catalan":            2 * mp.catalan,
        # EML-specific candidates
        "eml(1,1) = e":                     e,
        "eml(eml(1,1),1) = e^e - 0":       mp.exp(e),  # depth-2 all-ones tree
        "exp(exp(1) - 1)":                  mp.exp(e - 1),
        "exp(1 - 1/e)":                     mp.exp(1 - 1/e),
        "exp(e - ln(e^2))":                 mp.exp(e - 2),
        # Near 3.17 specifically
        "sqrt(10.06)":          mp.sqrt(mp.mpf("10.06")),
        "pi + 0.03":            pi + mp.mpf("0.03"),
        "pi - 0.03":            pi - mp.mpf("0.03"),
        "3.1696":               mp.mpf("3.1696"),
        "3.16964":              mp.mpf("3.16964"),
        # Hyperbolic / Bessel
        "2*cosh(1)":            2 * mp.cosh(1),
        "sinh(pi/2)":           mp.sinh(pi/2),
        "cosh(1) + 1":          mp.cosh(1) + 1,
        "1/(1-1/e^2)":          1 / (1 - mp.exp(-2)),
        # Misc
        "ln(phi) + 2":          mp.log(phi) + 2,
        "phi^2":                phi ** 2,
        "(1+sqrt(5))/2 + 1.5":  phi + mp.mpf("1.5"),
    }


CONSTANTS: dict = {}
try:
    CONSTANTS = _build_constants()
except Exception:
    pass


# ── Gradient collection ───────────────────────────────────────────────────────

def collect_attractor_values(
    n_seeds: int = 100,
    depth: int = 3,
    target: float = math.pi,
    steps: int = 3000,
) -> list[float]:
    """Run gradient descent on a depth-*depth* EML tree from *n_seeds* random starts.

    Requires torch.
    """
    try:
        import torch
    except ImportError as e:
        raise ImportError("torch required for collect_attractor_values") from e

    def _eml(x, y):
        return torch.exp(x) - torch.log(torch.clamp(y, min=1e-10))

    class _EMLTree(torch.nn.Module):
        def __init__(self, d: int) -> None:
            super().__init__()
            n_leaves = 2 ** d
            self.leaves = torch.nn.Parameter(torch.ones(n_leaves))

        def forward(self):
            vals = list(self.leaves)
            while len(vals) > 1:
                new_vals = []
                for i in range(0, len(vals) - 1, 2):
                    new_vals.append(_eml(vals[i], vals[i + 1]))
                if len(vals) % 2 == 1:
                    new_vals.append(vals[-1])
                vals = new_vals
            return vals[0]

    values: list[float] = []
    target_t = torch.tensor(float(target))

    for seed in range(n_seeds):
        torch.manual_seed(seed)
        tree = _EMLTree(depth)
        opt  = torch.optim.Adam(tree.parameters(), lr=5e-3)

        for _ in range(steps):
            opt.zero_grad()
            loss = (tree() - target_t) ** 2
            if not torch.isfinite(loss):
                break
            loss.backward()
            opt.step()

        val = tree().item()
        values.append(val)

        if (seed + 1) % 20 == 0:
            print(f"  seed {seed + 1:3d}/{n_seeds}: {val:.10f}")

    return values


# ── High-precision mean ───────────────────────────────────────────────────────

def high_precision_attractor(values: list[float], dps: int = 60) -> str:
    """Return the mean of *values* to *dps* decimal places via mpmath."""
    try:
        import mpmath as mp
        mp.mp.dps = dps
        total = sum(mp.mpf(str(v)) for v in values)
        mean  = total / len(values)
        return mp.nstr(mean, dps // 2)
    except ImportError:
        return str(sum(values) / len(values))


# ── Constant search ───────────────────────────────────────────────────────────

def search_constants(
    attractor_str: str,
    tolerance: float = 1e-6,
) -> tuple[list, list]:
    """Find known constants closest to *attractor*.

    Parameters
    ----------
    attractor_str:
        High-precision string representation of the attractor.
    tolerance:
        Match threshold.

    Returns
    -------
    (matches, top_20)
        *matches* — constants within *tolerance*;
        *top_20*  — 20 closest constants, sorted by distance.
    """
    try:
        import mpmath as mp
        mp.mp.dps = 60
        attractor = mp.mpf(attractor_str)
    except Exception:
        attractor = float(attractor_str)

    distances: list[tuple[str, float, float]] = []
    for name, value in CONSTANTS.items():
        try:
            dist = float(abs(value - attractor))
            distances.append((name, float(value), dist))
        except Exception:
            pass

    distances.sort(key=lambda x: x[2])
    matches = [(n, v, d) for n, v, d in distances if d < tolerance]
    top_20  = distances[:20]

    return matches, top_20


# ── Tree structure analysis ───────────────────────────────────────────────────

def analyze_attractor_tree(
    seed: int = 0,
    depth: int = 3,
    target: float = math.pi,
    steps: int = 3000,
) -> dict:
    """Run gradient descent to convergence and return the tree's internal values."""
    try:
        import torch
    except ImportError as e:
        raise ImportError("torch required for analyze_attractor_tree") from e

    def _eml(x, y):
        return torch.exp(x) - torch.log(torch.clamp(y, min=1e-10))

    class _EMLTree(torch.nn.Module):
        def __init__(self, d: int) -> None:
            super().__init__()
            n_leaves = 2 ** d
            self.leaves = torch.nn.Parameter(torch.ones(n_leaves))

        def forward(self):
            vals = list(self.leaves)
            while len(vals) > 1:
                new_vals = []
                for i in range(0, len(vals) - 1, 2):
                    new_vals.append(_eml(vals[i], vals[i + 1]))
                if len(vals) % 2 == 1:
                    new_vals.append(vals[-1])
                vals = new_vals
            return vals[0]

        def get_levels(self) -> list:
            levels: list[list[float]] = [
                [x.item() for x in self.leaves.detach()]
            ]
            vals = [x for x in self.leaves.detach()]
            while len(vals) > 1:
                new_vals = []
                for i in range(0, len(vals) - 1, 2):
                    new_vals.append(_eml(vals[i], vals[i + 1]))
                if len(vals) % 2 == 1:
                    new_vals.append(vals[-1])
                vals = new_vals
                levels.append([v.item() for v in vals])
            return levels

    torch.manual_seed(seed)
    tree = _EMLTree(depth)
    opt  = torch.optim.Adam(tree.parameters(), lr=5e-3)
    target_t = torch.tensor(float(target))

    for _ in range(steps):
        opt.zero_grad()
        loss = (tree() - target_t) ** 2
        if not torch.isfinite(loss):
            break
        loss.backward()
        opt.step()

    return {
        "final_value":          tree().item(),
        "leaf_values":          tree.leaves.detach().tolist(),
        "intermediate_levels":  tree.get_levels(),
        "target":               target,
        "depth":                depth,
    }


# ── Universality ──────────────────────────────────────────────────────────────

def test_universality(n_seeds: int = 20) -> dict:
    """Test if the attractor depends on the target value or tree depth."""
    targets = {
        "pi":    math.pi,
        "e":     math.e,
        "sqrt2": math.sqrt(2),
        "ln10":  math.log(10),
        "1.5":   1.5,
        "2.0":   2.0,
        "3.0":   3.0,
    }
    depths = [2, 3]
    results: dict[str, Any] = {}

    for target_name, target_val in targets.items():
        results[target_name] = {}
        for depth in depths:
            try:
                vals = collect_attractor_values(
                    n_seeds=n_seeds, depth=depth,
                    target=target_val, steps=1500,
                )
                import numpy as np
                mean = float(np.mean(vals))
                std  = float(np.std(vals))
                results[target_name][str(depth)] = {
                    "mean": mean,
                    "std":  std,
                    "clustered": std < 0.01,
                    "attractor_differs_from_target": abs(mean - target_val) > 0.001,
                }
            except ImportError:
                results[target_name][str(depth)] = {"error": "torch not available"}
            except Exception as exc:
                results[target_name][str(depth)] = {"error": str(exc)}

    return results


# ── CLI ───────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Phantom attractor investigation (~3.1696)."
    )
    parser.add_argument("--n-seeds",    type=int,   default=40)
    parser.add_argument("--depth",      type=int,   default=3)
    parser.add_argument("--target",     type=float, default=math.pi)
    parser.add_argument("--steps",      type=int,   default=3000)
    parser.add_argument("--tolerance",  type=float, default=1e-6)
    parser.add_argument("--universality", action="store_true")
    parser.add_argument(
        "--output", type=str, default="results/attractor_investigation.json"
    )
    args = parser.parse_args()

    output: dict[str, Any] = {
        "config": vars(args),
        "n_constants_tested": len(CONSTANTS),
    }

    # ── Gradient collection ───────────────────────────────────────────────────
    print(f"Collecting attractor values (n_seeds={args.n_seeds}, depth={args.depth})...")
    try:
        t0 = time.perf_counter()
        values = collect_attractor_values(
            n_seeds=args.n_seeds,
            depth=args.depth,
            target=args.target,
            steps=args.steps,
        )
        elapsed = time.perf_counter() - t0
        import numpy as np
        attractor_float = float(np.mean(values))
        attractor_str   = high_precision_attractor(values)
        output["attractor_float"]  = attractor_float
        output["attractor_hp"]     = attractor_str
        output["values_collected"] = values
        output["collection_elapsed_s"] = elapsed
        print(f"  Attractor: {attractor_str[:30]}... ({elapsed:.1f}s)")
    except ImportError:
        print("  [skip] torch not installed — cannot collect attractor values")
        attractor_str = "3.169642"
        attractor_float = 3.169642
        output["attractor_float"] = attractor_float
        output["attractor_hp"]    = attractor_str

    # ── Constant search ───────────────────────────────────────────────────────
    if CONSTANTS:
        print(f"\nSearching {len(CONSTANTS)} constants (tolerance={args.tolerance})...")
        matches, top_20 = search_constants(attractor_str, args.tolerance)
        output["constant_matches"]   = [(n, v, d) for n, v, d in matches]
        output["constant_top_20"]    = [(n, v, d) for n, v, d in top_20]

        if matches:
            print(f"  MATCH FOUND: {matches[0][0]} = {matches[0][1]:.10f}  "
                  f"(dist={matches[0][2]:.2e})")
        else:
            print(f"  No match within tolerance={args.tolerance}")
            print(f"  Closest: {top_20[0][0]} = {top_20[0][1]:.10f}  "
                  f"(dist={top_20[0][2]:.2e})")

        # Print top 5
        print("\nTop 5 closest constants:")
        for name, val, dist in top_20[:5]:
            print(f"  {name:30s}  {val:.12f}  dist={dist:.3e}")
    else:
        print("\n[skip] mpmath not installed — cannot search constants")

    # ── Tree structure ────────────────────────────────────────────────────────
    print("\nAnalyzing attractor tree structure...")
    try:
        tree_info = analyze_attractor_tree(
            seed=0, depth=args.depth,
            target=args.target, steps=args.steps,
        )
        output["attractor_tree"] = tree_info
        print(f"  Leaf values: {[f'{v:.4f}' for v in tree_info['leaf_values']]}")
        print(f"  Final value: {tree_info['final_value']:.10f}")
    except ImportError:
        print("  [skip] torch not installed")

    # ── Universality ──────────────────────────────────────────────────────────
    if args.universality:
        print("\nTesting universality (different targets and depths)...")
        univ = test_universality(n_seeds=min(args.n_seeds, 15))
        output["universality"] = univ
        for target_name, depth_results in univ.items():
            for depth_str, stats in depth_results.items():
                if "mean" in stats:
                    print(f"  target={target_name:8s} depth={depth_str}:  "
                          f"mean={stats['mean']:.6f}  std={stats['std']:.4f}  "
                          f"clustered={stats['clustered']}")

    # ── Save ─────────────────────────────────────────────────────────────────
    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved: {args.output}")

    # ── Summary ──────────────────────────────────────────────────────────────
    summary_path = args.output.replace(".json", "_summary.md")
    _write_summary(output, summary_path)
    print(f"Summary: {summary_path}")


def _write_summary(data: dict, path: str) -> None:
    lines = [
        "# Phantom Attractor Investigation",
        "",
        f"**Attractor value:** `{data.get('attractor_hp', 'N/A')}`",
        "",
        "## Closest Known Constants",
        "",
    ]
    for name, val, dist in data.get("constant_top_20", [])[:10]:
        lines.append(f"- `{name}` = {val:.12f}  (dist = {dist:.3e})")

    matches = data.get("constant_matches", [])
    lines += [
        "",
        "## Conclusion",
        "",
        (
            f"**IDENTIFIED:** The attractor matches `{matches[0][0]}` "
            f"within tolerance {matches[0][2]:.2e}."
            if matches else
            "**UNIDENTIFIED:** No known constant matched within tolerance. "
            "Candidate for new EML attractor constant."
        ),
    ]

    tree = data.get("attractor_tree", {})
    if tree:
        lines += [
            "",
            "## Attractor Tree Structure",
            "",
            f"- Leaf values: `{tree.get('leaf_values', [])}`",
            f"- Final value: `{tree.get('final_value', 'N/A')}`",
        ]

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
