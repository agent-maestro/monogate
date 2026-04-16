"""
monogate.chemistry — Reaction rate laws as EML expressions.

Chemical kinetics equations (Arrhenius, Michaelis-Menten, Hill) are naturally
expressed as EML trees.  The Arrhenius equation k = A·exp(-Ea/RT) is a
1-node EML expression: eml(-Ea/RT, 1/A) = exp(-Ea/RT) - ln(1/A) = k - ln(1/A).

This module provides:
  - A catalog of reaction laws with their EML representations.
  - `fit_reaction_law`: symbolic regression to discover rate laws from data.
  - `arrhenius_fit`: direct least-squares fit of the Arrhenius parameters.

Public API
----------
REACTION_CATALOG       — dict of named reaction law specifications
fit_reaction_law       — EMLRegressor-based symbolic regression on (X, y)
arrhenius_fit          — direct Arrhenius parameter estimation
ReactionLaw            — dataclass for a discovered or catalog reaction law
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

__all__ = [
    "REACTION_CATALOG",
    "fit_reaction_law",
    "arrhenius_fit",
    "ReactionLaw",
]

# ── Reaction catalog ──────────────────────────────────────────────────────────

#: Catalog of named reaction rate laws with EML descriptions.
REACTION_CATALOG: Dict[str, Dict[str, Any]] = {
    "arrhenius": {
        "name": "Arrhenius equation",
        "formula": "A * exp(-Ea / (R * T))",
        "eml_nodes": 1,
        "variables": ["T"],
        "parameters": ["A", "Ea", "R"],
        "domain": (200.0, 1000.0),  # Temperature in Kelvin
        "notes": (
            "k(T) = A * exp(-Ea/RT). One EML node: "
            "eml(-Ea/(RT), 1/A) = A*exp(-Ea/RT) after rearranging."
        ),
    },
    "michaelis_menten": {
        "name": "Michaelis-Menten kinetics",
        "formula": "Vmax * S / (Km + S)",
        "eml_nodes": 3,
        "variables": ["S"],
        "parameters": ["Vmax", "Km"],
        "domain": (0.0, 100.0),  # Substrate concentration [mM]
        "notes": (
            "v(S) = Vmax*S/(Km+S). Expressed via EML: "
            "Vmax/(1 + Km/S) requires log and exp composition."
        ),
    },
    "hill_equation": {
        "name": "Hill equation (cooperative binding)",
        "formula": "Vmax * S**n / (Km**n + S**n)",
        "eml_nodes": 5,
        "variables": ["S"],
        "parameters": ["Vmax", "Km", "n"],
        "domain": (0.0, 50.0),  # Substrate concentration [mM]
        "notes": (
            "v(S) = Vmax * S^n / (Km^n + S^n). Hill coefficient n controls cooperativity. "
            "n=1 reduces to Michaelis-Menten."
        ),
    },
    "eyring_rate": {
        "name": "Eyring (transition state) theory",
        "formula": "(kB * T / h) * exp(-dG / (R * T))",
        "eml_nodes": 2,
        "variables": ["T"],
        "parameters": ["kB", "h", "dG", "R"],
        "domain": (200.0, 800.0),  # Temperature in Kelvin
        "notes": (
            "k(T) = (kB*T/h) * exp(-ΔG/RT). Two EML nodes: "
            "temperature-dependent prefactor × Arrhenius-like exponential."
        ),
    },
    "bimolecular": {
        "name": "Bimolecular reaction rate",
        "formula": "k * A * B",
        "eml_nodes": 2,
        "variables": ["A", "B"],
        "parameters": ["k"],
        "domain": (0.0, 10.0),
        "notes": (
            "r = k[A][B]. Linear in concentrations; EML representation "
            "encodes the rate constant k via exp."
        ),
    },
    "competitive_inhibition": {
        "name": "Competitive inhibition",
        "formula": "Vmax * S / (Km * (1 + I/Ki) + S)",
        "eml_nodes": 4,
        "variables": ["S", "I"],
        "parameters": ["Vmax", "Km", "Ki"],
        "domain": (0.0, 100.0),
        "notes": (
            "v(S, I) = Vmax*S / (Km*(1+I/Ki)+S). Inhibitor I reduces "
            "effective Km by factor (1+I/Ki)."
        ),
    },
}


# ── ReactionLaw dataclass ─────────────────────────────────────────────────────

@dataclass
class ReactionLaw:
    """A discovered or catalog reaction rate law.

    Attributes:
        name:         Human-readable name.
        formula:      Symbolic formula string.
        eml_formula:  EML tree formula string (from EMLRegressor).
        eml_nodes:    Number of EML (internal) nodes.
        r2_score:     R² goodness-of-fit (1.0 = perfect).
        mse:          Mean squared error on training data.
        parameters:   Fitted parameter values (if applicable).
        notes:        Additional notes.
    """

    name: str
    formula: str
    eml_formula: str = ""
    eml_nodes: int = 0
    r2_score: float = float("nan")
    mse: float = float("nan")
    parameters: Dict[str, float] = field(default_factory=dict)
    notes: str = ""


# ── fit_reaction_law ──────────────────────────────────────────────────────────

def fit_reaction_law(
    X: "np.ndarray",
    y: "np.ndarray",
    max_nodes: int = 5,
    name: str = "discovered",
    seed: int = 42,
    n_simulations: int = 500,
) -> ReactionLaw:
    """Discover a reaction rate law from (X, y) data using EMLRegressor.

    Runs symbolic regression over the EML grammar to find the best-fitting
    expression tree for the provided experimental data.

    Args:
        X:             Input array of shape (n_samples, 1) or (n_samples,).
                       Typically temperature [K] or substrate concentration [mM].
        y:             Target rate values, shape (n_samples,).
        max_nodes:     Maximum EML tree nodes to search (default: 5).
        name:          Name for the discovered law (default: 'discovered').
        seed:          Random seed for reproducibility.
        n_simulations: MCTS simulations per node count.

    Returns:
        :class:`ReactionLaw` with best EML formula and fit statistics.

    Example::

        import numpy as np
        from monogate.chemistry import fit_reaction_law

        # Arrhenius: k = A * exp(-Ea / R / T)
        R = 8.314
        T = np.linspace(300, 1000, 50)
        k = 1e10 * np.exp(-50000 / (R * T))

        law = fit_reaction_law(T.reshape(-1, 1), k, max_nodes=3, seed=42)
        print(law.eml_formula, f"R²={law.r2_score:.4f}")
    """
    from .sklearn_wrapper import EMLRegressor

    X_arr = np.asarray(X).reshape(-1, 1) if np.asarray(X).ndim == 1 else np.asarray(X)
    y_arr = np.asarray(y).ravel()

    reg = EMLRegressor(max_nodes=max_nodes, n_simulations=n_simulations, seed=seed)
    reg.fit(X_arr, y_arr)

    y_pred = reg.predict(X_arr)
    ss_res = float(np.sum((y_arr - y_pred) ** 2))
    ss_tot = float(np.sum((y_arr - np.mean(y_arr)) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else float("nan")
    mse = float(np.mean((y_arr - y_pred) ** 2))

    return ReactionLaw(
        name=name,
        formula=reg.formula_ if hasattr(reg, "formula_") else str(reg),
        eml_formula=reg.formula_ if hasattr(reg, "formula_") else "",
        eml_nodes=getattr(reg, "n_nodes_", 0),
        r2_score=r2,
        mse=mse,
        notes=f"Fit via EMLRegressor(max_nodes={max_nodes}, seed={seed})",
    )


# ── arrhenius_fit ─────────────────────────────────────────────────────────────

def arrhenius_fit(
    T: "np.ndarray",
    k: "np.ndarray",
) -> Tuple[float, float, float]:
    """Fit Arrhenius parameters A and Ea from (T, k) data.

    Uses the linearized form: ln(k) = ln(A) - Ea/(R*T).
    Fits via ordinary least squares on (1/T, ln(k)).

    Args:
        T: Temperature values in Kelvin, shape (n,).
        k: Rate constants (must be strictly positive), shape (n,).

    Returns:
        Tuple (A, Ea, R2) where:
          - A: Pre-exponential factor.
          - Ea: Activation energy [J/mol].
          - R2: Coefficient of determination for the linear fit.

    Raises:
        ValueError: If any k values are non-positive.

    Example::

        import numpy as np
        from monogate.chemistry import arrhenius_fit

        R = 8.314
        T = np.linspace(300, 800, 30)
        k = 1e8 * np.exp(-40000 / (R * T))

        A, Ea, r2 = arrhenius_fit(T, k)
        print(f"A={A:.3e}, Ea={Ea:.1f} J/mol, R²={r2:.6f}")
    """
    R_gas = 8.314472  # J/(mol·K)

    T_arr = np.asarray(T, dtype=float).ravel()
    k_arr = np.asarray(k, dtype=float).ravel()

    if np.any(k_arr <= 0):
        raise ValueError("arrhenius_fit: all rate constants k must be strictly positive.")

    inv_T = 1.0 / T_arr
    ln_k = np.log(k_arr)

    # Linear regression: ln(k) = b0 + b1 * (1/T)
    # b0 = ln(A), b1 = -Ea/R
    A_mat = np.column_stack([np.ones_like(inv_T), inv_T])
    coeffs, _, _, _ = np.linalg.lstsq(A_mat, ln_k, rcond=None)
    ln_A, neg_Ea_over_R = coeffs

    A_fit = math.exp(ln_A)
    Ea_fit = -neg_Ea_over_R * R_gas

    # R² of the linear fit
    ln_k_pred = ln_A + neg_Ea_over_R * inv_T
    ss_res = float(np.sum((ln_k - ln_k_pred) ** 2))
    ss_tot = float(np.sum((ln_k - np.mean(ln_k)) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else float("nan")

    return A_fit, Ea_fit, r2
