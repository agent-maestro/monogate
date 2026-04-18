"""
Session 92 — Music Deep: Timbre, Psychoacoustics & Generative Composition

EML depth of timbre (spectral envelope), consonance/dissonance, roughness,
brightness, and rhythmic hierarchies. Perceptual qualities as EML-classified functionals.

Key theorem: Timbre = EML-3 (spectral envelope = sum of exp(2πi·n·f·t)); roughness
(Helmholtz beating) = EML-3 (beat frequency = difference of EML-3 tones); harmonic
entropy = EML-2 (information-theoretic). Perceptual brightness = EML-2 (spectral centroid).
"""

from __future__ import annotations
import math, json
from dataclasses import dataclass, field


EML_INF = float("inf")
PI = math.pi


@dataclass
class TimbreModel:
    """
    Timbre = the quality that distinguishes instruments playing the same pitch.
    Acoustically: the spectral envelope — how energy is distributed across harmonics.

    EML structure:
    - Pure tone A·sin(2πft): EML-3 (imaginary exponential)
    - N-th harmonic A_n·sin(2πnft): EML-3
    - Timbre = Σ_n A_n·sin(2πnft): EML-3 (superposition of EML-3 atoms)
    - Spectral centroid SC = Σ A_n·nf / Σ A_n: EML-2 (weighted mean of EML-3 frequencies)
    - ADSR envelope E(t) = A·exp(-t/τ_decay)·(1-exp(-t/τ_attack)): EML-1 × EML-1 = EML-1
    """

    INSTRUMENTS = {
        "pure_tone": [1.0],
        "piano": [1.0, 0.7, 0.5, 0.35, 0.25, 0.18, 0.12, 0.08, 0.05, 0.03],
        "clarinet": [1.0, 0.0, 0.5, 0.0, 0.25, 0.0, 0.12, 0.0, 0.06, 0.0],  # odd harmonics
        "violin": [1.0, 0.9, 0.7, 0.5, 0.35, 0.25, 0.18, 0.12, 0.08, 0.05],
        "trumpet": [1.0, 0.8, 0.9, 0.6, 0.4, 0.7, 0.3, 0.5, 0.2, 0.3],
    }

    def spectral_centroid(self, name: str) -> dict:
        harmonics = self.INSTRUMENTS.get(name, [1.0])
        n_vals = list(range(1, len(harmonics) + 1))
        weighted = sum(A * n for A, n in zip(harmonics, n_vals))
        total = sum(harmonics)
        centroid = weighted / total if total > 0 else 1.0
        return {
            "instrument": name,
            "harmonics": [round(A, 3) for A in harmonics],
            "spectral_centroid": round(centroid, 4),
            "brightness": "bright" if centroid > 3 else "mid" if centroid > 1.5 else "dark",
            "eml_timbre": 3,
            "eml_centroid": 2,
            "reason": "Centroid = weighted mean of harmonic indices = EML-2 (rational function of EML-3 amplitudes)",
        }

    def adsr_envelope(self, t: float, A: float = 1.0, D: float = 0.3,
                      S: float = 0.7, R: float = 0.5,
                      t_attack: float = 0.05, t_decay: float = 0.1, t_release_start: float = 0.8) -> dict:
        if t < t_attack:
            env = A * t / t_attack
        elif t < t_attack + t_decay:
            env = A - (A - S) * (t - t_attack) / t_decay
        elif t < t_release_start:
            env = S
        else:
            env = S * math.exp(-(t - t_release_start) / R)
        return {
            "t": round(t, 3),
            "envelope": round(env, 6),
            "eml": 1,
            "reason": "ADSR decay = exp(-t/R): EML-1",
        }

    def to_dict(self) -> dict:
        instruments = list(self.INSTRUMENTS.keys())
        t_vals = [0.01, 0.1, 0.5, 0.85, 1.0]
        return {
            "spectral_centroids": [self.spectral_centroid(inst) for inst in instruments],
            "adsr_envelope": [self.adsr_envelope(t) for t in t_vals],
            "eml_timbre": 3,
            "eml_centroid": 2,
            "eml_envelope": 1,
        }


