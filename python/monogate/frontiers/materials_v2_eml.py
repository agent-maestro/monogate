"""
Session 138 — Materials Science Deep II: Many-Body Systems, Superconductivity & Topology

EML operator: eml(x,y) = exp(x) - ln(y)
EML depth hierarchy: 0 (topology) | 1 (equilibria) | 2 (geometry) | 3 (waves) | ∞ (singularities)

Key theorem: BCS superconductivity is EML-1 (exponential gap); Mott and topological transitions are EML-∞.
"""

from __future__ import annotations
import math
from dataclasses import dataclass
from typing import Any


# ---------------------------------------------------------------------------
# 1. BCS Superconductivity
# ---------------------------------------------------------------------------

@dataclass
class BCSSuperconductivity:
    """Bardeen-Cooper-Schrieffer (1957): phonon-mediated Cooper pairing."""

    V: float = 0.2      # BCS coupling constant (attractive)
    N0: float = 1.0     # density of states at Fermi level
    hbar_omega_D: float = 0.02  # Debye energy (eV)
    kB: float = 8.617e-5  # eV/K

    def gap_equation(self) -> float:
        """
        BCS gap: Δ = 2 ħω_D * exp(-1/(N(0)*V)).
        EML-1: exponential in -1/(N₀V).
        """
        return 2 * self.hbar_omega_D * math.exp(-1.0 / (self.N0 * self.V))

    def critical_temperature(self) -> float:
        """T_c = (2e^γ/π) * ħω_D/k_B * exp(-1/(N₀V)). EML-1."""
        gamma_euler = 0.5772
        prefactor = (2 * math.exp(gamma_euler) / math.pi) * (self.hbar_omega_D / self.kB)
        return prefactor * math.exp(-1.0 / (self.N0 * self.V))

    def condensation_energy(self) -> float:
        """E_cond = -N(0)*Δ²/2. EML-2 (square of EML-1)."""
        delta = self.gap_equation()
        return -self.N0 * (delta ** 2) / 2.0

    def superfluid_density(self, T: float, Tc: float) -> float:
        """ρ_s(T) ≈ ρ_0 * (1 - (T/Tc)⁴). EML-2 (power law in T/Tc)."""
        if T >= Tc:
            return 0.0
        return 1.0 - (T / Tc) ** 4

    def gap_vs_temperature(self, T: float, Tc: float, Delta0: float) -> float:
        """Δ(T) ≈ Δ0 * sqrt(1 - T/Tc) near Tc. EML-2."""
        if T >= Tc:
            return 0.0
        return Delta0 * math.sqrt(1.0 - T / Tc)

    def analyze(self) -> dict[str, Any]:
        delta = self.gap_equation()
        Tc = self.critical_temperature()
        E_cond = self.condensation_energy()

        T_ratios = [0.0, 0.2, 0.5, 0.8, 0.9, 0.95, 1.0]
        gap_T = {round(r, 2): round(self.gap_vs_temperature(r * Tc, Tc, delta), 6)
                 for r in T_ratios}
        rho_s = {round(r, 2): round(self.superfluid_density(r * Tc, Tc), 4)
                 for r in T_ratios}

        return {
            "model": "BCSSuperconductivity",
            "coupling_N0_V": round(self.N0 * self.V, 3),
            "gap_eV": f"{delta:.4e}",
            "critical_temperature_K": round(Tc, 4),
            "condensation_energy_eV": f"{E_cond:.4e}",
            "gap_vs_T_ratio": gap_T,
            "superfluid_density_vs_T": rho_s,
            "eml_depth": {
                "bcs_gap": 1,
                "critical_temperature": 1,
                "condensation_energy": 2,
                "gap_vs_T": 2,
                "superconducting_transition": "∞"
            },
            "key_insight": "BCS gap = EML-1 (exponential in -1/λ); superconducting transition = EML-∞"
        }


# ---------------------------------------------------------------------------
# 2. Mott Insulator & Hubbard Model
# ---------------------------------------------------------------------------

