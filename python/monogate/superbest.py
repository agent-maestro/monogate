"""
SuperBEST Router — Dynamic Per-Operation Operator Selection
Finds the minimum-node operator for each arithmetic primitive in an expression tree.

Author: Arturo R. Almaguer
Session: FAM-C2
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
    "mul":   {"operator": "Mixed(EXL/EML)",        "nodes": 3, "domain": "x > 0",
              "construction": "exl(exl(0,x), eml(y,1))"},
    "div":   {"operator": "Mixed(EXL/EML/EDL)",    "nodes": 3, "domain": "x > 0, y != 0",
              "construction": "edl(exl(0,x), eml(y,1))"},
    "add":   {"operator": "Mixed(EXL/EML/EAL)",    "nodes": 3, "domain": "x > 0",
              "construction": "eal(exl(0,x), eml(y,1))"},
    "sub":   {"operator": "Mixed(EXL/EML)",        "nodes": 3, "domain": "x > 0",
              "construction": "eml(exl(0,x), eml(y,1))"},
    "neg":   {"operator": "Mixed(EXL/DEML)",       "nodes": 2, "domain": "all x",
              "construction": "exl(0, deml(x,1))",
              "construction_pos": "emn(exl(0,x), 1)", "nodes_pos": 2,
              "note": "2 nodes for all x (EXL+DEML); 2 nodes pos-domain (EMN+EXL)"},
    "recip": {"operator": "Mixed(EDL/EML)",        "nodes": 2, "domain": "x != 0",
              "construction": "edl(0, eml(x,1))"},
    "pow":   {"operator": "EXL",                   "nodes": 3, "domain": "x > 0",
              "construction": "eml(exl(ln(n),x), 1)"},
    "sin":   {"operator": "EML (complex)",         "nodes": 1, "domain": "all x",
              "construction": "Im(eml(ix, 1))"},
    "cos":   {"operator": "EML (complex)",         "nodes": 1, "domain": "all x",
              "construction": "Re(eml(ix, 1))"},
}

NAIVE_COSTS: dict[str, int] = {
    "exp": 1, "ln": 3, "mul": 7, "div": 7, "add": 11,
    "sub": 16, "neg": 11, "recip": 6, "pow": 11, "sin": 13, "cos": 13,
}

# Two-tier costs: general domain vs positive domain (x > 0)
SUPERBEST_COSTS_GEN: dict[str, int] = {
    "exp": 1, "ln": 1, "mul": 3, "div": 3, "add": 3,
    "sub": 3, "neg": 2, "recip": 2, "pow": 3, "sin": 1, "cos": 1,
}
SUPERBEST_COSTS_POS: dict[str, int] = {
    "exp": 1, "ln": 1, "mul": 3, "div": 3, "add": 3,
    "sub": 3, "neg": 2, "recip": 2, "pow": 3, "sin": 1, "cos": 1,
}


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
        annotations.append(f"mul → {superbest_construction('mul')} (3n)")
    if "+" in expr:
        annotations.append(f"add → {superbest_construction('add')} (3n)")
    if "-" in expr and "exp" not in expr:
        annotations.append(f"sub → {superbest_construction('sub')} (3n)")
    if "exp(" in expr or "math.exp" in expr:
        annotations.append(f"exp → {superbest_construction('exp')} (1n)")
    if "log(" in expr or "math.log" in expr:
        annotations.append(f"ln → {superbest_construction('ln')} (1n)")
    if "/" in expr:
        annotations.append(f"div → {superbest_construction('div')} (1n)")
    return expr + "  # SuperBEST: " + "; ".join(annotations)


def superbest_summary() -> str:
    """Return a human-readable summary of the SuperBEST routing table."""
    lines = ["SuperBEST Routing Table (two-tier: general / positive domain)",
             "=" * 72]
    lines.append(f"  {'Op':8} {'Gen':5} {'Pos':5} {'Naive':6} {'Construction':40}")
    lines.append("-" * 72)
    total_gen = total_pos = total_naive = 0
    for op in ["exp","ln","mul","div","add","sub","neg","recip","pow"]:
        gen = SUPERBEST_COSTS_GEN.get(op, 99)
        pos = SUPERBEST_COSTS_POS.get(op, 99)
        naive = NAIVE_COSTS.get(op, 0)
        total_gen += gen; total_pos += pos; total_naive += naive
        constr = superbest_construction(op)
        flag = " *" if gen != pos else ""
        lines.append(f"  {op:8} {gen:5} {pos:5} {naive:6} {constr:40}{flag}")
    lines.append("-" * 72)
    lines.append(f"  {'TOTAL':8} {total_gen:5} {total_pos:5} {total_naive:6}")
    pct_gen = (1 - total_gen/total_naive) * 100
    pct_pos = (1 - total_pos/total_naive) * 100
    lines.append(f"  Savings: {pct_gen:.1f}% (general) / {pct_pos:.1f}% (positive domain)")
    lines.append("  neg: 2n general (exl(0,deml(x,1)) = exp(0)*ln(exp(-x)) = -x, all x), 2n positive (emn(exl(0,x),1))")
    return "\n".join(lines)
