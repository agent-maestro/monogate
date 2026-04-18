"""
Session 113 — Epidemiology & Contagion: EML of Spreading Processes

SIR model, R₀, herd immunity, network SIR, and opinion dynamics classified
by EML depth.

Key theorem: Epidemic exponential growth is EML-1. The epidemic threshold
R₀=1 is EML-∞ (phase transition = EML-∞). Herd immunity threshold 1-1/R₀
is EML-2. Endemic equilibrium is EML-1 (Boltzmann-like fixed point).
Information spreading has identical EML structure to biological contagion.
"""

from __future__ import annotations
import math, json
from dataclasses import dataclass, field


EML_INF = float("inf")


@dataclass
class SIRModel:
    """
    SIR compartmental model: S→I→R.
    dS/dt = -βSI/N, dI/dt = βSI/N - γI, dR/dt = γI.

    EML structure:
    - R₀ = β/γ: EML-0 (ratio of two rate constants)
    - Exponential growth rate: r = γ(R₀-1): EML-2 near threshold, EML-1 far above
    - Initial growth: I(t) ~ I₀·exp(r·t): EML-1
    - Epidemic threshold R₀=1: EML-∞ (susceptibility diverges → phase transition)
    - Herd immunity: p_c = 1 - 1/R₀: EML-2 (rational function of R₀)
    - Endemic equilibrium I*: EML-1 (fixed point of mean-field dynamics)
    - Final size: R∞ satisfies R∞ = 1 - exp(-R₀·R∞): EML-1 (transcendental eq in R∞)
    """

    def basic_reproduction_number(self, beta: float, gamma: float) -> dict:
        R0 = beta / gamma
        r = gamma * (R0 - 1)
        p_c = 1 - 1 / R0 if R0 > 1 else 0.0
        return {
            "beta": beta, "gamma": gamma,
            "R0": round(R0, 4),
            "growth_rate_r": round(r, 4),
            "herd_immunity_threshold": round(p_c, 4),
            "eml_R0": 0,
            "eml_growth_rate": 2,
            "eml_herd_immunity": 2,
            "reason_R0": "R₀ = β/γ: ratio of rate constants = EML-0",
            "reason_herd": "p_c = 1-1/R₀: rational function of R₀ = EML-2",
        }

    def sir_growth_phase(self, t: float, I0: float, r: float) -> dict:
        """Early exponential growth: I(t) ≈ I₀·exp(r·t)."""
        I = I0 * math.exp(r * t)
        return {
            "t": t, "I0": I0, "r": r,
            "I_t": round(I, 4),
            "eml": 1,
            "reason": "I(t) ≈ I₀·exp(rt): EML-1 (exponential growth = ground state of spreading)",
        }

    def final_size_equation(self, R0: float) -> dict:
        """
        Final size R∞: 1 - R∞ = exp(-R₀·R∞). Solve numerically.
        """
        if R0 <= 1:
            return {"R0": R0, "R_inf": 0.0, "eml": 1}
        R_inf = 0.0
        for _ in range(200):
            R_inf_new = 1 - math.exp(-R0 * R_inf)
            if abs(R_inf_new - R_inf) < 1e-10:
                break
            R_inf = R_inf_new
        return {
            "R0": R0,
            "R_inf": round(R_inf, 6),
            "eml": 1,
            "reason": "R∞ = 1 - exp(-R₀·R∞): fixed point of EML-1 map = EML-1 (same as quasispecies, S102)",
        }

    def endemic_equilibrium(self, R0: float, mu: float = 0.01) -> dict:
        """
        SIRS endemic equilibrium (with waning immunity μ):
        I* = μ(R₀-1)/(β) in simple form. Fixed point of mean-field dynamics.
        """
        if R0 <= 1:
            return {"R0": R0, "I_star": 0.0, "eml": 1, "regime": "disease-free"}
        I_star = (1 - 1/R0)
        return {
            "R0": R0, "mu": mu,
            "I_star_fraction": round(I_star, 4),
            "eml": 1,
            "reason": "I* = 1-1/R₀: fixed point = EML-1 (Boltzmann equilibrium of spreading dynamics)",
        }

    def threshold_phase_transition(self, R0_vals: list[float]) -> list[dict]:
        """Show the epidemic phase transition at R₀=1."""
        results = []
        for R0 in R0_vals:
            above = R0 > 1
            near = abs(R0 - 1.0) < 0.05
            eml = EML_INF if near else (1 if above else 0)
            results.append({
                "R0": round(R0, 3),
                "regime": "epidemic" if above else "subcritical",
                "near_critical": near,
                "eml": "∞" if eml == EML_INF else eml,
                "analogy": "Ising T_c; percolation p_c; AMOC threshold — all EML-∞",
            })
        return results

    def to_dict(self) -> dict:
        R0_examples = [0.5, 0.8, 0.95, 1.0, 1.05, 1.5, 2.0, 3.0, 5.0]
        return {
            "reproduction_numbers": [
                self.basic_reproduction_number(b, 0.1)
                for b in [0.05, 0.08, 0.15, 0.2, 0.5]
            ],
            "growth_phase": [self.sir_growth_phase(t, 10, 0.15) for t in [0, 5, 10, 20]],
            "final_sizes": [self.final_size_equation(R0) for R0 in [1.5, 2.0, 3.0, 5.0, 10.0]],
            "endemic": [self.endemic_equilibrium(R0) for R0 in [0.8, 1.5, 2.0, 5.0]],
            "phase_transition": self.threshold_phase_transition(R0_examples),
            "eml_R0": 0,
            "eml_growth": 1,
            "eml_herd_immunity": 2,
            "eml_threshold": EML_INF,
        }


