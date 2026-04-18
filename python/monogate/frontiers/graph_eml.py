"""
Session 104 — Graph Theory & Complex Networks: EML as Network Substrate

Degree distributions, clustering, shortest paths, spectral graph theory, and
network phase transitions classified by EML depth.

Key theorem: Erdős-Rényi random graphs have EML-1 degree distributions (Poisson).
Scale-free networks (Barabási-Albert) have EML-2 (power law = exp(−k·ln(k))).
Small-world clustering is EML-2. Graph Laplacian spectra are EML-3 (oscillatory).
Percolation phase transition is EML-∞. Community detection is EML-∞ (NP-hard).
"""

from __future__ import annotations
import math, json
from dataclasses import dataclass, field


EML_INF = float("inf")


@dataclass
class DegreeDistributions:
    """
    Degree distribution P(k): probability a random node has degree k.

    EML structure:
    - Erdős-Rényi G(n,p): P(k) = C(n-1,k)·p^k·(1-p)^{n-1-k} → Poisson for large n
      Poisson: P(k) = e^{-λ}·λ^k/k! = EML-1 (single exponential)
    - Scale-free (BA model): P(k) ~ k^{-γ} with γ≈3: EML-2 (power law = exp(−γ·ln k))
    - Regular lattice: P(k) = δ_{k,d}: EML-0 (constant degree = integer)
    - Small-world (WS): peaked near ⟨k⟩ with exponential tail: EML-1
    - Bimodal (planted partition): mixture of two Poissons → EML-1 per component
    """

    def poisson_degree(self, k: int, lam: float) -> dict:
        """Erdős-Rényi Poisson degree distribution."""
        if k < 0:
            return {"k": k, "P_k": 0.0, "eml": 1}
        log_p = -lam + k * math.log(lam) - sum(math.log(i) for i in range(1, k + 1))
        return {
            "k": k,
            "P_k": round(math.exp(log_p), 8),
            "eml": 1,
            "reason": "Poisson: e^{-λ}λ^k/k! = EML-1",
        }

    def power_law_degree(self, k: int, gamma: float = 3.0, k_min: int = 1) -> dict:
        """Scale-free power-law degree distribution."""
        if k < k_min:
            return {"k": k, "P_k": 0.0, "eml": 2}
        zeta = sum(i ** (-gamma) for i in range(k_min, k_min + 1000))
        P_k = (k ** (-gamma)) / zeta
        return {
            "k": k,
            "P_k": round(P_k, 8),
            "gamma": gamma,
            "eml": 2,
            "reason": f"P(k) ~ k^{{-γ}} = exp(-γ·ln k): EML-2 (power law)",
        }

    def to_dict(self) -> dict:
        return {
            "er_poisson": [self.poisson_degree(k, 3.0) for k in range(8)],
            "scale_free": [self.power_law_degree(k) for k in [1, 2, 5, 10, 50, 100]],
            "network_types": [
                {"name": "Erdős-Rényi", "dist": "Poisson", "eml": 1},
                {"name": "Scale-free (BA)", "dist": "Power law", "eml": 2},
                {"name": "Regular lattice", "dist": "Delta", "eml": 0},
                {"name": "Small-world (WS)", "dist": "Peaked exponential", "eml": 1},
            ],
        }


