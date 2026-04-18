"""
Session 173 — Music & Perception Deep: Timbre, Emotion, EML-∞

EML operator: eml(x,y) = exp(x) - ln(y)
Key theorem: Timbre is EML-3 (spectral envelope × oscillatory partials);
emotional valence from music is EML-∞ (cross-domain qualia projection);
tension-resolution curves are EML-∞ at cadences; harmonic expectation = EML-2.
"""
from __future__ import annotations
import math
from dataclasses import dataclass
from typing import Any


@dataclass
class TimbreEML:
    """Timbre: spectral envelope, ADSR, and perceptual dimensions."""

    def spectral_envelope(self, freq: float, f0: float = 220.0,
                           formant_freqs: list[float] = None) -> dict[str, Any]:
        """
        Spectral envelope: A(f) = Σ_k G_k * exp(-((f - F_k)/σ_k)²). EML-3.
        Formant peaks: Gaussian shape. EML-3 (Gaussian = exp of quadratic).
        Harmonic series f_n = n*f0. EML-0 (integer multiples).
        """
        if formant_freqs is None:
            formant_freqs = [500.0, 1500.0, 2500.0]
        sigma = 200.0
        envelope = sum(
            math.exp(-((freq - F) / sigma) ** 2)
            for F in formant_freqs
        )
        harmonic_number = round(freq / f0) if f0 > 0 else 0
        return {
            "freq_Hz": freq,
            "f0_Hz": f0,
            "formant_freqs": formant_freqs,
            "envelope_amplitude": round(envelope, 6),
            "harmonic_number": harmonic_number,
            "eml_depth_envelope": 3,
            "eml_depth_harmonic_n": 0,
            "note": "Spectral envelope = EML-3 (Gaussian peaks); harmonic series = EML-0"
        }

    def adsr_envelope(self, t: float, A: float = 0.1, D: float = 0.2,
                      S_level: float = 0.7, R: float = 0.3,
                      note_off: float = 1.0) -> dict[str, Any]:
        """
        ADSR: Attack (linear ramp EML-0), Decay (exp(-t/τ_D) EML-1),
        Sustain (constant EML-0), Release (exp(-t/τ_R) EML-1).
        Overall envelope = EML-1 (dominated by exponential segments).
        """
        if t < A:
            amp = t / A
            phase = "attack"
            eml = 0
        elif t < A + D:
            dt = t - A
            amp = 1.0 - (1.0 - S_level) * (1 - math.exp(-dt / (D / 3)))
            phase = "decay"
            eml = 1
        elif t < note_off:
            amp = S_level
            phase = "sustain"
            eml = 0
        else:
            dt = t - note_off
            amp = S_level * math.exp(-dt / (R / 3))
            phase = "release"
            eml = 1
        return {
            "t": t, "amplitude": round(amp, 6),
            "phase": phase, "eml_depth": eml,
            "note": "ADSR: attack/sustain=EML-0; decay/release=EML-1"
        }

    def brightness_roughness(self, partials: list[tuple]) -> dict[str, Any]:
        """
        Brightness: spectral centroid = Σ(f_n * A_n)/Σ(A_n). EML-2 (weighted log-freq).
        Roughness: Σ_{n<m} A_n*A_m*R(|f_n-f_m|). EML-3 (beating = EML-3).
        Plomp-Levelt: R(Δf) = exp(-3.5*Δf/f_crit)*(1-exp(-3.5*Δf/f_crit))^0.3. EML-1.
        """
        if not partials:
            return {"error": "no_partials"}
        total_amp = sum(a for _, a in partials)
        centroid = sum(f * a for f, a in partials) / (total_amp + 1e-12)
        log_centroid = math.log(centroid + 1.0)
        roughness = 0.0
        for i, (fi, ai) in enumerate(partials):
            for j, (fj, aj) in enumerate(partials):
                if i < j:
                    df = abs(fi - fj)
                    f_crit = 0.24 * min(fi, fj) + 75
                    x = df / f_crit if f_crit > 0 else 0
                    r = math.exp(-3.5 * x) * (1 - math.exp(-3.5 * x + 1e-12)) ** 2
                    roughness += ai * aj * r
        return {
            "spectral_centroid_Hz": round(centroid, 2),
            "log_centroid": round(log_centroid, 4),
            "roughness": round(roughness, 6),
            "n_partials": len(partials),
            "eml_depth_centroid": 2,
            "eml_depth_roughness": 3,
            "eml_depth_plomp_levelt": 1
        }

    def analyze(self) -> dict[str, Any]:
        freq_vals = [220, 440, 660, 880, 1100, 1320]
        envelope = {f: self.spectral_envelope(float(f)) for f in freq_vals}
        t_vals = [0.05, 0.15, 0.5, 1.0, 1.2, 1.5]
        adsr = {t: self.adsr_envelope(t) for t in t_vals}
        piano_partials = [(220 * n, 1.0 / n) for n in range(1, 6)]
        violin_partials = [(220 * n, 0.8 ** (n - 1)) for n in range(1, 8)]
        br = {
            "piano": self.brightness_roughness(piano_partials),
            "violin": self.brightness_roughness(violin_partials)
        }
        return {
            "model": "TimbreEML",
            "spectral_envelope": envelope,
            "adsr_envelope": adsr,
            "brightness_roughness": br,
            "eml_depth": {
                "spectral_envelope": 3, "harmonic_series": 0,
                "adsr_attack_sustain": 0, "adsr_decay_release": 1,
                "spectral_centroid": 2, "roughness": 3
            },
            "key_insight": "Timbre = EML-3 (Gaussian spectral envelope); ADSR decay = EML-1"
        }


