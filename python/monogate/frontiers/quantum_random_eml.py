"""
Session 70 — Quantum Randomness & EML

Born rule, quantum amplitudes, Wigner function, Bell inequalities, and quantum entropy
classified through the EML depth hierarchy.

Key theorem: Quantum measurement outcomes are EML-∞ as functions of any hidden variable
(Bell's theorem → no EML-finite hidden variable completion of QM).
"""

from __future__ import annotations
import math
import cmath
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
# Born rule and quantum amplitudes
# ---------------------------------------------------------------------------

@dataclass
class QuantumState:
    """
    A finite-dimensional quantum state |ψ⟩ = Σ cₙ|n⟩.

    Born rule: P(n) = |cₙ|² — EML-2 (modulus squared).
    Amplitude cₙ = exp(iθₙ)/√Z — EML-1 per term (Z = normalization).
    """
    name: str
    amplitudes: list[complex]  # cₙ for n=0,1,...
    basis_labels: list[str]

    def probabilities(self) -> list[float]:
        """Born rule: P(n) = |cₙ|²"""
        return [abs(c) ** 2 for c in self.amplitudes]

    def is_normalized(self) -> bool:
        return abs(sum(abs(c) ** 2 for c in self.amplitudes) - 1.0) < 1e-10

    def entropy(self) -> float:
        """Von Neumann entropy for a pure state = 0 (always)."""
        return 0.0

    def eml_depth_of_probability(self) -> int:
        """P(n) = |cₙ|² = cₙ·cₙ* — modulus squared = EML-2."""
        return 2

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "amplitudes": [str(c) for c in self.amplitudes],
            "probabilities": [round(p, 6) for p in self.probabilities()],
            "normalized": self.is_normalized(),
            "born_rule_eml_depth": self.eml_depth_of_probability(),
            "born_rule_reason": "|c|² = exp(2·Re(ln c)) — two EML gates → EML-2",
        }


# Standard quantum states
QUBIT_ZERO = QuantumState("|0⟩", [complex(1, 0), complex(0, 0)], ["|0⟩", "|1⟩"])
QUBIT_ONE = QuantumState("|1⟩", [complex(0, 0), complex(1, 0)], ["|0⟩", "|1⟩"])
QUBIT_PLUS = QuantumState("|+⟩", [1 / math.sqrt(2), 1 / math.sqrt(2)], ["|0⟩", "|1⟩"])
QUBIT_MINUS = QuantumState("|-⟩", [1 / math.sqrt(2), -1 / math.sqrt(2)], ["|0⟩", "|1⟩"])
QUBIT_Y_PLUS = QuantumState("|+i⟩", [1 / math.sqrt(2), complex(0, 1) / math.sqrt(2)], ["|0⟩", "|1⟩"])


@dataclass
class CoherentState:
    """
    Coherent state |α⟩: eigenstate of annihilation operator â.
    Amplitude: cₙ = exp(-|α|²/2) · αⁿ/√(n!) — EML-1 envelope × EML-2 power
    |cₙ|² = exp(-|α|²) · |α|^{2n}/n! — Poisson distribution → EML-1 (Boltzmann-like)
    """
    alpha: complex  # coherent amplitude

    def amplitude(self, n: int) -> complex:
        """⟨n|α⟩ = exp(-|α|²/2) · αⁿ / √(n!)"""
        norm = math.exp(-abs(self.alpha) ** 2 / 2)
        return norm * (self.alpha ** n) / math.sqrt(math.factorial(n))

    def probability(self, n: int) -> float:
        """Poisson: P(n) = exp(-|α|²) · |α|^{2n} / n!"""
        lam = abs(self.alpha) ** 2
        return math.exp(-lam) * (lam ** n) / math.factorial(n)

    def mean_photon_number(self) -> float:
        return abs(self.alpha) ** 2

    def eml_classification(self) -> EMLClass:
        return EMLClass(1, "Poisson distribution P(n)", "exp(-λ)·λⁿ/n! = EML-1 Boltzmann factor at each n")

    def to_dict(self) -> dict:
        return {
            "alpha": str(self.alpha),
            "mean_photon_number": self.mean_photon_number(),
            "probabilities_first_10": [round(self.probability(n), 6) for n in range(10)],
            "eml_class": str(self.eml_classification()),
            "reason": "Coherent state amplitudes are EML-1 (Poisson = Boltzmann in disguise)",
        }


