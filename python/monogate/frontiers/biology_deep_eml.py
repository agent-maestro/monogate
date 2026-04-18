"""
Session 94 — Biology Deep: Morphogenesis, Evolution & Genetic Regulatory Networks

Turing patterns, evolutionary game theory, gene regulatory networks, and the EML depth
of biological self-organization. Key test: do biological models reduce to known EML classes?

Key theorem: Turing instability arises at the boundary between EML-3 (oscillatory activation)
and EML-∞ (spatial chaos). The activator-inhibitor ratio threshold is EML-2.
Evolutionary game theory payoff matrices are EML-1 (exponential fitness).
Gene regulatory Boolean networks: EML-0 per state, EML-∞ for the attractor landscape.
"""

from __future__ import annotations
import math, json
from dataclasses import dataclass, field


EML_INF = float("inf")


@dataclass
class TuringInstability:
    """
    Turing (1952) morphogenesis: reaction-diffusion system.
    ∂u/∂t = D_u·∇²u + f(u,v)
    ∂v/∂t = D_v·∇²v + g(u,v)

    Turing instability condition: D_v/D_u > (b_c/a_c)² (diffusion ratio)
    where a_c, b_c are Jacobian elements at homogeneous steady state.

    EML structure:
    - Homogeneous steady state (u*,v*): EML-1 (fixed point = EML-1 if nonlinear, EML-0 if linear)
    - Stability threshold D_v/D_u > threshold: EML-2 (rational function of Jacobian entries)
    - Most unstable mode k_c² = √(a₁₁/D_u·a₂₂/D_v): EML-2 (geometric mean)
    - Pattern wavelength λ = 2π/k_c: EML-3 (π appears via 2π/k)
    - Pattern amplitude: EML-3 (cos(k_c·x) = EML-3 spatial oscillation)
    - Far from threshold: spatiotemporal chaos = EML-∞
    """

    def stability_analysis(self, a11: float, a12: float, a21: float, a22: float,
                            Du: float, Dv: float) -> dict:
        """Linear stability of RD system at (u*, v*)."""
        trace = a11 + a22
        det = a11 * a22 - a12 * a21
        # Turing instability requires det > 0, trace < 0 (stable hom state)
        # AND diffusion-driven instability: Dv*a11 + Du*a22 > 0
        turing_condition = Dv * a11 + Du * a22
        is_turing_unstable = det > 0 and trace < 0 and turing_condition > 0
        # Critical wavenumber
        if Du > 0 and Dv > 0 and det > 0:
            k_c_sq = math.sqrt(det / (Du * Dv))
        else:
            k_c_sq = 0
        wavelength = 2 * math.pi / k_c_sq**0.5 if k_c_sq > 0 else float("inf")
        return {
            "jacobian": {"a11": a11, "a12": a12, "a21": a21, "a22": a22},
            "D_u": Du, "D_v": Dv,
            "trace": round(trace, 6),
            "det": round(det, 6),
            "turing_condition": round(turing_condition, 6),
            "turing_unstable": is_turing_unstable,
            "critical_wavenumber_sq": round(k_c_sq, 6),
            "pattern_wavelength": round(wavelength, 4) if wavelength < 1e6 else "∞",
            "eml_k_c": 2,
            "eml_wavelength": 3,
            "reason": "k_c = √(det/(D_u·D_v)): EML-2; wavelength = 2π/k_c: EML-3 (π appears)",
        }

    def gierer_meinhardt(self) -> dict:
        """Gierer-Meinhardt: f(u,v)=u²/v-u, g(u,v)=u²-v. Jacobian at (1,1): a11=1,a12=-1,a21=2,a22=-1."""
        return {
            "model": "Gierer-Meinhardt activator-inhibitor",
            "u_star": 1.0, "v_star": 1.0,
            "analysis": self.stability_analysis(1, -1, 2, -1, 0.01, 1.0),
            "biological_example": "Animal stripe/spot patterns (zebrafish, leopard)",
        }

    def to_dict(self) -> dict:
        return {
            "turing_mechanism": "Reaction-diffusion: short-range activation, long-range inhibition",
            "gierer_meinhardt": self.gierer_meinhardt(),
            "eml_near_threshold": 3,
            "eml_far_threshold": EML_INF,
            "eml_insight": "Turing instability threshold is EML-2; patterns are EML-3; spatiotemporal chaos beyond threshold is EML-∞",
        }


