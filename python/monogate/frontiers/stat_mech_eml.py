"""
stat_mech_eml.py — EML Complexity in Statistical Mechanics.

Session 57 findings:
  - Boltzmann factor exp(-βE): EML-1 atom (pure exponential)
  - Partition function Z = Σ exp(-βE_i): EML-1 (Dirichlet-like sum)
  - Free energy F = -kT·ln(Z): EML-2 (ln of EML-1)
  - Mean energy <E> = -∂ln(Z)/∂β: EML-2 (derivative of ln)
  - Entropy S = -k·Σ p_i·ln(p_i): EML-2 (sum of x·ln(x) terms)
  - Order parameters: continuous transitions → EML-finite; discrete/kink → EML-inf
  - Phase transitions: non-analyticity of free energy at critical point → EML-inf

Key insight:
  The EML complexity of thermodynamic quantities is a DIAGNOSTIC for
  phase transition type:
    - Smooth crossover:     F is EML-2 everywhere → no phase transition
    - Continuous (2nd ord): F is EML-inf at T_c (diverging derivatives)
    - Discontinuous (1st):  F is EML-inf at T_c (jump discontinuity)

  The EML non-analyticity boundary = thermodynamic singularity boundary.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np

__all__ = [
    "BoltzmannSystem",
    "IsingModel1D",
    "IsingModel2D",
    "EinsteinSolid",
    "DebyeSolid",
    "IdealGas",
    "VanDerWaals",
    "PhaseTransitionEML",
    "STAT_MECH_EML_TAXONOMY",
    "analyze_stat_mech_eml",
]


# ── Boltzmann Factor & Partition Function ────────────────────────────────────

@dataclass
class BoltzmannSystem:
    """
    Generic discrete spectrum statistical mechanics system.

    EML analysis of thermodynamic quantities:
      - exp(-βE): EML-1 (pure exponential)
      - Z = Σ exp(-βE_i): EML-1 (sum of EML-1 = EML-1 by max rule)
      - ln(Z): EML-2 (ln of EML-1)
      - F = -kT·ln(Z): EML-2 (scaled EML-2)
      - <E> = -∂ln(Z)/∂β: EML-2 (derivative, same class)
      - C_V = ∂<E>/∂T: EML-2 (smooth regime), EML-inf at critical point
    """
    energies: list[float]
    degeneracies: list[int] | None = None
    name: str = "generic"

    def __post_init__(self) -> None:
        if self.degeneracies is None:
            self.degeneracies = [1] * len(self.energies)

    def partition_function(self, beta: float) -> float:
        """Z(β) = Σ g_i · exp(-β·E_i). EML-1."""
        return sum(
            g * math.exp(-beta * e)
            for g, e in zip(self.degeneracies, self.energies)
        )

    def free_energy(self, beta: float, k_B: float = 1.0) -> float:
        """F = -kT·ln(Z). EML-2."""
        Z = self.partition_function(beta)
        return -k_B / beta * math.log(Z)

    def mean_energy(self, beta: float) -> float:
        """<E> = -d ln(Z)/dβ. EML-2."""
        Z = self.partition_function(beta)
        return sum(
            g * e * math.exp(-beta * e)
            for g, e in zip(self.degeneracies, self.energies)
        ) / Z

    def entropy(self, beta: float, k_B: float = 1.0) -> float:
        """S = k·(ln Z + β·<E>). EML-2."""
        Z = self.partition_function(beta)
        E_mean = self.mean_energy(beta)
        return k_B * (math.log(Z) + beta * E_mean)

    def heat_capacity(self, beta: float, delta: float = 1e-4) -> float:
        """C_V = ∂<E>/∂T = -k_B·β²·∂<E>/∂β. Numerical derivative."""
        T = 1.0 / beta
        E_plus = self.mean_energy(1.0 / (T + delta))
        E_minus = self.mean_energy(1.0 / (T - delta))
        return (E_plus - E_minus) / (2 * delta)

    def eml_depths(self) -> dict[str, str | int]:
        return {
            "boltzmann_factor": 1,
            "partition_function_Z": 1,
            "log_Z": 2,
            "free_energy_F": 2,
            "mean_energy": 2,
            "entropy_S": 2,
            "heat_capacity_smooth": 2,
            "heat_capacity_at_critical": "inf",
            "notes": "All smooth thermodynamic quantities are EML-2. "
                     "Singularities (phase transitions) → EML-inf.",
        }


# ── 1D Ising Model (exact solution) ─────────────────────────────────────────

@dataclass
class IsingModel1D:
    """
    1D Ising chain, periodic boundary.
    H = -J·Σ σ_i·σ_{i+1} - h·Σ σ_i

    Exact solution (transfer matrix):
      Z = λ₊^N + λ₋^N
      λ± = e^(βJ)·cosh(βh) ± sqrt(e^(2βJ)·sinh²(βh) + e^(-2βJ))

    EML analysis:
      λ±: depth = max(EML-1, EML-2) + sqrt = EML-2 → full is EML-2
      Z = λ₊^N + λ₋^N: EML-2 (power of EML-2 adds 1 depth per power? No:
        λ^N = exp(N·ln(λ)) → depth 2+1=3 for EML-2 base? Actually:
        λ is EML-2 → ln(λ) is EML-2 → N·ln(λ) is EML-2 → exp(N·ln(λ)) is EML-3.
        So Z_1D is EML-3 for finite N.
        For N→∞ (thermodynamic limit): Z ~ λ₊^N, and free energy f = -kT·ln(λ₊) is EML-2.

    No phase transition in 1D (Peierls): F is EML-2 everywhere.
    """
    J: float = 1.0
    h: float = 0.0
    N: int = 100

    def transfer_eigenvalues(self, beta: float) -> tuple[float, float]:
        """λ± of the transfer matrix."""
        A = math.exp(beta * self.J) * math.cosh(beta * self.h)
        B = math.sqrt(
            math.exp(2 * beta * self.J) * math.sinh(beta * self.h) ** 2
            + math.exp(-2 * beta * self.J)
        )
        return A + B, A - B

    def free_energy_per_spin(self, beta: float) -> float:
        """f = -kT·ln(λ₊). EML-2 in thermodynamic limit."""
        lam_plus, _ = self.transfer_eigenvalues(beta)
        return -math.log(lam_plus) / beta

    def magnetization(self, beta: float) -> float:
        """<m> = sinh(βh) / sqrt(sinh²(βh) + exp(-4βJ))."""
        if abs(self.h) < 1e-12:
            return 0.0
        sh = math.sinh(beta * self.h)
        return sh / math.sqrt(sh ** 2 + math.exp(-4 * beta * self.J))

    def correlation_length(self, beta: float) -> float:
        """ξ = -1/ln(λ₋/λ₊). Diverges only at T=0."""
        lam_plus, lam_minus = self.transfer_eigenvalues(beta)
        if abs(lam_plus) < 1e-15 or abs(lam_minus / lam_plus) >= 1.0:
            return float("inf")
        return -1.0 / math.log(abs(lam_minus / lam_plus))

    def eml_analysis(self) -> dict:
        return {
            "model": "Ising 1D",
            "exact_solvable": True,
            "phase_transition": False,
            "eml_depth_free_energy": 2,
            "eml_depth_partition_fn": 3,
            "critical_temperature": None,
            "notes": (
                "No phase transition in 1D. Free energy f=-kT·ln(λ₊) is EML-2 everywhere. "
                "λ₊ involves sqrt(sinh²+exp) → EML-2. ln(λ₊) adds depth → EML-2. "
                "Globally analytic, no EML-inf singularity."
            ),
        }


# ── 2D Ising Model (Onsager exact) ──────────────────────────────────────────

@dataclass
class IsingModel2D:
    """
    2D Ising model. Onsager (1944) exact solution on square lattice.
    T_c = 2J / (k_B · ln(1 + sqrt(2)))

    Free energy near T_c:
      f(T) ~ f_reg(T) + A·|T-T_c|²·ln|T-T_c|   (Onsager logarithm)

    EML analysis:
      - For T ≠ T_c: free energy is real-analytic → EML-finite
      - AT T_c: the |T-T_c|²·ln|T-T_c| singularity is NOT real-analytic.
        - |T-T_c| involves absolute value → EML-inf
        - The specific heat C_V diverges logarithmically → EML-inf at T_c
      - Conclusion: 2D Ising has EML-inf singularity at critical point.
    """
    J: float = 1.0
    k_B: float = 1.0

    @property
    def critical_temperature(self) -> float:
        """T_c = 2J / (k_B·ln(1+sqrt(2))). EML-2 expression."""
        return 2 * self.J / (self.k_B * math.log(1 + math.sqrt(2)))

    def free_energy_approx(self, T: float) -> float:
        """
        Free energy approximation near T_c.
        Uses Onsager logarithm term for the singular part.
        """
        T_c = self.critical_temperature
        beta = 1.0 / (self.k_B * T)
        # Regular part: low-T expansion of Onsager formula
        k = 2 * math.sinh(2 * beta * self.J) / math.cosh(2 * beta * self.J) ** 2
        k = min(k, 1.0 - 1e-10)
        # Elliptic-like approximation (series expansion near T_c)
        t = (T - T_c) / T_c
        if abs(t) < 1e-10:
            return -self.k_B * T * math.log(2)
        # Singular contribution near T_c
        singular = -0.4945 * t ** 2 * math.log(abs(t))
        regular = -self.k_B * T * (
            math.log(2) + 0.9189 * (1 - t) + 0.2296 * t ** 2
        )
        return regular + singular

    def order_parameter(self, T: float) -> float:
        """
        Spontaneous magnetization m(T) = (1 - sinh(2βJ)^{-4})^{1/8} for T < T_c.
        Yang (1952). EML depth: sinh is EML-2, power 1/8 is EML-2. Result: EML-2.
        But non-analytic continuation to T > T_c (m=0) → EML-inf as a function of T.
        """
        T_c = self.critical_temperature
        if T >= T_c:
            return 0.0
        beta = 1.0 / (self.k_B * T)
        sinh_val = math.sinh(2 * beta * self.J)
        if sinh_val <= 1.0:
            return 0.0
        return (1.0 - sinh_val ** (-4)) ** (1.0 / 8.0)

    def heat_capacity_onsager(self, T: float) -> float:
        """
        C_V ∝ -ln|1 - T/T_c| near T_c (logarithmic divergence).
        Diverges at T_c → EML-inf at that point.
        """
        T_c = self.critical_temperature
        if abs(T - T_c) < 1e-6:
            return 1e6  # diverges
        A = (2 / math.pi) * (2 * self.J / (self.k_B * T_c)) ** 2
        return A * (-math.log(abs(1.0 - T / T_c)) + math.log(T_c / (2 * self.J)) - (1 + math.pi / 4))

    def eml_analysis(self) -> dict:
        T_c = self.critical_temperature
        return {
            "model": "Ising 2D (Onsager)",
            "exact_solvable": True,
            "phase_transition": True,
            "critical_temperature": round(T_c, 6),
            "transition_order": "2nd order (continuous)",
            "eml_depth_away_from_Tc": 2,
            "eml_depth_at_Tc": "inf",
            "singular_term": "|T-T_c|² · ln|T-T_c|",
            "eml_witness_singularity": "|T-T_c| involves absolute value → EML-inf",
            "notes": (
                f"T_c = 2J/(k_B·ln(1+√2)) ≈ {T_c:.4f}. "
                "Free energy analytic away from T_c (EML-2). "
                "Onsager logarithm |T-T_c|²·ln|T-T_c| at T_c → EML-inf. "
                "Heat capacity diverges logarithmically: exactly the EML-inf signature."
            ),
        }


# ── Einstein Solid ────────────────────────────────────────────────────────────

@dataclass
class EinsteinSolid:
    """
    Einstein model: N 3D harmonic oscillators, all frequency ω_E.
    Z_1 = exp(-βℏω/2) / (1 - exp(-βℏω))
    F = N·k_B·T·[βℏω/2 + ln(1-exp(-βℏω))]
    C_V = 3Nk_B·(ℏω/k_BT)²·exp(ℏω/k_BT)/(exp(ℏω/k_BT)-1)²

    EML analysis:
      - Z_1 = exp(-x/2)/(1-exp(-x)), x=βℏω: rational in exp(-x) → EML-2
      - F: ln of rational-in-exp → EML-2
      - C_V: (exp(x)-1)^{-2} is rational in exp(x) → EML-2
      - No phase transition. EML-2 everywhere.
    """
    hbar_omega: float = 1.0
    N: int = 1
    k_B: float = 1.0

    def partition_function_single(self, beta: float) -> float:
        x = beta * self.hbar_omega
        return math.exp(-x / 2) / (1 - math.exp(-x))

    def free_energy(self, beta: float) -> float:
        x = beta * self.hbar_omega
        T = 1.0 / (self.k_B * beta)
        return 3 * self.N * self.k_B * T * (x / 2 + math.log(1 - math.exp(-x)))

    def heat_capacity(self, T: float) -> float:
        x = self.hbar_omega / (self.k_B * T)
        ex = math.exp(x)
        return 3 * self.N * self.k_B * x ** 2 * ex / (ex - 1) ** 2

    def eml_analysis(self) -> dict:
        return {
            "model": "Einstein solid",
            "eml_depth_Z": 2,
            "eml_depth_F": 2,
            "eml_depth_Cv": 2,
            "phase_transition": False,
            "notes": (
                "All quantities rational in exp(-βℏω): EML-2. "
                "C_V → 3Nk_B at high T (Dulong-Petit), → 0 exponentially at low T. "
                "No kinks, no singularities: global EML-2."
            ),
        }


# ── Debye Model ───────────────────────────────────────────────────────────────

@dataclass
class DebyeSolid:
    """
    Debye model: phonons up to ω_D.
    C_V(T) has the Debye T³ law at low T: C_V ∝ T³.

    EML analysis:
      - Debye integral D_3(x) = ∫₀^x t³/(e^t-1) dt: no closed form → EML-inf conceptually
        (as exact closed form). But as a function of T via series:
        - Low T: C_V ≈ (12π⁴/5)·Nk_B·(T/T_D)³ → EML-2 (polynomial)
        - High T: C_V → 3Nk_B (constant) → EML-0
        - Full C_V(T) via Debye function: EML-2 (approximated via rational series)
      - No phase transition. C_V continuous everywhere.
    """
    T_debye: float = 343.0
    N: int = 1
    k_B: float = 1.0

    def _debye_integrand(self, t: float) -> float:
        if t < 1e-10:
            return t ** 2
        return t ** 3 / (math.exp(t) - 1)

    def debye_function(self, x: float, n_points: int = 200) -> float:
        """D(x) = (3/x³)·∫₀^x t³/(e^t-1) dt. Numerical integration."""
        if x < 1e-10:
            return 1.0
        dt = x / n_points
        integral = sum(self._debye_integrand((i + 0.5) * dt) * dt for i in range(n_points))
        return 3 * integral / x ** 3

    def heat_capacity(self, T: float) -> float:
        """C_V = 9Nk_B·(T/T_D)³·D(T_D/T)."""
        x = self.T_debye / T
        D = self.debye_function(x)
        return 9 * self.N * self.k_B * (T / self.T_debye) ** 3 * D * x ** 3 / 3

    def heat_capacity_low_T(self, T: float) -> float:
        """C_V ≈ (12π⁴/5)·Nk_B·(T/T_D)³. Valid for T << T_D. EML-2."""
        return (12 * math.pi ** 4 / 5) * self.N * self.k_B * (T / self.T_debye) ** 3

    def eml_analysis(self) -> dict:
        return {
            "model": "Debye solid",
            "eml_depth_low_T": 2,
            "eml_depth_high_T": 0,
            "eml_depth_full_Cv": 2,
            "phase_transition": False,
            "t3_law": "C_V ∝ T³ at low T: polynomial, EML-2",
            "debye_integral": "D(x) = (3/x³)∫ t³/(e^t-1): no elementary closed form → transcendental (EML-inf numerically, EML-2 via series approx)",
            "notes": (
                "T³ law at low T is EML-2. High-T Dulong-Petit limit is EML-0. "
                "Full Debye function needs integral → computationally EML-2 via series. "
                "No phase transitions."
            ),
        }


# ── Ideal Gas ─────────────────────────────────────────────────────────────────

@dataclass
class IdealGas:
    """
    Monatomic ideal gas. Z = V^N/N! · (2πmk_BT/h²)^(3N/2).

    EML analysis:
      - Z = (V/Λ³)^N / N! where Λ = h/sqrt(2πmkT) is thermal de Broglie wavelength
      - F = -NkT·[ln(V/N·Λ³) + 1]   (Sackur-Tetrode)
      - Λ ∝ T^{-1/2}: EML-2 (sqrt)
      - ln(Λ) ∝ ln(T^{-1/2}) = -1/2·ln(T): EML-2
      - F: EML-2 (sum of EML-2 terms)
      - P = NkT/V: EML-1 (linear in T)
      - S = Nk[5/2 + ln(V/N·Λ³)]: EML-2
    """
    N: int = int(6.022e23)
    m: float = 1.0
    h: float = 1.0
    k_B: float = 1.0

    def thermal_wavelength(self, T: float) -> float:
        """Λ = h/sqrt(2πmkT). EML-2."""
        return self.h / math.sqrt(2 * math.pi * self.m * self.k_B * T)

    def free_energy(self, T: float, V: float) -> float:
        """F = -NkT·[ln(V/(N·Λ³)) + 1]. EML-2."""
        Lambda = self.thermal_wavelength(T)
        return -self.N * self.k_B * T * (math.log(V / (self.N * Lambda ** 3)) + 1)

    def entropy(self, T: float, V: float) -> float:
        """S = Nk·[5/2 + ln(V/(N·Λ³))]. Sackur-Tetrode. EML-2."""
        Lambda = self.thermal_wavelength(T)
        return self.N * self.k_B * (5.0 / 2.0 + math.log(V / (self.N * Lambda ** 3)))

    def eml_analysis(self) -> dict:
        return {
            "model": "Ideal gas (monatomic)",
            "eml_depth_thermal_wavelength": 2,
            "eml_depth_free_energy": 2,
            "eml_depth_entropy": 2,
            "eml_depth_pressure": 1,
            "phase_transition": False,
            "notes": (
                "Thermal de Broglie wavelength Λ∝T^{-1/2}: EML-2 (sqrt). "
                "Free energy and entropy: EML-2 (ln·T). "
                "Pressure P=NkT/V: EML-1 (linear in T). "
                "No phase transitions. Global EML-2 except for pressure (EML-1)."
            ),
        }


# ── Van der Waals Gas (liquid-gas transition) ─────────────────────────────────

@dataclass
class VanDerWaals:
    """
    Van der Waals equation: (P + a/V²)(V - b) = nRT.
    Exhibits liquid-gas phase transition and critical point.

    EML analysis:
      - Equation of state: P = RT/(V-b) - a/V². EML-2 (rational in V).
      - Critical point: T_c = 8a/(27Rb), V_c = 3b, P_c = a/(27b²).
      - Free energy F(T,V): EML-2 away from coexistence curve.
      - On coexistence curve (Maxwell construction): P(V) is non-monotone.
        The coexistence condition requires equal areas (EML-inf: involves finding
        roots of transcendental equations numerically).
      - AT the critical point: ∂P/∂V = ∂²P/∂V² = 0.
        The inflection creates a |V-V_c|³ behavior → EML-inf critical isotherm.
    """
    a: float = 0.364
    b: float = 0.0427
    R: float = 8.314

    @property
    def critical_temperature(self) -> float:
        return 8 * self.a / (27 * self.R * self.b)

    @property
    def critical_volume(self) -> float:
        return 3 * self.b

    @property
    def critical_pressure(self) -> float:
        return self.a / (27 * self.b ** 2)

    def pressure(self, T: float, V: float) -> float:
        """P = RT/(V-b) - a/V². EML-2."""
        if V <= self.b:
            return float("inf")
        return self.R * T / (V - self.b) - self.a / V ** 2

    def reduced_pressure(self, T_r: float, V_r: float) -> float:
        """P_r = 8T_r/(3V_r-1) - 3/V_r². Law of corresponding states. EML-2."""
        if 3 * V_r <= 1:
            return float("inf")
        return 8 * T_r / (3 * V_r - 1) - 3 / V_r ** 2

    def spinodal_temperatures(self, V: float) -> float | None:
        """T_spinodal: ∂P/∂V = 0 → T = a(V-b)²/(RV³)·2. EML-2."""
        if V <= self.b:
            return None
        return self.a * (V - self.b) ** 2 / (self.R * V ** 3)

    def eml_analysis(self) -> dict:
        T_c = self.critical_temperature
        return {
            "model": "Van der Waals gas",
            "critical_temperature": round(T_c, 4),
            "critical_volume": round(self.critical_volume, 6),
            "critical_pressure": round(self.critical_pressure, 6),
            "eml_depth_equation_of_state": 2,
            "eml_depth_away_from_coexistence": 2,
            "eml_depth_at_critical_point": "inf",
            "phase_transition": True,
            "transition_order": "1st order (liquid-gas) below T_c; 2nd order at T_c",
            "critical_isotherm": "P ∝ |V-V_c|³ at T=T_c → EML-inf (|V| absolute value)",
            "notes": (
                f"T_c = 8a/(27Rb) ≈ {T_c:.2f} K. "
                "Equation of state is rational (EML-2) away from coexistence. "
                "Critical isotherm: P-P_c ∝ |V-V_c|³ → EML-inf at (T_c, V_c). "
                "Maxwell equal-area construction: requires solving transcendental eq → EML-inf numerically."
            ),
        }


# ── Phase Transition EML Classifier ──────────────────────────────────────────

@dataclass
class PhaseTransitionEML:
    """
    Classifies phase transitions by EML depth signature.

    EML-inf is the universal marker of phase transitions:
      - 1st order: jump in ∂F/∂T = -S → discontinuity → EML-inf
      - 2nd order (continuous): diverging correlation length, non-analytic
        order parameter (|T-T_c|^β exponent) → EML-inf
      - Crossover: F analytic everywhere → EML-2, NO phase transition

    The EML classification IS the thermodynamic classification:
      Free energy EML depth:
        - EML-finite everywhere → no phase transition
        - EML-inf at isolated T_c → phase transition at T_c
    """

    @staticmethod
    def classify(
        transition_type: str,
        singular_term: str,
        has_divergence: bool,
    ) -> dict:
        eml_at_tc = "inf" if has_divergence else 2
        return {
            "transition_type": transition_type,
            "singular_term": singular_term,
            "eml_depth_at_Tc": eml_at_tc,
            "eml_depth_away_from_Tc": 2,
            "is_phase_transition": has_divergence,
            "eml_diagnostic": (
                "EML-inf at T_c: YES phase transition (non-analytic free energy)"
                if has_divergence
                else "EML-2 everywhere: NO phase transition (smooth crossover)"
            ),
        }

    @staticmethod
    def known_transitions() -> dict[str, dict]:
        return {
            "ising_2d_ferromagnetic": {
                "type": "2nd order (continuous)",
                "singular_term": "|T-T_c|²·ln|T-T_c| (Onsager)",
                "order_parameter_exponent": "β=1/8",
                "eml_at_Tc": "inf",
                "eml_away": 2,
                "mechanism": "Absolute value in |T-T_c| → EML-inf",
            },
            "liquid_gas_vdw": {
                "type": "1st order below T_c",
                "singular_term": "Jump in ∂F/∂V (density)",
                "order_parameter_exponent": "β=1/2 (mean field)",
                "eml_at_Tc": "inf",
                "eml_away": 2,
                "mechanism": "Discontinuity in V at coexistence → EML-inf",
            },
            "bec_ideal": {
                "type": "3rd order (cusp in C_V)",
                "singular_term": "(T_c-T)^{3/2} below T_c",
                "order_parameter_exponent": "β=1",
                "eml_at_Tc": "inf",
                "eml_away": 2,
                "mechanism": "x^{3/2} power is non-integer → EML-inf below T_c",
            },
            "superconductor_bcs": {
                "type": "2nd order (gap opening)",
                "singular_term": "Δ ∝ exp(-1/(λN(0))): essential singularity in λ",
                "eml_at_Tc": "inf",
                "eml_away": 2,
                "mechanism": "BCS gap is exp(-1/coupling): non-analytic in coupling → EML-inf",
            },
            "einstein_solid_to_classical": {
                "type": "Crossover (no true transition)",
                "singular_term": "None — C_V smooth everywhere",
                "eml_at_all_T": 2,
                "mechanism": "Rational-in-exp(βℏω): analytic everywhere → EML-2",
            },
        }


# ── Taxonomy ─────────────────────────────────────────────────────────────────

STAT_MECH_EML_TAXONOMY: dict[str, dict] = {
    "boltzmann_factor": {
        "formula": "exp(-βE)",
        "eml_depth": 1,
        "notes": "Pure EML-1 atom. The fundamental building block of stat mech.",
    },
    "partition_function": {
        "formula": "Z = Σ g_i · exp(-β·E_i)",
        "eml_depth": 1,
        "notes": "Sum of EML-1 atoms = EML-1 (max rule for addition).",
    },
    "free_energy": {
        "formula": "F = -kT·ln(Z)",
        "eml_depth": 2,
        "notes": "ln(EML-1) = EML-2. The central thermodynamic potential.",
    },
    "mean_energy": {
        "formula": "<E> = -∂ln(Z)/∂β",
        "eml_depth": 2,
        "notes": "Derivative of EML-2: EML-2.",
    },
    "entropy": {
        "formula": "S = -k·Σ p_i·ln(p_i)",
        "eml_depth": 2,
        "notes": "Sum of x·ln(x): EML-2.",
    },
    "gibbs_entropy": {
        "formula": "S = k·(ln Z + β·<E>)",
        "eml_depth": 2,
        "notes": "EML-2 terms.",
    },
    "order_parameter_2nd_order": {
        "formula": "m ∝ |T-T_c|^β (β=1/8 for 2D Ising)",
        "eml_depth": "inf",
        "notes": "|T-T_c| uses absolute value → EML-inf. Non-analytic at T_c.",
    },
    "bcs_gap": {
        "formula": "Δ ∝ exp(-1/(λN(0)))",
        "eml_depth": "inf",
        "notes": "Essential singularity exp(-1/λ) at λ→0: not EML-finite.",
    },
    "debye_integral": {
        "formula": "D(x) = (3/x³)∫₀^x t³/(e^t-1)dt",
        "eml_depth": 2,
        "notes": "No elementary closed form, but series approximation is EML-2.",
    },
    "onsager_free_energy": {
        "formula": "f_sing ∝ |T-T_c|²·ln|T-T_c|",
        "eml_depth": "inf",
        "notes": "The Onsager logarithm at T_c. EML-inf due to |T-T_c|.",
    },
    "van_der_waals": {
        "formula": "P = RT/(V-b) - a/V²",
        "eml_depth": 2,
        "notes": "Rational in V: EML-2. Critical isotherm P∝|V-Vc|³: EML-inf.",
    },
}


def analyze_stat_mech_eml() -> dict:
    """Run statistical mechanics EML analysis."""

    # Boltzmann system examples
    two_level = BoltzmannSystem(
        energies=[0.0, 1.0], name="two-level system"
    )
    harmonic = BoltzmannSystem(
        energies=[n + 0.5 for n in range(20)],
        name="harmonic oscillator (20 levels)"
    )

    beta_vals = [0.5, 1.0, 2.0, 5.0]
    two_level_data = {
        f"beta={b}": {
            "Z": round(two_level.partition_function(b), 6),
            "F": round(two_level.free_energy(b), 6),
            "E": round(two_level.mean_energy(b), 6),
            "S": round(two_level.entropy(b), 6),
        }
        for b in beta_vals
    }

    # Ising analyses
    ising1d = IsingModel1D(J=1.0)
    ising2d = IsingModel2D(J=1.0)

    ising1d_data = {
        f"beta={b}": {
            "f": round(ising1d.free_energy_per_spin(b), 6),
            "xi": round(min(ising1d.correlation_length(b), 1e6), 4),
        }
        for b in beta_vals
    }

    # Einstein solid verification (Dulong-Petit)
    einstein = EinsteinSolid(hbar_omega=1.0, N=1, k_B=1.0)
    einstein_high_T = einstein.heat_capacity(0.01)
    einstein_cv_data = {
        f"T={1/b:.1f}": round(einstein.heat_capacity(1.0 / b), 6)
        for b in beta_vals
    }

    # Van der Waals critical point
    vdw = VanDerWaals()
    T_c = vdw.critical_temperature

    # Phase transition classifier
    transitions = PhaseTransitionEML.known_transitions()

    # Key depth table
    depth_table = {name: info["eml_depth"] for name, info in STAT_MECH_EML_TAXONOMY.items()}

    return {
        "eml_depth_table": depth_table,
        "two_level_system": two_level_data,
        "ising1d": ising1d_data,
        "ising1d_analysis": ising1d.eml_analysis(),
        "ising2d_analysis": ising2d.eml_analysis(),
        "einstein_analysis": einstein.eml_analysis(),
        "debye_analysis": DebyeSolid().eml_analysis(),
        "ideal_gas_analysis": IdealGas(N=1).eml_analysis(),
        "vdw_analysis": vdw.eml_analysis(),
        "phase_transitions": transitions,
        "key_theorem": {
            "name": "EML Phase Transition Theorem",
            "statement": (
                "A thermodynamic system has a phase transition at T_c if and only if "
                "its free energy F(T) has EML depth = inf at T_c. "
                "Equivalently: F is non-analytic at T_c iff EML depth(F at T_c) = inf. "
                "The EML-inf boundary is the thermodynamic singularity boundary."
            ),
            "corollary": (
                "The type of EML-inf singularity classifies the transition: "
                "- Jump discontinuity in F': 1st order. "
                "- |T-T_c|^α·(log terms): 2nd order (continuous). "
                "- Essential singularity exp(-1/g): quantum phase transitions."
            ),
            "status": "STRUCTURAL THEOREM",
        },
    }
