"""
rep_theory_eml.py — EML Complexity in Representation Theory.

Session 65 findings:
  - U(1) representations: χ_n(e^{iθ}) = e^{inθ} → EML-1 atoms!
  - SU(2) characters: χ_j(θ) = sin((2j+1)θ)/sin(θ) → EML-3/EML-3 = EML-3
  - Weyl character formula: EML-1 numerator, EML-2 denominator
  - Peter-Weyl theorem: L²(G) = ⊕ V_λ ⊗ V_λ* → Fourier analysis on groups
  - Root systems: EML-0 (discrete integer lattices)
  - Casimir eigenvalue: EML-0
  - Wigner D-matrices for SO(3): trig → EML-3
  - Plancherel formula: EML-2 (L² norms)
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Callable

import numpy as np

__all__ = [
    "U1Representation",
    "SU2Character",
    "WeylFormula",
    "PeterWeyl",
    "WignerD",
    "REP_THEORY_EML_TAXONOMY",
    "analyze_rep_theory_eml",
]

# ── EML Taxonomy ─────────────────────────────────────────────────────────────

REP_THEORY_EML_TAXONOMY: dict[str, dict] = {
    "u1_character": {
        "formula": "χ_n(e^{iθ}) = e^{inθ}",
        "eml_depth": 1,
        "reason": "Pure EML-1 atom! U(1) representation = single exponential.",
    },
    "su2_character": {
        "formula": "χ_j(θ) = sin((2j+1)θ)/sin(θ)",
        "eml_depth": 3,
        "reason": "sin/sin ratio: sin is EML-3 (composition of EML-1 and inverse), ratio is EML-3.",
    },
    "weyl_character": {
        "formula": "χ_λ = Σ_{w∈W} (-1)^w e^{w(λ+ρ)} / Π_{α>0}(e^{α/2}-e^{-α/2})",
        "eml_depth": 1,
        "reason": "Numerator: sum of EML-1 atoms. Denominator: EML-1. Overall: EML-1 ratio.",
    },
    "so3_wigner_d": {
        "formula": "D^j_{mm'}(α,β,γ) = e^{-imα}·d^j_{mm'}(β)·e^{-im'γ}",
        "eml_depth": 3,
        "reason": "d^j_{mm'}(β) involves trig polynomials → EML-3.",
    },
    "casimir_eigenvalue": {
        "formula": "Ω|V_λ⟩ = λ(λ+2)·|V_λ⟩",
        "eml_depth": 0,
        "reason": "Eigenvalue is integer/algebraic number: EML-0.",
    },
    "weight_lattice": {
        "formula": "P ⊂ h*: integer lattice of highest weights",
        "eml_depth": 0,
        "reason": "Discrete lattice: EML-0.",
    },
    "plancherel_formula": {
        "formula": "∫_G |f(g)|² dg = Σ_λ d_λ ‖f̂(λ)‖²_HS",
        "eml_depth": 2,
        "reason": "L² norms: EML-2 (quadratic).",
    },
    "peter_weyl": {
        "formula": "L²(G) = ⊕ V_λ ⊗ V_λ*",
        "eml_depth": 1,
        "reason": "Matrix coefficients e^{inθ} for U(1): EML-1. Fourier = EML-1 basis.",
    },
}


# ── U(1) Representations ──────────────────────────────────────────────────────

@dataclass
class U1Representation:
    """
    U(1) = {e^{iθ}: θ ∈ ℝ/2πℤ}.

    Irreducible representations: χ_n(e^{iθ}) = e^{inθ}, n ∈ ℤ.
    Each is a PURE EML-1 ATOM: exp(i·n·θ).

    Fourier series = Peter-Weyl theorem for U(1):
    f(θ) = Σ_n f̂(n)·e^{inθ}  — sum of EML-1 atoms.

    This is exactly the EML-Fourier density theorem (Session 37):
    smooth functions have Fourier series converging at EML-1.
    """

    def character(self, n: int, theta: float) -> complex:
        """χ_n(e^{iθ}) = e^{inθ}. EML-1."""
        return complex(math.cos(n * theta), math.sin(n * theta))

    def fourier_series(self, f: Callable[[float], float],
                        n_max: int = 20, n_points: int = 1000) -> np.ndarray:
        """
        Compute Fourier coefficients f̂(n) = ∫f(θ)·e^{-inθ}dθ/(2π).
        """
        thetas = np.linspace(0, 2 * math.pi, n_points, endpoint=False)
        dtheta = 2 * math.pi / n_points
        f_vals = np.array([f(t) for t in thetas])
        coeffs = np.zeros(2 * n_max + 1, dtype=complex)
        for k, n in enumerate(range(-n_max, n_max + 1)):
            exp_vals = np.array([self.character(-n, t) for t in thetas])
            coeffs[k] = np.sum(f_vals * exp_vals) * dtheta / (2 * math.pi)
        return coeffs

    def reconstruct(self, coeffs: np.ndarray, theta: float) -> complex:
        """Reconstruct f(θ) = Σ_n f̂(n)·e^{inθ}."""
        n_max = (len(coeffs) - 1) // 2
        total = complex(0, 0)
        for k, n in enumerate(range(-n_max, n_max + 1)):
            total += coeffs[k] * self.character(n, theta)
        return total

    def eml_depth_character(self) -> int:
        return 1  # Pure EML-1 atom


# ── SU(2) Characters ──────────────────────────────────────────────────────────

@dataclass
class SU2Character:
    """
    SU(2) has irreps V_j for j = 0, 1/2, 1, 3/2, ...
    Character: χ_j(θ) = sin((2j+1)θ) / sin(θ)  for θ ≠ 0.
    At θ=0: χ_j(0) = 2j+1 (dimension of V_j).

    EML depth: sin/sin = EML-3/EML-3. The result involves EML-3 functions.
    """

    def character(self, j: float, theta: float) -> float:
        """χ_j(θ) = sin((2j+1)θ)/sin(θ). EML-3."""
        if abs(theta) < 1e-10:
            return 2 * j + 1.0
        sin_theta = math.sin(theta)
        if abs(sin_theta) < 1e-12:
            return 2 * j + 1.0
        return math.sin((2 * j + 1) * theta) / sin_theta

    def dimension(self, j: float) -> int:
        """dim(V_j) = 2j+1."""
        return int(2 * j + 1)

    def casimir_eigenvalue(self, j: float) -> float:
        """C₂(V_j) = j(j+1). EML-0 (algebraic)."""
        return j * (j + 1)

    def character_orthogonality(self, j1: float, j2: float,
                                  n_points: int = 1000) -> float:
        """
        Peter-Weyl orthogonality:
        ∫χ_{j1}(θ)·χ̄_{j2}(θ)·|sin θ|²/(2π) dθ = δ_{j1,j2}.
        """
        thetas = np.linspace(0.01, math.pi - 0.01, n_points)
        dtheta = (math.pi - 0.02) / (n_points - 1)
        chi1 = np.array([self.character(j1, t) for t in thetas])
        chi2 = np.array([self.character(j2, t) for t in thetas])
        measure = np.sin(thetas) ** 2
        # Normalize: ∫|sinθ|² dθ from 0 to π = π/2
        inner = float(np.sum(chi1 * chi2 * measure) * dtheta) / (math.pi / 2.0)
        return inner

    def weyl_integration(self, j: float, n_points: int = 500) -> float:
        """
        Verify: ∫|χ_j(θ)|²·sin²(θ)·dθ/(π/2) = 1 (normalization).
        """
        return self.character_orthogonality(j, j, n_points)

    def decompose_tensor_product(self, j1: float, j2: float) -> list[float]:
        """
        Clebsch-Gordan: V_{j1} ⊗ V_{j2} = ⊕ V_j for j=|j1-j2|,...,j1+j2.
        """
        j_min = abs(j1 - j2)
        j_max = j1 + j2
        j = j_min
        result = []
        while j <= j_max + 1e-10:
            result.append(j)
            j += 1.0
        return result

    def eml_depth(self) -> int:
        return 3


# ── Weyl Character Formula ────────────────────────────────────────────────────

@dataclass
class WeylFormula:
    """
    Weyl character formula for compact Lie groups.

    χ_λ = Σ_{w∈W} (-1)^{ℓ(w)} e^{w(λ+ρ)} / Π_{α>0}(e^{α/2}-e^{-α/2})

    For SU(2): W = {1, s}, ρ = 1/2,
    χ_j = (e^{(j+1/2)·2iθ} - e^{-(j+1/2)·2iθ}) / (e^{iθ} - e^{-iθ})
          = sin((2j+1)θ) / sin(θ)

    EML depth: numerator = sum of EML-1 atoms, denominator = EML-1 atom.
    Overall: EML-1 numerator / EML-1 = EML-1 ratio → EML-2 at most.
    The trigonometric form sin((2j+1)θ)/sinθ appears EML-3, but the
    Weyl formula form shows the rational structure is EML-1/EML-1.
    """

    def weyl_numerator_su2(self, j: float, theta: float) -> float:
        """
        Weyl numerator for SU(2):
        A_{j+1/2}(θ) = e^{i(j+1/2)·2θ} - e^{-i(j+1/2)·2θ} = 2i·sin((2j+1)θ).
        Return the real magnitude.
        """
        return 2.0 * abs(math.sin((2 * j + 1) * theta))

    def weyl_denominator_su2(self, theta: float) -> float:
        """
        Weyl denominator for SU(2): e^{iθ} - e^{-iθ} = 2i·sin(θ).
        Return magnitude.
        """
        return 2.0 * abs(math.sin(theta))

    def character_su2(self, j: float, theta: float) -> float:
        """χ_j = A_{j+ρ}(θ) / A_ρ(θ) = sin((2j+1)θ)/sin(θ). EML-3."""
        if abs(math.sin(theta)) < 1e-10:
            return 2 * j + 1.0
        return math.sin((2 * j + 1) * theta) / math.sin(theta)

    def eml_depth_numerator(self) -> int:
        return 1  # sum of EML-1 atoms

    def eml_depth_character(self) -> int:
        return 3  # sin ratio


# ── Peter-Weyl Theorem ────────────────────────────────────────────────────────

@dataclass
class PeterWeyl:
    """
    Peter-Weyl theorem: L²(G) = ⊕_λ V_λ ⊗ V_λ*.

    For U(1): L²(U(1)) = ⊕_{n∈ℤ} ℂ·e^{inθ}.
    Fourier series = Peter-Weyl decomposition for U(1).
    Basis functions e^{inθ} are EML-1 atoms.

    Plancherel formula: ‖f‖²_{L²} = Σ_λ d_λ ‖f̂(λ)‖²_HS.
    EML-2: L² = EML-2 (quadratic norms).
    """

    def plancherel_u1(self, coeffs: np.ndarray, dtheta: float = None) -> float:
        """
        Plancherel for U(1): ‖f‖² = Σ |f̂(n)|².
        """
        return float(np.sum(np.abs(coeffs) ** 2))

    def parseval_check(self, f: Callable[[float], float],
                        n_max: int = 30, n_points: int = 2000) -> dict:
        """
        Parseval: ‖f‖²_L² = Σ_n |f̂(n)|².
        Compute both sides and compare.
        """
        thetas = np.linspace(0, 2 * math.pi, n_points, endpoint=False)
        dtheta = 2 * math.pi / n_points
        f_vals = np.array([f(t) for t in thetas])

        # Left side: ‖f‖²
        l2_norm_sq = float(np.sum(f_vals ** 2) * dtheta / (2 * math.pi))

        # Right side: Σ |f̂(n)|²
        u1 = U1Representation()
        coeffs = u1.fourier_series(f, n_max=n_max, n_points=n_points)
        parseval_sum = float(np.sum(np.abs(coeffs) ** 2))

        return {
            "l2_norm_sq": l2_norm_sq,
            "parseval_sum": parseval_sum,
            "relative_error": abs(l2_norm_sq - parseval_sum) / (l2_norm_sq + 1e-10),
        }

    def fourier_convergence(self, f: Callable[[float], float],
                             theta: float, n_maxes: list[int],
                             n_points: int = 2000) -> list[dict]:
        """Show Peter-Weyl Fourier series convergence for U(1)."""
        u1 = U1Representation()
        exact = f(theta)
        rows = []
        for n_max in n_maxes:
            coeffs = u1.fourier_series(f, n_max=n_max, n_points=n_points)
            approx = u1.reconstruct(coeffs, theta).real
            rows.append({
                "n_max": n_max,
                "approximation": approx,
                "exact": exact,
                "error": abs(approx - exact),
            })
        return rows

    def eml_depth_basis(self) -> int:
        return 1  # e^{inθ} atoms


# ── Wigner D-Matrices ─────────────────────────────────────────────────────────

@dataclass
class WignerD:
    """
    Wigner D-matrices for SO(3): D^j_{mm'}(α,β,γ) = e^{-imα}·d^j_{mm'}(β)·e^{-im'γ}.

    The small-d matrix d^j_{mm'}(β) involves trig polynomials → EML-3.
    The full D-matrix: exp(i·integer·angle) × trig = EML-3.

    For j=1/2 (spin-1/2):
      d^{1/2}_{1/2,1/2}(β) = cos(β/2)
      d^{1/2}_{1/2,-1/2}(β) = -sin(β/2)
    These are EML-3 (trig of half-angle).
    """

    def d_half_spin(self, beta: float) -> np.ndarray:
        """
        d^{1/2}_{mm'}(β): 2×2 matrix for spin-1/2.
        [[cos(β/2), -sin(β/2)],
         [sin(β/2),  cos(β/2)]]
        """
        c = math.cos(beta / 2.0)
        s = math.sin(beta / 2.0)
        return np.array([[c, -s], [s, c]])

    def d_spin1(self, beta: float) -> np.ndarray:
        """
        d^1_{mm'}(β): 3×3 matrix for spin-1.
        Entries are trig polynomials → EML-3.
        """
        c = math.cos(beta)
        s = math.sin(beta)
        c2 = math.cos(beta / 2.0)
        s2 = math.sin(beta / 2.0)
        return np.array([
            [c2 ** 2, -s2 * c2 * math.sqrt(2), s2 ** 2],
            [s2 * c2 * math.sqrt(2), c, -s2 * c2 * math.sqrt(2)],
            [s2 ** 2, s2 * c2 * math.sqrt(2), c2 ** 2],
        ])

    def d_matrix_rotation(self, j: float, beta: float) -> np.ndarray:
        """Full small-d matrix for arbitrary j (simplified for j=1/2,1)."""
        if abs(j - 0.5) < 0.01:
            return self.d_half_spin(beta)
        elif abs(j - 1.0) < 0.01:
            return self.d_spin1(beta)
        else:
            # For higher j: use polynomial recursion (simplified placeholder)
            dim = int(2 * j + 1)
            return np.eye(dim)  # placeholder

    def unitarity_check(self, j: float, beta: float) -> float:
        """Verify D^j·(D^j)† = I: unitary representation."""
        d = self.d_matrix_rotation(j, beta)
        product = d @ d.T
        identity = np.eye(d.shape[0])
        return float(np.max(np.abs(product - identity)))

    def eml_depth(self) -> int:
        return 3  # Wigner d-functions are trig polynomials


# ── Grand Analysis ────────────────────────────────────────────────────────────

def analyze_rep_theory_eml() -> dict:
    """Run full representation theory EML analysis."""
    results: dict = {
        "session": 65,
        "title": "Representation Theory EML Complexity",
        "taxonomy": REP_THEORY_EML_TAXONOMY,
    }

    u1 = U1Representation()
    su2 = SU2Character()
    weyl = WeylFormula()
    pw = PeterWeyl()
    wd = WignerD()

    # U(1) characters
    theta_vals = [0.0, math.pi / 4, math.pi / 2, math.pi]
    results["u1_characters"] = {
        "n1": [u1.character(1, t) for t in theta_vals],
        "n2": [u1.character(2, t) for t in theta_vals],
        "n3": [u1.character(3, t) for t in theta_vals],
        "eml_depth": u1.eml_depth_character(),
    }

    # SU(2) characters
    j_vals = [0.5, 1.0, 1.5, 2.0, 3.0]
    theta = math.pi / 3
    su2_chars = {f"j_{j}": su2.character(j, theta) for j in j_vals}
    su2_norms = {f"j_{j}": su2.weyl_integration(j) for j in j_vals}
    results["su2_characters"] = {
        "theta": theta,
        "characters": su2_chars,
        "norms": su2_norms,
        "dimensions": {f"j_{j}": su2.dimension(j) for j in j_vals},
        "casimir": {f"j_{j}": su2.casimir_eigenvalue(j) for j in j_vals},
        "eml_depth": su2.eml_depth(),
    }

    # CG decomposition
    results["cg_decomposition"] = {
        "j1_half_x_j1_half": su2.decompose_tensor_product(0.5, 0.5),
        "j1_x_j1": su2.decompose_tensor_product(1.0, 1.0),
        "j1_x_j2": su2.decompose_tensor_product(1.0, 2.0),
    }

    # Parseval check
    f_step = lambda t: 1.0 if t < math.pi else -1.0
    parseval = pw.parseval_check(f_step, n_max=30)
    results["peter_weyl"] = {
        "parseval_l2": parseval["l2_norm_sq"],
        "parseval_fourier": parseval["parseval_sum"],
        "relative_error": parseval["relative_error"],
        "eml_depth_basis": pw.eml_depth_basis(),
    }

    # Fourier convergence
    f_smooth = lambda t: math.cos(t) + 0.5 * math.sin(2 * t)
    conv = pw.fourier_convergence(f_smooth, math.pi / 4, [5, 10, 20, 30])
    results["fourier_convergence"] = conv

    # Wigner D
    results["wigner_d"] = {
        "d_half_beta_pi2": wd.d_half_spin(math.pi / 2).tolist(),
        "d_spin1_beta_pi2": wd.d_spin1(math.pi / 2).tolist(),
        "unitarity_j_half": wd.unitarity_check(0.5, math.pi / 3),
        "unitarity_j_1": wd.unitarity_check(1.0, math.pi / 3),
        "eml_depth": wd.eml_depth(),
    }

    results["summary"] = {
        "key_insight": (
            "U(1) characters are EML-1 atoms — the purest non-trivial EML class. "
            "SU(2) characters involve sin/sin → EML-3. "
            "Weyl formula numerator: sum of EML-1 atoms. "
            "Peter-Weyl = Fourier analysis on groups, basis is EML-1. "
            "Wigner D-matrices: trig polynomials → EML-3."
        ),
        "eml_depths": {k: str(v["eml_depth"]) for k, v in REP_THEORY_EML_TAXONOMY.items()},
    }

    return results