@dataclass
class MusicalEmotionEML:
    """Musical emotion: valence, arousal, and EML-∞ qualia projection."""

    def valence_arousal_model(self, mode: str = "major",
                               tempo_bpm: float = 120.0,
                               loudness_db: float = -10.0) -> dict[str, Any]:
        """
        Valence: major=+1, minor=-1. EML-0 (binary categorical).
        Arousal: log(tempo/60) × loudness factor. EML-2.
        Russell circumplex: valence × arousal → emotion word. EML-0 map.
        Qualia projection: mapping circumplex → felt emotion = EML-∞.
        """
        valence = 1 if mode == "major" else -1
        arousal = math.log(tempo_bpm / 60.0) * (1 + loudness_db / 100)
        if valence > 0 and arousal > 0:
            emotion = "happy_excited"
        elif valence > 0 and arousal <= 0:
            emotion = "serene_content"
        elif valence <= 0 and arousal > 0:
            emotion = "angry_fearful"
        else:
            emotion = "sad_depressed"
        return {
            "mode": mode, "tempo_bpm": tempo_bpm, "loudness_db": loudness_db,
            "valence": valence,
            "arousal": round(arousal, 4),
            "circumplex_emotion": emotion,
            "eml_depth_valence": 0,
            "eml_depth_arousal": 2,
            "eml_depth_felt_emotion": "∞",
            "note": "Valence=EML-0; arousal=EML-2; felt qualia=EML-∞ (unbridgeable gap)"
        }

    def tension_resolution(self, chord_root: int, key_root: int = 0) -> dict[str, Any]:
        """
        Tonal tension: Lerdahl tension = T(c) based on voice-leading distance.
        Distance from tonic: 0=home, max at tritone. EML-2 (log distance).
        Cadence resolution V→I: EML-∞ (qualia of 'arriving home').
        Expectation satisfaction: I(resolution | context). EML-2.
        """
        chromatic_dist = min((chord_root - key_root) % 12,
                              (key_root - chord_root) % 12)
        tension = chromatic_dist / 6.0
        tritone = (chord_root - key_root) % 12 == 6
        return {
            "chord_root": chord_root,
            "key_root": key_root,
            "chromatic_distance": chromatic_dist,
            "tension_score": round(tension, 4),
            "is_tritone": tritone,
            "cadence_resolution_eml": "∞" if tritone else 2,
            "eml_depth_tension": 2,
            "note": "Tension = EML-2; tritone resolution = EML-∞ (phenomenal 'pull')"
        }

    def expectation_information(self, note: int, context: list[int]) -> dict[str, Any]:
        """
        Melodic expectation: I(x) = -log₂ P(x | context). EML-2.
        Surprise information content: high I = high surprise = high arousal change. EML-2.
        Musical climax: cascade of surprises → EML-∞ (emotional peak).
        """
        if not context:
            prob = 1.0 / 12
        else:
            last = context[-1]
            step_dist = min((note - last) % 12, (last - note) % 12)
            prob = math.exp(-0.3 * step_dist) / sum(math.exp(-0.3 * d) for d in range(7))
        info = -math.log2(prob + 1e-12)
        return {
            "note": note,
            "context_len": len(context),
            "probability": round(prob, 6),
            "information_bits": round(info, 4),
            "eml_depth": 2,
            "note_field": "Melodic expectation I = -log₂P = EML-2"
        }

    def analyze(self) -> dict[str, Any]:
        conditions = [
            ("major", 120.0, -10.0),
            ("minor", 60.0, -20.0),
            ("major", 180.0, -5.0),
            ("minor", 80.0, -15.0)
        ]
        emotions = {f"{m}_{t}bpm": self.valence_arousal_model(m, t, l)
                    for m, t, l in conditions}
        tensions = {f"chord_{r}": self.tension_resolution(r) for r in range(12)}
        context = [0, 2, 4, 5, 7]
        expect = {f"note_{n}": self.expectation_information(n, context) for n in range(12)}
        return {
            "model": "MusicalEmotionEML",
            "emotion_circumplex": emotions,
            "tension_scores": tensions,
            "melodic_expectation": expect,
            "eml_depth": {
                "valence": 0, "arousal": 2, "felt_qualia": "∞",
                "tension_curve": 2, "tritone_pull": "∞", "surprise": 2
            },
            "key_insight": "Musical emotion: structure=EML-0/2; felt quality=EML-∞ (unbridgeable)"
        }