@dataclass
class NetworkContagion:
    """
    Epidemic spreading on heterogeneous networks (Barabási-Albert, ER).

    EML structure:
    - ER threshold: β_c = γ·⟨k⟩/⟨k²⟩ = EML-2 (ratio of moments)
    - BA scale-free: β_c → 0 as N→∞ (no threshold!): special EML-∞
    - Mean-field on ER: I_k(t) = I_k·exp(r_k·t) with r_k = β·k - γ: EML-1 per degree class
    - Heterogeneous mean-field: ρ* = 1 - γ/β · ⟨k²⟩/⟨k⟩: EML-2
    - Super-spreaders (high-degree nodes): amplify by k²/⟨k⟩: EML-2
    """

    def er_threshold(self, k_mean: float, k2_mean: float, gamma: float) -> dict:
        """ER epidemic threshold: β_c = γ·⟨k⟩/⟨k²⟩."""
        beta_c = gamma * k_mean / k2_mean
        return {
            "k_mean": k_mean,
            "k2_mean": k2_mean,
            "gamma": gamma,
            "beta_c": round(beta_c, 6),
            "eml": 2,
            "reason": "β_c = γ⟨k⟩/⟨k²⟩: ratio of moments = EML-2",
        }

    def scale_free_threshold(self, gamma_sf: float = 3.0, N: int = 10000) -> dict:
        """For scale-free P(k)~k^{-γ_sf}, ⟨k²⟩ diverges → β_c → 0."""
        k_min = 1
        k_max = N
        if gamma_sf > 3:
            k2_mean = sum(k**(-gamma_sf+2) for k in range(k_min, k_max+1))
            k_mean = sum(k**(-gamma_sf+1) for k in range(k_min, k_max+1))
            beta_c_approx = k_mean / k2_mean
        else:
            k2_mean = float("inf")
            k_mean = sum(k**(-gamma_sf+1) for k in range(k_min, 1000))
            beta_c_approx = 0.0
        return {
            "gamma_sf": gamma_sf, "N": N,
            "k2_mean": round(k2_mean, 2) if k2_mean < 1e9 else "→∞",
            "beta_c": round(beta_c_approx, 6),
            "no_threshold": beta_c_approx < 1e-6,
            "eml_threshold": EML_INF if beta_c_approx < 1e-6 else 2,
            "reason": "Scale-free ⟨k²⟩→∞: β_c→0. No epidemic threshold = EML-∞ (always spreads)",
        }

    def to_dict(self) -> dict:
        return {
            "er_thresholds": [
                self.er_threshold(4, 20, 0.1),
                self.er_threshold(4, 100, 0.1),
            ],
            "scale_free": [
                self.scale_free_threshold(2.5),
                self.scale_free_threshold(3.0),
                self.scale_free_threshold(3.5),
            ],
            "eml_er_threshold": 2,
            "eml_ba_threshold": EML_INF,
            "super_spreader_amplification_eml": 2,
        }


