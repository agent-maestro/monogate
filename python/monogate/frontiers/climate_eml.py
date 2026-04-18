"""
Session 107 — Climate & Earth Systems: EML in Planetary Dynamics

Energy balance, radiative forcing, climate sensitivity, ocean circulation,
and tipping points classified by EML depth.

Key theorem: Earth's energy balance is EML-0 (Stefan-Boltzmann constant = EML-0,
T_eq = (S(1-α)/4σ)^{1/4}: EML-2). Climate sensitivity λ = ΔT/ΔF is EML-0 per
forcing unit. Radiative forcing ΔF = 5.35·ln(C/C₀): EML-2 (logarithmic in CO₂).
Ocean thermohaline circulation is EML-1 (exponential turnover). Climate tipping
points (ice-albedo feedback, AMOC collapse) are EML-∞.
"""

from __future__ import annotations
import math, json
from dataclasses import dataclass, field


EML_INF = float("inf")

SIGMA = 5.67e-8   # Stefan-Boltzmann constant W/(m²·K⁴)
S0 = 1361.0       # Solar constant W/m²


@dataclass
class EnergyBalanceModel:
    """
    Planetary energy balance: absorbed solar = emitted thermal.

    EML structure:
    - T_eq = ((S₀(1-α))/(4σ))^{1/4}: EML-2 (rational power of EML-0 constants)
    - Stefan-Boltzmann: F_out = σT⁴: EML-2 (T⁴ = exp(4·ln T))
    - Greenhouse effect: T_surface = T_eq·(1+τ/2)^{1/4}: EML-2
    - Climate sensitivity: λ = ΔT/ΔF ≈ 0.8 K/(W/m²): EML-0 (linear response constant)
    - Transient climate response: ECS = F_{2×CO₂}·λ = 5.35·ln(2)·λ: EML-2 (log × constant)
    - CO₂ radiative forcing: ΔF = 5.35·ln(C/C₀) W/m²: EML-2 (logarithmic)
    """

    def equilibrium_temperature(self, albedo: float = 0.30, tau: float = 0.0) -> dict:
        """T_eq = ((S₀(1-α)/4σ))^{1/4} with optional greenhouse τ."""
        T_eq = ((S0 * (1 - albedo)) / (4 * SIGMA)) ** 0.25
        T_surface = T_eq * (1 + tau / 2) ** 0.25
        return {
            "albedo": albedo,
            "tau_optical_depth": tau,
            "T_eq_K": round(T_eq, 2),
            "T_surface_K": round(T_surface, 2),
            "T_surface_C": round(T_surface - 273.15, 2),
            "eml": 2,
            "reason": "T = ((S₀(1-α)/4σ))^{1/4}: EML-2 (rational power of constants)",
        }

    def co2_forcing(self, C: float, C0: float = 280.0) -> dict:
        """Myhre formula: ΔF = 5.35·ln(C/C₀) W/m²."""
        if C <= 0 or C0 <= 0:
            return {"C": C, "C0": C0, "delta_F": 0.0, "eml": 2}
        delta_F = 5.35 * math.log(C / C0)
        delta_T = 0.8 * delta_F
        return {
            "C_ppm": C,
            "C0_ppm": C0,
            "delta_F_Wm2": round(delta_F, 3),
            "delta_T_K": round(delta_T, 3),
            "eml": 2,
            "reason": "ΔF = 5.35·ln(C/C₀): EML-2 (logarithmic forcing in CO₂ concentration)",
        }

    def stefan_boltzmann_emission(self, T_K: float) -> dict:
        F = SIGMA * T_K ** 4
        return {
            "T_K": T_K,
            "F_Wm2": round(F, 2),
            "eml": 2,
            "reason": "F = σT⁴ = σ·exp(4·ln T): EML-2 (power of temperature)",
        }

    def to_dict(self) -> dict:
        return {
            "equilibrium": [
                self.equilibrium_temperature(0.30, 0.0),
                self.equilibrium_temperature(0.30, 0.78),
                self.equilibrium_temperature(0.61, 0.0),
            ],
            "co2_forcing": [self.co2_forcing(C) for C in [280, 350, 420, 560, 840]],
            "stefan_boltzmann": [self.stefan_boltzmann_emission(T) for T in [255, 288, 310]],
            "climate_sensitivity_lambda": {"value_K_per_Wm2": 0.8, "eml": 0,
                                           "reason": "λ = ΔT/ΔF: EML-0 (linear response = proportionality constant)"},
        }


