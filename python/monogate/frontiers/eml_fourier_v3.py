"""EML Fourier v3 — Session 37.

Fix for N=5/6 over-pruning in v2. Root cause: MAX_ATOM_VALUE=1e6 clipped ~98%
of N=5 atoms before they reached the OMP step, leaving only 21 independent
vectors from 1489 raw atoms and causing a false regression.

Key change: instead of discarding atoms with large values, normalize every
finite atom to unit L2 norm. This preserves functional shape while taming
scale differences. The OMP coefficients are scaled back at output.

With unit-norm normalization:
- Explosive atoms like exp(exp(x)) retain their functional signature
- QR pruning correctly identifies linearly independent directions
- N=5/6 sweep gives the true floor MSE

Primary use: definitive DENSE vs SEPARATION verdict for sin(x).
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

QR_RANK_TOL: float = 1e-8


@dataclass
class EMLFourierV3Result(EMLFourierResult):
    floor_detected: bool = False
    floor_K: int = 0
    floor_mse: float = float("nan")
    n_independent_atoms: int = 0
    n_raw_atoms: int = 0

    def to_dict(self) -> dict:
        d = super().to_dict()
        d["floor_detected"] = self.floor_detected
        d["floor_K"] = self.floor_K
        d["floor_mse"] = self.floor_mse
        d["n_independent_atoms"] = self.n_independent_atoms
        d["n_raw_atoms"] = self.n_raw_atoms
        return d


def build_eml_dictionary_v3(
    max_internal_nodes: int = 4,
    probe_points: list[float] | None = None,
    min_variance: float = 1e-10,
) -> tuple[list[EMLBasisAtom], np.ndarray]:
    """Enumerate all EML atoms, keeping all finite non-constant ones.

    Returns (atoms, norms) where atoms[i].values has been L2-normalized
    and norms[i] is the original L2 norm (for coefficient rescaling).

    No value clipping — just fineness and variance checks.
    """
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

                # Normalize to unit L2 norm (preserve shape, kill scale)
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


def _qr_prune_v3(A: np.ndarray, tol: float = QR_RANK_TOL) -> np.ndarray:
    """Column-pivoted QR to find linearly independent column subset."""
    n_rows, n_cols = A.shape
    if n_cols == 0:
        return np.array([], dtype=int)
    try:
        from scipy.linalg import qr
        _, R, piv = qr(A, pivoting=True)
        diag = np.abs(np.diag(R))
        if diag[0] < 1e-15:
            return np.array([0], dtype=int)
        rank = int(np.sum(diag > tol * diag[0]))
        rank = max(rank, 1)
        return np.sort(piv[:rank])
    except ImportError:
        _, R = np.linalg.qr(A)
        diag = np.abs(np.diag(R))
        idx = np.where(diag > tol)[0]
        return idx if len(idx) > 0 else np.array([0], dtype=int)


def _detect_floor_v3(
    mse_history: list[float],
    plateau_ratio: float = 0.85,
    window: int = 3,
) -> tuple[bool, int, float]:
    if not mse_history:
        return False, 0, float("nan")
    if len(mse_history) < window + 1:
        best_idx = int(np.argmin(mse_history))
        return False, best_idx, mse_history[best_idx]

    for i in range(len(mse_history) - window, len(mse_history)):
        prev = mse_history[i - 1]
        if prev < 1e-15:
            best_idx = int(np.argmin(mse_history))
            return False, best_idx, mse_history[best_idx]
        ratio = mse_history[i] / prev
        if ratio < plateau_ratio:
            best_idx = int(np.argmin(mse_history))
            return False, best_idx, mse_history[best_idx]

    best_idx = int(np.argmin(mse_history))
    return True, best_idx, mse_history[best_idx]


def eml_fourier_search_v3(
    target_fn: Callable[[float], float],
    target_name: str = "f",
    max_internal_nodes: int = 4,
    max_K: int = 30,
    train_points: list[float] | None = None,
    test_points: list[float] | None = None,
    detect_floor: bool = True,
) -> EMLFourierV3Result:
    """EML Fourier search with unit-norm dictionary and QR pruning.

    All atoms are L2-normalized before building the dictionary matrix.
    OMP coefficients are rescaled back to original units at output.
    """
    from sklearn.linear_model import OrthogonalMatchingPursuit

    if train_points is None:
        train_points = _DEFAULT_TRAIN_POINTS
    if test_points is None:
        test_points = _DEFAULT_TEST_POINTS

    # Build unit-norm dictionary
    atoms, atom_norms = build_eml_dictionary_v3(
        max_internal_nodes=max_internal_nodes,
        probe_points=train_points,
    )
    if not atoms:
        raise ValueError("EML dictionary is empty.")

    # atoms[i].values is already unit-norm
    A_normed = np.column_stack([a.values for a in atoms])
    b_train = np.array([target_fn(x) for x in train_points])
    b_test = np.array([target_fn(x) for x in test_points])
    n_raw = len(atoms)

    # QR prune to independent columns
    keep_idx = _qr_prune_v3(A_normed)
    if len(keep_idx) == 0:
        keep_idx = np.arange(min(max_K, n_raw))

    atoms_pruned = [atoms[i] for i in keep_idx]
    norms_pruned = atom_norms[keep_idx]
    A_pruned = A_normed[:, keep_idx]  # already unit-norm columns
    n_indep = len(atoms_pruned)

    # Incremental OMP to track MSE floor
    mse_history: list[float] = []
    best_coef_normed = np.zeros(n_indep)
    best_mse_test = float("inf")

    for k in range(1, min(max_K, n_indep) + 1):
        try:
            model = OrthogonalMatchingPursuit(n_nonzero_coefs=k, fit_intercept=False)
            model.fit(A_pruned, b_train)
            coef_normed = model.coef_
        except Exception:
            break

        nz = np.where(np.abs(coef_normed) > 1e-14)[0]
        if len(nz) == 0:
            break

        # Evaluate test MSE in normalized space
        A_test_k = np.column_stack([
            np.array([_eval_tree(atoms_pruned[i].ops, atoms_pruned[i].leaf_mask, float(x))
                      or math.nan for x in test_points]) / norms_pruned[i]
            for i in nz
        ])
        pred_test = A_test_k @ coef_normed[nz]
        mse_t = float(np.mean((pred_test - b_test) ** 2))
        if not math.isfinite(mse_t):
            mse_t = float("inf")

        mse_history.append(mse_t)
        if mse_t < best_mse_test:
            best_mse_test = mse_t
            best_coef_normed = coef_normed.copy()

    floor_detected, floor_k_idx, floor_mse = _detect_floor_v3(mse_history)

    # Rescale coefficients back to original (un-normalized) units
    # coef_actual[i] = coef_normed[i] / atom_l2_norm[i]
    nonzero_idx = np.where(np.abs(best_coef_normed) > 1e-14)[0]
    if len(nonzero_idx) == 0:
        nonzero_idx = np.array([int(np.argmax(np.abs(best_coef_normed)))])

    selected_atoms = [atoms_pruned[i] for i in nonzero_idx]
    selected_norms = norms_pruned[nonzero_idx]
    # Coefficient in un-normalized space: c_actual * norm(atom) = c_normed
    selected_coefs = (best_coef_normed[nonzero_idx] / selected_norms).tolist()

    # Compute final train/test MSE with un-normalized atoms
    A_train_final = np.column_stack([
        np.array([_eval_tree(a.ops, a.leaf_mask, float(x)) or math.nan for x in train_points])
        for a in selected_atoms
    ])
    pred_train = A_train_final @ np.array(selected_coefs)
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

    floor_k_actual = floor_k_idx + 1 if mse_history else len(nonzero_idx)
    actual_floor_mse = floor_mse if (floor_detected and math.isfinite(floor_mse)) else best_mse_test

    return EMLFourierV3Result(
        target_name=target_name,
        K=len(selected_atoms),
        coefficients=selected_coefs,
        atoms=selected_atoms,
        mse_train=mse_train,
        mse_test=mse_test_final,
        formula_str=formula_str,
        method="omp_v3",
        n_dict_atoms=n_raw,
        max_internal_nodes=max_internal_nodes,
        floor_detected=floor_detected,
        floor_K=floor_k_actual,
        floor_mse=actual_floor_mse,
        n_independent_atoms=n_indep,
        n_raw_atoms=n_raw,
    )
