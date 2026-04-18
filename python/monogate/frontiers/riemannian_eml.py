"""
riemannian_eml.py — EML Complexity in Riemannian Geometry & General Relativity.

Session 63 findings:
  - Metric tensor g_{μν}: EML depth = depth of component functions
  - Christoffel symbols: same EML depth as metric (derivatives preserve depth)
  - Schwarzschild metric: components 1-2M/r → EML-2 (rational in r)
  - Singularity at r=0: 1/r² divergence → EML-inf there
  - Geodesic equation: EML depth = depth(Γ)
  - Hawking temperature T_H = ħc³/(8πGMk_B): formula EML-1 (∝1/M), derivation EML-3
  - Gravitational waves: h ∝ exp(iω(t-r/c))/r → EML-1 (carrier) × EML-2 (1/r envelope)
  - Penrose singularity: metric → EML-inf (non-smooth)
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Callable, Sequence

import numpy as np

__all__ = [
    "SchwarzschildMetric",
    "GeodesicEML",
    "HawkingRadiation",
    "GravitationalWaves",
    "RiemannianEMLAnalysis",
    "GR_EML_TAXONOMY",
    "analyze_riemannian_eml",
]

# ── EML Taxonomy ─────────────────────────────────────────────────────────────

GR_EML_TAXONOMY: dict[str, dict] = {
    "flat_metric": {
        "formula": "g_{μν} = diag(-1,1,1,1)  (Minkowski)",
        "eml_depth": 0,
        "reason": "Constant components: EML-0.",
    },
    "schwarzschild_metric": {
        "formula": "ds² = -(1-2M/r)dt² + (1-2M/r)^{-1}dr² + r²dΩ²",
        "eml_depth": 2,
        "reason": "Component 1-2M/r: rational in r → EML-2. Inverse also rational → EML-2.",
    },
    "christoffel_schwarzschild": {
        "formula": "Γ^r_{tt} = M(r-2M)/r³, etc.",
        "eml_depth": 2,
        "reason": "Derivatives and products of EML-2 metric components → EML-2.",
    },
    "geodesic_equation": {
        "formula": "ẍ^ρ + Γ^ρ_{μν}ẋ^μẋ^ν = 0",
        "eml_depth": 2,
        "reason": "EML depth = depth(Γ) = EML-2 for Schwarzschild.",
    },
    "hawking_temperature": {
        "formula": "T_H = ħc³/(8πGMk_B)",
        "eml_depth_formula": 1,
        "eml_depth_derivation": 3,
        "reason": (
            "Formula: T_H = const/M → EML-1 (rational in M, or constant×1/M). "
            "Derivation: involves erf-like thermal Green's function → EML-3."
        ),
    },
    "gravitational_waves": {
        "formula": "h_{μν} ∝ exp(iω(t-r/c))/r",
        "eml_depth": 2,
        "reason": "EML-1 carrier × EML-2 (1/r) envelope = EML-2 overall.",
    },
    "singularity_at_origin": {
        "formula": "Kretschner scalar K = 48M²/r⁶ → ∞ as r→0",
        "eml_depth": "inf",
        "reason": "1/r⁶ diverges: metric/curvature becomes EML-inf at r=0.",
    },
    "event_horizon": {
        "formula": "r_s = 2GM/c²  (Schwarzschild radius)",
        "eml_depth": 0,
        "reason": "r_s is a constant (given M): EML-0. Metric has coordinate singularity here.",
    },
}

# Physical constants (geometric units where c=G=1)
_G = 1.0
_C = 1.0
_HBAR = 1.0
_KB = 1.0


# ── Schwarzschild Metric ──────────────────────────────────────────────────────

@dataclass
class SchwarzschildMetric:
    """
    Schwarzschild solution: ds² = -(1-2M/r)dt² + (1-2M/r)^{-1}dr² + r²dΩ².
    M = mass of central body (geometric units: G=c=1).
    """

    mass: float = 1.0  # geometric units

    @property
    def schwarzschild_radius(self) -> float:
        """r_s = 2GM/c² = 2M in geometric units."""
        return 2.0 * self.mass

    def g_tt(self, r: float) -> float:
        """g_{tt} = -(1 - 2M/r). EML-2 (rational in r)."""
        if r <= 0:
            return float("-inf")
        return -(1.0 - 2.0 * self.mass / r)

    def g_rr(self, r: float) -> float:
        """g_{rr} = (1 - 2M/r)^{-1}. EML-2 (rational in r)."""
        denom = 1.0 - 2.0 * self.mass / r
        if abs(denom) < 1e-12:
            return float("inf")
        return 1.0 / denom

    def g_theta_theta(self, r: float) -> float:
        """g_{θθ} = r². EML-0 (polynomial)."""
        return r ** 2

    def christoffel_r_tt(self, r: float) -> float:
        """Γ^r_{tt} = M(r-2M)/r³. EML-2 (rational)."""
        if r <= 0:
            return 0.0
        return self.mass * (r - 2.0 * self.mass) / r ** 3

    def christoffel_t_tr(self, r: float) -> float:
        """Γ^t_{tr} = M/(r(r-2M)). EML-2 (rational)."""
        denom = r * (r - 2.0 * self.mass)
        if abs(denom) < 1e-12:
            return float("inf")
        return self.mass / denom

    def christoffel_r_rr(self, r: float) -> float:
        """Γ^r_{rr} = -M/(r(r-2M)). EML-2."""
        denom = r * (r - 2.0 * self.mass)
        if abs(denom) < 1e-12:
            return float("inf")
        return -self.mass / denom

    def christoffel_r_theta_theta(self, r: float) -> float:
        """Γ^r_{θθ} = -(r-2M). EML-2 (rational)."""
        return -(r - 2.0 * self.mass)

    def kretschner_scalar(self, r: float) -> float:
        """K = 48M²/r⁶. Diverges at r=0 → EML-inf at singularity."""
        if r <= 0:
            return float("inf")
        return 48.0 * self.mass ** 2 / r ** 6

    def photon_sphere_radius(self) -> float:
        """Photon sphere: r_ps = 3M (circular photon orbit)."""
        return 3.0 * self.mass

    def innermost_stable_orbit(self) -> float:
        """ISCO: r_ISCO = 6M (for massive particles)."""
        return 6.0 * self.mass

    def eml_depth_metric(self) -> int:
        return 2  # rational components

    def eml_depth_singularity(self) -> str:
        return "inf"


# ── Geodesic Equations ────────────────────────────────────────────────────────

@dataclass
class GeodesicEML:
    """
    Geodesic equation in Schwarzschild spacetime.

    ẍ^ρ + Γ^ρ_{μν}ẋ^μẋ^ν = 0

    EML depth = depth(Γ) = EML-2 (for Schwarzschild).

    Circular orbits: r=const requires Γ^r_{μν}ẋ^μẋ^ν = 0.
    → photon: r = 3M; massive particle: r = 6M (ISCO).
    """

    metric: SchwarzschildMetric = field(default_factory=SchwarzschildMetric)

    def effective_potential(self, r: float, L: float, m: float = 1.0) -> float:
        """
        Effective potential for radial motion:
        V_eff(r) = -(1-2M/r)·(m² + L²/r²)
        where L = angular momentum.
        """
        M = self.metric.mass
        if r <= 0:
            return float("-inf")
        return -(1.0 - 2.0 * M / r) * (m ** 2 + L ** 2 / r ** 2)

    def circular_orbit_radius(self, L: float, massive: bool = True) -> float:
        """
        Radius of circular orbit: dV_eff/dr = 0.
        For massless: r = 3M (photon sphere).
        For massive: r = 6M (ISCO at minimum).
        """
        M = self.metric.mass
        if not massive:
            return 3.0 * M  # photon sphere
        return 6.0 * M  # ISCO (approx for equatorial)

    def orbital_period(self, r: float) -> float:
        """
        Orbital period T = 2π√(r³/M) (from Kepler-like relation).
        """
        return 2.0 * math.pi * math.sqrt(r ** 3 / self.metric.mass)

    def geodesic_rhs(self, r: float, dr_dt: float,
                     theta: float = math.pi / 2.0,
                     L: float = 3.46) -> dict[str, float]:
        """
        Right-hand side of geodesic equations (equatorial, θ=π/2).
        Returns accelerations.
        """
        M = self.metric.mass
        if r <= 2.0 * M + 1e-6:
            return {"d2r_dt2": 0.0, "d2phi_dt2": 0.0}

        # Simplified: Newtonian limit for illustration
        # d²r/dt² = -M/r² + L²/r³ (approximately)
        d2r = -M / r ** 2 + L ** 2 / r ** 3
        return {
            "d2r_dt2": d2r,
            "christoffel_r_tt": self.metric.christoffel_r_tt(r),
            "r": r,
        }

    def eml_depth(self) -> int:
        return 2


# ── Hawking Radiation ─────────────────────────────────────────────────────────

@dataclass
class HawkingRadiation:
    """
    Hawking temperature T_H = ħc³/(8πGMk_B).

    In geometric units (G=c=ħ=k_B=1): T_H = 1/(8πM).

    FORMULA: EML-1 in M (T_H ∝ 1/M = rational inverse of mass).
    DERIVATION: involves thermal Green's function similar to erf → EML-3.

    KEY EML DISTINCTION: T_H = 1/(8πM) has EML-1 formula but EML-3 derivation.
    This illustrates that EML depth of the RESULT can be lower than the
    derivation (simplification/cancellation at the end).
    """

    mass: float = 1.0  # geometric units

    def temperature(self) -> float:
        """T_H = 1/(8πM) in geometric units."""
        return 1.0 / (8.0 * math.pi * self.mass)

    def temperature_si(self, M_kg: float) -> float:
        """T_H = ħc³/(8πGMk_B) in SI units."""
        hbar = 1.0546e-34  # J·s
        c = 3.0e8  # m/s
        G = 6.674e-11  # m³/(kg·s²)
        kB = 1.381e-23  # J/K
        return hbar * c ** 3 / (8.0 * math.pi * G * M_kg * kB)

    def evaporation_time(self) -> float:
        """t_evap = 5120π·G²M³/(ħc⁴) ≈ (5120π)·M³ (geometric)."""
        return 5120.0 * math.pi * self.mass ** 3

    def entropy(self) -> float:
        """Bekenstein-Hawking entropy S = 4πM² = A/(4ħG) (area law, geometric units)."""
        return 4.0 * math.pi * self.mass ** 2

    def eml_depth_formula(self) -> int:
        return 1  # T_H = const/M: rational in M, EML-1

    def eml_depth_derivation(self) -> int:
        return 3  # Bogoliubov transformation involves erf-like functions


# ── Gravitational Waves ───────────────────────────────────────────────────────

@dataclass
class GravitationalWaves:
    """
    Gravitational wave strain: h(t,r) ∝ exp(iω(t-r/c))/r.

    Structure:
      - Carrier: exp(iωt) → EML-1 (pure exponential phase)
      - Propagation: exp(-iωr/c) → EML-1 in r
      - Geometric decay: 1/r → EML-2 (rational)
      - Overall: EML-1 × EML-2 = EML-2

    Linear approximation: h_{μν} = ε_{μν}·exp(ik_αx^α) + c.c.
    EML-1 in coordinates.
    """

    frequency: float = 100.0  # Hz (LIGO range ~100 Hz)
    omega: float = field(init=False)

    def __post_init__(self) -> None:
        self.omega = 2.0 * math.pi * self.frequency

    def strain_amplitude(self, t: float, r: float,
                          M_chirp: float = 30.0, r_Mpc: float = 410.0) -> float:
        """
        |h(t,r)| ∝ GM_c/r (geometric factor).
        For GW150914: M_chirp ≈ 30M_sun, r ≈ 410 Mpc → h ≈ 10^-21.
        """
        # Simplified strain magnitude (in natural units with geometric factors)
        G = 6.674e-11  # SI
        c = 3e8
        M_sun = 2e30
        Mpc = 3.086e22
        M_c_kg = M_chirp * M_sun
        r_m = r_Mpc * Mpc
        h = 4.0 * G * M_c_kg / (c ** 2 * r_m)
        return h

    def strain(self, t: float, r: float, amplitude: float = 1.0) -> complex:
        """h(t,r) = A/r · exp(iω(t-r/c))."""
        if r <= 0:
            return complex(0, 0)
        phase = self.omega * (t - r / _C)
        return (amplitude / r) * complex(math.cos(phase), math.sin(phase))

    def chirp_frequency(self, t: float, t_merger: float,
                         M_chirp: float = 1.0) -> float:
        """
        Inspiral chirp: f(t) = (1/π)·(5GM_c/(256(t_merger-t)³))^{3/8}.
        """
        tau = t_merger - t
        if tau <= 0:
            return float("inf")
        # Geometric units
        return (1.0 / math.pi) * (5.0 / (256.0 * tau)) ** (3.0 / 8.0)

    def eml_depth(self) -> int:
        return 2  # EML-1 × EML-2 = EML-2 overall


# ── Full Analysis ─────────────────────────────────────────────────────────────

class RiemannianEMLAnalysis:
    """Wrapper for complete GR/Riemannian EML analysis."""

    def __init__(self, mass: float = 1.0):
        self.metric = SchwarzschildMetric(mass=mass)
        self.geodesic = GeodesicEML(metric=self.metric)
        self.hawking = HawkingRadiation(mass=mass)
        self.gw = GravitationalWaves()

    def christoffel_table(self, r_vals: list[float]) -> list[dict]:
        """Compute Christoffel symbols at various r."""
        rows = []
        for r in r_vals:
            rows.append({
                "r": r,
                "Gamma_r_tt": self.metric.christoffel_r_tt(r),
                "Gamma_t_tr": self.metric.christoffel_t_tr(r),
                "Gamma_r_rr": self.metric.christoffel_r_rr(r),
                "kretschner": self.metric.kretschner_scalar(r),
            })
        return rows

    def hawking_vs_mass(self, mass_vals: list[float]) -> list[dict]:
        """T_H = 1/(8πM): inverse proportional in M (EML-1)."""
        rows = []
        for M in mass_vals:
            hw = HawkingRadiation(mass=M)
            rows.append({
                "M": M,
                "T_H": hw.temperature(),
                "T_H_formula": 1.0 / (8.0 * math.pi * M),
                "match": abs(hw.temperature() - 1.0 / (8.0 * math.pi * M)) < 1e-14,
                "S_BH": hw.entropy(),
            })
        return rows


def analyze_riemannian_eml() -> dict:
    """Run full Riemannian geometry / GR EML analysis."""
    results: dict = {
        "session": 63,
        "title": "Riemannian Geometry & GR EML Complexity",
        "taxonomy": GR_EML_TAXONOMY,
    }

    analysis = RiemannianEMLAnalysis(mass=1.0)

    # Metric components
    r_vals = [3.0, 4.0, 6.0, 10.0, 100.0]
    results["schwarzschild_metric"] = {
        "r_s": analysis.metric.schwarzschild_radius,
        "photon_sphere": analysis.metric.photon_sphere_radius(),
        "isco": analysis.metric.innermost_stable_orbit(),
        "g_tt": {f"r_{r}": analysis.metric.g_tt(r) for r in r_vals},
        "g_rr": {f"r_{r}": analysis.metric.g_rr(r) for r in r_vals},
        "eml_depth": analysis.metric.eml_depth_metric(),
    }

    # Christoffel symbols
    results["christoffel_symbols"] = {
        "table": analysis.christoffel_table(r_vals),
        "eml_depth": 2,
    }

    # Hawking temperature
    mass_vals = [0.5, 1.0, 2.0, 5.0, 10.0]
    results["hawking_temperature"] = {
        "table": analysis.hawking_vs_mass(mass_vals),
        "formula": "T_H = 1/(8*pi*M)",
        "eml_depth_formula": 1,
        "eml_depth_derivation": 3,
    }

    # GW
    gw = GravitationalWaves(frequency=100.0)
    results["gravitational_waves"] = {
        "strain_GW150914": gw.strain_amplitude(t=0.0, r=0.0),
        "strain_at_r1_t0": gw.strain(0.0, 1.0).real,
        "strain_at_r2_t0": gw.strain(0.0, 2.0).real,
        "eml_depth": gw.eml_depth(),
    }

    # Singularity
    r_singular = [10.0, 1.0, 0.1, 0.01]
    results["singularity_analysis"] = {
        "kretschner": {f"r_{r}": analysis.metric.kretschner_scalar(r) for r in r_singular},
        "eml_depth_at_singularity": "inf",
        "note": "K = 48M²/r⁶ → ∞ as r→0: EML-inf",
    }

    results["summary"] = {
        "key_insight": (
            "Riemannian metrics have EML depth equal to their component functions. "
            "Schwarzschild: EML-2 (rational in r). "
            "Singularity: EML-inf (1/r^6 divergence). "
            "Hawking formula: EML-1 in M (simplification!), derivation: EML-3. "
            "Gravitational waves: EML-2 (carrier × 1/r)."
        ),
        "eml_depths": {
            k: str(v.get("eml_depth", v.get("eml_depth_formula", "?")))
            for k, v in GR_EML_TAXONOMY.items()
        },
    }

    return results
