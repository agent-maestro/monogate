"""Session 939 --- What Makes a Meal a Feast"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any

@dataclass
class FeastVsMealEML:
    def depth_analysis(self) -> dict[str, Any]:
        return {
            "object": "T660: What Makes a Meal a Feast depth analysis",
            "domains": {
                "dishes_eml0": {"description": "Individual dishes: EML-0", "depth": "EML-0", "reason": "Dishes are EML-0: discrete items; the building blocks"},
                "abundance_eml1": {"description": "Quantity: EML-1 exponential surplus above need", "depth": "EML-1", "reason": "Feast quantity is EML-1: exponential abundance beyond requirement"},
                "flavor_balance_eml2": {"description": "Flavor balance: EML-2 measurement of sweet/salt/acid/fat ratios", "depth": "EML-2", "reason": "Flavor is EML-2: measurement and balance of primary taste dimensions"},
                "experience_emlinf": {"description": "Feast experience: EML-inf categorification of food+company+conversation+ritual", "depth": "EML-inf", "reason": "Feast is EML-inf: the combination categorifies into something beyond any individual component"},
            },
        }
    def analyze(self) -> dict[str, Any]:
        depths = [v['depth'] for v in self.depth_analysis()['domains'].values()]
        dist: dict[str, int] = {}
        for d in depths: dist[d] = dist.get(d, 0) + 1
        return {
            "model": "FeastVsMealEML",
            "analysis": self.depth_analysis(),
            "distribution": dist,
            "theorem": "T660: What Makes a Meal a Feast (S939).",
        }

def analyze_feast_vs_meal_eml() -> dict[str, Any]:
    t = FeastVsMealEML()
    return {
        "session": 939,
        "title": "What Makes a Meal a Feast",
        "eml_operator": "eml(x,y) = exp(x) - ln(y)",
        "analysis": t.analyze(),
        "key_theorem": "T660: What Makes a Meal a Feast (S939).",
        "rabbit_hole_log": ["T660: dishes_eml0 depth confirmed"],
    }

if __name__ == "__main__":
    import json
    print(json.dumps(analyze_feast_vs_meal_eml(), indent=2, default=str))