"""
Session 154 — Cognition Deep IV: Embodied Cognition, Enactivism & 4E Approaches

EML operator: eml(x,y) = exp(x) - ln(y)
Key theorem: 4E cognition (Embodied, Extended, Enacted, Embedded) reveals that
cognition is not just EML-∞ at qualia but EML-∞ at the body-world boundary —
the coupling between organism and environment is irreducibly EML-∞.
"""
from __future__ import annotations
import math
from dataclasses import dataclass
from typing import Any


@dataclass
class EmbodiedCognition:
    """Sensorimotor contingencies, body schema, proprioception."""

    body_dof: int = 7   # degrees of freedom (arm)

    def forward_kinematics(self, joint_angles: list[float]) -> list[float]:
        """
        End-effector position from joint angles: EML-3 (trig functions of angles).
        Jacobian J: EML-3 (sin/cos entries).
        """
        n = min(len(joint_angles), self.body_dof)
        x = sum(math.cos(sum(joint_angles[:i + 1])) for i in range(n))
        y = sum(math.sin(sum(joint_angles[:i + 1])) for i in range(n))
        return [round(x, 6), round(y, 6)]

    def jacobian_determinant(self, angles: list[float]) -> float:
        """
        det(J) = 0 at singular configurations (arm fully extended).
        EML-∞ at singularity (loss of dexterity). Elsewhere EML-3.
        """
        n = len(angles)
        if n == 0:
            return 0.0
        det_approx = abs(math.sin(sum(angles)))
        return round(det_approx, 6)

    def body_schema_update(self, proprioceptive_error: float, alpha: float = 0.1) -> float:
        """
        Hebbian body schema update: Δθ = α * error. EML-0 (linear update).
        Schema formation via repeated exposure: EML-2 (information accumulation).
        """
        return alpha * proprioceptive_error

    def sensorimotor_loop(self, n_steps: int = 10) -> dict[str, Any]:
        """
        Sensorimotor contingencies: action → perception → action.
        Loop generates EML-3 oscillatory dynamics; meaning emerges from the loop = EML-∞.
        """
        error = 1.0
        history = []
        for i in range(n_steps):
            correction = self.body_schema_update(error)
            error = error - correction + 0.05 * math.sin(i * 0.5)
            history.append(round(error, 4))
        return {
            "n_steps": n_steps,
            "error_trajectory": history,
            "final_error": history[-1],
            "eml_depth_loop": 3,
            "eml_depth_meaning": "∞ (meaning = EML-∞ emergent from sensorimotor loop)"
        }

    def analyze(self) -> dict[str, Any]:
        angles = [0.3, 0.5, 0.2, 0.4, 0.1, 0.3, 0.2]
        fk = self.forward_kinematics(angles)
        jdet = self.jacobian_determinant(angles)
        loop = self.sensorimotor_loop()
        return {
            "model": "EmbodiedCognition",
            "body_dof": self.body_dof,
            "end_effector_xy": fk,
            "jacobian_det": jdet,
            "at_singularity": jdet < 0.01,
            "sensorimotor_loop": loop,
            "eml_depth": {"forward_kinematics": 3, "singularity": "∞",
                          "schema_update": 0, "sensorimotor_meaning": "∞"},
            "key_insight": "Forward kinematics = EML-3; kinematic singularity = EML-∞; meaning from loop = EML-∞"
        }


