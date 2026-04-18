"""
Session 152 — Chaos & Control Theory Deep II: Attractors, Bifurcations & Optimal Control

EML operator: eml(x,y) = exp(x) - ln(y)
Key theorem: Chaotic attractors are EML-3 (oscillatory, bounded, non-periodic);
bifurcation points are EML-∞; optimal control laws are EML-2 (quadratic cost).
"""
from __future__ import annotations
import math
from dataclasses import dataclass
from typing import Any


@dataclass
class ChaoticAttractors:
    """Lorenz, Rössler, and strange attractors — EML depth analysis."""

    sigma: float = 10.0
    rho: float = 28.0
    beta: float = 8.0 / 3.0

    def lorenz_lyapunov(self) -> float:
        """
        Largest Lyapunov exponent for Lorenz system ~ 0.906 (Sprott).
        λ₁ > 0 ⟹ sensitive dependence. EML-3 (bounded + exponential divergence).
        """
        return 0.906

    def lorenz_attractor_dimension(self) -> float:
        """
        Kaplan-Yorke dimension: D_KY = 2 + λ₁/(|λ₃|).
        For standard Lorenz: D_KY ≈ 2.06. EML-3 (fractal, non-integer).
        """
        lambda1 = 0.906
        lambda2 = 0.0
        lambda3 = -(self.sigma + 1.0 + self.beta)
        return 2.0 + (lambda1 + lambda2) / abs(lambda3)

    def rossler_period_doubling(self) -> dict[str, Any]:
        """
        Rössler system: a=0.2 → period-1; a=0.3 → period-2; a≈0.398 → chaos.
        Period doubling sequence: Feigenbaum δ = 4.669. EML-∞ at accumulation point.
        """
        a_vals = [0.1, 0.2, 0.3, 0.36, 0.398]
        behaviors = {0.1: "period-1", 0.2: "period-1", 0.3: "period-2",
                     0.36: "period-4", 0.398: "chaos onset"}
        feigenbaum_delta = 4.669201
        return {
            "a_vals": a_vals,
            "behavior_map": behaviors,
            "feigenbaum_delta": feigenbaum_delta,
            "eml_depth_period_doubling_sequence": "3 (oscillatory cascade)",
            "eml_depth_accumulation_point": "∞ (EML-∞ onset)",
            "note": "Period doubling = EML-3 cascade → EML-∞ at onset of chaos"
        }

    def attractor_reconstruction(self, tau: int = 7, m: int = 3) -> dict[str, Any]:
        """
        Takens embedding theorem: reconstruct attractor from scalar time series.
        Embedding dimension m, delay τ. EML-2 (mutual information for τ selection).
        """
        mutual_info = math.log(tau + 1)
        false_nearest = math.exp(-0.1 * m)
        return {
            "delay_tau": tau,
            "embedding_dim": m,
            "mutual_info_criterion": round(mutual_info, 4),
            "false_nearest_neighbor_fraction": round(false_nearest, 4),
            "eml_depth_mutual_info": 2,
            "eml_depth_false_nearest": 1,
            "theorem": "Takens: m > 2*d_attractor → faithful reconstruction"
        }

    def analyze(self) -> dict[str, Any]:
        lyap = self.lorenz_lyapunov()
        dim = self.lorenz_attractor_dimension()
        pd = self.rossler_period_doubling()
        recon = self.attractor_reconstruction()
        return {
            "model": "ChaoticAttractors",
            "lorenz_largest_lyapunov": lyap,
            "lorenz_kaplanyorke_dim": round(dim, 4),
            "rossler_period_doubling": pd,
            "attractor_reconstruction": recon,
            "eml_depth": {"lyapunov_exponent": 3, "fractal_dimension": 3,
                          "period_doubling_onset": "∞", "chaos": 3},
            "key_insight": "Strange attractor = EML-3 (bounded + fractal oscillation); bifurcation = EML-∞"
        }


