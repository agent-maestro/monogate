"""
monogate.frontiers.grammar_extension — Physics-Completeness Theorem Experiment

Tests the central hypothesis that extending the EML leaf set from {x, constants}
to {x, -x, constants} makes EML physics-complete: all 15 FUNCTIONAL_LAWS
become EML-native (depth ≤ 4) under the extended grammar.

**Key insight:**  To express exp(-f(x)) with the EML gate
    eml(a, b) = exp(a) - ln(b),
we need `a = -f(x)`.  In the standard grammar, -f(x) requires variable
subtraction which is unavailable.  With a neg_x leaf (-x), we can build
-x directly, making exp(-x) = eml(-x, 1) — a single-gate expression.

**Implementation trick:**  Rather than modifying the MCTS grammar, we observe
that a function f(x) is representable with a neg_x leaf if and only if
g(x) = f(-x) is representable in the standard grammar.  We therefore run
`mcts_search(lambda x: fn(-x), ...)` and check whether it finds MSE < 1e-6.
If so, the formula for f(x) uses the neg_x leaf exactly where g uses x.

Usage::

    python -m monogate.frontiers.grammar_extension --n-simulations 2000
    python -m monogate.frontiers.grammar_extension --n-simulations 500 --quick
"""
from __future__ import annotations

import argparse
import json
import math
import os
import time
from typing import Callable

__all__ = [
    "census_extended",
    "barrier_closed",
    "run_grammar_extension",
]

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _negated_fn(fn: Callable[[float], float]) -> Callable[[float], float]:
    """Return lambda x: fn(-x) — simulates neg_x leaf availability."""
    return lambda x: fn(-x)


def _domain_flip(domain: tuple[float, float]) -> tuple[float, float]:
    """Flip a domain (lo, hi) → (-hi, -lo) for the negated function."""
    lo, hi = domain
    return (-hi, -lo)


