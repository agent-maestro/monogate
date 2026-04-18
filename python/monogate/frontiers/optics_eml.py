"""
Session 116 — Optics, Diffraction & Quantum Coherence: EML of Light

Huygens-Fresnel, Fraunhofer diffraction, coherence, laser threshold,
and squeezed light classified by EML depth.

Key theorem: All wave optics is EML-3 (diffraction = oscillatory integrals).
Laser threshold is EML-∞ → EML-1 (pumping threshold = phase transition birthing
an EML-1 coherent state). Coherence length is EML-2. Photon statistics
(Poissonian) is EML-1. Squeezed light is sub-EML-1.
"""

from __future__ import annotations
import math, json
from dataclasses import dataclass, field


EML_INF = float("inf")


@dataclass
class FresnelFraunhofer:
    """
    Huygens-Fresnel principle: E(P) = ∫∫ A(Q)·exp(ikr)/r dS.
    Fraunhofer limit (far field): E(θ) = FT of aperture function.

    EML structure:
    - Amplitude factor A(Q): EML-0 (aperture = 0 or 1)
    - Phase factor exp(ikr): EML-1 (single exp of imaginary argument)
    - Interference sum: Σ exp(ikr_n): EML-3 (oscillatory superposition)
    - Intensity I = |E|²: EML-2 (modulus squared of EML-3 = EML-3 but averaged → EML-2)
    - Single slit I = I₀·sinc²(β): EML-3
    - Double slit I = I₀·cos²(δ/2)·sinc²(β): EML-3
    """

    def single_slit_intensity(self, theta: float, wavelength: float = 500e-9,
                               slit_width: float = 1e-5) -> dict:
        """I(θ) = I₀·(sin(β)/β)² where β = π·a·sin(θ)/λ."""
        if abs(theta) < 1e-12:
            return {"theta_deg": 0, "I_over_I0": 1.0, "eml": 3}
        beta = math.pi * slit_width * math.sin(theta) / wavelength
        sinc = math.sin(beta) / beta if abs(beta) > 1e-10 else 1.0
        I = sinc ** 2
        return {
            "theta_deg": round(math.degrees(theta), 3),
            "beta": round(beta, 4),
            "I_over_I0": round(I, 6),
            "eml": 3,
            "reason": "I = sinc²(β) = (sin β/β)²: EML-3 (oscillatory in angle)",
        }

    def double_slit_intensity(self, theta: float, wavelength: float = 500e-9,
                               slit_width: float = 1e-5,
                               slit_separation: float = 5e-5) -> dict:
        """I = I₀·cos²(πd·sinθ/λ)·sinc²(πa·sinθ/λ)."""
        if abs(theta) < 1e-12:
            return {"theta_deg": 0, "I_over_I0": 1.0, "eml": 3}
        beta = math.pi * slit_width * math.sin(theta) / wavelength
        delta_half = math.pi * slit_separation * math.sin(theta) / wavelength
        sinc = math.sin(beta) / beta if abs(beta) > 1e-10 else 1.0
        I = (math.cos(delta_half) ** 2) * (sinc ** 2)
        return {
            "theta_deg": round(math.degrees(theta), 3),
            "I_over_I0": round(I, 6),
            "eml": 3,
            "reason": "I = cos²(δ/2)·sinc²(β): EML-3 (product of oscillatory functions)",
        }

    def fraunhofer_aperture(self, aperture_type: str) -> dict:
        return {
            "aperture_type": aperture_type,
            "field_pattern": {
                "slit": "sinc(u) = sin(πu)/πu",
                "circle": "2J₁(v)/v (Airy disk)",
                "rectangular": "sinc(u)·sinc(v)",
                "grating": "Σ exp(inkd·sinθ) = sin(Nδ/2)/sin(δ/2)",
            }.get(aperture_type, "FT of aperture"),
            "eml": 3,
            "reason": "All Fraunhofer patterns = FT of aperture = EML-3 (oscillatory integral)",
        }

    def to_dict(self) -> dict:
        angles = [0, 0.001, 0.002, 0.005, 0.01, 0.02, 0.05]
        return {
            "single_slit": [self.single_slit_intensity(th) for th in angles],
            "double_slit": [self.double_slit_intensity(th) for th in angles],
            "aperture_types": [self.fraunhofer_aperture(t)
                               for t in ["slit", "circle", "rectangular", "grating"]],
            "eml_amplitude": 1,
            "eml_intensity": 3,
            "huygens_fresnel_eml": 3,
        }


