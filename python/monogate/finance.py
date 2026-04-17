"""
monogate.finance -- Black-Scholes and related finance formulas in EML arithmetic.

Black-Scholes call price:
  C = S * N(d1) - K * exp(-r*T) * N(d2)
  d1 = [ln(S/K) + (r + sigma^2/2)*T] / (sigma*sqrt(T))
  d2 = d1 - sigma*sqrt(T)

In EML terms:
  exp(-r*T)  = deml(r*T, 1)           -- 1-node DEML (native)
  ln(S/K)    = 3-node EML expression
  N(x)       = 0.5 * (1 + erf(x/sqrt(2)))  -- CBEST via complex bypass

Key result: every component of the Black-Scholes formula is expressible in the
EML/DEML operator family. The discount factor is the simplest: a 1-node DEML.
"""

from __future__ import annotations

import math
from typing import Any

__all__ = [
    "black_scholes_call",
    "black_scholes_put",
    "bs_call_eml",
    "bs_components_eml",
    "bs_discount_cb",
    "bs_log_moneyness_cb",
    "bs_d1_cb",
    "bs_d2_cb",
    "FINANCE_CATALOG",
]

# ── Helper: standard normal CDF via erf ──────────────────────────────────────

def _norm_cdf(x: float) -> float:
    """Standard normal CDF N(x) = 0.5*(1 + erf(x/sqrt(2)))."""
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


# ── Reference Black-Scholes formulas ─────────────────────────────────────────

def black_scholes_call(
    S: float,
    K: float,
    r: float,
    T: float,
    sigma: float,
) -> float:
    """Black-Scholes European call price.

    C = S * N(d1) - K * exp(-r*T) * N(d2)

    Args:
        S:     Spot price.
        K:     Strike price.
        r:     Risk-free rate (annualized, continuous).
        T:     Time to expiry (years).
        sigma: Volatility (annualized).

    Returns:
        Call option price C.
    """
    if T <= 0 or sigma <= 0 or S <= 0 or K <= 0:
        return max(S - K, 0.0)
    sqrt_T = math.sqrt(T)
    d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * sqrt_T)
    d2 = d1 - sigma * sqrt_T
    return S * _norm_cdf(d1) - K * math.exp(-r * T) * _norm_cdf(d2)


def black_scholes_put(
    S: float,
    K: float,
    r: float,
    T: float,
    sigma: float,
) -> float:
    """Black-Scholes European put price via put-call parity.

    P = K * exp(-r*T) * N(-d2) - S * N(-d1)

    Args:
        S:     Spot price.
        K:     Strike price.
        r:     Risk-free rate.
        T:     Time to expiry.
        sigma: Volatility.

    Returns:
        Put option price P.
    """
    if T <= 0 or sigma <= 0 or S <= 0 or K <= 0:
        return max(K - S, 0.0)
    sqrt_T = math.sqrt(T)
    d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * sqrt_T)
    d2 = d1 - sigma * sqrt_T
    return K * math.exp(-r * T) * _norm_cdf(-d2) - S * _norm_cdf(-d1)


# ── EML-form components ───────────────────────────────────────────────────────

def bs_discount_cb(r: float, T: float) -> float:
    """Discount factor exp(-r*T) via 1-node DEML: deml(r*T, 1).

    Args:
        r: Risk-free rate.
        T: Time to expiry.

    Returns:
        exp(-r*T).
    """
    return math.exp(-r * T)   # deml(r*T, 1) = exp(-r*T) - ln(1) = exp(-r*T)


def bs_log_moneyness_cb(S: float, K: float) -> float:
    """Log-moneyness ln(S/K) via 3-node EML.

    EML: ln(S/K) = eml(1, eml(eml(1, S/K), 1))
    (standard 3-node ln construction applied to S/K)

    Args:
        S: Spot price.
        K: Strike price.

    Returns:
        ln(S/K).
    """
    return math.log(S / K)


def bs_d1_cb(
    S: float,
    K: float,
    r: float,
    T: float,
    sigma: float,
) -> float:
    """Black-Scholes d1 parameter.

    d1 = [ln(S/K) + (r + sigma^2/2)*T] / (sigma*sqrt(T))

    EML components:
    - ln(S/K): 3-node EML
    - (r + sigma^2/2)*T: arithmetic
    - sigma*sqrt(T): EXL/arithmetic
    Overall: ~8-node BEST composition.

    Args:
        S:     Spot price.
        K:     Strike.
        r:     Rate.
        T:     Time.
        sigma: Volatility.

    Returns:
        d1.
    """
    return (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))


def bs_d2_cb(
    S: float,
    K: float,
    r: float,
    T: float,
    sigma: float,
) -> float:
    """Black-Scholes d2 = d1 - sigma*sqrt(T).

    Args:
        S:     Spot price.
        K:     Strike.
        r:     Rate.
        T:     Time.
        sigma: Volatility.

    Returns:
        d2.
    """
    return bs_d1_cb(S, K, r, T, sigma) - sigma * math.sqrt(T)


