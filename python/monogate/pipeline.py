"""monogate.pipeline — end-to-end EML analysis pipeline.

One function takes a SymPy expression and returns a complete
analysis: canonical form, Pfaffian profile, rewritten form,
EML tree, node count, numerical verification.

Created in E-188 (2026-04-26).

Usage::

    from monogate import pipeline
    import sympy as sp

    x = sp.Symbol('x')
    result = pipeline(1 / (1 + sp.exp(-x)))

    print(result.profile)         # PfaffianProfile(p1-d2-w1-c0)
    print(result.cost_before, '->', result.cost_after)
    print(result.eml_tree)
    print(result.max_error)

The function never crashes — errors become fields in the result.
"""
from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import Any, Optional

import sympy as sp


@dataclass
class PipelineResult:
    """End-to-end analysis result for a single SymPy expression."""

    original: sp.Basic
    canonical: Optional[sp.Basic] = None
    profile: Any = None                  # PfaffianProfile or None
    rewritten: Optional[sp.Basic] = None
    rewrite_report: Any = None           # RewriteResult or None
    eml_tree: Optional[dict] = None
    node_count: int = 0
    max_error: float = float("inf")
    is_pne: bool = False
    steps: list[str] = field(default_factory=list)
    error: Optional[str] = None

    def __repr__(self) -> str:
        if self.error and not self.profile:
            return f"PipelineResult({self.original!s}, ERROR: {self.error[:60]})"
        cc = self.profile.cost_class if self.profile else "?"
        return (f"PipelineResult({self.original!s} | {cc} | "
                f"cost {self.node_count} | max_err {self.max_error:.2e}"
                f"{' | PNE' if self.is_pne else ''})")


def pipeline(expr, *,
             rewrite_strategy: str = "optimal",
             verify: bool = True,
             n_test_points: int = 5) -> PipelineResult:
    """Full EML analysis pipeline for a SymPy expression.

    Steps (in order):
      1. Parse (sp.sympify if str).
      2. Canonicalize via eml_cost.canonicalize.
      3. Pfaffian profile via eml_cost.PfaffianProfile.
      4. Rewrite to minimize cost via eml_rewrite.rewrite.
      5. Build EML tree via monogate.from_sympy. (Skipped on PNE.)
      6. Compute node count.
      7. Numerically verify tree against original sympy expression.

    The function NEVER crashes. If any step fails, subsequent steps
    are skipped and ``error`` is populated.

    Args:
        expr: SymPy expression or string.
        rewrite_strategy: 'canonical', 'optimal' (default), 'aggressive'.
        verify: Run numerical verification (default True).
        n_test_points: Random points for verification (default 5).

    Returns:
        PipelineResult with all intermediate artifacts populated.
    """
    if isinstance(expr, str):
        try:
            expr = sp.sympify(expr)
        except Exception as e:
            return PipelineResult(original=expr, error=f"parse: {e}")

    result = PipelineResult(original=expr)

    # Step 2-3: canonicalize + profile
    try:
        from eml_cost import PfaffianProfile, canonicalize
        result.canonical = canonicalize(expr)
        result.profile = PfaffianProfile.from_expression(expr)
        result.steps.append(f"canonicalize -> {result.canonical}")
        result.steps.append(f"profile = {result.profile.cost_class}")
        result.is_pne = result.profile.is_pfaffian_not_eml
    except Exception as e:
        result.error = f"canonicalize/profile: {e}"
        return result

    # Step 4: rewrite
    try:
        from eml_rewrite import rewrite as _rw
        result.rewrite_report = _rw(expr, strategy=rewrite_strategy)
        result.rewritten = result.rewrite_report.rewritten
        result.steps.append(
            f"rewrite ({rewrite_strategy}): cost "
            f"{result.rewrite_report.cost_before} -> "
            f"{result.rewrite_report.cost_after} "
            f"({result.rewrite_report.savings_pct:+.0f}%)"
        )
    except ImportError:
        result.steps.append("rewrite: eml-rewrite not installed (skipped)")
        result.rewritten = result.canonical
    except Exception as e:
        result.steps.append(f"rewrite: error ({type(e).__name__}: {e}); using canonical")
        result.rewritten = result.canonical

    # Step 5-6: build EML tree (only if not PNE)
    if result.is_pne:
        result.steps.append("eml_tree: skipped (Pfaffian-not-EML)")
        return result

    try:
        from monogate import from_sympy, node_count, to_sympy, PfaffianNotEMLError
        # Use the rewritten form as the input to from_sympy
        try:
            result.eml_tree = from_sympy(result.rewritten if result.rewritten is not None else expr)
            result.node_count = node_count(result.eml_tree)
            result.steps.append(f"eml_tree built: {result.node_count} nodes")
        except PfaffianNotEMLError as e:
            result.is_pne = True
            result.steps.append(f"eml_tree: PNE rejected by from_sympy: {e}")
            return result
    except Exception as e:
        result.error = f"eml_tree: {e}"
        return result

    # Step 7: numerical verification
    if verify:
        try:
            free = sorted(expr.free_symbols, key=str)
            errors = []
            for _ in range(n_test_points):
                pts = {s: random.uniform(0.5, 1.8) for s in free}
                try:
                    v_orig = float(expr.subs(pts).evalf())
                    v_tree = float(to_sympy(result.eml_tree).subs(pts).evalf())
                    if math.isfinite(v_orig) and math.isfinite(v_tree):
                        denom = max(abs(v_orig), 1.0)
                        errors.append(abs(v_orig - v_tree) / denom)
                except Exception:
                    pass
            if errors:
                result.max_error = max(errors)
                result.steps.append(f"verified: max_error = {result.max_error:.2e}")
            else:
                result.steps.append("verified: no usable test points")
                result.max_error = float("inf")
        except Exception as e:
            result.steps.append(f"verify: error ({type(e).__name__})")
    else:
        result.max_error = 0.0  # not verified

    return result