# ---------------------------------------------------------------------------
# Wigner function
# ---------------------------------------------------------------------------

@dataclass
class WignerFunction:
    """
    Wigner quasi-probability distribution W(x,p) for quantum states.
    For harmonic oscillator eigenstate |n⟩:
      W_n(x,p) = ((-1)^n / π) · exp(-2H/ħω) · L_n(4H/ħω)
    where H = (p² + ω²x²)/2, L_n = Laguerre polynomial.

    EML classification:
    - W_0 = (1/π)·exp(-2H): EML-1 (pure Gaussian = Boltzmann factor)
    - W_n for n≥1: EML-3 (Laguerre polynomial × Gaussian)
    - W_n can be NEGATIVE: violates classical probability → quantum signature
    """

    def laguerre(self, n: int, x: float) -> float:
        """L_n(x) via recurrence."""
        if n == 0:
            return 1.0
        if n == 1:
            return 1.0 - x
        L_prev2, L_prev1 = 1.0, 1.0 - x
        for k in range(2, n + 1):
            L_curr = ((2 * k - 1 - x) * L_prev1 - (k - 1) * L_prev2) / k
            L_prev2, L_prev1 = L_prev1, L_curr
        return L_prev1

    def W_n(self, n: int, x: float, p: float, omega: float = 1.0, hbar: float = 1.0) -> float:
        """Wigner function for harmonic oscillator eigenstate |n⟩."""
        H = (p ** 2 + omega ** 2 * x ** 2) / 2.0
        sign = (-1) ** n
        gauss = math.exp(-2 * H / (hbar * omega))
        laguerre_arg = 4 * H / (hbar * omega)
        L = self.laguerre(n, laguerre_arg)
        return (sign / math.pi) * gauss * L

    def sample_grid(self, n: int, x_range: float = 3.0, pts: int = 8) -> dict:
        """Sample W_n on a coarse grid."""
        xs = [x_range * (2 * i / (pts - 1) - 1) for i in range(pts)]
        ps = [x_range * (2 * j / (pts - 1) - 1) for j in range(pts)]
        has_negative = False
        min_val = float("inf")
        max_val = float("-inf")
        for x in xs:
            for p in ps:
                val = self.W_n(n, x, p)
                if val < min_val:
                    min_val = val
                if val > max_val:
                    max_val = val
                if val < -1e-10:
                    has_negative = True
        return {
            "n": n,
            "min_value": round(min_val, 6),
            "max_value": round(max_val, 6),
            "has_negative_values": has_negative,
            "eml_depth": 1 if n == 0 else 3,
            "reason": (
                "W_0 = Gaussian = EML-1" if n == 0
                else f"W_{n} = Laguerre(L_{n}) × Gaussian = EML-3 (polynomial × exp)"
            ),
        }

    def eml_classification(self, n: int) -> EMLClass:
        if n == 0:
            return EMLClass(1, "W_0 = Gaussian", "exp(-2H/ħω) = EML-1 Boltzmann factor")
        return EMLClass(3, f"W_{n} = L_{n}·Gaussian", f"Laguerre polynomial L_{n} = EML-2; times Gaussian = EML-3")


# ---------------------------------------------------------------------------
# Bell inequalities
# ---------------------------------------------------------------------------

