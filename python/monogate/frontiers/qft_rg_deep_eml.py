"""
Session 84 — QFT Interacting Deep: Wilson RG, Fixed Points & Universality Classes

Wilson's renormalization group: integrating out high-energy modes → effective field theory.
Fixed points of the RG flow classify universality classes. EML depth of RG trajectories,
fixed-point operators, and critical exponents.

Key theorem: The Wilson-Fisher fixed point in φ⁴ theory in d=4-ε dimensions has critical
exponent ν = 1/2 + ε/12 + O(ε²) — EML-2 (rational + polynomial in ε). The approach to
the fixed point is EML-1 (exponential in RG time t = ln μ).
"""

from __future__ import annotations
import math, json
from dataclasses import dataclass, field
from typing import Callable


EML_INF = float("inf")


@dataclass
class WilsonRGFlow:
    """
    Wilson RG: integrate out modes with Λ/s < |k| < Λ.

    Beta function: dg/dt = β(g) where t = ln(s) is RG time.
    Fixed points: β(g*) = 0.

    EML structure:
    - RG time t = ln(s): EML-2 (logarithm)
    - Gaussian fixed point g* = 0: EML-0 (trivial)
    - Wilson-Fisher fixed point g* = ε/6 + O(ε²) in d=4-ε: EML-1 (linear in ε = EML-0 shift → EML-1 structure via exp)
    - Approach to fixed point: g(t) = g* + (g₀-g*)·exp(-yt): EML-1 decay
    - Critical exponent η = ε²/54 + O(ε³): EML-2 (polynomial in ε)
    """
    d: float = 4.0  # Spacetime dimension
    epsilon: float = 0.01  # d = 4 - ε

    def __post_init__(self) -> None:
        self.epsilon = 4.0 - self.d

    def gaussian_fixed_point(self) -> dict:
        return {
            "name": "Gaussian (free) fixed point",
            "g_star": 0.0,
            "eml_depth": 0,
            "stability": "unstable in d<4, marginal in d=4",
            "universality_class": "mean-field / free field",
        }

    def wilson_fisher_fixed_point(self) -> dict:
        eps = self.epsilon
        g_star = eps / 6 + eps**2 / 36 + 0.0  # leading + subleading
        # Anomalous dimension η = ε²/54 + O(ε³)
        eta = eps**2 / 54
        # Correlation length exponent ν = 1/2 + ε/12 + O(ε²)
        nu = 0.5 + eps / 12
        # Scaling exponent y = 2 - η ≈ 2
        y = 2 - eta
        return {
            "name": "Wilson-Fisher fixed point",
            "dimension": round(self.d, 4),
            "epsilon": round(eps, 4),
            "g_star": round(g_star, 6),
            "critical_exponents": {
                "nu": round(nu, 6),
                "eta": round(eta, 8),
                "gamma": round(nu * (2 - eta), 6),
                "beta_exponent": round(nu * self.d - 2 * nu, 6),
            },
            "eml_depth": 2,
            "eml_reason": "g* = ε/6: rational in ε = EML-2; η = ε²/54 = polynomial = EML-2",
        }

    def rg_trajectory(self, g0: float, n_steps: int = 20) -> list[dict]:
        """Euler integration of dg/dt = β(g) = -εg + 6g² (φ⁴ beta function)."""
        eps = self.epsilon
        g = g0
        dt = 0.5
        trajectory = []
        for i in range(n_steps):
            beta = -eps * g + 6 * g**2
            g_new = g - beta * dt
            trajectory.append({
                "t": round(i * dt, 2),
                "g": round(g, 6),
                "beta": round(beta, 8),
            })
            g = g_new
        return trajectory

    def to_dict(self) -> dict:
        return {
            "gaussian_fp": self.gaussian_fixed_point(),
            "wilson_fisher_fp": self.wilson_fisher_fixed_point(),
            "rg_trajectory_g0_0.3": self.rg_trajectory(0.3, 15),
            "eml_rg_time": "t = ln(s): EML-2 logarithm is the RG clock",
            "eml_approach": "g(t) → g* exponentially → EML-1 decay toward fixed point",
        }