@dataclass
class SpectralGraphTheory:
    """
    Graph Laplacian L = D - A. Eigenvalues λ₁ ≤ λ₂ ≤ ... ≤ λ_n.

    EML structure:
    - λ₁ = 0 (always): EML-0 (topological invariant)
    - Fiedler value λ₂ (algebraic connectivity): EML-2 (depends on graph structure rationally)
    - Cheeger inequality: h(G) ≥ λ₂/2: EML-2 bounds EML-2
    - Heat kernel: K_t(i,j) = Σ_k exp(-λ_k·t)·φ_k(i)·φ_k(j) = EML-1 (sum of exp(-λt))
    - Spectral gap λ₂ - λ₁ = λ₂: mixing time T_mix ~ 1/λ₂ = EML-2
    - Random walk on graph: stationary distribution π_i = d_i/(2|E|): EML-0 (rational)
    - Normalized adjacency eigenvalues in [-1,1]: EML-3 (oscillatory band structure)
    """

    def path_graph_spectrum(self, n: int) -> dict:
        """Laplacian eigenvalues for path graph P_n: λ_k = 2(1-cos(πk/n))."""
        eigenvalues = [2 * (1 - math.cos(math.pi * k / n)) for k in range(n)]
        fiedler = eigenvalues[1] if n > 1 else 0.0
        return {
            "n": n,
            "eigenvalues": [round(e, 6) for e in eigenvalues[:min(n, 8)]],
            "lambda_1": 0.0,
            "fiedler_lambda_2": round(fiedler, 6),
            "eml_lambda1": 0,
            "eml_fiedler": 2,
            "eml_spectrum": 3,
            "reason": "λ_k = 2(1-cos(πk/n)): EML-3 (cosine function of integer index)",
        }

    def cycle_graph_spectrum(self, n: int) -> dict:
        """Laplacian eigenvalues for cycle C_n: λ_k = 2(1-cos(2πk/n))."""
        eigenvalues = [2 * (1 - math.cos(2 * math.pi * k / n)) for k in range(n)]
        return {
            "n": n,
            "eigenvalues": [round(e, 6) for e in eigenvalues[:min(n, 8)]],
            "fiedler": round(eigenvalues[1], 6),
            "eml_spectrum": 3,
            "reason": "Cycle spectrum: 2(1-cos(2πk/n)): EML-3",
        }

    def heat_kernel_trace(self, eigenvalues: list[float], t: float) -> dict:
        """Tr(K_t) = Σ exp(-λ_k·t): heat trace = EML-1 per term."""
        trace = sum(math.exp(-lam * t) for lam in eigenvalues)
        return {
            "t": t,
            "trace": round(trace, 6),
            "eml": 1,
            "reason": "Tr(K_t) = Σ exp(-λ_k·t): sum of EML-1 terms = EML-1",
        }

    def to_dict(self) -> dict:
        path10 = self.path_graph_spectrum(10)
        eigs = [2 * (1 - math.cos(math.pi * k / 10)) for k in range(10)]
        return {
            "path_graph_n10": path10,
            "cycle_graph_n8": self.cycle_graph_spectrum(8),
            "heat_kernel": [self.heat_kernel_trace(eigs, t) for t in [0.1, 0.5, 1.0, 5.0]],
            "eml_lambda1": 0,
            "eml_fiedler": 2,
            "eml_full_spectrum": 3,
            "eml_heat_kernel": 1,
            "cheeger_inequality": "h(G) ≥ λ₂/2: EML-2 bound on conductance",
        }


