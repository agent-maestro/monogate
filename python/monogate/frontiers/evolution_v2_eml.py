"""
Session 132 — Evolutionary Biology Deep II: Fitness Landscapes, Speciation & Punctuated Equilibrium

EML operator: eml(x,y) = exp(x) - ln(y)
EML depth hierarchy: 0 (topology) | 1 (equilibria) | 2 (geometry) | 3 (waves) | ∞ (singularities)

Key theorem: Evolutionary stasis is EML-1 (exponential stability);
speciation and punctuated equilibrium transitions are EML-∞.
"""

from __future__ import annotations
import math
import random
from dataclasses import dataclass
from typing import Any


# ---------------------------------------------------------------------------
# 1. NK Fitness Landscape
# ---------------------------------------------------------------------------

@dataclass
class NKFitnessLandscape:
    """Kauffman (1993): N genes, each interacting with K others."""

    N: int = 10   # genome length
    K: int = 2    # epistatic connections per gene

    def expected_local_optima(self) -> float:
        """Expected number of local optima ~ exp(N) / (K+1)^N * correction. EML-1."""
        # Kauffman: approx 1/(K+1) fraction of genotypes are local optima
        # Total genotypes = 2^N; local optima ~ 2^N / (K+1)^N * correction
        fraction = 1.0 / (self.K + 1)
        n_optima = (2 ** self.N) * (fraction ** self.N)
        # Equivalently: exp(N * ln(2/(K+1))) = EML-1 structure
        log_n_optima = self.N * math.log(2.0 / (self.K + 1))
        return math.exp(log_n_optima)

    def fitness(self, genotype: list[int], seed: int = 42) -> float:
        """Random fitness landscape with epistasis."""
        rng = random.Random(seed)
        table: dict[tuple, float] = {}
        total = 0.0
        for i in range(self.N):
            interactions = tuple(sorted([i] + [rng.randint(0, self.N - 1)
                                               for _ in range(self.K)]))
            key = (i,) + tuple(genotype[j % self.N] for j in interactions)
            if key not in table:
                table[key] = rng.random()
            total += table[key]
        return total / self.N

    def adaptive_walk(self, n_steps: int = 20, seed: int = 0) -> list[float]:
        """Greedy adaptive walk: always move to fitter neighbor. EML-1 convergence."""
        rng = random.Random(seed)
        genotype = [rng.randint(0, 1) for _ in range(self.N)]
        trajectory = [self.fitness(genotype)]
        for _ in range(n_steps):
            best_neighbor = genotype[:]
            best_fit = self.fitness(genotype)
            for i in range(self.N):
                neighbor = genotype[:]
                neighbor[i] = 1 - neighbor[i]
                f = self.fitness(neighbor)
                if f > best_fit:
                    best_fit = f
                    best_neighbor = neighbor
            if best_neighbor == genotype:
                break
            genotype = best_neighbor
            trajectory.append(best_fit)
        return trajectory

    def ruggedness(self) -> float:
        """Landscape ruggedness ~ K/N. EML-2 (ratio)."""
        return self.K / self.N

    def analyze(self) -> dict[str, Any]:
        optima = self.expected_local_optima()
        walk = self.adaptive_walk(n_steps=15)
        return {
            "model": "NKFitnessLandscape",
            "N": self.N,
            "K": self.K,
            "expected_local_optima": round(optima, 2),
            "log_optima_structure": f"exp(N * ln(2/(K+1))) — EML-1",
            "adaptive_walk_fitness": [round(f, 4) for f in walk],
            "walk_converged_at_step": len(walk),
            "landscape_ruggedness": round(self.ruggedness(), 3),
            "eml_depth": {
                "n_optima_formula": 1,
                "adaptive_walk_convergence": 1,
                "ruggedness_ratio": 2,
                "fitness_landscape_structure": 2
            },
            "key_insight": "NK landscape: # optima = EML-1; each local basin = EML-1 exponential stability"
        }


# ---------------------------------------------------------------------------
# 2. Wright-Fisher Drift & Speciation
# ---------------------------------------------------------------------------

