"""
Session 98 — QFT Deep: Interacting Theories, Confinement & Non-Perturbative Effects

Non-perturbative QCD: instantons, monopoles, confinement string tension, Schwinger model,
large-N expansion, and the EML depth of non-perturbative effects.

Key theorem: Instantons are EML-1 (exp(-S_inst/g²)). Confinement string tension
σ ~ Λ_QCD² = (μ·exp(-c/g²))²: EML-1 (double exp structure = EML-1 of EML-2 argument).
The confinement transition at Λ_QCD is EML-∞ (Session 75). Large-N planar diagrams
are EML-2 (1/N² corrections).
"""

from __future__ import annotations
import math, json
from dataclasses import dataclass, field


EML_INF = float("inf")


@dataclass
class InstantonPhysics:
    """
    Instantons: classical solutions to Euclidean Yang-Mills in finite action.
    Self-dual: F^{μν} = ±F̃^{μν}

    EML structure:
    - Instanton action S_inst = 8π²/g²: EML-2 (rational × 1/g²)
    - Instanton amplitude: exp(-S_inst) = exp(-8π²/g²): EML-1 (single exp atom)
    - g² running: g²(μ) = g²₀/(1 + β₀g²₀·ln(μ/μ₀)/16π²): EML-2 (log = EML-2)
    - Instanton size distribution ρ^{-5}·exp(-8π²/g²(ρ)): EML-1 × EML-2 = EML-2
    - Vacuum tunneling rate: Γ ~ exp(-S_inst) = EML-1 (non-perturbative, invisible in pert. theory)
    """

    def instanton_amplitude(self, g_sq: float) -> dict:
        s_inst = 8 * math.pi**2 / g_sq
        amp = math.exp(-s_inst) if s_inst < 700 else 0.0
        return {
            "g_squared": g_sq,
            "S_inst": round(s_inst, 6),
            "amplitude_exp_minus_S": amp,
            "eml": 1,
            "reason": "exp(-8π²/g²): single exp = EML-1 (non-perturbative: invisible order by order in g²)",
        }

    def dilute_gas_density(self, g_sq: float, mu_scale: float = 1.0) -> dict:
        """Instanton density n_inst ~ (1/ρ^5)·exp(-8π²/g²(ρ)) at ρ ~ 1/μ."""
        s = 8 * math.pi**2 / g_sq
        n = mu_scale**4 * math.exp(-s) if s < 700 else 0.0
        return {
            "g_squared": g_sq,
            "n_inst_density": n,
            "eml": 2,
            "reason": "n ~ μ⁴·exp(-8π²/g²): EML-2 (exp argument g²(ρ) has log = EML-2 running)",
        }

    def to_dict(self) -> dict:
        g_sq_vals = [0.5, 1.0, 2.0, 4.0]
        return {
            "instanton_action": "S_inst = 8π²/g²: EML-2",
            "amplitudes": [self.instanton_amplitude(g) for g in g_sq_vals],
            "density": [self.dilute_gas_density(g) for g in g_sq_vals],
            "topological_charge": "Q = (1/16π²)∫TrF∧F ∈ ℤ: EML-0 (integer)",
            "eml_amplitude": 1,
            "eml_perturbative": 2,
        }


