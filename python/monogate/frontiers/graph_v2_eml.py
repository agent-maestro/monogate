"""
Session 134 — Graph Theory Deep II: Spectral Methods, Percolation & Networks

EML operator: eml(x,y) = exp(x) - ln(y)
EML depth hierarchy: 0 (topology) | 1 (equilibria) | 2 (geometry) | 3 (waves) | ∞ (singularities)

Key theorem: Spectral graph quantities are EML-2; percolation phase transitions are EML-∞.
"""

from __future__ import annotations
import math
from dataclasses import dataclass
from typing import Any


# ---------------------------------------------------------------------------
# 1. Spectral Graph Theory
# ---------------------------------------------------------------------------

@dataclass
class SpectralGraphTheory:
    """Laplacian spectrum, Cheeger inequality, random walk mixing."""

    n: int = 8      # number of vertices
    p: float = 0.4  # edge probability (Erdos-Renyi)

    def laplacian_eigenvalue_approx(self, k: int) -> float:
        """
        Approximate k-th eigenvalue of random regular graph Laplacian.
        For d-regular graph: λ_k ≈ d * (1 - cos(πk/n)). EML-2 (cosine).
        """
        d = self.p * (self.n - 1)  # expected degree
        return d * (1 - math.cos(math.pi * k / self.n))

    def algebraic_connectivity(self) -> float:
        """λ₂ (Fiedler value): measures connectivity. EML-2."""
        return self.laplacian_eigenvalue_approx(1)

    def cheeger_constant_bound(self) -> dict[str, float]:
        """
        Cheeger inequality: λ₂/2 ≤ h(G) ≤ √(2λ₂).
        EML-2 bounds on graph expansion.
        """
        lam2 = self.algebraic_connectivity()
        lower = lam2 / 2.0
        upper = math.sqrt(2 * lam2)
        return {"lambda_2": round(lam2, 4), "lower_bound": round(lower, 4), "upper_bound": round(upper, 4)}

    def mixing_time(self) -> float:
        """t_mix ≈ (1/λ₂) * log(n/ε). EML-2."""
        lam2 = self.algebraic_connectivity()
        epsilon = 0.01
        if lam2 < 1e-10:
            return float('inf')
        return (1.0 / lam2) * math.log(self.n / epsilon)

    def spectral_gap(self) -> float:
        """Gap between λ_1=0 and λ₂. Controls mixing. EML-2."""
        return self.algebraic_connectivity()

    def graph_energy(self) -> float:
        """Sum of |eigenvalues| ≈ n * expected_degree^{1/2}. EML-2."""
        d = self.p * (self.n - 1)
        return self.n * math.sqrt(d)

    def analyze(self) -> dict[str, Any]:
        eigenvalues = {k: round(self.laplacian_eigenvalue_approx(k), 4)
                       for k in range(self.n)}
        cheeger = self.cheeger_constant_bound()
        t_mix = self.mixing_time()
        return {
            "model": "SpectralGraphTheory",
            "n": self.n,
            "p": self.p,
            "expected_degree": round(self.p * (self.n - 1), 2),
            "laplacian_eigenvalues_approx": eigenvalues,
            "algebraic_connectivity_lambda2": round(self.algebraic_connectivity(), 4),
            "cheeger_bounds": cheeger,
            "mixing_time_steps": round(t_mix, 2),
            "graph_energy": round(self.graph_energy(), 4),
            "eml_depth": {
                "laplacian_eigenvalues": 2,
                "cheeger_bounds": 2,
                "mixing_time": 2,
                "graph_energy": 2
            },
            "key_insight": "All spectral graph quantities are EML-2 (quadratic/cosine structure)"
        }


# ---------------------------------------------------------------------------
# 2. Percolation Theory
# ---------------------------------------------------------------------------

