"""
Session 117 — KPZ Universality & Non-Equilibrium Growth: EML at the Edge

KPZ equation, random matrices, Tracy-Widom distribution, and non-equilibrium
universality classes classified by EML depth.

Key theorem: The KPZ nonlinear term (∇h)² breaks EML-2 to EML-∞ fluctuations.
KPZ exponents (1/3, 1/2, 3/2) are EML-2 (rational). Tracy-Widom is EML-∞
(no elementary closed form). Random matrix GUE level spacing P(s)~s·exp(-πs²/4)
is EML-3. KPZ = the EML-∞ universality class for non-equilibrium growth.
"""

from __future__ import annotations
import math, json
from dataclasses import dataclass, field


EML_INF = float("inf")


@dataclass
class KPZEquation:
    """
    KPZ equation: ∂h/∂t = ν∇²h + (λ/2)(∇h)² + η(x,t).

    The (∇h)² term is the nonlinear symmetry-breaking term.

    EML structure:
    - Linear part ν∇²h: EML-3 (heat equation → EML-3 solution, S62)
    - Noise η ~ Gaussian white: EML-1 per mode
    - Nonlinear term (λ/2)(∇h)²: EML-2 (squared gradient = power of EML-2 gradient)
    - This term BREAKS the EML-2 linear structure → EML-∞ fluctuations
    - KPZ exponents (1D): roughness α=1/2, growth β=1/3, dynamic z=3/2: EML-2 (rational)
    - Height variance: ⟨(h(x,t)-h̄)²⟩ ~ t^{2β}: EML-2 (power law in time)
    - KPZ fixed point (RG limit): EML-∞ (Tracy-Widom distribution)
    """

    def kpz_exponents_1d(self) -> dict:
        alpha = 1/2
        beta = 1/3
        z = 3/2
        return {
            "dimension": 1,
            "roughness_alpha": alpha,
            "growth_beta": beta,
            "dynamic_z": z,
            "scaling_relation": "α = z·β (check: 1/2 = 3/2 · 1/3 = 1/2 ✓)",
            "eml_exponents": 2,
            "reason": "KPZ exponents 1/2, 1/3, 3/2: rational = EML-2 (rationals are EML-2 algebraic)",
        }

    def kpz_height_variance(self, t: float, beta: float = 1/3) -> dict:
        """⟨(h-h̄)²⟩ ~ t^{2β} = t^{2/3}."""
        var = t ** (2 * beta)
        return {
            "t": t,
            "variance_exponent": round(2*beta, 4),
            "variance_t2beta": round(var, 6),
            "eml": 2,
            "reason": "⟨h²⟩ ~ t^{2/3}: EML-2 (power law in time with rational exponent)",
        }

    def cole_hopf_kpz(self) -> dict:
        """Cole-Hopf: Z = exp(h·λ/(2ν)) transforms KPZ to multiplicative noise SHE."""
        return {
            "transformation": "Z(x,t) = exp(λh/(2ν))",
            "result": "∂Z/∂t = ν∇²Z + (λ/2ν)·η·Z (stochastic heat equation = SHE)",
            "eml_Z": 1,
            "eml_KPZ_height": EML_INF,
            "insight": "Cole-Hopf maps KPZ (EML-∞ height) to SHE (EML-1 exponential). Same as Burgers (S76). EML-1 solution to EML-∞ problem via exp transformation.",
        }

    def kpz_universality_class(self) -> list[dict]:
        return [
            {"system": "KPZ equation (λ≠0)", "dim": 1, "eml_fluctuations": EML_INF,
             "reason": "Nonlinear term → EML-∞ fluctuations (Tracy-Widom)"},
            {"system": "Edwards-Wilkinson (λ=0)", "dim": 1, "eml_fluctuations": 3,
             "reason": "Linear: EML-3 (heat equation = EML-3 solution)"},
            {"system": "ASEP (asymmetric exclusion)", "dim": 1, "eml_fluctuations": EML_INF,
             "reason": "Discrete KPZ: same EML-∞ universality class"},
            {"system": "PNG model (polynuclear growth)", "dim": 1, "eml_fluctuations": EML_INF,
             "reason": "KPZ universality: Tracy-Widom = EML-∞"},
            {"system": "Random polymer (free energy)", "dim": 1, "eml_fluctuations": EML_INF,
             "reason": "Directed polymer in random environment: KPZ class = EML-∞"},
        ]

    def to_dict(self) -> dict:
        return {
            "exponents_1d": self.kpz_exponents_1d(),
            "height_variance": [self.kpz_height_variance(t) for t in [1, 4, 9, 16, 100]],
            "cole_hopf": self.cole_hopf_kpz(),
            "universality_class": self.kpz_universality_class(),
            "eml_linear_part": 3,
            "eml_noise": 1,
            "eml_nonlinear_term": 2,
            "eml_fluctuations": EML_INF,
            "eml_exponents": 2,
        }


