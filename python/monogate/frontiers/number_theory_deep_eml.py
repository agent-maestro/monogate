"""
Session 90 — Number Theory Deep: Dirichlet L-Functions, Primes & Zeta Zeros

EML depth of Dirichlet L-functions, prime gaps, Möbius function, explicit formula,
and the connection between primes and zeros of L-functions.

Key theorem: The explicit formula ψ(x) = x - Σ_{ρ} x^ρ/ρ - ln(2π) - ½ln(1-x^{-2})
expresses the prime-counting step function (EML-∞ jumps) as a sum of EML-3 oscillatory
terms (x^ρ = exp(ρ·ln x) = EML-3 since ρ = 1/2+iγ).
"""

from __future__ import annotations
import math, json
from dataclasses import dataclass, field
from typing import Callable


EML_INF = float("inf")
PI = math.pi


@dataclass
class DirichletLFunction:
    """
    Dirichlet L-function: L(s,χ) = Σ_{n=1}^∞ χ(n)/n^s

    EML depth:
    - χ(n): Dirichlet character = EML-3 (periodic, χ(n) = exp(2πi·k·n/q) for primitive χ)
    - n^{-s}: EML-3 (= exp(-s·ln n))
    - L(s,χ) = Σ χ(n)·exp(-s·ln n): EML-3
    - Euler product: L(s,χ) = ∏_p (1-χ(p)p^{-s})^{-1}: EML-3
    - GRH for L(s,χ): zeros on Re(s)=1/2: EML-3 (same as RH)
    """

    @staticmethod
    def dirichlet_characters_mod4() -> list[dict]:
        """Characters mod 4: χ₀ (principal) and χ₁ (non-principal)."""
        return [
            {
                "modulus": 4,
                "name": "χ₀ (principal)",
                "values": {1: 1, 2: 0, 3: 1, 4: 0},
                "primitive": False,
                "eml": 0,
                "reason": "Principal character: χ₀(n)=1 if gcd(n,q)=1 else 0 — EML-0 (integer-valued)",
            },
            {
                "modulus": 4,
                "name": "χ₁ (Kronecker symbol mod 4)",
                "values": {1: 1, 2: 0, 3: -1, 4: 0},
                "primitive": True,
                "eml": 0,
                "reason": "Values in {-1,0,1} — EML-0 per value; pattern = EML-3 (periodic = exp(2πin/4))",
            },
        ]

    def partial_L(self, chi_values: dict, s_re: float, s_im: float, N: int = 200) -> dict:
        """Compute |L(s,χ)| via partial Dirichlet series."""
        q = max(chi_values.keys())
        re_sum = im_sum = 0.0
        for n in range(1, N + 1):
            chi_n = chi_values.get(n % q if n % q != 0 else q, 0)
            if chi_n == 0:
                continue
            ln_n = math.log(n)
            modulus = n ** (-s_re)
            re_sum += chi_n * modulus * math.cos(-s_im * ln_n)
            im_sum += chi_n * modulus * math.sin(-s_im * ln_n)
        return {
            "s": f"{s_re}+{s_im}i",
            "Re_L": round(re_sum, 6),
            "Im_L": round(im_sum, 6),
            "modulus_L": round(math.sqrt(re_sum**2 + im_sum**2), 6),
            "N_terms": N,
        }

    def beta_function_values(self) -> list[dict]:
        """Dirichlet beta function β(s) = L(s,χ₋₄) = 1 - 1/3^s + 1/5^s - ..."""
        results = []
        for n_terms in [10, 50, 200]:
            beta_1 = sum((-1)**k / (2*k+1) for k in range(n_terms))
            results.append({
                "n_terms": n_terms,
                "beta_1": round(beta_1, 8),
                "pi_over_4": round(PI / 4, 8),
                "error": round(abs(beta_1 - PI/4), 8),
                "eml_beta_1": 3,
                "reason": "β(1) = π/4: π = EML-3",
            })
        return results

    def to_dict(self) -> dict:
        chi_kronecker = {1: 1, 2: 0, 3: -1, 4: 0}
        return {
            "definition": "L(s,χ) = Σ χ(n)/n^s = ∏_p (1-χ(p)p^{-s})^{-1}",
            "eml_depth": 3,
            "eml_reason": "χ(n) periodic + n^{-s} = exp(-s·ln n) → EML-3 series",
            "characters_mod4": self.dirichlet_characters_mod4(),
            "L_values": [
                self.partial_L(chi_kronecker, 0.5, 0, 200),
                self.partial_L(chi_kronecker, 0.5, 14.13, 200),
            ],
            "dirichlet_beta": self.beta_function_values(),
            "GRH": "Generalized RH: zeros of L(s,χ) on Re(s)=1/2 — EML-3 critical line",
        }