@dataclass
class CoherenceAndLasers:
    """
    Optical coherence and laser physics.

    EML structure:
    - Temporal coherence: γ(τ) = exp(-|τ|/τ_c): EML-1 (exponential decay)
    - Coherence time: τ_c = 1/Δν: EML-0 (inverse bandwidth = EML-0 rational)
    - Coherence length: l_c = c·τ_c = λ²/Δλ: EML-2 (λ²/Δλ = power law ratio)
    - Spatial coherence (van Cittert-Zernike): Γ(r₁,r₂) = FT of source: EML-3
    - Laser below threshold: spontaneous emission, ASE: EML-1 (chaotic light ~ Bose-Einstein)
    - Laser at threshold: EML-∞ (diverging photon number fluctuations)
    - Laser above threshold: coherent state |α⟩ with Poissonian statistics: EML-1
    - Phase diffusion: φ(t) = Brownian motion → linewidth Δν = 1/(2π·τ_c): EML-2
    """

    def temporal_coherence(self, tau: float, coherence_time: float = 1e-12) -> dict:
        """γ(τ) = exp(-|τ|/τ_c): EML-1 exponential decay."""
        gamma = math.exp(-abs(tau) / coherence_time)
        return {
            "tau_s": tau,
            "tau_c_s": coherence_time,
            "gamma": round(gamma, 6),
            "eml": 1,
            "reason": "γ(τ) = exp(-|τ|/τ_c): EML-1 (exponential coherence decay = ground state of dephasing)",
        }

    def coherence_length(self, wavelength_m: float, delta_lambda: float) -> dict:
        """l_c = λ²/Δλ."""
        l_c = wavelength_m**2 / delta_lambda
        return {
            "lambda_nm": wavelength_m * 1e9,
            "delta_lambda_nm": delta_lambda * 1e9,
            "l_c_mm": round(l_c * 1e3, 4),
            "eml": 2,
            "reason": "l_c = λ²/Δλ: EML-2 (ratio of squared wavelength to bandwidth = power law ratio)",
        }

    def laser_photon_statistics(self, n_mean: float, above_threshold: bool) -> dict:
        """
        Below threshold: thermal (Bose-Einstein) P(n) = n_mean^n/(1+n_mean)^{n+1}: EML-1
        Above threshold: coherent (Poissonian) P(n) = exp(-n_mean)·n_mean^n/n!: EML-1
        At threshold: EML-∞ (Mandel Q → ∞)
        """
        if above_threshold:
            P_0 = math.exp(-n_mean)
            dist_type = "Poissonian (coherent state)"
            eml = 1
            reason = "Poissonian P(n) = exp(-⟨n⟩)·⟨n⟩^n/n!: EML-1 (same structure as exp(-λ)λ^n/n!)"
        else:
            P_0 = 1.0 / (1 + n_mean)
            dist_type = "Bose-Einstein (thermal)"
            eml = 1
            reason = "Thermal P(n) = ⟨n⟩^n/(1+⟨n⟩)^{n+1}: EML-1 (geometric distribution = EML-1)"
        return {
            "n_mean": n_mean,
            "above_threshold": above_threshold,
            "dist_type": dist_type,
            "P_0": round(P_0, 6),
            "eml": eml,
            "reason": reason,
        }

    def laser_threshold_eml(self) -> dict:
        return {
            "below_threshold": {"eml": 1, "state": "thermal (chaotic) light", "Mandel_Q": "≥0"},
            "at_threshold": {"eml": EML_INF, "state": "critical — photon number diverges",
                             "Mandel_Q": "→∞", "reason": "Threshold = EML-∞ phase transition (laser = new ordered phase)"},
            "above_threshold": {"eml": 1, "state": "coherent state |α⟩", "Mandel_Q": "0"},
            "summary": "Laser threshold: EML-∞ transition birthing EML-1 coherent state — identical to all other ground-state transitions",
        }

    def to_dict(self) -> dict:
        return {
            "temporal_coherence": [self.temporal_coherence(t * 1e-13) for t in range(5)],
            "coherence_lengths": [
                self.coherence_length(633e-9, 1e-12),
                self.coherence_length(1550e-9, 1e-11),
                self.coherence_length(589e-9, 1e-9),
            ],
            "photon_statistics": [
                self.laser_photon_statistics(5, False),
                self.laser_photon_statistics(5, True),
            ],
            "laser_threshold": self.laser_threshold_eml(),
            "eml_coherence_time": 0,
            "eml_coherence_length": 2,
            "eml_coherence_function": 1,
            "eml_spatial_coherence": 3,
            "eml_laser_below": 1,
            "eml_laser_above": 1,
            "eml_laser_threshold": EML_INF,
        }