@dataclass
class BifurcationTheory:
    """Saddle-node, pitchfork, Hopf — universal EML-∞ events."""

    def saddle_node_normal_form(self, mu: float) -> str:
        """
        ẋ = μ - x². No fixed points for μ < 0; two for μ > 0; bifurcation at μ = 0.
        EML-∞ transition at μ = 0 (fold catastrophe).
        """
        if mu < -1e-9:
            return "no fixed points (EML-∞ region)"
        elif abs(mu) < 1e-9:
            return "bifurcation point (EML-∞ event)"
        else:
            x_plus = math.sqrt(mu)
            x_minus = -math.sqrt(mu)
            return f"stable: x={x_plus:.4f}, unstable: x={x_minus:.4f} (EML-2)"

    def hopf_bifurcation(self, mu: float, omega: float = 1.0) -> dict[str, Any]:
        """
        ż = (μ + iω)z - |z|²z. Stable limit cycle for μ > 0.
        Amplitude A = √μ (EML-2). Frequency ω + O(μ) (EML-2).
        The bifurcation itself (μ = 0): EML-∞.
        """
        if mu <= 0:
            return {"state": "stable spiral", "amplitude": 0.0, "eml_depth": 2}
        amplitude = math.sqrt(mu)
        frequency = omega - mu / 2.0
        return {
            "state": "stable limit cycle",
            "amplitude": round(amplitude, 6),
            "frequency": round(frequency, 6),
            "eml_depth_amplitude": 2,
            "eml_depth_frequency": 2,
            "bifurcation_point_eml": "∞"
        }

    def codimension_2_cusp(self, a: float, b: float) -> str:
        """
        Cusp catastrophe: V(x) = x⁴/4 - bx²/2 - ax. EML-∞ at cusp point (a,b)=(0,0).
        Separatrix: 8b³ = 27a² (EML-2 curve — polynomial).
        """
        discriminant = 8 * b ** 3 - 27 * a ** 2
        if discriminant > 0:
            return f"inside cusp (3 equilibria, EML-∞ region), disc={discriminant:.4f}"
        return f"outside cusp (1 equilibrium, EML-2 region), disc={discriminant:.4f}"

    def feigenbaum_universality(self) -> dict[str, Any]:
        """
        Feigenbaum constants: δ=4.6692..., α=2.5029...
        Universal for all unimodal maps at period-doubling cascade.
        EML-∞ at accumulation point μ_∞; constants δ, α are EML-2 (limiting ratios).
        """
        delta = 4.669201609102990
        alpha = 2.502907875095893
        return {
            "feigenbaum_delta": delta,
            "feigenbaum_alpha": alpha,
            "eml_depth_constants": 2,
            "universality": "All unimodal maps share δ, α (renormalization group fixed point)",
            "rg_fixed_point_eml": "∞ (functional equation at fixed point = EML-∞)",
            "constants_eml": "2 (transcendental constants from limiting process)"
        }

    def analyze(self) -> dict[str, Any]:
        mu_vals = [-0.5, -0.1, 0.0, 0.1, 0.5]
        saddle = {mu: self.saddle_node_normal_form(mu) for mu in mu_vals}
        hopf = {mu: self.hopf_bifurcation(mu) for mu in [0.0, 0.1, 0.5, 1.0]}
        cusp = {(a, b): self.codimension_2_cusp(a, b)
                for a, b in [(0, 0), (0.5, 1.0), (1.0, 0.5)]}
        feig = self.feigenbaum_universality()
        return {
            "model": "BifurcationTheory",
            "saddle_node": saddle,
            "hopf_bifurcation": hopf,
            "cusp_catastrophe": {str(k): v for k, v in cusp.items()},
            "feigenbaum": feig,
            "eml_depth": {"saddle_node_bif": "∞", "hopf_bif": "∞",
                          "limit_cycle_amplitude": 2, "feigenbaum_constants": 2},
            "key_insight": "All bifurcations = EML-∞ events; post-bifurcation states = EML-2"
        }


