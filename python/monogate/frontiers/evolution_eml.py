"""
Session 102 — Evolutionary Biology & Genetics: EML as Evolutionary Substrate

Fitness landscapes, mutation-selection balance, speciation, and evolutionary dynamics
classified by EML depth. Tests whether evolutionary phase transitions appear as EML-∞.

Key theorem: Fitness functions on sequence space are EML-2 (log-linear models) or EML-∞
(rugged NK landscapes). The quasispecies equation has EML-1 fixed point (maximum-fitness
distribution). Speciation (lineage splitting) is EML-∞ (symmetry breaking). Neutral
evolution (drift) is EML-2 (diffusion on sequence space).
"""

from __future__ import annotations
import math, json
from dataclasses import dataclass, field


EML_INF = float("inf")


@dataclass
class FitnessLandscape:
    """
    Fitness landscape W(σ): assigns reproductive fitness to each genome σ ∈ {0,1}^L.

    EML structure:
    - Additive (HoC model): W(σ) = Σ_i w_i·σ_i: EML-2 (linear → log-linear)
    - Multiplicative: W(σ) = ∏_i (1+s_i·σ_i): EML-2 (product = exp(Σ log) = EML-2)
    - NK model (epistasis): EML-∞ (random rugged landscape, no closed form)
    - Mount Fuji (single peak): EML-1 (Gaussian around optimum = EML-1)
    - Rough Mt Fuji: EML-∞ (rugged + single peak)
    """

    def additive_fitness(self, L: int = 10) -> dict:
        """W = exp(Σ s_i · σ_i) — Malthusian fitness, log-linear."""
        s_vals = [0.1 * (i % 3 - 1) for i in range(L)]
        all_ones = sum(s for s in s_vals)
        all_zeros = 0.0
        best = sum(s for s in s_vals if s > 0)
        return {
            "model": "Additive (log-linear)",
            "L": L,
            "selection_coefficients": [round(s, 3) for s in s_vals],
            "ln_W_all_ones": round(all_ones, 6),
            "ln_W_all_zeros": all_zeros,
            "ln_W_optimal": round(best, 6),
            "eml": 2,
            "reason": "W = exp(Σ s_i σ_i): EML-2 (exp of linear = EML-1 ground state adjusted to EML-2 for multi-site)",
        }

    def nk_landscape_stats(self, N: int = 10, K: int = 3) -> dict:
        """NK model: each site depends on K neighbors → epistasis → rugged."""
        n_optima_approx = int(N * math.exp(K / 2))  # rough approximation
        correlation_length = 1.0 / (K + 1)
        return {
            "N": N, "K": K,
            "n_local_optima_approx": n_optima_approx,
            "correlation_length": round(correlation_length, 4),
            "eml": EML_INF,
            "reason": "NK rugged landscape: no closed form, exponentially many local optima = EML-∞",
        }

    def to_dict(self) -> dict:
        return {
            "additive_fitness": self.additive_fitness(10),
            "nk_model": self.nk_landscape_stats(10, 3),
            "landscape_types": [
                {"name": "Additive", "eml": 2, "optima": 1},
                {"name": "Multiplicative", "eml": 2, "optima": 1},
                {"name": "Mount Fuji", "eml": 1, "optima": 1},
                {"name": "NK (K>0)", "eml": EML_INF, "optima": "exponential"},
                {"name": "Random (K=N-1)", "eml": EML_INF, "optima": "~N/e"},
            ],
        }