@dataclass
class QuantumOptics:
    """
    Quantum optics: photon number states, coherent states, squeezed states.

    EML structure:
    - Fock state |n⟩: EML-0 (integer photon number)
    - Coherent state |α⟩ = exp(-|α|²/2)·Σ αⁿ/√(n!)·|n⟩: EML-1 (exp amplitude)
    - Wigner function W(x,p) for coherent state: Gaussian = EML-3 (same as QHO ground state)
    - Squeezed state: variance ΔX < 1/2 in one quadrature: EML-1 squeezing parameter
    - Squeezed vacuum: W(x,p) = Gaussian with e^{±r} widths: EML-1 squeezing factor
    - Quantum Fisher information: F_Q = 4·Var(H): EML-2 (Fisher info = EML-2, S60)
    - Heisenberg limit: ΔΘ ≥ 1/√(N·F_Q): EML-2 sensitivity (1/N from entanglement)
    """

    def coherent_state_amplitude(self, alpha: float, n_max: int = 10) -> dict:
        """P(n) = exp(-|α|²)·|α|^{2n}/n! for coherent state."""
        alpha2 = alpha ** 2
        probabilities = []
        norm = math.exp(-alpha2)
        for n in range(n_max):
            p_n = norm * alpha2**n / math.factorial(n)
            probabilities.append(round(p_n, 6))
        return {
            "alpha": alpha,
            "n_mean": alpha2,
            "P_n": probabilities,
            "eml": 1,
            "reason": "|α⟩: P(n) = Poissonian = EML-1. State amplitude: exp(-|α|²/2) = EML-1",
        }

    def squeezing_variances(self, r: float) -> dict:
        """Squeezed state: ΔX₁² = exp(-2r)/4, ΔX₂² = exp(2r)/4."""
        var_X1 = math.exp(-2*r) / 4
        var_X2 = math.exp(2*r) / 4
        return {
            "squeezing_r": r,
            "Delta_X1_sq": round(var_X1, 6),
            "Delta_X2_sq": round(var_X2, 6),
            "product_DX1_DX2_sq": round(var_X1 * var_X2, 6),
            "heisenberg_min": 0.0625,
            "eml": 1,
            "reason": "Squeezed quadrature variance exp(±2r): EML-1 (exponential squeezing = EML-1)",
        }

    def to_dict(self) -> dict:
        return {
            "coherent_states": [self.coherent_state_amplitude(a) for a in [1.0, 2.0, 3.0]],
            "squeezing": [self.squeezing_variances(r) for r in [0.0, 0.5, 1.0, 2.0]],
            "eml_fock_state": 0,
            "eml_coherent_state": 1,
            "eml_wigner_coherent": 3,
            "eml_squeezed": 1,
            "heisenberg_limit_eml": 2,
        }