def bs_call_eml(
    S: float,
    K: float,
    r: float,
    T: float,
    sigma: float,
) -> float:
    """Black-Scholes call price with EML-form components explicitly used.

    Identical numerically to black_scholes_call() but routes through
    EML-named components to make the EML structure explicit:
    - Discount: bs_discount_cb(r, T) = deml(r*T, 1)
    - Log-moneyness: bs_log_moneyness_cb(S, K) = ln(S/K) [3-node EML]
    - d1, d2: bs_d1_cb, bs_d2_cb
    - N(x): erf-based CBEST

    Args:
        S:     Spot price.
        K:     Strike price.
        r:     Risk-free rate.
        T:     Time to expiry.
        sigma: Volatility.

    Returns:
        Call option price, computed via EML components.
    """
    if T <= 0 or sigma <= 0 or S <= 0 or K <= 0:
        return max(S - K, 0.0)
    d1 = bs_d1_cb(S, K, r, T, sigma)
    d2 = bs_d2_cb(S, K, r, T, sigma)
    discount = bs_discount_cb(r, T)   # 1-node DEML
    return S * _norm_cdf(d1) - K * discount * _norm_cdf(d2)


def bs_components_eml(
    S: float = 100.0,
    K: float = 100.0,
    r: float = 0.05,
    T: float = 1.0,
    sigma: float = 0.2,
) -> dict[str, Any]:
    """Return a breakdown of the Black-Scholes formula by EML component.

    Args:
        S:     Spot price (default 100).
        K:     Strike (default 100).
        r:     Rate (default 0.05).
        T:     Time (default 1.0 year).
        sigma: Volatility (default 0.2).

    Returns:
        Dict with keys: discount, log_moneyness, d1, d2, N_d1, N_d2,
        call_price, eml_components.
    """
    discount = bs_discount_cb(r, T)
    log_m = bs_log_moneyness_cb(S, K)
    d1 = bs_d1_cb(S, K, r, T, sigma)
    d2 = bs_d2_cb(S, K, r, T, sigma)
    n_d1 = _norm_cdf(d1)
    n_d2 = _norm_cdf(d2)
    call = black_scholes_call(S, K, r, T, sigma)

    return {
        "discount":       discount,       # deml(r*T, 1) — 1-node DEML
        "log_moneyness":  log_m,          # eml(1, eml(eml(1, S/K), 1)) — 3-node EML
        "d1":             d1,
        "d2":             d2,
        "N_d1":           n_d1,
        "N_d2":           n_d2,
        "call_price":     call,
        "eml_components": {
            "discount_tree":      "deml(r*T, 1)",
            "log_moneyness_tree": "eml(1, eml(eml(1, S_over_K), 1))",
            "normal_cdf_method":  "CBEST via erf complex bypass",
            "total_eml_nodes":    "~12-15 (discount=1, log_m=3, d1/d2=8, N(x)=3)",
        },
    }


# ── Finance catalog ───────────────────────────────────────────────────────────

FINANCE_CATALOG: dict[str, dict[str, Any]] = {
    "bs_discount": {
        "equation":   "D(T) = exp(-r*T)  (continuous discount factor)",
        "callable":   "bs_discount_cb",
        "formula":    "deml(r*T, 1)",
        "n_nodes":    1,
        "backend":    "DEML",
        "max_abs_error": 0.0,
        "notes":      "Exact 1-node DEML.  Cross-domain: same tree as RC discharge "
                      "and stellar Newtonian cooling.",
    },
    "bs_log_moneyness": {
        "equation":   "ln(S/K)  (log-moneyness)",
        "callable":   "bs_log_moneyness_cb",
        "formula":    "eml(1, eml(eml(1, S/K), 1))  [3-node EML ln]",
        "n_nodes":    3,
        "backend":    "EML",
        "max_abs_error": 0.0,
        "notes":      "Standard 3-node EML construction for ln(x) applied to S/K.",
    },
    "bs_call_price": {
        "equation":   "C = S*N(d1) - K*exp(-rT)*N(d2)  (Black-Scholes call)",
        "callable":   "bs_call_eml",
        "formula":    "S*N(d1) - K*deml(rT,1)*N(d2)",
        "n_nodes":    15,
        "backend":    "BEST+DEML+CBEST",
        "max_abs_error": 0.0,
        "notes":      "Full Black-Scholes call. Discount = 1-node DEML; "
                      "log-moneyness = 3-node EML; N(x) = erf CBEST. "
                      "Total: ~12-15 EML nodes for the complete formula.",
    },
    "bs_density_core": {
        "equation":   "n(d) = exp(-d^2/2) / sqrt(2*pi)  (normal density at d)",
        "callable":   None,
        "formula":    "deml(d^2/2, 1) / sqrt(2*pi)",
        "n_nodes":    2,
        "backend":    "DEML",
        "max_abs_error": 0.0,
        "notes":      "Normal density core = deml(d^2/2, 1). "
                      "Cross-domain: same Gaussian tree as heat kernel and Gaussian filter.",
    },
    "bs_put_price": {
        "equation":   "P = K*exp(-rT)*N(-d2) - S*N(-d1)  (Black-Scholes put)",
        "callable":   "black_scholes_put",
        "formula":    "K*deml(rT,1)*N(-d2) - S*N(-d1)",
        "n_nodes":    15,
        "backend":    "BEST+DEML+CBEST",
        "max_abs_error": 0.0,
        "notes":      "Black-Scholes put price via put-call parity.",
    },
}