def _run_mcts(
    fn: Callable[[float], float],
    domain: tuple[float, float],
    depth: int,
    n_simulations: int,
    seed: int = 42,
) -> float:
    """Run MCTS on fn over domain at given depth; return best MSE."""
    from monogate.search.mcts import mcts_search

    lo, hi = domain
    n_probe = 60
    probe = [lo + (hi - lo) * i / (n_probe - 1) for i in range(n_probe)]
    try:
        result = mcts_search(
            fn,
            probe_points=probe,
            depth=depth,
            n_simulations=n_simulations,
            seed=seed,
        )
        return float(result.best_mse)
    except Exception:
        return float("inf")


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def census_extended(
    n_simulations: int = 2000,
    verbose: bool = True,
) -> list[dict]:
    """Run MCTS functional census with the extended {x, -x} grammar.

    For each law in ``FUNCTIONAL_LAWS``, runs two searches:
    - **Standard grammar**: target = fn(x) on original domain.
    - **Extended grammar**: target = fn(-x) on flipped domain (simulates neg_x).

    A law is ``eml_native_extended`` if the extended MSE at depth 2 < 1e-6.
    A law ``newly_reachable`` if it was blocked in standard but native in extended.

    Args:
        n_simulations: MCTS budget per search.
        verbose:       Print per-law progress.

    Returns:
        List of dicts, one per law.
    """
    from monogate.frontiers.law_complexity import FUNCTIONAL_LAWS

    EML_NATIVE_THRESH = 1e-6
    results = []

    if verbose:
        print("\n" + "=" * 60)
        print("  GRAMMAR EXTENSION: {x, -x} vs {x} leaf sets")
        print("=" * 60)
        header = f"{'Law':<35} {'d2 std':>8} {'d2 ext':>8} {'native ext':>12}"
        print(header)
        print("-" * len(header))

    for law in FUNCTIONAL_LAWS:
        fn     = law["fn"]
        domain = law["domain"]
        name   = law["name"]

        # Standard grammar: f(x) on domain
        mse_std_d2 = _run_mcts(fn, domain, depth=2, n_simulations=n_simulations)
        mse_std_d4 = _run_mcts(fn, domain, depth=4, n_simulations=n_simulations // 2)

        # Extended grammar: f(-x) on flipped domain → same MCTS, simulates neg_x
        fn_neg    = _negated_fn(fn)
        dom_neg   = _domain_flip(domain)
        # Ensure domain is valid for the negated function (no log(0) etc.)
        dom_neg_safe = (max(dom_neg[0], 0.1), max(dom_neg[1], 0.2)) \
            if dom_neg[1] <= 0 else dom_neg
        mse_ext_d2 = _run_mcts(fn_neg, dom_neg_safe, depth=2,
                                n_simulations=n_simulations)
        mse_ext_d4 = _run_mcts(fn_neg, dom_neg_safe, depth=4,
                                n_simulations=n_simulations // 2)

        native_std = mse_std_d2 < EML_NATIVE_THRESH
        native_ext = mse_ext_d2 < EML_NATIVE_THRESH
        newly_reachable = (not native_std) and native_ext

        entry = {
            "name":             name,
            "mse_std_d2":       round(mse_std_d2, 6),
            "mse_std_d4":       round(mse_std_d4, 6),
            "mse_ext_d2":       round(mse_ext_d2, 6),
            "mse_ext_d4":       round(mse_ext_d4, 6),
            "native_standard":  native_std,
            "native_extended":  native_ext,
            "newly_reachable":  newly_reachable,
        }
        results.append(entry)

        if verbose:
            mark = "NEW!" if newly_reachable else ("✓" if native_ext else "·")
            print(
                f"  {name:<33} {mse_std_d2:>8.4f} {mse_ext_d2:>8.4f} "
                f"{mark:>12}"
            )

    return results


def barrier_closed(results: list[dict]) -> dict:
    """Analyze whether the negative-exponent barrier is closed by {x, -x}.

    Args:
        results: Output of :func:`census_extended`.

    Returns:
        Summary dict with ``n_native_extended``, ``n_newly_reachable``,
        ``barrier_closed`` (bool), and ``completion_rate``.
    """
    n_total         = len(results)
    n_native_std    = sum(1 for r in results if r["native_standard"])
    n_native_ext    = sum(1 for r in results if r["native_extended"])
    n_newly         = sum(1 for r in results if r["newly_reachable"])
    newly_names     = [r["name"] for r in results if r["newly_reachable"]]
    still_blocked   = [r["name"] for r in results if not r["native_extended"]]
    closed          = n_native_ext == n_total

    return {
        "n_laws":              n_total,
        "n_native_standard":   n_native_std,
        "n_native_extended":   n_native_ext,
        "n_newly_reachable":   n_newly,
        "barrier_closed":      closed,
        "completion_rate":     round(n_native_ext / max(n_total, 1), 4),
        "newly_reachable":     newly_names,
        "still_blocked":       still_blocked,
    }


def run_grammar_extension(
    n_simulations: int = 2000,
    output: str | None = None,
    verbose: bool = True,
) -> dict:
    """Full pipeline: extended census + barrier analysis + JSON save.

    Args:
        n_simulations: MCTS budget per search call.
        output:        Path to save JSON (optional; auto-saved to results/).
        verbose:       Print progress.

    Returns:
        dict with keys ``results``, ``barrier``, ``params``.
    """
    t0 = time.perf_counter()
    results = census_extended(n_simulations=n_simulations, verbose=verbose)
    barrier = barrier_closed(results)

    if verbose:
        print("\n" + "=" * 60)
        print("  BARRIER ANALYSIS SUMMARY")
        print("=" * 60)
        print(f"  Standard grammar native:  {barrier['n_native_standard']}"
              f"/{barrier['n_laws']}")
        print(f"  Extended grammar native:  {barrier['n_native_extended']}"
              f"/{barrier['n_laws']}")
        print(f"  Newly reachable:          {barrier['n_newly_reachable']}")
        if barrier["newly_reachable"]:
            for n in barrier["newly_reachable"]:
                print(f"    + {n}")
        if barrier["still_blocked"]:
            print(f"  Still blocked ({len(barrier['still_blocked'])}):")
            for n in barrier["still_blocked"][:5]:
                print(f"    - {n}")
        status = "CLOSED" if barrier["barrier_closed"] else "PARTIALLY OPEN"
        print(f"\n  Barrier status: {status} "
              f"(completion {barrier['completion_rate']*100:.0f}%)")
        print(f"  Total time: {time.perf_counter()-t0:.1f}s")
        print("=" * 60 + "\n")

    payload = {
        "params":  {"n_simulations": n_simulations},
        "barrier": barrier,
        "results": results,
    }

    # Auto-save to results directory
    out_dir = os.path.join(
        os.path.dirname(__file__), "..", "..", "results", "grammar_extension"
    )
    os.makedirs(out_dir, exist_ok=True)
    from datetime import datetime
    ts       = datetime.now().strftime("%Y%m%d_%H%M%S")
    auto_path = os.path.join(out_dir, f"grammar_ext_{ts}.json")
    with open(auto_path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, default=str)
    if verbose:
        print(f"Results: {auto_path}")

    if output:
        with open(output, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2, default=str)
        if verbose:
            print(f"Output saved to {output}")

    return payload


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Grammar Extension — Physics Completeness Theorem"
    )
    parser.add_argument("--n-simulations", type=int, default=2000,
                        help="MCTS budget per search (default 2000)")
    parser.add_argument("--output", type=str, default=None,
                        help="Path to save JSON results (optional)")
    parser.add_argument("--quick", action="store_true",
                        help="Quick mode: n-simulations=300 for smoke testing")
    args = parser.parse_args()

    n_sim = 300 if args.quick else args.n_simulations
    run_grammar_extension(n_simulations=n_sim, output=args.output, verbose=True)


if __name__ == "__main__":
    main()
