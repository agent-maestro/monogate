"""
monogate.frontiers.transfer_learning
======================================
Experiment 2: Does learning on one identity category transfer to another?

Usage::

    cd python
    # Single pair
    python -m monogate.frontiers.transfer_learning \\
        --train trig --test hyperbolic --n-runs 2

    # Full 5x5 matrix (slow)
    python -m monogate.frontiers.transfer_learning \\
        --full-matrix --n-runs 2 --output results/transfer_learning.json
"""

from __future__ import annotations

import argparse
import json
import os
import time
from typing import Any

import numpy as np

# ── Category mapping ──────────────────────────────────────────────────────────

CATEGORY_KEYS: dict[str, str] = {
    "trig":        "trigonometric",
    "hyperbolic":  "hyperbolic",
    "exponential": "exponential",
    "special":     "special",
    "physics":     "physics",
}


def _get_category(short: str) -> list:
    from monogate.identities import get_by_category
    full = CATEGORY_KEYS.get(short, short)
    return get_by_category(full)


# ── Core experiment ───────────────────────────────────────────────────────────

def run_transfer_experiment(
    train_cat: str,
    test_cat: str,
    n_runs: int = 3,
    max_train: int | None = None,
    max_test:  int | None = None,
) -> dict:
    """Measure transfer benefit from *train_cat* to *test_cat*.

    Protocol
    --------
    **Baseline**: fresh EMLProverV2(enable_learning=False) on test identities.
    **Transfer**: EMLProverV2(enable_learning=True) trained on *train_cat*,
    then scorer frozen (``prover.scorer = None``) before testing on *test_cat*.

    Transfer benefit > 1.0 means transfer helped; < 1.0 means it hurt.
    """
    from monogate.prover import EMLProverV2

    train_ids = _get_category(train_cat)
    test_ids  = _get_category(test_cat)

    if max_train is not None:
        train_ids = train_ids[:max_train]
    if max_test is not None:
        test_ids = test_ids[:max_test]

    results: dict[str, Any] = {
        "train_category": train_cat,
        "test_category":  test_cat,
        "n_train": len(train_ids),
        "n_test":  len(test_ids),
        "runs": [],
    }

    for run_idx in range(n_runs):
        # ── Baseline: no learning ────────────────────────────────────────────
        baseline_prover = EMLProverV2(enable_learning=False)
        baseline_elapsed = []
        for identity in test_ids:
            r = baseline_prover.prove(identity.expression)
            baseline_elapsed.append(r.elapsed_s)

        # ── Transfer: train then freeze ──────────────────────────────────────
        transfer_prover = EMLProverV2(enable_learning=True)
        # Training phase
        for identity in train_ids:
            transfer_prover.prove(identity.expression)
        # Freeze: remove scorer so it no longer blends into MCTS
        transfer_prover.scorer = None

        transfer_elapsed = []
        for identity in test_ids:
            r = transfer_prover.prove(identity.expression)
            transfer_elapsed.append(r.elapsed_s)

        baseline_mean  = float(np.mean(baseline_elapsed))  if baseline_elapsed  else 0.0
        transfer_mean  = float(np.mean(transfer_elapsed))  if transfer_elapsed  else 0.0

        results["runs"].append({
            "run_idx":       run_idx,
            "baseline_elapsed":  baseline_elapsed,
            "transfer_elapsed":  transfer_elapsed,
            "baseline_mean":     baseline_mean,
            "transfer_mean":     transfer_mean,
        })

    # ── Aggregate ────────────────────────────────────────────────────────────
    baseline_means = [r["baseline_mean"]  for r in results["runs"]]
    transfer_means = [r["transfer_mean"]  for r in results["runs"]]

    agg_baseline = float(np.mean(baseline_means)) if baseline_means else 0.0
    agg_transfer = float(np.mean(transfer_means)) if transfer_means else 0.0

    results["aggregate"] = {
        "baseline_mean":    agg_baseline,
        "transfer_mean":    agg_transfer,
        "transfer_benefit": agg_baseline / max(agg_transfer, 1e-9),
        "transfer_helps":   agg_transfer < agg_baseline,
    }

    return results


# ── Transfer matrix ───────────────────────────────────────────────────────────

