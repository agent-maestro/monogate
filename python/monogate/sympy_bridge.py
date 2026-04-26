"""
monogate.sympy_bridge — SymPy interoperability for EML expressions.

Converts EML expression trees (as produced by monogate search functions)
to and from SymPy expressions.  Enables symbolic simplification, LaTeX
rendering, identity verification, and end-to-end pipeline integration
with eml-cost / eml-rewrite.

E-186 (2026-04-26) extension: from_sympy() now handles all elementary
operations, not just exp/log. Pfaffian-not-EML expressions raise a
clear, actionable error instead of silently approximating.

Tree format (extended in E-186, backward compatible)
----------------------------------------------------
A tree is a ``dict`` with an ``"op"`` key. Supported ops:

  - ``leaf``   {"op": "leaf", "val": "x"|number}
  - ``eml``    {"op": "eml",  "left": tree, "right": tree}    -- exp(L) - log(R)
  - ``exp``    {"op": "exp",  "child": tree}                   -- exp(c)
  - ``log``    {"op": "log",  "child": tree}                   -- log(c)
  - ``neg``    {"op": "neg",  "child": tree}                   -- -c
  - ``add``    {"op": "add",  "children": [tree, ...]}         -- sum
  - ``mul``    {"op": "mul",  "children": [tree, ...]}         -- product
  - ``sub``    {"op": "sub",  "left": tree, "right": tree}     -- L - R
  - ``div``    {"op": "div",  "left": tree, "right": tree}     -- L / R
  - ``pow``    {"op": "pow",  "base": tree, "exponent": tree}  -- base ** exponent
  - ``sin``    {"op": "sin",  "child": tree}
  - ``cos``    {"op": "cos",  "child": tree}
  - ``tan``    {"op": "tan",  "child": tree}
  - ``sinh``   {"op": "sinh", "child": tree}
  - ``cosh``   {"op": "cosh", "child": tree}
  - ``tanh``   {"op": "tanh", "child": tree}
  - ``sqrt``   {"op": "sqrt", "child": tree}
  - ``atan``   {"op": "atan", "child": tree}

Pre-E-186 trees ({"op": "eml" | "leaf"} only) remain valid and evaluable.

Public API
----------
to_sympy(tree, x_sym=None)     -> sympy.Expr
from_sympy(expr)               -> dict
simplify_eml(tree)             -> sympy.Expr
latex_eml(tree)                -> str
verify_identity(tree1, tree2)  -> bool
node_count(tree)               -> int
"""

from __future__ import annotations

from typing import Any

__all__ = [
    "to_sympy",
    "from_sympy",
    "simplify_eml",
    "latex_eml",
    "verify_identity",
    "node_count",
    "PfaffianNotEMLError",
]


_SYMPY_MISSING_MSG = (
    "sympy is required for monogate.sympy_bridge.\n"
    "Install it with:  pip install monogate[sympy]\n"
    "or:               pip install sympy>=1.12"
)


class PfaffianNotEMLError(ValueError):
    """Raised when from_sympy is asked to convert a Pfaffian-not-EML expression.

    Bessel, Airy, Lambert W, hypergeometric, error function, and similar
    special functions live OUTSIDE the EML class. No finite EML tree can
    express them. We raise instead of silently approximating, so callers
    can route them to the appropriate substrate (eml-cost.analyze for
    structural profile, monogate.special for tabulated approximations).
    """


def _require_sympy():
    """Import and return sympy, raising ImportError with helpful message if absent."""
    try:
        import sympy
        return sympy
    except ImportError:
        raise ImportError(_SYMPY_MISSING_MSG) from None


# Pfaffian-not-EML SymPy classes — these raise PfaffianNotEMLError on conversion.
def _pne_classes():
    sp = _require_sympy()
    return (
        sp.besselj, sp.bessely, sp.besseli, sp.besselk,
        sp.airyai, sp.airybi, sp.airyaiprime, sp.airybiprime,
        sp.LambertW,
        sp.erf, sp.erfc, sp.erfi, sp.erfinv,
        sp.hyper, sp.meijerg,
        sp.gamma, sp.loggamma, sp.digamma, sp.polygamma,
        sp.zeta, sp.dirichlet_eta, sp.polylog,
    )


# ── EML tree → SymPy ──────────────────────────────────────────────────────────