@dataclass
class RoughnessConsonance:
    """
    Helmholtz roughness: two tones at f₁ and f₂ produce beating at |f₁-f₂|.
    Perceived roughness peaks at ~33 Hz difference (within critical band).

    EML structure:
    - Beat: cos(2πf₁t) + cos(2πf₂t) = 2·cos(π(f₁-f₂)t)·cos(π(f₁+f₂)t): EML-3
    - Beat frequency Δf = |f₁-f₂|: EML-2 (arithmetic difference)
    - Roughness R(Δf): EML-3 (psychoacoustic function, empirically ≈ exp(-a·Δf))
    - Consonance C = 1 - R: EML-3

    Harmonic entropy (Tenney): H = -Σ p_i·log₂(p_i) over JI ratios → EML-2 (Shannon entropy)
    """

    @staticmethod
    def beat_frequency(f1: float, f2: float) -> dict:
        delta_f = abs(f1 - f2)
        f_mean = (f1 + f2) / 2
        roughness_peak = 33.0  # Hz, ~1 critical band
        roughness = math.exp(-((delta_f - roughness_peak)**2) / (2 * roughness_peak**2))
        return {
            "f1": f1,
            "f2": f2,
            "beat_freq_Hz": round(delta_f, 2),
            "roughness": round(roughness, 4),
            "consonance": round(1 - roughness, 4),
            "eml_beat": 3,
            "eml_roughness": 3,
        }

    @staticmethod
    def just_intonation_ratios() -> list[dict]:
        intervals = [
            ("unison", 1, 1), ("minor_2nd", 16, 15), ("major_2nd", 9, 8),
            ("minor_3rd", 6, 5), ("major_3rd", 5, 4), ("perfect_4th", 4, 3),
            ("tritone", 7, 5), ("perfect_5th", 3, 2), ("minor_6th", 8, 5),
            ("major_6th", 5, 3), ("minor_7th", 16, 9), ("major_7th", 15, 8),
            ("octave", 2, 1),
        ]
        results = []
        for name, p, q in intervals:
            ratio = p / q
            complexity = p + q  # Tenney height-like
            entropy_approx = math.log2(complexity) if complexity > 1 else 0
            results.append({
                "interval": name,
                "ratio": f"{p}/{q}",
                "decimal": round(ratio, 6),
                "complexity_p_q": complexity,
                "harmonic_entropy_bits": round(entropy_approx, 4),
                "eml": 2,
                "reason": "log₂(p+q): EML-2 (logarithm of integer = EML-2)",
            })
        return results

    def to_dict(self) -> dict:
        f_base = 440.0  # A4
        test_pairs = [(f_base, f_base * 3/2), (f_base, f_base * 5/4),
                      (f_base, f_base + 1), (f_base, f_base + 33)]
        return {
            "beating_analysis": [self.beat_frequency(f1, f2) for f1, f2 in test_pairs],
            "just_intonation": self.just_intonation_ratios(),
            "eml_consonance": 3,
            "eml_harmonic_entropy": 2,
        }


