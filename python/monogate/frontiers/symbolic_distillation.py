"""
monogate.frontiers.symbolic_distillation — Frontier 5: Symbolic Distillation

Train a black-box neural network on noisy physics data, then use EMLRegressor
to distill the learned function into an interpretable EML formula.

Key questions:
1. Does NN denoising help EMLRegressor succeed on laws where direct fitting
   fails?
2. For EML-native laws, how does distillation compare to direct fitting?
3. What formula does the NN "think" it learned? (interpretability)

Usage::

    from monogate.frontiers.symbolic_distillation import run_distillation_benchmark
    results = run_distillation_benchmark(verbose=True)

CLI::

    python -m monogate.frontiers.symbolic_distillation --n-simulations 1000
"""
from __future__ import annotations

import argparse
import json
import math
import os
import time
import warnings
from typing import Callable

import numpy as np

__all__ = [
    "distillation_pipeline",
    "run_distillation_benchmark",
    "interpretability_demo",
    "plot_distillation_results",
]

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _check_sklearn() -> None:
    """Raise ImportError with friendly message if sklearn is missing."""
    try:
        import sklearn  # noqa: F401
    except ImportError as exc:
        raise ImportError(
            "scikit-learn is required for symbolic distillation.\n"
            "Install it with:  pip install scikit-learn>=1.3"
        ) from exc