@dataclass
class PercolationTheory:
    """Bond/site percolation on infinite lattice; phase transition at p_c."""

    dimension: int = 2
    lattice: str = "square"   # square or triangular

    def critical_probability(self) -> float:
        """
        Exact p_c:
        - Square: 1/2
        - Triangular: 2*sin(π/18) ≈ 0.3473
        EML-3 for triangular (contains sin), EML-0 for square.
        """
        if self.lattice == "triangular":
            return 2 * math.sin(math.pi / 18)
        return 0.5  # square lattice exact

    def order_parameter(self, p: float) -> float:
        """
        P_∞(p): probability of being in infinite cluster.
        P_∞ = 0 for p < p_c, P_∞ ~ (p-p_c)^β for p > p_c.
        EML-2 (power law), EML-∞ at p_c (non-analytic).
        """
        beta = 5.0 / 36.0  # 2D critical exponent
        pc = self.critical_probability()
        if p <= pc:
            return 0.0
        return (p - pc) ** beta

    def correlation_length(self, p: float) -> float:
        """
        ξ(p) ~ |p - p_c|^{-ν}. EML-2 (power law), diverges at p_c.
        ν = 4/3 in 2D.
        """
        nu = 4.0 / 3.0
        pc = self.critical_probability()
        if abs(p - pc) < 1e-10:
            return float('inf')
        return abs(p - pc) ** (-nu)

    def mean_cluster_size(self, p: float) -> float:
        """
        S(p) ~ |p - p_c|^{-γ}. EML-2 power law, diverges at criticality.
        γ = 43/18 in 2D.
        """
        gamma = 43.0 / 18.0
        pc = self.critical_probability()
        if abs(p - pc) < 1e-10:
            return float('inf')
        return abs(p - pc) ** (-gamma)

    def fractal_dimension(self) -> float:
        """
        At p_c, infinite cluster is fractal with d_f = 91/48 in 2D. EML-0 (rational).
        """
        return 91.0 / 48.0

    def analyze(self) -> dict[str, Any]:
        pc = self.critical_probability()
        p_vals = [0.3, 0.4, 0.45, pc, 0.55, 0.6, 0.7]
        order = {}
        xi = {}
        mean_s = {}
        for p in p_vals:
            key = round(p, 3)
            order[key] = round(self.order_parameter(p), 6)
            corr = self.correlation_length(p)
            xi[key] = round(corr, 4) if corr != float('inf') else "∞"
            ms = self.mean_cluster_size(p)
            mean_s[key] = round(ms, 4) if ms != float('inf') else "∞"

        return {
            "model": "PercolationTheory",
            "lattice": self.lattice,
            "dimension": self.dimension,
            "critical_probability_pc": round(pc, 6),
            "order_parameter_vs_p": order,
            "correlation_length_vs_p": xi,
            "mean_cluster_size_vs_p": mean_s,
            "fractal_dimension_at_pc": round(self.fractal_dimension(), 4),
            "critical_exponents": {"beta": 5.0/36.0, "nu": 4.0/3.0, "gamma": 43.0/18.0},
            "eml_depth": {
                "pc_square": 0,
                "pc_triangular": 3,
                "order_parameter": 2,
                "correlation_length": 2,
                "percolation_transition": "∞",
                "fractal_dimension": 0
            },
            "key_insight": "Percolation observables are EML-2 power laws; the transition itself is EML-∞"
        }


# ---------------------------------------------------------------------------
# 3. Dynamic Networks & Scale-Free Graphs
# ---------------------------------------------------------------------------

