"""
Session 146 — Linguistics Deep III: Emergence of Meaning & Deep Compositionality

EML operator: eml(x,y) = exp(x) - ln(y)
Key theorem: Semantic emergence — how meaning arises from meaningless symbols —
is EML-∞ (the symbol grounding problem). All formal semantic operations are EML-0 to EML-2.
"""
from __future__ import annotations
import math
from dataclasses import dataclass
from typing import Any


@dataclass
class SymbolGrounding:
    """Harnad (1990): symbol grounding problem — how symbols acquire meaning."""

    n_symbols: int = 1000
    n_referents: int = 10000

    def grounding_by_similarity(self, v1: list[float], v2: list[float]) -> float:
        """Cosine similarity as grounding proxy. EML-0."""
        dot = sum(a * b for a, b in zip(v1, v2))
        n1 = math.sqrt(sum(a ** 2 for a in v1))
        n2 = math.sqrt(sum(b ** 2 for b in v2))
        return dot / (n1 * n2 + 1e-15)

    def mutual_information_grounding(self, p_joint: float, p_sym: float, p_ref: float) -> float:
        """I(S;R) = log(P(s,r)/(P(s)P(r))). EML-2."""
        if p_joint <= 0 or p_sym <= 0 or p_ref <= 0:
            return 0.0
        return math.log(p_joint / (p_sym * p_ref))

    def symbol_grounding_gap(self) -> dict[str, str]:
        """The gap between syntactic manipulation and semantic content: EML-∞."""
        return {
            "formal_syntax": "EML-0 (structural manipulation)",
            "semantic_content": "EML-∞ (not derivable from syntax alone)",
            "grounding_step": "EML-∞ (the gap Searle's Chinese Room exposes)",
            "implication": "No EML-finite map: symbols → meanings"
        }

    def pragmatic_inference(self, literal_p: float, context_p: float) -> float:
        """
        Bayesian pragmatics (RSA): P(meaning | utterance) ∝ P(utterance | meaning) * P(meaning).
        EML-2 (Bayes = log-linear).
        """
        return literal_p * context_p / (literal_p * context_p + 1e-15)

    def analyze(self) -> dict[str, Any]:
        mi_examples = [
            self.mutual_information_grounding(0.01, 0.1, 0.1),
            self.mutual_information_grounding(0.05, 0.1, 0.1),
        ]
        pragmatic = {
            (0.8, 0.9): round(self.pragmatic_inference(0.8, 0.9), 4),
            (0.3, 0.9): round(self.pragmatic_inference(0.3, 0.9), 4),
            (0.8, 0.2): round(self.pragmatic_inference(0.8, 0.2), 4),
        }
        return {
            "model": "SymbolGrounding",
            "mutual_information_examples": [round(m, 4) for m in mi_examples],
            "pragmatic_inference_examples": {str(k): v for k, v in pragmatic.items()},
            "symbol_grounding_gap": self.symbol_grounding_gap(),
            "eml_depth": {"syntactic_operations": 0, "MI_grounding": 2,
                          "pragmatic_inference": 2, "symbol_grounding_itself": "∞"},
            "key_insight": "Symbol grounding = EML-∞: no EML-finite map from syntax to semantics"
        }


@dataclass
class MetaphorAndConceptualBlending:
    """Fauconnier & Turner: conceptual blending creates new meaning. EML-∞ emergence."""

    def blending_integration(self, input1_dim: int, input2_dim: int) -> dict[str, Any]:
        """
        Blended space has emergent structure not in either input.
        Selectivity: log(|blend|/|inputs|). EML-2 (log of ratio).
        But the emergent structure itself = EML-∞.
        """
        blend_dim = int(math.sqrt(input1_dim * input2_dim))  # EML-2: geometric mean
        selectivity = math.log(blend_dim / ((input1_dim + input2_dim) / 2))
        return {
            "input1_dim": input1_dim,
            "input2_dim": input2_dim,
            "blend_dim": blend_dim,
            "selectivity": round(selectivity, 4),
            "emergent_structure": "EML-∞"
        }

    def metaphor_productivity(self, source_domain: int, target_domain: int) -> float:
        """Number of mappings: log(|source| * |target|). EML-2."""
        return math.log(source_domain) + math.log(target_domain)

    def figurative_vs_literal(self) -> dict[str, str]:
        """Literal language = EML-2; figurative/novel metaphor = EML-∞."""
        return {
            "literal_meaning": "EML-2 (conventional, stored in distributional space)",
            "dead_metaphor": "EML-2 (conventional figurative = same as literal)",
            "live_metaphor": "EML-∞ (novel cross-domain blend = not EML-finite computable)",
            "irony": "EML-∞ (meaning = opposite of literal: EML-∞ inversion)",
            "humour_incongruity": "EML-∞ (violation of expectation = EML-∞ surprise)"
        }

    def analyze(self) -> dict[str, Any]:
        blends = [self.blending_integration(100, 200),
                  self.blending_integration(50, 500)]
        productivity = {(10, 10): round(self.metaphor_productivity(10, 10), 4),
                        (100, 50): round(self.metaphor_productivity(100, 50), 4)}
        return {
            "model": "MetaphorAndConceptualBlending",
            "blending_examples": blends,
            "metaphor_productivity": {str(k): v for k, v in productivity.items()},
            "figurative_vs_literal": self.figurative_vs_literal(),
            "eml_depth": {"blend_geometry": 2, "metaphor_productivity": 2,
                          "live_metaphor_meaning": "∞"},
            "key_insight": "Conceptual blending is EML-2 (geometric mean dim); emergence = EML-∞"
        }