def to_sympy(tree, x_sym=None):
    """Convert an EML expression tree to a SymPy expression.

    Handles every op listed in the module docstring. Pre-E-186 trees
    (eml + leaf only) still convert correctly.

    Args:
        tree:   EML tree dict (any supported op) or string leaf shorthand.
        x_sym:  Symbol to use for ``"x"`` leaves. Defaults to ``Symbol("x")``.

    Returns:
        sympy.Expr.

    Raises:
        ImportError: If sympy is not installed.
        TypeError:   If tree has an unrecognised op or shape.
    """
    sp = _require_sympy()
    if x_sym is None:
        x_sym = sp.Symbol("x")

    # String shorthand
    if isinstance(tree, str):
        if tree == "x":
            return x_sym
        try:
            v = float(tree)
            return sp.Integer(int(v)) if float(v) == int(float(v)) else sp.Float(v)
        except ValueError:
            raise TypeError(f"to_sympy: unknown string leaf {tree!r}")

    if not isinstance(tree, dict):
        raise TypeError(f"to_sympy: expected dict or str, got {type(tree)!r}")

    op = tree.get("op")

    # Leaves
    if op == "leaf":
        val = tree["val"]
        if val == "x":
            return x_sym
        if isinstance(val, str):
            # Allow named symbols in leaves (used by from_sympy for multi-symbol)
            return sp.Symbol(val)
        if isinstance(val, (int, float)):
            v = float(val)
            return sp.Integer(int(v)) if v == int(v) else sp.Float(v)
        raise TypeError(f"to_sympy: unknown leaf val {val!r}")

    # The original EML primitive: eml(a, b) = exp(a) - log(b)
    if op == "eml":
        a = to_sympy(tree["left"], x_sym)
        b = to_sympy(tree["right"], x_sym)
        return sp.exp(a) - sp.log(b)

    # E-186 extended ops
    if op == "exp":
        return sp.exp(to_sympy(tree["child"], x_sym))
    if op == "log":
        return sp.log(to_sympy(tree["child"], x_sym))
    if op == "neg":
        return -to_sympy(tree["child"], x_sym)
    if op == "add":
        children = [to_sympy(c, x_sym) for c in tree["children"]]
        result = children[0]
        for c in children[1:]:
            result = result + c
        return result
    if op == "mul":
        children = [to_sympy(c, x_sym) for c in tree["children"]]
        result = children[0]
        for c in children[1:]:
            result = result * c
        return result
    if op == "sub":
        return to_sympy(tree["left"], x_sym) - to_sympy(tree["right"], x_sym)
    if op == "div":
        return to_sympy(tree["left"], x_sym) / to_sympy(tree["right"], x_sym)
    if op == "pow":
        return to_sympy(tree["base"], x_sym) ** to_sympy(tree["exponent"], x_sym)
    if op == "sin":
        return sp.sin(to_sympy(tree["child"], x_sym))
    if op == "cos":
        return sp.cos(to_sympy(tree["child"], x_sym))
    if op == "tan":
        return sp.tan(to_sympy(tree["child"], x_sym))
    if op == "sinh":
        return sp.sinh(to_sympy(tree["child"], x_sym))
    if op == "cosh":
        return sp.cosh(to_sympy(tree["child"], x_sym))
    if op == "tanh":
        return sp.tanh(to_sympy(tree["child"], x_sym))
    if op == "sqrt":
        return sp.sqrt(to_sympy(tree["child"], x_sym))
    if op == "atan":
        return sp.atan(to_sympy(tree["child"], x_sym))

    if op == "?":
        raise ValueError(
            "to_sympy: tree contains unexpanded placeholder '?'. "
            "Fully expand the tree before converting."
        )

    raise TypeError(f"to_sympy: unknown op {op!r}")


# ── SymPy → EML tree (E-186 full elementary support) ─────────────────────────


def _leaf_for(expr) -> dict:
    """Wrap a SymPy atom (Symbol or Number) as a leaf dict."""
    sp = _require_sympy()
    if expr.is_Symbol:
        return {"op": "leaf", "val": expr.name}
    if expr.is_Number:
        try:
            v = float(expr)
            return {"op": "leaf", "val": v}
        except (TypeError, ValueError):
            # Symbolic constants like pi, E
            return {"op": "leaf", "val": str(expr)}
    raise TypeError(f"_leaf_for: not an atom: {expr!r}")


