"""
Session 206 — Ergodic Theory: Mixing, Birkhoff's Theorem & Entropy

EML operator: eml(x,y) = exp(x) - ln(y)
Key theorem: Birkhoff time average = EML-1 (exponential convergence to space average).
Mixing rate: EML-2 (log decay of correlations = power law in time).
KS entropy h_KS: EML-2 (log of Lyapunov exponents).
Spectral gap: EML-2. Isomorphism problem (Ornstein): EML-∞.
"""
from __future__ import annotations
import math
from dataclasses import dataclass
from typing import Any


@dataclass
class BirkhoffEML:
    """Birkhoff ergodic theorem and convergence rates."""

    def time_average_convergence(self, n: int = 100, lambda_mix: float = 0.1) -> dict[str, Any]:
        """
        Birkhoff: (1/N) Σ f(T^n x) → ∫f dμ as N→∞.
        Convergence rate: |time_avg - space_avg| ~ exp(-λ·N) for mixing systems.
        EML-1: exponential convergence.
        """
        convergence_bound = round(math.exp(-lambda_mix * n), 6)
        log_rate = round(-lambda_mix * n, 4)
        return {
            "n_steps": n,
            "mixing_rate": lambda_mix,
            "convergence_bound": convergence_bound,
            "log_convergence": log_rate,
            "birkhoff_depth": 1,
            "convergence_depth": 1,
            "note": "Birkhoff convergence = EML-1 (exponential approach to ergodic mean)"
        }

    def ergodic_decomposition(self) -> dict[str, Any]:
        """
        Every measure decomposes into ergodic components (Choquet).
        Ergodic components: EML-0 (countable/measurable indexing).
        Decomposition measure: EML-2 (log-based disintegration).
        Non-ergodic system: EML-∞ (no unique invariant measure).
        """
        return {
            "ergodic_components_depth": 0,
            "decomposition_measure_depth": 2,
            "non_ergodic_depth": "∞",
            "choquet_theory_depth": 2,
            "note": "Ergodic decomposition: components=EML-0; measure=EML-2; non-ergodic=EML-∞"
        }

    def analyze(self) -> dict[str, Any]:
        conv = self.time_average_convergence()
        decomp = self.ergodic_decomposition()
        return {
            "model": "BirkhoffEML",
            "convergence": conv,
            "decomposition": decomp,
            "key_insight": "Birkhoff=EML-1; ergodic decomposition measure=EML-2; non-ergodic=EML-∞"
        }


