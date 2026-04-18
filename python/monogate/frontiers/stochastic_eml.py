"""
stochastic_eml.py — EML Complexity in Stochastic Processes & Feynman-Kac.

Session 64 findings:
  - Brownian motion W_t: paths are EML-inf (non-differentiable)
  - E[f(W_T)]: even though W_T ~ EML-inf, expectations are EML-3 (via heat kernel)
  - GBM S_t = S₀·exp((μ-σ²/2)t + σW_t): EML-1 drift × EML-inf diffusion
  - Feynman-Kac: E[exp(-∫r)·f(X_T)] = PDE solution (EML depth(f) + 1)
  - Black-Scholes formula: E[max(S_T-K,0)] → EML-3 (involves erf/Φ)
  - Lévy-Khintchine: char fn = exp(t·ψ(θ)) → EML-1 in t
  - OU process: stationary distribution N(0,σ²/2γ) → EML-2
  - KEY BRIDGE: EML-inf (paths) → EML-3 (expectations) via heat kernel
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import Callable

import numpy as np

__all__ = [
    "BrownianMotion",
    "GeometricBrownianMotion",
    "FeynmanKac",
    "BlackScholes",
    "OrnsteinUhlenbeck",
    "LevyProcess",
    "STOCHASTIC_EML_TAXONOMY",
    "analyze_stochastic_eml",
]

# ── EML Taxonomy ─────────────────────────────────────────────────────────────

STOCHASTIC_EML_TAXONOMY: dict[str, dict] = {
    "brownian_paths": {
        "formula": "W_t: Hölder-1/2 paths, non-differentiable everywhere",
        "eml_depth": "inf",
        "reason": "Individual paths are EML-inf (no finite EML representation).",
    },
    "brownian_expectation": {
        "formula": "E[f(W_T)] = ∫f(x)·exp(-x²/2T)/√(2πT) dx",
        "eml_depth": "depth(f) + 1 typically, EML-3 for smooth f",
        "reason": (
            "Expectation = convolution with Gaussian (heat kernel, EML-2). "
            "For f=max(x-K,0): E = BSM formula involving Φ (erf) → EML-3. "
            "KEY BRIDGE: EML-inf paths → EML-3 expectations via integration."
        ),
    },
    "gbm": {
        "formula": "S_t = S₀·exp((μ-σ²/2)t + σW_t)",
        "eml_depth": "inf (path-by-path)",
        "reason": "Involves σW_t which is EML-inf. Expected value: EML-1 (log-normal mean).",
    },
    "ito_formula": {
        "formula": "df(X_t) = f'(X_t)dX_t + ½f''(X_t)dt",
        "eml_depth": "depth(f)",
        "reason": "Itô formula: EML depth of f preserved (differentiation preserves class).",
    },
    "feynman_kac": {
        "formula": "u(x,t) = E[exp(-∫r·ds)·f(X_T)|X_t=x] solves PDE",
        "eml_depth": "depth(f) + 1",
        "reason": "PDE solution has depth(f)+1 (heat kernel adds EML-2 propagation).",
    },
    "black_scholes": {
        "formula": "C = S·Φ(d₁) - K·exp(-rT)·Φ(d₂)",
        "eml_depth": 3,
        "reason": "Φ(d) = (1+erf(d/√2))/2: EML-3. BSM formula is EML-3.",
    },
    "levy_khintchine": {
        "formula": "E[exp(iθX_t)] = exp(t·ψ(θ))",
        "eml_depth": 1,
        "reason": "Characteristic function = exp(t·ψ): EML-1 in t.",
    },
    "ornstein_uhlenbeck": {
        "formula": "dX_t = -γX_t·dt + σ·dW_t; stationary: N(0,σ²/2γ)",
        "eml_depth": 2,
        "reason": "Stationary variance σ²/(2γ): EML-2 (Gaussian distribution).",
    },
}


# ── Brownian Motion ───────────────────────────────────────────────────────────

@dataclass
class BrownianMotion:
    """
    Standard Brownian motion W_t.

    Individual paths: EML-inf (Hölder-1/2 continuous, nowhere differentiable).
    Distribution W_t ~ N(0,t): EML-2 (Gaussian, known EML depth).
    Expected values E[f(W_T)]: EML-3 for smooth f (via heat kernel convolution).
    """

    seed: int | None = None

    def simulate(self, T: float, n_steps: int = 1000) -> np.ndarray:
        """Simulate one path W_t for t ∈ [0,T]."""
        if self.seed is not None:
            rng = np.random.default_rng(self.seed)
        else:
            rng = np.random.default_rng()
        dt = T / n_steps
        increments = rng.normal(0, math.sqrt(dt), n_steps)
        return np.concatenate([[0.0], np.cumsum(increments)])

    def expectation_monte_carlo(self, f: Callable[[float], float],
                                 T: float, n_samples: int = 10000,
                                 seed: int = 42) -> float:
        """E[f(W_T)] via Monte Carlo."""
        rng = np.random.default_rng(seed)
        samples = rng.normal(0, math.sqrt(T), n_samples)
        return float(np.mean([f(x) for x in samples]))

    def expectation_analytical(self, f_coefs: str, T: float, K: float = 1.0) -> dict[str, float]:
        """
        Analytical expectations for key payoff functions.
        - E[W_T²] = T
        - E[exp(αW_T)] = exp(α²T/2)
        - E[max(W_T-K,0)] = BSM with S=1, r=0, σ=1 (call payoff)
        """
        results = {}
        # E[W_T²] = T
        results["E_W2"] = T
        # E[exp(W_T)] = exp(T/2)
        results["E_exp_W"] = math.exp(T / 2.0)
        # E[|W_T|] = sqrt(2T/π)
        results["E_abs_W"] = math.sqrt(2.0 * T / math.pi)
        return results

    def holder_estimate(self, path: np.ndarray, dt: float,
                         alpha: float = 0.5) -> float:
        """Estimate Hölder-α norm of path."""
        diffs = np.abs(np.diff(path))
        return float(np.max(diffs) / (dt ** alpha))

    def eml_depth_path(self) -> str:
        return "inf"

    def eml_depth_expectation(self) -> int:
        return 3  # via heat kernel


# ── Geometric Brownian Motion ─────────────────────────────────────────────────

@dataclass
class GeometricBrownianMotion:
    """
    GBM: S_t = S₀·exp((μ-σ²/2)t + σW_t).

    Log-normal: E[S_t] = S₀·exp(μt) — EML-1 in t.
    Variance: Var[S_t] = S₀²·exp(2μt)·(exp(σ²t)-1) — EML-1.
    """

    mu: float = 0.05
    sigma: float = 0.2
    S0: float = 100.0
    seed: int | None = 42

    def simulate(self, T: float, n_steps: int = 252) -> np.ndarray:
        """Simulate GBM path."""
        rng = np.random.default_rng(self.seed)
        dt = T / n_steps
        z = rng.normal(0, 1, n_steps)
        log_returns = (self.mu - 0.5 * self.sigma ** 2) * dt + self.sigma * math.sqrt(dt) * z
        return self.S0 * np.exp(np.concatenate([[0.0], np.cumsum(log_returns)]))

    def mean(self, T: float) -> float:
        """E[S_T] = S₀·exp(μT). EML-1 in T."""
        return self.S0 * math.exp(self.mu * T)

    def variance(self, T: float) -> float:
        """Var[S_T] = S₀²·exp(2μT)·(exp(σ²T)-1)."""
        return self.S0 ** 2 * math.exp(2.0 * self.mu * T) * (math.exp(self.sigma ** 2 * T) - 1.0)

    def log_normal_pdf(self, s: float, T: float) -> float:
        """p(S_T=s): log-normal density."""
        if s <= 0 or T <= 0:
            return 0.0
        mu_log = math.log(self.S0) + (self.mu - 0.5 * self.sigma ** 2) * T
        sig_log = self.sigma * math.sqrt(T)
        log_s = math.log(s)
        exponent = -0.5 * ((log_s - mu_log) / sig_log) ** 2
        if exponent < -700:
            return 0.0
        return math.exp(exponent) / (s * sig_log * math.sqrt(2.0 * math.pi))

    def eml_depth_mean(self) -> int:
        return 1  # exp(μT): EML-1 in T


# ── Feynman-Kac Formula ───────────────────────────────────────────────────────

@dataclass
class FeynmanKac:
    """
    Feynman-Kac formula: u(x,t) = E[exp(-∫_t^T r·ds)·f(X_T) | X_t=x].
    u solves the PDE: u_t + Lu - r·u = 0, u(x,T) = f(x).
    where L = ½σ²∂²/∂x² + μ∂/∂x.

    For Brownian motion (μ=0, σ=1, r=0):
      u(x,t) = E[f(W_T-t + x)] = ∫f(y)·G(y-x,T-t)dy
    EML depth: depth(f) + 1 (heat kernel adds EML-2 propagation).
    """

    mu: float = 0.0
    sigma: float = 1.0
    r: float = 0.0

    def solve(self, x: float, t: float, T: float,
               f: Callable[[float], float],
               x_range: float = 8.0, n: int = 800) -> float:
        """Solve Feynman-Kac via numerical integration."""
        tau = T - t
        if tau <= 0:
            return f(x)
        sig = self.sigma * math.sqrt(tau)
        mu_drift = x + self.mu * tau
        ys = np.linspace(mu_drift - 6 * sig, mu_drift + 6 * sig, n)
        dy = ys[1] - ys[0]
        kernel = np.exp(-0.5 * ((ys - mu_drift) / sig) ** 2) / (sig * math.sqrt(2 * math.pi))
        f_vals = np.array([f(y) for y in ys])
        discount = math.exp(-self.r * tau)
        return float(discount * np.sum(kernel * f_vals) * dy)

    def eml_depth_solution(self, eml_depth_f: int) -> int:
        """EML depth of solution = depth(f) + 1 (from heat kernel convolution)."""
        return eml_depth_f + 1


# ── Black-Scholes Formula ─────────────────────────────────────────────────────

@dataclass
class BlackScholes:
    """
    Black-Scholes option pricing.

    C = S·Φ(d₁) - K·exp(-rT)·Φ(d₂)
    where Φ(x) = (1+erf(x/√2))/2 → EML-3.
    The BSM formula is EML-3 (contains Φ = erf-based).
    """

    def _norm_cdf(self, x: float) -> float:
        """Φ(x) = (1+erf(x/√2))/2. EML-3."""
        return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))

    def call_price(self, S: float, K: float, T: float,
                    r: float, sigma: float) -> float:
        """Black-Scholes call price. EML-3 (contains Φ = erf)."""
        if T <= 0 or sigma <= 0:
            return max(0.0, S - K)
        sqrt_T = math.sqrt(T)
        d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * sqrt_T)
        d2 = d1 - sigma * sqrt_T
        return S * self._norm_cdf(d1) - K * math.exp(-r * T) * self._norm_cdf(d2)

    def put_price(self, S: float, K: float, T: float,
                   r: float, sigma: float) -> float:
        """BSM put via put-call parity: P = C - S + K·exp(-rT)."""
        C = self.call_price(S, K, T, r, sigma)
        return C - S + K * math.exp(-r * T)

    def delta(self, S: float, K: float, T: float,
               r: float, sigma: float) -> float:
        """Delta = ∂C/∂S = Φ(d₁). EML-3."""
        if T <= 0:
            return 1.0 if S > K else 0.0
        d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
        return self._norm_cdf(d1)

    def monte_carlo_call(self, S: float, K: float, T: float,
                          r: float, sigma: float,
                          n: int = 100000, seed: int = 42) -> float:
        """Monte Carlo BSM price verification."""
        rng = np.random.default_rng(seed)
        z = rng.normal(0, 1, n)
        ST = S * np.exp((r - 0.5 * sigma ** 2) * T + sigma * math.sqrt(T) * z)
        payoffs = np.maximum(ST - K, 0.0)
        return float(math.exp(-r * T) * np.mean(payoffs))

    def eml_depth(self) -> int:
        return 3  # Φ = erf-based = EML-3


# ── Ornstein-Uhlenbeck Process ────────────────────────────────────────────────

@dataclass
class OrnsteinUhlenbeck:
    """
    dX_t = -γX_t·dt + σ·dW_t

    Solution: X_t = X_0·exp(-γt) + σ·∫_0^t exp(-γ(t-s))dW_s
    Mean: E[X_t] = X_0·exp(-γt) — EML-1 in t
    Variance: Var[X_t] = σ²(1-exp(-2γt))/(2γ) — EML-1
    Stationary distribution: N(0, σ²/(2γ)) — EML-2 (Gaussian)
    """

    gamma: float = 1.0  # mean reversion rate
    sigma: float = 1.0  # volatility
    x0: float = 0.0    # initial value
    seed: int | None = 42

    def mean(self, t: float) -> float:
        """E[X_t] = X₀·exp(-γt). EML-1."""
        return self.x0 * math.exp(-self.gamma * t)

    def variance(self, t: float) -> float:
        """Var[X_t] = σ²(1-exp(-2γt))/(2γ)."""
        return self.sigma ** 2 * (1.0 - math.exp(-2.0 * self.gamma * t)) / (2.0 * self.gamma)

    def stationary_variance(self) -> float:
        """σ_∞² = σ²/(2γ) as t→∞. EML-2 (Gaussian parameter)."""
        return self.sigma ** 2 / (2.0 * self.gamma)

    def simulate(self, T: float, n_steps: int = 1000) -> np.ndarray:
        """Simulate OU path using Euler-Maruyama."""
        rng = np.random.default_rng(self.seed)
        dt = T / n_steps
        x = self.x0
        path = [x]
        sqrt_dt = math.sqrt(dt)
        for _ in range(n_steps):
            dw = rng.normal(0, sqrt_dt)
            x += -self.gamma * x * dt + self.sigma * dw
            path.append(x)
        return np.array(path)

    def autocorrelation(self, lag: float) -> float:
        """Autocorrelation ρ(τ) = exp(-γ|τ|). EML-1."""
        return math.exp(-self.gamma * abs(lag))

    def eml_depth_stationary(self) -> int:
        return 2  # Gaussian stationary distribution


# ── Lévy Process ─────────────────────────────────────────────────────────────

@dataclass
class LevyProcess:
    """
    Lévy-Khintchine representation.

    Characteristic function: E[exp(iθX_t)] = exp(t·ψ(θ))
    where ψ(θ) = iaθ - σ²θ²/2 + ∫(e^{iθx}-1-iθx·1_{|x|<1})ν(dx)

    EML-1 in t: the whole expression is exp(t·ψ(θ)) — EML-1 atom in t.

    Examples:
      - Brownian: ψ(θ) = -σ²θ²/2 (EML-2 in θ)
      - Poisson: ψ(θ) = λ(e^{iθ}-1) (EML-1 in θ)
      - Cauchy: ψ(θ) = -|θ| (EML-2/3 in θ)
    """

    def char_fn_brownian(self, theta: float, t: float, sigma: float = 1.0) -> float:
        """E[exp(iθW_t)] = exp(-σ²θ²t/2). Real part: exp(-σ²θ²t/2)."""
        return math.exp(-sigma ** 2 * theta ** 2 * t / 2.0)

    def char_fn_poisson(self, theta: float, t: float, lam: float = 1.0) -> complex:
        """E[exp(iθN_t)] = exp(λt(e^{iθ}-1))."""
        psi = lam * (complex(math.cos(theta), math.sin(theta)) - 1)
        arg = t * psi
        # exp of complex number
        mag = math.exp(arg.real)
        return mag * complex(math.cos(arg.imag), math.sin(arg.imag))

    def char_fn_gamma(self, theta: float, t: float,
                       alpha: float = 1.0, beta: float = 1.0) -> float:
        """
        Gamma process: ψ(θ) = α·log(1 - iθ/β).
        |E[exp(iθX_t)]| = (1 + θ²/β²)^{-αt/2}.
        """
        return (1.0 + theta ** 2 / beta ** 2) ** (-alpha * t / 2.0)

    def eml_depth_in_t(self) -> int:
        return 1  # exp(t·ψ) is EML-1 in t


# ── Grand Analysis ────────────────────────────────────────────────────────────

def analyze_stochastic_eml() -> dict:
    """Run full stochastic processes EML analysis."""
    results: dict = {
        "session": 64,
        "title": "Stochastic Processes & Feynman-Kac EML Complexity",
        "taxonomy": STOCHASTIC_EML_TAXONOMY,
    }

    bm = BrownianMotion(seed=42)
    gbm = GeometricBrownianMotion()
    fk = FeynmanKac()
    bs = BlackScholes()
    ou = OrnsteinUhlenbeck()
    levy = LevyProcess()

    # Brownian motion expectations
    T = 1.0
    mc_e_x2 = bm.expectation_monte_carlo(lambda x: x ** 2, T)
    mc_e_exp = bm.expectation_monte_carlo(lambda x: math.exp(x), T)
    analytical = bm.expectation_analytical("", T)
    results["brownian"] = {
        "E_W2_mc": mc_e_x2,
        "E_W2_exact": T,
        "E_exp_W_mc": mc_e_exp,
        "E_exp_W_exact": math.exp(T / 2.0),
        "E_abs_W_exact": analytical["E_abs_W"],
        "eml_depth_path": bm.eml_depth_path(),
        "eml_depth_expectation": bm.eml_depth_expectation(),
    }

    # GBM
    results["gbm"] = {
        "mean_T1": gbm.mean(1.0),
        "mean_T1_formula": gbm.S0 * math.exp(gbm.mu * 1.0),
        "variance_T1": gbm.variance(1.0),
        "eml_depth_mean": gbm.eml_depth_mean(),
    }

    # Black-Scholes
    S, K, T_opt = 100.0, 100.0, 1.0
    r_rate, sig = 0.05, 0.2
    C_bsm = bs.call_price(S, K, T_opt, r_rate, sig)
    C_mc = bs.monte_carlo_call(S, K, T_opt, r_rate, sig)
    results["black_scholes"] = {
        "call_BSM": C_bsm,
        "call_MC": C_mc,
        "relative_error": abs(C_bsm - C_mc) / C_bsm,
        "delta": bs.delta(S, K, T_opt, r_rate, sig),
        "eml_depth": bs.eml_depth(),
        "note": "BSM formula contains Phi=erf → EML-3",
    }

    # Feynman-Kac: call payoff
    f_call = lambda x: max(x - 1.0, 0.0)
    fk_val = fk.solve(0.0, 0.0, 1.0, f_call)
    results["feynman_kac"] = {
        "call_payoff_fk": fk_val,
        "call_payoff_exact": bm.expectation_monte_carlo(f_call, 1.0, 200000),
        "eml_depth_for_call_payoff": fk.eml_depth_solution(3),
    }

    # OU process
    ou_stat_var = ou.stationary_variance()
    ou_var_t5 = ou.variance(5.0)
    results["ornstein_uhlenbeck"] = {
        "stationary_variance": ou_stat_var,
        "variance_t5": ou_var_t5,
        "variance_t10": ou.variance(10.0),
        "autocorr_lag1": ou.autocorrelation(1.0),
        "eml_depth_stationary": ou.eml_depth_stationary(),
    }

    # Lévy-Khintchine
    results["levy_khintchine"] = {
        "char_brownian_theta1_t1": levy.char_fn_brownian(1.0, 1.0),
        "char_brownian_theta2_t1": levy.char_fn_brownian(2.0, 1.0),
        "char_poisson_theta1_t1": abs(levy.char_fn_poisson(1.0, 1.0)),
        "eml_depth_in_t": levy.eml_depth_in_t(),
    }

    results["summary"] = {
        "key_bridge": (
            "EML-inf (Brownian paths) → EML-3 (expectations) via heat kernel (EML-2). "
            "The expectation operator INTEGRATES OUT the noise, reducing EML depth. "
            "BSM formula: EML-3 (contains erf/Φ). "
            "OU stationary: EML-2 (Gaussian). "
            "Lévy char fn: EML-1 in t."
        ),
        "eml_depths": {k: str(v["eml_depth"]) for k, v in STOCHASTIC_EML_TAXONOMY.items()},
    }

    return results
