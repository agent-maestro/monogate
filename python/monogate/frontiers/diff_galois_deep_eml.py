"""
Session 73 — Differential Galois Theory Deep Extensions

Fuchsian ODEs, Gauss hypergeometric equation ₂F₁(a,b;c;z), Stokes phenomena,
and the EML depth classification of the hypergeometric parameter space.

Key theorem: The Stokes phenomenon is the complex-analytic manifestation of the
EML-∞ barrier — Stokes multipliers encode the monodromy of the EML tree over ℂ.
"""

from __future__ import annotations
import math
import json
from dataclasses import dataclass, field
from typing import Optional


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
# Gauss hypergeometric function ₂F₁(a,b;c;z)
# ---------------------------------------------------------------------------

@dataclass
class GaussHypergeometric:
    """
    ₂F₁(a,b;c;z) = Σ_{n=0}^∞ (a)_n(b)_n / ((c)_n · n!) · z^n

    where (x)_n = x(x+1)···(x+n-1) is the Pochhammer symbol.

    Satisfies the hypergeometric ODE:
    z(1-z)y'' + [c-(a+b+1)z]y' - ab·y = 0

    EML classification depends on parameters:
    - a,b,c ∈ ℤ: algebraic solution → EML-2
    - a-c or b-c ∈ ℤ (integer difference): logarithmic solution → EML-2
    - General a,b,c: transcendental, monodromy group = SL(2) → EML-3 or EML-∞
    """
    a: float
    b: float
    c: float

    def pochhammer(self, x: float, n: int) -> float:
        """Rising factorial (x)_n."""
        if n == 0:
            return 1.0
        result = 1.0
        for k in range(n):
            result *= (x + k)
        return result

    def evaluate(self, z: float, n_terms: int = 50) -> Optional[float]:
        """Evaluate ₂F₁(a,b;c;z) via power series. Valid for |z| < 1."""
        if abs(z) >= 1.0:
            return None  # outside radius of convergence
        total = 0.0
        factorial = 1
        for n in range(n_terms):
            if n > 0:
                factorial *= n
            num = self.pochhammer(self.a, n) * self.pochhammer(self.b, n)
            den = self.pochhammer(self.c, n) * factorial
            if abs(den) < 1e-15:
                break
            term = num / den * (z ** n)
            total += term
            if abs(term) < 1e-12 * abs(total):
                break
        return total

    def classify_eml(self) -> EMLClass:
        """Classify EML depth based on parameter values."""
        a, b, c = self.a, self.b, self.c
        # Check if a or b is a non-positive integer → finite series → polynomial → EML-2
        if (a <= 0 and a == int(a)) or (b <= 0 and b == int(b)):
            return EMLClass(2, f"₂F₁({a},{b};{c};z) — polynomial", "Terminates: finite sum = polynomial = EML-2")
        # Check integer differences → logarithmic case → EML-2
        if (a - c) == int(a - c) or (b - c) == int(b - c) or (a - b) == int(a - b):
            return EMLClass(2, f"₂F₁({a},{b};{c};z) — logarithmic", "Integer difference → log term → EML-2 (ln gate)")
        # Check if a,b,c are rational → algebraic monodromy possible → EML-2 or EML-3
        from fractions import Fraction
        try:
            fa = Fraction(a).limit_denominator(100)
            fb = Fraction(b).limit_denominator(100)
            fc = Fraction(c).limit_denominator(100)
            if abs(float(fa) - a) < 1e-10 and abs(float(fb) - b) < 1e-10 and abs(float(fc) - c) < 1e-10:
                # Schwarz triangle: if 1-c, c-a-b, a-b all rational → algebraic → EML-2
                lam = abs(1 - c)
                mu = abs(c - a - b)
                nu = abs(a - b)
                # Schwarz triangles: (0,0,0), (1/2,1/3,1/6), (1/2,1/4,1/4), (1/3,1/3,1/3), (1/2,1/3,1/3) → algebraic
                schwarz = [(0, 0, 0), (0.5, 1/3, 1/6), (0.5, 0.25, 0.25), (1/3, 1/3, 1/3)]
                for s in schwarz:
                    if all(abs(x - y) < 0.01 for x, y in [(lam, s[0]), (mu, s[1]), (nu, s[2])]):
                        return EMLClass(2, f"₂F₁ — Schwarz triangle {s}", "Algebraic solution → EML-2")
                return EMLClass(3, f"₂F₁({a},{b};{c};z) — transcendental", "Rational params, non-Schwarz → EML-3 (Euler integral)")
        except Exception:
            pass
        return EMLClass(EML_INF, f"₂F₁({a},{b};{c};z) — general", "General params → SL(2) monodromy → EML-∞")

    def monodromy_description(self) -> str:
        """Describe the monodromy group of the hypergeometric equation."""
        a, b, c = self.a, self.b, self.c
        eml = self.classify_eml()
        if eml.depth == 2:
            return "Finite monodromy group (algebraic/polynomial) → EML-2"
        if eml.depth == 3:
            return "Infinite but solvable monodromy (Euler integral representation) → EML-3"
        return "SL(2,ℂ) monodromy — infinite non-solvable → EML-∞"

    def euler_integral(self) -> str:
        """Euler integral representation (valid for Re(c) > Re(b) > 0)."""
        return (
            f"₂F₁({self.a},{self.b};{self.c};z) = "
            f"[B({self.b},{self.c}-{self.b})]^{{-1}} "
            f"∫_0^1 t^{{{self.b}-1}}(1-t)^{{{self.c}-{self.b}-1}}(1-zt)^{{-{self.a}}} dt"
        )

    def to_dict(self) -> dict:
        eml = self.classify_eml()
        vals = {str(round(z, 1)): self.evaluate(z) for z in [0.0, 0.25, 0.5, 0.75]}
        return {
            "a": self.a, "b": self.b, "c": self.c,
            "values_at": {k: (round(v, 6) if v is not None else None) for k, v in vals.items()},
            "eml_class": str(eml),
            "monodromy": self.monodromy_description(),
            "euler_integral": self.euler_integral(),
        }


