"""EML Fourier v4 — Lasso-based sparse recovery.

Root cause of v3 regression: QR selects geometrically-spread atoms, not
sin-relevant ones. When N=2's good atoms are replaced by orthogonally-selected
N=3 atoms, OMP sees a worse basis and the floor jumps up.

Fix: replace QR-prune + OMP with Lasso (L1-regularized regression).
Lasso naturally selects atoms relevant to the target (sin-relevant residual
at each penalty level) and is robust to collinearity. We sweep alpha from
1e-8 to 1e-2, pick the alpha with lowest test MSE, and call that the floor.

All atoms still L2-normalized on train grid (numerical stability), with
coefficients rescaled at output.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Callable

import numpy as np

from monogate.frontiers.eml_fourier import (
    EMLBasisAtom,
    EMLFourierResult,
    _eval_tree,
    _format_tree,
    _generate_shapes,
    _DEFAULT_TRAIN_POINTS,
    _DEFAULT_TEST_POINTS,
)

# Log-spaced alpha grid for Lasso sweep
_ALPHAS = np.logspace(-8, -1, 40).tolist()


@dataclass
class EMLFourierV4Result(EMLFourierResult):
    floor_detected: bool = False
    floor_alpha: float = float("nan")
    floor_mse: float = float("nan")
    n_selected: int = 0
    n_raw_atoms: int = 0
    n_independent_atoms: int = 0

    def to_dict(self) -> dict:
        d = super().to_dict()
        d["floor_detected"] = self.floor_detected
        d["floor_alpha"] = self.floor_alpha
        d["floor_mse"] = self.floor_mse
        d["n_selected"] = self.n_selected
        d["n_raw_atoms"] = self.n_raw_atoms
        d["n_independent_atoms"] = self.n_independent_atoms
        return d


def build_eml_dictionary_v4(
    max_internal_nodes: int = 4,
    probe_points: list[float] | None = None,
    min_variance: float = 1e-10,
) -> tuple[list[EMLBasisAtom], np.ndarray]:
    """Build unit-norm EML dictionary. Same as v3."""
    if probe_points is None:
        probe_points = _DEFAULT_TRAIN_POINTS

    xs = np.array(probe_points, dtype=np.float64)
    atoms: list[EMLBasisAtom] = []
    norms: list[float] = []

    for n in range(1, max_internal_nodes + 1):
        shapes = _generate_shapes(n)
        n_leaves = n + 1
        n_leaf_combos = 1 << n_leaves

        for ops in shapes:
            for mask in range(n_leaf_combos):
                if mask == 0:
                    continue

                vals_raw = [_eval_tree(ops, mask, float(xv)) for xv in xs]
                if any(v is None for v in vals_raw):
                    continue

                vals_f = np.array(vals_raw, dtype=np.float64)
                if not np.all(np.isfinite(vals_f)):
                    continue
                if np.var(vals_f) < min_variance:
                    continue

                l2 = float(np.linalg.norm(vals_f))
                if l2 < 1e-15:
                    continue
                vals_normed = vals_f / l2

                atoms.append(EMLBasisAtom(
                    ops=ops,
                    leaf_mask=mask,
                    values=vals_normed,
                    formula=_format_tree(ops, mask),
                ))
                norms.append(l2)

    return atoms, np.array(norms, dtype=np.float64)


def _eval_atoms_on_points(
    atoms: list[EMLBasisAtom],
    norms: np.ndarray,
    points: list[float],
) -> np.ndarray:
    """Evaluate atoms on points, normalized by training norms."""
    rows = []
    for a, norm in zip(atoms, norms):
        vals = np.array([
            _eval_tree(a.ops, a.leaf_mask, float(x)) or math.nan
            for x in points
        ], dtype=np.float64)
        rows.append(vals / norm)
    return np.column_stack(rows)  # shape (n_points, n_atoms)


def eml_fourier_search_v4(
    target_fn: Callable[[float], float],
    target_name: str = "f",
    max_internal_nodes: int = 4,
    alphas: list[float] | None = None,
    train_points: list[float] | None = None,
    test_points: list[float] | None = None,
) -> EMLFourierV4Result:
    """EML Fourier search via Lasso alpha sweep.

    Sweeps alpha values in descending order (most sparse → densest).
    Tracks test MSE at each alpha; reports the alpha achieving the floor.
    No QR pruning — Lasso handles collinearity natively.
    """
    from sklearn.linear_model import Lasso

    if train_points is None:
        train_points = _DEFAULT_TRAIN_POINTS
    if test_points is None:
        test_points = _DEFAULT_TEST_POINTS
    if alphas is None:
        alphas = _ALPHAS

    atoms, atom_norms = build_eml_dictionary_v4(
        max_internal_nodes=max_internal_nodes,
        probe_points=train_points,
    )
    if not atoms:
        raise ValueError("EML dictionary is empty.")

    # Build normalized matrices
    A_train = np.column_stack([a.values for a in atoms])  # already unit-norm
    b_train = np.array([target_fn(x) for x in train_points])
    b_test = np.array([target_fn(x) for x in test_points])

    A_test = _eval_atoms_on_points(atoms, atom_norms, test_points)

    n_raw = len(atoms)

    # Count approximate rank via SVD
    try:
        sv = np.linalg.svd(A_train, compute_uv=False)
        n_indep = int(np.sum(sv > 1e-8 * sv[0]))
    except Exception:
        n_indep = n_raw

    # Sweep alpha descending (high sparsity → low sparsity)
    best_mse_test = float("inf")
    best_alpha = float("nan")
    best_coef_normed = np.zeros(n_raw)
    floor_detected = False

    mse_by_alpha: list[tuple[float, float]] = []

    for alpha in sorted(alphas, reverse=True):
        try:
            model = Lasso(alpha=alpha, fit_intercept=False, max_iter=5000, tol=1e-6)
            model.fit(A_train, b_train)
            coef = model.coef_
        except Exception:
            continue

        nz = np.where(np.abs(coef) > 1e-12)[0]
        if len(nz) == 0:
            continue

        # Test MSE in normalized space
        pred_test = A_test[:, nz] @ coef[nz]
        mse_t = float(np.mean((pred_test - b_test) ** 2))
        if not math.isfinite(mse_t):
            mse_t = float("inf")

        mse_by_alpha.append((alpha, mse_t))
        if mse_t < best_mse_test:
            best_mse_test = mse_t
            best_alpha = alpha
            best_coef_normed = coef.copy()

    # Detect floor: last 5 alphas don't improve by >5%
    if len(mse_by_alpha) >= 6:
        recent_mses = [m for _, m in mse_by_alpha[-5:]]
        if min(recent_mses) > 0.95 * mse_by_alpha[-6][1]:
            floor_detected = True

    # Rescale coefficients
    nonzero_idx = np.where(np.abs(best_coef_normed) > 1e-12)[0]
    if len(nonzero_idx) == 0:
        nonzero_idx = np.array([int(np.argmax(np.abs(best_coef_normed)))])

    selected_atoms = [atoms[i] for i in nonzero_idx]
    selected_norms = atom_norms[nonzero_idx]
    selected_coefs = (best_coef_normed[nonzero_idx] / selected_norms).tolist()

    # Final MSE with rescaled coefficients on raw atoms
    A_train_final = np.column_stack([
        np.array([_eval_tree(a.ops, a.leaf_mask, float(x)) or math.nan
                  for x in train_points], dtype=np.float64)
        for a in selected_atoms
    ])
    pred_train_final = A_train_final @ np.array(selected_coefs)
    mse_train = float(np.mean((pred_train_final - b_train) ** 2))

    A_test_final = np.column_stack([
        np.array([_eval_tree(a.ops, a.leaf_mask, float(x)) or math.nan
                  for x in test_points], dtype=np.float64)
        for a in selected_atoms
    ])
    pred_test_final = A_test_final @ np.array(selected_coefs)
    mse_test_final = float(np.mean((pred_test_final - b_test) ** 2))

    formula_parts = []
    for c, a in zip(selected_coefs, selected_atoms):
        sign = "+" if c >= 0 else "-"
        formula_parts.append(f"{sign} {abs(c):.6g}*{a.formula}")
    formula_str = " ".join(formula_parts).lstrip("+ ").strip()

    return EMLFourierV4Result(
        target_name=target_name,
        K=len(selected_atoms),
        coefficients=selected_coefs,
        atoms=selected_atoms,
        mse_train=mse_train,
        mse_test=mse_test_final,
        formula_str=formula_str,
        method="lasso_v4",
        n_dict_atoms=n_raw,
        max_internal_nodes=max_internal_nodes,
        floor_detected=floor_detected,
        floor_alpha=best_alpha,
        floor_mse=best_mse_test,
        n_selected=len(selected_atoms),
        n_raw_atoms=n_raw,
        n_independent_atoms=n_indep,
    )
