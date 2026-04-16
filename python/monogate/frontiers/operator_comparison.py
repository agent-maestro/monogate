"""
monogate.frontiers.operator_comparison
=======================================
Frontier 7 — Does any EML-family operator break the negative-exponent barrier?

Compares EML, EDL, EXL, EAL, EMN across:
1. Node counts for physics functions (extension of operators.py table)
2. Barrier analysis: can any operator express exp(-x) at depth ≤ 2?
3. MCTS functional census: best MSE at depth 2/4/6 for each operator on
   the 15 physics laws from law_complexity.py

Key finding (expected):
  All operators share the same barrier. Since every operator uses exp(left)
  as one component, building exp(-x) requires -x as an intermediate value.
  With leaves {x, constants ≥ 0} and no subtraction gate, -x is unreachable.

Usage::

    cd python
    python -m monogate.frontiers.operator_comparison --n-simulations 1500
"""

from __future__ import annotations

import math
import time
from typing import Any, Callable

import numpy as np


# ── Operator metadata ─────────────────────────────────────────────────────────

# (name, gate_formula, constant_terminal, can_express_expx_natively)
OPERATOR_META: dict[str, dict] = {
    "EML":  {"gate": "exp(a) − ln(b)",  "constant": 1.0,        "complete": True},
    "EDL":  {"gate": "exp(a) / ln(b)",  "constant": math.e,     "complete": True},
    "EMN":  {"gate": "ln(b) − exp(a)",  "constant": 1.0,        "complete": False},
    "EXL":  {"gate": "exp(a) × ln(b)",  "constant": math.e,     "complete": False},
    "EAL":  {"gate": "exp(a) + ln(b)",  "constant": 1.0,        "complete": False},
    "DEML": {"gate": "exp(−a) − ln(b)", "constant": 1.0,        "complete": False},
}


# ── Operator-specific tree eval functions ─────────────────────────────────────

def _eval_eml(node: dict, x: float) -> float:
    op = node["op"]
    if op == "leaf":
        val = node["val"]
        return x if val == "x" else float(val)
    a = _eval_eml(node["left"],  x)
    b = _eval_eml(node["right"], x)
    if b <= 0.0:
        raise ValueError(f"EML ln domain: b={b}")
    return math.exp(a) - math.log(b)


def _eval_edl(node: dict, x: float) -> float:
    op = node["op"]
    if op == "leaf":
        val = node["val"]
        return x if val == "x" else float(val)
    a = _eval_edl(node["left"],  x)
    b = _eval_edl(node["right"], x)
    if b <= 0.0:
        raise ValueError(f"EDL ln domain: b={b}")
    denom = math.log(b)
    if denom == 0.0:
        raise ValueError(f"EDL division by zero: ln({b})=0")
    return math.exp(a) / denom


def _eval_emn(node: dict, x: float) -> float:
    op = node["op"]
    if op == "leaf":
        val = node["val"]
        return x if val == "x" else float(val)
    a = _eval_emn(node["left"],  x)
    b = _eval_emn(node["right"], x)
    if b <= 0.0:
        raise ValueError(f"EMN ln domain: b={b}")
    return math.log(b) - math.exp(a)


def _eval_exl(node: dict, x: float) -> float:
    op = node["op"]
    if op == "leaf":
        val = node["val"]
        return x if val == "x" else float(val)
    a = _eval_exl(node["left"],  x)
    b = _eval_exl(node["right"], x)
    if b <= 0.0:
        raise ValueError(f"EXL ln domain: b={b}")
    return math.exp(a) * math.log(b)


def _eval_eal(node: dict, x: float) -> float:
    op = node["op"]
    if op == "leaf":
        val = node["val"]
        return x if val == "x" else float(val)
    a = _eval_eal(node["left"],  x)
    b = _eval_eal(node["right"], x)
    if b <= 0.0:
        raise ValueError(f"EAL ln domain: b={b}")
    return math.exp(a) + math.log(b)


def _eval_deml(node: dict, x: float) -> float:
    op = node["op"]
    if op == "leaf":
        val = node["val"]
        return x if val == "x" else float(val)
    a = _eval_deml(node["left"],  x)
    b = _eval_deml(node["right"], x)
    if b <= 0.0:
        raise ValueError(f"DEML ln domain: b={b}")
    return math.exp(-a) - math.log(b)


_EVAL_FNS: dict[str, Callable[[dict, float], float]] = {
    "EML":  _eval_eml,
    "EDL":  _eval_edl,
    "EMN":  _eval_emn,
    "EXL":  _eval_exl,
    "EAL":  _eval_eal,
    "DEML": _eval_deml,
}