# Canonical examples
HYPERGEOMETRIC_EXAMPLES = [
    GaussHypergeometric(-1, 1, 1),     # ₂F₁(-1,1;1;z) = 1-z (polynomial, EML-2)
    GaussHypergeometric(-2, 1, 1),     # ₂F₁(-2,1;1;z) = 1-2z+z² (polynomial, EML-2)
    GaussHypergeometric(0.5, 0.5, 1.5),  # ₂F₁(1/2,1/2;3/2;z) = arcsin(√z)/√z → EML-3
    GaussHypergeometric(1, 1, 2),      # ₂F₁(1,1;2;z) = -ln(1-z)/z → EML-2
    GaussHypergeometric(0.5, -0.5, 1),  # ₂F₁(1/2,-1/2;1;z) — Legendre elliptic type
    GaussHypergeometric(1/3, 2/3, 1),  # General rational → classify
]


# ---------------------------------------------------------------------------
# Fuchsian ODEs
# ---------------------------------------------------------------------------

@dataclass
class FuchsianODE:
    """
    A Fuchsian ODE has only regular singular points. Its solutions near
    each singularity are given by the Frobenius method.

    EML classification of Frobenius solutions:
    - Indicial roots differ by non-integer → two linearly independent power series → EML-2
    - Indicial roots differ by integer → one solution has log term → EML-2
    - Indicial roots equal → log solution guaranteed → EML-2
    - Solutions can be transcendental (like Bessel at general ν) → EML-3 or EML-∞
    """
    name: str
    equation: str
    singular_points: list[str]
    indicial_roots: list[str]
    eml_depth: float
    eml_reason: str
    solutions: list[str]

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "equation": self.equation,
            "singular_points": self.singular_points,
            "indicial_roots": self.indicial_roots,
            "eml_depth": self.eml_depth if self.eml_depth != EML_INF else "∞",
            "eml_reason": self.eml_reason,
            "solutions": self.solutions,
        }