@dataclass
class ExplicitFormula:
    """
    Von Mangoldt explicit formula: ψ(x) = x - Σ_ρ x^ρ/ρ - ln(2π) - ½ln(1-1/x²)

    EML depth:
    - ψ(x) = Σ_{p^k≤x} ln(p): EML-∞ (step function — jumps at prime powers)
    - x: linear = EML-1 (trivially exp(ln x))
    - x^ρ = exp(ρ·ln x): EML-3 (exp of product involving ln x = EML-2)
    - Σ_ρ x^ρ/ρ: EML-3 (superposition of EML-3 oscillations at Riemann zero frequencies)
    - ln(2π): EML-2 (logarithm of constant)

    The explicit formula decomposes EML-∞ (prime distribution) into EML-3 waves!
    This is the deepest connection: EML-∞ = EML-1 + EML-3 (Fourier decomposition over zeros).
    """

    RIEMANN_ZEROS_IM = [14.1347, 21.022, 25.011, 30.425, 32.935,
                        37.586, 40.919, 43.327, 48.005, 49.774]

    def psi_explicit(self, x: float, n_zeros: int = 10) -> dict:
        """Approximate ψ(x) via explicit formula with first n_zeros."""
        if x <= 1:
            return {}
        main = x
        oscillatory = 0.0
        for gamma in self.RIEMANN_ZEROS_IM[:n_zeros]:
            rho_re = 0.5
            rho_im = gamma
            # x^rho = exp(rho*ln x) = x^0.5 * (cos(gamma*ln x) + i*sin(gamma*ln x))
            # Re(x^rho / rho) = x^0.5 * Re(1/rho) * cos(gamma*ln x) + ...
            # For rho = 1/2 + i*gamma: 1/rho = (1/2-i*gamma)/(1/4+gamma^2)
            rho_mod2 = rho_re**2 + rho_im**2
            inv_re = rho_re / rho_mod2
            inv_im = -rho_im / rho_mod2
            x_half = x**0.5
            ln_x = math.log(x)
            cos_gln = math.cos(rho_im * ln_x)
            sin_gln = math.sin(rho_im * ln_x)
            # Re(x^rho * (1/rho)) = x^0.5 * Re((cos+i*sin)*(inv_re+i*inv_im))
            re_contribution = x_half * (cos_gln * inv_re - sin_gln * inv_im)
            oscillatory += 2 * re_contribution  # factor 2 for conjugate pair rho and rho-bar
        correction = -math.log(2 * PI)
        psi_approx = main - oscillatory + correction
        # Actual ψ(x): count prime powers
        psi_actual = sum(math.log(p) for p in range(2, int(x) + 1)
                         if all(p % d != 0 for d in range(2, int(p**0.5) + 1)))
        return {
            "x": x,
            "psi_explicit_approx": round(psi_approx, 4),
            "psi_actual_primes": round(psi_actual, 4),
            "main_term_x": round(main, 4),
            "oscillatory_correction": round(-oscillatory, 4),
            "n_zeros_used": n_zeros,
        }

    def to_dict(self) -> dict:
        x_vals = [10, 20, 50, 100]
        return {
            "formula": "ψ(x) = x - Σ_ρ x^ρ/ρ - ln(2π) - ½ln(1-x^{-2})",
            "eml_depth_psi": EML_INF,
            "eml_depth_main_term": 1,
            "eml_depth_oscillatory": 3,
            "depth_decomposition": "EML-∞ prime staircase = EML-1 main + EML-3 zeros — the explicit formula is an EML depth decomposition",
            "approximations": [self.psi_explicit(x, 10) for x in x_vals],
        }


