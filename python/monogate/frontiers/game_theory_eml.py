"""
Session 161 — Game Theory: EML Depth of Strategic Interaction

EML operator: eml(x,y) = exp(x) - ln(y)
Key theorem: Nash equilibria are EML-2 (fixed points of best-response maps);
evolutionary stable strategies are EML-3 (oscillatory replicator dynamics);
correlated equilibria and mechanism design are EML-∞ (non-computable in general).
"""
from __future__ import annotations
import math
from dataclasses import dataclass
from typing import Any


@dataclass
class NashEquilibria:
    """Nash equilibrium computation and EML depth."""

    def prisoners_dilemma(self) -> dict[str, Any]:
        """
        Payoff matrix: (C,C)=(3,3), (D,C)=(5,0), (C,D)=(0,5), (D,D)=(1,1).
        Nash: (D,D) with payoff (1,1). EML-0 (discrete argmax).
        Social optimum: (C,C) — EML-∞ gap between Nash and optimum.
        """
        matrix = {("C","C"): (3,3), ("D","C"): (5,0), ("C","D"): (0,5), ("D","D"): (1,1)}
        nash = ("D","D")
        pareto = ("C","C")
        price_of_anarchy = matrix[pareto][0] / matrix[nash][0]
        return {
            "payoff_matrix": {str(k): v for k, v in matrix.items()},
            "nash_equilibrium": nash,
            "pareto_optimum": pareto,
            "price_of_anarchy": round(price_of_anarchy, 4),
            "eml_depth_nash": 0,
            "eml_depth_gap": "∞",
            "note": "Nash = EML-0 argmax; Nash↔Pareto gap = EML-∞ (coordination failure)"
        }

    def mixed_strategy_nash(self, a: float = 3.0, b: float = 1.0,
                             c: float = 0.0, d: float = 5.0) -> dict[str, Any]:
        """
        2×2 game mixing: p* = (d-b)/(a-b-c+d). EML-0 (rational function).
        Expected payoff at Nash: EML-0.
        """
        denom = a - b - c + d
        if abs(denom) < 1e-9:
            return {"error": "no mixed strategy Nash"}
        p_star = (d - b) / denom
        p_star = max(0.0, min(1.0, p_star))
        q_star = (d - c) / denom
        q_star = max(0.0, min(1.0, q_star))
        expected = p_star * q_star * a + p_star * (1-q_star) * b + \
                   (1-p_star) * q_star * c + (1-p_star) * (1-q_star) * d
        return {
            "p_star": round(p_star, 6),
            "q_star": round(q_star, 6),
            "expected_payoff": round(expected, 6),
            "eml_depth": 0
        }

    def nash_complexity(self) -> dict[str, str]:
        """
        PPAD-completeness: finding Nash in 2-player general game is PPAD-complete.
        Equivalent complexity to finding Brouwer fixed point. EML-∞.
        """
        return {
            "2player_zero_sum": "EML-2 (linear programming)",
            "2player_general": "PPAD-complete (EML-∞)",
            "n_player": "PPAD-complete (EML-∞)",
            "correlated_equilibrium": "EML-2 (linear program)",
            "note": "Nash computation = EML-∞; correlated equilibrium = EML-2 (tractable)"
        }

    def analyze(self) -> dict[str, Any]:
        pd = self.prisoners_dilemma()
        mixed = self.mixed_strategy_nash()
        complexity = self.nash_complexity()
        return {
            "model": "NashEquilibria",
            "prisoners_dilemma": pd,
            "mixed_strategy": mixed,
            "nash_complexity": complexity,
            "eml_depth": {"pure_nash": 0, "mixed_nash": 0,
                          "nash_computation": "∞", "correlated_equilibrium": 2},
            "key_insight": "Nash equilibria = EML-0 (argmax); computing them = EML-∞ (PPAD); CE = EML-2"
        }