@dataclass
class PerceptualGroupingEML:
    """Gestalt grouping, auditory scene analysis, and EML depth."""

    def auditory_streaming(self, freq1: float, freq2: float,
                            delta_t: float = 0.1) -> dict[str, Any]:
        """
        Bregman streaming: two streams segregate when Δf large + Δt small.
        Δf critical ≈ 3 semitones. EML-2 (log freq ratio).
        Coherence measure: C = exp(-k * Δf_semitones). EML-1.
        Stream bifurcation: EML-∞ (perceptual bistability).
        """
        if freq2 <= 0 or freq1 <= 0:
            return {"error": "invalid_freq"}
        delta_f_semitones = 12 * abs(math.log2(freq2 / freq1))
        coherence = math.exp(-0.3 * delta_f_semitones)
        is_segregated = delta_f_semitones > 3.0 and delta_t < 0.15
        return {
            "freq1": freq1, "freq2": freq2, "delta_t": delta_t,
            "delta_f_semitones": round(delta_f_semitones, 4),
            "coherence": round(coherence, 6),
            "segregated": is_segregated,
            "eml_depth_delta_f": 2,
            "eml_depth_coherence": 1,
            "eml_depth_bifurcation": "∞",
            "note": "Δf = EML-2 (log); coherence = EML-1 (exp); stream split = EML-∞"
        }

    def rhythm_meter(self, ioi_pattern: list[float]) -> dict[str, Any]:
        """
        IOI (inter-onset interval) pattern → perceived meter.
        Metric strength = log(longest_IOI / shortest_IOI). EML-2.
        Syncopation = deviation from isochrony. EML-0 count.
        Meter induction: EML-∞ (perceptual commitment to meter grid).
        """
        if len(ioi_pattern) < 2:
            return {"error": "need_at_least_2_ioi"}
        min_ioi = min(ioi_pattern)
        max_ioi = max(ioi_pattern)
        metric_strength = math.log(max_ioi / (min_ioi + 1e-12) + 1.0)
        mean_ioi = sum(ioi_pattern) / len(ioi_pattern)
        syncopations = sum(1 for ioi in ioi_pattern if abs(ioi - mean_ioi) > mean_ioi * 0.3)
        return {
            "ioi_pattern": ioi_pattern,
            "mean_ioi": round(mean_ioi, 4),
            "metric_strength": round(metric_strength, 4),
            "syncopations": syncopations,
            "eml_depth_metric_strength": 2,
            "eml_depth_syncopation_count": 0,
            "eml_depth_meter_induction": "∞"
        }

    def analyze(self) -> dict[str, Any]:
        stream_pairs = [(440, 494), (440, 587), (440, 880), (440, 1760)]
        streaming = {f"{f1}_{f2}": self.auditory_streaming(float(f1), float(f2))
                     for f1, f2 in stream_pairs}
        ioi_patterns = {
            "isochronous": [0.5, 0.5, 0.5, 0.5],
            "waltz": [0.5, 0.25, 0.25, 0.5, 0.25, 0.25],
            "syncopated": [0.25, 0.75, 0.25, 0.75]
        }
        rhythm = {name: self.rhythm_meter(pattern)
                  for name, pattern in ioi_patterns.items()}
        return {
            "model": "PerceptualGroupingEML",
            "auditory_streaming": streaming,
            "rhythm_meter": rhythm,
            "eml_depth": {
                "freq_ratio": 2, "stream_coherence": 1, "stream_bifurcation": "∞",
                "metric_strength": 2, "syncopation_count": 0, "meter_induction": "∞"
            },
            "key_insight": "Perceptual grouping: measures=EML-0/1/2; bistable percept=EML-∞"
        }


