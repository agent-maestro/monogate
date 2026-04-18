"""
Session 87 — Representation Theory Higher: Kac-Moody Algebras & Moonshine

Infinite-dimensional Lie algebras: affine Lie algebras, Kac-Moody algebras,
the Monster group, monstrous moonshine, and the EML depth of characters.

Key theorem: The character of a highest-weight representation of an affine Lie algebra
is a modular form of weight 0 — EML-3 (involves exp(2πiτ) composed with Lie algebra data).
The Monster group M has |M| = 2^{46}·3^{20}·5^9·7^6·... which is EML-0 (integer constant).
McKay-Thompson series T_g(τ) = EML-3 (Hauptmoduln = modular functions = EML-3).
"""

from __future__ import annotations
import math, json
from dataclasses import dataclass, field
from typing import Callable


EML_INF = float("inf")
PI = math.pi


@dataclass
class KacMoodyAlgebra:
    """
    Kac-Moody algebra g(A): generalized Cartan matrix A + simple roots αᵢ.

    Types:
    - Finite type (det A > 0): ordinary semisimple Lie algebra (sl_n, so_n, sp_n, G₂, F₄, E₆,E₇,E₈)
    - Affine type (det A = 0): loop algebra ĝ + central extension → characters are modular forms
    - Indefinite type (det A < 0): hyperbolic Kac-Moody (e.g. E₁₀, E₁₁) → EML-∞ complexity

    EML depth of characters χ_λ(q) = Σ mult(μ)·q^{⟨μ,μ⟩/2}:
    - Finite g: χ = polynomial in q^α = EML-3 (finite sum of exp)
    - Affine ĝ: χ = Θ_{λ+ρ}/η^rank (ratio of theta functions) = EML-3 (modular form)
    - Indefinite: character is EML-∞ (no closed modular form formula)
    """

    @staticmethod
    def cartan_matrix_type(A: list[list[int]]) -> dict:
        n = len(A)
        # Compute determinant for 2x2 and 3x3
        if n == 2:
            det = A[0][0] * A[1][1] - A[0][1] * A[1][0]
        elif n == 3:
            det = (A[0][0] * (A[1][1] * A[2][2] - A[1][2] * A[2][1])
                   - A[0][1] * (A[1][0] * A[2][2] - A[1][2] * A[2][0])
                   + A[0][2] * (A[1][0] * A[2][1] - A[1][1] * A[2][0]))
        else:
            det = None
        if det is None:
            algebra_type = "unknown"
        elif det > 0:
            algebra_type = "finite (semisimple)"
        elif det == 0:
            algebra_type = "affine"
        else:
            algebra_type = "indefinite"
        return {"det_A": det, "type": algebra_type}

    @staticmethod
    def known_algebras() -> list[dict]:
        return [
            {
                "name": "sl₂ = A₁",
                "rank": 1,
                "type": "finite",
                "character_formula": "χ_j = (q^{j+1/2} - q^{-j-1/2})/(q^{1/2}-q^{-1/2}): Weyl formula",
                "eml": 3,
                "reason": "Character = ratio of EML-3 theta-like functions = EML-3",
            },
            {
                "name": "ŝl₂ (affine A₁)",
                "rank": 2,
                "type": "affine",
                "character_formula": "χ_k = Θ_{λ,k}/η(τ): theta/eta ratio",
                "eml": 3,
                "reason": "Modular form: Θ_{λ,k}(τ) = Σ_{n}q^{(λ+2kn)²/4k} = EML-3; η(τ) = q^{1/24}∏(1-qⁿ) = EML-3",
            },
            {
                "name": "E₈ (finite)",
                "rank": 8,
                "type": "finite",
                "character_formula": "Weyl character formula: ratio of alternating sums",
                "eml": 3,
                "reason": "E₈ character via Weyl formula = EML-3 (products of q-exponentials)",
            },
            {
                "name": "Ê₈ (affine E₈)",
                "rank": 9,
                "type": "affine",
                "character_formula": "χ = j(τ)^{1/3}: cube root of j-function",
                "eml": 3,
                "reason": "j(τ)^{1/3} is still a modular function = EML-3",
            },
            {
                "name": "E₁₀ (hyperbolic)",
                "rank": 10,
                "type": "indefinite",
                "character_formula": "No closed form known",
                "eml": EML_INF,
                "reason": "Hyperbolic Kac-Moody: no Weyl-type character formula → EML-∞",
            },
        ]

    def to_dict(self) -> dict:
        A_sl2 = [[2, -2], [-2, 2]]
        A_affine_sl2 = [[2, -2], [-2, 2]]  # same structure but det=0 for affine
        return {
            "finite_A1": self.cartan_matrix_type([[2]]),
            "affine_A1": {"det_A": 0, "type": "affine (det=0)"},
            "algebras": self.known_algebras(),
        }