@dataclass
class BellInequality:
    """
    CHSH inequality: |E(a,b) - E(a,b') + E(a',b) + E(a',b')| ≤ 2 (classical)
    Quantum: max = 2√2 (Tsirelson bound)

    EML analysis:
    - Classical bound 2 = EML-0 (integer constant)
    - Quantum bound 2√2 = 2·exp(½·ln 2) = EML-2 (involves ln)
    - Violation = quantum outcome distribution is EML-∞ in any hidden variable λ
      (Bell's theorem: no EML-finite λ-distribution reproduces quantum correlations)
    """

    @staticmethod
    def quantum_chsh_max() -> float:
        return 2 * math.sqrt(2)

    @staticmethod
    def classical_chsh_max() -> float:
        return 2.0

    @staticmethod
    def tsirelson_bound_eml() -> EMLClass:
        return EMLClass(2, "Tsirelson bound 2√2", "2·exp(½·ln 2) = EML-2; classical bound 2 = EML-0")

    @staticmethod
    def optimal_correlator(theta: float) -> dict:
        """
        For singlet state and angle θ between measurement axes:
        E(θ) = -cos(θ) — EML-3 (cosine = EML-3)
        """
        E = -math.cos(theta)
        return {
            "theta_deg": round(math.degrees(theta), 2),
            "E_theta": round(E, 6),
            "eml_depth": 3,
            "reason": "-cos(θ) = EML-3 (cosine requires EML-3 depth)",
        }

    @staticmethod
    def chsh_value(angles_deg: list[float]) -> dict:
        """Compute CHSH for angles [a, a', b, b'] in degrees."""
        a, a_prime, b, b_prime = [math.radians(x) for x in angles_deg]
        E_ab = -math.cos(a - b)
        E_ab_prime = -math.cos(a - b_prime)
        E_a_prime_b = -math.cos(a_prime - b)
        E_a_prime_b_prime = -math.cos(a_prime - b_prime)
        chsh = abs(E_ab - E_ab_prime + E_a_prime_b + E_a_prime_b_prime)
        return {
            "angles_deg": angles_deg,
            "E(a,b)": round(E_ab, 6),
            "E(a,b')": round(E_ab_prime, 6),
            "E(a',b)": round(E_a_prime_b, 6),
            "E(a',b')": round(E_a_prime_b_prime, 6),
            "CHSH": round(chsh, 6),
            "classical_bound": 2.0,
            "quantum_bound": round(2 * math.sqrt(2), 6),
            "violates_classical": chsh > 2.0 + 1e-10,
        }

    def to_dict(self) -> dict:
        optimal = self.chsh_value([0, 45, 22.5, 67.5])  # optimal CHSH angles
        return {
            "classical_bound": self.classical_chsh_max(),
            "quantum_bound_tsirelson": round(self.quantum_chsh_max(), 6),
            "tsirelson_eml": str(self.tsirelson_bound_eml()),
            "optimal_measurement": optimal,
            "hidden_variable_theorem": (
                "Bell's theorem: no EML-finite hidden variable λ can reproduce quantum correlations. "
                "The measurement outcome distribution as a function of λ must be EML-∞."
            ),
            "eml_consequence": (
                "Quantum randomness is EML-∞ in any hidden variable: "
                "if outcome O(a,λ) were EML-finite in λ, CHSH would be ≤ 2; "
                "but quantum mechanics achieves 2√2 > 2 → EML-∞ required."
            ),
        }


# ---------------------------------------------------------------------------
# Quantum entropy
# ---------------------------------------------------------------------------

@dataclass
class QuantumEntropy:
    """
    Von Neumann entropy S(ρ) = -Tr(ρ log ρ).
    EML-2 (same depth as Shannon entropy H = -Σp·log p).

    Key special cases:
    - Pure state: S = 0 = EML-0
    - Maximally mixed qubit ρ = I/2: S = ln 2 = EML-2
    - Bell state: S of reduced density matrix = ln 2 = EML-2 (maximum entanglement)
    """

    @staticmethod
    def entropy_diagonal(eigenvalues: list[float]) -> float:
        """S = -Σ λₙ ln λₙ for density matrix eigenvalues."""
        return -sum(lam * math.log(lam) for lam in eigenvalues if lam > 1e-15)

    @staticmethod
    def qubit_entropy(p: float) -> float:
        """Binary von Neumann entropy for qubit with eigenvalues p, 1-p."""
        if p <= 0 or p >= 1:
            return 0.0
        return -(p * math.log(p) + (1 - p) * math.log(1 - p))

    @staticmethod
    def mutual_information_bell() -> dict:
        """
        Bell state |Φ+⟩ = (|00⟩+|11⟩)/√2.
        Reduced density matrix of one qubit: ρ_A = I/2 → S(A) = ln 2.
        Mutual information I(A:B) = S(A) + S(B) - S(AB) = 2·ln 2 - 0 = 2·ln 2.
        """
        S_A = math.log(2)  # ln 2
        S_B = math.log(2)
        S_AB = 0.0  # pure state
        I_AB = S_A + S_B - S_AB
        return {
            "state": "|Φ+⟩ = (|00⟩+|11⟩)/√2",
            "S_A": round(S_A, 6),
            "S_B": round(S_B, 6),
            "S_AB": S_AB,
            "I_AB": round(I_AB, 6),
            "eml_depth_entropy": 2,
            "reason": "S = -Σ p·ln p = EML-2 (x·ln x is EML-2)",
        }

    @staticmethod
    def relative_entropy_kl(p_eigs: list[float], q_eigs: list[float]) -> dict:
        """Quantum relative entropy D(ρ||σ) = Tr(ρ(ln ρ - ln σ)) for diagonal states."""
        assert len(p_eigs) == len(q_eigs)
        D = sum(
            p * (math.log(p) - math.log(q))
            for p, q in zip(p_eigs, q_eigs)
            if p > 1e-15 and q > 1e-15
        )
        return {
            "p_eigenvalues": p_eigs,
            "q_eigenvalues": q_eigs,
            "D_KL": round(D, 6),
            "eml_depth": 2,
            "reason": "D(ρ||σ) = Σ p·(ln p - ln q) = EML-2",
        }