def _r2_score(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Coefficient of determination R²."""
    ss_res = float(np.sum((y_true - y_pred) ** 2))
    ss_tot = float(np.sum((y_true - np.mean(y_true)) ** 2))
    if ss_tot == 0.0:
        return 1.0 if ss_res == 0.0 else -math.inf
    return 1.0 - ss_res / ss_tot


def _safe_r2(reg, X: np.ndarray, y_true: np.ndarray) -> float:
    """Predict with *reg* and compute R²; return -inf on any error."""
    try:
        y_pred = reg.predict(X)
        return _r2_score(y_true, y_pred)
    except Exception:
        return -math.inf


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def distillation_pipeline(
    target_fn: Callable[[float], float],
    domain: tuple[float, float],
    name: str = "unknown",
    n_data: int = 60,
    noise: float = 0.05,
    nn_hidden: tuple = (64, 64),
    nn_max_iter: int = 2000,
    eml_max_depth: int = 3,
    eml_n_simulations: int = 3000,
    seed: int = 42,
) -> dict:
    """Full distillation pipeline for a single target function.

    Steps:
    1. Generate noisy synthetic data from *target_fn* on *domain*.
    2. Train ``sklearn.neural_network.MLPRegressor`` on noisy data.
    3. Sample clean NN predictions on a dense grid.
    4. Fit ``EMLRegressor`` to NN predictions  (distillation step).
    5. Also fit ``EMLRegressor`` directly to noisy data (baseline).

    Returns
    -------
    dict with keys:
        name, domain,
        direct_r2, direct_formula,
        distilled_r2, distilled_formula,
        nn_r2,
        elapsed_s
    """
    _check_sklearn()
    from sklearn.neural_network import MLPRegressor
    from monogate.sklearn_wrapper import EMLRegressor

    rng = np.random.default_rng(seed)
    t0 = time.perf_counter()

    lo, hi = domain
    # --- 1. Noisy training data ---
    x_train = rng.uniform(lo, hi, n_data)
    y_clean_train = np.array([target_fn(xi) for xi in x_train])
    noise_scale = noise * (np.max(y_clean_train) - np.min(y_clean_train) + 1e-12)
    y_noisy = y_clean_train + rng.normal(0.0, noise_scale, n_data)

    X_train = x_train.reshape(-1, 1)

    # --- 2. Train NN ---
    nn = MLPRegressor(
        hidden_layer_sizes=nn_hidden,
        max_iter=nn_max_iter,
        random_state=int(seed),
        n_iter_no_change=50,
        tol=1e-5,
    )
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        nn.fit(X_train, y_noisy)

    # NN quality on noise-free ground truth (same training grid)
    y_pred_nn_train = nn.predict(X_train)
    nn_r2 = _r2_score(y_clean_train, y_pred_nn_train)

    # --- 3. Dense NN predictions for distillation ---
    x_dense = np.linspace(lo, hi, 200)
    X_dense = x_dense.reshape(-1, 1)
    y_nn_dense = nn.predict(X_dense)
    y_true_dense = np.array([target_fn(xi) for xi in x_dense])

    # --- 4. Distillation: fit EMLRegressor to NN predictions ---
    eml_distilled = EMLRegressor(
        max_depth=eml_max_depth,
        n_simulations=eml_n_simulations,
        random_state=int(seed),
    )
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        eml_distilled.fit(X_dense, y_nn_dense)

    distilled_r2 = _safe_r2(eml_distilled, X_dense, y_true_dense)
    try:
        distilled_formula = eml_distilled.get_formula()
    except Exception:
        distilled_formula = "unavailable"

    # --- 5. Direct fit: EMLRegressor on noisy data ---
    eml_direct = EMLRegressor(
        max_depth=eml_max_depth,
        n_simulations=eml_n_simulations,
        random_state=int(seed),
    )
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        eml_direct.fit(X_train, y_noisy)

    direct_r2 = _safe_r2(eml_direct, X_dense, y_true_dense)
    try:
        direct_formula = eml_direct.get_formula()
    except Exception:
        direct_formula = "unavailable"

    elapsed = time.perf_counter() - t0

    return {
        "name": name,
        "domain": domain,
        "n_data": n_data,
        "noise": noise,
        "direct_r2": round(direct_r2, 4),
        "direct_formula": direct_formula,
        "distilled_r2": round(distilled_r2, 4),
        "distilled_formula": distilled_formula,
        "nn_r2": round(nn_r2, 4),
        "gain": round(distilled_r2 - direct_r2, 4),
        "elapsed_s": round(elapsed, 2),
    }


def run_distillation_benchmark(
    n_data: int = 60,
    noise: float = 0.05,
    nn_max_iter: int = 2000,
    eml_n_simulations: int = 3000,
    eml_max_depth: int = 3,
    seed: int = 42,
    verbose: bool = True,
) -> list[dict]:
    """Run distillation pipeline on all ``REDISCOVERY_LAWS``.

    Returns a list of result dicts (one per law).
    """
    from monogate.frontiers.law_complexity import REDISCOVERY_LAWS

    results = []
    header = f"{'Law':<35} {'NN R²':>7} {'Direct R²':>10} {'Distil R²':>10} {'Gain':>7}"
    sep = "-" * len(header)

    if verbose:
        print("\n" + "=" * 60)
        print("  SYMBOLIC DISTILLATION BENCHMARK")
        print("=" * 60)
        print(header)
        print(sep)

    for law in REDISCOVERY_LAWS:
        fn = law["fn"]
        domain = law["domain"]
        name = law["name"]

        result = distillation_pipeline(
            target_fn=fn,
            domain=domain,
            name=name,
            n_data=n_data,
            noise=noise,
            nn_max_iter=nn_max_iter,
            eml_max_depth=eml_max_depth,
            eml_n_simulations=eml_n_simulations,
            seed=seed,
        )
        results.append(result)

        if verbose:
            gain_str = f"{result['gain']:+.4f}"
            print(
                f"  {name:<33} {result['nn_r2']:>7.4f} "
                f"{result['direct_r2']:>10.4f} "
                f"{result['distilled_r2']:>10.4f} "
                f"{gain_str:>7}"
            )

    if verbose:
        print(sep)
        native = sum(1 for r in results if r["direct_r2"] > 0.95)
        improved = sum(1 for r in results if r["gain"] > 0.01)
        print(f"\n  EML-native (direct R²>0.95): {native}/{len(results)}")
        print(f"  Improved by distillation (gain>0.01): {improved}/{len(results)}")
        print("=" * 60 + "\n")

    return results


def interpretability_demo(
    nn_fn: Callable,
    domain: tuple[float, float],
    name: str = "NN",
    eml_n_simulations: int = 3000,
    eml_max_depth: int = 3,
    seed: int = 42,
) -> dict:
    """Recover a symbolic EML formula from any callable (e.g. trained NN).

    Given a black-box function *nn_fn* mapping a float to a float, this
    samples a dense grid and applies ``EMLRegressor`` to find the closest
    EML expression.

    Parameters
    ----------
    nn_fn:
        Any callable accepting a single float.  Typically a lambda wrapping
        a trained model's predict method.
    domain:
        (lo, hi) evaluation interval.
    name:
        Human-readable label for the function.
    eml_n_simulations, eml_max_depth:
        EMLRegressor search parameters.
    seed:
        Random state for reproducibility.

    Returns
    -------
    dict with keys: name, formula, r2, elapsed_s
    """
    _check_sklearn()
    from monogate.sklearn_wrapper import EMLRegressor
    import warnings

    lo, hi = domain
    x_grid = np.linspace(lo, hi, 200)
    y_grid = np.array([nn_fn(xi) for xi in x_grid])
    X_grid = x_grid.reshape(-1, 1)

    t0 = time.perf_counter()
    reg = EMLRegressor(
        max_depth=eml_max_depth,
        n_simulations=eml_n_simulations,
        random_state=int(seed),
    )
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        reg.fit(X_grid, y_grid)

    r2 = _safe_r2(reg, X_grid, y_grid)
    try:
        formula = reg.get_formula()
    except Exception:
        formula = "unavailable"

    return {
        "name": name,
        "formula": formula,
        "r2": round(r2, 4),
        "elapsed_s": round(time.perf_counter() - t0, 2),
    }


def plot_distillation_results(
    results: list[dict],
    output_path: str | None = None,
) -> None:
    """3-panel matplotlib figure: R² comparison, formula recovery, distillation gain.

    Parameters
    ----------
    results:
        List of result dicts from ``run_distillation_benchmark``.
    output_path:
        If given, save the figure to this path (PNG).  Otherwise show
        interactively.
    """
    try:
        import matplotlib.pyplot as plt
    except ImportError as exc:
        raise ImportError("matplotlib is required for plotting.") from exc

    names = [r["name"] for r in results]
    short = [n.split("(")[0].strip()[:22] for n in names]
    direct = [r["direct_r2"] for r in results]
    distilled = [r["distilled_r2"] for r in results]
    nn = [r["nn_r2"] for r in results]
    gain = [r["gain"] for r in results]
    n = len(results)
    idx = np.arange(n)

    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    fig.suptitle("Symbolic Distillation: EMLRegressor + NN Denoising", fontsize=13)

    # Panel 1: R² comparison
    ax = axes[0]
    w = 0.25
    ax.bar(idx - w, direct, width=w, label="Direct EML", color="steelblue")
    ax.bar(idx,       distilled, width=w, label="Distilled EML", color="coral")
    ax.bar(idx + w, nn, width=w, label="NN (teacher)", color="forestgreen", alpha=0.7)
    ax.set_xticks(idx)
    ax.set_xticklabels(short, rotation=45, ha="right", fontsize=8)
    ax.set_ylabel("R²")
    ax.set_title("R² by method")
    ax.legend(fontsize=8)
    ax.axhline(0.95, color="gray", linestyle="--", linewidth=0.8)
    ax.set_ylim(bottom=min(-0.5, min(direct + distilled) - 0.1))

    # Panel 2: formula recovery rate at threshold
    ax = axes[1]
    thresholds = [0.5, 0.8, 0.9, 0.95, 0.99]
    direct_rate = [sum(1 for v in direct if v >= t) / n for t in thresholds]
    distill_rate = [sum(1 for v in distilled if v >= t) / n for t in thresholds]
    t_labels = [str(t) for t in thresholds]
    x_pos = np.arange(len(thresholds))
    ax.bar(x_pos - 0.2, direct_rate, width=0.35, label="Direct", color="steelblue")
    ax.bar(x_pos + 0.2, distill_rate, width=0.35, label="Distilled", color="coral")
    ax.set_xticks(x_pos)
    ax.set_xticklabels([f"R²≥{t}" for t in thresholds], fontsize=9)
    ax.set_ylabel("Fraction of laws")
    ax.set_title("Formula recovery rate by R² threshold")
    ax.legend(fontsize=9)
    ax.set_ylim(0, 1.05)

    # Panel 3: gain from distillation
    ax = axes[2]
    colors = ["coral" if g > 0.01 else ("steelblue" if g < -0.01 else "gray")
              for g in gain]
    ax.barh(idx, gain, color=colors)
    ax.set_yticks(idx)
    ax.set_yticklabels(short, fontsize=8)
    ax.axvline(0, color="black", linewidth=0.8)
    ax.axvline(0.01, color="gray", linestyle="--", linewidth=0.7)
    ax.set_xlabel("Distilled R² − Direct R²")
    ax.set_title("Gain from NN distillation")

    plt.tight_layout()
    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches="tight")
        print(f"Figure saved to {output_path}")
    else:
        plt.show()


# ---------------------------------------------------------------------------
# Full pipeline runner
# ---------------------------------------------------------------------------

def run_full_distillation(
    n_data: int = 60,
    noise: float = 0.05,
    n_simulations: int = 3000,
    output: str | None = None,
    verbose: bool = True,
) -> dict:
    """Full pipeline: benchmark + optional JSON save.

    Parameters
    ----------
    n_data:
        Training samples per law.
    noise:
        Noise fraction (relative to signal range).
    n_simulations:
        EMLRegressor MCTS budget.
    output:
        Path to save JSON results; auto-generated under results/ if None.
    verbose:
        Print progress.

    Returns
    -------
    dict with keys: results, summary
    """
    results = run_distillation_benchmark(
        n_data=n_data,
        noise=noise,
        eml_n_simulations=n_simulations,
        verbose=verbose,
    )

    native = sum(1 for r in results if r["direct_r2"] > 0.95)
    improved = sum(1 for r in results if r["gain"] > 0.01)
    payload = {
        "params": {"n_data": n_data, "noise": noise, "n_simulations": n_simulations},
        "summary": {
            "n_laws": len(results),
            "eml_native": native,
            "improved_by_distillation": improved,
        },
        "results": results,
    }

    # Always save to results dir
    out_dir = os.path.join(os.path.dirname(__file__), "..", "..", "results",
                           "symbolic_distillation")
    os.makedirs(out_dir, exist_ok=True)
    from datetime import datetime
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    auto_path = os.path.join(out_dir, f"distillation_{ts}.json")
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
        description="Symbolic Distillation — NN → EML formula recovery"
    )
    parser.add_argument("--n-data", type=int, default=60,
                        help="Training samples per law (default 60)")
    parser.add_argument("--noise", type=float, default=0.05,
                        help="Noise fraction relative to signal range (default 0.05)")
    parser.add_argument("--n-simulations", type=int, default=3000,
                        help="MCTS budget for EMLRegressor (default 3000)")
    parser.add_argument("--output", type=str, default=None,
                        help="Path to save JSON results (optional)")
    parser.add_argument("--plot", type=str, default=None,
                        help="Path to save figure PNG (optional; requires matplotlib)")
    args = parser.parse_args()

    payload = run_full_distillation(
        n_data=args.n_data,
        noise=args.noise,
        n_simulations=args.n_simulations,
        output=args.output,
        verbose=True,
    )

    if args.plot:
        plot_distillation_results(payload["results"], output_path=args.plot)


if __name__ == "__main__":
    main()
