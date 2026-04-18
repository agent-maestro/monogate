"""Session 926 --- Why We Cry at Weddings"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any

@dataclass
class CryingAtWeddingsEML:
    def depth_analysis(self) -> dict[str, Any]:
        return {
            "object": "T647: Why We Cry at Weddings depth analysis",
            "domains": {
                "ceremony_eml0": {"description": "Ceremony: EML-0 ritual; discrete steps, prescribed order", "depth": "EML-0", "reason": "Wedding ceremony is EML-0: ritualized discrete sequence; externally structured"},
                "commitment_emlinf": {"description": "Commitment: EML-inf categorification of two people into one unit", "depth": "EML-inf", "reason": "Marriage commitment is EML-inf: irreversible identity merger; two EML-inf consciousnesses becoming one"},
                "overflow": {"description": "Tears: body response to EML-inf event exceeding EML-0 ritual container", "depth": "EML-inf", "reason": "Crying at weddings is overflow: EML-0 ceremony cannot contain EML-inf event; tears are the excess"},
                "ceremony_function": {"description": "Every ceremony: attempting to make EML-inf events survivable via EML-0 structure", "depth": "EML-0", "reason": "Ceremony theorem: ritual is EML-0 container for EML-inf events; makes categorification socially survivable"},
            },
        }
    def analyze(self) -> dict[str, Any]:
        depths = [v['depth'] for v in self.depth_analysis()['domains'].values()]
        dist: dict[str, int] = {}
        for d in depths: dist[d] = dist.get(d, 0) + 1
        return {
            "model": "CryingAtWeddingsEML",
            "analysis": self.depth_analysis(),
            "distribution": dist,
            "theorem": "T647: Why We Cry at Weddings (S926).",
        }

def analyze_crying_at_weddings_eml() -> dict[str, Any]:
    t = CryingAtWeddingsEML()
    return {
        "session": 926,
        "title": "Why We Cry at Weddings",
        "eml_operator": "eml(x,y) = exp(x) - ln(y)",
        "analysis": t.analyze(),
        "key_theorem": "T647: Why We Cry at Weddings (S926).",
        "rabbit_hole_log": ["T647: ceremony_eml0 depth confirmed"],
    }

if __name__ == "__main__":
    import json
    print(json.dumps(analyze_crying_at_weddings_eml(), indent=2, default=str))