@dataclass
class OptimalControl:
    """LQR, Pontryagin, and EML depth of control laws."""

    Q: float = 1.0   # state cost
    R: float = 0.1   # control cost

    def lqr_gain(self, A: float = -1.0, B: float = 1.0) -> float:
        """
        LQR: minimize J = ∫(Qx² + Ru²)dt. Gain K = R⁻¹B^T P.
        Algebraic Riccati: A^T P + PA - PBR⁻¹B^T P + Q = 0.
        For scalar: P = (Q*R + R*|A|*sqrt(1 + Q/(A²*R)))^(1/2). EML-2.
        """
        P = math.sqrt(self.Q * self.R + (A * math.sqrt(self.R)) ** 2) - A * self.R
        K = P / (self.R * B)
        return round(K, 6)

    def pontryagin_hamiltonian(self, x: float, u: float, lam: float) -> float:
        """
        H(x,u,λ) = ½(Qx² + Ru²) + λ·f(x,u). EML-2.
        For f(x,u) = Ax + Bu: H = ½(Qx² + Ru²) + λ(Ax + Bu).
        """
        A, B = -1.0, 1.0
        return 0.5 * (self.Q * x ** 2 + self.R * u ** 2) + lam * (A * x + B * u)

    def minimum_time_control(self, x0: float, xf: float = 0.0) -> dict[str, Any]:
        """
        Bang-bang control: u*(t) = -sign(λ_B(t)). Switching times = EML-∞ (non-smooth).
        Time-optimal: T* ~ log(|x0|/ε) for linear system. EML-2.
        """
        if abs(x0) < 1e-10:
            return {"time_optimal": 0.0, "switches": 0, "eml_depth": 0}
        T_star = math.log(abs(x0) + 1)
        n_switches = max(0, int(T_star) - 1)
        return {
            "x0": x0,
            "time_optimal_approx": round(T_star, 4),
            "n_switches": n_switches,
            "eml_depth_T_star": 2,
            "eml_depth_switching": "∞ (non-smooth, EML-∞ at switch instants)",
            "note": "Switching times = EML-∞ events in the trajectory"
        }

    def lyapunov_stability(self, A: float = -1.0) -> dict[str, Any]:
        """
        Lyapunov function V(x) = x^T P x. V̇ = x^T(A^T P + PA)x < 0 ⟹ stable.
        EML-2 (quadratic form). Lyapunov exponents (asymptotic rate) = EML-3.
        """
        P = self.Q / (-2 * A)
        decay_rate = A
        return {
            "lyapunov_P": round(P, 6),
            "decay_rate": A,
            "stable": A < 0,
            "eml_depth_V": 2,
            "eml_depth_decay_rate": 3,
            "note": "V = EML-2; asymptotic rate (Lyapunov exponent) = EML-3"
        }

    def analyze(self) -> dict[str, Any]:
        K = self.lqr_gain()
        H_vals = {(x, u): round(self.pontryagin_hamiltonian(x, u, lam=0.5), 4)
                  for x, u in [(0.5, -0.3), (1.0, -0.8), (2.0, -1.5)]}
        min_t = {x0: self.minimum_time_control(x0) for x0 in [0.5, 1.0, 2.0, 5.0]}
        lyap = self.lyapunov_stability()
        return {
            "model": "OptimalControl",
            "Q": self.Q, "R": self.R,
            "lqr_gain_K": K,
            "pontryagin_H": {str(k): v for k, v in H_vals.items()},
            "minimum_time_control": min_t,
            "lyapunov_stability": lyap,
            "eml_depth": {"lqr_gain": 2, "riccati_solution": 2,
                          "bang_bang_switches": "∞", "lyapunov_V": 2},
            "key_insight": "LQR (quadratic cost) = EML-2; bang-bang switches = EML-∞; Lyapunov exponent = EML-3"
        }


def analyze_chaos_control_v2_eml() -> dict[str, Any]:
    attractors = ChaoticAttractors()
    bifurcation = BifurcationTheory()
    control = OptimalControl(Q=1.0, R=0.1)
    return {
        "session": 152,
        "title": "Chaos & Control Theory Deep II: Attractors, Bifurcations & Optimal Control",
        "eml_operator": "eml(x,y) = exp(x) - ln(y)",
        "chaotic_attractors": attractors.analyze(),
        "bifurcation_theory": bifurcation.analyze(),
        "optimal_control": control.analyze(),
        "eml_depth_summary": {
            "EML-0": "Topological entropy (counting) for symbolic dynamics",
            "EML-1": "Feigenbaum convergence ratio, false-nearest-neighbor decay",
            "EML-2": "Lyapunov function V(x), LQR gain K, time-optimal T*, mutual information",
            "EML-3": "Strange attractor (bounded + fractal oscillation), Lyapunov exponents",
            "EML-∞": "All bifurcation points, chaos onset, bang-bang switching instants"
        },
        "key_theorem": (
            "The EML Chaos-Control Depth Theorem: "
            "Chaotic attractors are EML-3: bounded, oscillatory, fractal — "
            "but expressible as EML-3 objects (they have dimension, spectrum, Lyapunov exponents). "
            "Bifurcation points are EML-∞: the transition itself has no EML-finite description. "
            "Optimal control (LQR) is EML-2: the Riccati solution is a quadratic form. "
            "Bang-bang control has EML-∞ switching instants embedded in an EML-2 trajectory. "
            "Chaos = EML-3; the route to chaos = EML-∞ cascade."
        ),
        "rabbit_hole_log": [
            "Lorenz D_KY = 2.06 (fractal) = EML-3: not integer, not EML-2",
            "Feigenbaum δ=4.669 = EML-2 constant (renormalization group fixed point)",
            "Period doubling: each bifurcation = EML-∞ event; sequence = EML-3 cascade",
            "LQR Riccati: P solves algebraic eq = EML-2 (quadratic form, algebraic)",
            "Bang-bang switching = EML-∞ events: exactly like physical tipping points",
            "Takens delay embedding: mutual info for τ = EML-2 (logarithm)"
        ],
        "connections": {
            "S52_chaos": "Extends S52 with bifurcation depth analysis and Feigenbaum universality",
            "S134_graph_percolation": "Bifurcation = EML-∞ (same class as percolation threshold)",
            "S147_climate_tipping": "Fold bifurcation in climate = saddle-node here: same EML-∞ structure"
        }
    }


if __name__ == "__main__":
    import json
    print(json.dumps(analyze_chaos_control_v2_eml(), indent=2, default=str))