@dataclass
class EvolutionaryGameTheory:
    """
    Replicator dynamics: ṗ_i = p_i·[(Ap)_i - p·Ap]

    EML structure:
    - Payoff matrix A: EML-0 (matrix of numbers)
    - Fitness (Ap)_i: EML-2 (linear map of state = EML-2)
    - Replicator equation: polynomial ODE in p → Nash equilibria = EML-1
    - Lotka-Volterra connection: replicator = LV in simplex → EML-1 fixed points
    - Rock-Paper-Scissors (3-strategy cyclic): EML-3 (cyclic orbit = EML-3 oscillation)
    """

    GAMES = {
        "hawk_dove": {
            "A": [[0, 2], [0, 1]],  # simplified
            "nash": "mixed strategy p* = (1/2, 1/2)",
            "eml_nash": 2,
        },
        "prisoners_dilemma": {
            "A": [[3, 0], [5, 1]],
            "nash": "defect-defect (dominant strategy)",
            "eml_nash": 0,
        },
        "rps": {
            "A": [[0, -1, 1], [1, 0, -1], [-1, 1, 0]],
            "nash": "uniform (1/3,1/3,1/3)",
            "eml_nash": 2,
        },
    }

    def replicator_rps(self, n_steps: int = 30) -> list[dict]:
        """Rock-Paper-Scissors replicator dynamics on simplex."""
        p = [0.4, 0.4, 0.2]
        A = [[0, -1, 1], [1, 0, -1], [-1, 1, 0]]
        dt = 0.1
        results = []
        for i in range(n_steps):
            Ap = [sum(A[k][j] * p[j] for j in range(3)) for k in range(3)]
            avg = sum(p[k] * Ap[k] for k in range(3))
            dp = [p[k] * (Ap[k] - avg) for k in range(3)]
            p = [max(0, p[k] + dp[k] * dt) for k in range(3)]
            total = sum(p)
            p = [x / total for x in p]
            if i % 5 == 0:
                results.append({
                    "step": i,
                    "p_R": round(p[0], 4),
                    "p_P": round(p[1], 4),
                    "p_S": round(p[2], 4),
                    "distance_from_nash": round(sum(abs(x - 1/3) for x in p), 4),
                })
        return results

    def to_dict(self) -> dict:
        return {
            "games": self.GAMES,
            "rps_dynamics": self.replicator_rps(),
            "eml_payoff_matrix": 0,
            "eml_nash_equilibrium": 2,
            "eml_rps_orbit": 3,
            "eml_replicator_equation": 1,
            "reason": "Nash = fixed point of replicator (EML-2); RPS = cyclic orbit (EML-3); payoff = EML-0",
        }


@dataclass
class GeneRegulatoryNetwork:
    """
    Gene regulatory network (GRN): Boolean network model.
    Each gene g_i ∈ {0,1} updates: g_i(t+1) = f_i(g_1,...,g_n)

    EML structure:
    - Gene state per node: EML-0 (binary)
    - Boolean update function f_i: EML-0 (truth table)
    - State space: 2^n states = EML-0 (integer)
    - Attractor (fixed point or limit cycle): EML-2 (periodic orbit in discrete space)
    - Attractor basin: EML-0 (set of states)
    - Attractor landscape (all attractors): EML-∞ (no formula for generic network)
    - ODE limit (continuous GRN): Hill functions = EML-2; oscillations = EML-3
    """

    def boolean_network_3genes(self) -> dict:
        """Simple 3-gene network: g1→g2→g3⊣g1."""
        n = 3
        n_states = 2**n
        # Update rules: g1_new = NOT g3, g2_new = g1, g3_new = g2
        def update(state: tuple) -> tuple:
            g1, g2, g3 = state
            return (1 - g3, g1, g2)
        states = list(range(n_states))
        trajectory = {}
        for s in states:
            bits = ((s >> 2) & 1, (s >> 1) & 1, s & 1)
            next_bits = update(bits)
            next_s = next_bits[0] * 4 + next_bits[1] * 2 + next_bits[2]
            trajectory[s] = next_s
        # Find attractors
        attractors = []
        visited = set()
        for start in states:
            if start in visited:
                continue
            path = []
            s = start
            while s not in path:
                path.append(s)
                s = trajectory[s]
            if s in path:
                cycle_start = path.index(s)
                cycle = path[cycle_start:]
                if tuple(cycle) not in [tuple(a) for a in attractors]:
                    attractors.append(cycle)
            visited.update(path)
        return {
            "n_genes": n,
            "n_states": n_states,
            "update_rules": "g1←¬g3, g2←g1, g3←g2",
            "attractors": attractors,
            "eml_per_state": 0,
            "eml_attractor": 2,
            "eml_landscape": EML_INF,
            "reason": "Each state = EML-0; periodic attractor = EML-2; full landscape (all attractors) = EML-∞",
        }

    def hill_function_ode(self) -> dict:
        """Continuous GRN: Hill activation f(x) = x^n/(K^n + x^n)."""
        return {
            "hill_function": "f(x) = x^n/(K^n + x^n)",
            "eml": 2,
            "reason": "Rational function of x^n = EML-2 (rational of power = EML-2)",
            "limit_n_inf": "Step function Θ(x-K) — EML-∞ in the limit n→∞",
            "ode_with_hill": "ẋ = f(x) - γx: EML-2 ODE (rational RHS)",
            "oscillation": "Toggle switch bistability: EML-2 (saddle-node bifurcation at EML-2 threshold)",
        }

    def to_dict(self) -> dict:
        return {
            "boolean_network": self.boolean_network_3genes(),
            "hill_function": self.hill_function_ode(),
            "eml_boolean_state": 0,
            "eml_boolean_attractor": 2,
            "eml_continuous_grn": 2,
            "eml_ode_oscillation": 3,
        }