@dataclass
class OpinionDynamics:
    """
    Information/opinion spreading: same EML structure as SIR.

    Models: DeGroot, Voter model, Deffuant bounded confidence.

    EML structure:
    - DeGroot consensus: x(t) = W^t·x(0) → W^∞·x(0) = EML-1 (dominant eigenvector)
    - Voter model: consensus time T ~ N·ln(N): EML-2 (N × log N)
    - Meme virality: R₀ analog for information = EML-0 (ratio)
    - Polarization threshold: EML-∞ (bifurcation in opinion space)
    - Echo chambers: isolated EML-1 fixed points (like multiple epidemic equilibria)
    - Social contagion threshold: same EML-∞ as R₀=1
    """

    def degroot_convergence(self, n: int, spectral_gap: float) -> dict:
        """DeGroot: consensus at rate exp(-t·gap). Convergence in T~1/gap steps."""
        T_mix = math.log(n) / spectral_gap if spectral_gap > 0 else float("inf")
        return {
            "n_agents": n,
            "spectral_gap": spectral_gap,
            "T_consensus_approx": round(T_mix, 2),
            "eml_dynamics": 1,
            "eml_mixing_time": 2,
            "reason": "DeGroot: x(t)→W^∞x₀ = dominant eigenvector: EML-1. Mixing T~ln(n)/gap: EML-2",
        }

    def voter_model(self, N: int) -> dict:
        """Voter model: expected consensus time ~ N·ln(N)."""
        T = N * math.log(N)
        return {
            "N": N,
            "T_consensus": round(T, 1),
            "eml": 2,
            "reason": "Voter model T ~ N·ln(N): EML-2 (product of N and ln N)",
        }

    def to_dict(self) -> dict:
        return {
            "degroot": [self.degroot_convergence(n, gap)
                        for n, gap in [(10, 0.3), (100, 0.1), (1000, 0.05)]],
            "voter_model": [self.voter_model(N) for N in [100, 1000, 10000]],
            "opinion_polarization": {
                "eml": EML_INF,
                "reason": "Bifurcation in opinion space = EML-∞ (same as epidemic threshold, Ising transition)",
            },
            "meme_R0": {"eml": 0, "reason": "Viral coefficient = ratio = EML-0 (like epidemic R₀)"},
            "echo_chamber_eml": 1,
        }


def analyze_epidemiology_eml() -> dict:
    sir = SIRModel()
    net = NetworkContagion()
    opinion = OpinionDynamics()
    return {
        "session": 113,
        "title": "Epidemiology & Contagion: EML of Spreading Processes",
        "key_theorem": {
            "theorem": "EML Contagion Theorem",
            "statement": (
                "R₀ = β/γ is EML-0 (ratio of rate constants). "
                "Epidemic exponential growth I(t)~exp(rt) is EML-1. "
                "Herd immunity threshold 1-1/R₀ is EML-2. "
                "Final size R∞ (fixed point of 1-exp(-R₀·R∞)) is EML-1. "
                "Endemic equilibrium I* = 1-1/R₀ is EML-1 (Boltzmann ground state). "
                "Epidemic threshold R₀=1 is EML-∞ (phase transition). "
                "ER network threshold β_c = γ⟨k⟩/⟨k²⟩ is EML-2. "
                "Scale-free network threshold β_c→0 is EML-∞ (always spreads). "
                "DeGroot consensus = EML-1 (dominant eigenvector). "
                "Opinion polarization = EML-∞ (bifurcation)."
            ),
        },
        "sir_model": sir.to_dict(),
        "network_contagion": net.to_dict(),
        "opinion_dynamics": opinion.to_dict(),
        "eml_depth_summary": {
            "EML-0": "R₀ = β/γ; meme virality coefficient; discrete SIR state count",
            "EML-1": "Exponential growth I~exp(rt); final size fixed point; endemic equilibrium; DeGroot consensus",
            "EML-2": "Herd immunity 1-1/R₀; ER network threshold ⟨k⟩/⟨k²⟩; voter consensus N·ln(N); super-spreader amplification k²/⟨k⟩",
            "EML-∞": "Epidemic threshold R₀=1; scale-free BA threshold → 0; opinion polarization bifurcation",
        },
        "rabbit_hole_log": [
            "The epidemic threshold is the social analog of every other EML-∞ phase transition: Ising T_c, percolation p_c, AMOC threshold, climate tipping — all EML-∞. R₀=1 is the universality class representative for social/biological spreading. Above R₀=1, the infected fraction jumps continuously from 0 to a finite value — same order parameter as the Ising magnetization.",
            "Scale-free networks have no epidemic threshold: for P(k)~k^{-γ} with γ≤3, ⟨k²⟩→∞ and β_c→0. Any disease spreads on a sufficiently large BA network. This is EML-∞ in the network-theoretic sense: no finite EML-2 threshold exists. The internet and social networks are scale-free, so information and malware spread inevitably.",
            "The final size equation R∞ = 1-exp(-R₀·R∞) is EML-1 by the same logic as the quasispecies (Session 102): it's a fixed point of an EML-1 map. The epidemic 'remembers' its own history through the exp(-R₀·R∞) term — the fraction of immune people suppresses the force of infection exponentially.",
            "DeGroot consensus = EML-1: W^t·x₀ → π (dominant eigenvector of W) as t→∞. Opinion averaging is PageRank (Session 104) applied to belief vectors. All consensus dynamics — from cells averaging chemical signals to democracies averaging votes — converge to EML-1 ground states.",
        ],
        "connections": {
            "to_session_57": "Epidemic threshold = EML-∞ phase transition. Same universality class as Ising, percolation, AMOC.",
            "to_session_104": "Network SIR threshold = graph spectral gap (EML-2). Scale-free → EML-∞ (no threshold). Confirms Session 104.",
        },
    }


if __name__ == "__main__":
    print(json.dumps(analyze_epidemiology_eml(), indent=2, default=str))
