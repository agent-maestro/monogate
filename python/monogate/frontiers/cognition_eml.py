"""
Session 101 — Consciousness & Cognitive Science: EML as Model of Thought

Modeling cognitive processes (attention switching, memory recall, insight, qualia)
as EML trees or basis expansions. Tests whether consciousness-like phenomena have
natural EML-depth signatures.

Key theorem: Routine cognitive processes (attention, working memory) are EML-2 or EML-3.
Insight moments (sudden restructuring) are EML-∞ → EML-3 transitions (like grokking).
Qualia (subjective experience) hypothesized as EML-∞ (irreducible, non-compressible).
Integrated Information Φ is EML-2 (logarithmic functional of cause-effect structure).
"""

from __future__ import annotations
import math, json
from dataclasses import dataclass, field


EML_INF = float("inf")


@dataclass
class AttentionModel:
    """
    Attention as a soft-max selection over EML-3 feature activations.

    Transformer attention: Attn(Q,K,V) = softmax(QKᵀ/√d)·V

    EML structure:
    - Q, K, V matrices: EML-2 (linear projections = matrix multiplication)
    - QKᵀ/√d: EML-2 (dot product / constant)
    - softmax(x_i) = exp(x_i)/Σ exp(x_j): EML-1 (single exp = ground state)
    - Attention-weighted output: EML-2 (linear combination after EML-1 weights)
    - Multi-head attention: EML-2 (concatenation of EML-2 heads)

    Cognitive interpretation:
    - Attention weight = EML-1 (Boltzmann distribution over relevance scores)
    - Focal attention (one item): EML-0 (delta function = max-entropy degenerate)
    - Diffuse attention (uniform): EML-1 (uniform Boltzmann = high temperature)
    - Switching between foci: EML-∞ → EML-1 (sudden reconfiguration)
    """

    def softmax_attention(self, scores: list[float], temperature: float = 1.0) -> dict:
        scaled = [s / temperature for s in scores]
        max_s = max(scaled)
        exps = [math.exp(s - max_s) for s in scaled]
        total = sum(exps)
        weights = [e / total for e in exps]
        entropy = -sum(w * math.log(w) if w > 1e-15 else 0 for w in weights)
        return {
            "scores": scores,
            "temperature": temperature,
            "attention_weights": [round(w, 6) for w in weights],
            "entropy_bits": round(entropy / math.log(2), 4),
            "eml_weights": 1,
            "eml_scores": 2,
            "reason": "softmax = Boltzmann distribution = EML-1",
        }

    def attention_switching_eml(self) -> list[dict]:
        """Simulate attention switching between two stimuli."""
        return [
            {
                "state": "Focused on stimulus A",
                "weights": [0.95, 0.05],
                "eml": 1,
                "reason": "Nearly degenerate Boltzmann = EML-1 near EML-0 limit",
            },
            {
                "state": "Switching (transitional)",
                "weights": [0.5, 0.5],
                "eml": EML_INF,
                "reason": "Unstable transition state: attention split = EML-∞ (like phase boundary)",
            },
            {
                "state": "Focused on stimulus B",
                "weights": [0.05, 0.95],
                "eml": 1,
                "reason": "New EML-1 ground state after switching",
            },
        ]

    def to_dict(self) -> dict:
        return {
            "attention_mechanism": "softmax(QKᵀ/√d)·V: EML-1 weights × EML-2 values",
            "focused_attention": self.softmax_attention([5.0, 0.5, 0.3], 1.0),
            "diffuse_attention": self.softmax_attention([1.0, 1.0, 1.0], 1.0),
            "high_temp": self.softmax_attention([5.0, 0.5, 0.3], 5.0),
            "switching": self.attention_switching_eml(),
            "eml_softmax": 1,
            "eml_scores": 2,
        }