def compute_transfer_matrix(
    n_runs: int = 2,
    max_train: int = 10,
    max_test:  int = 8,
) -> dict:
    """Compute a 5×5 transfer-benefit matrix for all category pairs.

    Diagonal entries are always 1.0 (same-category baseline).
    """
    categories = list(CATEGORY_KEYS.keys())
    matrix: dict[str, dict[str, float]] = {}
    raw: dict[str, dict[str, Any]] = {}

    total = len(categories) ** 2 - len(categories)
    done = 0

    for train_cat in categories:
        matrix[train_cat] = {}
        raw[train_cat] = {}
        for test_cat in categories:
            if train_cat == test_cat:
                matrix[train_cat][test_cat] = 1.0
                raw[train_cat][test_cat] = {"transfer_benefit": 1.0}
                continue
            print(f"  [{done+1}/{total}] {train_cat} → {test_cat} ...")
            exp = run_transfer_experiment(
                train_cat, test_cat,
                n_runs=n_runs,
                max_train=max_train,
                max_test=max_test,
            )
            benefit = exp["aggregate"]["transfer_benefit"]
            matrix[train_cat][test_cat] = benefit
            raw[train_cat][test_cat] = exp["aggregate"]
            done += 1

    return {"matrix": matrix, "raw": raw, "categories": categories}


# ── Visualization ─────────────────────────────────────────────────────────────

def plot_transfer_matrix(matrix_data: dict, output_path: str) -> str:
    """Heatmap of transfer benefits."""
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("[warning] matplotlib not installed — skipping plot")
        return ""

    categories = matrix_data["categories"]
    matrix = matrix_data["matrix"]
    n = len(categories)

    data = np.zeros((n, n))
    for i, train_cat in enumerate(categories):
        for j, test_cat in enumerate(categories):
            data[i, j] = matrix[train_cat][test_cat]

    fig, ax = plt.subplots(figsize=(8, 6))
    im = ax.imshow(data, cmap="RdYlGn", vmin=0.5, vmax=2.0)

    ax.set_xticks(range(n))
    ax.set_yticks(range(n))
    ax.set_xticklabels(categories, rotation=45, ha="right")
    ax.set_yticklabels(categories)
    ax.set_xlabel("Test Category")
    ax.set_ylabel("Train Category")
    ax.set_title("Transfer Learning Benefit (>1 = helps, <1 = hurts)")

    for i in range(n):
        for j in range(n):
            val = data[i, j]
            color = "white" if (val > 1.6 or val < 0.65) else "black"
            ax.text(j, i, f"{val:.2f}", ha="center", va="center", color=color, fontsize=9)

    plt.colorbar(im)
    fig.tight_layout()
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    return output_path


# ── CLI ───────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Transfer learning experiment for EMLProverV2."
    )
    parser.add_argument(
        "--train", type=str, default="trig",
        help=f"Train category. Choices: {list(CATEGORY_KEYS)}"
    )
    parser.add_argument(
        "--test", type=str, default="hyperbolic",
        help="Test category."
    )
    parser.add_argument("--n-runs",     type=int, default=3)
    parser.add_argument("--max-train",  type=int, default=None)
    parser.add_argument("--max-test",   type=int, default=None)
    parser.add_argument("--full-matrix", action="store_true",
                        help="Compute full 5x5 matrix (slow).")
    parser.add_argument(
        "--output", type=str, default="results/transfer_learning.json"
    )
    args = parser.parse_args()

    if args.full_matrix:
        print("Computing full 5x5 transfer matrix...")
        t0 = time.perf_counter()
        result = compute_transfer_matrix(
            n_runs=args.n_runs,
            max_train=args.max_train or 10,
            max_test=args.max_test or 8,
        )
        print(f"Done in {time.perf_counter()-t0:.1f}s")

        plot_path = args.output.replace(".json", "_matrix.png")
        plot_transfer_matrix(result, plot_path)

        os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)
        print(f"\nResults  : {args.output}")
        print(f"Heatmap  : {plot_path}")

        print("\nTransfer matrix (benefit > 1.0 means training helped):")
        cats = result["categories"]
        header = f"{'':12s} " + "  ".join(f"{c:12s}" for c in cats)
        print(header)
        for train_cat in cats:
            row = f"{train_cat:12s} "
            row += "  ".join(
                f"{result['matrix'][train_cat][test_cat]:12.3f}" for test_cat in cats
            )
            print(row)
    else:
        print(f"Transfer experiment: {args.train} → {args.test}  (n_runs={args.n_runs})")
        t0 = time.perf_counter()
        result = run_transfer_experiment(
            args.train, args.test,
            n_runs=args.n_runs,
            max_train=args.max_train,
            max_test=args.max_test,
        )
        elapsed = time.perf_counter() - t0
        agg = result["aggregate"]
        print(f"\nDone in {elapsed:.1f}s")
        print(f"  Baseline mean  : {agg['baseline_mean']:.3f}s")
        print(f"  Transfer mean  : {agg['transfer_mean']:.3f}s")
        print(f"  Transfer benefit: {agg['transfer_benefit']:.2f}x")
        print(f"  Transfer helps : {agg['transfer_helps']}")

        os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)
        print(f"\nResults: {args.output}")


if __name__ == "__main__":
    main()