# ---------------------------------------------------------------------------
# EML Taxonomy for Quantum Randomness
# ---------------------------------------------------------------------------

QUANTUM_RANDOM_EML_TAXONOMY: dict[str, dict] = {
    "born_rule_probability": {
        "eml_depth": 2,
        "description": "P(n) = |cₙ|² — measurement outcome probability",
        "reason": "|c|² = exp(2 Re(ln c)); modulus squared = EML-2",
        "examples": ["P(↑) = cos²(θ/2)", "P(n|α) = Poisson(n;|α|²)"],
    },
    "quantum_amplitude_eml1": {
        "eml_depth": 1,
        "description": "Quantum amplitude cₙ = exp(iθₙ)/√Z per basis state",
        "reason": "Single exp gate; phase factor = EML-1 atom",
        "examples": ["exp(iωt)", "exp(ipx/ħ)", "coherent state amplitude"],
    },
    "wigner_vacuum": {
        "eml_depth": 1,
        "description": "Wigner function W_0 = Gaussian = EML-1",
        "reason": "exp(-2H/ħω) — Boltzmann factor at each phase space point",
        "examples": ["W_0(x,p) = (1/π)exp(-x²-p²)"],
    },
    "wigner_excited_n": {
        "eml_depth": 3,
        "description": "Wigner W_n for excited states: Laguerre × Gaussian",
        "reason": "L_n(x) = polynomial in x → EML-2; times exp → EML-3",
        "examples": ["W_1(x,p) = (1/π)(4(x²+p²)-2)exp(-x²-p²)"],
    },
    "tsirelson_bound": {
        "eml_depth": 2,
        "description": "Quantum CHSH bound 2√2 = 2·exp(½·ln 2)",
        "reason": "√2 = exp(½ ln 2) = EML-2; classical bound 2 = EML-0",
        "examples": ["CHSH ≤ 2 classical, ≤ 2√2 quantum"],
    },
    "bell_correlator": {
        "eml_depth": 3,
        "description": "E(θ) = -cos(θ) for singlet state",
        "reason": "cos(θ) = EML-3",
        "examples": ["E(a,b) = -cos(a-b) for singlet"],
    },
    "quantum_entropy_vn": {
        "eml_depth": 2,
        "description": "Von Neumann entropy S(ρ) = -Tr(ρ ln ρ)",
        "reason": "x·ln x = EML-2; same as Shannon entropy",
        "examples": ["S(I/2) = ln 2", "S(|ψ⟩⟨ψ|) = 0"],
    },
    "quantum_mutual_info": {
        "eml_depth": 2,
        "description": "I(A:B) = S(A) + S(B) - S(AB)",
        "reason": "Linear combination of EML-2 entropies = EML-2",
        "examples": ["I(A:B) = 2 ln 2 for Bell state"],
    },
    "quantum_outcome_hidden_variable": {
        "eml_depth": EML_INF,
        "description": "Measurement outcome O(a,λ) as function of hidden variable λ",
        "reason": "Bell's theorem: no EML-finite λ-function reproduces QM correlations",
        "examples": ["Any λ-model for singlet correlations must be EML-∞ in λ"],
    },
    "coherent_state_photon_dist": {
        "eml_depth": 1,
        "description": "Poisson distribution P(n|α) = exp(-|α|²)|α|^{2n}/n!",
        "reason": "Poisson = Boltzmann factor = EML-1 (same class as stat mech)",
        "examples": ["Laser photon statistics"],
    },
}


# ---------------------------------------------------------------------------
# Main analysis
# ---------------------------------------------------------------------------