@dataclass
class ExtendedMind:
    """Clark-Chalmers extended mind hypothesis — cognitive boundary is EML-∞."""

    def coupling_strength(self, agent_state: float, environment_state: float) -> float:
        """
        Coupling C = exp(-|agent - environment|). EML-1.
        Tight coupling → C → 1 (extended mind threshold).
        """
        diff = abs(agent_state - environment_state)
        return round(math.exp(-diff), 6)

    def otto_notebook_model(self, n_external_items: int) -> dict[str, Any]:
        """
        Otto carries a notebook as extended memory.
        Internal memory decays: M_int(t) = M0 * exp(-λt). EML-1.
        External memory = stable (EML-0 in ideal case).
        Combined: EML-∞ (the boundary is irreducible).
        """
        M0 = 1.0
        lambda_decay = 0.1
        t_vals = [0, 1, 5, 10, 20]
        internal = {t: round(M0 * math.exp(-lambda_decay * t), 4) for t in t_vals}
        return {
            "n_external_items": n_external_items,
            "internal_memory_decay": internal,
            "external_memory": "stable (EML-0)",
            "combined_eml": "∞",
            "boundary_status": "EML-∞: organism-environment coupling irreducible",
            "note": "Clark-Chalmers: cognitive boundary = EML-∞ event when extended"
        }

    def enactivism_sense_making(self, valence: float, intensity: float) -> float:
        """
        Sense-making (Maturana-Varela): organism evaluates environmental perturbation.
        Valence × arousal = affective appraisal. EML-2 (product of evaluations).
        But the significance = EML-∞ (normative, not physical).
        """
        appraisal = valence * math.log(1 + intensity)
        return round(appraisal, 6)

    def distributed_cognition(self, n_agents: int, connectivity: float) -> dict[str, Any]:
        """
        Hutchins: cognition distributed over agents + artifacts.
        Information capacity ~ n_agents * connectivity. EML-0.
        But the emergent cognitive process = EML-∞.
        """
        capacity = n_agents * connectivity
        entropy = math.log(n_agents + 1) * connectivity
        return {
            "n_agents": n_agents,
            "connectivity": connectivity,
            "info_capacity": round(capacity, 4),
            "distributed_entropy": round(entropy, 4),
            "eml_depth_capacity": 0,
            "eml_depth_process": "∞ (distributed cognition = EML-∞ emergent)"
        }

    def analyze(self) -> dict[str, Any]:
        coupling = {(a, e): self.coupling_strength(a, e)
                    for a, e in [(0, 0), (0.5, 0.5), (1.0, 1.0), (0, 1)]}
        otto = self.otto_notebook_model(n_external_items=50)
        sense = {(v, i): round(self.enactivism_sense_making(v, i), 4)
                 for v, i in [(1.0, 1.0), (-1.0, 2.0), (0.5, 0.5)]}
        distrib = self.distributed_cognition(n_agents=5, connectivity=0.7)
        return {
            "model": "ExtendedMind",
            "coupling_strength": {str(k): v for k, v in coupling.items()},
            "otto_notebook": otto,
            "sense_making": {str(k): v for k, v in sense.items()},
            "distributed_cognition": distrib,
            "eml_depth": {"coupling": 1, "external_memory": 0,
                          "sense_making_product": 2, "cognitive_boundary": "∞"},
            "key_insight": "Internal memory decay = EML-1; cognitive boundary itself = EML-∞ (Clark-Chalmers)"
        }


@dataclass
class PredictiveProcessingDeep:
    """Friston's free energy, active inference — EML depth of prediction."""

    def free_energy_bound(self, prediction: float, observation: float,
                          precision: float = 1.0) -> float:
        """
        F = precision/2 * (obs - pred)² + log(2π/precision)/2. EML-2.
        Free energy = upper bound on surprise = -log P(obs).
        """
        squared_error = (observation - prediction) ** 2
        log_term = 0.5 * math.log(2 * math.pi / (precision + 1e-12))
        return round(0.5 * precision * squared_error + log_term, 6)

    def variational_message_passing(self, mu: float, sigma2: float,
                                    obs: float, obs_var: float) -> dict[str, float]:
        """
        Gaussian belief update: posterior μ' = (μ/σ² + obs/obs_var) / (1/σ² + 1/obs_var).
        EML-2 (ratio of Gaussian parameters).
        """
        precision_prior = 1.0 / (sigma2 + 1e-12)
        precision_likelihood = 1.0 / (obs_var + 1e-12)
        mu_post = (mu * precision_prior + obs * precision_likelihood) / (
            precision_prior + precision_likelihood)
        sigma2_post = 1.0 / (precision_prior + precision_likelihood)
        return {
            "prior_mu": mu, "prior_sigma2": sigma2,
            "observation": obs, "obs_var": obs_var,
            "posterior_mu": round(mu_post, 6),
            "posterior_sigma2": round(sigma2_post, 6),
            "eml_depth": 2
        }

    def active_inference_action(self, free_energy_gradient: float,
                                 learning_rate: float = 0.1) -> float:
        """
        Active inference: a = -α * ∂F/∂a. EML-2 (gradient descent on free energy).
        Action reduces expected free energy. EML-∞ when action resolves ambiguity.
        """
        return round(-learning_rate * free_energy_gradient, 6)

    def allostasis_depth(self, set_point: float, current: float,
                          predicted_threat: float) -> dict[str, Any]:
        """
        Allostasis: predict future needs and act preemptively.
        Allostatic load = EML-2 (chronic deviation). Allostatic collapse = EML-∞.
        """
        homeostatic_error = abs(current - set_point)
        allostatic_burden = homeostatic_error * math.exp(predicted_threat)
        is_collapse = allostatic_burden > 10.0
        return {
            "set_point": set_point, "current": current,
            "homeostatic_error": round(homeostatic_error, 4),
            "predicted_threat": predicted_threat,
            "allostatic_burden": round(allostatic_burden, 4),
            "allostatic_collapse": is_collapse,
            "eml_depth": "∞ (collapse)" if is_collapse else "2 (burden)"
        }

    def analyze(self) -> dict[str, Any]:
        fe_vals = {(pred, obs): self.free_energy_bound(pred, obs)
                   for pred, obs in [(0.0, 0.5), (1.0, 0.8), (0.0, 2.0)]}
        vmp = self.variational_message_passing(mu=0.0, sigma2=1.0, obs=0.5, obs_var=0.25)
        actions = {g: self.active_inference_action(g) for g in [-1.0, -0.5, 0.0, 0.5, 1.0]}
        allostasis = {t: self.allostasis_depth(0.0, 1.0, t) for t in [0.5, 1.0, 2.5]}
        return {
            "model": "PredictiveProcessingDeep",
            "free_energy_vals": {str(k): v for k, v in fe_vals.items()},
            "variational_message_passing": vmp,
            "active_inference_actions": actions,
            "allostasis": allostasis,
            "eml_depth": {"free_energy": 2, "belief_update": 2,
                          "active_inference": 2, "allostatic_collapse": "∞"},
            "key_insight": "Free energy = EML-2; allostatic collapse = EML-∞; action = gradient descent (EML-2)"
        }


