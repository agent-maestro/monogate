"""
SuperBEST Router — Dynamic Per-Operation Operator Selection
Finds the minimum-node operator for each arithmetic primitive in an expression tree.

Author: Arturo R. Almaguer
Session: FAM-C2 / SuperBEST v5 (ADD-CASCADE 2026-04-20)

v5 changes vs v4:
  - add_gen: 11n → 2n for ALL real x, y (LEdiv(x, DEML(y,1)) = x+y)
  - add_pos: 3n → 2n (same construction, no domain restriction needed)
  - add unified entry: single add=2n covers all reals; positive-domain split eliminated
  - sqrt: now a first-class entry at 2n (EML(0.5*EXL(0,x), 1) = sqrt(x))
  - Total: 19n → 18n; savings: ~74% → 75.3% vs naive 73n baseline
  - Reference: SuperBEST_v5_Structural_Audit.tex, ADD_T1_General_Addition_2n.tex
"""
from __future__ import annotations
import math
import re
from typing import Any


# ---------------------------------------------------------------------------
# Operator node costs (EXL-extended, 0 and 1 as free constants)
# ---------------------------------------------------------------------------
SUPERBEST_TABLE: dict[str, dict] = {
    "exp":   {"operator": "EML",                  "nodes": 1, "domain": "all x",
              "construction": "eml(x, 1)"},
    "ln":    {"operator": "EXL",                  "nodes": 1, "domain": "x > 0",
              "construction": "exl(0, x)"},
    "mul":   {"operator": "Mixed(EXL/ELAd)",        "nodes": 2, "domain": "x > 0",
              "construction": "elad(exl(0,x), y)"},
    "div":   {"operator": "Mixed(EXL/ELSb)",       "nodes": 2, "domain": "x, y > 0",
              "construction": "elsb(exl(0,x), y)"},
    "add":   {"operator": "Mixed(DEML/LEdiv)",     "nodes": 2, "domain": "all x, y",
              "construction": "lediv(x, deml(y,1))",
              "note": "2 nodes for ALL reals: LEdiv(x,DEML(y,1))=x-ln(exp(-y))=x+y (ADD-T1)"},
    "sub":   {"operator": "Mixed(EML/LEdiv)",      "nodes": 2, "domain": "all x, y",
              "construction": "lediv(x, eml(y,1))"},
    "sqrt":  {"operator": "Mixed(EXL/EML)",        "nodes": 2, "domain": "x > 0",
              "construction": "eml(0.5*exl(0,x), 1)",
              "note": "2 nodes: EML(0.5*EXL(0,x),1) = exp(0.5*ln(x)) = sqrt(x)"},
    "neg":   {"operator": "Mixed(EXL/DEML)",       "nodes": 2, "domain": "all x",
              "construction": "exl(0, deml(x,1))",
              "construction_pos": "emn(exl(0,x), 1)", "nodes_pos": 2,
              "note": "2 nodes for all x (EXL+DEML); 2 nodes pos-domain (EMN+EXL)"},
    "recip": {"operator": "ELSb",                  "nodes": 1, "domain": "x != 0",
              "construction": "elsb(0, x)"},
    "pow":   {"operator": "EXL",                   "nodes": 3, "domain": "x > 0",
              "construction": "eml(exl(ln(n),x), 1)"},
    "sin":   {"operator": "EML (complex)",         "nodes": 1, "domain": "all x",
              "construction": "Im(eml(ix, 1))"},
    "cos":   {"operator": "EML (complex)",         "nodes": 1, "domain": "all x",
              "construction": "Re(eml(ix, 1))"},
}

NAIVE_COSTS: dict[str, int] = {
    "exp": 1, "ln": 3, "mul": 13, "div": 15, "add": 11,
    "sub": 5, "neg": 9, "recip": 5, "sqrt": 8, "pow": 15, "sin": 13, "cos": 13,
}

# SuperBEST v5: unified single-tier costs (no positive-domain split)
# All entries proved optimal in SuperBEST_v5_Structural_Audit.tex
SUPERBEST_COSTS_V5: dict[str, int] = {
    "exp": 1, "ln": 1, "recip": 1,
    "div": 2, "neg": 2, "mul": 2, "sub": 2, "add": 2, "sqrt": 2,
    "pow": 3,
    "sin": 1, "cos": 1,  # via complex EML
}

# Kept for backward compatibility — both tiers are now unified at v5 costs
SUPERBEST_COSTS_GEN: dict[str, int] = SUPERBEST_COSTS_V5
SUPERBEST_COSTS_POS: dict[str, int] = SUPERBEST_COSTS_V5


