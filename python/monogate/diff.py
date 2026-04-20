"""
monogate.diff — Symbolic differentiation of EML expression trees.

The EML derivative rule:

    d/dx [eml(f, g)] = f'·exp(f) − g'/g

Using the chain rule applied to exp(f) − ln(g):

    d/dx exp(f) = f' · exp(f)
    d/dx ln(g)  = g'/g

So the derivative of eml(f, g) is:

    sub(mul(f', eml(f, 1)),  div(g', g))

implemented using BEST-routing node costs (mul=4, div=1, sub=5).

Public API
----------
diff(tree)           -> tree (derivative as EML-format dict)
node_count(tree)     -> int  (BEST-routing node count)

Tree format (same as monogate.sympy_bridge)
-------------------------------------------
    {"op": "leaf", "val": "x"}      variable
    {"op": "leaf", "val": 1.0}      constant
    {"op": "eml",  "left": ..., "right": ...}

Examples::

    >>> from monogate.diff import diff, node_count
    >>> exp_x = {"op": "eml", "left": leaf("x"), "right": leaf(1)}
    >>> d = diff(exp_x)
    >>> node_count(d)   # exp(x) is self-derivative
    1
"""

from __future__ import annotations

__all__ = ["diff", "node_count", "leaf", "eml_node"]

# ── Tree constructors ─────────────────────────────────────────────────────────

def leaf(val: str | float | int) -> dict:
    return {"op": "leaf", "val": val}

def eml_node(left: dict, right: dict) -> dict:
    return {"op": "eml", "left": left, "right": right}

_LEAF_X    = leaf("x")
_LEAF_1    = leaf(1)
_LEAF_0    = leaf(0)
_LEAF_NEG1 = leaf(-1)

# Internal symbolic ops (not EML nodes — used during differentiation, then
# counted using BEST costs). These are separate from the public eml_node tree
# format so that intermediate operations can be simplified before counting.

def _mul(L: dict, R: dict) -> dict:
    return {"op": "_mul", "left": L, "right": R}

def _div(L: dict, R: dict) -> dict:
    return {"op": "_div", "left": L, "right": R}

def _sub(L: dict, R: dict) -> dict:
    return {"op": "_sub", "left": L, "right": R}

def _neg(X: dict) -> dict:
    return {"op": "_neg", "val": X}


# ── Simplification ────────────────────────────────────────────────────────────

def _is_zero(t: dict) -> bool:
    return t.get("op") == "leaf" and t.get("val") == 0

def _is_one(t: dict) -> bool:
    return t.get("op") == "leaf" and t.get("val") == 1

def _simplify(t: dict) -> dict:
    op = t.get("op")

    if op in ("leaf",):
        return t

    if op == "eml":
        L = _simplify(t["left"])
        R = _simplify(t["right"])
        return eml_node(L, R)

    if op == "_mul":
        L = _simplify(t["left"])
        R = _simplify(t["right"])
        if _is_zero(L) or _is_zero(R):
            return _LEAF_0
        if _is_one(L):
            return R
        if _is_one(R):
            return L
        return _mul(L, R)

    if op == "_div":
        L = _simplify(t["left"])
        R = _simplify(t["right"])
        if _is_zero(L):
            return _LEAF_0
        if _is_one(R):
            return L
        return _div(L, R)

    if op == "_sub":
        L = _simplify(t["left"])
        R = _simplify(t["right"])
        if _is_zero(R):
            return L
        if _is_zero(L):
            return _neg(R)
        return _sub(L, R)

    if op == "_neg":
        X = _simplify(t["val"])
        if _is_zero(X):
            return _LEAF_0
        return _neg(X)

    return t


# ── Symbolic differentiation ──────────────────────────────────────────────────

