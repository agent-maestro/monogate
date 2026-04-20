"""
DOOR-2: Functional Distinctness Count for EML-family Trees

Counts functionally distinct outputs (as functions of x) when building binary
trees of increasing depth (= number of operator nodes) over the terminal set
{1, x}, for operators:
  EML(a, b) = exp(a) - ln(b)
  EXL(a, b) = exp(a) * ln(b)
  EAL(a, b) = exp(a) + ln(b)

Equivalence: numeric agreement at 20 test points in (0.1, 5).
Speed trick: lambdify each expression ONCE when first seen, cache the result.

Depth k = number of operator nodes.
Inputs at depth k come from cumulative pool of all depths 0..k-1.

Results saved to python/results/s103_door2_function_count.json
"""

import sys
import json
import itertools
import traceback
import warnings
from typing import Callable
from pathlib import Path

import sympy as sp
import numpy as np

sys.stdout.reconfigure(encoding="utf-8")
warnings.filterwarnings("ignore")

# ── Symbolic variable ──────────────────────────────────────────────────────
x = sp.Symbol("x", positive=True, real=True)

# ── Test points ────────────────────────────────────────────────────────────
TEST_POINTS = np.array([
    0.1, 0.25, 0.5, 0.75, 1.0, 1.3, 1.8, 2.4, 3.0, 4.0, 5.0,
    0.15, 0.4, 0.9, 1.1, 1.6, 2.1, 2.8, 3.7, 4.5,
], dtype=float)
N_PTS = len(TEST_POINTS)

# ── Operators ──────────────────────────────────────────────────────────────

def eml_sym(a: sp.Expr, b: sp.Expr) -> sp.Expr:
    return sp.exp(a) - sp.log(b)


def exl_sym(a: sp.Expr, b: sp.Expr) -> sp.Expr:
    return sp.exp(a) * sp.log(b)


def eal_sym(a: sp.Expr, b: sp.Expr) -> sp.Expr:
    return sp.exp(a) + sp.log(b)


OPERATORS: dict[str, Callable[[sp.Expr, sp.Expr], sp.Expr]] = {
    "EML": eml_sym,
    "EXL": exl_sym,
    "EAL": eal_sym,
}

TERMINALS: list[sp.Expr] = [sp.Integer(1), x]


# ── Numeric evaluation (compiled once per expression) ─────────────────────

def compile_and_eval(expr: sp.Expr) -> np.ndarray | None:
    """
    Compile expr via lambdify and evaluate at TEST_POINTS.
    Returns float64 array (NaN where invalid/imaginary/overflow), or None
    if fewer than 5 finite real values.
    """
    vals = np.full(N_PTS, np.nan)
    try:
        f = sp.lambdify(x, expr, modules="numpy")
        raw = f(TEST_POINTS)
        if np.isscalar(raw):
            raw = np.full(N_PTS, float(raw))
        raw = np.asarray(raw, dtype=complex)
        real_part = np.real(raw)
        imag_part = np.imag(raw)
        valid = (
            np.isfinite(real_part)
            & np.isfinite(imag_part)
            & (np.abs(imag_part) < 1e-8)
            & (np.abs(real_part) < 1e15)
        )
        vals = np.where(valid, real_part, np.nan)
    except Exception:
        pass
    if np.sum(~np.isnan(vals)) < 5:
        return None
    return vals


def sigs_match(a: np.ndarray | None, b: np.ndarray | None) -> bool:
    """True if both are non-None and agree at >= 5 shared valid points."""
    if a is None or b is None:
        return False
    valid = ~np.isnan(a) & ~np.isnan(b)
    if valid.sum() < 5:
        return False
    return bool(np.all(np.abs(a[valid] - b[valid]) < 1e-9))


# ── Pool with cached numeric signatures ───────────────────────────────────

class FunctionPool:
    """
    Maintains a collection of functionally distinct expressions.
    Each expression is evaluated exactly ONCE and its signature cached.
    Lookups are O(n) in pool size but avoid repeated lambdify calls.
    """

    def __init__(self) -> None:
        self._exprs: list[sp.Expr] = []
        self._sigs: list[np.ndarray | None] = []

    def __len__(self) -> int:
        return len(self._exprs)

    def add_terminal(self, expr: sp.Expr) -> None:
        """Add a terminal without duplication check (used at depth 0)."""
        sig = compile_and_eval(expr)
        self._exprs.append(expr)
        self._sigs.append(sig)

    def try_add(self, expr: sp.Expr, sig: np.ndarray | None) -> bool:
        """
        Try to add expr (with its pre-computed sig).
        Returns True if genuinely new.
        sig must be pre-computed by the caller (avoids re-compilation).
        """
        for known_sig in self._sigs:
            if sigs_match(sig, known_sig):
                return False
        # Rare case: both None sigs — use symbolic equality as fallback
        if sig is None:
            for known_expr, known_sig in zip(self._exprs, self._sigs):
                if known_sig is None:
                    try:
                        diff = sp.simplify(expr - known_expr)
                        if diff == sp.Integer(0):
                            return False
                    except Exception:
                        pass
        self._exprs.append(expr)
        self._sigs.append(sig)
        return True

    def snapshot(self) -> list[tuple[sp.Expr, np.ndarray | None]]:
        """Return a snapshot of (expr, sig) pairs for iteration."""
        return list(zip(self._exprs, self._sigs))


