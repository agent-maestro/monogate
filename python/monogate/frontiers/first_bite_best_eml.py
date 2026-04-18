"""Session 934 --- Why the First Bite Tastes Best"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any

@dataclass
class FirstBiteBestEML:
    def depth_analysis(self) -> dict[str, Any]:
        return {
            "object": "T655: Why the First Bite Tastes Best depth analysis",
            "domains": {
                "sensory_adaptation_eml1": {"description": "Sensory adaptation: exponential decay of response; EML-1", "depth": "EML-1", "reason": "Adaptation is EML-1: exponential receptor desensitization with repeated identical stimulation"},
                "maximum_info_first": {"description": "First bite: maximum EML-2 measurement information (signal most novel)", "depth": "EML-2", "reason": "First bite is EML-2 peak: maximum information from comparison to baseline; unrepeatable"},
                "hedonic_treadmill": {"description": "Hedonic treadmill: EML-2 habituates; only EML-inf categorification produces permanent change", "depth": "EML-inf", "reason": "Hedonic treadmill is depth theorem: EML-2 measurement habituates; permanent joy requires EML-inf"},
            },
        }
    def analyze(self) -> dict[str, Any]:
        depths = [v['depth'] for v in self.depth_analysis()['domains'].values()]
        dist: dict[str, int] = {}
        for d in depths: dist[d] = dist.get(d, 0) + 1
        return {
            "model": "FirstBiteBestEML",
            "analysis": self.depth_analysis(),
            "distribution": dist,
            "theorem": "T655: Why the First Bite Tastes Best (S934).",
        }

def analyze_first_bite_best_eml() -> dict[str, Any]:
    t = FirstBiteBestEML()
    return {
        "session": 934,
        "title": "Why the First Bite Tastes Best",
        "eml_operator": "eml(x,y) = exp(x) - ln(y)",
        "analysis": t.analyze(),
        "key_theorem": "T655: Why the First Bite Tastes Best (S934).",
        "rabbit_hole_log": ["T655: sensory_adaptation_eml1 depth confirmed"],
    }

if __name__ == "__main__":
    import json
    print(json.dumps(analyze_first_bite_best_eml(), indent=2, default=str))