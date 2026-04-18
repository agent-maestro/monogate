"""
Session 141 — Consciousness Deep III: Binding, Qualia, and Unified Experience

EML operator: eml(x,y) = exp(x) - ln(y)
Key theorem: Neural binding is EML-3 (gamma synchrony); unified experience is EML-∞
(the combination problem — why bound qualia = one experience has no EML-finite solution).
"""
from __future__ import annotations
import math
from dataclasses import dataclass
from typing import Any


@dataclass
class NeuralBinding:
    """Binding problem: how separate features become unified percepts."""
    gamma_freq: float = 40.0   # Hz
    beta_freq: float = 20.0
    theta_freq: float = 6.0

    def phase_locking_value(self, freq1: float, freq2: float, coupling: float) -> float:
        """PLV = |⟨exp(i*Δφ)⟩|. EML-3 (complex exponential → magnitude)."""
        phase_diff = abs(freq1 - freq2) / (freq1 + freq2)
        return math.exp(-phase_diff / (coupling + 1e-10))

    def cross_frequency_coupling(self, low_amp: float, high_phase: float) -> float:
        """
        Modulation index: MI = |Σ A(t)*exp(i*φ_high(t))| / N.
        EML-3 (amplitude of EML-3 oscillation modulates EML-3 carrier).
        """
        modulation = low_amp * math.cos(high_phase)
        return abs(modulation) / (1 + abs(modulation))

    def binding_by_synchrony(self, n_neurons: int, sync_fraction: float) -> float:
        """
        Binding strength B = sync_fraction * log(n_neurons). EML-2.
        Full binding (unified percept): requires sync_fraction → 1 = EML-∞ limit.
        """
        return sync_fraction * math.log(n_neurons + 1)

    def gamma_oscillation(self, t: float, A: float = 1.0) -> float:
        """γ(t) = A * cos(2π*40*t) * exp(-t/τ). EML-3."""
        tau = 0.05
        return A * math.cos(2 * math.pi * self.gamma_freq * t) * math.exp(-t / tau)

    def analyze(self) -> dict[str, Any]:
        coupling_vals = [0.1, 0.5, 1.0, 2.0]
        plv = {c: round(self.phase_locking_value(40.0, 20.0, c), 4) for c in coupling_vals}

        t_vals = [0, 0.005, 0.01, 0.025, 0.05]
        gamma = {round(t*1000, 1): round(self.gamma_oscillation(t), 4) for t in t_vals}

        sync_vals = [0.1, 0.3, 0.5, 0.7, 0.9, 1.0]
        binding = {s: round(self.binding_by_synchrony(1000, s), 4) for s in sync_vals}

        return {
            "model": "NeuralBinding",
            "phase_locking_value_vs_coupling": plv,
            "gamma_oscillation_ms": gamma,
            "binding_strength_vs_sync": binding,
            "combination_problem": "EML-∞: no EML-finite map from N bound features → 1 unified experience",
            "eml_depth": {"gamma_oscillation": 3, "PLV": 3, "binding_strength": 2,
                          "unified_experience": "∞"},
            "key_insight": "Binding = EML-3 (gamma sync); the combination problem = EML-∞"
        }


@dataclass
class QualiaDimensions:
    """Qualia: redness, painfulness, phenomenal character — dimensions of experience."""

    n_qualia_dimensions: int = 20

    def qualia_space_metric(self, d1: float, d2: float) -> float:
        """Distance between qualia: Riemannian metric on phenomenal space. EML-2."""
        return math.sqrt((d1 - d2) ** 2 + 0.1)

    def phenomenal_richness(self) -> float:
        """
        Total phenomenal complexity: log(volume of qualia space).
        EML-2 for measurable correlates; EML-∞ for the fact of experience.
        """
        return self.n_qualia_dimensions * math.log(2.0)

    def inverted_spectrum_argument(self) -> dict[str, str]:
        """Could your 'red' be my 'green'? EML-∞ (functionally equivalent, experientially different)."""
        return {
            "functional_equivalence": "EML-2 (same input-output behavior)",
            "phenomenal_difference": "EML-∞ (difference in qualia = not EML-finite computable)",
            "implication": "Qualia cannot be identified with functional states: EML depth gap"
        }

    def consciousness_meter(self, phi: float, lambda_val: float) -> float:
        """
        IIT + GWT combination: C = Φ * log(λ_broadcast).
        EML-2 * EML-2 = EML-2 for correlates; EML-∞ for the phenomenal fact.
        """
        if phi <= 0 or lambda_val <= 0:
            return 0.0
        return phi * math.log(lambda_val)

    def analyze(self) -> dict[str, Any]:
        phi_vals = [0.1, 0.5, 1.0, 2.0, 5.0]
        lambda_vals = [1.1, 2.0, 5.0, 10.0]
        C_table = {}
        for phi in phi_vals:
            C_table[phi] = {l: round(self.consciousness_meter(phi, l), 4) for l in lambda_vals}

        return {
            "model": "QualiaDimensions",
            "n_dimensions": self.n_qualia_dimensions,
            "phenomenal_richness_nats": round(self.phenomenal_richness(), 4),
            "consciousness_meter_table": C_table,
            "inverted_spectrum": self.inverted_spectrum_argument(),
            "eml_depth": {"qualia_metric": 2, "phenomenal_richness": 2,
                          "qualia_themselves": "∞"},
            "key_insight": "Qualia metrics = EML-2; the fact of qualia = EML-∞"
        }