@dataclass
class OceanCirculation:
    """
    Thermohaline circulation (THC / AMOC): density-driven global ocean conveyor belt.

    EML structure:
    - Density ρ(T,S) = ρ₀(1 - α_T(T-T₀) + β_S(S-S₀)): EML-2 (linear in T,S = EML-2 approximation)
    - Meridional overturning: q ~ ΔT_pole: EML-2 (linear response to forcing)
    - Box model (Stommel 1961): q = k(α_T·ΔT - β_S·ΔS): EML-2 (linear combination)
    - Turnover time ~ 1000 years: EML-0 (characteristic time = EML-0 constant)
    - Exponential decay to equilibrium: EML-1 (relaxation)
    - AMOC bifurcation / collapse: EML-∞ (tipping point = saddle-node bifurcation)
    - El Niño: SST anomaly ~ ENSO index: EML-3 (quasi-periodic oscillation 3-7 yr)
    """

    def stommel_box_model(self, delta_T: float, delta_S: float,
                           alpha_T: float = 0.1, beta_S: float = 0.8,
                           k: float = 1.0) -> dict:
        """Stommel 2-box THC: q = k(α_T ΔT - β_S ΔS)."""
        q = k * (alpha_T * delta_T - beta_S * delta_S)
        regime = "stable_on" if q > 0.1 else "off_or_weak" if q < 0.0 else "marginal"
        return {
            "delta_T": delta_T,
            "delta_S": delta_S,
            "q_overturning": round(q, 4),
            "regime": regime,
            "eml": 2,
            "reason": "q = k(α_T ΔT - β_S ΔS): EML-2 (linear combination of forcings)",
        }

    def enso_oscillation(self, t_years: float) -> dict:
        """Simple ENSO toy model: SST anomaly ≈ A·cos(2πt/T_enso)·exp(-t/τ_damp)."""
        T_enso = 4.0
        tau_damp = 6.0
        A = 1.5
        SST = A * math.cos(2 * math.pi * t_years / T_enso) * math.exp(-t_years / tau_damp)
        return {
            "t_years": t_years,
            "SST_anomaly_K": round(SST, 4),
            "eml": 3,
            "reason": "A·cos(2πt/T)·exp(-t/τ): EML-3 (oscillation × EML-1 decay = EML-3)",
        }

    def amoc_tipping(self, freshwater_forcing: float, threshold: float = 0.3) -> dict:
        """AMOC collapse tipping point."""
        if freshwater_forcing < threshold:
            state = "on"
            eml = 2
            reason = "AMOC operational: EML-2 linear response regime"
        elif abs(freshwater_forcing - threshold) < 0.05:
            state = "critical"
            eml = EML_INF
            reason = "AMOC near tipping point: EML-∞ (saddle-node bifurcation)"
        else:
            state = "off"
            eml = EML_INF
            reason = "AMOC collapsed: EML-∞ transition (hysteresis, irreversible)"
        return {
            "freshwater_Sv": freshwater_forcing,
            "threshold_Sv": threshold,
            "AMOC_state": state,
            "eml": "∞" if eml == EML_INF else eml,
            "reason": reason,
        }

    def to_dict(self) -> dict:
        return {
            "stommel_box": [
                self.stommel_box_model(10, 2),
                self.stommel_box_model(10, 13),
                self.stommel_box_model(5, 10),
            ],
            "enso": [self.enso_oscillation(t) for t in [0.5, 1.0, 2.0, 4.0, 8.0]],
            "amoc_tipping": [self.amoc_tipping(f) for f in [0.1, 0.25, 0.3, 0.4, 0.6]],
            "eml_THC_turnover": 0,
            "eml_AMOC_linear": 2,
            "eml_ENSO": 3,
            "eml_AMOC_tipping": EML_INF,
        }


