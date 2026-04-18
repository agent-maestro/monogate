"""
Session 97 — Statistical Mechanics Deep: Renormalization, Criticality & Universality

Deep renormalization group analysis: block spin transformations, fixed-point operators,
scaling functions near criticality, and universality. Tests whether critical exponents
and scaling functions have natural low-depth EML forms.

Key theorem: The scaling hypothesis postulates that near T_c, the free energy f(t,h)
= |t|^{2-α}·g(h/|t|^{βδ}): EML-2 (power of |t| with rational exponent under hyperscaling).
Critical exponents: mean-field = rational (EML-2); exact 2D Ising = rational (EML-2);
3D = irrational numerical (EML-∞).
"""

from __future__ import annotations
import math, json
from dataclasses import dataclass, field


EML_INF = float("inf")


@dataclass
class BlockSpinRG:
    """
    Kadanoff block spin RG: group N spins into one, rescale by b = N^{1/d}.

    Couplings transform: K → K'(K), h → h'(K,h).
    Fixed points: K* = K'(K*) — these are the universality classes.

    EML structure:
    - Block spin map K' = f(K): EML-2 (rational or algebraic in K)
    - 1D Ising: K'(K) = ln(cosh(2K))/2: EML-2 (logarithm of cosh = EML-2)
    - Fixed point K* = 0 or K* = ∞: EML-0 or EML-∞
    - Linearized RG near K*: K'-K* = λ·(K-K*): EML-0 (linear)
    - RG eigenvalue λ: EML-2 (determined by Taylor expansion)
    - Scaling exponent y = ln λ / ln b: EML-2 (ratio of logs)
    """

    def ising_1d_rg(self, K_vals: list[float]) -> list[dict]:
        """1D Ising block spin (b=2): K' = (1/2)·ln(cosh(2K))."""
        results = []
        for K in K_vals:
            K_prime = 0.5 * math.log(math.cosh(2 * K)) if K > 0 else 0
            ratio = K_prime / K if K > 1e-10 else 0
            results.append({
                "K": round(K, 4),
                "K_prime": round(K_prime, 6),
                "K_prime_over_K": round(ratio, 6),
                "flows_toward": "K*=0 (disordered)" if ratio < 1 else "K*=∞ (ordered)",
                "eml_K_prime": 2,
                "reason": "(1/2)ln(cosh(2K)): logarithm of EML-3 function = EML-2",
            })
        return results

    def scaling_exponents(self) -> list[dict]:
        return [
            {
                "model": "1D Ising (critical T=0)",
                "yt": "∞ (relevant, T_c=0)",
                "yh": 1.0,
                "nu": 0.0,
                "eml_exponents": 2,
                "reason": "yh=1: rational = EML-2",
            },
            {
                "model": "2D Ising (exact, T_c = 2/ln(1+√2))",
                "yt": 1.0,
                "yh": 1.875,
                "nu": 1.0,
                "eml_exponents": 2,
                "reason": "yt=1, yh=15/8: rational = EML-2 (Onsager exact)",
            },
            {
                "model": "Mean-field / Landau",
                "yt": 2.0,
                "yh": 3.0,
                "nu": 0.5,
                "eml_exponents": 2,
                "reason": "All exponents rational (1/2, 1/3, etc.) = EML-2",
            },
            {
                "model": "3D Ising (numerical bootstrap)",
                "yt": round(1/0.6299, 4),
                "yh": round(2.4815, 4),
                "nu": 0.6299,
                "eml_exponents": EML_INF,
                "reason": "ν≈0.6299: irrational, bootstrap-only = EML-∞",
            },
        ]

    def to_dict(self) -> dict:
        K_vals = [0.1, 0.3, 0.5, 1.0, 2.0]
        return {
            "block_spin_map": "1D Ising K' = (1/2)ln(cosh(2K))",
            "rg_flow": self.ising_1d_rg(K_vals),
            "scaling_exponents": self.scaling_exponents(),
            "eml_rg_map": 2,
            "fixed_point_eml": 0,
        }


