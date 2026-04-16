"""
monogate.causal — EML trees as interpretable causal models.

Each node in an EML tree represents a causal mechanism: the exponential gate
mediates amplification and the log gate mediates compression.  This module
provides:

  - EMLCausalModel: fits an EML tree to (X, y) data and supports
    counterfactual ("do-calculus") queries on the discovered tree.
  - verify_causal_identity: wraps EMLProver to verify that a causal
    mechanism satisfies a given mathematical identity.
  - CausalResult: dataclass summarising a fitted causal model.

The counterfactual computation is structural: it replaces the input at a
specific variable index with an intervention value and re-evaluates the tree,
giving the predicted outcome under do(X_i = intervention).

Public API
----------
CausalResult           — dataclass for a fitted causal model
EMLCausalModel         — causal modelling class
verify_causal_identity — shortcut: EMLProver.prove on a causal identity string
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union

import numpy as np

__all__ = [
    "CausalResult",
    "EMLCausalModel",
    "verify_causal_identity",
]


# ── CausalResult ──────────────────────────────────────────────────────────────

@dataclass
class CausalResult:
    """Result of a fitted EML causal model.

    Attributes:
        formula:       EML formula string of the discovered causal mechanism.
        eml_nodes:     Number of EML (internal) nodes in the tree.
        r2_score:      Coefficient of determination (1 = perfect fit).
        mse:           Mean squared error on training data.
        n_samples:     Number of training samples.
        feature_names: Names of input features (if provided).
        notes:         Additional notes about the fit.
    """

    formula: str
    eml_nodes: int = 0
    r2_score: float = float("nan")
    mse: float = float("nan")
    n_samples: int = 0
    feature_names: List[str] = field(default_factory=list)
    notes: str = ""

    def __repr__(self) -> str:
        return (
            f"CausalResult(formula={self.formula!r}, "
            f"eml_nodes={self.eml_nodes}, "
            f"R²={self.r2_score:.4f})"
        )


# ── EMLCausalModel ────────────────────────────────────────────────────────────

class EMLCausalModel:
    """EML trees as interpretable causal models.

    Fits an EML expression tree to (X, y) observational data using
    EMLRegressor (symbolic regression), then supports:
      - Prediction: evaluate discovered causal mechanism on new inputs.
      - Counterfactual: predict outcome under do(X_j = value) intervention.
      - Identity verification: prove a causal identity via EMLProver.

    Args:
        max_nodes:     Maximum EML tree complexity.
        n_simulations: MCTS simulations per search step.
        seed:          Random seed.

    Example::

        import numpy as np
        from monogate.causal import EMLCausalModel

        rng = np.random.default_rng(0)
        T = rng.uniform(300, 800, 100)
        k = 1e6 * np.exp(-30000 / (8.314 * T))   # Arrhenius mechanism

        model = EMLCausalModel(max_nodes=3, seed=42)
        result = model.fit(T.reshape(-1, 1), k)
        print(result.formula)

        # Counterfactual: what if T were 500 K?
        cf = model.counterfactual(np.array([[400.0]]), intervention={0: 500.0})
        print(f"Counterfactual k at T=500K: {cf[0]:.4e}")
    """

    def __init__(
        self,
        max_nodes: int = 4,
        n_simulations: int = 500,
        seed: int = 42,
    ) -> None:
        self.max_nodes = max_nodes
        self.n_simulations = n_simulations
        self.seed = seed
        self._regressor: Optional[Any] = None
        self._result: Optional[CausalResult] = None

    # ── Public API ────────────────────────────────────────────────────────────

    def fit(
        self,
        X: "np.ndarray",
        y: "np.ndarray",
        feature_names: Optional[List[str]] = None,
    ) -> CausalResult:
        """Fit an EML causal mechanism to (X, y) observational data.

        Args:
            X:             Input array, shape (n_samples, n_features).
                           Currently supports 1-feature inputs (n_features=1).
            y:             Target array, shape (n_samples,).
            feature_names: Optional list of feature names for interpretability.

        Returns:
            :class:`CausalResult` with discovered formula and fit statistics.
        """
        from .sklearn_wrapper import EMLRegressor

        X_arr = np.asarray(X, dtype=float)
        if X_arr.ndim == 1:
            X_arr = X_arr.reshape(-1, 1)
        y_arr = np.asarray(y, dtype=float).ravel()

        reg = EMLRegressor(
            max_nodes=self.max_nodes,
            n_simulations=self.n_simulations,
            seed=self.seed,
        )
        reg.fit(X_arr, y_arr)
        self._regressor = reg

        y_pred = reg.predict(X_arr)
        ss_res = float(np.sum((y_arr - y_pred) ** 2))
        ss_tot = float(np.sum((y_arr - np.mean(y_arr)) ** 2))
        r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else float("nan")
        mse = float(np.mean((y_arr - y_pred) ** 2))

        names = feature_names or [f"x{i}" for i in range(X_arr.shape[1])]

        formula = reg.formula_ if hasattr(reg, "formula_") else str(reg)
        n_nodes = getattr(reg, "n_nodes_", 0)

        self._result = CausalResult(
            formula=formula,
            eml_nodes=n_nodes,
            r2_score=r2,
            mse=mse,
            n_samples=len(y_arr),
            feature_names=names,
            notes=f"Fitted EML causal model (max_nodes={self.max_nodes})",
        )
        return self._result

    def predict(self, X: "np.ndarray") -> "np.ndarray":
        """Predict outcomes using the fitted causal mechanism.

        Args:
            X: Input array, shape (n_samples, n_features).

        Returns:
            Predicted values, shape (n_samples,).

        Raises:
            RuntimeError: If fit() has not been called.
        """
        if self._regressor is None:
            raise RuntimeError("EMLCausalModel.fit() must be called before predict().")
        X_arr = np.asarray(X, dtype=float)
        if X_arr.ndim == 1:
            X_arr = X_arr.reshape(-1, 1)
        return self._regressor.predict(X_arr)

    def counterfactual(
        self,
        X: "np.ndarray",
        intervention: Dict[int, float],
    ) -> "np.ndarray":
        """Predict outcome under do-calculus intervention on feature j.

        Replaces feature j in X with the intervention value and evaluates
        the fitted causal mechanism.  This is a structural counterfactual:
        it directly substitutes the intervened value into the causal graph.

        Args:
            X:            Baseline input array, shape (n_samples, n_features).
            intervention: Dict mapping feature index → intervention value.
                          E.g. {0: 500.0} means do(X_0 = 500).

        Returns:
            Predicted outcomes under intervention, shape (n_samples,).

        Raises:
            RuntimeError: If fit() has not been called.
        """
        if self._regressor is None:
            raise RuntimeError("EMLCausalModel.fit() must be called before counterfactual().")

        X_arr = np.asarray(X, dtype=float).copy()
        if X_arr.ndim == 1:
            X_arr = X_arr.reshape(-1, 1)

        # Apply interventions (do-operator): override feature columns
        X_cf = X_arr.copy()
        for feature_idx, value in intervention.items():
            if feature_idx < X_cf.shape[1]:
                X_cf[:, feature_idx] = value

        return self._regressor.predict(X_cf)

    def summary(self) -> str:
        """Return a human-readable summary of the fitted causal model."""
        if self._result is None:
            return "EMLCausalModel (not fitted)"
        r = self._result
        lines = [
            "EMLCausalModel Summary",
            "=" * 40,
            f"Formula:    {r.formula}",
            f"EML nodes:  {r.eml_nodes}",
            f"R²:         {r.r2_score:.6f}",
            f"MSE:        {r.mse:.4e}",
            f"Samples:    {r.n_samples}",
            f"Features:   {', '.join(r.feature_names)}",
            f"Notes:      {r.notes}",
        ]
        return "\n".join(lines)


# ── verify_causal_identity ────────────────────────────────────────────────────

def verify_causal_identity(
    identity_str: str,
    n_simulations: int = 1000,
    verbose: bool = False,
) -> "Any":
    """Verify a causal identity using EMLProver.

    Shortcut: proves that the causal mechanism satisfies a mathematical
    identity string (e.g., 'exp(x) == exp(x)').

    Args:
        identity_str:  Mathematical identity to verify (e.g. 'exp(-x) == 1/exp(x)').
        n_simulations: Number of MCTS simulations for proof search.
        verbose:       If True, print proof details.

    Returns:
        :class:`ProofResult` with status and proof details.

    Example::

        from monogate.causal import verify_causal_identity

        # Verify the Arrhenius log-linear property
        result = verify_causal_identity("log(exp(x)) == x")
        print(result.status, result.proved())
    """
    from .prover import EMLProver

    prover = EMLProver(verbose=verbose)
    return prover.prove(identity_str, n_simulations=n_simulations)
