"""EML Fourier Experiment — Session 31.

Tests whether sin(x) can be expressed as a short linear combination of EML trees:
    sin(x) ≈ c₁·T₁(x) + c₂·T₂(x) + ... + cK·TK(x)

If true, EML is complete as a linear basis even though no single tree equals sin(x)
(the Infinite Zeros Barrier). This bridges the barrier result with classical Fourier
analysis.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field, asdict
from typing import Callable, Iterator

import numpy as np


# ── EML tree helpers (self-contained, avoids circular import) ─────────────────

def _generate_shapes(n: int) -> list[list[bool]]:
    """All full binary tree postorder op-sequences with n internal nodes."""
    if n == 0:
        return [[False]]
    shapes: list[list[bool]] = []
    for k in range(n):
        for ls in _generate_shapes(k):
            for rs in _generate_shapes(n - 1 - k):
                shapes.append(ls + rs + [True])
    return shapes


def _eml(a: float, b: float) -> float | None:
    """Raw EML: exp(a) - ln(b). Returns None on domain error."""
    if b <= 0:
        return None
    try:
        result = math.exp(a) - math.log(b)
        return result if math.isfinite(result) else None
    except (ValueError, OverflowError):
        return None


def _eval_tree(ops: list[bool], leaf_mask: int, x: float) -> float | None:
    stack: list[float] = []
    leaf_idx = 0
    for is_internal in ops:
        if not is_internal:
            val = x if (leaf_mask >> leaf_idx) & 1 else 1.0
            stack.append(val)
            leaf_idx += 1
        else:
            b = stack.pop()
            a = stack.pop()
            result = _eml(a, b)
            if result is None or not math.isfinite(result):
                return None
            stack.append(result)
    return stack[0] if (stack and math.isfinite(stack[0])) else None


def _format_tree(ops: list[bool], leaf_mask: int) -> str:
    stack: list[str] = []
    leaf_idx = 0
    for is_internal in ops:
        if not is_internal:
            stack.append("x" if (leaf_mask >> leaf_idx) & 1 else "1")
            leaf_idx += 1
        else:
            b = stack.pop()
            a = stack.pop()
            stack.append(f"eml({a},{b})")
    return stack[0] if stack else ""


# ── Data classes ──────────────────────────────────────────────────────────────

@dataclass
class EMLBasisAtom:
    ops: list[bool]
    leaf_mask: int
    values: np.ndarray
    formula: str = ""

    def to_dict(self) -> dict:
        return {
            "ops": self.ops,
            "leaf_mask": self.leaf_mask,
            "values": self.values.tolist(),
            "formula": self.formula,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "EMLBasisAtom":
        return cls(
            ops=d["ops"],
            leaf_mask=d["leaf_mask"],
            values=np.array(d["values"]),
            formula=d["formula"],
        )


@dataclass
class EMLFourierResult:
    target_name: str
    K: int
    coefficients: list[float]
    atoms: list[EMLBasisAtom]
    mse_train: float
    mse_test: float
    formula_str: str
    method: str
    n_dict_atoms: int
    max_internal_nodes: int

    def to_dict(self) -> dict:
        return {
            "target_name": self.target_name,
            "K": self.K,
            "coefficients": self.coefficients,
            "atoms": [a.to_dict() for a in self.atoms],
            "mse_train": self.mse_train,
            "mse_test": self.mse_test,
            "formula_str": self.formula_str,
            "method": self.method,
            "n_dict_atoms": self.n_dict_atoms,
            "max_internal_nodes": self.max_internal_nodes,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)


# ── Dictionary builder ────────────────────────────────────────────────────────

_DEFAULT_TRAIN_POINTS = list(np.linspace(0.05, 2.0, 80))
_DEFAULT_TEST_POINTS = list(np.linspace(0.025, 2.1, 40))


def build_eml_dictionary(
    max_internal_nodes: int = 4,
    probe_points: list[float] | None = None,
    min_variance: float = 1e-10,
) -> list[EMLBasisAtom]:
    """Enumerate all EML trees up to max_internal_nodes and return finite, non-constant ones.

    Each shape × each leaf bitmask (x vs 1.0) is one candidate function.
    Candidates that evaluate to infinity/NaN at any probe point, or that are
    effectively constant (variance < min_variance), are discarded.
    """
    if probe_points is None:
        probe_points = _DEFAULT_TRAIN_POINTS

    xs = np.array(probe_points, dtype=np.float64)
    atoms: list[EMLBasisAtom] = []

    for n in range(1, max_internal_nodes + 1):
        shapes = _generate_shapes(n)
        n_leaves = n + 1
        n_leaf_combos = 1 << n_leaves

        for ops in shapes:
            for mask in range(n_leaf_combos):
                if mask == 0:
                    continue  # all-constants tree — trivially constant
                vals = np.array(
                    [_eval_tree(ops, mask, float(xv)) for xv in xs],
                    dtype=object,
                )
                if any(v is None for v in vals):
                    continue
                vals_f = vals.astype(np.float64)
                if not np.all(np.isfinite(vals_f)):
                    continue
                if np.var(vals_f) < min_variance:
                    continue
                atoms.append(EMLBasisAtom(
                    ops=ops,
                    leaf_mask=mask,
                    values=vals_f,
                    formula=_format_tree(ops, mask),
                ))

    return atoms


# ── Sparse recovery ───────────────────────────────────────────────────────────

def eml_fourier_search(
    target_fn: Callable[[float], float],
    target_name: str = "f",
    max_internal_nodes: int = 4,
    max_K: int = 6,
    tol: float = 1e-6,
    method: str = "omp",
    train_points: list[float] | None = None,
    test_points: list[float] | None = None,
) -> EMLFourierResult:
    """Find a sparse EML basis decomposition of target_fn.

    method: "omp" (Orthogonal Matching Pursuit) or "lasso"
    """
    from sklearn.linear_model import OrthogonalMatchingPursuit, Lasso
    from sklearn.preprocessing import StandardScaler

    if train_points is None:
        train_points = _DEFAULT_TRAIN_POINTS
    if test_points is None:
        test_points = _DEFAULT_TEST_POINTS

    atoms = build_eml_dictionary(
        max_internal_nodes=max_internal_nodes,
        probe_points=train_points,
    )
    if not atoms:
        raise ValueError("EML dictionary is empty — check max_internal_nodes.")

    A_train = np.column_stack([a.values for a in atoms])
    b_train = np.array([target_fn(x) for x in train_points])

    # Normalize columns for numerical stability
    col_norms = np.linalg.norm(A_train, axis=0)
    col_norms[col_norms < 1e-12] = 1.0
    A_norm = A_train / col_norms

    if method == "omp":
        model = OrthogonalMatchingPursuit(n_nonzero_coefs=max_K, tol=None, fit_intercept=False)
        model.fit(A_norm, b_train)
        coef_norm = model.coef_
    elif method == "lasso":
        model = Lasso(alpha=1e-4, fit_intercept=False, max_iter=10000)
        model.fit(A_norm, b_train)
        coef_norm = model.coef_
    else:
        raise ValueError(f"Unknown method: {method!r}. Use 'omp' or 'lasso'.")

    coef = coef_norm / col_norms
    nonzero_idx = np.where(np.abs(coef) > 1e-12)[0]

    if len(nonzero_idx) == 0:
        nonzero_idx = np.array([np.argmax(np.abs(coef))])

    selected_atoms = [atoms[i] for i in nonzero_idx]
    selected_coefs = coef[nonzero_idx].tolist()
    K = len(selected_atoms)

    pred_train = A_train[:, nonzero_idx] @ np.array(selected_coefs)
    mse_train = float(np.mean((pred_train - b_train) ** 2))

    # Evaluate on held-out test points
    A_test = np.column_stack([
        np.array([_eval_tree(a.ops, a.leaf_mask, float(x)) or math.nan
                  for x in test_points])
        for a in selected_atoms
    ])
    b_test = np.array([target_fn(x) for x in test_points])
    pred_test = A_test @ np.array(selected_coefs)
    mse_test = float(np.mean((pred_test - b_test) ** 2))

    formula_parts = []
    for c, a in zip(selected_coefs, selected_atoms):
        sign = "+" if c >= 0 else "-"
        formula_parts.append(f"{sign} {abs(c):.6g}·{a.formula}")
    formula_str = " ".join(formula_parts).lstrip("+ ").strip()

    return EMLFourierResult(
        target_name=target_name,
        K=K,
        coefficients=selected_coefs,
        atoms=selected_atoms,
        mse_train=mse_train,
        mse_test=mse_test,
        formula_str=formula_str,
        method=method,
        n_dict_atoms=len(atoms),
        max_internal_nodes=max_internal_nodes,
    )


# ── Multi-target summary ──────────────────────────────────────────────────────

_STANDARD_TARGETS: list[tuple[str, Callable[[float], float]]] = [
    ("sin", math.sin),
    ("cos", math.cos),
    ("tan", lambda x: math.tan(x) if abs(math.cos(x)) > 0.1 else math.nan),
    ("exp", math.exp),
    ("log", lambda x: math.log(x) if x > 0 else math.nan),
    ("sinh", math.sinh),
    ("cosh", math.cosh),
]


def fourier_summary_table(
    max_internal_nodes: int = 3,
    max_K: int = 6,
    method: str = "omp",
) -> str:
    """Run EML Fourier search on standard targets and return a Markdown table."""
    rows = []
    for name, fn in _STANDARD_TARGETS:
        try:
            r = eml_fourier_search(
                fn, name,
                max_internal_nodes=max_internal_nodes,
                max_K=max_K,
                method=method,
            )
            rows.append((name, r.K, r.mse_train, r.mse_test, r.n_dict_atoms))
        except Exception as exc:
            rows.append((name, -1, float("nan"), float("nan"), 0))

    header = "| Target | K | MSE (train) | MSE (test) | Dict size |"
    sep    = "|--------|---|-------------|------------|-----------|"
    lines  = [header, sep]
    for name, K, mse_tr, mse_te, nd in rows:
        lines.append(f"| {name} | {K} | {mse_tr:.3e} | {mse_te:.3e} | {nd} |")
    return "\n".join(lines)
