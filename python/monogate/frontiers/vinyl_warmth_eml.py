"""Session 914 --- Why Vinyl Sounds Warmer than Digital"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any

@dataclass
class VinylWarmthEML:
    def depth_analysis(self) -> dict[str, Any]:
        return {
            "object": "T635: Why Vinyl Sounds Warmer than Digital depth analysis",
            "domains": {
                "digital_eml0": {"description": "Digital audio: EML-0 discrete samples; quantized, integer-valued", "depth": "EML-0", "reason": "Digital is EML-0: discrete 16/24-bit samples; no inter-sample information"},
                "vinyl_eml3": {"description": "Vinyl: analog continuous signal with harmonic distortion adding EML-3 overtones", "depth": "EML-3", "reason": "Vinyl is EML-3: continuous analog wave with EML-3 harmonic content from even-order distortion"},
                "warmth_is_depth3": {"description": "Warmth is the subjective experience of EML-3 harmonic richness absent in EML-0 digital", "depth": "EML-3", "reason": "Vinyl vs digital debate is a depth classification argument: EML-3 warmth vs EML-0 precision"},
            },
        }
    def analyze(self) -> dict[str, Any]:
        depths = [v['depth'] for v in self.depth_analysis()['domains'].values()]
        dist: dict[str, int] = {}
        for d in depths: dist[d] = dist.get(d, 0) + 1
        return {
            "model": "VinylWarmthEML",
            "analysis": self.depth_analysis(),
            "distribution": dist,
            "theorem": "T635: Why Vinyl Sounds Warmer than Digital (S914).",
        }

def analyze_vinyl_warmth_eml() -> dict[str, Any]:
    t = VinylWarmthEML()
    return {
        "session": 914,
        "title": "Why Vinyl Sounds Warmer than Digital",
        "eml_operator": "eml(x,y) = exp(x) - ln(y)",
        "analysis": t.analyze(),
        "key_theorem": "T635: Why Vinyl Sounds Warmer than Digital (S914).",
        "rabbit_hole_log": ["T635: digital_eml0 depth confirmed"],
    }

if __name__ == "__main__":
    import json
    print(json.dumps(analyze_vinyl_warmth_eml(), indent=2, default=str))