def make_operator_eval(op_name: str) -> Callable[[dict, float], float]:
    """Return an operator-specific tree eval function for use with mcts_search.

    Pass the result as `eval_tree_fn` in `mcts_search` to run MCTS with a
    non-EML operator.

    Example::

        from monogate.search.mcts import mcts_search
        from monogate.frontiers.operator_comparison import make_operator_eval

        edl_eval = make_operator_eval('EDL')
        result = mcts_search(math.exp, depth=2, n_simulations=1000,
                             eval_tree_fn=edl_eval)
    """
    if op_name not in _EVAL_FNS:
        raise KeyError(f"Unknown operator {op_name!r}. Available: {sorted(_EVAL_FNS)}")
    return _EVAL_FNS[op_name]


# ── Extended physics node-count table ────────────────────────────────────────
#
# Counts derived from core.py constructors.  None = not expressible in finite
# tree over {x, constants} for that operator.  "blocked" = barrier applies.
#
# Sources:
#   EML: exp_eml (1), ln_eml (3), recip_eml (5), neg_eml (9),
#        mul_eml (13), pow_eml (15), sub_eml (5)
#   EDL: exp_edl=1, ln_edl=3, recip_edl=2, neg_edl=6, mul_edl=7,
#        div_edl=1, pow_edl=11
#   EXL: exp_exl=1, ln_exl=1, pow_exl=3   (EXL is NOT complete)
#   EAL: exp_eal=1                          (EAL is NOT complete)
#   EMN: emn(x,1)=-exp(x); cannot express exp(x) natively

PHYSICS_NODE_COUNTS: dict[str, dict[str, int | None]] = {
    # function        EML    EDL    EXL    EAL    EMN   DEML
    "exp(x)":       {"EML":  1, "EDL":  1, "EXL":  1, "EAL":  1, "EMN": None, "DEML": None},
    "exp(-x)":      {"EML": None, "EDL": None, "EXL": None, "EAL": None, "EMN": None, "DEML": 1},
    "ln(x)":        {"EML":  3, "EDL":  3, "EXL":  1, "EAL": None, "EMN": None, "DEML":  3},
    "1/x":          {"EML":  5, "EDL":  2, "EXL": None, "EAL": None, "EMN": None, "DEML": None},
    "x^1.5":        {"EML": 15, "EDL": 11, "EXL":  3, "EAL": None, "EMN": None, "DEML": None},
    "x^4":          {"EML": 15, "EDL": 11, "EXL":  3, "EAL": None, "EMN": None, "DEML": None},
    "x^2":          {"EML": 15, "EDL": 11, "EXL":  3, "EAL": None, "EMN": None, "DEML": None},
    "1/(exp(x)-1)": {"EML": 20, "EDL": 16, "EXL": None, "EAL": None, "EMN": None, "DEML": None},
    "1/(exp(x)+1)": {"EML": 20, "EDL": 16, "EXL": None, "EAL": None, "EMN": None, "DEML": None},
    "exp(-x^2)":    {"EML": None, "EDL": None, "EXL": None, "EAL": None, "EMN": None, "DEML": None},
    "x*exp(-x)":    {"EML": None, "EDL": None, "EXL": None, "EAL": None, "EMN": None, "DEML": None},
}


def node_count_table() -> str:
    """Return a GitHub-Flavored Markdown table of physics function node counts."""
    operators = ["EML", "EDL", "EXL", "EAL", "EMN", "DEML"]
    header = "| Function | " + " | ".join(operators) + " |"
    sep    = "|----------|" + "|".join([":-----:"] * len(operators)) + "|"
    rows   = [header, sep]
    for fname, counts in PHYSICS_NODE_COUNTS.items():
        cells = [str(counts.get(op, "—")) if counts.get(op) is not None else "blocked"
                 for op in operators]
        rows.append(f"| `{fname}` | " + " | ".join(cells) + " |")
    return "\n".join(rows)


# ── Barrier analysis ──────────────────────────────────────────────────────────

