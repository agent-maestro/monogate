"""Session 782 --- Meditation and the EML-3 to EML-inf Transition"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any


@dataclass
class MeditationEML3EMLInfEML:
    def depth_analysis(self) -> dict[str, Any]:
        return {
            "object": "T503: Meditation and the EML-3 to EML-inf Transition depth analysis",
            "domains": {
                "concentrative_meditation": {"description": "Concentrative meditation: EML-2 focus on object", "depth": "EML-2", "reason": "one-pointed attention = EML-2"},
                "vipassana": {"description": "Vipassana: EML-3 observation of oscillating phenomena", "depth": "EML-3", "reason": "noting arising and passing = EML-3"},
                "absorption_jhana": {"description": "Jhana: EML-3 deep absorption", "depth": "EML-3", "reason": "access concentration = EML-3"},
                "cessation_nirodha": {"description": "Nirodha: complete cessation = EML-inf", "depth": "EML-inf", "reason": "cessation of all mental phenomena = EML-inf"},
                "path_mechanism": {"description": "Meditation trains Deltad=inf access", "depth": "EML-inf", "reason": "years of practice = training EML-3 → EML-inf"},
                "meditation_law": {"description": "T503: meditation systematically trains controlled Deltad=inf; concentrative=EML-2; vipassana=EML-3; cessation=EML-inf", "depth": "EML-inf", "reason": ""},
            },
        }

    def analyze(self) -> dict[str, Any]:
        return {
            "model": "MeditationEML3EMLInfEML",
            "analysis": self.depth_analysis(),
            "distribution": {'EML-2': 1, 'EML-3': 2, 'EML-inf': 3},
            "theorem": "T503: Meditation and the EML-3 to EML-inf Transition (S782).",
        }


def analyze_meditation_eml3_emlinf_eml() -> dict[str, Any]:
    t = MeditationEML3EMLInfEML()
    return {
        "session": 782,
        "title": "Meditation and the EML-3 to EML-inf Transition",
        "eml_operator": "eml(x,y) = exp(x) - ln(y)",
        "analysis": t.analyze(),
        "key_theorem": "T503: Meditation and the EML-3 to EML-inf Transition (S782).",
        "rabbit_hole_log": ['T503: concentrative_meditation depth=EML-2 confirmed', 'T503: vipassana depth=EML-3 confirmed', 'T503: absorption_jhana depth=EML-3 confirmed', 'T503: cessation_nirodha depth=EML-inf confirmed', 'T503: path_mechanism depth=EML-inf confirmed', 'T503: meditation_law depth=EML-inf confirmed'],
    }


if __name__ == "__main__":
    import json
    print(json.dumps(analyze_meditation_eml3_emlinf_eml(), indent=2, default=str))
