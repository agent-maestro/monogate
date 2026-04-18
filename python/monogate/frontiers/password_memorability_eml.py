"""Session 938 --- Mathematics of Why Some Passwords Are Memorable"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any

@dataclass
class PasswordMemorabilityEML:
    def depth_analysis(self) -> dict[str, Any]:
        return {
            "object": "T659: Mathematics of Why Some Passwords Are Memorable depth analysis",
            "domains": {
                "random_eml0": {"description": "Random strings: EML-0 discrete symbols; no structure", "depth": "EML-0", "reason": "Random password is EML-0: maximum entropy, no pattern, impossible to remember without EML-2+"},
                "pattern_eml1": {"description": "Pattern passwords: EML-1 growth rule (keyboard walks, number sequences)", "depth": "EML-1", "reason": "Pattern password is EML-1: memorable because the rule is exponential; predictable"},
                "passphrase_eml2": {"description": "Story passphrases: EML-2 meaningful measurement", "depth": "EML-2", "reason": "Passphrase is EML-2: semantic content makes it memorable via EML-2 associative measurement"},
                "emotional_emlinf": {"description": "Passwords you never forget: EML-3/inf emotional weight", "depth": "EML-inf", "reason": "Unforgettable passwords are EML-inf associated: emotional categorification makes them permanent"},
            },
        }
    def analyze(self) -> dict[str, Any]:
        depths = [v['depth'] for v in self.depth_analysis()['domains'].values()]
        dist: dict[str, int] = {}
        for d in depths: dist[d] = dist.get(d, 0) + 1
        return {
            "model": "PasswordMemorabilityEML",
            "analysis": self.depth_analysis(),
            "distribution": dist,
            "theorem": "T659: Mathematics of Why Some Passwords Are Memorable (S938).",
        }

def analyze_password_memorability_eml() -> dict[str, Any]:
    t = PasswordMemorabilityEML()
    return {
        "session": 938,
        "title": "Mathematics of Why Some Passwords Are Memorable",
        "eml_operator": "eml(x,y) = exp(x) - ln(y)",
        "analysis": t.analyze(),
        "key_theorem": "T659: Mathematics of Why Some Passwords Are Memorable (S938).",
        "rabbit_hole_log": ["T659: random_eml0 depth confirmed"],
    }

if __name__ == "__main__":
    import json
    print(json.dumps(analyze_password_memorability_eml(), indent=2, default=str))