@dataclass
class WrightFisherDynamics:
    """Genetic drift in finite populations; speciation as EML-∞ threshold crossing."""

    population_size: int = 100
    mutation_rate: float = 0.01

    def drift_variance(self, p: float) -> float:
        """Genetic drift: Var[Δp] = p(1-p)/N. EML-2 (product of EML-1 terms)."""
        return p * (1 - p) / self.population_size

    def fixation_probability(self, s: float, p0: float = 0.01) -> float:
        """
        Kimura's fixation probability: π(p0) = (1-exp(-2Ns*p0))/(1-exp(-2Ns)).
        EML-1 (both numerator and denominator are EML-1).
        """
        Ns2 = 2 * self.population_size * s
        if abs(s) < 1e-10:
            return p0  # neutral drift
        num = 1 - math.exp(-Ns2 * p0)
        den = 1 - math.exp(-Ns2)
        if abs(den) < 1e-15:
            return p0
        return num / den

    def coalescence_time(self) -> float:
        """Expected time to MRCA: T ~ 2N generations. EML-0 (linear)."""
        return 2 * self.population_size

    def reproductive_isolation_threshold(self, divergence_t: float,
                                         mu: float = 0.001) -> float:
        """
        Genetic distance D(t) = 1 - exp(-mu*t). Speciation at D > threshold.
        EML-1 in D; the speciation event itself is EML-∞ (discontinuous split).
        """
        return 1 - math.exp(-mu * divergence_t)

    def speciation_time(self, threshold: float = 0.5, mu: float = 0.001) -> float:
        """Time to reach speciation threshold: t* = -ln(1-threshold)/mu. EML-2."""
        return -math.log(1 - threshold) / mu

    def analyze(self) -> dict[str, Any]:
        p_vals = [0.01, 0.05, 0.1, 0.5]
        s_vals = [0.0, 0.001, 0.01, 0.05]

        fixation_table = {}
        for s in s_vals:
            fixation_table[s] = {
                round(p, 2): round(self.fixation_probability(s, p), 4)
                for p in p_vals
            }

        div_times = [100, 500, 1000, 5000, 10000]
        isolation = {t: round(self.reproductive_isolation_threshold(t), 4)
                     for t in div_times}

        spec_time = self.speciation_time(threshold=0.5)

        return {
            "model": "WrightFisherDynamics",
            "population_size": self.population_size,
            "drift_variance_at_p0.5": round(self.drift_variance(0.5), 6),
            "fixation_probability_table": fixation_table,
            "coalescence_time_generations": self.coalescence_time(),
            "reproductive_isolation_vs_time": isolation,
            "speciation_time_at_threshold_0.5": round(spec_time, 1),
            "eml_depth": {
                "drift_variance": 2,
                "fixation_probability": 1,
                "reproductive_isolation": 1,
                "speciation_event": "∞"
            },
            "key_insight": "Fixation = EML-1 (Kimura formula); speciation threshold crossing = EML-∞"
        }


# ---------------------------------------------------------------------------
# 3. Punctuated Equilibrium
# ---------------------------------------------------------------------------

@dataclass
class PunctuatedEquilibrium:
    """Eldredge & Gould (1972): long stasis punctuated by rapid speciation events."""

    stasis_duration: float = 1000.0   # generations
    event_duration: float = 10.0      # generations (rapid change)
    stasis_rate: float = 0.001        # phenotypic change rate in stasis

    def stasis_phenotype(self, t: float, p0: float = 1.0) -> float:
        """
        Phenotypic change during stasis: Ornstein-Uhlenbeck mean reversion.
        p(t) ≈ p0 * exp(-stasis_rate * t). EML-1.
        """
        return p0 * math.exp(-self.stasis_rate * t)

    def punctuation_event(self, t: float, t_event: float,
                          delta_p: float = 5.0) -> float:
        """
        Rapid morphological change at t_event: sigmoid step function.
        Sharp limit → EML-∞ (non-analytic jump).
        """
        k = 10.0 / self.event_duration  # steepness
        exponent = -k * (t - t_event)
        exponent = max(-500.0, min(500.0, exponent))
        return delta_p / (1 + math.exp(exponent))

    def combined_trajectory(self, n_events: int = 3) -> list[tuple[float, float]]:
        """Full evolutionary trajectory: stasis + punctuation events."""
        total_time = self.stasis_duration * (n_events + 1)
        trajectory = []
        event_times = [self.stasis_duration * (i + 1) for i in range(n_events)]

        for i in range(200):
            t = total_time * i / 199
            p = self.stasis_phenotype(t % self.stasis_duration)
            for et in event_times:
                p += self.punctuation_event(t, et)
            trajectory.append((round(t, 1), round(p, 4)))
        return trajectory

    def information_rate(self) -> dict[str, float]:
        """
        Information generated: during stasis = low (EML-1 compression possible);
        during event = high (EML-∞ incompressible).
        """
        stasis_info = self.stasis_rate * math.log(self.stasis_duration)  # EML-2
        event_info_rate = 1.0 / self.event_duration  # EML-0 (rate)
        return {
            "stasis_info_nats": round(stasis_info, 4),
            "event_info_rate_per_gen": round(event_info_rate, 4),
            "ratio_event_to_stasis": round(event_info_rate / (stasis_info + 1e-10), 2)
        }

    def sexual_selection_runaway(self, t_vals: list[float],
                                 initial_trait: float = 0.1) -> list[float]:
        """
        Fisher's runaway: trait T(t) = T0 * exp(alpha * t). EML-1.
        Terminates when fitness cost = benefit (EML-2 balance) or EML-∞ extinction.
        """
        alpha = 0.05  # runaway rate
        return [initial_trait * math.exp(alpha * t) for t in t_vals]

    def analyze(self) -> dict[str, Any]:
        trajectory = self.combined_trajectory(n_events=2)
        sample = trajectory[::20]  # every 20th point

        runaway_times = [0, 10, 20, 30, 40, 50]
        runaway = self.sexual_selection_runaway(runaway_times)

        info = self.information_rate()

        return {
            "model": "PunctuatedEquilibrium",
            "stasis_duration_gens": self.stasis_duration,
            "event_duration_gens": self.event_duration,
            "trajectory_sample": sample[:8],
            "information_rates": info,
            "sexual_selection_runaway": {
                t: round(v, 4) for t, v in zip(runaway_times, runaway)
            },
            "eml_depth": {
                "stasis_dynamics": 1,
                "sexual_selection_runaway": 1,
                "punctuation_event": "∞",
                "information_during_stasis": 2,
                "information_during_event": "∞"
            },
            "key_insight": (
                "Stasis = EML-1 (mean reversion, exponential stability). "
                "Sexual selection runaway = EML-1 (exponential growth). "
                "Speciation/punctuation = EML-∞ (non-analytic morphological jump)."
            )
        }


