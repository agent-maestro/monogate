"""
Session 169 — Financial Mathematics: EML Depth of Market Dynamics

EML operator: eml(x,y) = exp(x) - ln(y)
Key theorem: Black-Scholes is EML-3 (log-normal process, heat equation);
market crashes are EML-∞ (tail events beyond Gaussian, fat tails);
option pricing = EML-2 (risk-neutral measure); market microstructure = EML-∞.
"""
from __future__ import annotations
import math
from dataclasses import dataclass
from typing import Any


@dataclass
class BlackScholes:
    """Black-Scholes option pricing — EML-3 framework."""

    S: float = 100.0   # spot price
    K: float = 100.0   # strike
    T: float = 1.0     # time to expiry
    r: float = 0.05    # risk-free rate
    sigma: float = 0.2  # volatility

    def d1(self) -> float:
        """d₁ = (log(S/K) + (r + σ²/2)T) / (σ√T). EML-2 (log term)."""
        return (math.log(self.S / self.K) + (self.r + 0.5 * self.sigma ** 2) * self.T) / \
               (self.sigma * math.sqrt(self.T))

    def d2(self) -> float:
        """d₂ = d₁ - σ√T. EML-2."""
        return self.d1() - self.sigma * math.sqrt(self.T)

    def norm_cdf(self, x: float) -> float:
        """Φ(x) = (1 + erf(x/√2))/2. EML-3 (error function involves integral of Gaussian)."""
        return 0.5 * (1 + math.erf(x / math.sqrt(2)))

    def call_price(self) -> float:
        """C = S·Φ(d₁) - K·e^{-rT}·Φ(d₂). EML-3 (Φ = EML-3, e^{-rT} = EML-1)."""
        return self.S * self.norm_cdf(self.d1()) - \
               self.K * math.exp(-self.r * self.T) * self.norm_cdf(self.d2())

    def put_price(self) -> float:
        """P = K·e^{-rT}·Φ(-d₂) - S·Φ(-d₁). EML-3."""
        return self.K * math.exp(-self.r * self.T) * self.norm_cdf(-self.d2()) - \
               self.S * self.norm_cdf(-self.d1())

    def delta(self) -> float:
        """Δ = Φ(d₁). EML-3."""
        return self.norm_cdf(self.d1())

    def vega(self) -> float:
        """ν = S·φ(d₁)·√T. φ = Gaussian density. EML-3."""
        phi = math.exp(-self.d1() ** 2 / 2) / math.sqrt(2 * math.pi)
        return self.S * phi * math.sqrt(self.T)

    def analyze(self) -> dict[str, Any]:
        d1 = self.d1()
        d2 = self.d2()
        call = self.call_price()
        put = self.put_price()
        greeks = {"delta": round(self.delta(), 6), "vega": round(self.vega(), 4)}
        implied_vol_approximation = self.sigma
        return {
            "model": "BlackScholes",
            "S": self.S, "K": self.K, "T": self.T, "r": self.r, "sigma": self.sigma,
            "d1": round(d1, 6), "d2": round(d2, 6),
            "call_price": round(call, 4),
            "put_price": round(put, 4),
            "greeks": greeks,
            "put_call_parity_check": round(call - put - self.S + self.K * math.exp(-self.r * self.T), 6),
            "eml_depth": {"d1_d2": 2, "call_price": 3, "greeks": 3, "bs_framework": 3},
            "key_insight": "BS call/put = EML-3 (Gaussian CDF); d₁,d₂ = EML-2 (log terms)"
        }