@dataclass
class RandomMatrices:
    """
    Random Matrix Theory (RMT): eigenvalue statistics of large random matrices.

    EML structure:
    - GUE/GOE/GSE level spacing P(s): Wigner surmise
      GUE: P(s) = (32/π²)·s²·exp(-4s²/π): EML-3 (s² × exp(-s²) = EML-3 Gaussian modulated)
      GOE: P(s) = (π/2)·s·exp(-πs²/4): EML-3 (s × exp(-s²) = EML-3)
    - Poisson (uncorrelated): P(s) = exp(-s): EML-1
    - Level repulsion: GOE β=1, GUE β=2, GSE β=4: EML-0 (Dyson index = integer)
    - Marchenko-Pastur distribution (Wishart): EML-3 (semicircle-like)
    - Wigner semicircle: ρ(λ) = √(R²-λ²)/(2πR²): EML-2 (square root = power law)
    - Tracy-Widom (largest eigenvalue): EML-∞ (no elementary closed form)
    """

    def wigner_surmise_gue(self, s: float) -> dict:
        """P(s) = (32/π²)·s²·exp(-4s²/π) for GUE."""
        if s < 0:
            return {"s": s, "P_s": 0.0, "eml": 3}
        P = (32 / math.pi**2) * s**2 * math.exp(-4 * s**2 / math.pi)
        return {
            "s": round(s, 3),
            "P_s_GUE": round(P, 6),
            "eml": 3,
            "reason": "P(s) = c·s²·exp(-4s²/π): EML-3 (power × Gaussian = EML-3)",
        }

    def wigner_surmise_goe(self, s: float) -> dict:
        """P(s) = (π/2)·s·exp(-πs²/4) for GOE."""
        if s < 0:
            return {"s": s, "P_s": 0.0, "eml": 3}
        P = (math.pi / 2) * s * math.exp(-math.pi * s**2 / 4)
        return {
            "s": round(s, 3),
            "P_s_GOE": round(P, 6),
            "eml": 3,
            "reason": "P(s) = (π/2)s·exp(-πs²/4): EML-3 (linear × Gaussian = EML-3)",
        }

    def wigner_semicircle(self, lam: float, R: float = 2.0) -> dict:
        """ρ(λ) = √(R²-λ²)/(2πR²) for |λ| < R."""
        if abs(lam) >= R:
            return {"lambda": lam, "rho": 0.0, "eml": 2}
        rho = math.sqrt(R**2 - lam**2) / (2 * math.pi * R**2) * 2 * math.pi
        rho /= math.pi
        return {
            "lambda": round(lam, 3),
            "rho": round(rho, 6),
            "eml": 2,
            "reason": "Semicircle ρ ~ √(R²-λ²): EML-2 (square root of polynomial)",
        }

    def poisson_spacing(self, s: float) -> dict:
        """Integrable systems: P(s) = exp(-s) (no level repulsion)."""
        P = math.exp(-s) if s >= 0 else 0.0
        return {
            "s": s, "P_s": round(P, 6),
            "eml": 1,
            "reason": "Poisson P(s) = e^{-s}: EML-1 (exponential = ground state of uncorrelated levels)",
        }

    def to_dict(self) -> dict:
        s_vals = [0.0, 0.5, 1.0, 1.5, 2.0, 3.0]
        lam_vals = [-1.8, -1.0, -0.5, 0.0, 0.5, 1.0, 1.8]
        return {
            "gue_spacing": [self.wigner_surmise_gue(s) for s in s_vals],
            "goe_spacing": [self.wigner_surmise_goe(s) for s in s_vals],
            "poisson_spacing": [self.poisson_spacing(s) for s in s_vals],
            "semicircle": [self.wigner_semicircle(lam) for lam in lam_vals],
            "dyson_index_eml": 0,
            "eml_GUE_spacing": 3,
            "eml_GOE_spacing": 3,
            "eml_poisson": 1,
            "eml_semicircle": 2,
            "eml_tracy_widom": EML_INF,
        }


@dataclass
class TracyWidomAndConnections:
    """
    Tracy-Widom distribution: fluctuations of the largest eigenvalue.

    F_2(t) = exp(-∫_t^∞ (x-t)·q(x)²dx) where q satisfies Painlevé II: q'' = tq + 2q³
    This is EML-∞: Painlevé II has no elementary solutions.

    KPZ-RMT connection: KPZ height h(t) - t ~ t^{1/3}·F_2 (Tracy-Widom).
    Both are EML-∞ — the same distribution describes:
    - Largest eigenvalue of GUE
    - Longest increasing subsequence of random permutation
    - KPZ height fluctuations
    - Longest common subsequence
    """

    def painleve_ii_eml(self) -> dict:
        return {
            "equation": "q'' = tq + 2q³ (Painlevé II)",
            "solution_type": "Transcendental — no closed form in elementary functions",
            "eml": EML_INF,
            "reason": "Painlevé II is EML-∞: outside elementary and algebraic functions, cannot be expressed in any finite EML tree",
            "tracy_widom": "F_2(t) = exp(-∫_t^∞ (x-t)q²dx): defined via Painlevé II solution → EML-∞",
        }

    def kpz_rmt_universality(self) -> dict:
        return {
            "universal_distribution": "Tracy-Widom F_2",
            "eml": EML_INF,
            "appears_in": [
                "Largest GUE eigenvalue fluctuation",
                "KPZ 1D height fluctuation t^{1/3}",
                "Longest increasing subsequence length fluctuation",
                "First passage time of TASEP",
                "Free energy of directed polymer",
            ],
            "mean_TW": round(-1.7711, 4),
            "variance_TW": round(0.8132, 4),
            "reason_inf": "All controlled by Painlevé II = EML-∞. The entire KPZ universality class has EML-∞ fluctuations.",
        }

    def to_dict(self) -> dict:
        return {
            "painleve_II": self.painleve_ii_eml(),
            "kpz_rmt_connection": self.kpz_rmt_universality(),
            "hierarchy": {
                "Edwards_Wilkinson": {"eml": 3, "fluctuations": "Gaussian (EML-3)"},
                "KPZ_1D": {"eml": EML_INF, "fluctuations": "Tracy-Widom (EML-∞)"},
                "MBE_growth": {"eml": EML_INF, "fluctuations": "Higher KPZ class"},
            },
        }