def barrier_analysis(
    n_simulations: int = 1000,
    operators:     list[str] | None = None,
) -> dict[str, dict]:
    """Empirically confirm the negative-exponent barrier for each operator.

    Runs MCTS at depth=2 on exp(-x) for each operator and reports the best
    achievable MSE.  All operators are expected to achieve high MSE (blocked).

    Returns:
        dict mapping operator name → {"best_mse": float, "best_formula": str,
                                       "blocked": bool}
    """
    from monogate.search.mcts import mcts_search

    ops = operators or list(_EVAL_FNS)
    domain = (0.1, 3.0)
    n_probe = 60
    lo, hi = domain
    probe = [lo + (hi - lo) * i / (n_probe - 1) for i in range(n_probe)]
    target = lambda x: math.exp(-x)

    results = {}
    for op_name in ops:
        eval_fn = _EVAL_FNS[op_name]
        try:
            r = mcts_search(
                target_fn=target,
                probe_points=probe,
                depth=2,
                n_simulations=n_simulations,
                seed=42,
                eval_tree_fn=eval_fn,
            )
            blocked = r.best_mse > 0.05
            results[op_name] = {
                "best_mse":     r.best_mse,
                "best_formula": r.best_formula,
                "blocked":      blocked,
            }
        except Exception as exc:
            results[op_name] = {
                "best_mse":     float("inf"),
                "best_formula": "",
                "blocked":      True,
                "error":        str(exc),
            }
    return results


# ── Per-operator functional census ────────────────────────────────────────────

def census_one_operator(
    op_name:       str,
    laws:          list[dict],
    n_simulations: int  = 1500,
    depths:        tuple[int, ...] = (2, 4, 6),
    verbose:       bool = False,
) -> list[dict]:
    """Run the functional census for *one* operator on a list of law dicts.

    Each law dict must have keys ``'fn'`` and ``'domain'``.

    Returns a list of result dicts with ``depth_<d>`` MSE entries.
    """
    from monogate.search.mcts import mcts_search

    eval_fn = _EVAL_FNS[op_name]
    rows = []

    for law in laws:
        fn    = law["fn"]
        lo, hi = law["domain"]
        n_probe = 60
        probe = [lo + (hi - lo) * i / (n_probe - 1) for i in range(n_probe)]

        # Guard: filter non-finite targets
        valid = [(x, fn(x)) for x in probe
                 if _safe_eval(fn, x)]
        if len(valid) < 10:
            rows.append({"name": law.get("name", "?"), "error": "insufficient probes"})
            continue

        valid_x, valid_y = zip(*valid)
        valid_x = list(valid_x)

        result: dict[str, Any] = {
            "name":     law.get("name", "?"),
            "category": law.get("category", "?"),
            "operator": op_name,
        }

        for depth in depths:
            try:
                r = mcts_search(
                    target_fn=fn,
                    probe_points=valid_x,
                    depth=depth,
                    n_simulations=n_simulations,
                    seed=42,
                    eval_tree_fn=eval_fn,
                )
                result[f"depth_{depth}"] = {
                    "mse":     r.best_mse,
                    "formula": r.best_formula,
                }
            except Exception as exc:
                result[f"depth_{depth}"] = {
                    "mse":     float("inf"),
                    "formula": "",
                    "error":   str(exc),
                }

        min_depth = min(depths)
        mse_min = result.get(f"depth_{min_depth}", {}).get("mse", float("inf"))
        result["eml_native"] = mse_min < 1e-6
        eff = None
        for d in depths:
            if result.get(f"depth_{d}", {}).get("mse", float("inf")) < 0.05:
                eff = d
                break
        result["min_effective_depth"] = eff
        rows.append(result)

        if verbose:
            d2 = result.get("depth_2", {}).get("mse", 999)
            print(f"  [{op_name}] {law.get('name', '?'):35s} d2={d2:.3f}")

    return rows


def _safe_eval(fn: Callable, x: float) -> bool:
    try:
        y = fn(x)
        return math.isfinite(y)
    except Exception:
        return False


def compare_all_operators(
    n_simulations: int       = 1500,
    operators:     list[str] | None = None,
    verbose:       bool      = True,
) -> dict:
    """Run census for multiple operators on FUNCTIONAL_LAWS.

    Returns nested dict: ``{op_name: [per-law result dicts]}``.
    """
    from monogate.frontiers.law_complexity import FUNCTIONAL_LAWS

    ops = operators or list(_EVAL_FNS)
    results = {}

    for op_name in ops:
        if verbose:
            print(f"\n[{op_name}] ({OPERATOR_META[op_name]['gate']})")
            print("-" * 50)
        rows = census_one_operator(
            op_name, FUNCTIONAL_LAWS,
            n_simulations=n_simulations,
            verbose=verbose,
        )
        results[op_name] = rows

        if verbose:
            native = sum(1 for r in rows if r.get("eml_native"))
            mean_d2 = _mean_mse(rows, "depth_2")
            print(f"  native={native}/{len(rows)}  mean_d2={mean_d2:.3f}")

    return results


