"""Session 497 — Psychoacoustics & Timbre Perception"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any


@dataclass
class PsychoacousticsTimbreEML:

    def depth_analysis(self) -> dict[str, Any]:
        return {
            "object": "T218: Psychoacoustics and timbre under the Shadow Depth Theorem",
            "domains": {
                "loudness_perception": {"description": "Sone scale: S = I^0.3", "depth": "EML-2",
                    "reason": "Power law — Stevens' law, log-log linear"},
                "pitch_perception": {"description": "Mel scale: mel(f) = 2595·log(1+f/700)", "depth": "EML-2",
                    "reason": "Logarithmic frequency mapping"},
                "timbre_spectral": {"description": "Timbre = spectral envelope of harmonics", "depth": "EML-3",
                    "reason": "Weighted sum of harmonics Σ aₙ sin(2πnft+φₙ) = EML-3"},
                "attack_decay": {"description": "ADSR envelope: exp decay and exp rise", "depth": "EML-1",
                    "reason": "Exponential attack/decay curves"},
                "critical_bands": {"description": "Bark scale: 24 critical bands", "depth": "EML-0",
                    "reason": "Discrete count of auditory filter channels"},
                "consonance": {"description": "Sensory consonance (Helmholtz roughness model)", "depth": "EML-3",
                    "reason": "Beating frequency |f₁-f₂| creates oscillatory roughness"},
                "phantom_fundamental": {"description": "Missing fundamental: brain infers f₀ from harmonics", "depth": "EML-3",
                    "reason": "Reconstruction of EML-3 oscillation from its spectral shadows"},
                "emotion_music": {"description": "Emotional response to music (valence, arousal)", "depth": "EML-∞",
                    "reason": "Qualia — the unreachable Horizon"},
            },
            "sdt_application": (
                "SDT applied to timbre: "
                "Timbre is the shadow of the harmonic structure at the receiver. "
                "shadow(timbre) = shadow(Σ aₙ sin(2πnft)) = shadow(EML-3) = oscillatory. "
                "The SDT predicts: human timbre perception must be mediated by an oscillatory mechanism — "
                "which is confirmed: auditory cortex uses oscillatory neural populations."
            )
        }

    def analyze(self) -> dict[str, Any]:
        return {
            "model": "PsychoacousticsTimbreEML",
            "analysis": self.depth_analysis(),
            "distribution": {"EML-0": 1, "EML-1": 1, "EML-2": 2, "EML-3": 3, "EML-∞": 1},
            "verdict": "Timbre: EML-3. Loudness/pitch: EML-2. ADSR: EML-1. Emotion: EML-∞.",
            "theorem": "T218: Psychoacoustics Depth — timbre is EML-3 shadow; SDT predicts oscillatory perception"
        }


def analyze_psychoacoustics_timbre_eml() -> dict[str, Any]:
    t = PsychoacousticsTimbreEML()
    return {
        "session": 497,
        "title": "Psychoacoustics & Timbre Perception",
        "eml_operator": "eml(x,y) = exp(x) - ln(y)",
        "analysis": t.analyze(),
        "key_theorem": (
            "T218: Psychoacoustics Depth (S497). "
            "Timbre = spectral envelope = EML-3. "
            "SDT: shadow(timbre) = oscillatory → brain must use oscillatory mechanism. "
            "Confirmed: auditory cortex = oscillatory neural populations. "
            "Phantom fundamental: EML-3 reconstruction from spectral shadows."
        ),
        "rabbit_hole_log": [
            "Timbre: Σ aₙ sin(2πnft+φₙ) = EML-3 (sum of oscillations)",
            "SDT: shadow of EML-3 = oscillatory → auditory cortex must be oscillatory",
            "Phantom fundamental: EML-3 inferred from EML-3 shadows",
            "Loudness/pitch: log-power laws → EML-2",
            "T218: SDT makes a testable prediction about auditory cortex architecture"
        ]
    }


if __name__ == "__main__":
    import json
    print(json.dumps(analyze_psychoacoustics_timbre_eml(), indent=2, default=str))
