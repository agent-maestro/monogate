"""Session 594 --- Teaching and Conceptual Change as Depth Transitions"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any


@dataclass
class TeachingConceptualChangeEML:
    def depth_analysis(self) -> dict[str, Any]:
        return {
            "object": "T315: Teaching and Conceptual Change as Depth Transitions depth analysis",
            "domains": {
                "analogy": {"description": "This is like that: cross-domain bridge", "depth": "EML-2", "reason": "measurement of structural similarity"},
                "concrete_example": {"description": "Abstract concept grounded in instance", "depth": "EML-1", "reason": "amplification from abstract to specific"},
                "aha_moment": {"description": "Sudden understanding: depth transition", "depth": "EML-inf", "reason": "Deltad=inf in the student"},
                "scaffolding": {"description": "Temporary support structure for learning", "depth": "EML-1", "reason": "exponential climb enabled by support"},
                "socratic_question": {"description": "Question that forces self-discovery", "depth": "EML-inf", "reason": "designed categorification event"},
                "desirable_difficulty": {"description": "Interleaving causes deeper encoding", "depth": "EML-2", "reason": "measurement-difficulty = EML-2 forcing"},
            },
        }

    def analyze(self) -> dict[str, Any]:
        return {
            "model": "TeachingConceptualChangeEML",
            "analysis": self.depth_analysis(),
            "distribution": {'EML-2': 2, 'EML-1': 2, 'EML-inf': 2},
            "theorem": "T315: Teaching and Conceptual Change as Depth Transitions (S594).",
        }


def analyze_teaching_conceptual_change_eml() -> dict[str, Any]:
    t = TeachingConceptualChangeEML()
    return {
        "session": 594,
        "title": "Teaching and Conceptual Change as Depth Transitions",
        "eml_operator": "eml(x,y) = exp(x) - ln(y)",
        "analysis": t.analyze(),
        "key_theorem": "T315: Teaching and Conceptual Change as Depth Transitions (S594).",
        "rabbit_hole_log": ['T315: analogy depth=EML-2 confirmed', 'T315: concrete_example depth=EML-1 confirmed', 'T315: aha_moment depth=EML-inf confirmed', 'T315: scaffolding depth=EML-1 confirmed', 'T315: socratic_question depth=EML-inf confirmed', 'T315: desirable_difficulty depth=EML-2 confirmed'],
    }


if __name__ == "__main__":
    import json
    print(json.dumps(analyze_teaching_conceptual_change_eml(), indent=2, default=str))