def analyze_cognition_v4_eml() -> dict[str, Any]:
    embodied = EmbodiedCognition(body_dof=7)
    extended = ExtendedMind()
    predictive = PredictiveProcessingDeep()
    return {
        "session": 154,
        "title": "Cognition Deep IV: Embodied Cognition, Enactivism & 4E Approaches",
        "eml_operator": "eml(x,y) = exp(x) - ln(y)",
        "embodied_cognition": embodied.analyze(),
        "extended_mind": extended.analyze(),
        "predictive_processing": predictive.analyze(),
        "eml_depth_summary": {
            "EML-0": "Semitone counts, linear body schema update, cognitive capacity",
            "EML-1": "Internal memory decay exp(-λt), organism-environment coupling exp(-|diff|)",
            "EML-2": "Free energy bound, variational inference, allostatic burden, sense-making",
            "EML-3": "Forward kinematics (trig), sensorimotor loop oscillations",
            "EML-∞": "Kinematic singularity, cognitive boundary (extended mind), allostatic collapse, meaning"
        },
        "key_theorem": (
            "The EML 4E Cognition Theorem: "
            "Body kinematics is EML-3 (trigonometric); kinematic singularity is EML-∞. "
            "Free energy and Bayesian belief update are EML-2 (quadratic forms). "
            "The cognitive boundary — the irreducible organism-environment coupling — is EML-∞: "
            "no EML-finite function captures where the mind ends and the world begins. "
            "Meaning, sense-making, and normativity are EML-∞: "
            "they cannot be reduced to any EML-finite computation."
        ),
        "rabbit_hole_log": [
            "Forward kinematics = EML-3: Σcos(θ₁+...+θ_n) = EML-3 (trig sums)",
            "Kinematic singularity = EML-∞: same class as phase transitions",
            "Internal memory exp(-λt) = EML-1: same as Kondo T_K, BCS gap",
            "Free energy F = EML-2: squared prediction error (same as predictive coding from S141)",
            "Allostatic collapse = EML-∞: tipping point of the organism (same as climate tipping!)",
            "Cognitive boundary = EML-∞: Clark-Chalmers parity principle violates EML-finite closure"
        ],
        "connections": {
            "S141_cognition_v3": "Extends binding/qualia with embodied + extended mind EML analysis",
            "S131_cognition_v2": "Free energy from S131 predictive coding → deeper here with 4E",
            "S147_climate_tipping": "Allostatic collapse ↔ climate tipping: same EML-∞ structure",
            "S152_chaos_control": "Kinematic singularity ↔ bifurcation: both EML-∞ loss of control"
        }
    }


if __name__ == "__main__":
    import json
    print(json.dumps(analyze_cognition_v4_eml(), indent=2, default=str))