def analyze_quantum_random_eml() -> dict:
    """Run full Session 70 analysis."""

    # 1. Quantum states
    states = [QUBIT_ZERO, QUBIT_PLUS, QUBIT_MINUS, QUBIT_Y_PLUS]
    states_report = [s.to_dict() for s in states]

    # 2. Coherent state
    cs = CoherentState(alpha=complex(1.5, 0))
    coherent_report = cs.to_dict()

    # 3. Wigner function
    wf = WignerFunction()
    wigner_report = [wf.sample_grid(n) for n in range(4)]

    # 4. Bell inequalities
    bell = BellInequality()
    bell_report = bell.to_dict()

    # Also compute CHSH for several angle choices
    angle_choices = [
        [0, 45, 22.5, 67.5],   # optimal
        [0, 90, 45, 135],       # less optimal
        [0, 0, 0, 0],           # trivial (CHSH=0)
    ]
    chsh_values = [bell.chsh_value(angles) for angles in angle_choices]

    # 5. Quantum entropy
    qe = QuantumEntropy()
    entropy_report = {
        "bell_state_mutual_info": qe.mutual_information_bell(),
        "qubit_entropy_sweep": [
            {"p": round(p, 2), "S": round(qe.qubit_entropy(p), 6)}
            for p in [0.0, 0.1, 0.25, 0.5, 0.75, 0.9, 1.0]
        ],
        "kl_divergence_example": qe.relative_entropy_kl([0.9, 0.1], [0.5, 0.5]),
    }

    # 6. Wigner negativity as EML-∞ indicator
    wigner_negativity = {
        "W_0_has_negative": wigner_report[0]["has_negative_values"],
        "W_1_has_negative": wigner_report[1]["has_negative_values"],
        "W_2_has_negative": wigner_report[2]["has_negative_values"],
        "W_3_has_negative": wigner_report[3]["has_negative_values"],
        "comment": (
            "Wigner negativity is a quantum signature. Classically W ≥ 0 (EML-1 Gaussian). "
            "Quantum excited states W_n < 0 → breaks classical probability interpretation. "
            "But W_n itself is EML-3 (not EML-∞): the quantum structure is expressible in EML-3."
        ),
    }

    return {
        "session": 70,
        "title": "Quantum Randomness & EML",
        "key_theorem": {
            "theorem": "Quantum Bell-EML Theorem",
            "statement": (
                "Quantum measurement outcomes are EML-∞ as functions of any hidden variable λ. "
                "No EML-finite function O(a,λ) exists that reproduces all quantum correlations."
            ),
            "proof_sketch": (
                "Assume O(a,λ) is EML-k for some finite k. "
                "Then the CHSH expression is a linear combination of EML-k functions integrated "
                "against a probability distribution ρ(λ) — the result is EML-k, bounded by |·| ≤ 2. "
                "But quantum mechanics achieves 2√2 > 2. Contradiction. "
                "Therefore O(a,λ) must be EML-∞ for at least some λ."
            ),
            "tsirelson_bound": {
                "value": round(2 * math.sqrt(2), 6),
                "eml_class": "EML-2 (2·exp(½·ln 2))",
            },
        },
        "quantum_states": states_report,
        "coherent_state": coherent_report,
        "wigner_function": wigner_report,
        "wigner_negativity": wigner_negativity,
        "bell_inequality": bell_report,
        "chsh_examples": chsh_values,
        "quantum_entropy": entropy_report,
        "taxonomy": QUANTUM_RANDOM_EML_TAXONOMY,
        "eml_depth_summary": {
            "EML-0": "Topological quantum numbers, Chern numbers (TQFT partition functions)",
            "EML-1": "Quantum amplitudes exp(iθ), Poisson photon statistics, vacuum Wigner function",
            "EML-2": "Born rule probabilities |c|², quantum entropy, Tsirelson bound 2√2",
            "EML-3": "Wigner function W_n (Laguerre×Gaussian), Bell correlator cos(θ), harmonic oscillator eigenstates",
            "EML-∞": "Hidden variable functions violating Bell, quantum measurement outcomes in λ-space",
        },
        "connections": {
            "to_session_57": "Coherent state photon distribution = Boltzmann/Poisson = EML-1 (stat mech connection)",
            "to_session_58": "TQFT partition function = EML-0 (Chern-Simons) — topology connection",
            "to_session_61": "Path integral amplitude = EML-1 per history (QFT connection)",
            "to_session_69": "Quantum randomness = EML-∞ like algorithmic randomness; both transcend EML-finite",
        },
    }


if __name__ == "__main__":
    result = analyze_quantum_random_eml()
    print(json.dumps(result, indent=2, default=str))
