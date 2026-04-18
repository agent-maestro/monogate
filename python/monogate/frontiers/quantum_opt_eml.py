"""
quantum_opt_eml.py — EML Complexity in Quantum Computing & Optimization.

Session 67 findings:
  - Quantum gates: H (EML-2), R_θ (EML-1), CNOT (EML-0)
  - QFT matrix entries = e^{2πijk/n}/√n → EML-1 (roots of unity)
  - Circuit depth d with EML-k gates: overall EML ≤ k·d
  - Grover amplitude sin((2k+1)arcsin(1/√N)) → EML-3 (arcsin composition)
  - VQE: parameterized circuit → EML-2 for smooth optimization
  - Legendre transform: f*(y)=sup_x{xy-f(x)}: for f=x²/2 → f*=y²/2 (EML-2→EML-2, depth-preserving)
  - For f=exp(x): f*(y)=y·log(y)-y → EML-2 (log appears)
  - Mirror descent: entropy mirror -Σ x_i log x_i → EML-2
  - KKT: Lagrangian L=f+Σλ_i g_i: EML depth = max(depth(f), depth(g))
  - Interior point: log-barrier -Σ log(-g_i) → EML-2
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Callable

import numpy as np

__all__ = [
    "QuantumGates",
    "QuantumFourierTransform",
    "GroverSearch",
    "LegendreTransform",
    "ConvexOptimizationEML",
    "QC_OPT_EML_TAXONOMY",
    "analyze_quantum_opt_eml",
]

# ── EML Taxonomy ─────────────────────────────────────────────────────────────

QC_OPT_EML_TAXONOMY: dict[str, dict] = {
    "hadamard_gate": {
        "formula": "H = (1/√2)[[1,1],[1,-1]]",
        "eml_depth": 2,
        "reason": "Entry 1/√2 = 2^{-1/2}: algebraic (EML-2 as real number, but rational power).",
    },
    "phase_gate": {
        "formula": "R_θ = diag(1, e^{iθ})",
        "eml_depth": 1,
        "reason": "Entry e^{iθ}: EML-1 atom.",
    },
    "cnot_gate": {
        "formula": "CNOT = [[1,0,0,0],[0,1,0,0],[0,0,0,1],[0,0,1,0]]",
        "eml_depth": 0,
        "reason": "Permutation matrix (0s and 1s only): EML-0.",
    },
    "qft_matrix": {
        "formula": "QFT_n: entry (j,k) = e^{2πijk/n}/√n",
        "eml_depth": 1,
        "reason": "e^{2πi·rational}: roots of unity = EML-1 atoms.",
    },
    "grover_amplitude": {
        "formula": "sin((2k+1)·arcsin(1/√N))",
        "eml_depth": 3,
        "reason": "arcsin = inverse of EML-3 sin → EML-3; composition → EML-3.",
    },
    "legendre_transform_quadratic": {
        "formula": "f(x)=x²/2: f*(y)=y²/2",
        "eml_depth": 2,
        "reason": "EML-2 → EML-2: Legendre transform preserves depth for quadratics.",
    },
    "legendre_transform_exp": {
        "formula": "f(x)=exp(x): f*(y)=y·log(y)-y",
        "eml_depth": 2,
        "reason": "y·log(y)-y: contains log → EML-2.",
    },
    "log_barrier": {
        "formula": "-Σ log(-g_i(x))  (interior point method)",
        "eml_depth": 2,
        "reason": "Contains log of constraint: EML-2.",
    },
    "kkt_lagrangian": {
        "formula": "L = f + Σ λ_i g_i",
        "eml_depth": "max(depth(f), depth(g))",
        "reason": "Linear combination: EML depth = max of components.",
    },
    "entropy_mirror": {
        "formula": "-Σ x_i log x_i  (mirror descent potential)",
        "eml_depth": 2,
        "reason": "Same structure as entropy H(x): EML-2.",
    },
}


# ── Quantum Gates ─────────────────────────────────────────────────────────────

@dataclass
class QuantumGates:
    """
    Quantum gates and their EML depths.

    H (Hadamard): 1/√2 matrix entries → EML-2 (algebraic)
    R_θ (Phase): e^{iθ} entry → EML-1 (exponential)
    CNOT: permutation → EML-0 (integer matrix)
    T gate: e^{iπ/4} = (1+i)/√2 → EML-2 (algebraic)
    """

    def hadamard(self) -> np.ndarray:
        """H = (1/√2)[[1,1],[1,-1]]. EML-2."""
        return np.array([[1, 1], [1, -1]], dtype=complex) / math.sqrt(2)

    def phase_gate(self, theta: float) -> np.ndarray:
        """R_θ = diag(1, e^{iθ}). EML-1."""
        return np.array([[1, 0], [0, complex(math.cos(theta), math.sin(theta))]])

    def cnot(self) -> np.ndarray:
        """CNOT gate: integer permutation matrix. EML-0."""
        return np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 0, 1],
            [0, 0, 1, 0],
        ], dtype=complex)

    def t_gate(self) -> np.ndarray:
        """T gate = diag(1, e^{iπ/4}). EML-2 (e^{iπ/4} = (1+i)/√2, algebraic)."""
        return self.phase_gate(math.pi / 4)

    def rx_gate(self, theta: float) -> np.ndarray:
        """Rx(θ) = exp(-iθX/2) = [[cos,−i·sin],[−i·sin,cos]]. EML-3."""
        c = math.cos(theta / 2)
        s = math.sin(theta / 2)
        return np.array([[c, complex(0, -s)], [complex(0, -s), c]])

    def circuit_eml_depth(self, gate_depths: list[int], circuit_depth: int) -> int:
        """
        EML depth of circuit = max(gate depths) × circuit depth (conservative bound).
        """
        max_gate = max(gate_depths) if gate_depths else 0
        return max_gate * circuit_depth

    def eml_depth_hadamard(self) -> int:
        return 2

    def eml_depth_phase(self) -> int:
        return 1

    def eml_depth_cnot(self) -> int:
        return 0


# ── Quantum Fourier Transform ─────────────────────────────────────────────────

@dataclass
class QuantumFourierTransform:
    """
    QFT_n: n×n unitary matrix with entries ω^{jk}/√n where ω = e^{2πi/n}.

    Entries = e^{2πijk/n}/√n: roots of unity × 1/√n.
    Roots of unity e^{2πi·rational}: EML-1 atoms.
    1/√n: algebraic → EML-2 or EML-0 (for n=power of 2: 1/√(2^k) = 2^{-k/2}).
    Overall: EML-1 (dominant structure from roots of unity).
    """

    def matrix(self, n: int) -> np.ndarray:
        """QFT_n matrix with entries e^{2πijk/n}/√n."""
        omega = complex(math.cos(2 * math.pi / n), math.sin(2 * math.pi / n))
        mat = np.zeros((n, n), dtype=complex)
        for j in range(n):
            for k in range(n):
                mat[j, k] = omega ** (j * k) / math.sqrt(n)
        return mat

    def verify_unitary(self, n: int) -> float:
        """Max |QFT†·QFT - I|."""
        q = self.matrix(n)
        return float(np.max(np.abs(q @ q.conj().T - np.eye(n))))

    def verify_dft_equivalence(self, n: int, x: np.ndarray) -> float:
        """QFT should match classical DFT (up to normalization and conjugation)."""
        q = self.matrix(n)
        x_qft = q @ x
        x_fft = np.fft.fft(x) / math.sqrt(n)
        return float(np.max(np.abs(x_qft - x_fft)))

    def eml_depth_entry(self) -> int:
        return 1  # roots of unity = EML-1


# ── Grover's Algorithm ────────────────────────────────────────────────────────

@dataclass
class GroverSearch:
    """
    Grover's search algorithm.

    After k iterations starting from equal superposition (N items, 1 target):
    Amplitude of target: sin((2k+1)·arcsin(1/√N))
    Probability: sin²((2k+1)·arcsin(1/√N))

    EML-3: arcsin = inverse of sin (asin), composition → EML-3.
    Optimal k ≈ π√N/4 iterations gives success prob ≈ 1.
    """

    def amplitude(self, N: int, k: int) -> float:
        """sin((2k+1)·arcsin(1/√N)). EML-3."""
        if N <= 0:
            return 0.0
        alpha = math.asin(1.0 / math.sqrt(N))
        return math.sin((2 * k + 1) * alpha)

    def success_probability(self, N: int, k: int) -> float:
        """P(success) = sin²((2k+1)·arcsin(1/√N)). EML-3."""
        return self.amplitude(N, k) ** 2

    def optimal_iterations(self, N: int) -> int:
        """k_opt ≈ floor(π√N/4)."""
        return int(math.pi * math.sqrt(N) / 4.0)

    def success_prob_at_optimal(self, N: int) -> float:
        """P(success) at optimal k."""
        k_opt = self.optimal_iterations(N)
        return self.success_probability(N, k_opt)

    def quantum_speedup_classical_ratio(self, N: int) -> float:
        """Quantum: O(√N) queries. Classical: O(N). Ratio: N/√N = √N."""
        return math.sqrt(N)

    def eml_depth(self) -> int:
        return 3  # arcsin composition


# ── Legendre Transform ────────────────────────────────────────────────────────

@dataclass
class LegendreTransform:
    """
    Legendre-Fenchel transform: f*(y) = sup_x{x·y - f(x)}.

    Key examples:
    1. f(x) = x²/2: f*(y) = y²/2  → depth-preserving (EML-2 → EML-2)
    2. f(x) = exp(x): f*(y) = y·log(y) - y  (for y>0)  → EML-2 (contains log)
    3. f(x) = x^p/p: f*(y) = y^q/q where 1/p+1/q=1  → EML-0 (power law)
    4. f(x) = |x|: f*(y) = 0 if |y|≤1, ∞ else  → EML-0 (indicator)
    """

    def legendre_quadratic(self, y: float) -> float:
        """f(x)=x²/2: f*(y)=y²/2. EML-2 → EML-2."""
        return y ** 2 / 2.0

    def legendre_exp(self, y: float) -> float:
        """f(x)=exp(x): f*(y)=y·log(y)-y for y>0. EML-2 (contains log)."""
        if y <= 0:
            return float("inf")
        return y * math.log(y) - y

    def legendre_power(self, y: float, p: float) -> float:
        """f(x)=x^p/p (p>1): f*(y)=y^q/q where 1/p+1/q=1. EML-0 (power law)."""
        q = p / (p - 1)
        if y < 0:
            return float("inf")
        return y ** q / q

    def legendre_gaussian(self, y: float, sigma: float = 1.0) -> float:
        """
        f(x) = x²/(2σ²): f*(y) = σ²y²/2.
        Used in Gaussian smoothing: LT of Gaussian is Gaussian → EML-2.
        """
        return sigma ** 2 * y ** 2 / 2.0

    def verify_quadratic(self, y_vals: list[float]) -> list[dict]:
        """Verify f*(y)=y²/2 for f=x²/2 numerically via sup_x{xy-x²/2}."""
        rows = []
        for y in y_vals:
            # f*(y) = sup_x{xy - x²/2} = y²/2 (at x*=y)
            xs = np.linspace(-10, 10, 2000)
            vals = xs * y - xs ** 2 / 2.0
            numerical = float(np.max(vals))
            exact = self.legendre_quadratic(y)
            rows.append({
                "y": y,
                "numerical": numerical,
                "exact": exact,
                "match": abs(numerical - exact) < 0.01,
            })
        return rows

    def eml_depth_quadratic(self) -> int:
        return 2  # y²/2 → EML-2

    def eml_depth_exp(self) -> int:
        return 2  # y·log(y)-y → EML-2 (contains log)


# ── Convex Optimization EML ───────────────────────────────────────────────────

@dataclass
class ConvexOptimizationEML:
    """
    EML analysis of convex optimization concepts.

    Gradient descent: x_{k+1} = x_k - α·∇f(x_k).
    EML depth of iterates: depends on f (differentiation preserves EML).

    Mirror descent: x_{k+1} = argmin{α·⟨g_k,x⟩ + D_ψ(x,x_k)}
    with ψ = -Σ x_i·log(x_i) (entropy mirror) → EML-2.

    Log-barrier: B(x) = -Σ log(-g_i(x)) → EML-2.
    KKT conditions: L = f + Σ λ_i·g_i, EML depth = max(depth(f), depth(g_i)).
    """

    def log_barrier(self, x: float, g: float) -> float:
        """
        Log-barrier contribution: -log(-g(x)) for g(x)<0.
        Returns -log(-g) where g = constraint function value.
        """
        if g >= 0:
            return float("inf")
        return -math.log(-g)

    def entropy_mirror(self, probs: np.ndarray) -> float:
        """ψ(x) = -Σ x_i·log(x_i). EML-2 (entropy)."""
        probs = np.asarray(probs, dtype=float)
        mask = probs > 0
        return float(-np.sum(probs[mask] * np.log(probs[mask])))

    def gradient_descent_path(self, f: Callable[[float], float],
                               df: Callable[[float], float],
                               x0: float, alpha: float = 0.1,
                               n_steps: int = 50) -> list[float]:
        """x_{k+1} = x_k - α·f'(x_k)."""
        x = x0
        path = [x]
        for _ in range(n_steps):
            x -= alpha * df(x)
            path.append(x)
        return path

    def kkt_lagrangian_depth(self, depth_f: int, depth_g: list[int]) -> int:
        """EML depth of Lagrangian L = f + Σ λ_i g_i."""
        return max([depth_f] + depth_g)

    def eml_depth_log_barrier(self) -> int:
        return 2  # log(-g) → EML-2

    def eml_depth_entropy_mirror(self) -> int:
        return 2  # -Σ x·log x → EML-2