@dataclass
class ClimateFeeback:
    """
    Climate feedbacks: Planck, water vapor, ice-albedo, lapse rate, cloud.

    EML structure:
    - Planck feedback: λ_P = -dF/dT = -4σT³: EML-2 (T³ power = EML-2)
    - Water vapor feedback: Clausius-Clapeyron e_s(T) = e_0·exp(-L_v/(R_v·T)): EML-1
    - Ice-albedo feedback: dα/dT < 0 near ice edge: EML-2 (linear to first order)
    - Total feedback: λ_total = λ_P + λ_WV + λ_LR + λ_cloud: EML-2 (sum of EML-2)
    - Climate sensitivity: ECS = -F_{2xCO2}/λ_total: EML-2 (ratio)
    - Tipping elements (ice sheets, permafrost): EML-∞ (bifurcations)
    """

    def clausius_clapeyron(self, T_K: float, e0: float = 611.2,
                            Lv: float = 2.5e6, Rv: float = 461.5) -> dict:
        """Saturation vapor pressure: e_s(T) = e₀·exp(-L_v/(R_v·T))."""
        e_s = e0 * math.exp(-Lv / (Rv * T_K))
        return {
            "T_K": T_K,
            "T_C": round(T_K - 273.15, 1),
            "e_s_Pa": round(e_s, 2),
            "eml": 1,
            "reason": "e_s = e₀·exp(-L_v/R_vT): EML-1 (Boltzmann-like exponential in 1/T)",
        }

    def planck_feedback(self, T_K: float) -> dict:
        """Planck feedback λ_P = -4σT³."""
        lambda_P = -4 * SIGMA * T_K ** 3
        return {
            "T_K": T_K,
            "lambda_P": round(lambda_P, 4),
            "eml": 2,
            "reason": "λ_P = -4σT³: EML-2 (T³ = power law)",
        }

    def feedback_table(self) -> list[dict]:
        return [
            {"name": "Planck", "lambda_Wm2K": -3.2, "eml": 2,
             "reason": "-4σT³: EML-2"},
            {"name": "Water vapor", "lambda_Wm2K": 1.8, "eml": 1,
             "reason": "e^{-L/RT}: EML-1 Clausius-Clapeyron"},
            {"name": "Lapse rate", "lambda_Wm2K": -0.5, "eml": 2,
             "reason": "Temperature profile change: EML-2"},
            {"name": "Ice-albedo", "lambda_Wm2K": 0.35, "eml": 2,
             "reason": "dα/dT: linear near ice edge = EML-2"},
            {"name": "Cloud (net)", "lambda_Wm2K": 0.4, "eml": EML_INF,
             "reason": "Cloud feedbacks: largest uncertainty, nonlinear = EML-∞"},
        ]

    def ecs_estimate(self, F_2xCO2: float = 3.7) -> dict:
        """ECS = -F_{2×CO₂} / λ_total."""
        feedbacks = self.feedback_table()
        lambda_total = sum(f["lambda_Wm2K"] for f in feedbacks if f["eml"] != EML_INF)
        ECS = -F_2xCO2 / lambda_total if lambda_total != 0 else float("inf")
        return {
            "F_2xCO2": F_2xCO2,
            "lambda_total_no_cloud": round(lambda_total, 3),
            "ECS_K": round(ECS, 2),
            "eml_ECS": 2,
            "note": "Cloud feedbacks excluded (EML-∞ uncertainty); best estimate ECS ~ 2.5-4.0 K",
        }

    def to_dict(self) -> dict:
        return {
            "clausius_clapeyron": [self.clausius_clapeyron(T) for T in [263, 273, 283, 293, 303]],
            "planck_feedback": [self.planck_feedback(T) for T in [255, 273, 288]],
            "feedback_table": self.feedback_table(),
            "ecs": self.ecs_estimate(),
            "tipping_elements": [
                {"name": "WAIS (West Antarctic Ice Sheet)", "eml": EML_INF,
                 "reason": "Marine ice sheet instability = EML-∞ tipping point"},
                {"name": "Amazon dieback", "eml": EML_INF,
                 "reason": "Vegetation-rainfall feedback collapse = EML-∞"},
                {"name": "Permafrost thaw", "eml": EML_INF,
                 "reason": "Carbon release feedback: threshold crossing = EML-∞"},
            ],
        }