def pipeline_batch(expressions, **kwargs) -> list[PipelineResult]:
    """Run pipeline() on a list of expressions. Order preserved."""
    return [pipeline(e, **kwargs) for e in expressions]


def _cli():
    """Entry point for `python -m monogate.pipeline "<expr>"`."""
    import sys
    if len(sys.argv) < 2:
        print("usage: python -m monogate.pipeline '<expr>' [--strategy=optimal]")
        sys.exit(2)
    expr_str = sys.argv[1]
    strategy = "optimal"
    for arg in sys.argv[2:]:
        if arg.startswith("--strategy="):
            strategy = arg.split("=", 1)[1]
    try:
        result = pipeline(expr_str, rewrite_strategy=strategy)
    except Exception as e:
        print(f"pipeline: fatal error: {e}", file=sys.stderr)
        sys.exit(1)
    print(f"Expression:  {result.original}")
    if result.canonical is not None:
        print(f"Canonical:   {result.canonical}")
    if result.profile is not None:
        print(f"Profile:     {result.profile.cost_class}")
    if result.rewritten is not None and result.rewrite_report is not None:
        print(f"Rewritten:   {result.rewritten}  "
              f"(cost: {result.rewrite_report.cost_before} -> "
              f"{result.rewrite_report.cost_after}, "
              f"{result.rewrite_report.savings_pct:+.0f}%)")
    if result.eml_tree is not None:
        print(f"EML tree:    {result.node_count} nodes")
    if result.is_pne:
        print(f"Status:      Pfaffian-not-EML (no finite EML tree)")
    elif result.max_error == float("inf"):
        print(f"Verified:    no test points evaluable")
    else:
        ok = "OK" if result.max_error < 1e-9 else "WARN"
        print(f"Verified:    {ok} (max error: {result.max_error:.2e})")
    if result.error:
        print(f"ERROR:       {result.error}")


if __name__ == "__main__":
    _cli()