@dataclass
class MarketMicrostructure:
    """Order book, bid-ask spread, market impact — EML depth."""

    def kyle_lambda(self, sigma_v: float = 0.1, sigma_u: float = 1.0) -> float:
        """
        Kyle (1985): λ = σ_v / (2σ_u). Price impact per unit order flow. EML-0.
        λ measures information advantage. Linear price impact.
        """
        return sigma_v / (2 * sigma_u)

    def amihud_illiquidity(self, returns: list[float], volumes: list[float]) -> float:
        """
        Amihud: ILLIQ = (1/T) Σ|r_t|/Volume_t. EML-0 (mean of ratios).
        """
        if not returns or not volumes:
            return 0.0
        return sum(abs(r) / (v + 1e-10) for r, v in zip(returns, volumes)) / len(returns)

    def market_impact(self, order_size: float, ADV: float = 1e6,
                       sigma: float = 0.02) -> float:
        """
        Square-root law: MI = σ * sqrt(order_size / ADV). EML-2 (sqrt = EML-2).
        Non-linear market impact = EML-∞ (beyond sqrt law in extreme cases).
        """
        return sigma * math.sqrt(order_size / ADV)

    def bid_ask_spread(self, sigma: float = 0.01, lambda_: float = 0.1) -> float:
        """
        Glosten-Milgrom: spread = 2λσ. EML-0 (linear).
        Spread = 2 * adverse selection cost. EML-0.
        """
        return 2 * lambda_ * sigma

    def analyze(self) -> dict[str, Any]:
        kyle = self.kyle_lambda()
        test_returns = [0.01, -0.02, 0.015, -0.01, 0.005]
        test_volumes = [1e5, 2e5, 1.5e5, 3e5, 1e5]
        amihud = self.amihud_illiquidity(test_returns, test_volumes)
        impact = {q: round(self.market_impact(q), 6) for q in [1e3, 1e4, 1e5, 1e6]}
        spread = self.bid_ask_spread()
        return {
            "model": "MarketMicrostructure",
            "kyle_lambda": round(kyle, 6),
            "amihud_illiquidity": round(amihud, 8),
            "market_impact_sqrt_law": impact,
            "bid_ask_spread": round(spread, 4),
            "eml_depth": {"kyle_lambda": 0, "amihud": 0,
                          "market_impact": 2, "flash_crash": "∞"},
            "key_insight": "Spread = EML-0; market impact = EML-2 (√); flash crash = EML-∞"
        }


@dataclass
class TailRiskEML:
    """Fat tails, extreme value theory, and market crashes."""

    def pareto_tail(self, x: float, alpha: float = 2.5, x_min: float = 1.0) -> float:
        """
        P(X > x) = (x_min/x)^α. EML-2. Fat tail: α < 2 (infinite variance).
        S&P 500 return tail: α ≈ 3 (finite variance, fat tail).
        """
        if x < x_min:
            return 1.0
        return (x_min / x) ** alpha

    def black_swan_probability(self, sigma_gauss: float = 0.01,
                                n_sigmas: float = 10.0) -> dict[str, Any]:
        """
        Gaussian: P(|r| > 10σ) = 2*Φ(-10) ≈ 10^{-23}. EML-3 (Gaussian tail).
        Fat tail: P(|r| > 10σ) ≈ (1/10)^α ≈ 10^{-7} for α=3. EML-2.
        Black swan excess = fat tail / Gaussian ≈ 10^{16}. EML-∞.
        """
        x = n_sigmas * sigma_gauss
        gauss_prob = 2 * (1 - 0.5 * (1 + math.erf(n_sigmas / math.sqrt(2))))
        fat_prob = self.pareto_tail(n_sigmas, alpha=3.0, x_min=1.0)
        if gauss_prob > 0:
            excess = fat_prob / (gauss_prob + 1e-30)
        else:
            excess = float('inf')
        return {
            "n_sigmas": n_sigmas,
            "gaussian_prob": f"{gauss_prob:.2e}",
            "fat_tail_prob": f"{fat_prob:.4f}",
            "probability_excess": f"{excess:.2e}" if excess < 1e50 else "∞",
            "eml_depth_gaussian": 3,
            "eml_depth_fat_tail": 2,
            "eml_depth_gap": "∞"
        }

    def extreme_value_gev(self, x: float, mu: float = 0.0,
                           sigma: float = 1.0, xi: float = 0.3) -> float:
        """
        GEV distribution: F(x) = exp(-(1+ξ*(x-μ)/σ)^{-1/ξ}).
        EML-1 (exp of power law). ξ > 0: Fréchet (heavy tail). EML-1 overall.
        """
        z = 1 + xi * (x - mu) / sigma
        if z <= 0:
            return 0.0
        return math.exp(-(z ** (-1.0 / xi)))

    def analyze(self) -> dict[str, Any]:
        x_vals = [1, 2, 5, 10, 20]
        pareto = {x: round(self.pareto_tail(x), 6) for x in x_vals}
        black_swan = self.black_swan_probability()
        gev = {x: round(self.extreme_value_gev(x), 6) for x in [-1, 0, 1, 2, 3]}
        return {
            "model": "TailRiskEML",
            "pareto_tail": pareto,
            "black_swan": black_swan,
            "gev_distribution": gev,
            "eml_depth": {"pareto_tail": 2, "gaussian_tail": 3,
                          "gev": 1, "crash_event": "∞"},
            "key_insight": "Fat tails = EML-2; Gaussian tails = EML-3; market crash = EML-∞"
        }