# ---------------------------------------------------------------------------
# Main analysis function
# ---------------------------------------------------------------------------

def analyze_evolution_v2_eml() -> dict[str, Any]:
    nk = NKFitnessLandscape(N=10, K=2)
    wf = WrightFisherDynamics(population_size=200, mutation_rate=0.005)
    pe = PunctuatedEquilibrium(stasis_duration=1000.0, event_duration=10.0)

    return {
        "session": 132,
        "title": "Evolutionary Biology Deep II: Fitness Landscapes, Speciation & Punctuated Equilibrium",
        "eml_operator": "eml(x,y) = exp(x) - ln(y)",
        "nk_fitness_landscape": nk.analyze(),
        "wright_fisher_dynamics": wf.analyze(),
        "punctuated_equilibrium": pe.analyze(),
        "eml_depth_summary": {
            "EML-0": "Topology of genotype space, coalescence counts",
            "EML-1": "NK local optima count, adaptive walk convergence, fixation probability, stasis, runaway",
            "EML-2": "Drift variance, reproductive isolation, ruggedness ratio, stasis information",
            "EML-3": "Oscillatory population dynamics (predator-prey limit cycles)",
            "EML-∞": "Speciation threshold crossing, punctuation events, extinction (irreversible)"
        },
        "key_theorem": (
            "The EML Evolutionary Depth Theorem: "
            "All gradual evolutionary processes (drift, selection, stasis) are EML-1 or EML-2. "
            "The discrete, irreversible events of evolutionary history — speciation, extinction, "
            "punctuated equilibrium jumps — are EML-∞: they cannot be expressed as finite compositions "
            "of exp and ln over the continuous state space."
        ),
        "rabbit_hole_log": [
            "NK optima count = EML-1: same structure as Boltzmann partition function",
            "Kimura fixation = EML-1: (1-exp)/(1-exp) — ratio of two EML-1 atoms",
            "Reproductive isolation = 1-exp(-mu*t): EML-1 in time, EML-2 as depth (involves ln in inversion)",
            "Stasis = Ornstein-Uhlenbeck = EML-1 attractor",
            "Punctuation events: sharp limit of sigmoid → step function = EML-∞",
            "Sexual selection runaway = EML-1 until fitness cost triggers EML-∞ crash/speciation"
        ],
        "connections": {
            "S57_stat_mech": "Boltzmann factor structure = NK local optima count (both EML-1)",
            "S62_pde": "OU process in stasis = EML-1 (same as Ornstein-Uhlenbeck = mean-reverting SDE)",
            "S75_qft": "Phase transition in speciation = EML-∞ (same class as QCD confinement)",
            "S130_grand_synthesis_7": "Speciation is irreversible: asymmetry Δd=∞ (EML-∞ barrier)"
        }
    }


if __name__ == "__main__":
    import json
    print(json.dumps(analyze_evolution_v2_eml(), indent=2, default=str))