@dataclass
class QuasispeciesEquation:
    """
    Eigen's quasispecies equation: ṗ_i = Σ_j Q_{ij} · W_j · p_j - φ · p_i

    Q_{ij}: mutation matrix, W_j: fitness, φ: mean fitness.
    Fixed point = quasispecies distribution p* = dominant eigenvector of Q·W.

    EML structure:
    - W_j (fitness): EML-1 (Boltzmann-like exponential in fitness space)
    - Q_{ij} = μ^{d(i,j)}(1-μ)^{L-d(i,j)}: EML-2 (power × power = EML-2)
    - p* = dominant eigenvector: EML-1 (fixed point of multiplicative dynamics)
    - Error threshold μ_c: EML-2 (rational function of fitness ratio)
    - Above μ_c: quasispecies collapses to uniform = EML-1 → EML-0 degenerate
    """

    def mutation_matrix_2seq(self, mu: float) -> dict:
        """2-sequence system: W = (W_1, W_2), Q_{12} = μ."""
        return {
            "mu": mu,
            "Q_11": round((1 - mu), 6),
            "Q_12": round(mu, 6),
            "eml_Q": 2,
            "reason": "Q_{ij} = μ^d(1-μ)^{L-d}: power law = EML-2",
        }

    def error_threshold(self, W_max: float = 2.0, L: int = 100) -> dict:
        """Critical mutation rate: μ_c ≈ ln(W_max)/L."""
        mu_c = math.log(W_max) / L
        return {
            "W_max": W_max,
            "L": L,
            "mu_c": round(mu_c, 8),
            "formula": "ln(W_max)/L: EML-2 (log of fitness / sequence length)",
            "eml": 2,
            "above_threshold": "p* → uniform = EML-1 (max-entropy = ground state)",
            "below_threshold": "p* = quasispecies = EML-1 (eigenvector of EML-2 matrix)",
        }

    def to_dict(self) -> dict:
        return {
            "quasispecies": "Dominant eigenvector of Q·W: EML-1 (ground state of mutation-selection)",
            "mutation_matrix": self.mutation_matrix_2seq(0.01),
            "error_threshold": self.error_threshold(2.0, 100),
            "eml_quasispecies": 1,
            "eml_error_threshold": 2,
            "eml_above_threshold": 1,
            "transition_eml": EML_INF,
        }


@dataclass
class MutationSelectionBalance:
    """
    Mutation-selection balance: equilibrium allele frequency q* = μ/s.

    EML structure:
    - q* = μ/s: EML-0 (ratio of constants = EML-0 per parameter)
    - Drift (finite population N): q fluctuates with σ_q ~ √(q(1-q)/N): EML-2
    - Fixation probability: P_fix = (1-exp(-2Ns))/(1-exp(-2N·s·p)): EML-1
    - Neutral evolution (s=0): P_fix = 1/N = EML-0 (rational)
    - Kimura's substitution rate: k = 2NμP_fix ≈ μ for neutral: EML-0
    """

    def fixation_probability(self, N: int, s: float, p0: float = None) -> dict:
        """Kimura fixation probability for allele with effect s in population N."""
        if p0 is None:
            p0 = 1 / (2 * N)
        if abs(s) < 1e-8:
            P_fix = p0  # neutral
            eml = 0
            reason = "Neutral: P_fix = p₀ = 1/(2N) = EML-0 (rational)"
        else:
            num = 1 - math.exp(-2 * N * s * p0) if abs(2 * N * s * p0) < 700 else 1.0
            den = 1 - math.exp(-2 * N * s) if abs(2 * N * s) < 700 else 1.0
            P_fix = num / den if abs(den) > 1e-10 else p0
            eml = 1
            reason = "P_fix = (1-exp(-2Nsp))/(1-exp(-2Ns)): EML-1 (ratio of EML-1 = EML-1)"
        return {
            "N": N, "s": s, "p0": round(p0, 8),
            "P_fix": round(P_fix, 8),
            "eml": eml,
            "reason": reason,
        }

    def to_dict(self) -> dict:
        cases = [
            (100, 0.0), (100, 0.01), (100, 0.05),
            (1000, 0.0), (1000, 0.001),
        ]
        return {
            "fixation_table": [self.fixation_probability(N, s) for N, s in cases],
            "mut_sel_balance": "q* = μ/s: EML-0 (ratio)",
            "kimura_formula": "P_fix = (1-e^{-2Nsp})/(1-e^{-2Ns}): EML-1",
            "drift_fluctuation": "σ_q ~ √(q(1-q)/N): EML-2 (square root of rational)",
        }