@dataclass
class WorkingMemoryEML:
    """
    Working memory as a dynamical system with limited capacity (Miller: 7±2 items).

    EML structure:
    - Memory item activation a_i(t): EML-1 (exponential decay a_i ~ exp(-t/τ))
    - Rehearsal loop: EML-3 (oscillatory refresh ~ sin(ωt) refresh cycle)
    - Forgetting curve (Ebbinghaus): R(t) = exp(-t/S): EML-1
    - Capacity limit: EML-0 (integer: 7±2)
    - Chunking: EML-2 (hierarchical grouping = logarithmic compression)

    Memory consolidation (short → long term):
    - STM → LTM: EML-1 decay of STM, EML-3 replay during sleep (hippocampal oscillations)
    - LTM retrieval: EML-3 (pattern completion via associative oscillation)
    """

    def ebbinghaus_retention(self, t_hours: float, strength: float = 1.0) -> dict:
        R = math.exp(-t_hours / (strength * 24))
        return {
            "t_hours": t_hours,
            "retention_fraction": round(R, 4),
            "eml": 1,
            "reason": "R(t) = exp(-t/S): EML-1 exponential forgetting",
        }

    def capacity_limit_eml(self) -> dict:
        return {
            "miller_capacity": "7±2 items",
            "eml_capacity": 0,
            "eml_item_activation": 1,
            "eml_rehearsal": 3,
            "eml_chunking": 2,
            "chunking_insight": "Chunking: N items → log_k(N) chunks = EML-2 (logarithmic compression reduces EML-0 count)",
        }

    def to_dict(self) -> dict:
        times = [0.5, 1, 4, 24, 168]
        return {
            "ebbinghaus_curve": [self.ebbinghaus_retention(t) for t in times],
            "capacity": self.capacity_limit_eml(),
            "sleep_replay": {
                "theta_oscillation": "4-8 Hz hippocampal theta: EML-3 (oscillation during REM)",
                "consolidation": "EML-3 replay → EML-2 consolidated trace (depth reduction through sleep)",
                "eml_stm": 1,
                "eml_ltm": 2,
            },
        }


@dataclass
class InsightAndQualia:
    """
    Insight (Aha! moments): sudden restructuring of problem representation.
    Analogous to grokking (Session 96): EML-∞ random search → EML-3 structured solution.

    Qualia (subjective experience): the 'what it's like' aspect.
    Hard problem of consciousness: why does physical processing generate subjective experience?

    EML hypothesis for qualia:
    - Neural correlates of consciousness (NCC): EML-3 (40 Hz gamma oscillations)
    - Binding problem: integration of EML-3 features → EML-∞? (irreducible unity of experience)
    - Qualia themselves: EML-∞ (cannot be described by any finite EML tree from observer's view)
    - Integrated Information Φ: EML-2 (logarithm of cause-effect repertoire)
    """

    def integrated_information(self, n_nodes: int, connectivity: float) -> dict:
        """
        Tononi's Φ: simplified estimate for a complete graph of n nodes.
        Φ ≈ n · log(1/(1-connectivity)) for strongly connected networks.
        """
        if connectivity <= 0 or connectivity >= 1:
            phi = 0 if connectivity <= 0 else float("inf")
        else:
            phi = n_nodes * math.log(1 / (1 - connectivity))
        return {
            "n_nodes": n_nodes,
            "connectivity": connectivity,
            "phi_approx": round(phi, 4) if phi < 1e9 else "→∞",
            "eml": 2,
            "reason": "Φ ≈ n·log(1/(1-c)): EML-2 (logarithm of rational function)",
        }

    def aha_moment_dynamics(self) -> list[dict]:
        return [
            {
                "phase": "Impasse (stuck)",
                "representation": "Fixed wrong frame, exhaustive EML-∞ search",
                "eml": EML_INF,
                "description": "Random search in wrong solution space = EML-∞ (incompressible)",
            },
            {
                "phase": "Incubation",
                "representation": "Background spreading activation = EML-3 (oscillatory diffusion)",
                "eml": 3,
                "description": "Unconscious diffusion of activation: EML-3 spatial oscillation in neural space",
            },
            {
                "phase": "Insight flash",
                "representation": "Sudden restructuring: EML-∞ → EML-3 transition",
                "eml": EML_INF,
                "description": "The transition instant itself is EML-∞ (discontinuous reconfiguration)",
            },
            {
                "phase": "Post-insight",
                "representation": "New EML-3 structured frame",
                "eml": 3,
                "description": "Problem now has compact EML-3 solution — depth reduced",
            },
        ]

    def to_dict(self) -> dict:
        return {
            "insight_dynamics": self.aha_moment_dynamics(),
            "integrated_information": [
                self.integrated_information(10, 0.3),
                self.integrated_information(100, 0.5),
                self.integrated_information(1000, 0.7),
            ],
            "qualia_hypothesis": {
                "ncc_gamma_40hz": "EML-3 (oscillation)",
                "binding_unity": "EML-∞ (irreducible integration?)",
                "phi_iit": "EML-2 (logarithmic functional)",
                "hard_problem": "Qualia may be EML-∞: no finite EML tree can generate subjective 'redness'",
                "eml_consciousness": "EML-3 (measurable correlates) + EML-∞ (irreducible qualia) = hybrid",
            },
        }