def _mean_mse(rows: list[dict], depth_key: str) -> float:
    vals = [r[depth_key]["mse"] for r in rows
            if depth_key in r and math.isfinite(r[depth_key]["mse"])]
    return float(np.mean(vals)) if vals else float("inf")


# ── Full pipeline ─────────────────────────────────────────────────────────────

def run_full_comparison(
    n_simulations: int  = 1500,
    operators:     list[str] | None = None,
    verbose:       bool = True,
) -> dict:
    """Run the complete operator comparison and save results to JSON.

    Pipeline:
    1. Barrier analysis (exp(-x) at depth=2 for each operator)
    2. Node-count table (analytical, from PHYSICS_NODE_COUNTS)
    3. Functional census (MCTS on 15 physics laws per operator)
    """
    import json
    from pathlib import Path

    timestamp = time.strftime("%Y%m%d_%H%M%S")
    out_dir   = Path("results/operator_comparison")
    out_dir.mkdir(parents=True, exist_ok=True)

    ops = operators or list(_EVAL_FNS)

    print("\n" + "=" * 60)
    print("  OPERATOR COMPARISON — NEGATIVE-EXPONENT BARRIER")
    print("=" * 60)

    # 1 — Barrier analysis
    print("\n[1/3] Barrier analysis (exp(-x) at depth=2)")
    print("-" * 50)
    barrier = barrier_analysis(n_simulations=min(n_simulations, 800), operators=ops)
    for op_name, res in barrier.items():
        blocked = "BLOCKED" if res["blocked"] else "not blocked"
        print(f"  {op_name}: mse={res['best_mse']:.4f}  [{blocked}]")

    # 2 — Node-count table
    print("\n[2/3] Node-count table (analytical)")
    print("-" * 50)
    table = node_count_table()
    print(table)

    # 3 — Census (optional, takes time)
    print(f"\n[3/3] Functional census (n_simulations={n_simulations})")
    print("-" * 50)
    census = compare_all_operators(
        n_simulations=n_simulations,
        operators=ops,
        verbose=verbose,
    )

    # Print summary table
    print("\n" + "=" * 60)
    print("  SUMMARY: mean MSE at depth=2 per operator")
    print("=" * 60)
    print(f"  {'Operator':8s}  {'Gate':22s}  {'mean d2 MSE':>12s}  {'Native':>8s}")
    print("  " + "-" * 54)
    for op_name in ops:
        rows  = census.get(op_name, [])
        mean2 = _mean_mse(rows, "depth_2")
        nat   = sum(1 for r in rows if r.get("eml_native"))
        gate  = OPERATOR_META[op_name]["gate"]
        print(f"  {op_name:8s}  {gate:22s}  {mean2:>12.3f}  {nat:>6d}/{len(rows)}")

    # Save
    out_path = out_dir / f"comparison_{timestamp}.json"
    session = {
        "timestamp":   timestamp,
        "operators":   ops,
        "barrier":     barrier,
        "node_counts": PHYSICS_NODE_COUNTS,
        "census":      census,
    }
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(session, f, indent=2, default=str)
    print(f"\nResults: {out_path}")

    return session


# ── CLI ───────────────────────────────────────────────────────────────────────

def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        description="Operator Comparison — Negative-Exponent Barrier Analysis"
    )
    parser.add_argument("--n-simulations", type=int, default=1500)
    parser.add_argument("--operators", type=str, default="EML,EDL,EXL",
                        help="Comma-separated operator names (default: EML,EDL,EXL)")
    parser.add_argument("--barrier-only", action="store_true",
                        help="Only run barrier analysis (fastest)")
    parser.add_argument("--output", type=str, default=None)
    args = parser.parse_args()

    ops = [o.strip().upper() for o in args.operators.split(",")]

    if args.barrier_only:
        print("\n[Barrier analysis only]\n" + "-" * 40)
        barrier = barrier_analysis(n_simulations=args.n_simulations, operators=ops)
        for op_name, res in barrier.items():
            blocked = "BLOCKED" if res["blocked"] else "NOT BLOCKED"
            print(f"  {op_name}: mse={res['best_mse']:.4f}  [{blocked}]")
    else:
        session = run_full_comparison(
            n_simulations=args.n_simulations,
            operators=ops,
        )
        if args.output:
            import json
            with open(args.output, "w", encoding="utf-8") as f:
                json.dump(session, f, indent=2, default=str)
            print(f"Output saved to {args.output}")


if __name__ == "__main__":
    main()
