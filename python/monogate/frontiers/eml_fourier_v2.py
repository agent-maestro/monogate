"""EML Fourier v2 — Session 36.

Improvements over v1:
- Value clipping (MAX_ATOM_VALUE=1e6) to tame explosive N>=4 atoms
- QR column pruning to keep only linearly independent basis vectors
- Floor detection: tracks MSE plateau across K values
- Monotone MSE tracking: reports best K seen, not last K

Primary use: sin floor asymptotics — sweep N=1..6 to answer DENSE vs SEPARATION.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Callable

import numpy as np

from monogate.frontiers.eml_fourier import (
    EMLBasisAtom,
    EMLFourierResult,
    _generate_shapes,
    _eval_tree,
    _format_tree,
    _DEFAULT_TRAIN_POINTS,
    _DEFAULT_TEST_POINTS,
)

MAX_ATOM_VALUE: float = 1e6
QR_RANK_TOL: float = 1e-10


@dataclass
class EMLFourierV2Result(EMLFourierResult):
    floor_detected: bool = False
    floor_K: int = 0
    floor_mse: float = float("nan")
    n_independent_atoms: int = 0

    def to_dict(self) -> dict:
        d = super().to_dict()
        d["floor_detected"] = self.floor_detected
        d["floor_K"] = self.floor_K
        d["floor_mse"] = self.floor_mse
        d["n_independent_atoms"] = self.n_independent_atoms
        return d


def build_eml_dictionary_v2(
    max_internal_nodes: int = 4,
    probe_points: list[float] | None = None,
    min_variance: float = 1e-10,
    max_atom_value: float = MAX_ATOM_VALUE,
) -> list[EMLBasisAtom]:
    """Like v1 but clips atoms whose values exceed max_atom_value."""
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
                    continue
                vals_raw = [_eval_tree(ops, mask, float(xv)) for xv in xs]
                if any(v is None for v in vals_raw):
                    continue
                vals_f = np.array(vals_raw, dtype=np.float64)
                if not np.all(np.isfinite(vals_f)):
                    continue
                if np.any(np.abs(vals_f) > max_atom_value):
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


def _qr_prune(A: np.ndarray, tol: float = QR_RANK_TOL) -> np.ndarray:
    """Return column indices of a linearly independent subset of A's columns."""
    n_rows, n_cols = A.shape
    if n_cols == 0:
        return np.array([], dtype=int)

    # Column-pivoted QR: columns sorted by decreasing contribution
    try:
        from scipy.linalg import qr
        _, R, piv = qr(A, pivoting=True)
        diag = np.abs(np.diag(R))
        rank = int(np.sum(diag > tol * diag[0] if diag[0] > 0 else diag > tol))
        return np.sort(piv[:rank])
    except ImportError:
        # Fallback: greedy norm-based selection
        Q, R = np.linalg.qr(A)
        diag = np.abs(np.diag(R))
        return np.where(diag > tol)[0]


def _detect_floor(
    mse_history: list[float],
    plateau_ratio: float = 0.9,
    window: int = 3,
) -> tuple[bool, int, float]:
    """Return (floor_detected, floor_K_index, floor_mse).

    Floor detected when last `window` steps all have ratio >= plateau_ratio.
    """
    if len(mse_history) < window + 1:
        return False, len(mse_history) - 1, mse_history[-1] if mse_history else float("nan")

    for i in range(len(mse_history) - window, len(mse_history)):
        if mse_history[i - 1] < 1e-15:
            return False, i - 1, mse_history[i - 1]
        ratio = mse_history[i] / mse_history[i - 1]
        if ratio < plateau_ratio:
            return False, len(mse_history) - 1, mse_history[-1]

    best_idx = int(np.argmin(mse_history))
    return True, best_idx, mse_history[best_idx]