@dataclass
class RhythmicHierarchy:
    """
    Rhythmic hierarchy: metric levels from beat to measure to phrase.
    Each level is a ratio of the level below: EML-0 (integer ratio).
    Polyrhythm: simultaneous n:m meters = EML-3 (quasi-periodic).

    EML structure:
    - Single pulse at period T: EML-3 (periodic = EML-3 oscillation)
    - n:m polyrhythm: quasi-periodic with period lcm(n,m)·T = EML-3
    - Metric hierarchy: 2×2×3×2 = 12/8 time = EML-0 (integer structure)
    - Syncopation: deviation from metric grid = EML-3 (phase shift in EML-3 oscillation)
    """

    def polyrhythm_analysis(self, n: int, m: int, T: float = 1.0) -> dict:
        lcm = n * m // math.gcd(n, m)
        return {
            "ratio": f"{n}:{m}",
            "period_lcm": lcm * T,
            "beat_n_interval": round(T, 4),
            "beat_m_interval": round(T * n / m, 4),
            "eml_each_pulse": 3,
            "eml_polyrhythm": 3,
            "reason": "Two EML-3 periodic signals with incommensurate periods → quasi-periodic = EML-3",
        }

    def generative_composition_rules(self) -> list[dict]:
        return [
            {
                "rule": "Harmonic rhythm",
                "formula": "f_n = f_0 · 2^{n/12} (equal temperament)",
                "eml": 3,
                "reason": "2^{n/12} = exp(n·ln2/12): EML-3 (exp of EML-2)",
            },
            {
                "rule": "Phase modulation (vibrato)",
                "formula": "x(t) = A·sin(2πf·t + β·sin(2πf_v·t))",
                "eml": 3,
                "reason": "sin of sin = EML-3 composition",
            },
            {
                "rule": "Amplitude modulation (tremolo)",
                "formula": "x(t) = (1 + m·sin(2πf_t·t))·A·sin(2πf·t)",
                "eml": 3,
                "reason": "Product of EML-3 = EML-3",
            },
            {
                "rule": "Spectral centroid trajectory",
                "formula": "SC(t) = SC_0 + A·exp(-t/τ)",
                "eml": 1,
                "reason": "Exponential decay of brightness = EML-1",
            },
        ]

    def to_dict(self) -> dict:
        return {
            "polyrhythms": [
                self.polyrhythm_analysis(3, 2),
                self.polyrhythm_analysis(4, 3),
                self.polyrhythm_analysis(5, 4),
            ],
            "generative_rules": self.generative_composition_rules(),
            "eml_rhythm": 3,
            "eml_metric_hierarchy": 0,
        }


def analyze_music_deep_eml() -> dict:
    timbre = TimbreModel()
    roughness = RoughnessConsonance()
    rhythm = RhythmicHierarchy()
    return {
        "session": 92,
        "title": "Music Deep: Timbre, Psychoacoustics & Generative Composition",
        "key_theorem": {
            "theorem": "EML-3 Universality of Musical Structure",
            "statement": (
                "All musical sound phenomena are EML-3: "
                "pure tones A·sin(2πft), timbre (spectral superposition), beating and roughness, "
                "polyrhythms, vibrato, and generative composition rules. "
                "Perceptual quantities derived from spectra are EML-2: "
                "spectral centroid, harmonic entropy, loudness (energy = EML-2 functional). "
                "Metric hierarchy (integer time signatures) is EML-0. "
                "EML depth of music matches EML depth of physics: waves = EML-3, energy = EML-2, counting = EML-0."
            ),
        },
        "timbre": timbre.to_dict(),
        "roughness_consonance": roughness.to_dict(),
        "rhythmic_hierarchy": rhythm.to_dict(),
        "eml_depth_summary": {
            "EML-0": "Integer time signatures 4/4, 3/4; note values (whole/half/quarter); just intonation integer ratios",
            "EML-1": "ADSR decay envelope exp(-t/τ); spectral centroid decay; loudness falloff",
            "EML-2": "Spectral centroid (weighted mean); harmonic entropy log₂(p+q); equal temperament 2^{n/12}",
            "EML-3": "Tones sin(2πft); timbre (spectral sum); beating; polyrhythms; vibrato; composition rules",
        },
        "rabbit_hole_log": [
            "Music is EML-3 physics: the ear is a Fourier analyzer (inner hair cells = EML-3 frequency decomposition). Consonance = constructive interference of EML-3 waves. Dissonance = beating between EML-3 components.",
            "Equal temperament 2^{1/12} ≈ 1.05946: this is exp(ln2/12) = EML-3 (exp of EML-2). Just intonation uses p/q rationals = EML-0. The tension between EML-3 (ET) and EML-0 (JI) is the fundamental tuning problem.",
            "Generative composition: if we parameterize music by its EML tree, then EML-3 rules (PM, AM, FM) generate all classical synthesis. Higher EML depth = more complex timbres. Algorithmic composition = navigation of EML-3 space.",
        ],
        "connections": {
            "to_session_37": "Session 37 (EML Fourier): Fourier basis = EML-3. Session 92: music IS Fourier analysis in physical form",
            "to_session_60": "Harmonic entropy = Shannon entropy of JI approximations = EML-2. Same class as Fisher information",
        },
    }


if __name__ == "__main__":
    print(json.dumps(analyze_music_deep_eml(), indent=2, default=str))
