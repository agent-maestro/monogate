"""
Session 71 — Pseudo vs True Randomness & EML Complexity

Linear congruential generators, Mersenne Twister, cryptographic PRNGs, and
the EML depth as a randomness measure.

Key theorem: A sequence is pseudo-random iff its minimal EML depth is finite (EML-2 for PRNGs);
truly random sequences are EML-∞.
"""

from __future__ import annotations
import math
import json
from dataclasses import dataclass, field
from typing import Iterator


EML_INF = float("inf")


@dataclass
class EMLClass:
    depth: float
    label: str
    reason: str

    def __str__(self) -> str:
        d = "∞" if self.depth == EML_INF else str(int(self.depth))
        return f"EML-{d}: {self.label}"


# ---------------------------------------------------------------------------
# Linear Congruential Generator (LCG)
# ---------------------------------------------------------------------------

@dataclass
class LCG:
    """
    x_{n+1} = (a·x_n + c) mod m

    Closed form: x_n = (a^n · x_0 + c·(a^n - 1)/(a-1)) mod m

    EML analysis:
    - a^n = exp(n·ln a) — EML-2 (one exp, one ln)
    - The closed form is EML-2 as a function of n
    - Output sequence has full period (Hull-Dobell theorem) when conditions on a,c,m hold
    """
    a: int = 1664525
    c: int = 1013904223
    m: int = 2 ** 32
    seed: int = 12345

    def __post_init__(self) -> None:
        self._state = self.seed

    def next(self) -> int:
        self._state = (self.a * self._state + self.c) % self.m
        return self._state

    def sequence(self, n: int) -> list[int]:
        state = self.seed
        result = []
        for _ in range(n):
            state = (self.a * state + self.c) % self.m
            result.append(state)
        return result

    def closed_form(self, n: int) -> int:
        """x_n = (a^n · x_0 + c·(a^n-1)/(a-1)) mod m"""
        a_n = pow(self.a, n, self.m)
        if self.a == 1:
            x_n = (self.seed + self.c * n) % self.m
        else:
            inv = pow(self.a - 1, -1, self.m)
            x_n = (a_n * self.seed + self.c * (a_n - 1) * inv) % self.m
        return x_n

    def verify_closed_form(self, n_checks: int = 5) -> bool:
        """Verify that closed form matches recurrence."""
        try:
            seq = self.sequence(n_checks)
            return all(seq[i] == self.closed_form(i + 1) for i in range(n_checks))
        except (ValueError, ZeroDivisionError):
            return False  # a-1 not invertible mod m for these parameters

    def eml_classification(self) -> EMLClass:
        return EMLClass(2, "LCG closed form x_n = f(n)", "a^n = exp(n·ln a) → EML-2; full expression is EML-2")

    def to_dict(self) -> dict:
        seq = self.sequence(20)
        normalized = [x / self.m for x in seq]
        # Verify closed form
        closed_ok = self.verify_closed_form(10)
        return {
            "type": "Linear Congruential Generator",
            "parameters": {"a": self.a, "c": self.c, "m": self.m, "seed": self.seed},
            "first_20_values": seq[:20],
            "normalized_01": [round(x, 6) for x in normalized],
            "closed_form_matches_recurrence": closed_ok,
            "closed_form": "x_n = (a^n·x_0 + c·(a^n-1)/(a-1)) mod m",
            "eml_class": str(self.eml_classification()),
            "reason": "a^n = exp(n·ln a) is EML-2; full LCG recurrence is EML-2",
        }


# ---------------------------------------------------------------------------
# Mersenne Twister (simplified model)
# ---------------------------------------------------------------------------

@dataclass
class MersenneTwister:
    """
    MT19937: period 2^{19937}-1, based on linear recurrence over GF(2).

    EML analysis:
    - State update is a linear recurrence over GF(2) → EML-2 structure
    - Closed form: x_n = M^n · x_0 (mod 2) where M is the companion matrix
    - M^n = exp(n·ln M) symbolically (for the integer recurrence) → EML-2
    - Statistical quality: passes all NIST tests → empirically EML-∞ in behavior
    - But: given seed, entire sequence is determined → EML-2 in principle

    Period: 2^19937 - 1 = exp(19937·ln 2) - 1 → EML-2 as a number
    """
    seed: int = 42

    def _mt_simple(self, n: int) -> list[int]:
        """Simplified MT-like generator using Python's random (which uses MT19937)."""
        import random
        rng = random.Random(self.seed)
        return [rng.getrandbits(32) for _ in range(n)]

    def period_as_eml(self) -> dict:
        p = 2 ** 19937 - 1
        log_p = 19937 * math.log(2)  # ln(2^19937 - 1) ≈ 19937·ln 2
        return {
            "period": "2^19937 - 1",
            "log_period": round(log_p, 4),
            "eml_expression": "exp(19937·ln 2) - 1",
            "eml_depth": 2,
        }

    def eml_classification(self) -> EMLClass:
        return EMLClass(2, "MT19937 output sequence", "Linear recurrence over GF(2) → EML-2 closed form")

    def to_dict(self) -> dict:
        seq = self._mt_simple(20)
        return {
            "type": "Mersenne Twister MT19937",
            "seed": self.seed,
            "first_20_values": seq,
            "period": self.period_as_eml(),
            "eml_class": str(self.eml_classification()),
            "reason": (
                "MT state update is a linear recurrence: x_n = M^n·x_0 over GF(2). "
                "M^n symbolically = exp(n·ln M) → EML-2. "
                "Empirically passes all statistical tests, but structurally EML-2."
            ),
            "cryptographic_security": False,
            "note": "MT is not cryptographically secure: given 624 outputs, future outputs are predictable.",
        }