# ── Operator evaluation over vectors (the real speed-up) ──────────────────
# Rather than lambdify each new composite expression separately, we can
# directly compute op(a_vals, b_vals) using numpy on cached signatures.
# This avoids any SymPy/lambdify overhead for the inner loop.

def _combine_eml(a: np.ndarray | None, b: np.ndarray | None) -> np.ndarray | None:
    """exp(a) - ln(b) applied element-wise to signature arrays."""
    if a is None or b is None:
        return None
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        try:
            vals = np.exp(a) - np.log(b)
            valid = np.isfinite(vals) & (np.abs(vals) < 1e15)
            result = np.where(valid, vals, np.nan)
            if np.sum(~np.isnan(result)) < 5:
                return None
            return result
        except Exception:
            return None


def _combine_exl(a: np.ndarray | None, b: np.ndarray | None) -> np.ndarray | None:
    """exp(a) * ln(b) applied element-wise."""
    if a is None or b is None:
        return None
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        try:
            vals = np.exp(a) * np.log(b)
            valid = np.isfinite(vals) & (np.abs(vals) < 1e15)
            result = np.where(valid, vals, np.nan)
            if np.sum(~np.isnan(result)) < 5:
                return None
            return result
        except Exception:
            return None


def _combine_eal(a: np.ndarray | None, b: np.ndarray | None) -> np.ndarray | None:
    """exp(a) + ln(b) applied element-wise."""
    if a is None or b is None:
        return None
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        try:
            vals = np.exp(a) + np.log(b)
            valid = np.isfinite(vals) & (np.abs(vals) < 1e15)
            result = np.where(valid, vals, np.nan)
            if np.sum(~np.isnan(result)) < 5:
                return None
            return result
        except Exception:
            return None


NUMERIC_COMBINE: dict[str, Callable] = {
    "EML": _combine_eml,
    "EXL": _combine_exl,
    "EAL": _combine_eal,
}


# ── Depth-by-depth enumeration ─────────────────────────────────────────────

def run_depth_analysis(
    op_name: str,
    op_sym: Callable[[sp.Expr, sp.Expr], sp.Expr],
    max_depth: int = 3,
) -> dict:
    op_num = NUMERIC_COMBINE[op_name]

    print(f"\n{'='*60}")
    print(f"Operator: {op_name}")
    print(f"{'='*60}")

    depth_results: dict[int, dict] = {}
    pool = FunctionPool()

    # Depth 0
    for t in TERMINALS:
        pool.add_terminal(t)

    count_d0 = len(pool)
    depth_results[0] = {
        "count": count_d0,
        "expressions": [str(e) for e, _ in pool.snapshot()],
    }
    print(f"Depth 0: {count_d0} distinct — {depth_results[0]['expressions']}")

    for depth in range(1, max_depth + 1):
        snap = pool.snapshot()
        pool_size = len(pool)
        print(f"\nDepth {depth}: generating from pool of {pool_size} ...", flush=True)

        new_this_depth = 0
        raw_count = 0
        sample_new: list[str] = []

        for (a_expr, a_sig), (b_expr, b_sig) in itertools.product(snap, repeat=2):
            raw_count += 1
            # Compute numeric signature purely from parent signatures — no lambdify
            new_sig = op_num(a_sig, b_sig)

            # Build symbolic expression (cheap — just tree construction, no eval)
            try:
                new_expr = op_sym(a_expr, b_expr)
            except Exception:
                continue

            if pool.try_add(new_expr, new_sig):
                new_this_depth += 1
                if len(sample_new) < 12:
                    sample_new.append(str(new_expr))

        total = len(pool)
        print(f"  Raw pairs: {raw_count}")
        print(f"  New distinct at depth {depth}: {new_this_depth}")
        print(f"  Cumulative (0..{depth}): {total}", flush=True)

        depth_results[depth] = {
            "new_distinct_count": new_this_depth,
            "cumulative_count": total,
            "sample_new_expressions": sample_new,
        }

        if new_this_depth == 0:
            print(f"  [SATURATED] No new functions at depth {depth}.")
            break

    return {
        "operator": op_name,
        "depth_results": {str(k): v for k, v in depth_results.items()},
        "final_cumulative": len(pool),
    }


# ── Growth analysis ────────────────────────────────────────────────────────