@dataclass
class CognitivePhaseDiagram:
    """
    Cognitive phase diagram: different states of mind mapped to EML classes.

    - Deep sleep / anesthesia: EML-0 (minimal activity, near ground state)
    - Dreamless sleep / slow wave: EML-1 (synchronized slow oscillations = EML-1 ground state)
    - REM / dreaming: EML-3 (narrative oscillation, memory replay)
    - Focused attention / flow: EML-2 or EML-3 (structured task processing)
    - Creativity / divergent thinking: EML-3 (broad search, recombination)
    - Psychosis / mania: EML-∞ (disordered, incompressible thought patterns)
    - Insight / meditation peak: EML-3 → EML-2 (deepening structure)
    """

    COGNITIVE_STATES = [
        {"state": "Deep anesthesia", "eml": 0, "oscillation": "None", "phi": "~0"},
        {"state": "Slow-wave sleep", "eml": 1, "oscillation": "0.5-2 Hz delta", "phi": "low"},
        {"state": "REM / dreaming", "eml": 3, "oscillation": "Theta 6-8 Hz", "phi": "medium"},
        {"state": "Focused attention", "eml": 2, "oscillation": "Beta 13-30 Hz", "phi": "medium-high"},
        {"state": "Flow state", "eml": 3, "oscillation": "Gamma 40 Hz", "phi": "high"},
        {"state": "Creativity / insight", "eml": 3, "oscillation": "Mixed theta+gamma", "phi": "high"},
        {"state": "Psychosis", "eml": EML_INF, "oscillation": "Disorganized", "phi": "disrupted"},
        {"state": "Meditation (deep)", "eml": 2, "oscillation": "Low-freq synchrony", "phi": "very high"},
    ]

    def to_dict(self) -> dict:
        states = []
        for s in self.COGNITIVE_STATES:
            entry = dict(s)
            if entry["eml"] == EML_INF:
                entry["eml"] = "∞"
            states.append(entry)
        return {
            "cognitive_phase_diagram": states,
            "key_insight": "Healthy cognition oscillates between EML-1 (rest) and EML-3 (active). Pathology = EML-∞ (disorganized) or EML-0 (vegetative). Insight = brief EML-∞ transition enabling EML-3 restructuring.",
        }


def analyze_cognition_eml() -> dict:
    attn = AttentionModel()
    mem = WorkingMemoryEML()
    insight = InsightAndQualia()
    phases = CognitivePhaseDiagram()
    return {
        "session": 101,
        "title": "Consciousness & Cognitive Science: EML as Model of Thought",
        "key_theorem": {
            "theorem": "EML Cognitive Depth Theorem",
            "statement": (
                "Cognitive processes follow the EML depth hierarchy: "
                "resting state = EML-1 (synchronized ground state). "
                "Attention = EML-1 (softmax = Boltzmann). "
                "Working memory capacity = EML-0 (7±2), decay = EML-1, rehearsal = EML-3. "
                "Insight = EML-∞ → EML-3 depth transition (like grokking in neural networks). "
                "Qualia = EML-∞ hypothesis (irreducible, non-compressible subjective experience). "
                "Integrated Information Φ = EML-2 (logarithmic). "
                "Psychosis = EML-∞ (disordered thought); deep meditation = EML-2 (structured stillness)."
            ),
        },
        "attention": attn.to_dict(),
        "working_memory": mem.to_dict(),
        "insight_qualia": insight.to_dict(),
        "cognitive_phases": phases.to_dict(),
        "eml_depth_summary": {
            "EML-0": "Vegetative state; discrete memory capacity 7±2; digit span",
            "EML-1": "Slow-wave sleep oscillation; attention weights (softmax); memory decay exp(-t/τ)",
            "EML-2": "Integrated information Φ; chunking compression; beta-wave focused attention",
            "EML-3": "REM replay; gamma oscillation NCC; insight post-restructuring; creativity",
            "EML-∞": "Qualia (hard problem); psychosis; attention switching instant; pre-insight impasse",
        },
        "rabbit_hole_log": [
            "Attention as Boltzmann: softmax weights are exactly exp(score_i)/Z = EML-1. The brain's attention mechanism computes the same distribution as statistical mechanics ground states. This suggests attention is a physical minimum-energy operation.",
            "Insight = grokking: the EML-∞ → EML-3 transition in Session 96 (modular arithmetic) mirrors the Aha! moment: random search (EML-∞) suddenly finds the compact structure (EML-3). Incubation = background EML-3 diffusion enabling the restructuring.",
            "The hard problem of consciousness: qualia resist EML classification because they're private. From a third-person (external) view, NCCs are EML-3 (measurable oscillations). But the first-person 'what it's like' may genuinely be EML-∞ — not because it's complex, but because no external formula captures it.",
        ],
        "connections": {
            "to_session_96": "Grokking = EML-∞→EML-3. Insight moments follow identical EML depth transition",
            "to_session_57": "Phase transitions = EML-∞. Attention switching = cognitive phase transition = EML-∞ at the moment",
        },
    }


if __name__ == "__main__":
    print(json.dumps(analyze_cognition_eml(), indent=2, default=str))
