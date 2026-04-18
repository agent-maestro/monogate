"""
Session 147 — Climate Deep III: Full Earth System Coupling & Long-Term Dynamics

EML operator: eml(x,y) = exp(x) - ln(y)
Key theorem: Full Earth system coupling creates EML-∞ cascades —
cross-system tipping interactions are not EML-finite even when each individual
tipping point is a simple fold bifurcation.
"""
from __future__ import annotations
import math
from dataclasses import dataclass
from typing import Any


@dataclass
class CarbonCycleFeedbacks:
    """Full carbon cycle: atmosphere, ocean, land, permafrost interactions."""

    T_ref: float = 288.0    # K reference temperature
    C_pre: float = 280.0    # ppm pre-industrial CO2
    lambda_WV: float = 1.8  # W/m²/K water vapor feedback

    def co2_from_temperature(self, delta_T: float) -> float:
        """
        Carbon cycle feedback: ΔC/ΔT ≈ 20 ppm/K (IPCC).
        C(T) = C_pre * exp(delta_T * 20/C_pre). EML-1.
        """
        beta = 20.0 / self.C_pre
        return self.C_pre * math.exp(beta * delta_T)

    def radiative_forcing(self, C: float) -> float:
        """ΔF = 5.35 * ln(C/C_pre). EML-2."""
        if C <= 0:
            return 0.0
        return 5.35 * math.log(C / self.C_pre)

    def permafrost_carbon_release(self, delta_T: float) -> float:
        """
        Permafrost C release: R(T) = R0 * exp(alpha*delta_T) (Q10 response).
        EML-1. Abrupt thaw events = EML-∞.
        """
        R0 = 50.0  # GtC initial
        alpha = 0.25
        return R0 * math.exp(alpha * delta_T)

    def ocean_carbon_uptake(self, pCO2_atm: float, T: float) -> float:
        """
        Ocean-atmosphere flux: F = k * (pCO2_atm - pCO2_ocean).
        pCO2_ocean decreases with warming: EML-2 (Henry's law + T correction).
        """
        pCO2_ocean = 280.0 * math.exp(0.04 * (T - self.T_ref))
        k = 0.1
        return k * (pCO2_atm - pCO2_ocean)

    def analyze(self) -> dict[str, Any]:
        delta_T_vals = [0, 1, 2, 3, 4, 6]
        co2_feedback = {dT: round(self.co2_from_temperature(dT), 1) for dT in delta_T_vals}
        rf_vals = {C: round(self.radiative_forcing(C), 3)
                   for C in [280, 350, 420, 560, 840]}
        permafrost = {dT: round(self.permafrost_carbon_release(dT), 1)
                      for dT in delta_T_vals}
        ocean_flux = {C: round(self.ocean_carbon_uptake(C, 290.0), 2)
                      for C in [280, 420, 560, 840]}
        return {
            "model": "CarbonCycleFeedbacks",
            "co2_from_T_feedback_ppm": co2_feedback,
            "radiative_forcing_vs_CO2": rf_vals,
            "permafrost_carbon_release_GtC": permafrost,
            "ocean_flux_vs_CO2": ocean_flux,
            "eml_depth": {"co2_feedback": 1, "radiative_forcing": 2,
                          "permafrost": 1, "abrupt_permafrost_thaw": "∞"},
            "key_insight": "Carbon cycle feedbacks = EML-1/2; abrupt permafrost thaw = EML-∞"
        }


@dataclass
class TippingDomino:
    """
    Cascading tipping: one tipping element triggers others.
    Armstrong McKay et al. (2022): 16 tipping elements, many coupled.
    """

    def tipping_cascade_probability(self, n_triggered: int, coupling: float) -> float:
        """
        P(cascade | n triggered) = 1 - exp(-coupling * n_triggered^2).
        EML-1 base; EML-∞ at full cascade.
        """
        exponent = -coupling * n_triggered ** 2
        exponent = max(-700.0, exponent)
        return 1 - math.exp(exponent)

    def cross_tipping_forcing(self, T_arctic: float, T_amazon: float) -> float:
        """
        Arctic ice loss → jet stream weakening → Amazon drought feedback.
        Interaction term = EML-2 (product of two EML-1 changes).
        """
        arctic_effect = math.exp(-0.1 * T_arctic)
        amazon_sensitivity = math.exp(-0.05 * T_amazon)
        return arctic_effect * amazon_sensitivity

    def risk_hothouse_earth(self, warming: float) -> float:
        """
        Lenton et al. hothouse Earth: P(hothouse | warming) = sigmoid.
        EML-∞ qualitative transition; sigmoid approximation = EML-2.
        """
        k = 2.0
        T_crit = 2.0
        exponent = -k * (warming - T_crit)
        exponent = max(-500.0, min(500.0, exponent))
        return 1.0 / (1 + math.exp(exponent))

    def analyze(self) -> dict[str, Any]:
        n_vals = [1, 2, 3, 4, 5, 8]
        cascade_probs = {n: {c: round(self.tipping_cascade_probability(n, c), 4)
                              for c in [0.1, 0.3, 0.5]}
                         for n in n_vals}
        warming_vals = [1.0, 1.5, 2.0, 2.5, 3.0, 4.0]
        hothouse = {T: round(self.risk_hothouse_earth(T), 4) for T in warming_vals}
        cross = {(T_a, T_am): round(self.cross_tipping_forcing(T_a, T_am), 4)
                 for T_a, T_am in [(2, 3), (4, 5), (6, 8)]}
        return {
            "model": "TippingDomino",
            "cascade_probability": cascade_probs,
            "hothouse_earth_risk": hothouse,
            "cross_tipping_interaction": {str(k): v for k, v in cross.items()},
            "known_tipping_cascades": [
                "Arctic ice → AMOC → Amazon (via jet stream) — EML-∞ chain",
                "AMOC collapse → monsoon shift → Sahel greening — EML-∞",
                "Permafrost → CO2 → further warming → more permafrost — EML-∞ loop"
            ],
            "eml_depth": {"cascade_prob": 1, "cross_tipping": 2,
                          "hothouse_transition": "∞", "full_cascade": "∞"},
            "key_insight": "Individual tipping = EML-∞; domino cascades = EML-∞ composed — still EML-∞"
        }