def _diff_internal(t: dict) -> dict:
    """d/dx of tree t. Returns a tree using _mul/_div/_sub/_neg/_eml/_leaf."""
    op = t.get("op")

    if op == "leaf":
        if t.get("val") == "x":
            return _LEAF_1       # d/dx x = 1
        return _LEAF_0           # d/dx c = 0

    if op == "eml":
        # eml(f, g) = exp(f) - ln(g)
        # d/dx = f' * exp(f) - g'/g
        f, g = t["left"], t["right"]
        df = _diff_internal(f)
        dg = _diff_internal(g)
        exp_f = eml_node(f, _LEAF_1)          # exp(f) = eml(f, 1)
        term1 = _mul(df, exp_f)               # f' * exp(f)
        term2 = _div(dg, g)                   # g'/g
        return _sub(term1, term2)

    if op == "_mul":
        # product rule: (LR)' = L'R + LR'
        L, R = t["left"], t["right"]
        dL = _diff_internal(L)
        dR = _diff_internal(R)
        return _sub(_mul(dL, R), _neg(_mul(L, dR)))

    if op == "_div":
        # quotient rule: (L/R)' = (L'R - LR') / R²
        L, R = t["left"], t["right"]
        dL = _diff_internal(L)
        dR = _diff_internal(R)
        num = _sub(_mul(dL, R), _mul(L, dR))
        den = _mul(R, R)
        return _div(num, den)

    if op == "_sub":
        L, R = t["left"], t["right"]
        return _sub(_diff_internal(L), _diff_internal(R))

    if op == "_neg":
        return _neg(_diff_internal(t["val"]))

    return _LEAF_0


# ── BEST-routing node count ───────────────────────────────────────────────────

# BEST routing costs (updated: mul=4 via EXL/EAL/EML mixed, add=3)
_BEST_COST = {
    "eml":   1,    # one EML gate
    "_mul":  4,    # Mixed EXL/EAL/EML (MUL-10 result)
    "_div":  1,    # EDL: div_edl = 1 node
    "_sub":  5,    # EML: sub_eml = 5 nodes
    "_neg":  6,    # EDL: neg_edl = 6 nodes
}


def node_count(t: dict) -> int:
    """BEST-routing node count for a derivative tree."""
    op = t.get("op")
    if op == "leaf":
        return 0
    cost = _BEST_COST.get(op, 1)
    children = []
    if "left" in t:  children.append(t["left"])
    if "right" in t: children.append(t["right"])
    if "val" in t and isinstance(t["val"], dict): children.append(t["val"])
    return cost + sum(node_count(c) for c in children)


# ── Public API ────────────────────────────────────────────────────────────────

def diff(tree: dict) -> dict:
    """Differentiate an EML expression tree with respect to x.

    The derivative of eml(f, g) is:

        f'·exp(f) − g'/g

    implemented recursively and simplified (zero/one elimination).
    The result is a mixed tree using EML nodes plus intermediate _mul/_div/_sub
    nodes — call ``node_count()`` for the BEST-routing cost.

    Args:
        tree: EML expression tree dict.
              Leaves: ``{"op": "leaf", "val": "x"}`` or ``{"op": "leaf", "val": c}``.
              Nodes:  ``{"op": "eml", "left": ..., "right": ...}``.

    Returns:
        Derivative tree (same dict format).

    Examples::

        >>> from monogate.diff import diff, node_count, leaf, eml_node
        >>> # exp(x) = eml(x, 1)
        >>> exp_x = eml_node(leaf("x"), leaf(1))
        >>> d = diff(exp_x)
        >>> node_count(d)
        1
        >>> # exp(x) is self-derivative: d/dx exp(x) = exp(x)

        >>> # e - ln(x) = eml(1, x) — derivative is -1/x
        >>> eminuslnx = eml_node(leaf(1), leaf("x"))
        >>> node_count(diff(eminuslnx))
        7

        >>> # eml(eml(x, 1), 1) = exp(exp(x)) — derivative is exp(exp(x)) * exp(x)
        >>> expexpx = eml_node(eml_node(leaf("x"), leaf(1)), leaf(1))
        >>> node_count(diff(expexpx))
        7
    """
    raw = _diff_internal(tree)
    return _simplify(raw)


def diff_info(tree: dict) -> dict:
    """Return derivative tree plus metadata.

    Returns dict with keys:
        tree      : the input tree
        derivative: the derivative tree (simplified)
        n_input   : BEST node count of input
        n_deriv   : BEST node count of derivative
        ratio     : n_deriv / n_input (infinity for constant trees)
    """
    d = diff(tree)
    n_in  = node_count(tree)
    n_out = node_count(d)
    return {
        "tree":       tree,
        "derivative": d,
        "n_input":    n_in,
        "n_deriv":    n_out,
        "ratio":      n_out / n_in if n_in > 0 else float("inf"),
    }