@dataclass
class MixingEntropyEML:
    """Mixing rates, KS entropy, and spectral gap."""

    def mixing_rates(self, t: float = 10.0, alpha: float = 0.5) -> dict[str, Any]:
        """
        Correlation decay for mixing systems:
        - Exponential mixing: C(t) ~ exp(-γt) → EML-1
        - Polynomial mixing: C(t) ~ t^{-α} → EML-2 (power law = log-scale)
        - Non-mixing: C(t) → const ≠ 0 → EML-0 (constant)
        """
        exp_mixing = round(math.exp(-0.3 * t), 6)
        poly_mixing = round(t**(-alpha), 6)
        return {
            "t": t,
            "exponential_mixing": exp_mixing,
            "polynomial_mixing": poly_mixing,
            "exp_mixing_depth": 1,
            "poly_mixing_depth": 2,
            "non_mixing_depth": 0,
            "note": "Mixing: exponential=EML-1; polynomial=EML-2 (power law); non-mixing=EML-0"
        }

    def ks_entropy(self, lyapunov_exponents: list = None) -> dict[str, Any]:
        """
        Kolmogorov-Sinai entropy: h_KS = Σ max(λ_i, 0) (Pesin formula).
        Lyapunov exponents λ_i: EML-2 (log of eigenvalues of Jacobian).
        h_KS = sum of positive Lyapunov exponents = EML-2.
        Zero entropy: EML-1 (integrable systems). Positive entropy: EML-2.
        """
        if lyapunov_exponents is None:
            lyapunov_exponents = [0.693, 0.0, -0.693]
        h_ks = round(sum(max(lam, 0) for lam in lyapunov_exponents), 4)
        return {
            "lyapunov_exponents": lyapunov_exponents,
            "ks_entropy": h_ks,
            "lyapunov_depth": 2,
            "ks_entropy_depth": 2,
            "zero_entropy_depth": 1,
            "pesin_formula_depth": 2,
            "note": "KS entropy = Σ positive Lyapunov exponents = EML-2; Lyapunov = log(Jac) = EML-2"
        }

    def spectral_gap(self, operator_norm: float = 0.95) -> dict[str, Any]:
        """
        Spectral gap δ = 1 - |second eigenvalue| of transfer operator.
        Mixing time t_mix ~ 1/δ: EML-2 (inverse of gap = power law in δ).
        Spectral gap itself: EML-2 (log-scale quantity for mixing speed).
        """
        gap = round(1 - operator_norm, 4)
        t_mix = round(1 / gap, 2) if gap > 0 else float("inf")
        return {
            "second_eigenvalue": operator_norm,
            "spectral_gap": gap,
            "mixing_time": t_mix,
            "gap_depth": 2,
            "mixing_time_depth": 2,
            "note": "Spectral gap=EML-2; mixing time t_mix=1/δ=EML-2"
        }

    def ornstein_isomorphism(self) -> dict[str, Any]:
        """
        Ornstein theorem: two Bernoulli shifts with the same entropy are isomorphic.
        Isomorphism classification: EML-0 (classified by entropy value = single number).
        But construction of isomorphism: EML-∞ (non-constructive, existence proof).
        Beyond Bernoulli (K-systems, non-Bernoulli): EML-∞ isomorphism problem.
        """
        return {
            "bernoulli_classification_depth": 0,
            "isomorphism_construction_depth": "∞",
            "k_system_depth": "∞",
            "entropy_invariant_depth": 2,
            "ornstein_theorem": "Bernoulli shifts classified by entropy=EML-0; construction=EML-∞",
            "note": "Ornstein: entropy=EML-0 invariant; isomorphism proof=EML-∞"
        }

    def analyze(self) -> dict[str, Any]:
        mix = self.mixing_rates()
        ks = self.ks_entropy()
        gap = self.spectral_gap()
        orn = self.ornstein_isomorphism()
        return {
            "model": "MixingEntropyEML",
            "mixing_rates": mix,
            "ks_entropy": ks,
            "spectral_gap": gap,
            "ornstein": orn,
            "key_insight": "KS entropy=EML-2; spectral gap=EML-2; mixing=EML-1 or 2; isomorphism=EML-∞"
        }


def analyze_ergodic_theory_eml() -> dict[str, Any]:
    birk = BirkhoffEML()
    mix = MixingEntropyEML()
    return {
        "session": 206,
        "title": "Ergodic Theory: Mixing, Birkhoff's Theorem & Entropy",
        "eml_operator": "eml(x,y) = exp(x) - ln(y)",
        "birkhoff": birk.analyze(),
        "mixing_entropy": mix.analyze(),
        "eml_depth_summary": {
            "EML-0": "Ergodic components (countable), Bernoulli classification by entropy, non-mixing constant",
            "EML-1": "Birkhoff convergence (exponential), zero-entropy integrable, exponential mixing",
            "EML-2": "KS entropy (Pesin formula), Lyapunov exponents, spectral gap, polynomial mixing",
            "EML-∞": "Isomorphism construction (non-constructive), non-Bernoulli K-systems"
        },
        "key_theorem": (
            "The EML Ergodic Theory Theorem (S206): "
            "Ergodic theory spans the EML ladder naturally: "
            "Birkhoff convergence = EML-1 (exponential approach to ergodic mean). "
            "KS entropy h_KS = Σ max(λ_i,0) = EML-2 (Pesin: sum of positive Lyapunov). "
            "Spectral gap δ = EML-2 (mixing speed in log scale). "
            "Polynomial mixing C(t)~t^{-α} = EML-2 (power law = universal EML-2 signature). "
            "Ornstein isomorphism: Bernoulli classification by entropy = EML-0; "
            "construction of isomorphism = EML-∞ (non-constructive existence proof). "
            "DELTA_D HIGHLIGHT: h_KS computation path: "
            "Jacobian (EML-0 matrix) → eigenvalues (EML-2) = Δd=2 (anomalous dimension pattern)."
        ),
        "rabbit_hole_log": [
            "KS entropy = EML-2: same depth as Shannon, Fisher, KL — all information-theoretic",
            "Bernoulli classification = EML-0: one number (entropy) suffices — the EML-0 anchor",
            "Polynomial mixing = EML-2: power law appears in ergodic theory same as in physics"
        ]
    }


if __name__ == "__main__":
    import json
    print(json.dumps(analyze_ergodic_theory_eml(), indent=2, default=str))