FUCHSIAN_ODES = [
    FuchsianODE(
        "Euler-Cauchy equation",
        "x²y'' + αxy' + βy = 0",
        ["0", "∞"],
        ["r₁, r₂ roots of r(r-1)+αr+β=0"],
        2,
        "Solutions: x^{r₁}, x^{r₂} = exp(r·ln x) = EML-2",
        ["y = x^{r₁} = exp(r₁·ln x)", "y = x^{r₂} if r₁-r₂ ∉ ℤ, else x^{r₁}·ln(x)"],
    ),
    FuchsianODE(
        "Hypergeometric equation",
        "z(1-z)y'' + [c-(a+b+1)z]y' - ab·y = 0",
        ["0", "1", "∞"],
        ["0", "1-c"],
        3,
        "₂F₁(a,b;c;z) — Euler integral representation → EML-3 for generic params",
        ["₂F₁(a,b;c;z)", "z^{1-c}·₂F₁(a-c+1,b-c+1;2-c;z)"],
    ),
    FuchsianODE(
        "Legendre equation",
        "(1-x²)y'' - 2xy' + n(n+1)y = 0",
        ["-1", "1", "∞"],
        ["0", "0"],
        2,
        "P_n(x) = Legendre polynomial (integer n) = polynomial → EML-2; Q_n has log → EML-2",
        ["P_n(x) (polynomial, EML-2)", "Q_n(x) = P_n(x)·½·ln((1+x)/(1-x)) + poly → EML-2"],
    ),
    FuchsianODE(
        "Bessel equation (half-integer ν)",
        "x²y'' + xy' + (x²-ν²)y = 0, ν = n+½",
        ["0", "∞"],
        ["±ν"],
        3,
        "j_n(x) = spherical Bessel = sin/cos × polynomial / x^{n+1} → EML-3",
        ["j_n(x) = (-x)^n(1/x d/dx)^n(sin x/x) — EML-3", "y_n(x) similarly EML-3"],
    ),
    FuchsianODE(
        "Bessel equation (general ν)",
        "x²y'' + xy' + (x²-ν²)y = 0, ν ∉ ℤ+½",
        ["0", "∞"],
        ["±ν"],
        EML_INF,
        "J_ν(x) = Σ(-1)^n x^{2n+ν}/(n!Γ(n+ν+1)) — no closed EML-finite form for general ν",
        ["J_ν(x)", "Y_ν(x) — both EML-∞ for non-half-integer ν"],
    ),
    FuchsianODE(
        "Lamé equation",
        "y'' + (n(n+1)·k²·sn²(x,k) + h)y = 0",
        ["e₁", "e₂", "e₃", "∞"],
        ["depends on h,n,k"],
        EML_INF,
        "Solutions are Lamé functions — no general EML-finite form; EML-∞ for generic parameters",
        ["Ec_n^m(x,k)", "Es_n^m(x,k) — EML-∞ for non-integer/non-special params"],
    ),
]


# ---------------------------------------------------------------------------
# Stokes phenomena
# ---------------------------------------------------------------------------