def analyze_financial_math_eml() -> dict[str, Any]:
    bs = BlackScholes(S=100, K=100, T=1.0, r=0.05, sigma=0.2)
    micro = MarketMicrostructure()
    tail = TailRiskEML()
    return {
        "session": 169,
        "title": "Financial Mathematics: EML Depth of Market Dynamics",
        "eml_operator": "eml(x,y) = exp(x) - ln(y)",
        "black_scholes": bs.analyze(),
        "market_microstructure": micro.analyze(),
        "tail_risk": tail.analyze(),
        "eml_depth_summary": {
            "EML-0": "Bid-ask spread, Kyle λ, Amihud illiquidity, put-call parity (integer check)",
            "EML-1": "Discount factor e^{-rT}, GEV distribution, GARCH volatility clustering",
            "EML-2": "d₁,d₂ log terms, market impact √(Q/ADV), fat tail Pareto",
            "EML-3": "Black-Scholes call price (Gaussian CDF), delta, vega, Gaussian return tails",
            "EML-∞": "Market crashes, flash crashes, contagion, systemic risk"
        },
        "key_theorem": (
            "The EML Financial Mathematics Depth Theorem: "
            "Black-Scholes is EML-3: it assumes log-normal prices (exp of Brownian motion = EML-3). "
            "The Greeks (delta, vega) are EML-3 (Gaussian CDF). "
            "Market microstructure (spreads, Kyle's λ) is EML-0. "
            "Fat tails are EML-2 (power law), but Gaussian model predicts EML-3 tails. "
            "The gap between EML-2 fat tails and EML-3 Gaussian predictions is EML-∞: "
            "it explains why Black-Scholes fails in crashes, and why market crashes are EML-∞ events."
        ),
        "rabbit_hole_log": [
            "BS d₁ = log(S/K)/(σ√T) = EML-2: log ratio (same as running coupling α_s!)",
            "BS call = EML-3: Φ(d₁) = error function = integral of Gaussian = EML-3",
            "e^{-rT} = EML-1: discount factor (same as BCS, Kondo, instanton!)",
            "Fat tail P(X>x) = x^{-α} = EML-2: power law (same as Zipf, SOC avalanche)",
            "Market crash = EML-∞: 1987 crash was ~25σ event — impossible under Gaussian (EML-3)",
            "Kyle λ = EML-0: linear price impact (simplest possible market structure)"
        ],
        "connections": {
            "S156_stochastic": "BS = log-normal = Brownian motion = EML-3 (from S156)",
            "S165_soc": "Market crashes = SOC avalanches: same EML-∞ structure",
            "S155_qft_nonpert": "e^{-rT} = EML-1: same depth class as instanton, BCS, Kondo"
        }
    }


if __name__ == "__main__":
    import json
    print(json.dumps(analyze_financial_math_eml(), indent=2, default=str))
