"""
monogate.equality — Bounded-depth F16 equality decision procedure.

Implements the decidability result (blind-session THM 04-A):

    The equality problem for two F16 tree expressions of bounded depth is
    decidable unconditionally (no Schanuel-type hypothesis required).

The module exposes:

    * ``F16Tree``        — AST for F16 expressions (leaf / operator node)
    * ``parse``          — parse an F16 expression string into ``F16Tree``
    * ``decide``         — adaptive-precision equality decision procedure
    * ``DecisionResult`` — structured verdict

Usage:

    >>> from monogate.equality import parse, decide
    >>> a = parse("EML(1, 1)")      # exp(1) - ln(1) = e
    >>> b = parse("e")
    >>> decide(a, b).verdict
    'EQUAL'

    >>> decide(parse("e"), parse("pi")).verdict
    'UNEQUAL'

Grammar:

    leaf  := NUMBER | NAME | "-" expr
    expr  := OP "(" expr ("," expr)* ")" | leaf

Leaves recognised: numeric literals ("0", "1", "0.5", "1/2"), named
constants ("e", "pi", "ln2"). Operators recognised: F16 operators
(``EML``, ``EAL``, ``EXL``, ``EDL``, ``DEML``, ``LEdiv``, ``ELAd``,
``EML_neg``) and elementary ``ADD``/``SUB``/``MUL``/``DIV``/``NEG``/
``EXP``/``LOG``.

Algorithm:
    Adaptive-precision evaluation using mpmath. Starting precision
    ``p = 50 + 10*depth + 2*size``. At each round: evaluate both trees
    at precision ``p``, compare against a threshold ``10^{-p/2}``.
    If the difference is below the threshold for three successive
    doublings of ``p``, return ``EQUAL``. If the difference exceeds
    ``1000 * threshold``, return ``UNEQUAL``. Otherwise double ``p``
    and repeat. After ``max_precision`` the verdict is
    ``INDETERMINATE``.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Callable, Union

from mpmath import e, exp, log, mp, mpf, pi

__all__ = [
    "F16Tree",
    "DecisionResult",
    "parse",
    "decide",
    "F16_OPS",
    "LEAF_CONSTANTS",
]


# ─── Operator implementations ─────────────────────────────────────────

def _EML(a: mpf, b: mpf) -> mpf:
    return exp(a) - log(b)


def _EAL(a: mpf, b: mpf) -> mpf:
    return exp(a) + log(b)


def _EXL(a: mpf, b: mpf) -> mpf:
    return exp(a) * log(b)


def _EDL(a: mpf, b: mpf) -> mpf:
    return exp(a) / log(b)


def _DEML(a: mpf, b: mpf) -> mpf:
    return exp(-a) - log(b)


def _LEdiv(a: mpf, b: mpf) -> mpf:
    return a / exp(b)


def _ELAd(a: mpf, b: mpf) -> mpf:
    return exp(a) * b


def _EML_neg(a: mpf, b: mpf) -> mpf:
    return exp(-a) - log(b)


def _ADD(a: mpf, b: mpf) -> mpf:
    return a + b


def _SUB(a: mpf, b: mpf) -> mpf:
    return a - b


def _MUL(a: mpf, b: mpf) -> mpf:
    return a * b


def _DIV(a: mpf, b: mpf) -> mpf:
    return a / b


def _NEG(a: mpf) -> mpf:
    return -a


def _EXP(a: mpf) -> mpf:
    return exp(a)


def _LOG(a: mpf) -> mpf:
    return log(a)


F16_OPS: dict[str, Callable[..., mpf]] = {
    "EML": _EML, "EAL": _EAL, "EXL": _EXL, "EDL": _EDL,
    "DEML": _DEML, "LEdiv": _LEdiv, "ELAd": _ELAd, "EML_neg": _EML_neg,
    "ADD": _ADD, "SUB": _SUB, "MUL": _MUL, "DIV": _DIV,
    "NEG": _NEG, "EXP": _EXP, "LOG": _LOG,
}

LEAF_CONSTANTS: dict[str, Callable[[], mpf]] = {
    "e": lambda: e,
    "pi": lambda: pi,
    "ln2": lambda: log(mpf(2)),
}


# ─── AST ──────────────────────────────────────────────────────────────

LeafValue = Union[mpf, int, float]


@dataclass(frozen=True)
class F16Tree:
    """Immutable F16 tree AST.

    A leaf has ``op == "LEAF"`` and ``value`` set; an internal node
    has ``op`` in :data:`F16_OPS` and ``args`` as a tuple of
    :class:`F16Tree`.
    """

    op: str
    args: tuple["F16Tree", ...] = field(default_factory=tuple)
    value: LeafValue | None = None

    @classmethod
    def leaf(cls, v: LeafValue) -> "F16Tree":
        return cls(op="LEAF", args=(), value=v)

    def depth(self) -> int:
        if self.op == "LEAF":
            return 0
        if not self.args:
            return 0
        return 1 + max(a.depth() for a in self.args)

    def size(self) -> int:
        if self.op == "LEAF":
            return 1
        return 1 + sum(a.size() for a in self.args)

    def evaluate(self) -> mpf:
        """Evaluate the tree at the *current* mpmath precision."""
        return _eval(self)

    def __repr__(self) -> str:
        if self.op == "LEAF":
            return str(self.value)
        return f"{self.op}({','.join(repr(a) for a in self.args)})"


# ─── Parser ───────────────────────────────────────────────────────────

_TOKEN_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*|[-+*/()0-9.,]|\S")


def _tokenize(s: str) -> list[str]:
    return [t for t in _TOKEN_RE.findall(s) if t.strip()]


def parse(expr: str) -> F16Tree:
    """Parse an F16 expression string into an :class:`F16Tree`.

    Raises :class:`ValueError` on malformed input.
    """
    tokens = _tokenize(expr)
    pos = [0]

    def peek() -> str | None:
        return tokens[pos[0]] if pos[0] < len(tokens) else None

    def consume() -> str:
        t = tokens[pos[0]]
        pos[0] += 1
        return t

    def parse_expr() -> F16Tree:
        tok = peek()
        if tok is None:
            raise ValueError("unexpected end of input")

        if tok in F16_OPS and pos[0] + 1 < len(tokens) and tokens[pos[0] + 1] == "(":
            op = consume()
            consume()  # "("
            args: list[F16Tree] = []
            while peek() != ")":
                args.append(parse_expr())
                if peek() == ",":
                    consume()
            consume()  # ")"
            return F16Tree(op=op, args=tuple(args))

        if tok in LEAF_CONSTANTS:
            consume()
            return F16Tree.leaf(LEAF_CONSTANTS[tok]())

        if tok == "-":
            consume()
            inner = parse_expr()
            return F16Tree(op="NEG", args=(inner,))

        if re.match(r"^[0-9.]+$", tok):
            consume()
            v: mpf = mpf(tok)
            if peek() == "/":
                consume()
                denom_tok = consume()
                v = v / mpf(denom_tok)
            return F16Tree.leaf(v)

        raise ValueError(f"unexpected token: {tok!r} at position {pos[0]}")

    tree = parse_expr()
    if pos[0] != len(tokens):
        raise ValueError(
            f"trailing tokens starting at {pos[0]}: {tokens[pos[0]:]}"
        )
    return tree


# ─── Evaluator ────────────────────────────────────────────────────────

def _eval(t: F16Tree) -> mpf:
    if t.op == "LEAF":
        return mpf(t.value) if not isinstance(t.value, mpf) else t.value
    op_fn = F16_OPS[t.op]
    vals = [_eval(a) for a in t.args]
    return op_fn(*vals)


# ─── Decision procedure ──────────────────────────────────────────────

@dataclass(frozen=True)
class DecisionResult:
    """Structured verdict from :func:`decide`."""

    verdict: str              # "EQUAL" | "UNEQUAL" | "INDETERMINATE"
    precision_used: int
    final_diff_str: str
    max_depth: int
    max_size: int


def decide(
    t1: F16Tree,
    t2: F16Tree,
    *,
    max_precision: int = 1000,
    stability_runs: int = 3,
) -> DecisionResult:
    """Decide whether two F16 trees represent the same real number.

    Parameters
    ----------
    t1, t2 : F16Tree
        The trees to compare.
    max_precision : int, default 1000
        Maximum number of mpmath decimal places to try. If the
        decision is not resolved at this precision the verdict is
        ``INDETERMINATE``.
    stability_runs : int, default 3
        Number of successive precision doublings at which the
        difference must remain below threshold for the verdict to
        be ``EQUAL``.

    Returns
    -------
    DecisionResult
        Structured verdict.
    """
    d = max(t1.depth(), t2.depth())
    sz = t1.size() + t2.size()

    p = max(50, 50 + 10 * d + 2 * sz)
    equal_runs = 0
    last_diff_str = "n/a"

    while p <= max_precision:
        mp.dps = p
        try:
            v1 = _eval(t1)
            v2 = _eval(t2)
            diff = abs(v1 - v2)
        except Exception:
            return DecisionResult(
                verdict="INDETERMINATE",
                precision_used=p,
                final_diff_str="error",
                max_depth=d,
                max_size=sz,
            )

        threshold = mpf(10) ** -(p // 2)
        last_diff_str = mp.nstr(diff, 15)

        if diff > threshold * mpf(1000):
            return DecisionResult(
                verdict="UNEQUAL",
                precision_used=p,
                final_diff_str=last_diff_str,
                max_depth=d,
                max_size=sz,
            )

        if diff < threshold:
            equal_runs += 1
            if equal_runs >= stability_runs:
                return DecisionResult(
                    verdict="EQUAL",
                    precision_used=p,
                    final_diff_str=last_diff_str,
                    max_depth=d,
                    max_size=sz,
                )
        else:
            equal_runs = 0

        p = p * 2

    return DecisionResult(
        verdict="INDETERMINATE",
        precision_used=p // 2,
        final_diff_str=last_diff_str,
        max_depth=d,
        max_size=sz,
    )
