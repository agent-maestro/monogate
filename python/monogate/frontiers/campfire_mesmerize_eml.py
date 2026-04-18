"""Session 944 --- Why a Campfire Mesmerizes"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any

@dataclass
class CampfireMesmerizeEML:
    def depth_analysis(self) -> dict[str, Any]:
        return {
            "object": "T665: Why a Campfire Mesmerizes depth analysis",
            "domains": {
                "flame_eml3": {"description": "Flame flicker: EML-3 oscillatory; 10-12 Hz", "depth": "EML-3", "reason": "Campfire flicker is EML-3: stochastic oscillatory combustion; complex enough to resist prediction"},
                "ember_eml1": {"description": "Ember glow: EML-1 exponential decay cooling", "depth": "EML-1", "reason": "Ember decay is EML-1: exponential temperature decrease; hypnotic slow glow"},
                "trance_shift": {"description": "Firegazing: voluntary depth shift from EML-2 analytical to EML-3 oscillatory absorption", "depth": "EML-3", "reason": "Campfire trance is EML-3 absorption: EML-2 analytical thinking suspends; EML-3 oscillatory mode dominates"},
                "natural_meditation": {"description": "Campfire is natural meditation device (T503): voluntary EML-3->EML-inf boundary approach", "depth": "EML-inf", "reason": "Campfire theorem: staring at fire is controlled depth descent; natural version of meditation EML-3->EML-inf"},
            },
        }
    def analyze(self) -> dict[str, Any]:
        depths = [v['depth'] for v in self.depth_analysis()['domains'].values()]
        dist: dict[str, int] = {}
        for d in depths: dist[d] = dist.get(d, 0) + 1
        return {
            "model": "CampfireMesmerizeEML",
            "analysis": self.depth_analysis(),
            "distribution": dist,
            "theorem": "T665: Why a Campfire Mesmerizes (S944).",
        }

def analyze_campfire_mesmerize_eml() -> dict[str, Any]:
    t = CampfireMesmerizeEML()
    return {
        "session": 944,
        "title": "Why a Campfire Mesmerizes",
        "eml_operator": "eml(x,y) = exp(x) - ln(y)",
        "analysis": t.analyze(),
        "key_theorem": "T665: Why a Campfire Mesmerizes (S944).",
        "rabbit_hole_log": ["T665: flame_eml3 depth confirmed"],
    }

if __name__ == "__main__":
    import json
    print(json.dumps(analyze_campfire_mesmerize_eml(), indent=2, default=str))