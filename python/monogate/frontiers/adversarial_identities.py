"""
monogate.frontiers.adversarial_identities
==========================================
Experiment 5: What are the neural scorer's blind spots?

Generate adversarial variants of known-good identities by applying
syntactic transformations that preserve truth but change surface form.
Measure how much harder (or easier) the prover finds each variant.

Usage::

    cd python
    # Quick benchmark (5 identities × 3 methods)
    python -m monogate.frontiers.adversarial_identities \\
        --n-identities 5 --output results/adversarial_benchmark.json

    # Full benchmark + training loop (20 identities, 3 rounds)
    python -m monogate.frontiers.adversarial_identities \\
        --n-identities 20 --training-loop --n-rounds 3 \\
        --output results/adversarial_benchmark.json
"""

from __future__ import annotations

import argparse
import json
import os
import time
from typing import Any

import numpy as np


# ── Adversarial Generator ─────────────────────────────────────────────────────

class AdversarialGenerator:
    """Generate truth-preserving variants of mathematical identities.

    Each method takes an expression string of the form ``lhs == rhs`` (or
    just an expression) and returns an equivalent but syntactically different
    expression.

    Requires ``sympy``; individual methods are no-ops if sympy is absent.
    """

    def __init__(self) -> None:
        try:
            import sympy as sp  # noqa: F401
            self._has_sympy = True
        except ImportError:
            self._has_sympy = False

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _split_eq(self, expr_str: str) -> tuple[str, str | None]:
        """Split 'lhs == rhs' into (lhs, rhs). Returns (expr, None) if no ==."""
        if "==" in expr_str:
            parts = expr_str.split("==", 1)
            return parts[0].strip(), parts[1].strip()
        return expr_str.strip(), None

    def _join_eq(self, lhs: str, rhs: str | None) -> str:
        if rhs is None:
            return lhs
        return f"{lhs} == {rhs}"

    def _parse(self, expr_str: str):
        """Parse expression with sympy."""
        import sympy as sp
        return sp.sympify(expr_str, evaluate=True)

    # ── Transformation methods ────────────────────────────────────────────────

    def expand_trig(self, expr_str: str) -> str:
        """Apply sympy.expand_trig to the LHS."""
        if not self._has_sympy:
            return expr_str
        try:
            import sympy as sp
            lhs, rhs = self._split_eq(expr_str)
            expanded = sp.expand_trig(self._parse(lhs))
            return self._join_eq(str(expanded), rhs)
        except Exception:
            return expr_str

    def add_zero(self, expr_str: str) -> str:
        """Append '+ (sin(x)**2 + cos(x)**2 - 1)' to the LHS (adds zero)."""
        if not self._has_sympy:
            return expr_str
        try:
            import sympy as sp
            lhs, rhs = self._split_eq(expr_str)
            x = sp.Symbol("x")
            zero = sp.sin(x)**2 + sp.cos(x)**2 - 1
            new_lhs = sp.simplify(self._parse(lhs) + zero)
            return self._join_eq(str(new_lhs), rhs)
        except Exception:
            return expr_str

    def double_and_halve(self, expr_str: str) -> str:
        """Multiply LHS by 2, multiply RHS by 2 (identity preserved)."""
        if not self._has_sympy:
            return expr_str
        try:
            import sympy as sp
            lhs, rhs = self._split_eq(expr_str)
            new_lhs = sp.simplify(2 * self._parse(lhs))
            if rhs is not None:
                new_rhs = sp.simplify(2 * self._parse(rhs))
                return self._join_eq(str(new_lhs), str(new_rhs))
            return str(new_lhs)
        except Exception:
            return expr_str

    def rewrite_sin_cos(self, expr_str: str) -> str:
        """Rewrite LHS using complex exponential form via sympy.rewrite."""
        if not self._has_sympy:
            return expr_str
        try:
            import sympy as sp
            lhs, rhs = self._split_eq(expr_str)
            rewritten = self._parse(lhs).rewrite(sp.exp)
            return self._join_eq(str(rewritten), rhs)
        except Exception:
            return expr_str

    def negate_both(self, expr_str: str) -> str:
        """Negate LHS and RHS: a == b becomes -a == -b."""
        if not self._has_sympy:
            return expr_str
        try:
            import sympy as sp
            lhs, rhs = self._split_eq(expr_str)
            new_lhs = sp.simplify(-self._parse(lhs))
            if rhs is not None:
                new_rhs = sp.simplify(-self._parse(rhs))
                return self._join_eq(str(new_lhs), str(new_rhs))
            return str(new_lhs)
        except Exception:
            return expr_str

    def generate(self, expr_str: str, method: str) -> str:
        """Generate an adversarial variant using the named method."""
        fn = getattr(self, method, None)
        if fn is None:
            raise ValueError(f"Unknown method: {method!r}")
        return fn(expr_str)

    @property
    def methods(self) -> list[str]:
        """List of all transformation method names."""
        return ["expand_trig", "add_zero", "double_and_halve",
                "rewrite_sin_cos", "negate_both"]