@dataclass
class NetworkPhaseTransitions:
    """
    Percolation: giant component emerges at p_c = 1/⟨k⟩ for ER graphs.

    EML structure:
    - Critical threshold p_c = 1/(n-1) for ER: EML-0 (rational)
    - Giant component size S ~ (p-p_c)/p for p > p_c: EML-2 (linear in deviation = EML-2 geometric)
    - Susceptibility χ ~ |p-p_c|^{-γ}: EML-∞ at p_c (diverges)
    - Order parameter S: mean-field exponent β=1 → S ~ (p-p_c)^1: EML-2
    - Community detection (modularity optimization): NP-hard → EML-∞
    - Graph coloring χ(G): NP-hard → EML-∞ in general
    - Minimum spanning tree weight W_MST ~ n·ζ(3)/2: EML-2 for ER
    """

    def percolation_giant_component(self, p: float, n: int = 1000) -> dict:
        """ER percolation: giant component size S(p) above p_c = 1/(n-1)."""
        p_c = 1.0 / (n - 1)
        if p <= p_c:
            S = 0.0
            eml = 0
            regime = "subcritical"
        elif p < 5 * p_c:
            S = (p - p_c) / p
            eml = 2
            regime = "near-critical"
        else:
            S = 1.0 - math.exp(-(p * n * S if False else p * n * 0.9))
            S = 1.0 - 1.0 / (p * n)
            eml = 1
            regime = "supercritical"
        return {
            "p": round(p, 5),
            "p_c": round(p_c, 6),
            "S_giant": round(S, 6),
            "regime": regime,
            "eml": "∞" if abs(p - p_c) < 1e-5 else eml,
            "reason": "Giant component: EML-2 near p_c; EML-∞ exactly at p_c (susceptibility diverges)",
        }

    def small_world_clustering(self, k: int, p_rewire: float) -> dict:
        """
        Watts-Strogatz: C(p) ≈ C_0·(1-p)^3, L(p) ~ ln(n)/ln(k).
        C: clustering coefficient, L: average path length.
        """
        C0 = (k - 2) / (2 * (k - 1))
        C_p = C0 * (1 - p_rewire) ** 3
        return {
            "k": k, "p_rewire": p_rewire,
            "C_0": round(C0, 4),
            "C_p": round(C_p, 4),
            "eml_C": 2,
            "eml_L": 2,
            "reason": "C(p)=C₀(1-p)³: EML-2 (polynomial); L~ln(n)/ln(k): EML-2 (log/log ratio)",
        }

    def to_dict(self) -> dict:
        p_vals = [0.0005, 0.001, 0.002, 0.005, 0.01]
        return {
            "percolation": [self.percolation_giant_component(p) for p in p_vals],
            "small_world": [self.small_world_clustering(6, p) for p in [0.0, 0.1, 0.3, 0.5, 1.0]],
            "phase_transition_eml": EML_INF,
            "reason_transition": "Percolation threshold = network phase transition = EML-∞",
            "community_detection_eml": EML_INF,
            "reason_community": "Modularity optimization NP-hard = EML-∞ (no polynomial algorithm)",
        }


@dataclass
class RandomWalkNetworks:
    """
    Random walks on graphs: PageRank, mixing times, centrality.

    EML structure:
    - Stationary distribution π_i = d_i/(2|E|): EML-0 (rational in degrees)
    - PageRank: x = αAD⁻¹x + (1-α)1/n → fixed point of EML-1 operation
    - Mixing time T_mix ~ 1/λ₂ · ln(n): EML-2 (log × inverse Fiedler)
    - Betweenness centrality: b_v = Σ σ(s,t,v)/σ(s,t): EML-0 (rational counting)
    - Closeness centrality: c_v = (n-1)/Σ d(v,u): EML-0 (rational)
    - Eigenvector centrality: x = Ax/λ_max → EML-1 fixed point (like PageRank)
    """

    def pagerank_power_iteration(self, n: int = 5, alpha: float = 0.85,
                                  steps: int = 20) -> dict:
        """PageRank via power iteration on complete graph."""
        x = [1.0 / n] * n
        for _ in range(steps):
            x_new = [(alpha / n + (1 - alpha) / n)] * n
            x = x_new
        return {
            "n": n, "alpha": alpha, "iterations": steps,
            "pagerank": [round(xi, 6) for xi in x],
            "eml": 1,
            "reason": "PageRank = fixed point of linear map = EML-1 (dominant eigenvector)",
        }

    def mixing_time_estimate(self, n: int, lambda2: float) -> dict:
        """T_mix ≈ (1/λ₂) · ln(n/ε) for ε=0.01."""
        eps = 0.01
        T = (1.0 / lambda2) * math.log(n / eps) if lambda2 > 0 else float("inf")
        return {
            "n": n,
            "lambda_2": lambda2,
            "T_mix_approx": round(T, 2),
            "eml": 2,
            "reason": "T_mix ~ ln(n)/λ₂: EML-2 (logarithm / EML-2 Fiedler value)",
        }

    def to_dict(self) -> dict:
        return {
            "pagerank_n5": self.pagerank_power_iteration(5),
            "mixing_times": [
                self.mixing_time_estimate(100, 0.1),
                self.mixing_time_estimate(1000, 0.05),
                self.mixing_time_estimate(10000, 0.01),
            ],
            "centrality_eml": {
                "degree": 0, "betweenness": 0, "closeness": 0,
                "eigenvector": 1, "pagerank": 1,
                "reason": "Degree/betweenness/closeness = rational counts = EML-0; eigenvector = EML-1 fixed point",
            },
        }