# ---------------------------------------------------------------------------
# Cryptographic PRNG
# ---------------------------------------------------------------------------

@dataclass
class CryptographicPRNG:
    """
    CSPRNGs (e.g., ChaCha20, AES-CTR) are computationally indistinguishable from EML-∞
    but are actually EML-2 (determined by key and counter).

    ChaCha20 state update uses ARX (Add-Rotate-XOR) operations:
    - Each operation is linear or bitwise → polynomial in the state bits
    - Full round function is a polynomial map over GF(2)^512 → EML-2

    EML depth paradox:
    - Structural EML depth: EML-2 (polynomial map)
    - Computational EML depth: EML-∞ (no poly-time algorithm can find the EML-2 expression)
    - This is the cryptographic one-way function: easy to compute, hard to invert
    """

    @staticmethod
    def eml_structural() -> EMLClass:
        return EMLClass(2, "ChaCha20/AES-CTR structure", "ARX operations = polynomial map over GF(2) → EML-2")

    @staticmethod
    def eml_computational() -> EMLClass:
        return EMLClass(EML_INF, "ChaCha20/AES-CTR output (observer view)", "Indistinguishable from EML-∞ by any poly-time adversary")

    @staticmethod
    def to_dict() -> dict:
        return {
            "type": "Cryptographic PRNG (ChaCha20/AES-CTR model)",
            "structural_eml": str(CryptographicPRNG.eml_structural()),
            "computational_eml": str(CryptographicPRNG.eml_computational()),
            "paradox": (
                "CSPRNG is EML-2 structurally (polynomial map of key+counter) "
                "but EML-∞ computationally (no poly-time algorithm identifies the EML-2 form). "
                "This is the EML interpretation of one-way functions and computational pseudorandomness."
            ),
            "eml_one_way_principle": (
                "A function f is one-way iff its EML depth (structural) is finite "
                "but its computational EML depth (to invert) is effectively EML-∞."
            ),
        }


# ---------------------------------------------------------------------------
# EML as Randomness Measure
# ---------------------------------------------------------------------------

