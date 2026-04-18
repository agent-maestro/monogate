"""
Session 82 — Pseudo vs True Randomness: Chaos vs Stochastic Deep Comparison

Deep comparison: deterministic chaos (EML-2 short-time, EML-∞ long-time) vs
stochastic processes (EML-∞ paths, EML-3 expectations). Recurrence times,
invariant measures, and the EML depth of attractors.

Key theorem: A deterministic chaotic system and a stochastic process are
EML-indistinguishable at observation time scales larger than the Lyapunov time —
both are EML-∞ from an external observer's perspective.
"""

from __future__ import annotations
import math, json, random
from dataclasses import dataclass, field
from typing import Callable


EML_INF = float("inf")


@dataclass
class ChaoticAttractor:
    """
    Strange attractor: fractal set in phase space with SRB (Sinai-Ruelle-Bowen) measure.

    EML depth of attractor properties:
    - Lyapunov exponent λ > 0: EML-1 (divergence rate = exp(λt))
    - Attractor dimension d_H (Hausdorff): EML-2 (Kaplan-Yorke formula: rational + log)
    - SRB measure μ_SRB: EML-∞ (fractal, not absolutely continuous)
    - Invariant density (if exists): EML-1 or EML-2 for simple attractors
    """
    name: str
    lyapunov_exponent: float
    correlation_dimension: float
    kaplan_yorke_dim: float
    eml_attractor: float
    eml_reason: str

    def recurrence_time(self, epsilon: float) -> float:
        """Kac's lemma: mean recurrence time ~ 1/μ(B_ε) ~ ε^{-d_H} → EML-2 power law."""
        return epsilon ** (-self.kaplan_yorke_dim)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "lyapunov_exponent": self.lyapunov_exponent,
            "correlation_dimension": self.correlation_dimension,
            "kaplan_yorke_dim": round(self.kaplan_yorke_dim, 4),
            "recurrence_time_epsilon_0.01": round(self.recurrence_time(0.01), 4),
            "eml_attractor": "∞" if self.eml_attractor == EML_INF else self.eml_attractor,
            "eml_reason": self.eml_reason,
        }


ATTRACTORS = [
    ChaoticAttractor(
        "Logistic map (r=3.9)", 0.486, 0.97, 1.0, EML_INF,
        "Strange attractor: Cantor-set-like structure = fractal = EML-∞; SRB measure is EML-∞",
    ),
    ChaoticAttractor(
        "Hénon map", 0.42, 1.26, 1.26, EML_INF,
        "Fractal attractor with dimension 1.26 (non-integer) → EML-∞; SRB measure not smooth",
    ),
    ChaoticAttractor(
        "Circle map (rotation by √2)", 0.0, 1.0, 1.0, 3,
        "Quasi-periodic on circle: trajectory dense but EML-3 (parametrized by exp(2πi√2·n))",
    ),
    ChaoticAttractor(
        "Lorenz attractor", 0.906, 2.06, 2.06, EML_INF,
        "Butterfly wings: fractal, non-integer Hausdorff dimension → EML-∞",
    ),
]


@dataclass
class LyapunovTime:
    """
    Below the Lyapunov time τ_L = 1/λ: deterministic, EML-2.
    Above τ_L: chaotic, EML-∞ in practice.

    EML transition horizon:
    - t << τ_L: trajectory predictable, EML-2 (finite truncation of Taylor series)
    - t ≈ τ_L: perturbations amplified by exp(1) → EML-1 sensitivity
    - t >> τ_L: effectively random, EML-∞ from any finite-precision initial condition

    Connection to randomness:
    A chaotic trajectory with EML-2 initial condition after n·τ_L steps has
    EML depth approximately EML-∞: the finite-precision representation has been
    "randomized" by the exponential sensitivity.
    """
    lyapunov: float  # λ > 0

    def predict_horizon(self, initial_precision_bits: int = 64) -> dict:
        """How many steps can we predict with `initial_precision_bits` precision?"""
        n_steps = int(initial_precision_bits * math.log(2) / self.lyapunov)
        return {
            "lyapunov_exponent": self.lyapunov,
            "initial_precision_bits": initial_precision_bits,
            "predictable_steps": n_steps,
            "predictable_time_tau_L": round(n_steps / (1 / self.lyapunov), 2),
            "eml_short_time": "EML-2 (deterministic, closed form)",
            "eml_long_time": "EML-∞ (EML-2 initial condition → EML-∞ after n·τ_L steps)",
        }