@dataclass
class MottInsulatorHubbard:
    """Hubbard model: t*hopping + U*repulsion. Mott transition at U/t ~ 12."""

    t: float = 1.0    # hopping integral (bandwidth unit)
    U: float = 8.0    # on-site repulsion
    n_sites: int = 8  # lattice sites

    def bandwidth(self) -> float:
        """W = 2z*t where z = coordination number. EML-0 (linear)."""
        z = 2  # 1D chain
        return 2 * z * self.t

    def mott_gap(self) -> float:
        """
        Mott-Hubbard gap: Δ_Mott = U - W.
        Open at U > W (insulating), zero at U = W (metallic).
        EML-0 (difference), but the transition is EML-∞.
        """
        W = self.bandwidth()
        return max(0.0, self.U - W)

    def quasiparticle_weight(self) -> float:
        """
        Z = 1 - (U/U_c)² in Brinkman-Rice approximation.
        EML-2 (quadratic). Z→0 at transition = EML-∞.
        """
        U_c = 8 * self.t  # Brinkman-Rice critical U
        ratio = self.U / U_c
        if ratio >= 1.0:
            return 0.0  # Mott insulator = EML-∞ transition
        return max(0.0, 1.0 - ratio ** 2)

    def dos_lower_hubbard_band(self, omega: float) -> float:
        """
        Semicircular DOS of lower Hubbard band. EML-2 (semicircle = √(1-x²)).
        """
        W = self.bandwidth()
        center = -self.U / 2
        x = (omega - center) / (W / 2)
        if abs(x) > 1:
            return 0.0
        return (2.0 / (math.pi * W / 2)) * math.sqrt(1 - x ** 2)

    def wigner_crystal_threshold(self) -> float:
        """
        Wigner crystal forms when r_s > r_s^*. r_s = interparticle spacing / Bohr.
        r_s^* ≈ 100 in 3D. EML-∞ transition.
        """
        return 100.0  # critical r_s for Wigner crystallization

    def analyze(self) -> dict[str, Any]:
        W = self.bandwidth()
        gap = self.mott_gap()
        Z = self.quasiparticle_weight()

        omega_vals = [-6.0, -4.0, -2.0, 0.0, 2.0, 4.0, 6.0]
        dos = {w: round(self.dos_lower_hubbard_band(w), 4) for w in omega_vals}

        U_sweep = [0, 2, 4, 6, 8, 10, 12]
        Z_sweep = {u: round(MottInsulatorHubbard(t=self.t, U=u).quasiparticle_weight(), 4)
                   for u in U_sweep}

        return {
            "model": "MottInsulatorHubbard",
            "hopping_t": self.t,
            "repulsion_U": self.U,
            "bandwidth_W": round(W, 3),
            "mott_gap": round(gap, 3),
            "quasiparticle_weight_Z": round(Z, 4),
            "lower_hubbard_band_DOS": dos,
            "Z_vs_U": Z_sweep,
            "wigner_crystal_threshold_rs": self.wigner_crystal_threshold(),
            "eml_depth": {
                "bandwidth": 0,
                "mott_gap": 0,
                "quasiparticle_weight": 2,
                "mott_transition": "∞",
                "wigner_crystal_transition": "∞"
            },
            "key_insight": "Brinkman-Rice Z = EML-2; Mott transition (Z→0) and Wigner crystal = EML-∞"
        }


# ---------------------------------------------------------------------------
# 3. Topological Phases
# ---------------------------------------------------------------------------

