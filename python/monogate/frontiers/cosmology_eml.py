"""
Session 103 — Cosmology & Early Universe: EML in Extreme Regimes

Inflation, Big Bang singularity, dark energy, cosmic microwave background, and
quantum gravity effects. Models cosmological potentials and scale factors via EML depth.

Key theorem: de Sitter inflation is EML-1 (a(t)=exp(Ht)). Slow-roll inflation with
potential V(φ) is EML-1 or EML-2. CMB power spectrum is EML-3 (oscillatory acoustic peaks).
Big Bang singularity is EML-∞. Dark energy Λ is EML-0 (cosmological constant = EML-0).
Eternal inflation generates EML-∞ multiverse structure.
"""

from __future__ import annotations
import math, json
from dataclasses import dataclass, field


EML_INF = float("inf")


@dataclass
class InflationaryCosmology:
    """
    Inflation: exponential expansion driven by slow-rolling scalar field φ.

    EML structure:
    - Pure de Sitter: a(t) = exp(Ht): EML-1 (Session 77 confirmed)
    - Slow-roll: φ̈ + 3Hφ̇ + V'(φ) = 0, H² = V(φ)/3M²_pl
    - V(φ) = λφ⁴/4: EML-2 (polynomial)
    - V(φ) = m²φ²/2: EML-2 (polynomial)
    - V(φ) = Λ⁴(1-cos(φ/f)): EML-3 (natural inflation: cosine potential)
    - V(φ) = Λ⁴(1-exp(-√(2/3)φ/M_pl))²: Starobinsky = EML-1 (exp of field)
    - a(t) during slow-roll: EML-1 (quasi-de Sitter)
    - N e-folds = ∫H dt ≈ V/V'·dφ: EML-2
    """

    def slow_roll_efolds(self, V_func: str, phi_start: float, phi_end: float) -> dict:
        """Estimate e-folds N ≈ ∫(V/V') dφ for simple potentials."""
        if V_func == "chaotic_m2":
            N = (phi_start**2 - phi_end**2) / 4
            eml = 2
            reason = "V=m²φ²/2: N = (φ_start²-φ_end²)/4 = EML-2"
        elif V_func == "lambda_phi4":
            N = (phi_start**2 - phi_end**2) / 8
            eml = 2
            reason = "V=λφ⁴/4: N = (φ²_start-φ²_end)/8 = EML-2"
        elif V_func == "starobinsky":
            x_start = math.exp(-math.sqrt(2/3) * phi_start)
            x_end = math.exp(-math.sqrt(2/3) * phi_end)
            N = (3/4) * ((x_end - 1) - (x_start - 1) - math.log(abs((x_end-1)/(x_start-1) + 1e-30)))
            eml = 1
            reason = "Starobinsky V = Λ⁴(1-e^{-φ})²: N involves exp integrals = EML-1"
        else:
            N = 60.0
            eml = 2
            reason = "Generic slow-roll"
        return {
            "potential": V_func,
            "phi_start": phi_start,
            "phi_end": phi_end,
            "N_efolds": round(abs(N), 4),
            "eml": eml,
            "reason": reason,
        }

    def scale_factor(self, model: str, t: float, H: float = 1.0) -> dict:
        if model == "de_sitter":
            a = math.exp(H * t)
            eml = 1
            reason = "a(t) = exp(Ht): EML-1"
        elif model == "matter_dominated":
            a = t**(2/3)
            eml = 2
            reason = "a(t) = t^{2/3}: EML-2 (power law)"
        elif model == "radiation_dominated":
            a = t**(1/2)
            eml = 2
            reason = "a(t) = t^{1/2}: EML-2"
        elif model == "big_bang":
            a = 0.0 if t == 0 else t**(1/2)
            eml = EML_INF if t == 0 else 2
            reason = "a(0) = 0: Big Bang singularity = EML-∞"
        else:
            a = 1.0
            eml = 0
            reason = "Static universe"
        return {"model": model, "t": t, "a_t": round(a, 6), "eml": eml, "reason": reason}

    def to_dict(self) -> dict:
        return {
            "e_folds": [
                self.slow_roll_efolds("chaotic_m2", 15.0, 1.0),
                self.slow_roll_efolds("lambda_phi4", 20.0, 1.0),
                self.slow_roll_efolds("starobinsky", 5.0, 0.1),
            ],
            "scale_factors": [
                self.scale_factor("de_sitter", 1.0),
                self.scale_factor("matter_dominated", 1.0),
                self.scale_factor("radiation_dominated", 1.0),
                self.scale_factor("big_bang", 0.0),
            ],
            "eml_inflation": 1,
            "eml_potentials": 2,
            "eml_natural_inflation": 3,
        }