@dataclass
class LanguageEvolutionAndOrigin:
    """How did language evolve? Cultural evolution of communication systems."""

    pop_size: int = 10000
    mutation_rate: float = 0.001

    def cultural_evolution_rate(self, n_learners: int, n_teachers: int) -> float:
        """Cultural change rate ~ n_learners/n_teachers * mutation_rate. EML-0."""
        return (n_learners / n_teachers) * self.mutation_rate

    def expressiveness_growth(self, t: float) -> float:
        """
        Expressiveness E(t) = E0 * exp(r * t) until saturation. EML-1.
        Language diversification follows similar exponential dynamics.
        """
        r = 0.02
        E0 = 1.0
        sat = 1000.0
        return sat * E0 * math.exp(r * t) / (sat + E0 * (math.exp(r * t) - 1))

    def language_divergence(self, t: float, mu: float = 0.01) -> float:
        """Levenshtein distance growth: D(t) = 1 - exp(-mu*t). EML-1."""
        return 1 - math.exp(-mu * t)

    def language_origin_gap(self) -> dict[str, str]:
        """The origin of language: crossing the threshold from signal to symbol = EML-∞."""
        return {
            "animal_signaling": "EML-1 (graded, continuous)",
            "protolanguage": "EML-2 (compositional fragments)",
            "full_language_with_recursion": "EML-∞ (infinite expressiveness via recursion)",
            "origin_transition": "EML-∞ (the crossing itself is irreversible and non-analytic)"
        }

    def analyze(self) -> dict[str, Any]:
        t_vals = [0, 50, 100, 500, 1000, 5000]
        expressiveness = {t: round(self.expressiveness_growth(t), 2) for t in t_vals}
        divergence = {t: round(self.language_divergence(t), 4) for t in t_vals}
        return {
            "model": "LanguageEvolutionAndOrigin",
            "expressiveness_growth": expressiveness,
            "language_divergence": divergence,
            "language_origin_gap": self.language_origin_gap(),
            "eml_depth": {"expressiveness_growth": 1, "divergence": 1,
                          "language_origin": "∞"},
            "key_insight": "Language evolution = EML-1; origin transition (signal→symbol) = EML-∞"
        }


def analyze_linguistics_v3_eml() -> dict[str, Any]:
    grounding = SymbolGrounding()
    blending = MetaphorAndConceptualBlending()
    evolution = LanguageEvolutionAndOrigin()
    return {
        "session": 146,
        "title": "Linguistics Deep III: Emergence of Meaning & Deep Compositionality",
        "eml_operator": "eml(x,y) = exp(x) - ln(y)",
        "symbol_grounding": grounding.analyze(),
        "metaphor_and_blending": blending.analyze(),
        "language_evolution": evolution.analyze(),
        "eml_depth_summary": {
            "EML-0": "Formal syntactic operations (lambda, tree rewriting)",
            "EML-1": "Expressiveness growth, language divergence (1-exp(-μt))",
            "EML-2": "MI grounding, pragmatic inference (Bayesian), metaphor productivity",
            "EML-3": "No natural linguistic example at this level",
            "EML-∞": "Symbol grounding (syntax→semantics), live metaphor, language origin transition"
        },
        "key_theorem": (
            "The EML Semantic Emergence Theorem: "
            "All formal linguistic operations (syntax, compositionality, pragmatic inference) "
            "are EML-0 to EML-2. "
            "The emergence of meaning from symbols — the symbol grounding problem — is EML-∞: "
            "there is no EML-finite algorithm that takes a formal symbol system and outputs "
            "the semantic content it represents. "
            "This is Searle's Chinese Room in EML language."
        ),
        "rabbit_hole_log": [
            "Symbol grounding = EML-∞: Searle's insight = EML asymmetry theorem",
            "Pragmatic inference = Bayesian = EML-2 (same as free energy, PMI)",
            "Conceptual blend dim = geometric mean = EML-2; emergence = EML-∞",
            "Language origin: signal (EML-1) → symbol (EML-∞) = EML-∞ transition",
            "No EML-3 in linguistics: oscillations/waves don't naturally appear in semantics"
        ],
        "connections": {
            "S136_linguistics_v2": "Extends S136 with symbol grounding + metaphor + origin",
            "S131_cognition_v2": "Symbol grounding ↔ hard problem: both = EML-∞ explanatory gaps",
            "S140_grand_synthesis_8": "Language emergence = major transition = EML-∞ (per Horizon Theorem)"
        }
    }


if __name__ == "__main__":
    import json
    print(json.dumps(analyze_linguistics_v3_eml(), indent=2, default=str))