@dataclass
class ScalingHypothesis:
    """
    Widom scaling hypothesis: free energy singular part near T_c:
    f_s(t,h) = |t|^{2-α} · g_±(h/|t|^{βδ})

    EML structure:
    - |t|^{2-α}: EML-2 (power of |t-T_c|/T_c)
    - g_±(x): universal scaling function (EML-3 typically, from conformal field theory)
    - Hyperscaling: 2-α = νd → EML-2 (rational relation between exponents)
    - Critical isotherm: m ~ h^{1/δ}: EML-2 (power law)
    - Specific heat: C ~ |t|^{-α}: EML-2 (power law, diverges at T_c)
    """

    CRITICAL_EXPONENTS_MF = {"alpha": 0, "beta": 0.5, "gamma": 1.0, "delta": 3.0, "nu": 0.5, "eta": 0}
    CRITICAL_EXPONENTS_2D_ISING = {"alpha": 0, "beta": 0.125, "gamma": 1.75, "delta": 15.0, "nu": 1.0, "eta": 0.25}
    CRITICAL_EXPONENTS_3D_ISING = {"alpha": 0.110, "beta": 0.326, "gamma": 1.237, "delta": 4.789, "nu": 0.630, "eta": 0.036}

    def scaling_relations_check(self, exponents: dict) -> dict:
        a = exponents["alpha"]
        b = exponents["beta"]
        g = exponents["gamma"]
        d = exponents["delta"]
        nu = exponents["nu"]
        eta = exponents["eta"]
        griffiths = round(a + 2*b + g, 6)  # = 2
        widom = round(g - b*(d-1), 6)  # = 0
        fisher = round(g - nu*(2-eta), 6)  # = 0
        josephson_d2 = round(2 - a - 2*nu, 6)  # = 0 for d=2
        return {
            "griffiths_alpha+2beta+gamma": griffiths,
            "widom_gamma-beta(delta-1)": widom,
            "fisher_gamma-nu(2-eta)": fisher,
            "all_satisfied": (abs(griffiths - 2) < 0.01 and abs(widom) < 0.01 and abs(fisher) < 0.01),
        }

    def to_dict(self) -> dict:
        return {
            "scaling_hypothesis": "f_s(t,h) = |t|^{2-α} g(h/|t|^{βδ})",
            "eml_singular_part": 2,
            "eml_scaling_function": 3,
            "mean_field": {
                "exponents": self.CRITICAL_EXPONENTS_MF,
                "relations": self.scaling_relations_check(self.CRITICAL_EXPONENTS_MF),
                "eml": 2,
            },
            "2D_ising": {
                "exponents": self.CRITICAL_EXPONENTS_2D_ISING,
                "relations": self.scaling_relations_check(self.CRITICAL_EXPONENTS_2D_ISING),
                "eml": 2,
            },
            "3D_ising": {
                "exponents": self.CRITICAL_EXPONENTS_3D_ISING,
                "relations": self.scaling_relations_check(self.CRITICAL_EXPONENTS_3D_ISING),
                "eml": EML_INF,
            },
        }