@dataclass
class MobiusAndLiouville:
    """
    Möbius μ(n) and Liouville λ(n): arithmetic functions with EML-∞ behavior.

    μ(n) = 0 if p²|n; (-1)^k if n = p₁p₂...p_k distinct primes.
    λ(n) = (-1)^Ω(n) where Ω(n) = total prime factors (with multiplicity).

    EML depth:
    - μ(n) per value: EML-0 (integer in {-1,0,1})
    - Σ_{n≤x} μ(n) = M(x): EML-∞ (no closed form; oscillates irregularly)
    - Under RH: M(x) = O(x^{1/2+ε}) — EML-3 bound (x^{1/2} = exp(½ ln x) = EML-3)
    - 1/ζ(s) = Σ μ(n)/n^s: EML-3 (Dirichlet series in EML-3 class)
    - Mertens conjecture: |M(x)| < √x — disproved (Odlyzko-te Riele 1985): EML-∞ violations
    """

    @staticmethod
    def sieve_mobius(n_max: int) -> list[int]:
        mu = [0] * (n_max + 1)
        mu[1] = 1
        is_prime = [True] * (n_max + 1)
        primes = []
        for p in range(2, n_max + 1):
            if is_prime[p]:
                primes.append(p)
                mu[p] = -1
            for q in primes:
                if p * q > n_max:
                    break
                is_prime[p * q] = False
                if p % q == 0:
                    mu[p * q] = 0
                    break
                else:
                    mu[p * q] = -mu[p]
        return mu

    def mertens_function(self, N: int = 100) -> list[dict]:
        mu = self.sieve_mobius(N)
        M = 0
        results = []
        for n in range(1, N + 1):
            M += mu[n]
            if n % 10 == 0 or n <= 5:
                results.append({
                    "n": n,
                    "M_n": M,
                    "sqrt_n": round(n**0.5, 3),
                    "within_mertens_bound": abs(M) < n**0.5,
                })
        return results

    def liouville_partial_sum(self, N: int = 50) -> list[dict]:
        """λ(n) = (-1)^Ω(n); L(x) = Σ_{n≤x} λ(n)."""
        mu = self.sieve_mobius(N)
        # λ(n): count total prime factors
        omega = [0] * (N + 1)
        for p in range(2, N + 1):
            if all(p % d != 0 for d in range(2, int(p**0.5) + 1)):
                for k in range(p, N + 1, p):
                    m = k
                    while m % p == 0:
                        omega[k] += 1
                        m //= p
        lam = [(-1)**omega[n] for n in range(N + 1)]
        L = 0
        results = []
        for n in range(1, N + 1):
            L += lam[n]
            if n % 5 == 0:
                results.append({"n": n, "L_n": L, "lambda_n": lam[n]})
        return results

    def to_dict(self) -> dict:
        return {
            "mobius_mu": {
                "definition": "μ(n) = 0 (sq-free fails) or (-1)^ω(n)",
                "eml_per_value": 0,
                "eml_partial_sum_M_x": EML_INF,
                "eml_under_rh": 3,
                "reason_under_rh": "M(x) = O(x^{1/2+ε}) under RH: x^{1/2} = EML-3",
            },
            "mertens_function": self.mertens_function(50),
            "liouville_lambda": self.liouville_partial_sum(50),
            "mertens_conjecture": {
                "statement": "|M(x)| < √x for all x > 1",
                "status": "DISPROVED (Odlyzko-te Riele 1985)",
                "eml_violation": EML_INF,
                "reason": "Disproof uses EML-∞ oscillations in M(x) that exceed √x",
            },
        }


def analyze_number_theory_deep_eml() -> dict:
    L = DirichletLFunction()
    explicit = ExplicitFormula()
    mobius = MobiusAndLiouville()
    return {
        "session": 90,
        "title": "Number Theory Deep: Dirichlet L-Functions, Primes & Zeta Zeros",
        "key_theorem": {
            "theorem": "EML Explicit Formula Decomposition",
            "statement": (
                "The von Mangoldt explicit formula decomposes the prime-counting function ψ(x) "
                "(EML-∞: irregular step function) into EML-1 (main term x) + EML-3 oscillations "
                "(Σ x^ρ/ρ with ρ on critical line). "
                "This is the EML depth decomposition of primes: EML-∞ = EML-1 + EML-3. "
                "Dirichlet L-functions are EML-3 (Euler product over EML-3 characters). "
                "Möbius M(x) is EML-∞ unconditionally; EML-3 under RH."
            ),
        },
        "dirichlet_L_functions": L.to_dict(),
        "explicit_formula": explicit.to_dict(),
        "mobius_liouville": mobius.to_dict(),
        "eml_depth_summary": {
            "EML-0": "μ(n) per value ∈ {-1,0,1}; λ(n) per value; prime indicators",
            "EML-1": "Main term x in explicit formula; prime number theorem x/ln(x)",
            "EML-2": "ln(x) corrections; Meissel-Mertens constant; prime gap mean ln(p)",
            "EML-3": "x^{1/2+iγ} oscillatory terms; L(s,χ) Dirichlet series; M(x) under RH",
            "EML-∞": "ψ(x) full prime staircase; M(x) unconditional; prime gap max",
        },
        "rabbit_hole_log": [
            "The explicit formula is literally an EML decomposition: it writes an EML-∞ object as EML-1 + (sum of EML-3 terms). Each Riemann zero contributes one EML-3 frequency. RH = all frequencies have amplitude x^{1/2} (EML-3 bound).",
            "Dirichlet characters χ(n) mod q: their Gauss sums τ(χ) = Σ χ(n)exp(2πin/q) are EML-3 (exponential sum). |τ(χ)|² = q for primitive χ — EML-0 = q (integer).",
            "Twin prime conjecture: prime gaps p_{n+1}-p_n are EML-∞ (no formula). Hardy-Littlewood conjectures: density of twin primes ~ 2C₂·x/ln²x (EML-2 density).",
        ],
        "connections": {
            "to_session_89": "Session 89: RH zeros = EML-3. Session 90: explicit formula uses those zeros to reconstruct EML-∞ prime distribution",
            "to_session_87": "Session 87: Dedekind η(τ) = EML-3. Session 90: L(s,χ) = EML-3 — both are EML-3 arithmetic series",
        },
    }


if __name__ == "__main__":
    print(json.dumps(analyze_number_theory_deep_eml(), indent=2, default=str))