@dataclass
class LongTermClimateEvolution:
    """Million-year climate evolution: ice ages, weathering, solar evolution."""

    solar_increase_rate: float = 0.01  # per Gyr

    def faint_young_sun(self, t_Gyr: float) -> float:
        """Solar luminosity: L(t) = L0 / (1 + 0.4*(1 - t/t_now)). EML-2 (rational)."""
        t_now = 4.5
        return 1.0 / (1 + 0.4 * (1 - t_Gyr / t_now))

    def weathering_thermostat(self, T: float, T_ref: float = 288.0) -> float:
        """
        Silicate weathering CO2 drawdown: W(T) = W0 * exp(k*(T-T_ref)).
        Negative feedback: EML-1 stabilizer.
        """
        k = 0.05
        return math.exp(k * (T - T_ref))

    def snowball_bifurcation(self, L: float, L_crit: float = 0.94) -> str:
        """Snowball Earth: L < L_crit → ice-albedo runaway. EML-∞ transition."""
        if L < L_crit:
            return "Snowball (EML-∞ glaciation)"
        return "Habitable (EML-1 stabilized)"

    def analyze(self) -> dict[str, Any]:
        t_vals = [0.5, 1.0, 2.0, 3.0, 4.0, 4.5]
        L_vals = {t: round(self.faint_young_sun(t), 4) for t in t_vals}
        T_vals = [280, 285, 288, 292, 295]
        W_vals = {T: round(self.weathering_thermostat(T), 4) for T in T_vals}
        snowball = {t: self.snowball_bifurcation(self.faint_young_sun(t))
                    for t in t_vals}
        return {
            "model": "LongTermClimateEvolution",
            "solar_luminosity_vs_Gyr": L_vals,
            "weathering_thermostat": W_vals,
            "snowball_vs_time": snowball,
            "eml_depth": {"solar_luminosity": 2, "weathering_feedback": 1,
                          "snowball_transition": "∞"},
            "key_insight": "Weathering thermostat = EML-1 stabilizer; snowball bifurcation = EML-∞"
        }


def analyze_climate_v3_eml() -> dict[str, Any]:
    carbon = CarbonCycleFeedbacks()
    tipping = TippingDomino()
    longterm = LongTermClimateEvolution()
    return {
        "session": 147,
        "title": "Climate Deep III: Full Earth System Coupling & Long-Term Dynamics",
        "eml_operator": "eml(x,y) = exp(x) - ln(y)",
        "carbon_cycle_feedbacks": carbon.analyze(),
        "tipping_domino": tipping.analyze(),
        "long_term_evolution": longterm.analyze(),
        "eml_depth_summary": {
            "EML-0": "Stoichiometric ratios, topological network of tipping connections",
            "EML-1": "Carbon cycle feedbacks (Q10), weathering thermostat, permafrost",
            "EML-2": "Radiative forcing ln(C/C₀), cross-tipping interaction products",
            "EML-3": "Solar-driven oscillations (Milankovitch — from S137)",
            "EML-∞": "All individual tipping, all cascades, snowball Earth, hothouse Earth"
        },
        "key_theorem": (
            "The EML Earth System Theorem: "
            "Earth system feedbacks are EML-1 (exponential responses). "
            "Forcing functions are EML-2 (logarithmic CO₂, rational solar). "
            "All tipping transitions are EML-∞. "
            "Critically: cascading tipping (domino effects) are ALSO EML-∞ — "
            "composition of EML-∞ events does not increase the depth, "
            "but does increase the probability and decrease the threshold."
        ),
        "rabbit_hole_log": [
            "CO₂ feedback C(T) = C_pre*exp(β*ΔT) = EML-1 (same as BCS gap structure!)",
            "Weathering thermostat = EML-1 negative feedback: stabilizes Gaia for 4 Gyr",
            "Cascade probability = 1-exp(-λn²) = EML-1 with quadratic exponent",
            "Cross-tipping product = exp(-0.1T_a)*exp(-0.05T_am) = EML-1 composed = EML-1",
            "Hothouse sigmoid → EML-∞ in sharp limit (same as all transition phenomena)"
        ],
        "connections": {
            "S137_climate_v2": "Extends S137 with full carbon cycle + domino tipping + Gyr dynamics",
            "S132_evolution_v2": "Major evolutionary transitions ↔ tipping points: both EML-∞",
            "S57_stat_mech": "Carbon cycle feedback = EML-1 (same as Boltzmann partition)"
        }
    }


if __name__ == "__main__":
    import json
    print(json.dumps(analyze_climate_v3_eml(), indent=2, default=str))