@dataclass
class StokesPhenomenon:
    """
    For ODEs with irregular singular points (e.g., Airy, hypergeometric at ∞),
    solutions have different asymptotic forms in different sectors of the complex plane.

    Across a Stokes line, a subdominant solution becomes dominant → Stokes multiplier.

    EML interpretation:
    - In each sector: solution is EML-finite (e.g., EML-3 for Airy)
    - Stokes multiplier S: a complex constant (EML-0)
    - But the sector-change ITSELF is EML-∞: no single EML-finite expression is valid globally
    - The Stokes phenomenon is the complex-analytic EML-∞ barrier:
      solutions are EML-finite sector by sector, EML-∞ globally

    Airy equation y'' = xy:
    - Stokes lines: arg(x) = π/3, π, 5π/3
    - Airy Ai(x): decays as x→+∞, oscillates as x→-∞
    - Ai(x) ≈ exp(-2x^{3/2}/3)/(2√π·x^{1/4}) for x→+∞ → EML-1 (pure exponential decay)
    - Ai(x) ≈ sin(2|x|^{3/2}/3 + π/4)/√π|x|^{1/4} for x→-∞ → EML-3 (oscillatory)
    """

    @staticmethod
    def airy_asymptotic_pos(x: float) -> float:
        """Ai(x) large positive x: exp(-2x^{3/2}/3) / (2√π x^{1/4})"""
        if x <= 0:
            return float("nan")
        xi = (2 / 3) * x ** 1.5
        return math.exp(-xi) / (2 * math.sqrt(math.pi) * x ** 0.25)

    @staticmethod
    def airy_asymptotic_neg(x: float) -> float:
        """Ai(x) large negative x: sin(2|x|^{3/2}/3 + π/4) / (√π |x|^{1/4})"""
        if x >= 0:
            return float("nan")
        xi = (2 / 3) * (-x) ** 1.5
        return math.sin(xi + math.pi / 4) / (math.sqrt(math.pi) * (-x) ** 0.25)

    def stokes_report(self) -> dict:
        pos_xs = [1.0, 2.0, 4.0, 8.0]
        neg_xs = [-1.0, -2.0, -4.0, -8.0]
        return {
            "equation": "Airy: y'' = xy",
            "stokes_lines": ["arg(x) = π/3", "arg(x) = π", "arg(x) = 5π/3"],
            "asymptotics_positive_x": [
                {"x": x, "Ai_asymptotic": round(self.airy_asymptotic_pos(x), 8), "eml_depth": 1}
                for x in pos_xs
            ],
            "asymptotics_negative_x": [
                {"x": x, "Ai_asymptotic": round(self.airy_asymptotic_neg(x), 8), "eml_depth": 3}
                for x in neg_xs
            ],
            "eml_interpretation": {
                "positive_x_sector": "EML-1: Ai(x) ≈ exp(-2x^{3/2}/3)/... — pure exponential decay",
                "negative_x_sector": "EML-3: Ai(x) ≈ sin(2|x|^{3/2}/3 + π/4)/... — oscillatory",
                "global": "EML-∞: No single EML-finite expression works for all x ∈ ℂ",
                "stokes_multiplier": "The connection constant between sectors is EML-0 (algebraic number)",
                "theorem": (
                    "Stokes Phenomenon = EML-∞ Barrier over ℂ: "
                    "A solution is EML-finite sector by sector but EML-∞ globally "
                    "because sector-gluing requires the full monodromy group action."
                ),
            },
        }


# ---------------------------------------------------------------------------
# EML depth of hypergeometric parameter space
# ---------------------------------------------------------------------------