@dataclass
class DedekindEtaFunction:
    """
    Dedekind η(τ) = q^{1/24} ∏_{n=1}^∞ (1-q^n),  q = exp(2πiτ)

    EML depth:
    - q = exp(2πiτ): EML-3 (exp of imaginary = oscillatory)
    - η(τ) = q^{1/24} × infinite product: EML-3
    - η(τ)^{24} = Δ(τ): discriminant modular form, weight 12
    - ln η(τ): EML-3 (logarithm of modular form)

    Partition function p(n): η(τ)^{-1} = Σ p(n)q^n
    - Hardy-Ramanujan formula: p(n) ~ exp(π√(2n/3))/(4n√3): EML-1 asymptotic (single exp)
    """

    def eta_coefficients(self, n_terms: int = 15) -> list[dict]:
        """
        Compute log-η coefficients: ln η = (1/24)·2πiτ + Σ_{n=1}^∞ ln(1-q^n).
        Return partition numbers p(n) from 1/η = Σ p(n) q^{n-1/24}.
        """
        p = [0] * (n_terms + 1)
        p[0] = 1
        for k in range(1, n_terms + 1):
            for m in range(k, n_terms + 1):
                p[m] += p[m - k]
        # Hardy-Ramanujan approximation
        results = []
        for n in range(1, min(n_terms + 1, 12)):
            exact = p[n]
            hr_approx = math.exp(math.pi * math.sqrt(2 * n / 3)) / (4 * n * math.sqrt(3))
            results.append({
                "n": n,
                "p_n_exact": exact,
                "hr_approx": round(hr_approx, 2),
                "relative_error": round(abs(exact - hr_approx) / exact, 4) if exact > 0 else None,
            })
        return results

    def to_dict(self) -> dict:
        return {
            "definition": "η(τ) = q^{1/24} ∏(1-q^n), q = exp(2πiτ)",
            "eml_depth": 3,
            "eml_reason": "q = exp(2πiτ): EML-3; infinite product of EML-3 terms = EML-3",
            "modular_weight": "1/2",
            "partition_numbers": self.eta_coefficients(12),
            "hr_formula": {
                "formula": "p(n) ~ exp(π√(2n/3)) / (4n√3)",
                "eml": 1,
                "reason": "Single exp atom: EML-1 asymptotic",
            },
        }


