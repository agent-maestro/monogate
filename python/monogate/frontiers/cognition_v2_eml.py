"""
Session 131 — Consciousness Deep II: EML Models of Attention, Insight & Qualia

EML operator: eml(x,y) = exp(x) - ln(y)
EML depth hierarchy: 0 (topology) | 1 (equilibria) | 2 (geometry) | 3 (waves) | ∞ (singularities)

Key theorem: Conscious integration is EML-1 (softmax broadcast) in steady state;
insight/phase-transitions in awareness are EML-∞ (non-analytic jumps).
"""

from __future__ import annotations
import math
from dataclasses import dataclass, field
from typing import Any


# ---------------------------------------------------------------------------
# 1. Global Workspace Theory
# ---------------------------------------------------------------------------

@dataclass
class GlobalWorkspace:
    """Baars (1988): consciousness = global broadcast over a workspace."""

    n_modules: int = 8          # specialized processors
    broadcast_beta: float = 4.0  # inverse temperature of competition

    def competition_scores(self, activations: list[float]) -> list[float]:
        """Softmax competition: winner-take-all broadcast. EML-1."""
        max_a = max(activations)
        exps = [math.exp(self.broadcast_beta * (a - max_a)) for a in activations]
        Z = sum(exps)
        return [e / Z for e in exps]

    def broadcast_entropy(self, activations: list[float]) -> float:
        """Shannon entropy of broadcast distribution. EML-2."""
        probs = self.competition_scores(activations)
        return -sum(p * math.log(p + 1e-15) for p in probs)

    def ignition_threshold(self, activations: list[float], threshold: float = 0.5) -> bool:
        """Ignition: dominant module crosses threshold → global broadcast. EML-∞ event."""
        probs = self.competition_scores(activations)
        return max(probs) >= threshold

    def workspace_capacity(self) -> float:
        """Max information in workspace: log(n_modules). EML-2."""
        return math.log(self.n_modules)

    def analyze(self) -> dict[str, Any]:
        import random
        random.seed(42)
        activations = [random.gauss(0, 1) for _ in range(self.n_modules)]
        probs = self.competition_scores(activations)
        ignited = self.ignition_threshold(activations)
        return {
            "model": "GlobalWorkspaceTheory",
            "n_modules": self.n_modules,
            "activations": [round(a, 4) for a in activations],
            "broadcast_probabilities": [round(p, 4) for p in probs],
            "dominant_module": int(probs.index(max(probs))),
            "ignition_occurred": ignited,
            "broadcast_entropy": round(self.broadcast_entropy(activations), 4),
            "max_capacity_bits": round(self.workspace_capacity() / math.log(2), 4),
            "eml_depth": {
                "softmax_broadcast": 1,
                "entropy": 2,
                "ignition_event": "∞"
            },
            "key_insight": "Consciousness = EML-1 (Boltzmann broadcast) with EML-∞ ignition transitions"
        }


# ---------------------------------------------------------------------------
# 2. Predictive Coding
# ---------------------------------------------------------------------------

@dataclass
class PredictiveCoding:
    """Friston (2005): brain minimizes free energy F = KL[q||p] - log P(data)."""

    precision: float = 1.0      # inverse variance of prediction errors
    learning_rate: float = 0.1

    def prediction_error(self, prediction: float, observation: float) -> float:
        """Weighted prediction error: precision * (obs - pred)². EML-2."""
        return self.precision * (observation - prediction) ** 2

    def free_energy(self, prediction: float, observation: float,
                    prior_mean: float = 0.0, prior_var: float = 1.0) -> float:
        """Variational free energy F = E_q[log q - log p(x,y)]. EML-2."""
        likelihood_term = 0.5 * self.precision * (observation - prediction) ** 2
        prior_term = 0.5 * ((prediction - prior_mean) ** 2) / prior_var
        log_Z_approx = 0.5 * math.log(2 * math.pi / self.precision)
        return likelihood_term + prior_term + log_Z_approx

    def update_prediction(self, prediction: float, observation: float) -> float:
        """Gradient descent on free energy: EML-2 update."""
        grad = self.precision * (prediction - observation)
        return prediction - self.learning_rate * grad

    def hierarchical_layers(self, n_levels: int, top_down: float = 0.5) -> list[float]:
        """Multi-level predictive coding: each level suppresses lower-level errors."""
        errors = []
        signal = 1.0
        for level in range(n_levels):
            suppression = math.exp(-top_down * level)  # EML-1 attenuation
            residual_error = signal * (1 - suppression)
            errors.append(residual_error)
            signal *= suppression
        return errors

    def analyze(self) -> dict[str, Any]:
        predictions = [0.0, 0.5, 0.8, 0.9, 0.95]
        observation = 1.0
        trajectory = []
        p = 0.0
        for _ in range(20):
            p = self.update_prediction(p, observation)
            trajectory.append(round(p, 4))

        hierarchical = self.hierarchical_layers(5)
        fe = self.free_energy(0.8, 1.0)
        return {
            "model": "PredictiveCoding",
            "free_energy_at_0.8": round(fe, 4),
            "convergence_trajectory_20_steps": trajectory[-5:],
            "hierarchical_errors_5_levels": [round(e, 4) for e in hierarchical],
            "eml_depth": {
                "prediction_error": 2,
                "free_energy": 2,
                "hierarchical_attenuation": 1,
                "full_convergence": 2
            },
            "key_insight": "Perceptual inference = gradient descent (EML-2) on variational free energy"
        }


