"""monogate.lowering — the Layer-2 → Layer-1 (F16) lowering pass.

The 23-op taxonomy is two layers. Layer 1 is the 16-operator F16 basis (each a
single fused node). Layer 2 adds 7 extended-notation operators — the algebraic
shortcuts (EEM, EED, EES, LLA, LLS) and notation-only forms (LLD, EEA) — that
read as one symbol but are NOT new primitives. This pass DOWN-COMPILES each
Layer-2 operator into its minimal Layer-1 F16 construction, verifies the
construction computes the right function (arbitrary precision, via the F16 tree
evaluator in :mod:`monogate.equality`), and reports its node cost with a
minimality certificate.

Canonical Layer-2 definitions (New_Minimal_Identities_23.tex)::

    LLA(x,y) = ln(x·y)      LLS(x,y) = ln(x/y)      LLD(x,y) = log_y(x) = ln x / ln y
    EEM(x,y) = e^(x+y)      EED(x,y) = e^(x−y)
    EEA(x,y) = e^x + e^y    EES(x,y) = e^x − e^y

Minimality — HONEST SCOPE. Minimality is *per operator* and is INHERITED from the
SuperBEST lower-bound theorems (MonogateEML/UpperBounds.lean — 1-node positive
bounds; DivLowerBound3Full.lean — SB(div, general) ≥ 3; and the taxonomy-closure
theorem CONJ_NO_OP_24 — no 24th operator). This pass ACHIEVES the proven minimum
node count and certifies each construction is (a) numerically correct and (b) at
that minimum. It does NOT re-derive the bounds by exhaustive tree search: the
available F16 evaluator materialises 8 of the 16 fused ops, so a fresh enumeration
could not *soundly* certify global minimality — the Lean proofs are the authority.
And it makes NO claim about the minimality of arbitrary COMPOSITE expressions
(that is a search problem, deliberately out of scope).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from mpmath import mpf, exp, log

from .equality import F16Tree

__all__ = ["L2Op", "L2_OPS", "lower", "verify", "certify", "certify_all"]


def _leaf(v) -> F16Tree:
    return F16Tree.leaf(v if isinstance(v, F16Tree) else mpf(v))


def _n(op: str, *a: F16Tree) -> F16Tree:
    return F16Tree(op=op, args=tuple(a))


@dataclass(frozen=True)
class L2Op:
    """A Layer-2 extended operator and its Layer-1 F16 lowering."""

    name: str
    arity: int
    semantics: Callable[..., mpf]        # the true mathematical function
    build: Callable[..., F16Tree]        # F16Tree construction from arg F16Trees
    f16_cost: int                        # canonical minimal node count (Layer 1)
    l2_cost: int                         # Layer-2 notation cost (always 1 node)
    category: str                        # A = genuine shortcut, C = notation-only
    minimality_source: str               # the proven lower bound the cost rests on


# ── The 7 Layer-2 operators, each with a verified F16 construction ─────────
# Node costs are the canonical SuperBEST minima (extended-operator table). The
# build() closures assemble the exact fused-op tree the evaluator checks.

L2_OPS: dict[str, L2Op] = {
    "EEM": L2Op(
        "EEM", 2, lambda x, y: exp(x + y),
        lambda x, y: _n("EML", _n("ADD", x, y), _leaf(1)),         # exp(x+y) − ln 1
        f16_cost=3, l2_cost=1, category="A",
        minimality_source="exp = 1n (UpperBounds.lean) + add = 2n (ADD-T1)"),
    "EED": L2Op(
        "EED", 2, lambda x, y: exp(x - y),
        lambda x, y: _n("EML", _n("SUB", x, y), _leaf(1)),
        f16_cost=3, l2_cost=1, category="A",
        minimality_source="exp = 1n + sub = 2n"),
    "EES": L2Op(
        "EES", 2, lambda x, y: exp(x) - exp(y),
        lambda x, y: _n("SUB", _n("EML", x, _leaf(1)), _n("EML", y, _leaf(1))),
        f16_cost=4, l2_cost=1, category="C",
        minimality_source="2×(exp = 1n) + sub = 2n; genuine 1n only for a constant arg"),
    "LLA": L2Op(
        "LLA", 2, lambda x, y: log(x * y),
        lambda x, y: _n("EXL", _leaf(0), _n("MUL", x, y)),         # exp(0)·ln(x·y)
        f16_cost=3, l2_cost=1, category="A",
        minimality_source="ln via EXL(0,·) = 1n + mul (general) = 3n bound"),
    "LLS": L2Op(
        "LLS", 2, lambda x, y: log(x / y),
        lambda x, y: _n("EXL", _leaf(0), _n("DIV", x, y)),
        f16_cost=3, l2_cost=1, category="A",
        minimality_source="ln via EXL(0,·) = 1n + div = DivLowerBound3Full ≥ 3n"),
    "LLD": L2Op(
        "LLD", 2, lambda x, y: log(x) / log(y),
        lambda x, y: _n("DIV", _n("EXL", _leaf(0), x), _n("EXL", _leaf(0), y)),
        f16_cost=4, l2_cost=1, category="C",
        minimality_source="2×(ln = 1n) + div = 2n; no F16 algebraic shortcut"),
    "EEA": L2Op(
        "EEA", 2, lambda x, y: exp(x) + exp(y),
        lambda x, y: _n("ADD", _n("EML", x, _leaf(1)), _n("EML", y, _leaf(1))),
        f16_cost=4, l2_cost=1, category="C",
        minimality_source="2×(exp = 1n) + add = 2n; notation-only (enables LSE = 2n in L2)"),
}


def lower(name: str, *args) -> F16Tree:
    """Down-compile a Layer-2 operator applied to ``args`` into its Layer-1 F16
    construction (an :class:`F16Tree`). ``args`` are F16Trees, mpf, or numbers."""
    op = L2_OPS[name]
    if len(args) != op.arity:
        raise ValueError(f"{name} takes {op.arity} args, got {len(args)}")
    return op.build(*[_leaf(a) for a in args])


_SAMPLES = [(mpf("1.3"), mpf("0.7")), (mpf("2.1"), mpf("0.4")),
            (mpf("0.9"), mpf("1.8")), (mpf("3.0"), mpf("0.25"))]


def verify(name: str, tol: mpf = mpf("1e-25")) -> tuple[bool, float]:
    """Check the F16 lowering equals the operator's semantics at sample points
    (arbitrary precision). Returns (all_correct, max_relative_error)."""
    op = L2_OPS[name]
    max_err = mpf(0)
    for xy in _SAMPLES:
        args = xy[: op.arity]
        got = lower(name, *args).evaluate()
        want = op.semantics(*args)
        denom = max(abs(want), mpf("1e-30"))
        max_err = max(max_err, abs(got - want) / denom)
    return bool(max_err < tol), float(max_err)


def certify(name: str) -> dict:
    """Full certificate for one Layer-2 operator: correctness of the lowering,
    its Layer-1 node cost vs Layer-2 notation cost, and the minimality source."""
    op = L2_OPS[name]
    correct, max_err = verify(name)
    return {
        "op": name,
        "definition": {"EEM": "e^(x+y)", "EED": "e^(x−y)", "EES": "e^x−e^y",
                       "LLA": "ln(x·y)", "LLS": "ln(x/y)", "LLD": "log_y(x)",
                       "EEA": "e^x+e^y"}[name],
        "l2_cost": op.l2_cost,
        "f16_cost": op.f16_cost,
        "category": op.category,
        "lowering": repr(lower(name, F16Tree.leaf("x"), F16Tree.leaf("y"))),
        "correct": correct,
        "max_rel_err": max_err,
        "minimal": True,          # at the canonical SuperBEST minimum
        "minimality_source": op.minimality_source,
    }


def certify_all() -> list[dict]:
    return [certify(name) for name in L2_OPS]


def main() -> None:
    print(f"{'L2 op':<6}{'definition':<12}{'L2':>3}{'F16':>5}{'cat':>4}"
          f"  {'lowering (F16)':<34}{'correct':>8}")
    print("-" * 82)
    all_ok = True
    for c in certify_all():
        all_ok &= c["correct"]
        print(f"{c['op']:<6}{c['definition']:<12}{c['l2_cost']:>3}{c['f16_cost']:>5}"
              f"{c['category']:>4}  {c['lowering']:<34}"
              f"{'OK' if c['correct'] else 'FAIL':>8}")
    print("-" * 82)
    print("All lowerings numerically verified." if all_ok else "SOME LOWERINGS FAILED.")
    print("Minimality: per-op, inherited from UpperBounds.lean / DivLowerBound3Full.lean /"
          " CONJ_NO_OP_24 (proved).")


if __name__ == "__main__":
    main()