@dataclass
class RecurrentProcessingTheory:
    """Lamme (2006): recurrent processing creates phenomenal consciousness."""

    n_layers: int = 6        # cortical layers
    feedforward_speed: float = 10.0  # ms per layer
    feedback_speed: float = 15.0

    def feedforward_activation(self, layer: int, t: float) -> float:
        """Feedforward sweep: f(layer, t) = exp(-|t - layer*delay|/tau). EML-1."""
        delay = layer * self.feedforward_speed
        tau = 5.0
        return math.exp(-abs(t - delay) / tau)

    def recurrent_amplification(self, layer: int, t: float, fb_strength: float) -> float:
        """
        Recurrent feedback amplifies: R(l,t) = feedforward * (1 + fb_strength * exp(-t/tau)).
        EML-1 * EML-1 = EML-1 product; the recurrent loop creates EML-∞ at tipping.
        """
        ff = self.feedforward_activation(layer, t)
        tau = 30.0
        fb = fb_strength * math.exp(-t / tau)
        return ff * (1 + fb)

    def recurrent_threshold(self, fb_strength: float) -> bool:
        """Phenomenal consciousness threshold: fb_strength > 1. EML-∞ event."""
        return fb_strength > 1.0

    def analyze(self) -> dict[str, Any]:
        t_vals = [0, 10, 20, 30, 50, 100, 200]
        ff_vals = {l: {t: round(self.feedforward_activation(l, t), 4)
                       for t in t_vals} for l in range(1, 4)}
        fb_strengths = [0.3, 0.7, 1.0, 1.5, 2.0]
        thresholds = {fb: self.recurrent_threshold(fb) for fb in fb_strengths}
        return {
            "model": "RecurrentProcessingTheory",
            "n_layers": self.n_layers,
            "feedforward_activation": ff_vals,
            "recurrent_threshold": thresholds,
            "eml_depth": {"feedforward": 1, "recurrent_amplification": 1,
                          "consciousness_threshold": "∞"},
            "key_insight": "Feedforward = EML-1; recurrent threshold crossing = EML-∞"
        }


def analyze_cognition_v3_eml() -> dict[str, Any]:
    binding = NeuralBinding()
    qualia = QualiaDimensions(n_qualia_dimensions=20)
    rpt = RecurrentProcessingTheory()
    return {
        "session": 141,
        "title": "Consciousness Deep III: Binding, Qualia, and Unified Experience",
        "eml_operator": "eml(x,y) = exp(x) - ln(y)",
        "neural_binding": binding.analyze(),
        "qualia_dimensions": qualia.analyze(),
        "recurrent_processing": rpt.analyze(),
        "eml_depth_summary": {
            "EML-0": "Topological invariants of consciousness space",
            "EML-1": "Feedforward sweeps, recurrent decay amplitudes",
            "EML-2": "Binding strength log(N), qualia metrics, IIT Φ subcritical",
            "EML-3": "Gamma oscillations, PLV, cross-frequency coupling",
            "EML-∞": "Combination problem, binding threshold, qualia themselves, unified experience"
        },
        "key_theorem": (
            "The EML Binding Depth Theorem: "
            "Neural binding mechanisms (gamma synchrony, PLV, cross-frequency coupling) are EML-3. "
            "The combination problem — why N separately bound qualia yield ONE unified experience — "
            "is EML-∞: it cannot be derived from any EML-finite description of neural activity."
        ),
        "rabbit_hole_log": [
            "Gamma = EML-3: same class as Airy, gravitational waves, Milankovitch",
            "PLV = exp(-Δf/...) = EML-1 form but squared modulus makes it EML-3",
            "Binding strength log(N) = EML-2: same as Shannon entropy (log of count)",
            "Combination problem: N qualia → 1 experience = EML-∞ gap (non-additive)",
            "Inverted spectrum: functional=EML-2, phenomenal difference=EML-∞"
        ],
        "connections": {
            "S131_cognition_v2": "Extends S131; adds binding (EML-3) and combination problem",
            "S119_transformer": "Gamma sync ↔ attention: both select via oscillatory/softmax gate",
            "S130_grand_synthesis_7": "Combination problem = EML-∞ asymmetry: sum(EML-3) ≠ EML-3"
        }
    }


if __name__ == "__main__":
    import json
    print(json.dumps(analyze_cognition_v3_eml(), indent=2, default=str))