@dataclass
class UniversalityClass:
    """
    Universality class: all systems in the same class share the same critical exponents.

    EML classification of universality classes:
    - Gaussian (mean-field): EML-0 (free theory, no interactions)
    - Ising (d=2): EML-3 (exact solution via spinors, involves sin/cos conformal blocks)
    - 3D Ising: EML-∞ (no exact solution; critical exponents only known numerically/CFT bootstrap)
    - XY (d=2): EML-3 (Kosterlitz-Thouless transition via exp(-c/√(T-T_c)) = EML-1 in singular part)
    - O(N) vector: EML-2 (large-N solvable; N→∞ gives exact EML-2 results)
    """
    name: str
    dimension: float
    order_parameter: str
    symmetry: str
    nu: float
    eta: float
    eml_depth: float
    eml_reason: str

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "dimension": self.dimension,
            "order_parameter": self.order_parameter,
            "symmetry": self.symmetry,
            "critical_exponents": {
                "nu": self.nu,
                "eta": self.eta,
                "gamma": round(self.nu * (2 - self.eta), 4),
            },
            "eml_depth": "∞" if self.eml_depth == EML_INF else self.eml_depth,
            "eml_reason": self.eml_reason,
        }


UNIVERSALITY_CLASSES = [
    UniversalityClass(
        "Mean-field / Landau", 4.0, "scalar φ", "Z₂",
        0.5, 0.0, 0,
        "Free Gaussian theory: no interactions, EML-0 fixed point"
    ),
    UniversalityClass(
        "2D Ising (exact)", 2.0, "spin σ", "Z₂",
        1.0, 0.25, 3,
        "Onsager solution via spinors: critical correlators = EML-3 (conformal blocks with sin/cos)"
    ),
    UniversalityClass(
        "3D Ising (CFT bootstrap)", 3.0, "scalar φ", "Z₂",
        0.6299, 0.0363, EML_INF,
        "No closed form; bootstrap gives ν≈0.6299 numerically → EML-∞ (no EML-finite formula known)"
    ),
    UniversalityClass(
        "2D XY / Kosterlitz-Thouless", 2.0, "phase θ", "U(1)",
        float("inf"), 0.25, 3,
        "KT transition: correlation length ξ ~ exp(c/√(T-T_KT)) = EML-1 singular behavior; η=1/4 at T_KT"
    ),
    UniversalityClass(
        "O(N) large-N", 3.0, "N-vector φ", "O(N)",
        round(1 / (d := 3 - 2) if False else 1.0, 4), 0.0, 2,
        "Large-N solvable: ν = 1/(d-2) in 2<d<4 → rational → EML-2"
    ),
    UniversalityClass(
        "Wilson-Fisher (d=4-ε)", 3.0, "scalar φ⁴", "Z₂",
        round(0.5 + 1 / 12, 4), round(1 / 54, 6), 2,
        "ε-expansion: g*=ε/6, ν=1/2+ε/12, η=ε²/54 — polynomials in ε = EML-2"
    ),
]


@dataclass
class OperatorProductExpansion:
    """
    OPE: φ(x)·φ(y) = Σ_k C_k(x-y) · O_k(y)

    EML structure of OPE coefficients:
    - Free field: C_k(x-y) = |x-y|^{-2Δ_φ+Δ_k}: EML-2 (power law)
    - Interacting (CFT): C_k(x-y) = C_k · |x-y|^{Δ_k-2Δ_φ} · [1 + anomalous]: EML-2 leading, EML-∞ full
    - OPE convergence: exponential in |x-y| → EML-1

    Key: the EML depth of a CFT is determined by whether the spectrum of scaling dimensions
    is algebraically determined (EML-2) or only numerically accessible (EML-∞).
    """

    @staticmethod
    def ope_coefficient_eml(theory: str, operator: str) -> dict:
        table = {
            "free_scalar_propagator": {
                "theory": "Free scalar",
                "operator": "unit",
                "C(r)": "r^{-2Δ}",
                "eml": 2,
                "reason": "Power law: EML-2 (rational exponent)",
            },
            "ising_spin_spin": {
                "theory": "2D Ising",
                "operator": "σ×σ → 1+ε",
                "C(r)": "r^{-1/4} (exact)",
                "eml": 3,
                "reason": "Onsager: Δ_σ=1/8, exact via spinors → EML-3",
            },
            "3d_ising_ope": {
                "theory": "3D Ising",
                "operator": "σ×σ → 1+ε+...",
                "C(r)": "r^{-2Δ_σ} with Δ_σ≈0.5182",
                "eml": EML_INF,
                "reason": "Δ_σ known only from bootstrap numerics → EML-∞",
            },
        }
        return table.get(theory + "_" + operator, {"eml": "unknown"})

    def to_dict(self) -> dict:
        return {
            "ope_free_scalar": self.ope_coefficient_eml("free_scalar", "propagator"),
            "ope_2d_ising": self.ope_coefficient_eml("ising", "spin_spin"),
            "ope_3d_ising": self.ope_coefficient_eml("3d_ising", "ope"),
            "eml_principle": (
                "OPE coefficients are EML-2 when scaling dimensions are rational/algebraic; "
                "EML-∞ when dimensions are only numerically accessible (e.g. 3D Ising bootstrap)"
            ),
        }


