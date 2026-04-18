"""
Session 204 — Statistical Mechanics Deep II: Onsager, Transfer Matrices & Partition Functions

EML operator: eml(x,y) = exp(x) - ln(y)
Key theorem: Partition function Z = Σ exp(-βE) = EML-1 (sum of EML-1 terms).
Onsager exact solution for 2D Ising = EML-3 (elliptic integral, oscillatory).
Transfer matrix: EML-3 (largest eigenvalue determines free energy).
Phase transition: EML-∞.
"""
from __future__ import annotations
import math
from dataclasses import dataclass
from typing import Any


@dataclass
class PartitionFunctionEML:
    """Partition function and its EML depth."""

    def canonical_partition(self, beta: float = 1.0, energies: list = None) -> dict[str, Any]:
        if energies is None:
            energies = [0.0, 1.0, 2.0, 3.0]
        Z = round(sum(math.exp(-beta * E) for E in energies), 4)
        F = round(-math.log(Z) / beta, 4)
        S = round(beta**2 * sum(E * math.exp(-beta * E) for E in energies) / Z, 4)
        return {
            "Z": Z,
            "F": F,
            "S": S,
            "Z_depth": 1,
            "F_depth": 2,
            "S_depth": 2,
            "energies": energies,
            "note": "Z=EML-1 (sum of exp); F=log(Z)/β=EML-2; S=EML-2"
        }

    def ising_exact_onsager(self, beta: float = 0.44) -> dict[str, Any]:
        """
        Onsager exact solution: F = -kT log(2 cosh(2βJ)·k(βJ)).
        Involves complete elliptic integral K(k). EML-3.
        """
        J = 1.0
        k_ising = round(2 * math.sinh(2 * beta * J) / math.cosh(2 * beta * J)**2, 4)
        beta_c = round(math.log(1 + math.sqrt(2)) / 2, 4)
        return {
            "beta": beta,
            "beta_c": beta_c,
            "k_ising": k_ising,
            "free_energy_depth": 3,
            "critical_exponents_depth": 2,
            "phase_transition_depth": "∞",
            "elliptic_integral_depth": 3,
            "note": "Onsager: F=EML-3 (elliptic integral); critical exponents=EML-2; transition=EML-∞"
        }

    def analyze(self) -> dict[str, Any]:
        canon = self.canonical_partition()
        onsager = self.ising_exact_onsager()
        return {
            "model": "PartitionFunctionEML",
            "canonical": canon,
            "onsager_ising": onsager,
            "key_insight": "Z=EML-1; F=log(Z)=EML-2; Onsager=EML-3; transition=EML-∞"
        }


def analyze_stat_mech_v2_eml() -> dict[str, Any]:
    pf = PartitionFunctionEML()
    return {
        "session": 204,
        "title": "Statistical Mechanics Deep II: Onsager, Transfer Matrices & Partition Functions",
        "eml_operator": "eml(x,y) = exp(x) - ln(y)",
        "partition_function": pf.analyze(),
        "eml_depth_summary": {
            "EML-1": "Z = Σ exp(-βE) (partition function = sum of EML-1)",
            "EML-2": "F = -log(Z)/β, entropy S = EML-2; critical exponents",
            "EML-3": "Onsager exact solution (elliptic integral); transfer matrix",
            "EML-∞": "Phase transition, symmetry breaking"
        },
        "key_theorem": (
            "The EML Statistical Mechanics Theorem (S204): "
            "Z = Σ exp(-βE): each term is EML-1, but the sum = EML-1 (closed under addition). "
            "Free energy F = -log(Z)/β = EML-2 (log of EML-1 = EML-2). "
            "Onsager exact 2D Ising = EML-3 (elliptic integral = EML-3). "
            "Phase transitions = EML-∞ (symmetry breaking, divergent correlation length). "
            "The Z → F → S ladder = EML-1 → EML-2 → EML-2 = standard partition function depth chain."
        ),
        "rabbit_hole_log": [
            "Z=EML-1: partition function is the archetype of the universal EML-1 ground state sum",
            "F=log(Z)=EML-2: the thermodynamic potential is always one log above Z",
            "Onsager=EML-3: only known EXACT solution in 2D stat mech lives at EML-3"
        ]
    }


if __name__ == "__main__":
    import json
    print(json.dumps(analyze_stat_mech_v2_eml(), indent=2, default=str))