@dataclass
class ConfinementString:
    """
    Confinement in QCD: quarks are permanently bound; the potential V(r) ~ σ·r (linear).
    String tension σ ~ Λ_QCD².

    Λ_QCD dimensional transmutation: g²(Λ_QCD) = ∞ → Λ_QCD = μ·exp(-c/g²(μ)).
    This is the most dramatic EML structure in QFT:
    - Λ_QCD = μ·exp(-8π²/(β₀·g²)): EML-1 (exp of EML-2 = EML-1 × EML-2)
    - σ ~ Λ_QCD²: EML-2 (square of EML-1 = EML-2... but log(σ) = EML-1!)
    - Wilson loop W(C) = exp(-σ·Area): EML-1 (exp of area law)
    - Deconfinement transition at T = T_deconf ~ Λ_QCD: EML-∞ (phase transition)
    """

    def dimensional_transmutation(self, g_sq: float, mu: float = 1.0, beta0: float = 11.0) -> dict:
        """Λ_QCD = μ·exp(-8π²/(β₀·g²))."""
        exponent = -8 * math.pi**2 / (beta0 * g_sq)
        Lambda_QCD = mu * math.exp(exponent) if exponent > -700 else 0.0
        string_tension = Lambda_QCD**2
        return {
            "g_squared": g_sq,
            "mu": mu,
            "Lambda_QCD": Lambda_QCD,
            "string_tension_sigma": string_tension,
            "eml_Lambda": 1,
            "eml_sigma": 2,
            "reason": "Λ = μ·exp(-8π²/β₀g²) = μ × (EML-1 atom). σ = Λ² = (EML-1)² = EML-2",
        }

    def wilson_loop_area_law(self, sigma: float, area: float) -> dict:
        """W(C) = exp(-σ·Area) for large loops (confinement)."""
        w = math.exp(-sigma * area) if sigma * area < 700 else 0.0
        return {
            "sigma": sigma,
            "area": area,
            "W_C": w,
            "eml": 1,
            "reason": "W(C) = exp(-σ·Area): EML-1 (single exp = area law of confinement)",
        }

    def to_dict(self) -> dict:
        g_sq_vals = [0.5, 1.0, 2.0]
        return {
            "dimensional_transmutation": [self.dimensional_transmutation(g) for g in g_sq_vals],
            "wilson_loop": [self.wilson_loop_area_law(0.18, A) for A in [1, 4, 9, 16]],
            "eml_Lambda_QCD": 1,
            "eml_string_tension": 2,
            "eml_deconfinement": EML_INF,
            "depth_summary": "Λ_QCD = EML-1; σ = EML-2; deconfinement phase transition = EML-∞",
        }


@dataclass
class LargeNExpansion:
    """
    't Hooft large-N limit: N_c → ∞ with λ = g²N_c fixed (t'Hooft coupling).

    EML structure:
    - Planar diagrams (topology = sphere): leading order in 1/N_c
    - 1/N_c expansion: F = N_c²·f₀ + f₁ + (1/N_c²)·f₂ + ...: EML-2 (power series in 1/N_c)
    - t'Hooft coupling λ = g²N_c: EML-0 × EML-2 = EML-2
    - Matrix model: partition function = integral over N×N matrices: EML-2 (Gaussian integral)
    - AdS/CFT: string theory description = N_c = ∞ limit = EML-3 (string amplitudes)
    """

    def free_energy_expansion(self, N_c: int, g_sq: float) -> dict:
        lam = g_sq * N_c  # t'Hooft coupling
        f0 = 1.0  # planar amplitude (normalized)
        f1 = 0.2  # torus
        f2 = 0.05  # genus 2
        F = N_c**2 * f0 + f1 + f2 / N_c**2
        return {
            "N_c": N_c,
            "lambda_tHooft": round(lam, 4),
            "F_free_energy": round(F, 6),
            "leading_N_c_sq": round(N_c**2 * f0, 2),
            "subleading_torus": f1,
            "subsubleading": round(f2 / N_c**2, 8),
            "eml": 2,
            "reason": "F = N_c²f₀ + f₁ + 1/N_c²·f₂: power series in N_c = EML-2",
        }

    def maldacena_conjecture(self) -> dict:
        return {
            "conjecture": "AdS/CFT: N=4 SYM at large N_c ↔ Type IIB string on AdS₅×S⁵",
            "eml_CFT": 3,
            "eml_string": 3,
            "eml_gravity_regime": 2,
            "reason": "CFT operators = EML-3 (conformal blocks); string amplitudes = EML-3; classical gravity (N→∞) = EML-2",
            "strong_coupling": "λ → ∞: classical gravity description = EML-2; weak coupling: gauge theory = EML-3",
        }

    def to_dict(self) -> dict:
        return {
            "free_energy": [self.free_energy_expansion(N, 0.1) for N in [3, 10, 100]],
            "maldacena": self.maldacena_conjecture(),
            "eml_large_N": 2,
            "insight": "Large-N is a topological expansion: each genus contributes N_c^{2-2g} = EML-2 factor",
        }