@dataclass
class EMLRandomnessMeasure:
    """
    Classifies sources of randomness by their EML depth.

    Spectrum:
    EML-0: Constant sequence (not random at all)
    EML-1: Exponential modulation (structured, not random)
    EML-2: LCG, MT, CSPRNG (structurally deterministic but statistically random)
    EML-3: π digits (transcendental, conjectured normal but EML-3 generating formula)
    EML-∞: True randomness (thermal, radioactive, quantum), Chaitin Ω

    Key theorem: A sequence is pseudo-random iff its minimal EML depth is finite.
    True random iff EML-∞.
    """

    SPECTRUM: list[dict] = field(default_factory=lambda: [
        {
            "source": "Constant 0101... (period 2)",
            "eml_depth": 0,
            "statistical_quality": "fails all tests",
            "deterministic": True,
            "eml_generator": "x_n = n mod 2",
        },
        {
            "source": "Logistic map r=3.57 (onset of chaos)",
            "eml_depth": 2,
            "statistical_quality": "structured correlations",
            "deterministic": True,
            "eml_generator": "x_{n+1} = r·x_n·(1-x_n) — rational recurrence",
        },
        {
            "source": "LCG (linear congruential)",
            "eml_depth": 2,
            "statistical_quality": "passes basic tests, fails lattice test",
            "deterministic": True,
            "eml_generator": "x_n = (a^n·x_0 + ...) mod m = EML-2",
        },
        {
            "source": "Mersenne Twister MT19937",
            "eml_depth": 2,
            "statistical_quality": "passes NIST, Diehard, TestU01",
            "deterministic": True,
            "eml_generator": "linear recurrence mod 2^32 = EML-2",
        },
        {
            "source": "ChaCha20-based CSPRNG",
            "eml_depth_structural": 2,
            "eml_depth_computational": "∞",
            "statistical_quality": "passes all known tests, cryptographically secure",
            "deterministic": True,
            "eml_generator": "ARX polynomial map = EML-2 structurally; EML-∞ computationally",
        },
        {
            "source": "π digits (decimal)",
            "eml_depth": 3,
            "statistical_quality": "conjectured normal (passes frequency tests)",
            "deterministic": True,
            "eml_generator": "BBP formula = EML-3; digits EML-3",
        },
        {
            "source": "Chaitin Ω digits",
            "eml_depth": "∞",
            "statistical_quality": "Martin-Löf random",
            "deterministic": False,
            "eml_generator": "No finite EML tree; left-computable only",
        },
        {
            "source": "Thermal noise (Johnson-Nyquist)",
            "eml_depth": "∞",
            "statistical_quality": "True Gaussian white noise",
            "deterministic": False,
            "eml_generator": "Physical process — no EML-finite generator",
        },
        {
            "source": "Quantum measurement (QRNG)",
            "eml_depth": "∞",
            "statistical_quality": "Certifiably random (Bell inequality)",
            "deterministic": False,
            "eml_generator": "No hidden variable EML-finite generator (Bell theorem)",
        },
    ])

    def theorem_statement(self) -> str:
        return (
            "EML Randomness Theorem: "
            "A sequence s = (s_n) is pseudo-random iff there exists k < ∞ such that "
            "s_n = round(f(n)) for some EML-k function f. "
            "A sequence is truly random iff no EML-finite function generates it, i.e., "
            "the minimal EML depth of any generating function is EML-∞."
        )

    def to_dict(self) -> dict:
        return {
            "theorem": self.theorem_statement(),
            "spectrum": self.SPECTRUM,
        }


# ---------------------------------------------------------------------------
# Lyapunov chaos and EML-∞ transition
# ---------------------------------------------------------------------------

@dataclass
class LyapunovChaos:
    """
    Logistic map x_{n+1} = r·x_n·(1-x_n).

    For r < r_∞ ≈ 3.5699...: periodic orbits → EML-2 (period doubles)
    At r = r_∞: onset of chaos (Feigenbaum)
    For r > r_∞: chaotic → effective EML-∞ in the long-time limit

    EML depth as function of time:
    - Short time: EML-2 (recurrence has closed form)
    - Long time (chaos): effective EML-∞ (Lyapunov divergence)

    Lyapunov exponent λ > 0 → nearby trajectories diverge as exp(λt) → EML-1 divergence rate
    """
    r: float = 3.9

    def iterate(self, x0: float, n: int) -> list[float]:
        x = x0
        trajectory = [x]
        for _ in range(n):
            x = self.r * x * (1 - x)
            trajectory.append(x)
        return trajectory

    def lyapunov_exponent(self, x0: float = 0.5, n: int = 1000) -> float:
        """λ = (1/n) Σ ln|f'(x_i)| where f'(x) = r(1-2x)"""
        x = x0
        total = 0.0
        for _ in range(n):
            deriv = abs(self.r * (1 - 2 * x))
            if deriv > 1e-15:
                total += math.log(deriv)
            x = self.r * x * (1 - x)
        return total / n

    def eml_depth_vs_time(self, n_transient: int = 100, n_sample: int = 50) -> dict:
        """
        Early iterations are EML-2 (rational recurrence).
        After many iterations, sequence is chaotic and effectively EML-∞.
        """
        trajectory = self.iterate(0.4, n_transient + n_sample)
        early = trajectory[:10]
        late = trajectory[n_transient:]
        return {
            "r": self.r,
            "lyapunov_exponent": round(self.lyapunov_exponent(), 4),
            "chaotic": self.lyapunov_exponent() > 0,
            "early_values": [round(x, 6) for x in early],
            "late_values": [round(x, 6) for x in late[:10]],
            "eml_depth_short_time": 2,
            "eml_depth_long_time": "∞",
            "reason": (
                "Short time: recurrence x_n = f^n(x_0) is a rational function → EML-2. "
                "Long time: chaos → Lyapunov divergence exp(λt) → sensitive dependence → "
                "effective EML-∞ (no finite-depth tree predicts x_n for large n without full precision)."
            ),
        }

    def feigenbaum_transition(self) -> dict:
        """At r_∞ ≈ 3.5699..., chaos onset."""
        r_inf = 3.56995  # Feigenbaum point
        lce_below = LyapunovChaos(r=3.4).lyapunov_exponent()
        lce_above = LyapunovChaos(r=3.9).lyapunov_exponent()
        return {
            "r_feigenbaum": r_inf,
            "lyapunov_below_r_inf": round(lce_below, 4),
            "lyapunov_above_r_inf": round(lce_above, 4),
            "eml_transition": "EML-2 → EML-∞ at r = r_∞",
            "feigenbaum_constant_delta": 4.6692016,
            "feigenbaum_eml": "δ = lim (r_{n+1}-r_n)/(r_{n+2}-r_{n+1}) = EML-3 (transcendental constant)",
            "connection": "Same EML-∞ transition as phase transitions (Session 57) and NS blowup (Session 62)",
        }