@dataclass
class ReplicatorDynamics:
    """Evolutionary game theory — replicator equation and EML-3 oscillations."""

    def replicator_fitness(self, freq: list[float], payoffs: list[list[float]]) -> list[float]:
        """
        f_i(x) = Σ_j A_{ij} x_j. EML-0 (linear).
        Mean fitness: f̄ = Σ_i x_i f_i. EML-0.
        """
        n = len(freq)
        fitness = []
        for i in range(n):
            fi = sum(payoffs[i][j] * freq[j] for j in range(n))
            fitness.append(fi)
        mean = sum(freq[i] * fitness[i] for i in range(n))
        return fitness, mean

    def replicator_step(self, freq: list[float], payoffs: list[list[float]],
                        dt: float = 0.1) -> list[float]:
        """
        ẋ_i = x_i(f_i - f̄). EML-2 (quadratic: x_i × linear).
        """
        fitness, mean = self.replicator_fitness(freq, payoffs)
        new_freq = [max(0.0, freq[i] + dt * freq[i] * (fitness[i] - mean))
                    for i in range(len(freq))]
        total = sum(new_freq) + 1e-12
        return [x / total for x in new_freq]

    def rock_paper_scissors(self, n_steps: int = 30) -> dict[str, Any]:
        """
        RPS payoff matrix: antisymmetric. Replicator has periodic orbit (EML-3).
        Center frequency = (1/3, 1/3, 1/3). EML-0.
        """
        payoffs = [[0, -1, 1], [1, 0, -1], [-1, 1, 0]]
        freq = [0.4, 0.3, 0.3]
        trajectory = [freq[:]]
        for _ in range(n_steps):
            freq = self.replicator_step(freq, payoffs, dt=0.05)
            trajectory.append([round(x, 4) for x in freq])
        return {
            "payoff_antisymmetric": True,
            "center_equilibrium": [round(1/3, 4)] * 3,
            "initial_freq": trajectory[0],
            "final_freq": trajectory[-1],
            "orbit_type": "periodic (EML-3)",
            "eml_depth": 3
        }

    def hawk_dove_ess(self, V: float = 2.0, C: float = 6.0) -> dict[str, Any]:
        """
        Hawk-Dove: ESS p* = V/C. EML-0.
        Payoffs: HH=(V-C)/2, HD=V, DH=0, DD=V/2.
        """
        ess = V / C
        payoffs_hawk = [0.5 * (V - C), V]
        payoffs_dove = [0.0, 0.5 * V]
        return {
            "V": V, "C": C,
            "ess_hawk_fraction": round(ess, 4),
            "payoffs_hawk": payoffs_hawk,
            "payoffs_dove": payoffs_dove,
            "eml_depth_ess": 0,
            "eml_depth_dynamics": 2
        }

    def analyze(self) -> dict[str, Any]:
        rps = self.rock_paper_scissors()
        hd = self.hawk_dove_ess()
        payoffs_pd = [[3,0],[5,1]]
        freq_pd = [0.5, 0.5]
        pd_trajectory = [freq_pd[:]]
        for _ in range(20):
            freq_pd = self.replicator_step(freq_pd, payoffs_pd)
            pd_trajectory.append([round(x, 4) for x in freq_pd])
        return {
            "model": "ReplicatorDynamics",
            "rock_paper_scissors": rps,
            "hawk_dove_ess": hd,
            "pd_replicator_final": pd_trajectory[-1],
            "eml_depth": {"replicator_step": 2, "rps_orbit": 3,
                          "ess": 0, "pd_convergence": 2},
            "key_insight": "RPS replicator = EML-3 (cyclic orbit); ESS = EML-0; PD convergence = EML-2"
        }