def estimate_growth(new_counts: list[int]) -> dict:
    catalan = [1, 1, 2, 5, 14, 42, 132, 429]
    n = len(new_counts)
    ratios: list[float] = []
    for i in range(1, n):
        prev = new_counts[i - 1]
        if prev > 0:
            ratios.append(round(new_counts[i] / prev, 3))

    if len(ratios) >= 2:
        spread = max(ratios) - min(ratios)
        avg_ratio = round(sum(ratios) / len(ratios), 3)
        increasing = all(ratios[i] >= ratios[i - 1] for i in range(1, len(ratios)))
        if spread < 1.0:
            growth_type = "approximately exponential"
        elif increasing:
            growth_type = "super-exponential (accelerating)"
        else:
            growth_type = "irregular"
    elif len(ratios) == 1:
        avg_ratio = ratios[0]
        growth_type = "single step only"
    else:
        avg_ratio = 0.0
        growth_type = "insufficient_data"

    catalan_match = (
        n <= len(catalan)
        and all(abs(new_counts[i] - catalan[i]) <= 1 for i in range(min(n, len(catalan))))
    )
    return {
        "growth_type": growth_type,
        "depth_to_depth_ratios": ratios,
        "avg_ratio": avg_ratio,
        "catalan_match": catalan_match,
    }


# ── Main ───────────────────────────────────────────────────────────────────

def main() -> None:
    print("DOOR-2: Functional Distinctness Count for EML-family Trees")
    print("Terminals: {1, x} | Depth = number of operator nodes")
    print("Equivalence: numeric signatures at 20 points in (0.1, 5)")
    print()

    all_results: dict = {}
    growth_summary: dict = {}

    for op_name, op_sym in OPERATORS.items():
        try:
            result = run_depth_analysis(op_name, op_sym, max_depth=3)
            all_results[op_name] = result

            dr = result["depth_results"]
            new_counts = [dr["0"]["count"]]
            cumul_counts = [dr["0"]["count"]]
            for d in range(1, 4):
                key = str(d)
                if key in dr:
                    new_counts.append(dr[key]["new_distinct_count"])
                    cumul_counts.append(dr[key]["cumulative_count"])

            growth_summary[op_name] = {
                "new_at_each_depth": new_counts,
                "cumulative_at_each_depth": cumul_counts,
                "growth_analysis": estimate_growth(new_counts),
            }
        except Exception as e:
            print(f"ERROR: {op_name}: {e}")
            traceback.print_exc()
            all_results[op_name] = {"error": str(e)}

    # Print summary
    print("\n" + "=" * 60)
    print("COMPARISON SUMMARY")
    print("=" * 60)
    for op_name, gs in growth_summary.items():
        ga = gs["growth_analysis"]
        print(f"\n{op_name}:")
        print(f"  New per depth:        {gs['new_at_each_depth']}")
        print(f"  Cumulative:           {gs['cumulative_at_each_depth']}")
        print(f"  Growth type:          {ga.get('growth_type')}")
        print(f"  Depth-to-depth ratio: {ga.get('depth_to_depth_ratios')}")
        print(f"  Catalan match:        {ga.get('catalan_match')}")

    # Detect combinatorial equivalences
    combinatorial_equivalences: list[str] = []
    op_names = list(growth_summary.keys())
    for i in range(len(op_names)):
        for j in range(i + 1, len(op_names)):
            a, b = op_names[i], op_names[j]
            gs_a = growth_summary.get(a, {})
            gs_b = growth_summary.get(b, {})
            if "new_at_each_depth" not in gs_a or "new_at_each_depth" not in gs_b:
                continue
            if gs_a["new_at_each_depth"] == gs_b["new_at_each_depth"]:
                note = f"{a} and {b} identical new-per-depth: {gs_a['new_at_each_depth']}"
                combinatorial_equivalences.append(note)
                print(f"\nCOMBINATORIAL EQUIV: {note}")
            elif gs_a["cumulative_at_each_depth"] == gs_b["cumulative_at_each_depth"]:
                note = f"{a} and {b} identical cumulative: {gs_a['cumulative_at_each_depth']}"
                combinatorial_equivalences.append(note)
                print(f"\nCOMBINATORIAL EQUIV (cumulative): {note}")

    output = {
        "study": "DOOR-2: Functional Distinctness Count for EML-family Trees",
        "terminals": ["1", "x"],
        "depth_definition": "number of operator nodes (not tree height)",
        "equivalence_method": (
            "numeric agreement at 20 points in (0.1, 5.0); "
            "symbolic fallback only for both-None-signature pairs"
        ),
        "operators": all_results,
        "growth_summary": growth_summary,
        "combinatorial_equivalences": combinatorial_equivalences,
    }

    out_path = Path("D:/monogate/python/results/s103_door2_function_count.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"\nResults saved to {out_path}")


if __name__ == "__main__":
    main()