@dataclass
class SDEvsODE:
    """
    Comparison of SDE (stochastic) and chaotic ODE (deterministic):

    SDE: dX = f(X)dt + σdW  — X_t is EML-∞ (Brownian noise)
    ODE: dx/dt = g(x)       — x_t is EML-2 short-time, EML-∞ long-time

    Observable distinction:
    - Power spectrum: SDE → flat (white noise = EML-∞); ODE → peaks at Lyapunov exponents
    - Autocorrelation: SDE → delta function; ODE chaotic → exponential decay C(τ)~exp(-λτ) = EML-1
    - Finite-time Lyapunov: SDE → 0 (no sensitivity); ODE → λ > 0

    EML indistinguishability theorem: for t >> τ_L, chaotic ODE and SDE are
    EML-∞ indistinguishable from observations of a finite window.
    """

    @staticmethod
    def autocorrelation_comparison() -> dict:
        return {
            "chaotic_ode": {
                "autocorrelation": "C(τ) ~ exp(-λτ): EML-1 exponential decay",
                "power_spectrum": "Broad band with peaks: rational + EML-3",
                "eml_short": 2,
                "eml_long": "∞",
            },
            "sde_brownian": {
                "autocorrelation": "C(τ) = δ(τ): EML-∞ (Dirac delta)",
                "power_spectrum": "White noise: flat = EML-∞",
                "eml_path": "∞",
                "eml_expectation": 3,
            },
            "indistinguishability": (
                "For t >> τ_L = 1/λ, a chaotic ODE and an SDE with matched mean/variance "
                "are EML-∞ indistinguishable: both generate sequences with K(x_n) ≈ Θ(n)."
            ),
        }

    @staticmethod
    def invariant_measure_eml() -> dict:
        return {
            "periodic_orbit": {"eml": 0, "description": "Dirac masses on periodic points: EML-0"},
            "quasi_periodic": {"eml": 3, "description": "Lebesgue measure on torus: EML-3 (parametrized by angles)"},
            "srb_measure_chaotic": {"eml": "∞", "description": "Fractal SRB measure: EML-∞"},
            "gaussian_sde": {"eml": 1, "description": "Ornstein-Uhlenbeck stationary measure = Gaussian = EML-1"},
            "poisson_sde": {"eml": 1, "description": "Stationary measure of counting process = Poisson = EML-1"},
        }


def analyze_chaos_stochastic_eml() -> dict:
    attractors_report = [a.to_dict() for a in ATTRACTORS]
    lyapunov = LyapunovTime(lyapunov=0.5)
    sde_ode = SDEvsODE()
    return {
        "session": 82,
        "title": "Pseudo vs True Randomness: Chaos vs Stochastic Deep",
        "key_theorem": {
            "theorem": "EML Indistinguishability Theorem",
            "statement": (
                "For observation windows t >> τ_L = 1/λ, a deterministic chaotic system "
                "and an SDE with matched statistics are EML-∞ indistinguishable: "
                "both generate sequences with K(x_n) ≈ Θ(n) (incompressible). "
                "The distinction (deterministic vs stochastic) is only visible at t << τ_L (EML-2)."
            ),
        },
        "strange_attractors": attractors_report,
        "lyapunov_time": lyapunov.predict_horizon(64),
        "sde_vs_ode": sde_ode.autocorrelation_comparison(),
        "invariant_measures": sde_ode.invariant_measure_eml(),
        "eml_depth_summary": {
            "EML-0": "Periodic orbit invariant measure; fixed points",
            "EML-1": "Autocorrelation decay exp(-λτ); Ornstein-Uhlenbeck stationary measure; Gaussian SDE",
            "EML-2": "Short-time ODE trajectory; Kaplan-Yorke dimension; recurrence time power law",
            "EML-3": "Quasi-periodic invariant measure; torus parametrization",
            "EML-∞": "Strange attractor SRB measure; Brownian paths; chaotic trajectories t>>τ_L",
        },
        "connections": {
            "to_session_71": "Session 71: PRNG=EML-2. Session 82: chaos also EML-2 short-time → EML-∞ long-time",
            "to_session_64": "SDE paths = EML-∞; expectations = EML-3 (Feynman-Kac). Session 82 compares to chaos.",
        },
    }


if __name__ == "__main__":
    print(json.dumps(analyze_chaos_stochastic_eml(), indent=2, default=str))