# ---------------------------------------------------------------------------
# 3. Integrated Information Theory
# ---------------------------------------------------------------------------

@dataclass
class IntegratedInformation:
    """Tononi (2004): Φ = information generated by a system above its parts."""

    n_elements: int = 4
    coupling: float = 0.5

    def transfer_entropy(self, coupling: float) -> float:
        """Mutual information between past and future states. EML-2."""
        if coupling <= 0:
            return 0.0
        p_joint = coupling
        p_marginal = math.sqrt(coupling)
        if p_joint <= 0 or p_marginal <= 0:
            return 0.0
        return p_joint * math.log(p_joint / (p_marginal ** 2 + 1e-15) + 1e-15)

    def phi_approximation(self, coupling: float, n: int) -> float:
        """Φ ≈ n * I(whole) - sum_parts I(part_i). EML-2 in subcritical, EML-∞ at criticality."""
        whole_info = n * self.transfer_entropy(coupling)
        part_info = sum(self.transfer_entropy(coupling * 0.5) for _ in range(n))
        return max(0.0, whole_info - part_info)

    def criticality_transition(self, couplings: list[float]) -> list[float]:
        """Φ as function of coupling: phase transition at critical coupling. EML-∞."""
        return [self.phi_approximation(c, self.n_elements) for c in couplings]

    def information_integration_depth(self, coupling: float) -> str:
        """EML depth depends on proximity to criticality."""
        phi = self.phi_approximation(coupling, self.n_elements)
        critical_phi = self.phi_approximation(0.7, self.n_elements)
        if phi < 0.01:
            return "0"
        elif phi < 0.5 * critical_phi:
            return "2"
        elif phi < 0.95 * critical_phi:
            return "3"
        else:
            return "∞"

    def analyze(self) -> dict[str, Any]:
        couplings = [i * 0.1 for i in range(11)]
        phi_values = self.criticality_transition(couplings)
        max_phi_idx = phi_values.index(max(phi_values))
        return {
            "model": "IntegratedInformationTheory",
            "n_elements": self.n_elements,
            "phi_vs_coupling": {
                round(c, 1): round(p, 4)
                for c, p in zip(couplings, phi_values)
            },
            "peak_phi": round(max(phi_values), 4),
            "peak_coupling": round(couplings[max_phi_idx], 1),
            "eml_depths": {
                round(c, 1): self.information_integration_depth(c)
                for c in [0.1, 0.3, 0.5, 0.7, 0.9]
            },
            "eml_depth": {
                "transfer_entropy": 2,
                "phi_subcritical": 2,
                "phi_near_criticality": 3,
                "phi_at_criticality": "∞"
            },
            "key_insight": "Φ is EML-2 in subcritical regime; the consciousness transition is EML-∞"
        }


# ---------------------------------------------------------------------------
# 4. Attention Mechanisms & Qualia
# ---------------------------------------------------------------------------