# ── Grand Analysis ────────────────────────────────────────────────────────────

def analyze_quantum_opt_eml() -> dict:
    """Run full quantum computing & optimization EML analysis."""
    results: dict = {
        "session": 67,
        "title": "Quantum Computing & Optimization EML",
        "taxonomy": QC_OPT_EML_TAXONOMY,
    }

    gates = QuantumGates()
    qft = QuantumFourierTransform()
    grover = GroverSearch()
    legendre = LegendreTransform()
    optim = ConvexOptimizationEML()

    # Gates
    H = gates.hadamard()
    results["quantum_gates"] = {
        "hadamard_matrix": H.tolist(),
        "hadamard_unitary_err": float(np.max(np.abs(H @ H.conj().T - np.eye(2)))),
        "phase_pi4_entry": gates.phase_gate(math.pi / 4)[1, 1],
        "cnot_is_permutation": bool(np.all(gates.cnot() == gates.cnot().astype(int))),
        "eml_hadamard": gates.eml_depth_hadamard(),
        "eml_phase": gates.eml_depth_phase(),
        "eml_cnot": gates.eml_depth_cnot(),
    }

    # QFT
    n_vals = [4, 8, 16]
    qft_results = {}
    for n in n_vals:
        unitary_err = qft.verify_unitary(n)
        x_test = np.random.default_rng(42).normal(0, 1, n) + 1j * np.random.default_rng(43).normal(0, 1, n)
        dft_err = qft.verify_dft_equivalence(n, x_test)
        qft_results[f"n_{n}"] = {"unitary_err": unitary_err, "dft_match_err": dft_err}
    results["qft"] = {
        "tests": qft_results,
        "eml_depth_entry": qft.eml_depth_entry(),
    }

    # Grover
    N_vals = [4, 16, 100, 1000]
    grover_data = []
    for N in N_vals:
        k_opt = grover.optimal_iterations(N)
        p_success = grover.success_prob_at_optimal(N)
        grover_data.append({
            "N": N,
            "k_opt": k_opt,
            "p_success": p_success,
            "classical_queries": N,
            "quantum_queries": int(math.ceil(math.pi * math.sqrt(N) / 4)),
        })
    results["grover"] = {
        "data": grover_data,
        "N100_k5_amplitude": grover.amplitude(100, 5),
        "eml_depth": grover.eml_depth(),
    }

    # Legendre
    y_vals = [-2.0, -1.0, 0.0, 1.0, 2.0, 3.0]
    results["legendre"] = {
        "quadratic_table": legendre.verify_quadratic(y_vals),
        "exp_fstar": [{"y": y, "f*": legendre.legendre_exp(y)} for y in [0.5, 1.0, 2.0, math.e]],
        "eml_quadratic": legendre.eml_depth_quadratic(),
        "eml_exp": legendre.eml_depth_exp(),
        "depth_preserving_note": "Legendre of x^2/2 = y^2/2: EML-2 → EML-2 (depth preserved!)",
    }

    # Optimization
    def f_quad(x): return x ** 2 / 2
    def df_quad(x): return x
    gd_path = optim.gradient_descent_path(f_quad, df_quad, x0=5.0, alpha=0.1, n_steps=30)
    results["optimization"] = {
        "gd_path": gd_path[:10],
        "gd_converges_to": gd_path[-1],
        "kkt_depth_f2_g2": optim.kkt_lagrangian_depth(2, [2, 2]),
        "kkt_depth_f2_g0": optim.kkt_lagrangian_depth(2, [0]),
        "entropy_mirror_uniform": optim.entropy_mirror(np.array([0.25, 0.25, 0.25, 0.25])),
        "eml_log_barrier": optim.eml_depth_log_barrier(),
        "eml_entropy_mirror": optim.eml_depth_entropy_mirror(),
    }

    results["summary"] = {
        "key_insight": (
            "QFT entries are EML-1 (roots of unity). "
            "Grover amplitude: EML-3 (arcsin composition). "
            "Legendre transform of x²/2 = y²/2: depth-preserving (EML-2→EML-2). "
            "Log-barrier and entropy mirror: EML-2. "
            "The Legendre transform's depth-preservation is a key optimization theorem."
        ),
        "eml_depths": {k: str(v["eml_depth"]) for k, v in QC_OPT_EML_TAXONOMY.items()},
    }

    return results