def from_sympy(expr) -> dict[str, Any]:
    """Convert a SymPy expression to an EML tree.

    Recursively walks the SymPy AST and maps every node to the
    corresponding EML tree op. Pre-E-186 behavior (exp/log direct
    handling) preserved for backwards compatibility — the resulting
    trees may differ slightly in shape but evaluate identically.

    Args:
        expr: SymPy expression.

    Returns:
        EML tree dict.

    Raises:
        ImportError:           If sympy is not installed.
        PfaffianNotEMLError:   If expr contains erf, Bessel, Airy,
                               Lambert W, hypergeometric, gamma, etc.
                               These have no finite EML tree.
        NotImplementedError:   If expr contains an op we don't recognize.

    Examples::

        >>> import sympy as sp
        >>> x = sp.Symbol('x')
        >>> from_sympy(sp.exp(x) + sp.sin(x))
        {'op': 'add', 'children': [
            {'op': 'exp', 'child': {'op': 'leaf', 'val': 'x'}},
            {'op': 'sin', 'child': {'op': 'leaf', 'val': 'x'}}]}

    Pfaffian-not-EML raises clearly::

        >>> from_sympy(sp.erf(x))
        Traceback (most recent call last):
            ...
        PfaffianNotEMLError: erf(x) is Pfaffian-not-EML (chain order 2). ...
    """
    sp = _require_sympy()

    # Atoms first
    if expr.is_Symbol or expr.is_Number:
        return _leaf_for(expr)

    # Symbolic constants (pi, E) — concretize to float leaves
    import math as _math
    if expr is sp.pi:
        return {"op": "leaf", "val": _math.pi}
    if expr is sp.E:
        return {"op": "leaf", "val": _math.e}
    if expr is sp.EulerGamma:
        return {"op": "leaf", "val": 0.5772156649015329}

    # Imaginary unit and complex literals are not in the real EML class.
    if expr is sp.I or expr.is_complex and not expr.is_real:
        raise NotImplementedError(
            f"from_sympy: complex/imaginary literal {expr} cannot be converted "
            f"to a real-valued EML tree. Use sin_via_euler / cos_via_euler "
            f"for complex-routed trig if needed."
        )

    # Min/Max are non-smooth, not elementary in the EML sense.
    if expr.func in (sp.Min, sp.Max, sp.Abs):
        raise NotImplementedError(
            f"from_sympy: {expr.func.__name__}({expr.args}) is non-smooth and "
            f"not in the EML elementary class. ReLU = Max(0, x) and similar "
            f"piecewise functions require a different substrate."
        )

    # Pfaffian-not-EML guard
    pne = _pne_classes()
    for cls in pne:
        if isinstance(expr, cls):
            cls_name = type(expr).__name__
            raise PfaffianNotEMLError(
                f"{expr} is Pfaffian-not-EML (class {cls_name}). "
                f"No finite EML tree exists. Use eml_cost.analyze() to "
                f"inspect its Pfaffian profile."
            )
    # Recursive walk — also catch PNE in subexpressions
    for sub in expr.args:
        for cls in pne:
            if isinstance(sub, cls):
                cls_name = type(sub).__name__
                raise PfaffianNotEMLError(
                    f"{expr} contains a Pfaffian-not-EML subterm {sub} "
                    f"(class {cls_name}). No finite EML tree exists."
                )

    func = expr.func

    # Elementary special funcs
    if func is sp.exp:
        return {"op": "exp", "child": from_sympy(expr.args[0])}
    if func is sp.log:
        return {"op": "log", "child": from_sympy(expr.args[0])}
    if func is sp.sin:
        return {"op": "sin", "child": from_sympy(expr.args[0])}
    if func is sp.cos:
        return {"op": "cos", "child": from_sympy(expr.args[0])}
    if func is sp.tan:
        return {"op": "tan", "child": from_sympy(expr.args[0])}
    if func is sp.sinh:
        return {"op": "sinh", "child": from_sympy(expr.args[0])}
    if func is sp.cosh:
        return {"op": "cosh", "child": from_sympy(expr.args[0])}
    if func is sp.tanh:
        return {"op": "tanh", "child": from_sympy(expr.args[0])}
    if func is sp.atan:
        return {"op": "atan", "child": from_sympy(expr.args[0])}

    # sqrt(x) is sympy.Pow(x, 1/2). Catch it explicitly for cleaner trees.
    if func is sp.Pow:
        base, exponent = expr.args
        if exponent == sp.Rational(1, 2):
            return {"op": "sqrt", "child": from_sympy(base)}
        if exponent == -1:
            # 1/x → div(1, x)
            return {"op": "div", "left": {"op": "leaf", "val": 1.0},
                    "right": from_sympy(base)}
        return {"op": "pow",
                "base": from_sympy(base),
                "exponent": from_sympy(exponent)}

    # Add: handle the special case "exp(a) - log(b)" → eml(a, b) for
    # backwards compatibility, plus general n-ary add with negation
    # extracted into sub.
    if func is sp.Add:
        # First, try the legacy exp(a) + (-1)*log(b) → eml(a, b) shortcut.
        # This preserves pre-E-186 tree shapes for users who depend on them.
        if len(expr.args) == 2:
            a, b = expr.args
            # exp(a) + Mul(-1, log(b))
            if isinstance(a, sp.exp) and isinstance(b, sp.Mul):
                if len(b.args) == 2 and b.args[0] == -1 and isinstance(b.args[1], sp.log):
                    return {"op": "eml",
                            "left": from_sympy(a.args[0]),
                            "right": from_sympy(b.args[1].args[0])}
            if isinstance(b, sp.exp) and isinstance(a, sp.Mul):
                if len(a.args) == 2 and a.args[0] == -1 and isinstance(a.args[1], sp.log):
                    return {"op": "eml",
                            "left": from_sympy(b.args[0]),
                            "right": from_sympy(a.args[1].args[0])}
        # General Add: convert each child, sum
        return {"op": "add",
                "children": [from_sympy(arg) for arg in expr.args]}

    # Mul: handle negation (Mul(-1, x) → neg(x)) and general product
    if func is sp.Mul:
        # Mul(-1, ...) → neg(rest)
        coeffs = [a for a in expr.args if a == -1]
        rest = [a for a in expr.args if a != -1]
        if coeffs and not rest:
            # Just -1
            return {"op": "leaf", "val": -1.0}
        if coeffs and len(coeffs) == 1:
            # Negation of the rest
            if len(rest) == 1:
                return {"op": "neg", "child": from_sympy(rest[0])}
            return {"op": "neg",
                    "child": {"op": "mul",
                              "children": [from_sympy(a) for a in rest]}}
        # General Mul
        return {"op": "mul",
                "children": [from_sympy(arg) for arg in expr.args]}

    raise NotImplementedError(
        f"from_sympy: cannot convert {expr!r} (class {type(expr).__name__}) "
        f"to EML tree. Either it is Pfaffian-not-EML "
        f"(use eml_cost.analyze for structural profile) or it is an "
        f"unrecognized SymPy class (please file an issue)."
    )


