"""Session 870 --- The Smell of Rain - Petrichor Depth"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any

@dataclass
class SmellOfRainEML:
    def depth_analysis(self) -> dict[str, Any]:
        return {
            "object": "T591: The Smell of Rain - Petrichor Depth depth analysis",
            "domains": {
                "spore_eml1": {"description": "Geosmin released from bacterial spores by raindrops: EML-1 aerosol dispersal", "depth": "EML-1", "reason": "Petrichor dispersal is EML-1: exponential aerosol spread from impact sites"},
                "olfactory_eml2": {"description": "Olfactory detection: logarithmic Weber-Fechner; EML-2", "depth": "EML-2", "reason": "Petrichor detection is EML-2: log-scale olfactory sensitivity (few parts per trillion)"},
                "nostalgia_emlinf": {"description": "Emotional experience of rain smell: memory trigger; possibly EML-inf", "depth": "EML-inf", "reason": "Nostalgia triggered by petrichor is EML-inf: involuntary full memory reconstruction"},
                "nostalgia_classifier": {"description": "Nostalgia is a depth classifier: EML-1 chemistry -> EML-2 detection -> EML-inf meaning", "depth": "EML-inf", "reason": "Smell of rain is EML-1 physical -> EML-2 perception -> EML-inf emotional portal"},
            },
        }
    def analyze(self) -> dict[str, Any]:
        depths = [v['depth'] for v in self.depth_analysis()['domains'].values()]
        dist: dict[str, int] = {}
        for d in depths: dist[d] = dist.get(d, 0) + 1
        return {
            "model": "SmellOfRainEML",
            "analysis": self.depth_analysis(),
            "distribution": dist,
            "theorem": "T591: The Smell of Rain - Petrichor Depth (S870).",
        }

def analyze_smell_of_rain_eml() -> dict[str, Any]:
    t = SmellOfRainEML()
    return {
        "session": 870,
        "title": "The Smell of Rain - Petrichor Depth",
        "eml_operator": "eml(x,y) = exp(x) - ln(y)",
        "analysis": t.analyze(),
        "key_theorem": "T591: The Smell of Rain - Petrichor Depth (S870).",
        "rabbit_hole_log": ["T591: spore_eml1 depth confirmed"],
    }

if __name__ == "__main__":
    import json
    print(json.dumps(analyze_smell_of_rain_eml(), indent=2, default=str))