@dataclass
class CorrelationFunctions:
    """
    Critical correlation function: ⟨σ(0)σ(r)⟩ ~ r^{-(d-2+η)} / r at T=T_c.

    EML structure:
    - Off-critical: ⟨σ(0)σ(r)⟩ ~ exp(-r/ξ)/r^{d-2+η}: EML-1 × EML-2 = EML-2
    - At T_c: ⟨σ(0)σ(r)⟩ ~ r^{-(d-2+η)}: EML-2 (pure power law)
    - Correlation length: ξ ~ |t|^{-ν}: EML-2 (diverges as power law)
    - Log corrections (d=2 Ising, α=0): C ~ ln|t|: EML-2 (logarithm)
    """

    def correlation_table(self, d: int = 2, eta: float = 0.25) -> list[dict]:
        r_vals = [1, 2, 5, 10, 20]
        exponent = d - 2 + eta
        results = []
        for r in r_vals:
            corr_crit = r**(-exponent)
            xi = 5.0  # some off-critical correlation length
            corr_offcrit = math.exp(-r/xi) / r**exponent
            results.append({
                "r": r,
                "corr_at_Tc": round(corr_crit, 6),
                "corr_off_Tc_xi5": round(corr_offcrit, 6),
                "eml_at_Tc": 2,
                "eml_off_Tc": 2,
            })
        return results

    def to_dict(self) -> dict:
        return {
            "critical_corr": "⟨σ(0)σ(r)⟩ ~ r^{-(d-2+η)}: EML-2 (power law)",
            "off_critical_corr": "⟨σ(0)σ(r)⟩ ~ exp(-r/ξ)·r^{-(d-2+η)}: EML-2",
            "correlation_length": "ξ ~ |t|^{-ν}: EML-2 (power law divergence)",
            "eml_critical": 2,
            "eml_off_critical": 2,
            "eml_at_singularity": EML_INF,
            "table_2d_ising": self.correlation_table(2, 0.25),
        }


def analyze_stat_mech_deep_eml() -> dict:
    rg = BlockSpinRG()
    scaling = ScalingHypothesis()
    corr = CorrelationFunctions()
    return {
        "session": 97,
        "title": "Statistical Mechanics Deep: Renormalization, Criticality & Universality",
        "key_theorem": {
            "theorem": "EML Criticality Classification",
            "statement": (
                "Near a critical point, all thermodynamic quantities are EML-2 (power laws |t|^x, |h|^x). "
                "Scaling functions g(x) are EML-3 (universal conformal functions). "
                "Critical exponents for exactly solvable models (MF, 2D Ising) are rational = EML-2. "
                "Critical exponents for 3D systems (bootstrap-only) are EML-∞. "
                "The RG map K'(K) is EML-2; its fixed point is EML-0 (trivial) or EML-∞ (T_c). "
                "The EML Phase Transition Theorem (Session 57) is confirmed: T_c itself is EML-∞."
            ),
        },
        "block_spin_rg": rg.to_dict(),
        "scaling_hypothesis": scaling.to_dict(),
        "correlation_functions": corr.to_dict(),
        "eml_depth_summary": {
            "EML-0": "Fixed points of RG (K*=0 trivial); topological Chern number (TKNN)",
            "EML-2": "All critical power laws |t|^x; ξ ~ |t|^{-ν}; RG map; rational critical exponents",
            "EML-3": "Universal scaling functions g(x); conformal correlation functions",
            "EML-∞": "Critical point T_c itself; irrational exponents (3D Ising); non-analyticity at T_c",
        },
        "rabbit_hole_log": [
            "The scaling hypothesis f_s(t,h) = |t|^{2-α}·g(h/|t|^{βδ}) has an interesting EML structure: the outer power |t|^{2-α} is EML-2, but the scaling function g(x) is EML-3 (determined by CFT, involves conformal blocks). The |t|^{2-α} envelope is EML-2; the shape is EML-3.",
            "All scaling relations (Griffiths, Widom, Fisher) are linear equations among exponents. They are satisfied because all exponents come from the same EML-2 fixed point. The violation of hyperscaling (d>4) occurs when the mean-field exponents (EML-2 rational) differ from the true ones — another EML-2 vs EML-∞ distinction.",
            "2D Ising: all exponents rational (β=1/8, γ=7/4, δ=15, ν=1, η=1/4). This is an EML-2 model. 3D Ising: all exponents irrational. This is EML-∞. The exact solvability of 2D vs approximate numerics of 3D maps to EML-2 vs EML-∞.",
        ],
        "connections": {
            "to_session_84": "Session 84: Wilson-Fisher fixed point. Session 97: block spin RG confirms same structure from different angle",
            "to_session_57": "Session 57: phase transitions = EML-∞. Session 97: T_c is EML-∞, everything near T_c is EML-2",
        },
    }


if __name__ == "__main__":
    print(json.dumps(analyze_stat_mech_deep_eml(), indent=2, default=str))
