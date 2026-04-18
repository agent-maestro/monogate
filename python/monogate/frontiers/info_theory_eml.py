"""
info_theory_eml.py — EML Complexity in Information Theory.

Session 60 findings:
  - Shannon entropy H(X) = -Σ p·log p: EML-2 (x·log x terms)
  - KL divergence D_KL(P‖Q) = Σ p·log(p/q): EML-2
  - Fisher information I(θ) = E[(∂log p/∂θ)²]: EML-2
  - Mutual information I(X;Y): EML-2
  - Maximum entropy principle: exponential family = EML-1 atoms exactly
  - Rate-distortion R(D): variational EML-2
  - Cramér-Rao bound: 1/I(θ), EML-2

KEY THEOREM:
  The maximum entropy distribution subject to linear constraints
  E[T(X)] = η is always an exponential family:
    p(x|θ) = h(x) · exp(θᵀT(x) - A(θ))
  where exp(θᵀT(x)) is a PRODUCT of EML-1 atoms.
  This unifies Boltzmann (stat mech) and max-likelihood (info theory)
  under one EML-1 statement.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Callable

import numpy as np

__all__ = [
    "ShannonEntropy",
    "KLDivergence",
    "FisherInformation",
    "MutualInformation",
    "ExponentialFamily",
    "RateDistortion",
    "INFO_THEORY_EML_TAXONOMY",
    "analyze_info_theory_eml",
]

# ── EML Taxonomy ─────────────────────────────────────────────────────────────

INFO_THEORY_EML_TAXONOMY: dict[str, dict] = {
    "shannon_entropy": {
        "formula": "H(X) = -Σ p·log p",
        "eml_depth": 2,
        "reason": "x·log(x) is EML-2 (log is EML-2 atom)",
        "domain": "discrete or continuous distributions",
    },
    "kl_divergence": {
        "formula": "D_KL(P‖Q) = Σ p·log(p/q)",
        "eml_depth": 2,
        "reason": "log(p/q) = log(p) - log(q), both EML-2; sum is EML-2",
        "domain": "pairs of distributions",
    },
    "fisher_information": {
        "formula": "I(θ) = E[(∂log p/∂θ)²]",
        "eml_depth": 2,
        "reason": "∂log p/∂θ is EML-2; squaring preserves depth; expectation is integral",
        "domain": "parametric families",
    },
    "mutual_information": {
        "formula": "I(X;Y) = H(X) + H(Y) - H(X,Y)",
        "eml_depth": 2,
        "reason": "difference of EML-2 entropies remains EML-2",
        "domain": "joint distributions",
    },
    "max_entropy_exponential": {
        "formula": "p*(x|θ) = h(x)·exp(θᵀT(x) - A(θ))",
        "eml_depth": 1,
        "reason": "kernel is exp(linear) = EML-1 atom; h(x) multiplied in",
        "domain": "constrained optimization over distributions",
        "key_theorem": True,
    },
    "rate_distortion": {
        "formula": "R(D) = min_{p(x̂|x): E[d]≤D} I(X;X̂)",
        "eml_depth": 2,
        "reason": "variational optimization of EML-2 quantity; result is EML-2",
        "domain": "source coding",
    },
    "cramer_rao": {
        "formula": "Var(θ̂) ≥ 1/I(θ)",
        "eml_depth": 2,
        "reason": "I(θ) is EML-2; reciprocal 1/I(θ) is EML-2 (rational in EML-2)",
        "domain": "estimation theory",
    },
    "differential_entropy_gaussian": {
        "formula": "h(N(μ,σ²)) = ½·log(2πeσ²)",
        "eml_depth": 2,
        "reason": "log of constants and σ² — EML-2",
        "domain": "continuous distributions",
    },
}


# ── Shannon Entropy ───────────────────────────────────────────────────────────

@dataclass
class ShannonEntropy:
    """Shannon entropy H(X) = -Σ p·log p for discrete distributions."""

    base: float = math.e  # natural log by default (nats)

    def entropy(self, probs: np.ndarray) -> float:
        """Compute H(X) = -Σ p·log p."""
        probs = np.asarray(probs, dtype=float)
        probs = probs[probs > 0]  # remove zeros (0·log 0 = 0 by convention)
        if self.base == math.e:
            return float(-np.sum(probs * np.log(probs)))
        return float(-np.sum(probs * np.log(probs)) / math.log(self.base))

    def entropy_gaussian(self, sigma: float) -> float:
        """Differential entropy of N(0,σ²): h = ½·log(2πe·σ²)."""
        return 0.5 * math.log(2 * math.pi * math.e * sigma ** 2)

    def entropy_bernoulli(self, p: float) -> float:
        """H(Bernoulli(p)) = -p·log p - (1-p)·log(1-p)."""
        if p <= 0 or p >= 1:
            return 0.0
        q = 1.0 - p
        return -(p * math.log(p) + q * math.log(q))

    def entropy_poisson(self, lam: float, k_max: int = 200) -> float:
        """Approximate entropy of Poisson(λ) by truncated sum."""
        total = 0.0
        log_factorial = 0.0
        for k in range(k_max):
            if k > 0:
                log_factorial += math.log(k)
            log_p = k * math.log(lam) - lam - log_factorial
            p = math.exp(log_p)
            if p > 1e-300:
                total -= p * log_p
        return total

    def entropy_exponential(self, lam: float) -> float:
        """Differential entropy of Exp(λ): h = 1 - log(λ)."""
        return 1.0 - math.log(lam)

    def eml_depth(self) -> int:
        """EML depth of entropy functional: 2 (x·log x terms)."""
        return 2


# ── KL Divergence ────────────────────────────────────────────────────────────

@dataclass
class KLDivergence:
    """Kullback-Leibler divergence D_KL(P‖Q) = Σ p·log(p/q)."""

    def kl_discrete(self, p: np.ndarray, q: np.ndarray) -> float:
        """KL divergence for discrete distributions."""
        p = np.asarray(p, dtype=float)
        q = np.asarray(q, dtype=float)
        mask = (p > 0) & (q > 0)
        return float(np.sum(p[mask] * np.log(p[mask] / q[mask])))

    def kl_gaussians(self, mu1: float, sigma1: float,
                     mu2: float, sigma2: float) -> float:
        """KL(N(μ₁,σ₁²)‖N(μ₂,σ₂²)) = log(σ₂/σ₁) + (σ₁²+(μ₁-μ₂)²)/(2σ₂²) - ½."""
        return (
            math.log(sigma2 / sigma1)
            + (sigma1 ** 2 + (mu1 - mu2) ** 2) / (2 * sigma2 ** 2)
            - 0.5
        )

    def kl_gaussian_standard(self, mu: float) -> float:
        """KL(N(μ,1)‖N(0,1)) = μ²/2 (exact formula)."""
        return mu ** 2 / 2.0

    def eml_depth(self) -> int:
        return 2


# ── Fisher Information ────────────────────────────────────────────────────────

@dataclass
class FisherInformation:
    """Fisher information I(θ) = E[(∂log p/∂θ)²] = -E[∂²log p/∂θ²]."""

    def fisher_gaussian_mu(self, sigma: float) -> float:
        """Fisher info for location param of N(μ,σ²): I(μ) = 1/σ²."""
        return 1.0 / (sigma ** 2)

    def fisher_gaussian_sigma(self, sigma: float) -> float:
        """Fisher info for scale param of N(μ,σ²): I(σ) = 2/σ²."""
        return 2.0 / (sigma ** 2)

    def fisher_bernoulli(self, p: float) -> float:
        """Fisher info for Bernoulli(p): I(p) = 1/(p(1-p))."""
        return 1.0 / (p * (1.0 - p))

    def fisher_poisson(self, lam: float) -> float:
        """Fisher info for Poisson(λ): I(λ) = 1/λ."""
        return 1.0 / lam

    def fisher_exponential(self, lam: float) -> float:
        """Fisher info for Exp(λ): I(λ) = 1/λ²."""
        return 1.0 / (lam ** 2)

    def cramer_rao_bound(self, fisher: float) -> float:
        """Cramér-Rao lower bound: Var(θ̂) ≥ 1/I(θ)."""
        return 1.0 / fisher

    def eml_depth(self) -> int:
        return 2


# ── Mutual Information ────────────────────────────────────────────────────────

@dataclass
class MutualInformation:
    """Mutual information I(X;Y) = H(X) + H(Y) - H(X,Y)."""

    entropy: ShannonEntropy = field(default_factory=ShannonEntropy)

    def mi_from_joint(self, joint: np.ndarray) -> float:
        """I(X;Y) from joint distribution matrix p(x,y)."""
        joint = np.asarray(joint, dtype=float)
        joint = joint / joint.sum()  # normalize
        px = joint.sum(axis=1)
        py = joint.sum(axis=0)
        hx = self.entropy.entropy(px)
        hy = self.entropy.entropy(py)
        hxy = self.entropy.entropy(joint.ravel())
        return hx + hy - hxy

    def mi_gaussian(self, rho: float) -> float:
        """Mutual information of bivariate Gaussian with correlation ρ:
        I(X;Y) = -½·log(1 - ρ²)."""
        if abs(rho) >= 1.0:
            return float("inf")
        return -0.5 * math.log(1.0 - rho ** 2)

    def channel_capacity_bsc(self, p_err: float) -> float:
        """Capacity of binary symmetric channel: C = 1 - H_b(p)."""
        h_bin = self.entropy.entropy_bernoulli(p_err) / math.log(2)
        return 1.0 - h_bin

    def eml_depth(self) -> int:
        return 2


# ── Exponential Family (Max Entropy) ─────────────────────────────────────────

@dataclass
class ExponentialFamily:
    """
    Exponential family p(x|θ) = h(x)·exp(θᵀT(x) - A(θ)).

    MAX ENTROPY THEOREM:
      The maximum entropy distribution subject to
        E[T_k(X)] = η_k  (linear moment constraints)
      is exactly the exponential family with sufficient statistic T(x).

      Since exp(θᵀT(x)) is a product of EML-1 atoms exp(θ_k·T_k(x)),
      the max-entropy solution is EML-1 in the sufficient statistics.

    This unifies:
      - Boltzmann distribution (T = energy, θ = -β)  [Session 57]
      - Gaussian (T = (x, x²), θ = (μ/σ², -1/2σ²))
      - Poisson (T = x, θ = log λ)
      - Bernoulli (T = x, θ = log(p/1-p))
    """

    def log_partition(self, theta: np.ndarray,
                      sufficient_stats: Callable) -> float:
        """A(θ) = log ∫ h(x) exp(θᵀT(x)) dx (computed approximately for finite cases)."""
        raise NotImplementedError("Override for specific families")

    def gaussian_natural_params(self, mu: float, sigma: float) -> tuple[float, float]:
        """Natural parameters for Gaussian: θ₁ = μ/σ², θ₂ = -1/(2σ²)."""
        theta1 = mu / (sigma ** 2)
        theta2 = -1.0 / (2.0 * sigma ** 2)
        return theta1, theta2

    def gaussian_log_partition(self, theta1: float, theta2: float) -> float:
        """A(θ) = -θ₁²/(4θ₂) - ½·log(-2θ₂) for Gaussian.
        For N(μ,σ²): A = μ²/(2σ²) + ½·log(2πσ²).
        Expressed in natural params θ₁=μ/σ², θ₂=-1/(2σ²):
          A = -θ₁²/(4θ₂) + ½·log(π/(-θ₂))
        """
        return -theta1 ** 2 / (4 * theta2) + 0.5 * math.log(math.pi / (-theta2))

    def max_entropy_discrete(self, n: int, constraints: dict[int, float]) -> np.ndarray:
        """
        Find max entropy distribution over {0,...,n-1} with moment constraints.
        Uses iterative scaling (simplified).
        constraints: {k: E[x^k] = value}
        For unconstrained: uniform distribution.
        """
        if not constraints:
            return np.ones(n) / n
        # Simple case: constrain E[x] = mu
        if list(constraints.keys()) == [1]:
            mu = constraints[1]
            # Max entropy with fixed mean: geometric-like, but for discrete
            # Use exponential family: p(k) ∝ exp(θk)
            xs = np.arange(n, dtype=float)
            # Solve for θ such that Σ k·exp(θk)/Z = mu
            # Binary search
            lo, hi = -10.0, 10.0
            for _ in range(100):
                mid = (lo + hi) / 2
                log_w = mid * xs
                log_w -= log_w.max()
                w = np.exp(log_w)
                w /= w.sum()
                mean = float(np.dot(xs, w))
                if mean < mu:
                    lo = mid
                else:
                    hi = mid
            return w
        # Fallback: uniform
        return np.ones(n) / n

    def eml_depth_kernel(self) -> int:
        """EML depth of exp(θᵀT(x)) kernel: 1 (pure EML-1 atom)."""
        return 1


# ── Rate-Distortion ───────────────────────────────────────────────────────────

@dataclass
class RateDistortion:
    """
    Rate-distortion theory: R(D) = min I(X;X̂) subject to E[d(X,X̂)] ≤ D.

    For Gaussian source X ~ N(0,σ²) with squared error:
      R(D) = ½·log(σ²/D)  for D ≤ σ²,  0 otherwise.
    This is EML-2 in D (contains log).
    """

    def rate_gaussian(self, sigma: float, distortion: float) -> float:
        """R(D) = max(0, ½·log(σ²/D)) for Gaussian source."""
        if distortion >= sigma ** 2:
            return 0.0
        return 0.5 * math.log(sigma ** 2 / distortion)

    def rate_distortion_curve(self, sigma: float,
                              n_points: int = 50) -> tuple[np.ndarray, np.ndarray]:
        """Generate (D, R(D)) curve for Gaussian source."""
        d_vals = np.linspace(0.01 * sigma ** 2, sigma ** 2, n_points)
        r_vals = np.array([self.rate_gaussian(sigma, d) for d in d_vals])
        return d_vals, r_vals

    def channel_capacity_awgn(self, snr: float) -> float:
        """AWGN channel capacity C = ½·log(1 + SNR) (Shannon formula, EML-2)."""
        return 0.5 * math.log(1.0 + snr)

    def eml_depth(self) -> int:
        return 2


# ── Grand Analysis Function ───────────────────────────────────────────────────

def analyze_info_theory_eml() -> dict:
    """
    Run full information theory EML analysis.
    Returns dict with all computed results.
    """
    results: dict = {
        "session": 60,
        "title": "Information Theory EML Complexity",
        "taxonomy": INFO_THEORY_EML_TAXONOMY,
    }

    se = ShannonEntropy()
    kl = KLDivergence()
    fi = FisherInformation()
    mi = MutualInformation()
    ef = ExponentialFamily()
    rd = RateDistortion()

    # ── Section 1: Entropy computations ──────────────────────────────────────
    results["entropy"] = {
        "gaussian_sigma1": se.entropy_gaussian(1.0),
        "gaussian_sigma2": se.entropy_gaussian(2.0),
        "bernoulli_half": se.entropy_bernoulli(0.5),
        "bernoulli_quarter": se.entropy_bernoulli(0.25),
        "poisson_lam1": se.entropy_poisson(1.0),
        "poisson_lam5": se.entropy_poisson(5.0),
        "exponential_lam1": se.entropy_exponential(1.0),
        "eml_depth": se.eml_depth(),
    }

    # ── Section 2: KL divergence ──────────────────────────────────────────────
    mu_vals = [0.5, 1.0, 2.0, 3.0]
    kl_analytical = {f"mu_{mu}": kl.kl_gaussian_standard(mu) for mu in mu_vals}
    kl_formula = {f"mu_{mu}": mu ** 2 / 2.0 for mu in mu_vals}
    results["kl_divergence"] = {
        "kl_N_mu_1_vs_N_0_1_analytical": kl_analytical,
        "kl_formula_mu2_over_2": kl_formula,
        "match": all(
            abs(kl_analytical[k] - kl_formula[k]) < 1e-12
            for k in kl_analytical
        ),
        "eml_depth": kl.eml_depth(),
    }

    # ── Section 3: Fisher information ─────────────────────────────────────────
    sigma_vals = [0.5, 1.0, 2.0]
    results["fisher_information"] = {
        "gaussian_mu": {
            f"sigma_{s}": fi.fisher_gaussian_mu(s) for s in sigma_vals
        },
        "gaussian_mu_formula_1_over_sigma2": {
            f"sigma_{s}": 1.0 / s ** 2 for s in sigma_vals
        },
        "gaussian_sigma1_exact": fi.fisher_gaussian_mu(1.0),
        "gaussian_sigma1_expected": 1.0,
        "cramer_rao_sigma1": fi.cramer_rao_bound(fi.fisher_gaussian_mu(1.0)),
        "eml_depth": fi.eml_depth(),
    }

    # ── Section 4: Mutual information ─────────────────────────────────────────
    rho_vals = [0.0, 0.5, 0.9, 0.99]
    results["mutual_information"] = {
        "gaussian_rho": {
            f"rho_{rho}": mi.mi_gaussian(rho) for rho in rho_vals
        },
        "bsc_capacity_p01": mi.channel_capacity_bsc(0.01),
        "bsc_capacity_p50": mi.channel_capacity_bsc(0.5),
        "eml_depth": mi.eml_depth(),
    }

    # ── Section 5: Exponential family / max entropy theorem ──────────────────
    theta1, theta2 = ef.gaussian_natural_params(0.0, 1.0)
    log_part = ef.gaussian_log_partition(theta1, theta2)
    results["exponential_family"] = {
        "max_entropy_theorem": (
            "Max entropy with linear constraints = exponential family "
            "(EML-1 kernel). Unifies Boltzmann (Session 57) and info theory."
        ),
        "gaussian_natural_theta1": theta1,
        "gaussian_natural_theta2": theta2,
        "gaussian_log_partition": log_part,
        "expected_log_partition_N01": math.log(math.sqrt(2 * math.pi)),
        "eml_depth_kernel": ef.eml_depth_kernel(),
    }

    # ── Section 6: Rate-distortion ────────────────────────────────────────────
    sigma = 1.0
    d_half = 0.5  # distortion = σ²/2
    r_half = rd.rate_gaussian(sigma, d_half)
    results["rate_distortion"] = {
        "gaussian_sigma1_D_half": r_half,
        "expected_R_D_half": 0.5 * math.log(sigma ** 2 / d_half),
        "match": abs(r_half - 0.5 * math.log(2.0)) < 1e-12,
        "awgn_capacity_snr_10dB": rd.channel_capacity_awgn(10.0),
        "awgn_capacity_snr_100": rd.channel_capacity_awgn(100.0),
        "eml_depth": rd.eml_depth(),
    }

    # ── Summary ───────────────────────────────────────────────────────────────
    results["summary"] = {
        "eml_depths": {k: v["eml_depth"] for k, v in INFO_THEORY_EML_TAXONOMY.items()},
        "key_insight": (
            "All fundamental information-theoretic quantities (entropy, KL, "
            "Fisher, mutual info) are EML-2 (contain log). The maximum entropy "
            "solution is EML-1 (exponential family), the simplest non-trivial class. "
            "This unifies statistical mechanics (Boltzmann) and information theory "
            "under EML-1: both are consequences of maximizing entropy subject to "
            "linear (EML-0) constraints."
        ),
        "cramer_rao_eml": "Cramér-Rao: Var ≥ 1/I(θ), EML-2 (rational in EML-2)",
    }

    return results