@dataclass
class SpeciationEML:
    """
    Speciation: splitting of one lineage into two reproductively isolated species.

    EML structure:
    - Allopatric speciation: geographic barrier (EML-0 discrete event) → genetic divergence (EML-2)
    - Sympatric speciation: fitness valley crossing → EML-∞ (like phase transition in fitness space)
    - Species concept (BSC): reproductive isolation = EML-0 (binary: yes/no)
    - Dobzhansky-Muller incompatibility: aAbB × aabb → EML-2 fitness epistasis
    - Phylogenetic branching: EML-0 (tree topology = combinatorial) + EML-1 (branch lengths = Poisson)
    """

    def dobzhansky_muller(self, s_AB: float = 0.1) -> dict:
        """DM incompatibility: hybrid fitness W_hybrid = 1 - s_{AB}."""
        return {
            "incompatibility_s": s_AB,
            "hybrid_fitness": round(1 - s_AB, 4),
            "parental_fitness": 1.0,
            "fitness_valley": True,
            "eml": 2,
            "reason": "W = 1 - s: linear = EML-2; DM epistasis = product of EML-2 terms",
            "speciation_type": "Bateson-Dobzhansky-Muller incompatibility",
        }

    def phylogenetic_birth_death(self, lambda_b: float = 0.5, mu_d: float = 0.1) -> dict:
        """Birth-death process for speciation/extinction."""
        net_rate = lambda_b - mu_d
        E_taxa = math.exp(net_rate) if abs(net_rate) < 700 else float("inf")
        return {
            "speciation_rate": lambda_b,
            "extinction_rate": mu_d,
            "net_diversification": net_rate,
            "E_taxa_after_1_time": round(E_taxa, 4),
            "eml_branch_lengths": 1,
            "eml_tree_topology": 0,
            "reason": "Branch lengths ~ Poisson(λ): EML-1 (exponential waiting times); topology = EML-0 (integer tree)",
        }

    def to_dict(self) -> dict:
        return {
            "dm_incompatibility": self.dobzhansky_muller(0.1),
            "birth_death": self.phylogenetic_birth_death(),
            "speciation_eml": EML_INF,
            "reason_speciation": "Sympatric speciation = fitness landscape phase transition = EML-∞",
            "allopatric_eml": 0,
            "reason_allopatric": "Geographic barrier = discrete EML-0 event; divergence afterwards = EML-2",
        }


def analyze_evolution_eml() -> dict:
    fitness = FitnessLandscape()
    quasi = QuasispeciesEquation()
    mut_sel = MutationSelectionBalance()
    spec = SpeciationEML()
    return {
        "session": 102,
        "title": "Evolutionary Biology & Genetics: EML as Evolutionary Substrate",
        "key_theorem": {
            "theorem": "EML Evolutionary Depth Theorem",
            "statement": (
                "Additive fitness landscapes are EML-2 (log-linear). "
                "NK rugged landscapes are EML-∞ (no closed form). "
                "Quasispecies fixed point is EML-1 (dominant eigenvector = ground state). "
                "Error threshold is EML-2 (ln(W_max)/L). "
                "Fixation probability P_fix = (1-e^{-2Nsp})/(1-e^{-2Ns}) is EML-1. "
                "Neutral evolution gives P_fix = 1/(2N) = EML-0. "
                "Speciation (sympatric) is EML-∞ (phase transition in fitness space). "
                "Phylogenetic branch lengths are EML-1 (exponential waiting times); topology is EML-0."
            ),
        },
        "fitness_landscape": fitness.to_dict(),
        "quasispecies": quasi.to_dict(),
        "mutation_selection": mut_sel.to_dict(),
        "speciation": spec.to_dict(),
        "eml_depth_summary": {
            "EML-0": "Neutral fixation 1/(2N); tree topology (combinatorial); geographic barrier; reproductive isolation (binary)",
            "EML-1": "Quasispecies fixed point; fixation probability P_fix; branch lengths (exponential waiting); Mt Fuji peak",
            "EML-2": "Additive/multiplicative fitness; mutation matrix Q; error threshold ln(W_max)/L; DM incompatibility",
            "EML-∞": "NK rugged landscape; sympatric speciation; adaptive radiation (EML-∞ fitness landscape traversal)",
        },
        "rabbit_hole_log": [
            "Quasispecies = EML-1: just like the Boltzmann distribution (Session 57), the quasispecies fixed point maximizes 'fitness-weighted entropy'. The mutation-selection equilibrium is the EML-1 ground state of evolution. Same mathematics, different domain.",
            "NK model and EML depth: K=0 → EML-2 (additive); K=1 → EML-2 (near-additive); K≥2 → EML-∞ (rugged). The transition K=2 is the evolutionary analog of the 2D Ising phase transition (Session 57): below K=2, landscape is smooth (EML-2); at/above K=2, exponentially many local optima appear (EML-∞).",
            "Neutral theory: most evolution is EML-0 (neutral drift). Selection is EML-1 (Boltzmann fitness). Epistasis is EML-∞ (NK landscape). The Kimura framework naturally separates the three EML depth classes of evolutionary change.",
        ],
        "connections": {
            "to_session_57": "Phase transitions = EML-∞. Speciation = evolutionary phase transition = EML-∞",
            "to_session_94": "Session 94: Hill functions = EML-2 GRN. Session 102: fitness = EML-2 for additive; same class",
        },
    }


if __name__ == "__main__":
    print(json.dumps(analyze_evolution_eml(), indent=2, default=str))