# ── Gap measurement ───────────────────────────────────────────────────────────

def measure_gap(prover, original_expr: str, adversarial_expr: str) -> dict:
    """Measure how much harder the adversarial form is to prove.

    Parameters
    ----------
    prover:
        A live :class:`~monogate.prover.EMLProverV2` instance.
    original_expr:
        The original identity expression string.
    adversarial_expr:
        The transformed (adversarial) expression string.

    Returns
    -------
    dict with keys: original_elapsed_s, adversarial_elapsed_s, gap_ratio,
    original_proved, adversarial_proved.
    gap_ratio = adversarial / original  (>1 means adversarial harder).
    """
    r_orig = prover.prove(original_expr)
    r_adv  = prover.prove(adversarial_expr)

    orig_t = r_orig.elapsed_s
    adv_t  = r_adv.elapsed_s
    gap    = adv_t / max(orig_t, 1e-9)

    return {
        "original_expr":       original_expr,
        "adversarial_expr":    adversarial_expr,
        "original_elapsed_s":  orig_t,
        "adversarial_elapsed_s": adv_t,
        "gap_ratio":           gap,
        "original_proved":     r_orig.proved(),
        "adversarial_proved":  r_adv.proved(),
    }


# ── Benchmark ─────────────────────────────────────────────────────────────────

def run_adversarial_benchmark(
    n_identities: int = 20,
    methods: list[str] | None = None,
) -> dict:
    """Run the adversarial benchmark on *n_identities* trigonometric identities.

    For each identity and each method:
    - Generate adversarial variant
    - Prove both original and adversarial
    - Record gap_ratio

    Returns
    -------
    dict with keys: results (list), mean_gap, max_gap, robustness_score,
    method_breakdown (dict[method, mean_gap]).
    """
    from monogate.identities import get_by_category
    from monogate.prover import EMLProverV2

    gen = AdversarialGenerator()
    if methods is None:
        methods = gen.methods

    # Use trig identities as primary targets (rich in sin/cos patterns)
    trig_ids = get_by_category("trigonometric")[:n_identities]
    if not trig_ids:
        from monogate.identities import ALL_IDENTITIES
        trig_ids = list(ALL_IDENTITIES)[:n_identities]

    prover = EMLProverV2(enable_learning=False)
    results: list[dict[str, Any]] = []

    for identity in trig_ids:
        orig_expr = identity.expression
        for method in methods:
            adv_expr = gen.generate(orig_expr, method)
            if adv_expr == orig_expr:
                # transformation was a no-op (e.g., sympy absent) — skip
                continue
            gap_result = measure_gap(prover, orig_expr, adv_expr)
            gap_result["identity_name"] = identity.name
            gap_result["method"] = method
            results.append(gap_result)

    if not results:
        return {
            "results": [],
            "mean_gap": 1.0,
            "max_gap":  1.0,
            "robustness_score": 1.0,
            "method_breakdown": {},
        }

    gaps = [r["gap_ratio"] for r in results]
    mean_gap = float(np.mean(gaps))
    max_gap  = float(np.max(gaps))
    robustness_score = 1.0 / (1.0 + mean_gap)

    method_breakdown: dict[str, float] = {}
    for method in methods:
        method_gaps = [r["gap_ratio"] for r in results if r["method"] == method]
        if method_gaps:
            method_breakdown[method] = float(np.mean(method_gaps))

    return {
        "results":           results,
        "mean_gap":          mean_gap,
        "max_gap":           max_gap,
        "robustness_score":  robustness_score,
        "method_breakdown":  method_breakdown,
        "n_identities":      len(trig_ids),
        "n_methods":         len(methods),
        "n_results":         len(results),
    }