def analyze_qft_confinement_eml() -> dict:
    inst = InstantonPhysics()
    conf = ConfinementString()
    largeN = LargeNExpansion()
    return {
        "session": 98,
        "title": "QFT Deep: Confinement, Instantons & Non-Perturbative Effects",
        "key_theorem": {
            "theorem": "EML Non-Perturbative QFT Theorem",
            "statement": (
                "Instantons contribute exp(-8π²/g²) = EML-1 to vacuum amplitudes — "
                "invisible to all orders in perturbation theory (EML-2). "
                "Dimensional transmutation Λ_QCD = μ·exp(-8π²/β₀g²) is EML-1 (single exp). "
                "String tension σ ~ Λ_QCD² is EML-2. "
                "Wilson area law W(C) = exp(-σ·Area) is EML-1. "
                "Large-N expansion is EML-2 (power series in 1/N_c²). "
                "The deconfinement phase transition at T_c ~ Λ_QCD is EML-∞ (Session 57 PT theorem). "
                "Non-perturbative physics lives at EML-1 depth — one level below perturbative EML-2."
            ),
        },
        "instantons": inst.to_dict(),
        "confinement": conf.to_dict(),
        "large_N": largeN.to_dict(),
        "eml_depth_summary": {
            "EML-0": "Topological charge Q ∈ ℤ; instanton winding number; Euler characteristic of gauge bundle",
            "EML-1": "Instanton amplitude exp(-8π²/g²); Λ_QCD dimensional transmutation; Wilson area law exp(-σA)",
            "EML-2": "Running coupling g²(μ) via ln(μ); large-N expansion 1/N²; string tension Λ²; planar diagrams",
            "EML-3": "CFT operators; string amplitudes (AdS/CFT); perturbative Feynman diagrams (EML-2 propagators + EML-3 loops)",
            "EML-∞": "Deconfinement phase transition; QCD vacuum structure (non-abelian = EML-∞ topology)",
        },
        "rabbit_hole_log": [
            "Non-perturbative = EML-1: the key insight is that non-perturbative physics (instantons, tunneling, confinement) lives at EML-1 depth, BELOW perturbative corrections (EML-2). This is the opposite of the usual ordering: non-pert effects are typically exponentially smaller, but they're EML simpler.",
            "Λ_QCD = μ·exp(-c/g²(μ)): this is EML-1 (single exp of EML-2 argument). The running coupling in the exponent is EML-2 (involves ln μ). So Λ_QCD is EML-1 composed with EML-2 = stays EML-1 (exp is the outermost gate).",
            "Large-N and topology: the genus expansion N_c^{2-2g} is EML-2 (power of N_c). The Euler characteristic 2-2g is EML-0. The full partition function Z = Σ_g N_c^{2-2g} f_g(λ) combines EML-0 (topology), EML-2 (large-N), and EML-3 (f_g = string amplitudes).",
        ],
        "connections": {
            "to_session_75": "Session 75: confinement = EML-∞ phase transition. Session 98: the non-perturbative mechanism (instantons) is EML-1",
            "to_session_84": "Session 84: Wilson RG fixed point = EML-2. Session 98: large-N is also EML-2 — both are perturbative/semiclassical",
        },
    }


if __name__ == "__main__":
    print(json.dumps(analyze_qft_confinement_eml(), indent=2, default=str))