def analyze_optics_eml() -> dict:
    diff = FresnelFraunhofer()
    coh = CoherenceAndLasers()
    qo = QuantumOptics()
    return {
        "session": 116,
        "title": "Optics, Diffraction & Quantum Coherence: EML of Light",
        "key_theorem": {
            "theorem": "EML Optics Depth Theorem",
            "statement": (
                "Wave amplitude exp(ikr) is EML-1 per ray. "
                "Interference patterns (sinc², cos²) are EML-3 (oscillatory). "
                "Fraunhofer diffraction = FT of aperture = EML-3. "
                "Temporal coherence γ(τ)=exp(-|τ|/τ_c) is EML-1. "
                "Coherence length λ²/Δλ is EML-2. "
                "Spatial coherence = van Cittert-Zernike = EML-3. "
                "Laser threshold = EML-∞ (phase transition). "
                "Coherent state photon statistics = EML-1 (Poissonian). "
                "Squeezed quadrature variance exp(±2r) = EML-1. "
                "Wigner function of coherent state = EML-3 (Gaussian in phase space)."
            ),
        },
        "diffraction": diff.to_dict(),
        "coherence_lasers": coh.to_dict(),
        "quantum_optics": qo.to_dict(),
        "eml_depth_summary": {
            "EML-0": "Photon number n (Fock state); coherence time τ_c = 1/Δν; aperture function (0 or 1)",
            "EML-1": "Wave amplitude exp(ikr); temporal coherence exp(-|τ|/τ_c); coherent state; squeezed variance exp(±2r)",
            "EML-2": "Coherence length λ²/Δλ; Heisenberg limit 1/√N; linewidth Δν ~ 1/τ_c",
            "EML-3": "All diffraction patterns (sinc², Airy, grating); spatial coherence FT; Wigner function",
            "EML-∞": "Laser threshold (critical fluctuations); photon number divergence at threshold",
        },
        "rabbit_hole_log": [
            "The laser is a perfect EML-∞→EML-1 transition: below threshold, light is thermal (EML-1 Bose-Einstein). At threshold, photon number fluctuations diverge (EML-∞). Above threshold, a coherent state emerges (EML-1). This is the optical analog of every other EML-∞→EML-1 transition: Ising T_c→ferromagnet, epidemic R₀=1→endemic, de Sitter inflation onset.",
            "All optics is EML-3 because light is waves: every diffraction pattern — single slit sinc², double slit cosine modulation, circular aperture Airy disk, grating comb — is EML-3. The Fourier transform of any aperture function is EML-3 because it is an oscillatory integral (EML-3 by definition). Wave optics and EML-3 are coextensive.",
            "Squeezed light is EML-1 below the vacuum: the squeezing parameter r controls quadrature variances as exp(±2r). This is EML-1 squeezing of the EML-3 Wigner function. You can squeeze the uncertainty below the vacuum level (ΔX < 1/2) by concentrating the EML-3 uncertainty into the conjugate quadrature. Quantum control is EML-1 modulation of EML-3 quantum states.",
            "Coherence time is EML-0 (τ_c = 1/Δν) but coherence length is EML-2 (l_c = λ²/Δλ): this is the EML-0→EML-2 gap from spatial to temporal. Adding propagation (multiplying by c) introduces a wavelength-squared structure that costs one EML level. Distance is EML-2 relative to frequency because distance involves the geometry of the wave (EML-3 cycle length).",
        ],
        "connections": {
            "to_session_57": "Laser threshold = EML-∞ phase transition. Same universality as Ising, epidemic, de Sitter.",
            "to_session_61": "QHO Wigner function = EML-3 Gaussian. Coherent state Wigner = EML-3. Optics = QM in phase space.",
        },
    }


if __name__ == "__main__":
    print(json.dumps(analyze_optics_eml(), indent=2, default=str))