# ---------------------------------------------------------------------------
# Main analysis
# ---------------------------------------------------------------------------

def analyze_pseudo_random_eml() -> dict:
    """Run full Session 71 analysis."""

    # 1. LCG
    lcg = LCG(seed=42)
    lcg_report = lcg.to_dict()

    # 2. Mersenne Twister
    mt = MersenneTwister(seed=42)
    mt_report = mt.to_dict()

    # 3. CSPRNG
    csprng_report = CryptographicPRNG.to_dict()

    # 4. EML randomness measure
    measure = EMLRandomnessMeasure()
    measure_report = measure.to_dict()

    # 5. Lyapunov chaos
    chaos_periodic = LyapunovChaos(r=3.2)
    chaos_full = LyapunovChaos(r=3.9)

    chaos_report = {
        "periodic_r3.2": chaos_periodic.eml_depth_vs_time(),
        "chaotic_r3.9": chaos_full.eml_depth_vs_time(),
        "feigenbaum_transition": chaos_full.feigenbaum_transition(),
    }

    # 6. EML depth comparison table
    comparison = [
        {"source": "010101...", "eml_depth": 0, "period": 2, "passes_tests": False},
        {"source": "LCG (Numerical Recipes)", "eml_depth": 2, "period": 2**32, "passes_tests": "basic"},
        {"source": "MT19937", "eml_depth": 2, "period": "2^19937-1", "passes_tests": True},
        {"source": "ChaCha20 (structural)", "eml_depth": 2, "period": "2^128", "passes_tests": True},
        {"source": "π digits", "eml_depth": 3, "period": None, "passes_tests": "conjectured"},
        {"source": "Thermal noise", "eml_depth": "∞", "period": None, "passes_tests": True},
        {"source": "QRNG (Bell-certified)", "eml_depth": "∞", "period": None, "passes_tests": True},
        {"source": "Chaitin Ω", "eml_depth": "∞", "period": None, "passes_tests": True},
    ]

    return {
        "session": 71,
        "title": "Pseudo vs True Randomness & EML Complexity",
        "key_theorem": {
            "theorem": "EML Randomness Theorem",
            "statement": (
                "A sequence s = (s_n) is pseudo-random iff its minimal EML depth is finite. "
                "PRNGs are EML-2: their closed-form generator is x_n = f(n) for EML-2 f. "
                "True random sequences (thermal noise, quantum, Chaitin Ω) are EML-∞: "
                "no EML-finite function generates them."
            ),
            "corollary_csprng": (
                "CSPRNGs exhibit an EML depth paradox: structural depth is EML-2 (polynomial key map) "
                "but computational depth is EML-∞ (no poly-time inversion). "
                "This is the EML interpretation of one-way functions."
            ),
            "corollary_chaos": (
                "Deterministic chaotic systems transition from EML-2 (short time) to effective EML-∞ "
                "(long time) at the Lyapunov scale. This is the same EML-∞ transition as "
                "phase transitions (Session 57) and PDE blowup (Session 62)."
            ),
        },
        "lcg": lcg_report,
        "mersenne_twister": mt_report,
        "csprng": csprng_report,
        "randomness_spectrum": measure_report,
        "lyapunov_chaos": chaos_report,
        "eml_depth_comparison": comparison,
        "eml_depth_summary": {
            "EML-0": "Constant and periodic sequences",
            "EML-1": "Exponentially modulated sequences (structured)",
            "EML-2": "LCG, Mersenne Twister, CSPRNG (structurally), logistic map (short time)",
            "EML-3": "π digits (conjectured normal; BBP formula is EML-3)",
            "EML-∞": "True thermal noise, quantum randomness (QRNG), Chaitin Ω, logistic map (long time)",
        },
        "connections": {
            "to_session_57": "Phase transition EML-∞ = same barrier as deterministic chaos onset",
            "to_session_69": "Chaitin Ω = EML-∞ (algorithmic) = EML-∞ (PRNG barrier)",
            "to_session_70": "Quantum QRNG = EML-∞ via Bell theorem = same class as thermal noise",
            "to_complexity_theory": "One-way functions = EML-2 structurally, EML-∞ computationally",
        },
    }


if __name__ == "__main__":
    result = analyze_pseudo_random_eml()
    print(json.dumps(result, indent=2, default=str))