@dataclass
class CMBPowerSpectrum:
    """
    Cosmic Microwave Background: temperature fluctuations T(θ,φ) = Σ a_{lm} Y_{lm}.

    EML structure:
    - Y_{lm}: spherical harmonics = EML-3 (sin/cos of angles)
    - C_l = ⟨|a_{lm}|²⟩: angular power spectrum
    - Acoustic peaks: C_l ~ cos²(l·θ_s) modulated by damping: EML-3
    - Sachs-Wolfe plateau (low l): C_l ~ const: EML-0
    - Silk damping (high l): C_l ~ exp(-l²/l²_D): EML-1 (Gaussian damping)
    - Spectral index n_s: C_l ~ l^{n_s-1}: EML-2 (power law)
    - Primordial spectrum P(k) ~ k^{n_s-1}: EML-2
    """

    def cmb_cl_approx(self, l: int, n_s: float = 0.965) -> dict:
        """Approximate C_l: Sachs-Wolfe + acoustic oscillations + Silk damping."""
        if l == 0 or l == 1:
            return {"l": l, "C_l": 1.0, "eml": 0, "regime": "monopole/dipole"}
        l_D = 1500  # Silk damping scale
        l_eq = 230   # first acoustic peak
        A_SW = 1.0 / l  # Sachs-Wolfe ~ l^{-1}
        A_acoustic = math.cos(math.pi * l / (2 * l_eq))**2
        A_silk = math.exp(-(l / l_D)**2)
        C_l = A_SW * A_acoustic * A_silk * l**n_s
        regime = "Sachs-Wolfe" if l < 50 else "acoustic" if l < 1200 else "damped"
        eml = 0 if l < 10 else 3 if l < 1200 else 1
        return {
            "l": l,
            "C_l": round(C_l, 8),
            "regime": regime,
            "eml": eml,
            "silk_factor": round(A_silk, 6),
        }

    def to_dict(self) -> dict:
        l_vals = [2, 10, 50, 220, 540, 800, 1500, 2500]
        return {
            "definition": "T(θ,φ) = Σ a_lm Y_lm: EML-3 (spherical harmonics)",
            "power_spectrum": [self.cmb_cl_approx(l) for l in l_vals],
            "eml_Y_lm": 3,
            "eml_SW_plateau": 0,
            "eml_acoustic": 3,
            "eml_silk": 1,
            "eml_primordial": 2,
            "n_s_planck": 0.9651,
            "n_s_eml": 2,
            "reason_ns": "n_s ≈ 0.965: power law index = EML-2 (power of wavenumber k)",
        }


@dataclass
class DarkEnergyAndSingularities:
    """
    Dark energy: cosmological constant Λ or quintessence field.
    Big Bang singularity: Penrose-Hawking theorem applies.

    EML structure:
    - Λ: EML-0 (constant! the simplest EML object)
    - Hubble constant H₀: EML-0 (measured constant)
    - Quintessence V(φ) = M⁴exp(-λφ/M_pl): EML-1 (exponential quintessence)
    - Big Bang (t=0): a(0)=0, ρ→∞: EML-∞ (curvature singularity)
    - Big Rip (phantom dark energy): a(t) → ∞ in finite time t_rip: EML-∞
    - Eternal inflation: inflating regions → EML-∞ (fractal structure of multiverse)
    - Holographic bound: S ≤ A/(4G): EML-2 (area law = EML-2 geometric)
    """

    def friedmann_energy(self, a: float, Omega_m: float = 0.3, Omega_Lambda: float = 0.7) -> dict:
        """H²/H₀² = Omega_m/a³ + Omega_Lambda."""
        if a <= 0:
            H_sq = float("inf")
            eml = EML_INF
        else:
            H_sq = Omega_m / a**3 + Omega_Lambda
            eml = 2
        return {
            "a": a,
            "H_sq_over_H0_sq": round(H_sq, 6) if H_sq < 1e9 else "→∞",
            "eml": "∞" if eml == EML_INF else eml,
            "dominant": "matter" if a > 0 and Omega_m/a**3 > Omega_Lambda else "Λ",
        }

    def dark_energy_models(self) -> list[dict]:
        return [
            {"model": "Cosmological constant Λ", "w": -1, "V": "Λ = const", "eml": 0,
             "reason": "Λ = constant: EML-0"},
            {"model": "Quintessence (exponential)", "w": round(-0.8, 2), "V": "M⁴exp(-λφ)", "eml": 1,
             "reason": "Exp potential: EML-1"},
            {"model": "k-essence", "w": round(-0.9, 2), "V": "non-canonical kinetic", "eml": 2,
             "reason": "Non-canonical: EML-2 Lagrangian"},
            {"model": "Phantom (w<-1)", "w": round(-1.1, 2), "V": "Crosses phantom divide", "eml": EML_INF,
             "reason": "Big Rip singularity in finite time = EML-∞"},
        ]

    def to_dict(self) -> dict:
        a_vals = [0.0, 0.1, 0.5, 1.0, 2.0]
        return {
            "friedmann": [self.friedmann_energy(a) for a in a_vals],
            "dark_energy": self.dark_energy_models(),
            "big_bang_eml": EML_INF,
            "Lambda_eml": 0,
            "holographic_S_leq_A_4G": {"eml": 2, "reason": "S ~ A: EML-2 (geometric, area = EML-2)"},
            "eternal_inflation": {"eml": EML_INF, "reason": "Fractal multiverse: EML-∞ landscape"},
        }


