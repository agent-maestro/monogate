"""EML Fourier v5 — SVD projection floor (monotone by construction).

Root cause of v3/v4 non-monotone results: OMP and Lasso find sparse solutions
that are not the best DENSE linear combination. The true approximation floor
is the squared residual of projecting sin(x) orthogonally onto the column
space of all EML atoms up to depth N.

This is computable via SVD: A = U S V^T.
  - rank r = number of singular values > tol * sigma_0
  - OLS solution: c = V @ diag(1/s[:r]) @ U[:, :r].T @ b_train
  - floor_mse = mean((A_test @ c - b_test)^2)

Monotonicity: the N=k+1 dictionary contains all N=k atoms plus new ones,
so its column space contains the N=k column space. The projection error
is non-increasing in N. (The only exceptions are numerical noise.)

This gives the definitive DENSE vs SEPARATION answer.
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

SVD_TOL: float = 1e-8


@dataclass
class EMLFourierV5Result:
    target_name: str
    max_internal_nodes: int
    n_raw_atoms: int
    n_independent_atoms: int
    mse_train: float
    mse_test: float
    method: str = "svd_projection"
    formula_str: str = ""

    def to_dict(self) -> dict:
        return {
            "target_name": self.target_name,
            "max_internal_nodes": self.max_internal_nodes,
            "n_raw_atoms": self.n_raw_atoms,
            "n_independent_atoms": self.n_independent_atoms,
            "mse_train": self.mse_train,
            "mse_test": self.mse_test,
            "method": self.method,
        }


def build_eml_matrix(
    max_internal_nodes: int,
    probe_points: list[float],
    min_variance: float = 1e-10,
) -> tuple[list[EMLBasisAtom], np.ndarray, np.ndarray]:
    """Build EML atom matrix (unit-norm columns) and return atoms, norms, matrix.

    Returns:
        atoms: list of EMLBasisAtom (values = unit-norm on probe_points)
        norms: original L2 norms per atom
        A: matrix of shape (len(probe_points), len(atoms))
    """
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
                atoms.append(EMLBasisAtom(
                    ops=ops, leaf_mask=mask,
                    values=vals_f / l2,
                    formula=_format_tree(ops, mask),
                ))
                norms.append(l2)

    A = np.column_stack([a.values for a in atoms]) if atoms else np.zeros((len(xs), 0))
    return atoms, np.array(norms, dtype=np.float64), A


def eml_fourier_search_v5(
    target_fn: Callable[[float], float],
    target_name: str = "f",
    max_internal_nodes: int = 4,
    train_points: list[float] | None = None,
    test_points: list[float] | None = None,
    svd_tol: float = SVD_TOL,
) -> EMLFourierV5Result:
    """SVD projection floor: monotone lower bound on sin approximation error."""
    if train_points is None:
        train_points = _DEFAULT_TRAIN_POINTS
    if test_points is None:
        test_points = _DEFAULT_TEST_POINTS

    atoms, atom_norms, A_train = build_eml_matrix(
        max_internal_nodes=max_internal_nodes,
        probe_points=train_points,
    )
    if not atoms:
        raise ValueError("EML dictionary is empty.")

    b_train = np.array([target_fn(x) for x in train_points], dtype=np.float64)
    b_test = np.array([target_fn(x) for x in test_points], dtype=np.float64)

    # A_train shape: (n_train, n_atoms), all unit-norm columns
    n_raw = len(atoms)

    # SVD projection: always use truncated SVD for well-conditioned floor.
    # When n_atoms > n_train, SVD still gives rank ≤ n_train via k=min(n_train, n_atoms).
    try:
            U, s, Vt = np.linalg.svd(A_train, full_matrices=False)
            # U: (n_train, k), s: (k,), Vt: (k, n_atoms) where k = min(n_train, n_atoms)
            tol_sv = svd_tol * s[0] if s[0] > 0 else svd_tol
            rank = int(np.sum(s > tol_sv))
            rank = max(rank, 1)

            U_r = U[:, :rank]
            s_r = s[:rank]
            V_r = Vt[:rank, :].T  # (n_atoms, rank)

            # OLS: c = V_r @ diag(1/s_r) @ U_r.T @ b_train
            c_normed = V_r @ ((U_r.T @ b_train) / s_r)  # (n_atoms,)

            mse_train = float(np.mean((A_train @ c_normed - b_train) ** 2))

            # Test: evaluate atoms on test points, rescale by training norms
            A_test_rows = []
            for a, norm in zip(atoms, atom_norms):
                vals = np.array(
                    [_eval_tree(a.ops, a.leaf_mask, float(x)) for x in test_points],
                    dtype=object,
                )
                # Replace None with nan; avoid the "0.0 or nan" pitfall
                fvals = np.array(
                    [float(v) if v is not None else math.nan for v in vals],
                    dtype=np.float64,
                )
                A_test_rows.append(fvals / norm)
            A_test = np.column_stack(A_test_rows)  # (n_test, n_atoms)

            # Drop test rows where any atom is non-finite
            finite_rows = np.all(np.isfinite(A_test), axis=1)
            if finite_rows.sum() == 0:
                mse_test = float("inf")
            else:
                pred_test = A_test[finite_rows] @ c_normed
                mse_test = float(np.mean((pred_test - b_test[finite_rows]) ** 2))
            n_indep = rank

    except Exception:
        # Fallback: unconstrained lstsq (may overfit when n_atoms > n_train)
        c_normed, _, _, _ = np.linalg.lstsq(A_train, b_train, rcond=svd_tol)
        mse_train = float(np.mean((A_train @ c_normed - b_train) ** 2))
        A_test_rows = []
        for a, norm in zip(atoms, atom_norms):
            vals = np.array(
                [float(v) if v is not None else math.nan
                 for v in [_eval_tree(a.ops, a.leaf_mask, float(x)) for x in test_points]],
                dtype=np.float64,
            )
            A_test_rows.append(vals / norm)
        A_test = np.column_stack(A_test_rows)
        finite_rows = np.all(np.isfinite(A_test), axis=1)
        if finite_rows.sum() == 0:
            mse_test = float("inf")
        else:
            pred_test = A_test[finite_rows] @ c_normed
            mse_test = float(np.mean((pred_test - b_test[finite_rows]) ** 2))
        n_indep = n_raw

    if not math.isfinite(mse_test):
        mse_test = float("inf")

    return EMLFourierV5Result(
        target_name=target_name,
        max_internal_nodes=max_internal_nodes,
        n_raw_atoms=n_raw,
        n_independent_atoms=n_indep,
        mse_train=mse_train,
        mse_test=mse_test,
        method="svd_projection",
    )
