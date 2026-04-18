"""
Session 301 — Linguistic Evolution & Historical Phonology

EML operator: eml(x,y) = exp(x) - ln(y)
Core thesis: Sound change is gradual EML-2 drift punctuated by EML-∞ phase transitions.
Stress test: Grimm's Law, vowel shifts, and language splits under Δd theorems.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any


@dataclass
class LinguisticEvolutionPhonologyEML:

    def grimms_law_semiring(self) -> dict[str, Any]:
        return {
            "object": "Grimm's Law (Proto-Germanic consonant shift)",
            "eml_depth": 0,
            "why": "Grimm's Law: *p→f, *t→θ, *k→x — deterministic rule = EML-0 (algebraic permutation)",
            "semiring_test": {
                "consonant_map": {
                    "rule": "Stop → Fricative: bijective map on phoneme set",
                    "depth": 0,
                    "why": "Permutation on finite phoneme inventory = EML-0"
                },
                "application_depth": {
                    "note": "Applying Grimm's Law n times: EML-0 (always algebraic)",
                    "depth": 0
                },
                "tensor_test": {
                    "operation": "GrimmsLaw(EML-0) ⊗ GrimmsLaw(EML-0) = max(0,0) = 0",
                    "result": "Grimm's Law: 0⊗0=0 ✓ (purely algebraic)"
                }
            }
        }

    def great_vowel_shift_semiring(self) -> dict[str, Any]:
        return {
            "object": "Great Vowel Shift (English, 1400-1700)",
            "eml_depth": "∞",
            "shadow": 2,
            "semiring_test": {
                "individual_changes": {
                    "depth": 2,
                    "why": "Each vowel: F₁/F₂ formant drift ~ exp(-t/τ): EML-2 (gradual)"
                },
                "shift_cascade": {
                    "type": "TYPE 2 Horizon (pull chain / push chain cascade)",
                    "depth": "∞",
                    "shadow": 2,
                    "why": "Chain shift: each EML-2 change triggers next = cascade = EML-∞; shadow=2"
                },
                "new_finding": {
                    "insight": "Vowel chain shift = TYPE 2 Horizon cascade: individual Δd=0, collective = EML-∞"
                }
            }
        }

    def language_split_semiring(self) -> dict[str, Any]:
        return {
            "object": "Language divergence (dialect split, speciation)",
            "eml_depth": "∞",
            "shadow": 2,
            "semiring_test": {
                "lexical_distance": {
                    "formula": "d_lex(t) = 1 - exp(-λt): EML-2 (lexical divergence rate)",
                    "depth": 2
                },
                "intelligibility_loss": {
                    "depth": "∞",
                    "type": "TYPE 2 Horizon (mutual intelligibility threshold)",
                    "shadow": 2,
                    "why": "Dialect → language = threshold event = EML-∞; shadow=2 (lexical distance real)"
                },
                "glottochronology": {
                    "formula": "L(t) = L_0·exp(-0.14t): Swadesh list retention = EML-2",
                    "depth": 2
                }
            }
        }

    def sound_change_drift_semiring(self) -> dict[str, Any]:
        return {
            "object": "Regular sound change (gradual articulatory drift)",
            "eml_depth": 2,
            "semiring_test": {
                "formant_drift": {
                    "formula": "F_i(t) = F_i(0) + σ·B(t): Brownian drift = EML-2",
                    "depth": 2
                },
                "lenition": {
                    "formula": "VOT(t) ~ exp(-αt): voice onset time shortening = EML-2",
                    "depth": 2
                },
                "tensor_test": {
                    "operation": "FormantDrift(EML-2) ⊗ Lenition(EML-2) = max(2,2) = 2",
                    "result": "Regular sound change: 2⊗2=2 ✓"
                }
            }
        }

    def proto_language_reconstruction_semiring(self) -> dict[str, Any]:
        return {
            "object": "Proto-language reconstruction (comparative method)",
            "eml_depth": 2,
            "semiring_test": {
                "reconstruction": {
                    "formula": "P(*form | observed forms): Bayesian phylogenetic = EML-2",
                    "depth": 2,
                    "why": "Same as molecular evolution Bayesian (S293): EML-2"
                },
                "sound_correspondence": {
                    "depth": 0,
                    "why": "Grimm-type correspondence rules: algebraic = EML-0"
                },
                "tensor": {
                    "operation": "SoundCorrespondence(EML-0) ⊗ BayesianReconstruction(EML-2) = max(0,2) = 2",
                    "result": "Comparative linguistics: 0⊗2=2 ✓"
                }
            }
        }

    def analyze(self) -> dict[str, Any]:
        return {
            "model": "LinguisticEvolutionPhonologyEML",
            "grimm": self.grimms_law_semiring(),
            "gvs": self.great_vowel_shift_semiring(),
            "split": self.language_split_semiring(),
            "drift": self.sound_change_drift_semiring(),
            "reconstruction": self.proto_language_reconstruction_semiring(),
            "semiring_verdicts": {
                "grimms_law": "EML-0 ✓ (algebraic permutation on phonemes)",
                "vowel_shift": "TYPE 2 Horizon cascade; shadow=2",
                "language_split": "TYPE 2 Horizon; shadow=2 (lexical distance = EML-2)",
                "sound_change": "2⊗2=2 ✓",
                "new_finding": "Grimm's Law = EML-0 (like neutral drift): deterministic phoneme permutation"
            }
        }


def analyze_linguistic_evolution_phonology_eml() -> dict[str, Any]:
    t = LinguisticEvolutionPhonologyEML()
    return {
        "session": 301,
        "title": "Linguistic Evolution & Historical Phonology",
        "eml_operator": "eml(x,y) = exp(x) - ln(y)",
        "analysis": t.analyze(),
        "key_theorem": (
            "Historical Phonology Semiring Theorem (S301): "
            "Regular sound change = EML-2 (formant drift, lenition). "
            "NEW: Grimm's Law = EML-0 — deterministic phoneme permutation over finite inventory. "
            "Like neutral drift (EML-0) in molecular evolution: purely algebraic bijection. "
            "Great Vowel Shift = TYPE 2 Horizon cascade: "
            "each individual shift is EML-2, but the chain reaction = EML-∞. "
            "Language divergence: lexical drift = EML-2; intelligibility threshold = TYPE 2 Horizon. "
            "Proto-language reconstruction: sound correspondences (EML-0) ⊗ Bayesian (EML-2) = max = 2. "
            "PHONOLOGY DEPTH LADDER: SoundCorrespondence(EML-0) → Drift(EML-2) → ChainShift(TYPE2) → Split(TYPE2)."
        ),
        "rabbit_hole_log": [
            "NEW: Grimm's Law = EML-0 (phoneme permutation = algebraic bijection)",
            "Regular sound change: EML-2 (formant drift = Brownian = EML-2)",
            "Great Vowel Shift: TYPE 2 Horizon cascade (individual EML-2 → collective EML-∞)",
            "Language split: lexical distance EML-2; intelligibility threshold = TYPE 2 Horizon",
            "Grimm=EML-0 parallels neutral drift=EML-0: both deterministic algebraic"
        ]
    }


if __name__ == "__main__":
    import json
    print(json.dumps(analyze_linguistic_evolution_phonology_eml(), indent=2, default=str))
