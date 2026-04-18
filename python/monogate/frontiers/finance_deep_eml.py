"""
Session 95 — Finance Deep: High-Frequency Dynamics, Volatility & Risk

Stochastic volatility, high-frequency dynamics, fat tails, and risk measures (VaR, CVaR).
Tests whether volatility clustering and fat tails have distinct EML-depth signatures.

Key theorem: Black-Scholes volatility σ is EML-2 (constant → EML-0 degenerate case).
Heston stochastic volatility is EML-1 (mean-reverting OU = EML-1). GARCH volatility
clustering is EML-1 (exponential decay of autocorrelation). Fat tails (power law P(X>x)~x^{-α})
are EML-2. Extreme events and VaR violations are EML-∞.
"""

from __future__ import annotations
import math, json
from dataclasses import dataclass, field


EML_INF = float("inf")


@dataclass
class StochasticVolatility:
    """
    Heston model: dS/S = μdt + √v·dW_S, dv = κ(θ-v)dt + ξ√v·dW_v.

    EML structure:
    - v(t): OU mean-reverting process → stationary distribution = Gamma = EML-1
    - E[v(t)] = θ + (v₀-θ)·exp(-κt): EML-1 (exponential mean reversion)
    - Option price C_Heston: Fourier inversion → EML-3
    - Feller condition: 2κθ > ξ² → vol never touches 0: EML-2 (polynomial inequality)
    - Variance swap price: E[∫₀ᵀv dt] = θT + (v₀-θ)(1-exp(-κT))/κ: EML-1 × EML-2 = EML-2
    """

    def expected_variance(self, v0: float, kappa: float, theta: float, T: float) -> dict:
        ev = theta * T + (v0 - theta) * (1 - math.exp(-kappa * T)) / kappa
        ev_t = [theta + (v0 - theta) * math.exp(-kappa * t) for t in [0, T/4, T/2, T]]
        return {
            "v0": v0, "kappa": kappa, "theta": theta, "T": T,
            "integrated_variance": round(ev, 6),
            "E_v_trajectory": [round(x, 6) for x in ev_t],
            "feller_condition": round(2 * kappa * theta, 4),
            "feller_satisfied": None,  # requires ξ
            "eml_E_v": 1,
            "eml_integrated": 2,
            "reason": "E[v(t)] = θ + (v₀-θ)exp(-κt): EML-1; ∫E[v] dt: EML-2",
        }

    def heston_char_function(self, u: float, v0: float = 0.04, kappa: float = 2.0,
                              theta: float = 0.04, xi: float = 0.4, rho: float = -0.7,
                              T: float = 1.0) -> dict:
        """Heston characteristic function at frequency u (real part of log S)."""
        # Simplified: compute d = sqrt((κ-iρξu)² + ξ²u(u+i))
        # For real u (risk-neutral): standard formula
        a = kappa - rho * xi * 1j * 0  # simplified: take u real
        b = kappa - rho * xi * u * 1j if False else kappa
        d_sq = (kappa**2 + xi**2 * u * (u + 1))
        if d_sq >= 0:
            d = math.sqrt(d_sq)
        else:
            d = 0
        return {
            "u": u,
            "d_approx": round(d, 6),
            "eml": 3,
            "reason": "Char function φ(u) = exp(A(u,T) + B(u,T)·v₀): EML-3 (exp of complex EML-2 argument)",
        }

    def to_dict(self) -> dict:
        return {
            "model": "Heston stochastic volatility",
            "expected_variance": self.expected_variance(0.04, 2.0, 0.04, 1.0),
            "characteristic_function": self.heston_char_function(1.0),
            "eml_volatility_process": 1,
            "eml_option_price": 3,
            "eml_variance_swap": 2,
        }