@dataclass
class KosterlitzThouless:
    """
    Kosterlitz-Thouless (KT) transition in the 2D XY model.

    The KT transition is driven by vortex unbinding: below T_KT, vortices are bound in pairs;
    above T_KT, free vortices proliferate → disordering.

    EML structure:
    - Correlation length: ξ(T) ~ exp(c / √(T - T_KT)) as T → T_KT^+
      This is EML-1 (single exp atom) × EML-2 argument (1/√(T-T_KT))
      → composite EML-2 (log ξ = c/√(T-T_KT) = EML-2)
    - Helicity modulus Y(T): Y = 0 above T_KT (universal jump ΔY = 2T_KT/π)
    - Vortex fugacity y ~ exp(-E_c/T): EML-1

    The "BKT essential singularity" is the defining EML-∞-type behavior at T_KT
    from below (infinite-order phase transition — all derivatives finite, but ξ diverges faster
    than any power law).
    """
    T_KT: float = 0.8935  # For 2D XY model on square lattice (dimensionless)
    c: float = 1.5  # Non-universal constant

    def correlation_length(self, T: float) -> float:
        if T <= self.T_KT:
            return float("inf")
        return math.exp(self.c / math.sqrt(T - self.T_KT))

    def helicity_jump(self) -> dict:
        return {
            "Delta_Y": round(2 * self.T_KT / math.pi, 6),
            "T_KT": self.T_KT,
            "eml_jump": "Universal jump ΔY = 2T_KT/π: EML-2 (rational × T_KT)",
        }

    def to_dict(self) -> dict:
        temps = [0.90, 0.92, 0.95, 1.0, 1.1]
        xi_table = [
            {"T": T, "xi": round(self.correlation_length(T), 4) if T > self.T_KT else "∞"}
            for T in temps
        ]
        return {
            "T_KT": self.T_KT,
            "correlation_length_table": xi_table,
            "helicity_modulus_jump": self.helicity_jump(),
            "eml_depth": 2,
            "eml_reason": (
                "ln ξ = c/√(T-T_KT): EML-2 (inverse square root of distance from T_KT). "
                "The essential singularity is an EML-2 divergence in ln ξ, not ξ itself."
            ),
            "kt_vs_normal_transition": (
                "Normal transition: ξ ~ (T-T_c)^{-ν} = EML-2 power law. "
                "KT transition: ln ξ ~ (T-T_KT)^{-1/2} = EML-2 — same depth but different form."
            ),
        }


def analyze_qft_rg_deep_eml() -> dict:
    rg = WilsonRGFlow(d=3.0)
    kt = KosterlitzThouless()
    ope = OperatorProductExpansion()
    return {
        "session": 84,
        "title": "QFT Interacting Deep: Wilson RG, Fixed Points & Universality Classes",
        "key_theorem": {
            "theorem": "EML Universality Classification Theorem",
            "statement": (
                "Fixed points of the Wilson RG are EML-classified by the algebraic accessibility "
                "of their critical exponents: "
                "Gaussian (EML-0), ε-expansion Wilson-Fisher (EML-2), exact 2D Ising (EML-3), "
                "3D Ising/bootstrap (EML-∞). "
                "The approach to any fixed point is EML-1 (exponential in RG time t = ln μ). "
                "The KT transition has EML-2 essential singularity: ln ξ = c(T-T_KT)^{-1/2}."
            ),
        },
        "wilson_rg": rg.to_dict(),
        "universality_classes": [uc.to_dict() for uc in UNIVERSALITY_CLASSES],
        "kosterlitz_thouless": kt.to_dict(),
        "operator_product_expansion": ope.to_dict(),
        "eml_depth_summary": {
            "EML-0": "Gaussian/free fixed point; mean-field theory",
            "EML-1": "Exponential approach to fixed point g(t)→g*; vortex fugacity exp(-E_c/T)",
            "EML-2": "Wilson-Fisher exponents (ε-expansion); KT ln ξ singularity; O(N) large-N",
            "EML-3": "2D Ising exact (Onsager spinors); OPE in exactly solvable CFTs",
            "EML-∞": "3D Ising bootstrap exponents; OPE of numerically-only CFTs",
        },
        "connections": {
            "to_session_75": "Session 75: running coupling = EML-2. Session 84: Wilson-Fisher fixed point = EML-2 (same depth class)",
            "to_session_57": "Session 57: Boltzmann = EML-1. Session 84: approach to fixed point = EML-1 same universality",
        },
    }


if __name__ == "__main__":
    print(json.dumps(analyze_qft_rg_deep_eml(), indent=2, default=str))