def analyze_biology_deep_eml() -> dict:
    turing = TuringInstability()
    egt = EvolutionaryGameTheory()
    grn = GeneRegulatoryNetwork()
    return {
        "session": 94,
        "title": "Biology Deep: Morphogenesis, Evolution & Genetic Regulatory Networks",
        "key_theorem": {
            "theorem": "EML Biology Depth Theorem",
            "statement": (
                "Biological self-organization follows the EML depth hierarchy: "
                "gene states are EML-0, Hill functions and attractor thresholds are EML-2, "
                "Turing patterns and oscillations are EML-3, and complex attractor landscapes "
                "are EML-∞. Nash equilibria in evolutionary games are EML-2 (rational strategies). "
                "Rock-Paper-Scissors cyclic dynamics are EML-3. "
                "The Turing instability threshold (diffusion ratio) is EML-2; "
                "the resulting spatial pattern wavelength is EML-3 (involves π)."
            ),
        },
        "turing_morphogenesis": turing.to_dict(),
        "evolutionary_game_theory": egt.to_dict(),
        "gene_regulatory_networks": grn.to_dict(),
        "eml_depth_summary": {
            "EML-0": "Gene expression states {0,1}; payoff matrix entries; discrete cell fates",
            "EML-1": "Population growth exp(rt); fitness landscape max-entropy fixed point",
            "EML-2": "Hill function x^n/(K^n+x^n); Nash equilibrium; Turing instability ratio; ODE steady states",
            "EML-3": "Turing spatial patterns cos(k·x); RPS cyclic orbit; GRN oscillations; circadian rhythm",
            "EML-∞": "Generic GRN attractor landscape; spatiotemporal chaos beyond Turing threshold; ecological chaos",
        },
        "rabbit_hole_log": [
            "Turing's insight was EML-3: the homogeneous state (EML-1) destabilizes into spatial EML-3 patterns via a EML-2 threshold (diffusion ratio). The biology encodes the EML depth transition EML-1 → EML-3 via EML-2 mechanism.",
            "Hill functions approach step functions as n→∞: EML-2 → EML-∞ in the sharp switching limit. This is the biological version of the EML-∞ phase transition: gene expression switches become EML-∞ sharp thresholds.",
            "Evolutionary game theory Nash equilibria: mixed strategy = EML-2 (rational frequency). But evolutionary dynamics can be chaotic (EML-∞) for general n-strategy games — Lotka-Volterra chaos in high dimensions.",
        ],
        "connections": {
            "to_session_57": "Session 57: phase transitions = EML-∞. Session 94: Turing instability threshold = EML-2 → EML-3 pattern transition",
            "to_session_60": "Nash equilibrium = max-entropy = EML-2. Same as Fisher information geometry of payoff landscape",
        },
    }


if __name__ == "__main__":
    print(json.dumps(analyze_biology_deep_eml(), indent=2, default=str))