def analyze_climate_eml() -> dict:
    ebm = EnergyBalanceModel()
    ocean = OceanCirculation()
    feedback = ClimateFeeback()
    return {
        "session": 107,
        "title": "Climate & Earth Systems: EML in Planetary Dynamics",
        "key_theorem": {
            "theorem": "EML Climate Depth Theorem",
            "statement": (
                "Earth's equilibrium temperature T_eq = (S₀(1-α)/4σ)^{1/4} is EML-2 (rational power). "
                "CO₂ forcing ΔF = 5.35·ln(C/C₀) is EML-2 (logarithmic in concentration). "
                "Climate sensitivity λ is EML-0 (linear response constant). "
                "Stefan-Boltzmann F=σT⁴ is EML-2 (power of temperature). "
                "Planck feedback -4σT³ is EML-2. "
                "Water vapor feedback (Clausius-Clapeyron) is EML-1 (exp(-L/RT)). "
                "ENSO oscillation is EML-3 (quasi-periodic). "
                "Climate tipping points (AMOC, ice sheets, permafrost) are EML-∞."
            ),
        },
        "energy_balance": ebm.to_dict(),
        "ocean_circulation": ocean.to_dict(),
        "feedbacks": feedback.to_dict(),
        "eml_depth_summary": {
            "EML-0": "Climate sensitivity λ; ocean turnover time ~1000 yr; discrete tipping element list",
            "EML-1": "Water vapor (Clausius-Clapeyron e^{-L/RT}); AMOC exponential relaxation to equilibrium",
            "EML-2": "T_eq (rational power of constants); CO₂ forcing ln(C/C₀); Stefan-Boltzmann T⁴; Planck feedback T³; ECS estimate",
            "EML-3": "ENSO quasi-oscillation; Milankovitch orbital cycles (quasi-periodic); atmospheric Rossby waves",
            "EML-∞": "AMOC collapse tipping; ice sheet marine instability; permafrost carbon feedback; cloud feedbacks",
        },
        "rabbit_hole_log": [
            "CO₂ forcing is logarithmic (EML-2) because of spectral saturation: the central absorption bands of CO₂ are already opaque. Each doubling of CO₂ adds the same radiative forcing. The EML-2 structure of forcing is the physical reason why climate sensitivity is defined per CO₂ doubling, not per ppm increment.",
            "Clausius-Clapeyron is EML-1: water vapor pressure e_s(T) = e₀·exp(-L_v/R_vT). This is the Boltzmann factor of evaporation. Water vapor feedback amplifies Planck (EML-2) feedback by the ratio of EML-1 sensitivity to temperature, making it the dominant positive feedback in the climate system.",
            "Tipping elements are EML-∞ precisely because they are saddle-node bifurcations: the system approaches a fold in phase space where the Jacobian eigenvalue crosses zero. At this fold, the normal form is x' = μ - x², exactly the EML-∞ structure of the Ising transition and NS blowup.",
            "Milankovitch cycles (EML-3) force EML-∞ ice ages: quasi-periodic orbital forcing (EML-3: 41 kyr obliquity, 100 kyr eccentricity, 23 kyr precession) drives the system across EML-∞ tipping thresholds. The climate is an EML-3 → EML-∞ cascade system.",
        ],
        "connections": {
            "to_session_57": "Phase transitions = EML-∞. Climate tipping points = planetary EML-∞ phase transitions.",
            "to_session_76": "NS equations (EML-∞ turbulence) govern ocean and atmospheric dynamics. Same EML class.",
        },
    }


if __name__ == "__main__":
    print(json.dumps(analyze_climate_eml(), indent=2, default=str))