def analyze_cosmology_eml() -> dict:
    inflation = InflationaryCosmology()
    cmb = CMBPowerSpectrum()
    dark = DarkEnergyAndSingularities()
    return {
        "session": 103,
        "title": "Cosmology & Early Universe: EML in Extreme Regimes",
        "key_theorem": {
            "theorem": "EML Cosmological Depth Theorem",
            "statement": (
                "de Sitter inflation a(t)=exp(Ht): EML-1 (ground state of accelerated expansion). "
                "Slow-roll potentials V(φ): EML-2 (polynomial) or EML-1 (Starobinsky: exp). "
                "Natural inflation V ~ 1-cos(φ/f): EML-3. "
                "CMB acoustic peaks: EML-3 (cos oscillations × Silk damping EML-1). "
                "Primordial power spectrum n_s~0.965: EML-2. "
                "Cosmological constant Λ: EML-0 (simplest possible dark energy). "
                "Big Bang singularity and Big Rip: EML-∞. "
                "Eternal inflation multiverse: EML-∞ (fractal landscape)."
            ),
        },
        "inflation": inflation.to_dict(),
        "cmb_spectrum": cmb.to_dict(),
        "dark_energy_singularities": dark.to_dict(),
        "eml_depth_summary": {
            "EML-0": "Cosmological constant Λ; Hubble constant H₀; Sachs-Wolfe plateau (l<10)",
            "EML-1": "de Sitter expansion exp(Ht); Starobinsky potential; Silk CMB damping exp(-l²/l_D²)",
            "EML-2": "Slow-roll potentials (φ², φ⁴); e-folds N; primordial spectrum k^{n_s}; Friedmann equation",
            "EML-3": "CMB acoustic peaks (cos oscillations); spherical harmonics Y_lm; natural inflation V~cos",
            "EML-∞": "Big Bang singularity; Big Rip; eternal inflation multiverse; quantum gravity regime",
        },
        "rabbit_hole_log": [
            "The cosmological constant Λ is the only truly EML-0 physical constant (a number with no EML structure). All other constants have EML-2 or higher status through dimensional transmutation or running. Λ's EML-0 status makes it both the simplest and most mysterious constant in physics.",
            "CMB spectrum as EML layering: EML-0 (Sachs-Wolfe) + EML-3 (acoustic) × EML-1 (Silk) + EML-2 (primordial tilt). The four EML classes contribute at different angular scales — the CMB is a natural EML decomposition of the universe's initial conditions.",
            "Slow-roll eternal inflation: in the 'quantum diffusion dominated' regime, φ̇ ~ H·δφ_quantum. This is a comparison between EML-2 (classical slow-roll) and EML-∞ (quantum fluctuations). When quantum > classical, eternal inflation begins and the landscape becomes EML-∞.",
        ],
        "connections": {
            "to_session_77": "Session 77: de Sitter = EML-1. Session 103: confirms + extends to CMB and inflation",
            "to_session_86": "Big Bang singularity = EML-∞ (Penrose-Hawking). Session 103 confirms from cosmological side",
        },
    }


if __name__ == "__main__":
    print(json.dumps(analyze_cosmology_eml(), indent=2, default=str))