@dataclass
class MonstrousMoonshine:
    """
    Monstrous Moonshine (Conway-Norton, 1979; Borcherds proof, 1992):

    The Monster group M (largest sporadic simple group) acts on the moonshine module V♮.
    McKay-Thompson series: T_g(τ) = Σ_{n=-1}^∞ Tr(g|V♮_n)·q^n for g ∈ M.

    T_e(τ) = j(τ) - 744 = q^{-1} + 196884q + 21493760q² + ...
    where j(τ) is the elliptic modular function.

    EML structure:
    - |M| = 2^{46}·3^{20}·5^9·7^6·11^2·13^3·17·19·23·29·31·41·47·59·71: EML-0 (integer)
    - j(τ) = q^{-1} + 744 + 196884q + ...: EML-3 (modular function = Hauptmodul for SL₂(ℤ)\ℍ)
    - T_g(τ): EML-3 (Hauptmodul for genus-0 group Γ_g ⊂ SL₂(ℝ))
    - Borcherds proof: uses vertex algebra = EML-3 (products of q-series)
    - Sporadic connection: 196884 = 196883 + 1 (Monster rep dimensions = EML-0 = integers)
    """

    @staticmethod
    def monster_order_factored() -> dict:
        primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 41, 47, 59, 71]
        exponents = [46, 20, 9, 6, 2, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        order = 1
        for p, e in zip(primes, exponents):
            order *= p**e
        return {
            "primes": primes,
            "exponents": exponents,
            "log2_order": round(math.log2(order), 2),
            "eml": 0,
            "reason": "Integer = EML-0",
        }

    @staticmethod
    def j_function_coefficients() -> list[dict]:
        coeffs = [
            (-1, "q^{-1} (pole at cusp)"),
            (0, "constant 744 (choice of normalization: j-744 = McKay-Thompson T_e)"),
            (196884, "2nd Monster irrep: 196883+1"),
            (21493760, "196883 + 21296876 + 299 (Monster reps)"),
            (864299970, "sum of Monster irrep dims"),
        ]
        return [
            {"n": i - 1, "coefficient": c, "note": note, "eml": 3}
            for i, (c, note) in enumerate(coeffs)
        ]

    @staticmethod
    def mckay_observation() -> dict:
        return {
            "McKay_1978": "196884 = 196883 + 1",
            "196883": "Dimension of smallest non-trivial Monster irrep",
            "1": "Trivial Monster rep",
            "j_coefficient": 196884,
            "significance": "j(τ) 'knows about' the Monster group — moonshine connection",
            "eml_Monster_reps": 0,
            "eml_j_function": 3,
            "moonshine": "EML-0 integers (Monster rep dims) appear as coefficients of EML-3 modular function",
        }

    def to_dict(self) -> dict:
        return {
            "Monster_order": self.monster_order_factored(),
            "j_function_coefficients": self.j_function_coefficients(),
            "McKay_observation": self.mckay_observation(),
            "Borcherds_1992": {
                "tool": "Vertex operator algebra (VOA) V♮",
                "key_identity": "Φ(f,g) = ∏_{m>0,n∈ℤ} (1-p^m q^n)^{c(mn)}: infinite product = EML-3",
                "eml": 3,
                "reason": "Infinite product over q-series = EML-3 (modular)",
            },
            "generalized_moonshine": {
                "Mathieu_moonshine": "M₂₄ ↔ K3 surface Hodge numbers: EML-3 (elliptic genus)",
                "Umbral_moonshine": "23 cases of moonshine for Niemeier lattice automorphisms: EML-3",
                "eml": 3,
            },
        }


def analyze_rep_theory_higher_eml() -> dict:
    km = KacMoodyAlgebra()
    eta = DedekindEtaFunction()
    moonshine = MonstrousMoonshine()
    return {
        "session": 87,
        "title": "Representation Theory Higher: Kac-Moody Algebras & Moonshine",
        "key_theorem": {
            "theorem": "EML-3 Universality of Modular Representation Theory",
            "statement": (
                "Characters of affine Lie algebra representations are modular forms: EML-3. "
                "The Monster group |M| is EML-0 (integer). "
                "McKay-Thompson series T_g(τ) are EML-3 (Hauptmoduln = modular functions). "
                "Hardy-Ramanujan p(n) ~ exp(π√(2n/3)) is EML-1 (single exp asymptotic). "
                "Indefinite Kac-Moody (E₁₀, E₁₁) characters are EML-∞: no Weyl-type closed form exists. "
                "Moonshine is the phenomenon where EML-0 integers (Monster rep dims) appear "
                "as Fourier coefficients of EML-3 modular functions."
            ),
        },
        "kac_moody": km.to_dict(),
        "dedekind_eta": eta.to_dict(),
        "monstrous_moonshine": moonshine.to_dict(),
        "eml_depth_summary": {
            "EML-0": "Monster group order |M|; Monster irrep dimensions; linking numbers in moonshine",
            "EML-1": "Hardy-Ramanujan p(n) ~ exp(π√(2n/3)); character growth bounds",
            "EML-2": "Root system geometry; Cartan matrix; Weyl denominator",
            "EML-3": "Affine characters (theta/eta ratio); j(τ); McKay-Thompson T_g; Dedekind η",
            "EML-∞": "Indefinite Kac-Moody characters (E₁₀, E₁₁); no modular formula",
        },
        "connections": {
            "to_session_58": "Session 58: Chern numbers = EML-0. Session 87: Monster order = EML-0 — topological integer",
            "to_session_73": "Session 73: hypergeometric functions = EML-3. Session 87: modular forms = EML-3 — same depth class",
        },
    }


if __name__ == "__main__":
    print(json.dumps(analyze_rep_theory_higher_eml(), indent=2, default=str))