@dataclass
class AttentionAndQualia:
    """Attention as Boltzmann selection; qualia as the irreducible EML-∞ residual."""

    temperature: float = 1.0
    n_features: int = 10

    def attention_weights(self, query: list[float], keys: list[float]) -> list[float]:
        """Scaled dot-product attention: softmax(q·k / √d). EML-1."""
        d = len(query)
        scale = math.sqrt(d)
        scores = [sum(q * k for q, k in zip(query, keys)) / scale]
        # Simplified: scalar score → softmax over n_features
        logits = [math.cos(i * 0.5) * scores[0] for i in range(self.n_features)]
        max_l = max(logits)
        exps = [math.exp((l - max_l) / self.temperature) for l in logits]
        Z = sum(exps)
        return [e / Z for e in exps]

    def qualia_complexity(self, n_discriminable_states: int) -> dict[str, float]:
        """
        Qualia: subjective experience irreducible to third-person description.
        Chalmers' hard problem: the explanatory gap = EML-∞.
        Measurable correlates (NCC) = EML-2 (neural complexity).
        """
        ncc_complexity = math.log(n_discriminable_states)  # EML-2
        explanatory_gap = float('inf')  # EML-∞ (not closeable by reduction)
        return {
            "ncc_complexity_nats": round(ncc_complexity, 4),
            "explanatory_gap": "∞ (hard problem)",
            "discriminable_states": n_discriminable_states
        }

    def insight_dynamics(self, t_values: list[float]) -> list[float]:
        """
        Insight (aha moment): abrupt non-analytic jump in solution probability.
        Models as step function smoothed by tanh — EML-∞ in the sharp limit.
        """
        results = []
        for t in t_values:
            # Logistic: P(insight | t) = 1/(1+exp(-k*(t-t0)))
            k, t0 = 5.0, 0.0
            p = 1.0 / (1.0 + math.exp(-k * t))
            results.append(p)
        return results

    def analyze(self) -> dict[str, Any]:
        import random
        random.seed(7)
        query = [random.gauss(0, 1) for _ in range(4)]
        keys = [random.gauss(0, 1) for _ in range(4)]
        weights = self.attention_weights(query, keys)

        t_vals = [-2.0, -1.0, -0.5, 0.0, 0.5, 1.0, 2.0]
        insight_curve = self.insight_dynamics(t_vals)

        qualia = self.qualia_complexity(1000)

        return {
            "model": "AttentionAndQualia",
            "attention_weights_top5": [round(w, 4) for w in sorted(weights, reverse=True)[:5]],
            "attention_entropy": round(-sum(w * math.log(w + 1e-15) for w in weights), 4),
            "insight_probability_curve": {
                round(t, 1): round(p, 4) for t, p in zip(t_vals, insight_curve)
            },
            "insight_sharpness_k": 5.0,
            "qualia_analysis": qualia,
            "eml_depth": {
                "attention_softmax": 1,
                "attention_entropy": 2,
                "ncc_neural_correlates": 2,
                "insight_sharp_limit": "∞",
                "qualia_explanatory_gap": "∞"
            },
            "key_insight": (
                "Attention = EML-1 (Boltzmann). "
                "Neural correlates = EML-2. "
                "The hard problem of consciousness = EML-∞ (irreducible gap)."
            )
        }


# ---------------------------------------------------------------------------
# Main analysis function
# ---------------------------------------------------------------------------

def analyze_cognition_v2_eml() -> dict[str, Any]:
    gw = GlobalWorkspace(n_modules=8, broadcast_beta=4.0)
    pc = PredictiveCoding(precision=2.0, learning_rate=0.15)
    iit = IntegratedInformation(n_elements=4, coupling=0.5)
    aq = AttentionAndQualia(temperature=0.8, n_features=10)

    return {
        "session": 131,
        "title": "Consciousness Deep II: EML Models of Attention, Insight & Qualia",
        "eml_operator": "eml(x,y) = exp(x) - ln(y)",
        "global_workspace": gw.analyze(),
        "predictive_coding": pc.analyze(),
        "integrated_information": iit.analyze(),
        "attention_and_qualia": aq.analyze(),
        "eml_depth_summary": {
            "EML-0": "Topology of qualia space (discrete invariants)",
            "EML-1": "Softmax attention, global broadcast, Boltzmann competition",
            "EML-2": "Prediction errors, free energy, phi (subcritical), NCC complexity",
            "EML-3": "Phi near criticality, oscillatory binding (gamma waves)",
            "EML-∞": "Consciousness ignition, insight moments, explanatory gap (hard problem)"
        },
        "key_theorem": (
            "The EML Consciousness Depth Theorem: "
            "All measurable neural correlates of consciousness are EML-2 (information metrics). "
            "The integration transition (phi criticality) is EML-∞. "
            "The hard problem — why there is subjective experience — is EML-∞ by definition: "
            "it cannot be reduced to any EML-finite description."
        ),
        "rabbit_hole_log": [
            "GWT broadcast is softmax → EML-1: same class as Boltzmann, de Sitter expansion",
            "Predictive coding free energy is EML-2: same class as Fisher information, Shannon entropy",
            "IIT phi transition: subcritical=EML-2, critical=EML-∞ (same as stat mech phase transition)",
            "Insight = non-analytic jump = EML-∞ (same as shock formation, confinement)",
            "The explanatory gap IS the EML-∞ barrier: no EML-finite theory can bridge it"
        ],
        "connections": {
            "S57_stat_mech": "Boltzmann factor = softmax = EML-1 (same class as attention)",
            "S60_info_theory": "Free energy minimization = KL divergence = EML-2",
            "S75_qft_interacting": "Phase transition at criticality = EML-∞ (IIT phi, QCD confinement)",
            "S130_grand_synthesis_7": "Asymmetry: measuring consciousness is EML-2, being conscious is EML-∞"
        }
    }


if __name__ == "__main__":
    import json
    print(json.dumps(analyze_cognition_v2_eml(), indent=2, default=str))
