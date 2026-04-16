"""
monogate.frontiers.pretrain_scorer
====================================
Experiment 3: Pre-train the neural scorer on all 151 identities.

The trained scorer is saved to ``monogate/data/pretrained_scorer.json`` so
that ``EMLProverV2(use_pretrained=True)`` loads it automatically.

Usage::

    cd python
    # Quick 1-epoch pre-train (fast sanity check)
    python -m monogate.frontiers.pretrain_scorer \\
        --n-epochs 1 --output monogate/data/pretrained_scorer.json

    # Full 3-epoch pre-train
    python -m monogate.frontiers.pretrain_scorer \\
        --n-epochs 3 --output monogate/data/pretrained_scorer.json

    # Benchmark pretrained vs fresh
    python -m monogate.frontiers.pretrain_scorer --benchmark-only
"""

from __future__ import annotations

import argparse
import json
import os
import random
import time
from typing import Any

import numpy as np


# ── Pre-training ──────────────────────────────────────────────────────────────

def pretrain_scorer(
    n_epochs: int = 3,
    seed: int = 42,
) -> tuple:
    """Train scorer on ALL_IDENTITIES for *n_epochs* passes.

    Returns
    -------
    (scorer, stats)
        ``scorer`` is a :class:`~monogate.neural_scorer.FeatureBasedEMLScorer`
        with weights updated from proved witnesses.
        ``stats`` is a list of per-epoch dicts.
    """
    from monogate.identities import ALL_IDENTITIES
    from monogate.prover import EMLProverV2

    prover = EMLProverV2(enable_learning=True)
    identities = list(ALL_IDENTITIES)
    n_total = len(identities)
    stats: list[dict[str, Any]] = []

    for epoch in range(n_epochs):
        print(f"\n=== Epoch {epoch + 1}/{n_epochs} ===")
        rng = random.Random(seed + epoch)
        rng.shuffle(identities)

        n_proved = 0
        n_failed = 0

        for i, identity in enumerate(identities):
            try:
                result = prover.prove(identity.expression)
                if result.proved():
                    n_proved += 1
                else:
                    n_failed += 1
            except Exception as exc:
                print(f"  [error] {identity.name}: {exc}")
                n_failed += 1

            if (i + 1) % 25 == 0:
                buf_size = len(prover.scorer._buffer)
                print(f"  {i + 1}/{n_total}  proved={n_proved}  "
                      f"failed={n_failed}  buffer={buf_size}")

        buf_size = len(prover.scorer._buffer)
        trained = prover.scorer.is_trained()
        print(f"  Epoch {epoch + 1}: proved={n_proved}  failed={n_failed}  "
              f"buffer={buf_size}  is_trained={trained}")
        stats.append({
            "epoch":       epoch + 1,
            "n_proved":    n_proved,
            "n_failed":    n_failed,
            "buffer_size": buf_size,
            "is_trained":  trained,
        })

    return prover.scorer, stats


# ── Benchmark ─────────────────────────────────────────────────────────────────

def benchmark_pretrained(n_test: int = 15) -> dict:
    """Compare ``use_pretrained=True`` vs fresh scorer on easy identities.

    Returns elapsed_s stats for both and a speedup ratio.
    """
    from monogate.identities import get_by_difficulty
    from monogate.prover import EMLProverV2

    test_ids = get_by_difficulty("easy")[:n_test]
    if not test_ids:
        from monogate.identities import ALL_IDENTITIES
        test_ids = list(ALL_IDENTITIES)[:n_test]

    # ── Fresh scorer ─────────────────────────────────────────────────────────
    fresh_prover = EMLProverV2(use_pretrained=False, enable_learning=False)
    fresh_elapsed = []
    for identity in test_ids:
        r = fresh_prover.prove(identity.expression)
        fresh_elapsed.append(r.elapsed_s)

    # ── Pretrained scorer ─────────────────────────────────────────────────────
    pretrained_prover = EMLProverV2(use_pretrained=True, enable_learning=False)
    pretrained_elapsed = []
    for identity in test_ids:
        r = pretrained_prover.prove(identity.expression)
        pretrained_elapsed.append(r.elapsed_s)

    fresh_mean      = float(np.mean(fresh_elapsed))
    pretrained_mean = float(np.mean(pretrained_elapsed))
    speedup         = fresh_mean / max(pretrained_mean, 1e-9)

    return {
        "n_test":          len(test_ids),
        "fresh_mean_s":    fresh_mean,
        "pretrained_mean_s": pretrained_mean,
        "speedup":         speedup,
        "pretrained_faster": pretrained_mean < fresh_mean,
        "fresh_elapsed":   fresh_elapsed,
        "pretrained_elapsed": pretrained_elapsed,
    }


# ── CLI ───────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Pre-train the EMLProverV2 neural scorer on all identities."
    )
    parser.add_argument("--n-epochs",    type=int, default=3)
    parser.add_argument("--seed",        type=int, default=42)
    parser.add_argument(
        "--output", type=str,
        default=os.path.join(
            os.path.dirname(__file__), "..", "data", "pretrained_scorer.json"
        ),
        help="Where to save the pre-trained scorer weights (JSON).",
    )
    parser.add_argument(
        "--stats-output", type=str,
        default="results/pretrain_stats.json",
    )
    parser.add_argument(
        "--benchmark-only", action="store_true",
        help="Skip pretraining; just benchmark pretrained vs fresh.",
    )
    parser.add_argument("--n-benchmark", type=int, default=15)
    args = parser.parse_args()

    if not args.benchmark_only:
        print(f"Pre-training scorer ({args.n_epochs} epoch(s))...")
        t0 = time.perf_counter()
        scorer, stats = pretrain_scorer(n_epochs=args.n_epochs, seed=args.seed)
        elapsed = time.perf_counter() - t0
        print(f"\nPre-training complete in {elapsed:.1f}s")

        # Save scorer
        out_path = os.path.abspath(args.output)
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        scorer.save(out_path)
        print(f"Scorer saved: {out_path}")

        # Save stats
        stats_path = os.path.abspath(args.stats_output)
        os.makedirs(os.path.dirname(stats_path), exist_ok=True)
        with open(stats_path, "w", encoding="utf-8") as f:
            json.dump({"epochs": stats, "elapsed_s": elapsed}, f, indent=2)
        print(f"Stats saved: {stats_path}")

    # Benchmark
    print(f"\nBenchmarking pretrained vs fresh (n={args.n_benchmark})...")
    bench = benchmark_pretrained(n_test=args.n_benchmark)
    print(f"  Fresh scorer   : {bench['fresh_mean_s']:.3f}s / proof")
    print(f"  Pretrained     : {bench['pretrained_mean_s']:.3f}s / proof")
    print(f"  Speedup        : {bench['speedup']:.2f}x")
    print(f"  Pretrained faster: {bench['pretrained_faster']}")


if __name__ == "__main__":
    main()