@dataclass
class MechanismDesign:
    """Vickrey-Clarke-Groves, revelation principle, and EML-∞ impossibility."""

    def vickrey_auction(self, bids: list[float]) -> dict[str, Any]:
        """
        Vickrey (second-price): winner pays 2nd-highest bid. Dominant strategy = truthful.
        Revenue = 2nd-price. EML-0 (sorting).
        """
        if len(bids) < 2:
            return {"error": "need ≥ 2 bidders"}
        sorted_bids = sorted(bids, reverse=True)
        winner_idx = bids.index(sorted_bids[0])
        payment = sorted_bids[1]
        return {
            "bids": bids,
            "winner": winner_idx,
            "payment": round(payment, 4),
            "social_welfare": round(sorted_bids[0], 4),
            "eml_depth": 0,
            "truthful": True
        }

    def gibbard_satterthwaite(self) -> dict[str, str]:
        """
        Gibbard-Satterthwaite: any non-dictatorial voting rule is manipulable.
        EML-∞: the theorem shows truthful revelation is generically EML-∞ (impossible).
        """
        return {
            "theorem": "Any non-dictatorial, onto voting rule is manipulable",
            "eml_depth_theorem": "∞",
            "implication": "Strategy-proof mechanisms are EML-∞ rare (only Vickrey + variations)",
            "arrow_impossibility": "EML-∞: no social welfare function satisfies all Arrow axioms",
            "note": "Impossibility theorems = EML-∞ (non-existence proofs)"
        }

    def myerson_revenue(self, n_bidders: int, value_distribution: str = "uniform") -> float:
        """
        Myerson optimal auction: virtual valuation φ(v) = v - (1-F(v))/f(v).
        For uniform [0,1]: φ(v) = 2v - 1. EML-0.
        Optimal reserve price: φ(r) = 0 ⟹ r = 1/2. EML-0.
        Expected revenue (n bidders, uniform): (n-1)/(n+1). EML-0.
        """
        if value_distribution == "uniform":
            revenue = (n_bidders - 1) / (n_bidders + 1)
            reserve = 0.5
            return round(revenue, 6)
        return 0.0

    def analyze(self) -> dict[str, Any]:
        bids_test = [3.5, 2.1, 4.8, 1.9]
        vcg = self.vickrey_auction(bids_test)
        gs = self.gibbard_satterthwaite()
        revenues = {n: self.myerson_revenue(n) for n in [1, 2, 3, 5, 10, 100]}
        return {
            "model": "MechanismDesign",
            "vickrey_auction": vcg,
            "gibbard_satterthwaite": gs,
            "myerson_revenue_by_n": revenues,
            "eml_depth": {"vickrey": 0, "myerson_revenue": 0,
                          "gibbard_satterthwaite": "∞", "arrow_impossibility": "∞"},
            "key_insight": "Vickrey/Myerson = EML-0 (sorting); G-S impossibility = EML-∞"
        }


def analyze_game_theory_eml() -> dict[str, Any]:
    nash = NashEquilibria()
    replicator = ReplicatorDynamics()
    mechanism = MechanismDesign()
    return {
        "session": 161,
        "title": "Game Theory: EML Depth of Strategic Interaction",
        "eml_operator": "eml(x,y) = exp(x) - ln(y)",
        "nash_equilibria": nash.analyze(),
        "replicator_dynamics": replicator.analyze(),
        "mechanism_design": mechanism.analyze(),
        "eml_depth_summary": {
            "EML-0": "Pure/mixed Nash (argmax), ESS (V/C), Vickrey payment, Myerson revenue",
            "EML-1": "Not prominent in strategic games",
            "EML-2": "Correlated equilibrium (LP), replicator dynamics (quadratic), PD convergence",
            "EML-3": "Rock-Paper-Scissors replicator (cyclic orbit = EML-3 oscillation)",
            "EML-∞": "Nash computation (PPAD), Gibbard-Satterthwaite, Arrow impossibility"
        },
        "key_theorem": (
            "The EML Game Theory Depth Theorem: "
            "Nash equilibria (as fixed points) are EML-0 — argmax operations. "
            "Computing them is EML-∞ (PPAD-complete). "
            "Correlated equilibria are EML-2 (linear program). "
            "Replicator dynamics for symmetric games are EML-2; for antisymmetric (RPS) EML-3. "
            "All social choice impossibility theorems (Arrow, G-S) are EML-∞: "
            "they prove non-existence of EML-finite mechanisms that satisfy normative axioms."
        ),
        "rabbit_hole_log": [
            "Nash equilibrium = EML-0 (argmax); same depth as sorting, counting",
            "RPS replicator orbit = EML-3: cyclic oscillation (same as Lotka-Volterra, gravity waves)",
            "Correlated equilibrium = EML-2: Linear program over joint distributions",
            "PPAD = EML-∞: computing Nash = same complexity as Brouwer fixed point",
            "Arrow impossibility = EML-∞: non-existence theorems live at EML-∞ (like Gödel)"
        ],
        "connections": {
            "S142_evolution_v3": "RPS replicator orbit = EML-3: same as S142 evolutionary cycling",
            "S139_foundations_v2": "Arrow impossibility = EML-∞: same class as Gödel/CH undecidability",
            "S158_cellular_automata": "PPAD-completeness = EML-∞ computation class (same as Turing-complete)"
        }
    }


if __name__ == "__main__":
    import json
    print(json.dumps(analyze_game_theory_eml(), indent=2, default=str))