# ── Tree introspection ───────────────────────────────────────────────────────


def node_count(tree) -> int:
    """Count operator nodes in an EML tree (excludes leaves).

    For SuperBEST cost comparison: this counts the EML primitive nodes
    that an optimal routing would build. Compound ops (add/mul/sub/div/
    sin/cos/...) are counted by their SuperBEST construction cost rather
    than as a single node, since each compounds into multiple eml-level
    nodes when actually realized.

    Cost table (positive-domain SuperBEST defaults):
      eml=1, exp=1, log=3, neg=2, add=3, mul=2, sub=3, div=1,
      pow=3, sqrt=1, sin=1, cos=1, tan=2, sinh=2, cosh=2, tanh=1, atan=1
    """
    if isinstance(tree, str):
        return 0
    if not isinstance(tree, dict):
        return 0
    op = tree.get("op")
    if op == "leaf":
        return 0
    op_costs = {
        "eml": 1, "exp": 1, "log": 3, "neg": 2,
        "add": 3, "mul": 2, "sub": 3, "div": 1,
        "pow": 3, "sqrt": 1,
        "sin": 1, "cos": 1, "tan": 2,
        "sinh": 2, "cosh": 2, "tanh": 1, "atan": 1,
    }
    cost = op_costs.get(op, 0)
    children = []
    if "child" in tree:
        children.append(tree["child"])
    if "left" in tree:
        children.append(tree["left"])
    if "right" in tree:
        children.append(tree["right"])
    if "base" in tree:
        children.append(tree["base"])
    if "exponent" in tree:
        children.append(tree["exponent"])
    if "children" in tree:
        children.extend(tree["children"])
    for c in children:
        cost += node_count(c)
    return cost


# ── simplify_eml / latex_eml / verify_identity (preserved API) ──────────────


def simplify_eml(tree):
    """Convert EML tree to SymPy and apply sympy.simplify()."""
    sp = _require_sympy()
    return sp.simplify(to_sympy(tree))


def latex_eml(tree) -> str:
    """LaTeX representation via SymPy."""
    sp = _require_sympy()
    return sp.latex(to_sympy(tree))


def verify_identity(tree1, tree2) -> bool:
    """True if SymPy proves the two EML trees symbolically equal."""
    sp = _require_sympy()
    diff = sp.simplify(to_sympy(tree1) - to_sympy(tree2))
    return diff == 0