@dataclass
class DynamicNetworks:
    """Barabasi-Albert preferential attachment; network phase transitions."""

    n_nodes: int = 1000
    m: int = 2  # edges added per new node

    def degree_distribution(self, k: int) -> float:
        """P(k) ~ k^{-3} for BA networks. EML-2 (power law)."""
        if k <= 0:
            return 0.0
        return 2.0 * (self.m ** 2) / (k * (k + 1) * (k + 2))

    def clustering_coefficient(self, k: int) -> float:
        """C(k) ~ k^{-1} in BA networks. EML-2."""
        if k <= 1:
            return 0.0
        return (math.log(self.n_nodes) ** 2) / (k * self.n_nodes)

    def average_path_length(self) -> float:
        """L ~ ln(N)/ln(ln(N)) for scale-free. EML-2 (double log)."""
        if self.n_nodes <= 2:
            return 1.0
        ln_n = math.log(self.n_nodes)
        ln_ln_n = math.log(ln_n) if ln_n > 1 else 1.0
        return ln_n / ln_ln_n

    def rich_club_coefficient(self, k_threshold: int = 50) -> float:
        """Fraction of edges among high-degree nodes. EML-2."""
        total_high = sum(1 for k in range(k_threshold, int(self.n_nodes / 2))
                         if self.degree_distribution(k) * self.n_nodes > 0.5)
        return total_high / max(1, self.n_nodes // 2)

    def robustness_to_attack(self, fraction_removed: float) -> float:
        """
        Fraction of network destroyed by targeted attack (remove hubs).
        For scale-free: robust to random failure, fragile to targeted attack.
        Critical fraction ~ 1/ln(N). EML-2.
        """
        critical_fraction = 1.0 / math.log(self.n_nodes)
        if fraction_removed >= critical_fraction:
            return 0.0  # network collapses = EML-∞ event
        return 1.0 - fraction_removed / critical_fraction

    def analyze(self) -> dict[str, Any]:
        k_vals = [2, 5, 10, 20, 50, 100]
        degree_dist = {k: round(self.degree_distribution(k), 6) for k in k_vals}
        clustering = {k: round(self.clustering_coefficient(k), 6) for k in k_vals}
        L = self.average_path_length()
        critical_f = 1.0 / math.log(self.n_nodes)
        robustness = {round(f, 2): round(self.robustness_to_attack(f), 4)
                      for f in [0.05, 0.1, 0.15, 0.2]}

        return {
            "model": "DynamicNetworks",
            "n_nodes": self.n_nodes,
            "m": self.m,
            "degree_distribution_BA": degree_dist,
            "clustering_coefficient": clustering,
            "average_path_length": round(L, 4),
            "critical_attack_fraction": round(critical_f, 4),
            "robustness_to_targeted_attack": robustness,
            "eml_depth": {
                "degree_distribution": 2,
                "clustering": 2,
                "average_path_length": 2,
                "network_collapse": "∞"
            },
            "key_insight": "Scale-free networks: all measurables are EML-2; collapse under attack is EML-∞"
        }


# ---------------------------------------------------------------------------
# Main analysis function
# ---------------------------------------------------------------------------

def analyze_graph_v2_eml() -> dict[str, Any]:
    sg = SpectralGraphTheory(n=12, p=0.35)
    perc = PercolationTheory(dimension=2, lattice="square")
    dn = DynamicNetworks(n_nodes=1000, m=2)

    return {
        "session": 134,
        "title": "Graph Theory Deep II: Spectral Methods, Percolation & Scale-Free Networks",
        "eml_operator": "eml(x,y) = exp(x) - ln(y)",
        "spectral_graph_theory": sg.analyze(),
        "percolation_theory": perc.analyze(),
        "dynamic_networks": dn.analyze(),
        "eml_depth_summary": {
            "EML-0": "Euler characteristic, chromatic number, topological graph invariants, fractal dimension",
            "EML-1": "Random walk stationary distribution (Boltzmann over degrees)",
            "EML-2": "Laplacian eigenvalues, Cheeger bounds, mixing time, power-law degree distribution",
            "EML-3": "Oscillatory processes on graphs, quantum walks (unitary → EML-3)",
            "EML-∞": "Percolation transition, network collapse under attack, giant component emergence"
        },
        "key_theorem": (
            "The EML Graph Depth Theorem: "
            "All quantitative graph observables (eigenvalues, mixing times, degree distributions, "
            "path lengths) are EML-2 (quadratic or logarithmic structure). "
            "The discrete phase transitions — percolation, network collapse, giant component "
            "formation — are EML-∞: non-analytic jumps in the order parameter at critical p_c."
        ),
        "rabbit_hole_log": [
            "Laplacian eigenvalues = d*(1-cos(πk/n)): cosine → EML-2 (same as Fisher info curvature)",
            "Cheeger inequality: both bounds are EML-2 (linear and square root of λ₂)",
            "Mixing time = (1/λ₂)*log(n/ε): double application of log → EML-2",
            "Percolation P∞ ~ (p-p_c)^β: power law = EML-2, but p_c transition is EML-∞",
            "BA scale-free: P(k)~k^{-3} = power law = EML-2; collapse = EML-∞",
            "Average path length L~ln(N)/ln(ln(N)): double log structure = EML-2"
        ],
        "connections": {
            "S60_info_theory": "Spectral gap = information-geometric curvature (EML-2)",
            "S57_stat_mech": "Random walk stationary distribution = Boltzmann = EML-1",
            "S75_qft": "Percolation transition = same universality class as QFT phase transitions",
            "S124_graph_deep": "Extends spectral methods from Session 124 with percolation + dynamics"
        }
    }


if __name__ == "__main__":
    import json
    print(json.dumps(analyze_graph_v2_eml(), indent=2, default=str))