# ── Adversarial training loop ─────────────────────────────────────────────────

def adversarial_training_loop(
    n_rounds: int = 3,
    n_identities: int = 10,
    gap_threshold: float = 2.0,
) -> list[dict]:
    """Iterative adversarial hardening loop.

    Protocol
    --------
    Each round:
    1. Run benchmark to find hard adversarial examples (gap > threshold).
    2. Prove them using a *learning* prover (updates scorer).
    3. Re-score overall robustness.

    Returns
    -------
    List of per-round dicts with: round, pre_robustness, post_robustness,
    n_hard_examples, learning_delta.
    """
    from monogate.prover import EMLProverV2

    gen = AdversarialGenerator()
    learning_prover = EMLProverV2(enable_learning=True)
    history: list[dict[str, Any]] = []

    for round_idx in range(n_rounds):
        bench = run_adversarial_benchmark(n_identities=n_identities)
        pre_robustness = bench["robustness_score"]

        # Find hard examples
        hard = [r for r in bench["results"] if r["gap_ratio"] > gap_threshold]

        # Train on hard examples
        for r in hard:
            adv_expr = r["adversarial_expr"]
            try:
                learning_prover.prove(adv_expr)
            except Exception:
                pass

        # Re-evaluate
        bench2 = run_adversarial_benchmark(n_identities=n_identities)
        post_robustness = bench2["robustness_score"]

        history.append({
            "round":            round_idx + 1,
            "pre_robustness":   pre_robustness,
            "post_robustness":  post_robustness,
            "n_hard_examples":  len(hard),
            "learning_delta":   post_robustness - pre_robustness,
            "pre_mean_gap":     bench["mean_gap"],
            "post_mean_gap":    bench2["mean_gap"],
        })

        print(f"  Round {round_idx+1}/{n_rounds}: "
              f"hard={len(hard)}  "
              f"robustness: {pre_robustness:.3f} → {post_robustness:.3f}")

    return history


# ── CLI ───────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Adversarial identity benchmark for EMLProverV2."
    )
    parser.add_argument("--n-identities", type=int, default=20)
    parser.add_argument(
        "--methods", type=str, default=None,
        help="Comma-separated list of methods (default: all)."
    )
    parser.add_argument(
        "--training-loop", action="store_true",
        help="Run adversarial hardening loop after benchmark."
    )
    parser.add_argument("--n-rounds",       type=int, default=3)
    parser.add_argument("--gap-threshold",  type=float, default=2.0)
    parser.add_argument(
        "--output", type=str, default="results/adversarial_benchmark.json"
    )
    args = parser.parse_args()

    methods = args.methods.split(",") if args.methods else None

    print(f"Running adversarial benchmark (n={args.n_identities})...")
    t0 = time.perf_counter()
    bench = run_adversarial_benchmark(
        n_identities=args.n_identities,
        methods=methods,
    )
    elapsed = time.perf_counter() - t0

    print(f"\nDone in {elapsed:.1f}s")
    print(f"  Mean gap ratio   : {bench['mean_gap']:.3f}x")
    print(f"  Max gap ratio    : {bench['max_gap']:.3f}x")
    print(f"  Robustness score : {bench['robustness_score']:.3f}")
    print(f"  Method breakdown :")
    for method, gap in sorted(bench["method_breakdown"].items(), key=lambda x: -x[1]):
        print(f"    {method:20s}: {gap:.3f}x")

    output: dict[str, Any] = {"benchmark": bench}

    if args.training_loop:
        print(f"\nRunning adversarial training loop ({args.n_rounds} rounds)...")
        history = adversarial_training_loop(
            n_rounds=args.n_rounds,
            n_identities=args.n_identities,
            gap_threshold=args.gap_threshold,
        )
        output["training_loop"] = history

        if history:
            first = history[0]["pre_robustness"]
            last  = history[-1]["post_robustness"]
            print(f"\n  Overall robustness: {first:.3f} → {last:.3f}  "
                  f"(delta={last - first:+.3f})")

    out_path = os.path.abspath(args.output)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)
    print(f"\nResults: {out_path}")


if __name__ == "__main__":
    main()