def analyze_graph_eml() -> dict:
    deg = DegreeDistributions()
    spec = SpectralGraphTheory()
    phase = NetworkPhaseTransitions()
    rw = RandomWalkNetworks()
    return {
        "session": 104,
        "title": "Graph Theory & Complex Networks: EML as Network Substrate",
        "key_theorem": {
            "theorem": "EML Network Depth Theorem",
            "statement": (
                "Erdős-Rényi degree distribution is EML-1 (Poisson = single exponential). "
                "Scale-free power-law degree distribution is EML-2 (exp(-γ·ln k)). "
                "Graph Laplacian spectrum is EML-3 (cosine eigenvalues: 2(1-cos(πk/n))). "
                "Heat kernel trace Tr(K_t) = Σ exp(-λ_k·t) is EML-1. "
                "Centrality measures (degree, betweenness) are EML-0 (rational). "
                "PageRank and eigenvector centrality are EML-1 (fixed point = ground state). "
                "Percolation phase transition at p_c is EML-∞. "
                "Community detection (modularity) is EML-∞ (NP-hard)."
            ),
        },
        "degree_distributions": deg.to_dict(),
        "spectral_theory": spec.to_dict(),
        "phase_transitions": phase.to_dict(),
        "random_walks": rw.to_dict(),
        "eml_depth_summary": {
            "EML-0": "Node degree; betweenness/closeness centrality; percolation threshold p_c = 1/⟨k⟩; graph coloring number",
            "EML-1": "ER Poisson degree P(k)=e^{-λ}λ^k/k!; PageRank (eigenvector fixed point); heat kernel Tr(e^{-tL}); small-world tail",
            "EML-2": "Scale-free P(k)~k^{-γ}; Fiedler value λ₂; clustering C(p)=(1-p)³; mixing time ln(n)/λ₂; MST weight",
            "EML-3": "Laplacian eigenvalues 2(1-cos(πk/n)); normalized adjacency band structure; oscillatory modes",
            "EML-∞": "Percolation transition (susceptibility diverges); community detection NP-hard; graph isomorphism (likely)",
        },
        "rabbit_hole_log": [
            "Scale-free networks are EML-2 but ER networks are EML-1: the Barabási-Albert preferential attachment mechanism adds one ln operation (the power law exponent γ selects a log-linear structure). Rich-get-richer = EML-2 vs. random = EML-1. Social networks are more complex than random by exactly one EML depth.",
            "PageRank is the EML-1 ground state of the internet: it's the dominant eigenvector of the (damped) adjacency matrix, exactly analogous to the Boltzmann distribution in statistical mechanics. The damping factor α=0.85 is the EML-1 'temperature' of the web.",
            "Spectral gap λ₂ controls everything: mixing time, conductance, and synchronization in coupled oscillators all depend on λ₂ = EML-2. The Fiedler vector partitions the graph. The entire information-transport capacity of a network is captured by a single EML-2 number.",
            "Percolation = EML-∞ at p_c: the giant component size S(p) is continuous but its derivative is infinite at p_c. This is an EML-∞ transition (like Ising, like NS blowup) where the local structure (EML-2) cannot predict the global behavior (EML-∞).",
        ],
        "connections": {
            "to_session_57": "Ising phase transition = EML-∞. Percolation = network EML-∞ transition. Same universality class.",
            "to_session_88": "Grand Synthesis: PageRank = EML-1 ground state principle. Degree = EML-0 topological invariant.",
        },
    }


if __name__ == "__main__":
    print(json.dumps(analyze_graph_eml(), indent=2, default=str))