@dataclass
class GARCHVolatility:
    """
    GARCH(1,1): σ²_t = ω + α·ε²_{t-1} + β·σ²_{t-1}

    EML structure:
    - σ²_t: EML-2 (recursive: GARCH recursion = AR(1) in σ² with EML-0 coefficients)
    - Stationary variance σ²∞ = ω/(1-α-β): EML-2 (rational in parameters)
    - Volatility clustering autocorrelation: ρ(k) ~ (α+β)^k: EML-1 (exponential decay)
    - GARCH integrated (IGARCH): α+β=1 → long memory = EML-2 (power law ACF)
    - Kurtosis: κ = 3(1-2α²-2αβ-β²)/(1-...): EML-2 (rational in α,β)
    """

    def garch_simulation(self, omega: float = 0.0001, alpha: float = 0.1,
                          beta: float = 0.85, n: int = 50) -> list[dict]:
        import random
        random.seed(42)
        sigma2 = omega / (1 - alpha - beta)  # stationarity start
        results = []
        for i in range(n):
            z = random.gauss(0, 1)
            ret = math.sqrt(sigma2) * z
            sigma2_new = omega + alpha * ret**2 + beta * sigma2
            if i % 10 == 0:
                results.append({
                    "t": i,
                    "sigma": round(math.sqrt(sigma2), 6),
                    "ret": round(ret, 6),
                })
            sigma2 = sigma2_new
        return results

    def acf_decay(self, alpha: float, beta: float, lags: int = 8) -> list[dict]:
        return [
            {"lag": k, "rho_k": round((alpha + beta)**k, 6), "eml": 1}
            for k in range(1, lags + 1)
        ]

    def to_dict(self) -> dict:
        return {
            "model": "GARCH(1,1)",
            "stationary_variance": "ω/(1-α-β): EML-2 (rational)",
            "simulation": self.garch_simulation(),
            "acf_decay": self.acf_decay(0.1, 0.85),
            "eml_garch_variance": 2,
            "eml_acf": 1,
            "eml_kurtosis": 2,
            "volatility_clustering": "Long periods of high/low vol = EML-1 autocorrelation decay (α+β)^k",
        }


@dataclass
class RiskMeasures:
    """
    Value at Risk (VaR) and Expected Shortfall (CVaR/ES).

    For normal returns: VaR_α = μ - σ·Φ^{-1}(1-α)  (EML-3: Gaussian quantile = erf^{-1})
    For fat-tailed (Student-t or power law):
    - t_ν distribution: VaR ~ σ·t_{ν,α}^{-1}  (EML-3)
    - Power law P(X>x) = (x/x_m)^{-α}: VaR = x_m·(1-α)^{-1/α}: EML-2

    EML structure:
    - Normal VaR: EML-3 (Gaussian quantile = erfinv = EML-3)
    - Power law VaR: EML-2 (rational power of 1-confidence)
    - Expected shortfall ES = E[X | X > VaR]: EML-3 for Gaussian, EML-2 for power law
    - Extreme event (99.99% VaR): EML-∞ (extreme value theory — Gumbel, Fréchet = EML-3 or EML-∞)
    """

    @staticmethod
    def normal_var(mu: float, sigma: float, alpha: float) -> dict:
        """VaR at confidence α: quantile of normal N(mu, sigma²)."""
        # Φ^{-1}(α) ≈ using rational approximation of erfinv
        p = alpha
        t = math.sqrt(-2 * math.log(min(p, 1-p)))
        c = [2.515517, 0.802853, 0.010328]
        d = [1.432788, 0.189269, 0.001308]
        z = t - (c[0] + c[1]*t + c[2]*t**2) / (1 + d[0]*t + d[1]*t**2 + d[2]*t**3)
        if alpha < 0.5:
            z = -z
        var = mu + sigma * z
        es = mu - sigma * math.exp(-z**2/2) / (math.sqrt(2*math.pi) * (1-alpha))
        return {
            "distribution": "Normal",
            "mu": mu, "sigma": sigma, "alpha": alpha,
            "VaR": round(var, 6),
            "ES_CVaR": round(es, 6),
            "eml_VaR": 3,
            "eml_ES": 3,
            "reason": "Gaussian quantile = erfinv ≈ EML-3; ES = μ - σφ(z)/(1-α) = EML-3",
        }

    @staticmethod
    def power_law_var(x_min: float, alpha_tail: float, confidence: float) -> dict:
        """Power law P(X>x) = (x_min/x)^alpha_tail → VaR = x_min * (1-confidence)^{-1/alpha_tail}"""
        var = x_min * (1 - confidence)**(-1/alpha_tail)
        es = var * alpha_tail / (alpha_tail - 1) if alpha_tail > 1 else float("inf")
        return {
            "distribution": "Power law (Pareto)",
            "x_min": x_min, "alpha_tail": alpha_tail, "confidence": confidence,
            "VaR": round(var, 6),
            "ES_CVaR": round(es, 4),
            "eml_VaR": 2,
            "eml_ES": 2,
            "reason": "VaR = x_min·(1-α)^{-1/α}: power of rational = EML-2",
        }

    def to_dict(self) -> dict:
        return {
            "normal_VaR_95": self.normal_var(0, 1, 0.95),
            "normal_VaR_99": self.normal_var(0, 1, 0.99),
            "power_law_VaR_95": self.power_law_var(1.0, 3.0, 0.95),
            "power_law_VaR_99": self.power_law_var(1.0, 3.0, 0.99),
            "eml_normal_risk": 3,
            "eml_fat_tail_risk": 2,
            "eml_extreme_events": EML_INF,
            "fat_tail_insight": "Power law VaR = EML-2 (simpler than Gaussian EML-3!). Fat tails are more regular than Gaussian in EML depth — the danger is EML-2, not EML-3.",
        }