def eml_fourier_search_v2(
    target_fn: Callable[[float], float],
    target_name: str = "f",
    max_internal_nodes: int = 4,
    max_K: int = 20,
    method: str = "omp",
    train_points: list[float] | None = None,
    test_points: list[float] | None = None,
    detect_floor: bool = True,
    max_atom_value: float = MAX_ATOM_VALUE,
) -> EMLFourierV2Result:
    """Sparse EML Fourier decomposition with QR pruning and floor detection."""
    from sklearn.linear_model import OrthogonalMatchingPursuit, Lasso

    if train_points is None:
        train_points = _DEFAULT_TRAIN_POINTS
    if test_points is None:
        test_points = _DEFAULT_TEST_POINTS

    atoms = build_eml_dictionary_v2(
        max_internal_nodes=max_internal_nodes,
        probe_points=train_points,
        max_atom_value=max_atom_value,
    )
    if not atoms:
        raise ValueError("EML dictionary is empty — all atoms were clipped or trivial.")

    A_full = np.column_stack([a.values for a in atoms])
    b_train = np.array([target_fn(x) for x in train_points])
    b_test = np.array([target_fn(x) for x in test_points])

    # QR prune to independent columns
    keep_idx = _qr_prune(A_full)
    if len(keep_idx) == 0:
        keep_idx = np.arange(min(max_K, len(atoms)))

    atoms_pruned = [atoms[i] for i in keep_idx]
    A_train = A_full[:, keep_idx]
    n_independent = len(atoms_pruned)

    # Normalize columns
    col_norms = np.linalg.norm(A_train, axis=0)
    col_norms[col_norms < 1e-12] = 1.0
    A_norm = A_train / col_norms

    # Incremental OMP to track MSE at each K (for floor detection)
    if detect_floor and method == "omp":
        mse_history: list[float] = []
        best_coef: np.ndarray = np.zeros(n_independent)
        best_mse_test = float("inf")

        for k in range(1, min(max_K, n_independent) + 1):
            try:
                model = OrthogonalMatchingPursuit(n_nonzero_coefs=k, fit_intercept=False)
                model.fit(A_norm, b_train)
                coef_norm = model.coef_
            except Exception:
                break

            coef = coef_norm / col_norms
            nz = np.where(np.abs(coef) > 1e-12)[0]
            if len(nz) == 0:
                break

            # Evaluate test MSE
            A_test_k = np.column_stack([
                np.array([_eval_tree(atoms_pruned[i].ops, atoms_pruned[i].leaf_mask, float(x))
                          or math.nan for x in test_points])
                for i in nz
            ])
            pred_test = A_test_k @ coef[nz]
            mse_t = float(np.mean((pred_test - b_test) ** 2))
            if not math.isfinite(mse_t):
                mse_t = float("inf")

            mse_history.append(mse_t)
            if mse_t < best_mse_test:
                best_mse_test = mse_t
                best_coef = coef.copy()

        floor_detected, floor_k_idx, floor_mse = _detect_floor(mse_history) if mse_history else (False, 0, float("nan"))
        coef_final = best_coef
    else:
        # Single run
        eff_K = min(max_K, n_independent)
        if method == "omp":
            model = OrthogonalMatchingPursuit(n_nonzero_coefs=eff_K, fit_intercept=False)
            model.fit(A_norm, b_train)
            coef_norm = model.coef_
        else:
            model = Lasso(alpha=1e-4, fit_intercept=False, max_iter=10000)
            model.fit(A_norm, b_train)
            coef_norm = model.coef_

        coef_final = coef_norm / col_norms
        floor_detected = False
        floor_k_idx = eff_K - 1
        floor_mse = float("nan")
        mse_history = []

    # Build final result from best coef
    nonzero_idx = np.where(np.abs(coef_final) > 1e-12)[0]
    if len(nonzero_idx) == 0:
        nonzero_idx = np.array([int(np.argmax(np.abs(coef_final)))])

    selected_atoms = [atoms_pruned[i] for i in nonzero_idx]
    selected_coefs = coef_final[nonzero_idx].tolist()
    K_final = len(selected_atoms)

    pred_train = A_train[:, nonzero_idx] @ np.array(selected_coefs)
    mse_train = float(np.mean((pred_train - b_train) ** 2))

    A_test_final = np.column_stack([
        np.array([_eval_tree(a.ops, a.leaf_mask, float(x)) or math.nan for x in test_points])
        for a in selected_atoms
    ])
    pred_test_final = A_test_final @ np.array(selected_coefs)
    mse_test_final = float(np.mean((pred_test_final - b_test) ** 2))

    formula_parts = []
    for c, a in zip(selected_coefs, selected_atoms):
        sign = "+" if c >= 0 else "-"
        formula_parts.append(f"{sign} {abs(c):.6g}*{a.formula}")
    formula_str = " ".join(formula_parts).lstrip("+ ").strip()

    floor_k_actual = floor_k_idx + 1 if mse_history else K_final

    return EMLFourierV2Result(
        target_name=target_name,
        K=K_final,
        coefficients=selected_coefs,
        atoms=selected_atoms,
        mse_train=mse_train,
        mse_test=mse_test_final,
        formula_str=formula_str,
        method=method,
        n_dict_atoms=len(atoms),
        max_internal_nodes=max_internal_nodes,
        floor_detected=floor_detected,
        floor_K=floor_k_actual,
        floor_mse=floor_mse if floor_detected else mse_test_final,
        n_independent_atoms=n_independent,
    )
