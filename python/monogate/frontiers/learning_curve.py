"""
monogate.frontiers.learning_curve
===================================
Experiment 1: Does the neural scorer improve search efficiency over time?

Usage::

    cd python
    python -m monogate.frontiers.learning_curve \\
        --n-identities 50 --n-runs 5 --output results/learning_curve.json

The script runs EMLProverV2 on a shuffled batch of identities twice — once
with ``enable_learning=True`` and once with ``enable_learning=False`` — and
compares the elapsed time per proof as a function of experience.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import random
import time
from typing import Any

import numpy as np


# ── Core experiment ───────────────────────────────────────────────────────────

def run_learning_curve(
    n_identities: int = 50,
    n_runs: int = 5,
    seed: int = 42,
    enable_learning: bool = True,
) -> dict:
    """Prove *n_identities* in sequence, tracking elapsed time per proof.

    Repeats *n_runs* times with different random orderings.

    Parameters
    ----------
    n_identities:
        How many identities to prove per run (capped at catalog size).
    n_runs:
        Number of independent runs (each with a fresh prover and different
        shuffle order).
    seed:
        Base random seed; run *k* uses ``seed + k``.
    enable_learning:
        Whether the prover's neural scorer is active.

    Returns
    -------
    dict with keys ``learning_enabled``, ``n_identities``, ``n_runs``,
    ``runs`` (list of per-run dicts).
    """
    from monogate.identities import ALL_IDENTITIES
    from monogate.prover import EMLProverV2

    pool = list(ALL_IDENTITIES)[:n_identities]
    actual_n = len(pool)

    results: dict[str, Any] = {
        "learning_enabled": enable_learning,
        "n_identities": actual_n,
        "n_runs": n_runs,
        "runs": [],
    }

    for run_idx in range(n_runs):
        rng = random.Random(seed + run_idx)
        order = list(range(actual_n))
        rng.shuffle(order)

        prover = EMLProverV2(enable_learning=enable_learning)
        run_data: dict[str, Any] = {"run_idx": run_idx, "proofs": []}

        for pos, idx in enumerate(order):
            identity = pool[idx]
            r = prover.prove(identity.expression)
            run_data["proofs"].append({
                "pos": pos,
                "name": identity.name,
                "category": identity.category,
                "difficulty": identity.difficulty,
                "status": r.status,
                "elapsed_s": r.elapsed_s,
                "mcts_simulations": r.mcts_simulations,
                "node_count": r.node_count,
                "proved": r.proved(),
            })

        results["runs"].append(run_data)

    return results


# ── Analysis ──────────────────────────────────────────────────────────────────

def analyze_learning_curve(results: dict) -> dict:
    """Compute summary statistics across runs.

    Returns a dict with:
    - ``mean_by_position`` / ``std_by_position`` — per-position elapsed_s stats
    - ``first_quarter_mean`` / ``last_quarter_mean``
    - ``improvement_ratio`` — first_quarter / last_quarter (>1 = got faster)
    - ``rolling_mean`` — rolling average with window=5
    - ``prove_rate`` — fraction of proofs that succeeded
    """
    n = results["n_identities"]
    n_runs = results["n_runs"]
    window = 5

    elapsed = np.zeros((n_runs, n))
    proved  = np.zeros((n_runs, n))

    for r, run in enumerate(results["runs"]):
        for proof in run["proofs"]:
            p = proof["pos"]
            elapsed[r, p] = proof["elapsed_s"]
            proved[r, p]  = float(proof["proved"])

    mean = elapsed.mean(axis=0)
    std  = elapsed.std(axis=0)
    q = max(1, n // 4)
    rolling = np.convolve(mean, np.ones(window) / window, mode="valid").tolist()

    first_q = float(mean[:q].mean())
    last_q  = float(mean[n - q:].mean()) if n - q > 0 else first_q

    return {
        "mean_by_position":   mean.tolist(),
        "std_by_position":    std.tolist(),
        "first_quarter_mean": first_q,
        "last_quarter_mean":  last_q,
        "improvement_ratio":  first_q / max(last_q, 1e-9),
        "rolling_mean":       rolling,
        "prove_rate":         float(proved.mean()),
        "window":             window,
    }


# ── Visualization ─────────────────────────────────────────────────────────────

def plot_learning_curve(
    res_on: dict,
    res_off: dict,
    output_path: str,
) -> str:
    """Two-panel learning curve plot.

    Left panel: raw mean ± 1 std.
    Right panel: rolling average (window=5).
    """
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("[warning] matplotlib not installed — skipping plot")
        return ""

    an_on  = analyze_learning_curve(res_on)
    an_off = analyze_learning_curve(res_off)

    n = res_on["n_identities"]
    n_runs_on  = res_on["n_runs"]
    n_runs_off = res_off["n_runs"]
    window = an_on["window"]

    # Rebuild raw arrays for fill_between
    def _elapsed_matrix(res: dict) -> np.ndarray:
        nr = res["n_runs"]
        ni = res["n_identities"]
        mat = np.zeros((nr, ni))
        for r, run in enumerate(res["runs"]):
            for proof in run["proofs"]:
                mat[r, proof["pos"]] = proof["elapsed_s"]
        return mat

    mat_on  = _elapsed_matrix(res_on)
    mat_off = _elapsed_matrix(res_off)

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # --- Left: raw mean ± std ---
    ax = axes[0]
    for mat, an, label, color in [
        (mat_on,  an_on,  "Learning ON",  "steelblue"),
        (mat_off, an_off, "Learning OFF", "tomato"),
    ]:
        m = np.array(an["mean_by_position"])
        s = np.array(an["std_by_position"])
        ax.plot(range(n), m, label=label, color=color)
        ax.fill_between(range(n), m - s, m + s, alpha=0.2, color=color)

    ax.set_xlabel("Identity number (proof order)")
    ax.set_ylabel("Elapsed time (s)")
    ax.set_title("Learning Curve: Search Effort vs Experience")
    ax.legend()
    ax.grid(True, alpha=0.3)

    # --- Right: rolling average ---
    ax = axes[1]
    for an, label, color in [
        (an_on,  "Learning ON",  "steelblue"),
        (an_off, "Learning OFF", "tomato"),
    ]:
        roll = np.array(an["rolling_mean"])
        ax.plot(
            range(window - 1, n),
            roll,
            label=f"{label} (rolling avg w={window})",
            color=color,
        )

    ax.set_xlabel("Identity number")
    ax.set_ylabel("Elapsed time (s, rolling avg)")
    ax.set_title(f"Smoothed Learning Curve (window={window})")
    ax.legend()
    ax.grid(True, alpha=0.3)

    fig.tight_layout()
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    return output_path


# ── CLI ───────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Learning curve benchmark for EMLProverV2 neural scorer."
    )
    parser.add_argument("--n-identities", type=int, default=50)
    parser.add_argument("--n-runs",       type=int, default=5)
    parser.add_argument("--seed",         type=int, default=42)
    parser.add_argument(
        "--output", type=str, default="results/learning_curve.json",
    )
    args = parser.parse_args()

    print(f"Running with learning ENABLED  (n={args.n_identities}, runs={args.n_runs})...")
    t0 = time.perf_counter()
    res_on = run_learning_curve(
        n_identities=args.n_identities,
        n_runs=args.n_runs,
        seed=args.seed,
        enable_learning=True,
    )
    print(f"  Done in {time.perf_counter()-t0:.1f}s")

    print(f"Running with learning DISABLED (n={args.n_identities}, runs={args.n_runs})...")
    t0 = time.perf_counter()
    res_off = run_learning_curve(
        n_identities=args.n_identities,
        n_runs=args.n_runs,
        seed=args.seed,
        enable_learning=False,
    )
    print(f"  Done in {time.perf_counter()-t0:.1f}s")

    an_on  = analyze_learning_curve(res_on)
    an_off = analyze_learning_curve(res_off)

    plot_path = args.output.replace(".json", ".png")
    plot_learning_curve(res_on, res_off, plot_path)

    output = {
        "learning_enabled":  res_on,
        "learning_disabled": res_off,
        "analysis_learning":    an_on,
        "analysis_no_learning": an_off,
        "summary": {
            "improvement_ratio_learning":    an_on["improvement_ratio"],
            "improvement_ratio_no_learning": an_off["improvement_ratio"],
            "learning_benefit": an_on["improvement_ratio"] / max(
                an_off["improvement_ratio"], 1e-9
            ),
            "prove_rate_learning":    an_on["prove_rate"],
            "prove_rate_no_learning": an_off["prove_rate"],
        },
    }

    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    print(f"\nResults  : {args.output}")
    if plot_path:
        print(f"Plot     : {plot_path}")
    print("\nSummary:")
    print(f"  Learning ON  — improvement ratio: {an_on['improvement_ratio']:.2f}x")
    print(f"  Learning OFF — improvement ratio: {an_off['improvement_ratio']:.2f}x")
    print(f"  Learning benefit:                 {output['summary']['learning_benefit']:.2f}x")
    print(f"  Prove rate (ON):                  {an_on['prove_rate']:.0%}")
    print(f"  Prove rate (OFF):                 {an_off['prove_rate']:.0%}")


if __name__ == "__main__":
    main()