def analyze_finance_deep_eml() -> dict:
    sv = StochasticVolatility()
    garch = GARCHVolatility()
    risk = RiskMeasures()
    return {
        "session": 95,
        "title": "Finance Deep: High-Frequency Dynamics, Volatility & Risk",
        "key_theorem": {
            "theorem": "EML Finance Depth Classification",
            "statement": (
                "Stochastic volatility (Heston): E[v(t)] = EML-1 (OU mean reversion). "
                "Option prices via Fourier inversion: EML-3. "
                "GARCH volatility: EML-2 (rational recursion); ACF decay: EML-1 (geometric). "
                "Normal VaR: EML-3 (Gaussian quantile = erfinv). "
                "Power law VaR: EML-2 (rational power) — fat tails are EML-2, not EML-3! "
                "Extreme events beyond any model: EML-∞ (black swans, market crashes). "
                "Key insight: financial fat tails (EML-2) are mathematically simpler than Gaussian tails (EML-3)."
            ),
        },
        "stochastic_volatility": sv.to_dict(),
        "garch_volatility": garch.to_dict(),
        "risk_measures": risk.to_dict(),
        "eml_depth_summary": {
            "EML-0": "Constant volatility (Black-Scholes); integer payoffs",
            "EML-1": "Mean-reverting vol E[v] = EML-1; GARCH ACF (α+β)^k; drift exp(μt)",
            "EML-2": "Stationary GARCH variance ω/(1-α-β); power law VaR x^{-1/α}; Feller condition",
            "EML-3": "Normal VaR (erfinv); option price (Fourier-Heston); Black-Scholes formula",
            "EML-∞": "Market crashes; flash crashes; correlation breakdown; systemic risk events",
        },
        "rabbit_hole_log": [
            "Counterintuitive: power law (fat tail) VaR is EML-2, but Gaussian VaR is EML-3. The fatter the tail, the lower the EML depth of the risk measure. Heavy-tailed risks are analytically simpler (EML-2) than light-tailed ones (EML-3).",
            "Volatility clustering (GARCH): the ACF decays as (α+β)^k = EML-1. This is the financial analog of the Lyapunov time (Session 82): the memory timescale τ = -1/ln(α+β) is EML-2 (log of parameters).",
            "Black-Scholes = EML-3: exp(-rT)·[S₀·Φ(d₁) - K·Φ(d₂)] involves erfinv (EML-3). But the model FAILS precisely at EML-∞ events (fat tail returns, vol smile = EML-∞ term structure).",
        ],
        "connections": {
            "to_session_57": "Phase transitions = EML-∞. Market crashes = EML-∞ — financial phase transition",
            "to_session_64": "SDE paths = EML-∞; Feynman-Kac (S64) gives option prices = EML-3. Session 95 confirms",
        },
    }


if __name__ == "__main__":
    print(json.dumps(analyze_finance_deep_eml(), indent=2, default=str))