def analyze_music_perception_eml() -> dict[str, Any]:
    timbre = TimbreEML()
    emotion = MusicalEmotionEML()
    grouping = PerceptualGroupingEML()
    return {
        "session": 173,
        "title": "Music & Perception Deep: Timbre, Emotion, EML-∞",
        "eml_operator": "eml(x,y) = exp(x) - ln(y)",
        "timbre": timbre.analyze(),
        "musical_emotion": emotion.analyze(),
        "perceptual_grouping": grouping.analyze(),
        "eml_depth_summary": {
            "EML-0": "Harmonic series n*f0, valence major/minor, syncopation count, locking ratio",
            "EML-1": "ADSR decay/release exp(-t/τ), Plomp-Levelt roughness, stream coherence",
            "EML-2": "Spectral centroid, arousal log(tempo), tension chromatic distance, Δf semitones",
            "EML-3": "Spectral envelope Gaussian, roughness beating, oscillatory waveforms",
            "EML-∞": "Felt emotion qualia, tritone resolution pull, stream bifurcation, meter induction"
        },
        "key_theorem": (
            "The EML Music Depth Theorem: "
            "Musical structure spans all EML depths: "
            "harmonic integers = EML-0, ADSR decay = EML-1, tension curves = EML-2, "
            "timbre spectral envelope = EML-3. "
            "The gap between structure and felt qualia is EML-∞: "
            "valence (major/minor = EML-0) induces felt happiness/sadness (EML-∞). "
            "This is the musical instance of the Hard Problem: "
            "EML-finite structural descriptions cannot bridge to EML-∞ felt musical experience. "
            "Perceptual bistability (streaming, meter induction) = EML-∞: "
            "the same stimulus admits two perceptual interpretations separated by a EML-∞ transition."
        ),
        "rabbit_hole_log": [
            "Spectral envelope = EML-3: Gaussian formant peaks — same as wave packet (QM!)",
            "ADSR decay = EML-1: exp(-t/τ) — same as Boltzmann, ISI, instanton, BCS",
            "Arousal = log(tempo/60) = EML-2: log ratio — same as running coupling α_s",
            "Tritone resolution = EML-∞: the 'pull' to resolution is qualia, not structure",
            "Stream bifurcation = EML-∞: perceptual bistability (same as chimera state!)",
            "Meter induction = EML-∞: commitment to a meter grid = spontaneous symmetry breaking"
        ],
        "connections": {
            "S153_music": "Spectral ratios (S153) = EML-0; timbre envelope (S173) = EML-3 — deeper",
            "S174_consciousness": "Musical qualia = felt emotion = EML-∞: same stratum as qualia (next!)",
            "S172_chaos_sync": "Stream bifurcation = EML-∞: same as Kuramoto sync transition"
        }
    }


if __name__ == "__main__":
    import json
    print(json.dumps(analyze_music_perception_eml(), indent=2, default=str))