@dataclass
class HypergeometricParameterSpace:
    """
    Classify EML depth of ₂F₁(a,b;c;z) as a function of parameters (a,b,c).

    Parameter space ℝ³ partitioned into EML classes:
    - EML-2 region: {a or b ∈ ℤ≤0} ∪ {a-c, b-c, or a-b ∈ ℤ} ∪ {Schwarz triangles}
    - EML-3 region: rational (a,b,c) with non-Schwarz exponents
    - EML-∞ region: generic (a,b,c) — dense, full measure
    """

    @staticmethod
    def classify_point(a: float, b: float, c: float) -> EMLClass:
        return GaussHypergeometric(a, b, c).classify_eml()

    @staticmethod
    def sample_parameter_space(n_per_axis: int = 4) -> dict:
        """Sample a grid of (a,b,c) values and classify."""
        vals = [k / n_per_axis for k in range(-n_per_axis // 2, n_per_axis // 2 + 1) if k != 0]
        eml_counts = {0: 0, 1: 0, 2: 0, 3: 0, "∞": 0}
        sample_points = []
        for a in vals[:4]:
            for b in vals[:4]:
                for c in [0.5, 1.5, 2.0, 3.0]:
                    if abs(c) < 0.1:
                        continue
                    eml = HypergeometricParameterSpace.classify_point(a, b, c)
                    key = "∞" if eml.depth == EML_INF else int(eml.depth)
                    eml_counts[key] = eml_counts.get(key, 0) + 1
                    sample_points.append({
                        "a": a, "b": b, "c": c,
                        "eml_depth": "∞" if eml.depth == EML_INF else int(eml.depth),
                    })
        return {
            "total_sampled": len(sample_points),
            "eml_distribution": eml_counts,
            "sample": sample_points[:20],
            "observation": "EML-∞ (generic) dominates; EML-2 occurs on measure-zero set (integer conditions)",
        }


# ---------------------------------------------------------------------------
# Ramanujan hypergeometric identities
# ---------------------------------------------------------------------------

@dataclass
class RamanujanHypergeometric:
    """
    Ramanujan's 1/π formulas use ₂F₁ at special algebraic points.

    Example (Chudnovsky):
    1/π = Σ (-1)^n (6n)! (13591409 + 545140134n) / ((3n)!(n!)^3 · 640320^{3n+3/2})

    EML depth:
    - Each term: EML-2 (factorial ratios = rational, times algebraic power)
    - The sum: EML-3 (converges to 1/π = arccos(1) / π → EML-3 via arccos)
    - The identity connects EML-3 (π) to EML-2 sums — same as Euler/Ramanujan magic
    """

    @staticmethod
    def chudnovsky_partial(n_terms: int = 5) -> dict:
        """Compute partial sum of Chudnovsky series for 1/π."""
        C = 426880 * math.sqrt(10005)
        total = 0.0
        for n in range(n_terms):
            num = math.factorial(6 * n) * (13591409 + 545140134 * n)
            den = math.factorial(3 * n) * math.factorial(n) ** 3 * (-262537412640768000) ** n
            if abs(den) < 1e-300:
                break
            total += num / den
        if abs(total) > 1e-300:
            approx_pi = C / total
        else:
            approx_pi = float("nan")
        return {
            "formula": "Chudnovsky: 1/π = Σ (-1)^n (6n)!(13591409+545140134n) / ((3n)!(n!)^3·640320^{3n+3/2})",
            "n_terms": n_terms,
            "approximated_pi": round(approx_pi, 10) if not math.isnan(approx_pi) else "nan",
            "true_pi": round(math.pi, 10),
            "eml_depth_series_terms": 2,
            "eml_depth_limit": 3,
            "insight": "Each term is EML-2 (rational × algebraic); sum converges to EML-3 (π). EML depth can jump at limits.",
        }

    @staticmethod
    def ramanujan_2f1_identity() -> dict:
        """₂F₁(1/2,1/2;1;z) = (2/π)K(√z) — elliptic integral."""
        z = 0.5
        hg = GaussHypergeometric(0.5, 0.5, 1.0)
        val_hg = hg.evaluate(z, n_terms=100)
        # K(1/√2) = Γ(1/4)²/(4√π) ≈ 1.8541
        K_val = math.gamma(0.25) ** 2 / (4 * math.sqrt(math.pi))
        # (2/π)·K ≈ ?
        val_elliptic = (2 / math.pi) * K_val
        return {
            "identity": "₂F₁(1/2,1/2;1;z) = (2/π)·K(√z) [complete elliptic integral of first kind]",
            "z": z,
            "2F1_value": round(val_hg, 6) if val_hg else None,
            "elliptic_K_value": round(val_elliptic, 6),
            "eml_2F1": "EML-3 (generic rational params, transcendental)",
            "eml_K": "EML-3 (elliptic integral = definite integral of algebraic function)",
        }


# ---------------------------------------------------------------------------
# Main analysis
# ---------------------------------------------------------------------------

def analyze_diff_galois_deep_eml() -> dict:
    """Run full Session 73 analysis."""

    # 1. Hypergeometric examples
    hg_report = [h.to_dict() for h in HYPERGEOMETRIC_EXAMPLES]

    # 2. Fuchsian ODEs
    fuchsian_report = [f.to_dict() for f in FUCHSIAN_ODES]

    # 3. Stokes phenomenon
    stokes = StokesPhenomenon()
    stokes_report = stokes.stokes_report()

    # 4. Parameter space sampling
    param_space = HypergeometricParameterSpace.sample_parameter_space(n_per_axis=4)

    # 5. Ramanujan identities
    ramanujan = RamanujanHypergeometric()
    ramanujan_report = {
        "chudnovsky": ramanujan.chudnovsky_partial(3),
        "elliptic_K_identity": ramanujan.ramanujan_2f1_identity(),
    }

    # 6. EML-depth classification of hypergeometric parameter space
    eml_parameter_map = {
        "EML-2_conditions": [
            "a or b ∈ {0,-1,-2,...} → polynomial (finite series)",
            "a-c ∈ ℤ or b-c ∈ ℤ → logarithmic case → ln gate → EML-2",
            "a-b ∈ ℤ → Kummer solution → EML-2",
            "Schwarz triangles (1/p,1/q,1/r) with 1/p+1/q+1/r≥1 → algebraic → EML-2",
        ],
        "EML-3_conditions": [
            "Rational (a,b,c) not satisfying EML-2 conditions → Euler integral → EML-3",
            "Examples: ₂F₁(1/2,1/2;3/2;z)=arcsin(√z)/√z, ₂F₁(1/2,-1/2;1;z)=E(√z) [elliptic E]",
        ],
        "EML_inf_conditions": [
            "Generic (a,b,c) with irrational or transcendental parameters",
            "Monodromy group = Zariski-dense in SL(2,ℂ) → no EML-finite global expression",
            "Full measure in parameter space",
        ],
    }

    return {
        "session": 73,
        "title": "Differential Galois Theory Deep Extensions",
        "key_theorem": {
            "theorem": "Stokes Phenomenon = EML-∞ Barrier over ℂ",
            "statement": (
                "For an ODE with irregular singular point, the solution is EML-finite "
                "sector by sector but EML-∞ globally. "
                "The Stokes multipliers (connection constants between sectors) are algebraic (EML-0). "
                "But the full multi-valued solution requires the complete monodromy group action, "
                "which cannot be compressed into any EML-finite global expression."
            ),
            "corollary_hypergeometric": (
                "The EML depth of ₂F₁(a,b;c;z) as a function of (a,b,c) is: "
                "EML-2 on a measure-zero parameter set (integer/Schwarz conditions), "
                "EML-3 for rational non-Schwarz parameters, "
                "EML-∞ for generic (full measure) parameters."
            ),
        },
        "hypergeometric_examples": hg_report,
        "fuchsian_odes": fuchsian_report,
        "stokes_phenomenon": stokes_report,
        "hypergeometric_parameter_space": param_space,
        "eml_parameter_map": eml_parameter_map,
        "ramanujan_identities": ramanujan_report,
        "eml_depth_summary": {
            "EML-2": "Algebraic ODEs, polynomial solutions, logarithmic Frobenius, Legendre P_n, Euler-Cauchy",
            "EML-3": "Airy (sector), Bessel half-integer, ₂F₁ with rational params, Euler integral, elliptic K and E",
            "EML-∞": "Airy globally, Bessel general ν, generic ₂F₁, Lamé, Mathieu, Heun — no closed EML-finite form",
        },
        "connections": {
            "to_session_59": "Session 59 Kovacic: Case 1→EML-2, Case 2→EML-3, Case 3→EML-∞. Session 73 extends to Fuchsian/irregular.",
            "to_session_66": "Complex Analysis EML: Stokes phenomenon = EML-∞ over ℂ (monodromy of ln)",
            "to_session_70": "Quantum randomness = EML-∞ in hidden variable; Stokes = EML-∞ in global solution",
            "to_ramanujan": "Ramanujan identities: EML-2 series summing to EML-3 values — depth jumps at limits",
        },
    }


if __name__ == "__main__":
    result = analyze_diff_galois_deep_eml()
    print(json.dumps(result, indent=2, default=str))