def analyze_kpz_eml() -> dict:
    kpz = KPZEquation()
    rmt = RandomMatrices()
    tw = TracyWidomAndConnections()
    return {
        "session": 117,
        "title": "KPZ Universality & Non-Equilibrium Growth: EML at the Edge",
        "key_theorem": {
            "theorem": "EML Non-Equilibrium Universality Theorem",
            "statement": (
                "KPZ nonlinear term (∇h)² breaks EML-3 (linear) to EML-∞ (fluctuations). "
                "KPZ scaling exponents (α=1/2, β=1/3, z=3/2) are EML-2 (rational). "
                "Cole-Hopf Z=exp(λh/2ν) maps EML-∞ height to EML-1 multiplicative noise. "
                "GUE/GOE level spacing P(s) ~ s^β·exp(-cs²) is EML-3. "
                "Wigner semicircle ~ √(R²-λ²) is EML-2. "
                "Poisson (integrable) level spacing exp(-s) is EML-1. "
                "Tracy-Widom F_2 (Painlevé II) is EML-∞. "
                "KPZ height fluctuations = largest GUE eigenvalue = EML-∞ universality class."
            ),
        },
        "kpz_equation": kpz.to_dict(),
        "random_matrices": rmt.to_dict(),
        "tracy_widom": tw.to_dict(),
        "eml_depth_summary": {
            "EML-0": "Dyson index β ∈ {1,2,4}; KPZ universality class membership (discrete label)",
            "EML-1": "Poisson level spacing exp(-s) (integrable = no repulsion); noise η per mode",
            "EML-2": "Wigner semicircle √(R²-λ²); KPZ exponents (rational); height variance t^{2/3}",
            "EML-3": "GUE P(s)~s²e^{-cs²}; GOE P(s)~se^{-cs²}; Edwards-Wilkinson (linear) fluctuations",
            "EML-∞": "Tracy-Widom F_2 (Painlevé II); KPZ height fluctuations; ASEP; longest increasing subsequence",
        },
        "rabbit_hole_log": [
            "The KPZ nonlinear term is the minimal perturbation that breaks EML-2: ∂h/∂t = ν∇²h (EML-3 solution) becomes EML-∞ with the addition of (λ/2)(∇h)² (EML-2 term). The EML-2 perturbation of an EML-3 linear equation produces EML-∞ fluctuations. This is the sharpest example of EML depth non-monotonicity under perturbation: adding an EML-2 term to an EML-3 equation jumps to EML-∞.",
            "Cole-Hopf appears again (Session 76, Burgers): Z=exp(h) maps EML-∞ to EML-1. The same transformation that solved Burgers equation maps KPZ to a stochastic heat equation. EML-1 is the 'solver' of EML-∞ problems via the exponential transformation. This pattern appears in: Burgers (S76), KPZ (S117), Black-Scholes (S95), and BCS gap (S108).",
            "Tracy-Widom is EML-∞ but with precise numerical values: mean -1.7711, variance 0.8132. These numbers are known to thousands of digits from the Painlevé II connection. EML-∞ doesn't mean 'we don't know the numbers' — it means there's no elementary formula. Tracy-Widom is the canonical example of an EML-∞ object that is completely characterized numerically.",
            "The KPZ-RMT connection is the deepest universality result since Ising: the Tracy-Widom distribution appears identically in KPZ height fluctuations, GUE largest eigenvalue, longest increasing subsequence, and free polymer energy. These EML-∞ problems all share the same Painlevé II transcendent. Universality = same EML-∞ fixed point.",
        ],
        "connections": {
            "to_session_76": "Burgers equation Cole-Hopf (S76) = KPZ Cole-Hopf (S117). Same EML-∞ → EML-1 transformation.",
            "to_session_57": "KPZ transition EML-3→EML-∞: adding nonlinear term crosses the universality class boundary. Same as Ising above T_c.",
        },
    }


if __name__ == "__main__":
    print(json.dumps(analyze_kpz_eml(), indent=2, default=str))