def superbest_cost(op: str) -> int:
    """Return the SuperBEST node cost for the given operation."""
    if op in SUPERBEST_TABLE:
        return SUPERBEST_TABLE[op]["nodes"]
    return NAIVE_COSTS.get(op, 99)


def superbest_operator(op: str) -> str:
    """Return the optimal operator name for the given operation."""
    if op in SUPERBEST_TABLE:
        return SUPERBEST_TABLE[op]["operator"]
    return "unknown"


def superbest_construction(op: str) -> str:
    """Return the minimal-node construction for the given operation."""
    if op in SUPERBEST_TABLE:
        return SUPERBEST_TABLE[op]["construction"]
    return "unknown"


def savings_vs_naive(op: str) -> int:
    """Return node savings vs naive single-operator evaluation."""
    return NAIVE_COSTS.get(op, 0) - superbest_cost(op)


def route_expression(ops: list[str]) -> dict:
    """
    Given a list of arithmetic operations in an expression,
    return the SuperBEST routing and total node count.

    Args:
        ops: List of operation names, e.g., ["mul", "add", "exp"]

    Returns:
        Dictionary with per-op routing and totals.
    """
    result = {}
    total_superbest = 0
    total_naive = 0
    for op in ops:
        sb = superbest_cost(op)
        naive = NAIVE_COSTS.get(op, 99)
        total_superbest += sb
        total_naive += naive
        result[op] = {
            "operator": superbest_operator(op),
            "nodes": sb,
            "naive_nodes": naive,
            "savings": naive - sb,
            "construction": superbest_construction(op),
        }
    result["__totals__"] = {
        "superbest_nodes": total_superbest,
        "naive_nodes": total_naive,
        "total_savings": total_naive - total_superbest,
        "savings_pct": round((1 - total_superbest / max(total_naive, 1)) * 100, 1),
    }
    return result


def rewrite_python_expr(expr: str) -> str:
    """
    Naive regex-based rewriter: annotates Python expressions with SuperBEST operators.
    Not a full compiler — purely for demonstration of routing decisions.

    Args:
        expr: Python expression string, e.g., "x * y + math.exp(z)"

    Returns:
        Annotated string showing SuperBEST operator choices.
    """
    annotations = []
    if re.search(r"\*(?!\*)", expr):
        annotations.append(f"mul → {superbest_construction('mul')} (2n)")
    if "+" in expr:
        annotations.append(f"add → {superbest_construction('add')} (2n, all reals)")
    if "-" in expr and "exp" not in expr:
        annotations.append(f"sub → {superbest_construction('sub')} (2n)")
    if "exp(" in expr or "math.exp" in expr:
        annotations.append(f"exp → {superbest_construction('exp')} (1n)")
    if "log(" in expr or "math.log" in expr:
        annotations.append(f"ln → {superbest_construction('ln')} (1n)")
    if "/" in expr:
        annotations.append(f"div → {superbest_construction('div')} (2n)")
    return expr + "  # SuperBEST: " + "; ".join(annotations)


def superbest_summary() -> str:
    """Return a human-readable summary of the SuperBEST v5 routing table."""
    lines = [
        "SuperBEST v5 Routing Table — Unified (no positive-domain split)",
        "All 10 entries structurally proved optimal (SuperBEST_v5_Structural_Audit.tex)",
        "=" * 72,
    ]
    lines.append(f"  {'Op':8} {'Nodes':6} {'Naive':6} {'Savings':8} {'Construction':40}")
    lines.append("-" * 72)
    total_sb = total_naive = 0
    ops_v5 = ["exp", "ln", "recip", "div", "neg", "mul", "sub", "add", "sqrt", "pow"]
    for op in ops_v5:
        sb = SUPERBEST_COSTS_V5.get(op, 99)
        naive = NAIVE_COSTS.get(op, 0)
        total_sb += sb
        total_naive += naive
        constr = superbest_construction(op)
        savings_n = naive - sb
        lines.append(f"  {op:8} {sb:6} {naive:6} {savings_n:+8d} {constr:40}")
    lines.append("-" * 72)
    pct = (1 - total_sb / max(total_naive, 1)) * 100
    lines.append(f"  {'TOTAL':8} {total_sb:6} {total_naive:6} {total_naive-total_sb:+8d}")
    lines.append(f"  Savings: {pct:.1f}% vs naive {total_naive}n baseline")
    lines.append("  Key v5 result: add=2n for ALL reals via LEdiv(x,DEML(y,1))=x+y (ADD-T1)")
    return "\n".join(lines)