@dataclass
class TopologicalPhases:
    """Integer quantum Hall effect, topological insulators, Chern numbers."""

    n_bands: int = 4

    def chern_number_model(self, m: float) -> int:
        """
        Haldane model Chern number: C = 0 if |m| > 1, C = ±1 if |m| < 1.
        EML-0 (integer topological invariant).
        """
        if abs(m) < 1.0:
            return 1 if m > 0 else -1
        return 0

    def tknn_invariant(self, sigma_xy: float) -> float:
        """TKNN: σ_xy = C * e²/h. EML-0 (integer * constant)."""
        e2_over_h = 3.874e-5  # S (conductance quantum)
        return sigma_xy * e2_over_h

    def berry_phase(self, k_path_n: int) -> float:
        """
        Berry phase: γ = ∮ A·dk. For unit winding: γ = π. EML-3.
        Approximation for band with n k-points.
        """
        return math.pi * (1 - 1.0 / k_path_n)

    def topological_gap(self, m: float) -> float:
        """
        Topological gap: Δ_topo = |m| for |m| < 1, else 0. EML-0.
        Gap closes at topological transition (m = ±1) = EML-∞.
        """
        return max(0.0, 1.0 - abs(m))

    def bulk_edge_correspondence(self) -> dict[str, str]:
        """
        Bulk-boundary correspondence: bulk topology (C≠0) → edge states.
        EML-0 (integer count), but edge state energy = EML-2.
        """
        return {
            "bulk_chern_number": "EML-0 (integer invariant)",
            "n_edge_states": "EML-0 (equals |C|)",
            "edge_state_dispersion": "EML-2 (linear in k: E = v_F * k)",
            "topological_transition": "EML-∞ (gap closing = phase boundary)",
            "Z2_invariant": "EML-0 (Boolean: trivial or topological)"
        }

    def analyze(self) -> dict[str, Any]:
        m_vals = [-2.0, -1.0, -0.5, 0.0, 0.5, 1.0, 2.0]
        chern = {m: self.chern_number_model(m) for m in m_vals}
        gap = {m: round(self.topological_gap(m), 4) for m in m_vals}

        k_points = [4, 8, 16, 32, 64, 128]
        berry = {k: round(self.berry_phase(k), 6) for k in k_points}

        return {
            "model": "TopologicalPhases",
            "n_bands": self.n_bands,
            "haldane_chern_number_vs_m": chern,
            "topological_gap_vs_m": gap,
            "berry_phase_vs_n_k_points": berry,
            "bulk_edge_correspondence": self.bulk_edge_correspondence(),
            "eml_depth": {
                "chern_number": 0,
                "topological_gap": 0,
                "berry_phase": 3,
                "edge_state_dispersion": 2,
                "topological_transition": "∞"
            },
            "key_insight": "Topological invariants (Chern, Z2) = EML-0; transitions (gap closing) = EML-∞"
        }


# ---------------------------------------------------------------------------
# Main analysis function
# ---------------------------------------------------------------------------

def analyze_materials_v2_eml() -> dict[str, Any]:
    bcs = BCSSuperconductivity(V=0.25, N0=1.0, hbar_omega_D=0.025)
    mott = MottInsulatorHubbard(t=1.0, U=6.0)
    topo = TopologicalPhases(n_bands=4)

    return {
        "session": 138,
        "title": "Materials Science Deep II: BCS Superconductivity, Mott Transition & Topological Phases",
        "eml_operator": "eml(x,y) = exp(x) - ln(y)",
        "bcs_superconductivity": bcs.analyze(),
        "mott_insulator_hubbard": mott.analyze(),
        "topological_phases": topo.analyze(),
        "eml_depth_summary": {
            "EML-0": "Chern numbers, Z2 invariants, topological gap, Mott gap (integer/linear)",
            "EML-1": "BCS gap Δ=2ħω_D exp(-1/λ), critical temperature T_c",
            "EML-2": "Condensation energy (Δ²), quasiparticle weight Z, superfluid density, DOS",
            "EML-3": "Berry phase (π from winding), phonon dispersion curves",
            "EML-∞": "Superconducting transition, Mott metal-insulator transition, topological phase change, Wigner crystal"
        },
        "key_theorem": (
            "The EML Materials Depth Theorem: "
            "BCS superconductivity is EML-1 — the gap Δ = exp(-1/λ) is a single EML atom. "
            "This is the same universality class as Boltzmann, de Sitter, and PRNG recurrences. "
            "Topological invariants (Chern, Z2) are EML-0 — they are counting invariants. "
            "All phase transitions — superconducting, Mott, topological, Wigner — are EML-∞: "
            "they occur at non-analytic boundaries where the ground state changes discontinuously."
        ),
        "rabbit_hole_log": [
            "BCS gap = exp(-1/N₀V): EML-1 — single exponential with log-inverse argument",
            "T_c = (2e^γ/π)*(ħω_D/k_B)*exp(-1/λ): EML-1 (same structure as BCS gap)",
            "Condensation energy = N₀Δ²/2: EML-2 (square of EML-1 = EML-2)",
            "Chern number = integer: EML-0 (topological invariant, not computed by exp/ln)",
            "Topological transition: gap closes → EML-∞ (same as percolation, IIT criticality)",
            "Mott transition Z→0: quadratic Brinkman-Rice = EML-2, divergence = EML-∞"
        ],
        "connections": {
            "S57_stat_mech": "BCS gap = EML-1: same as Boltzmann factor (both single-exponential)",
            "S58_topology": "Chern numbers = topological invariants = EML-0 (same class)",
            "S75_qft": "Superconducting transition = QFT phase transition (EML-∞)",
            "S128_materials_deep": "Extends superconductivity from Session 128 with topology"
        }
    }


if __name__ == "__main__":
    import json
    print(json.dumps(analyze_materials_v2_eml(), indent=2, default=str))
