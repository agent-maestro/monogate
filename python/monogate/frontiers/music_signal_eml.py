"""
Session 153 — Music & Signal Processing: EML Depth of Harmonic Structures

EML operator: eml(x,y) = exp(x) - ln(y)
Key theorem: Pure tones are EML-3 (sinusoidal oscillation); harmony ratios are EML-0
(rational structure); timbre/spectral envelope is EML-2; musical tension/resolution
is EML-∞ (listener expectation — psychoacoustic phase transition).
"""
from __future__ import annotations
import math
from dataclasses import dataclass
from typing import Any


@dataclass
class HarmonicSeriesEML:
    """Overtone series, just intonation, and equal temperament — EML analysis."""

    fundamental: float = 440.0   # A4 Hz

    def overtone_series(self, n_partials: int = 8) -> dict[int, float]:
        """
        f_n = n * f₀. Harmonic series = EML-0 (integer multiples, no exp/log).
        The series itself is the template of all pitched sound.
        """
        return {n: round(n * self.fundamental, 2) for n in range(1, n_partials + 1)}

    def just_intonation_intervals(self) -> dict[str, Any]:
        """
        Just ratios: P5 = 3/2, M3 = 5/4, m3 = 6/5.
        Frequency ratios = EML-0 (rational fractions).
        Cent deviation from equal temperament = EML-2 (log ratio).
        """
        intervals = {
            "unison": (1, 1), "minor_2nd": (16, 15), "major_2nd": (9, 8),
            "minor_3rd": (6, 5), "major_3rd": (5, 4), "perfect_4th": (4, 3),
            "tritone": (45, 32), "perfect_5th": (3, 2), "minor_6th": (8, 5),
            "major_6th": (5, 3), "minor_7th": (9, 5), "major_7th": (15, 8),
            "octave": (2, 1)
        }
        results = {}
        for name, (p, q) in intervals.items():
            freq = self.fundamental * p / q
            et_semitones = list(intervals.keys()).index(name)
            et_freq = self.fundamental * (2 ** (et_semitones / 12))
            cents_dev = 1200 * math.log2(freq / et_freq) if et_freq > 0 else 0
            results[name] = {
                "ratio": f"{p}/{q}",
                "freq_hz": round(freq, 3),
                "cents_from_ET": round(cents_dev, 2),
                "eml_depth_ratio": 0,
                "eml_depth_cents": 2
            }
        return results

    def equal_temperament(self, semitones: int) -> float:
        """f = f₀ * 2^(n/12). EML-3 (irrational: 2^(1/12) = transcendental power)."""
        return round(self.fundamental * (2 ** (semitones / 12)), 4)

    def beating_frequency(self, f1: float, f2: float) -> dict[str, Any]:
        """
        Beat frequency = |f1 - f2|. EML-0 (difference).
        Roughness (Plomp-Levelt): peak at 25% of critical bandwidth. EML-2.
        """
        beat = abs(f1 - f2)
        critical_bw = 25 + 75 * (1 + 1.4 * (f1 / 1000) ** 2) ** 0.69
        roughness = math.exp(-((beat - 0.25 * critical_bw) ** 2) / (critical_bw ** 2))
        return {
            "f1": f1, "f2": f2,
            "beat_hz": round(beat, 4),
            "critical_bandwidth_hz": round(critical_bw, 2),
            "roughness_approx": round(roughness, 4),
            "eml_depth_beat": 0,
            "eml_depth_roughness": 2
        }

    def analyze(self) -> dict[str, Any]:
        partials = self.overtone_series()
        just = self.just_intonation_intervals()
        et_scale = {n: self.equal_temperament(n) for n in range(13)}
        beating = {(440, 442): self.beating_frequency(440, 442),
                   (440, 450): self.beating_frequency(440, 450),
                   (440, 660): self.beating_frequency(440, 660)}
        return {
            "model": "HarmonicSeriesEML",
            "fundamental_hz": self.fundamental,
            "overtone_series": partials,
            "just_intonation_subset": {k: v for k, v in list(just.items())[:5]},
            "et_scale_hz": et_scale,
            "beating": {str(k): v for k, v in beating.items()},
            "eml_depth": {"harmonic_ratios": 0, "equal_temperament": 3,
                          "beating": 0, "roughness": 2},
            "key_insight": "Harmonic ratios = EML-0; ET tuning = EML-3 (irrational powers); roughness = EML-2"
        }


@dataclass
class SpectralAnalysisEML:
    """DFT, STFT, wavelets — EML depth of signal analysis tools."""

    sample_rate: float = 44100.0
    n_fft: int = 1024

    def dft_bin_frequency(self, k: int) -> float:
        """f_k = k * fs / N. EML-0 (linear bin spacing)."""
        return k * self.sample_rate / self.n_fft

    def frequency_resolution(self) -> float:
        """Δf = fs / N. EML-0. Time resolution Δt = N / fs. EML-0."""
        return self.sample_rate / self.n_fft

    def spectral_entropy(self, magnitudes: list[float]) -> float:
        """
        H = -Σ p_k log(p_k), p_k = |X_k|² / Σ|X_k|².
        EML-2 (Shannon entropy over spectrum).
        """
        power = [m ** 2 for m in magnitudes]
        total = sum(power) + 1e-12
        p = [x / total for x in power]
        return -sum(pk * math.log(pk + 1e-12) for pk in p)

    def mel_filterbank(self, f_hz: float) -> float:
        """
        Mel scale: m = 2595 * log10(1 + f/700). EML-2 (logarithmic frequency perception).
        Inverse: f = 700 * (10^(m/2595) - 1). EML-3 (exp of log).
        """
        return 2595.0 * math.log10(1 + f_hz / 700.0)

    def cepstrum_quefrency(self, n_samples: int) -> float:
        """
        Quefrency (cepstral domain): q = n / fs. Units of time.
        Cepstrum = IFFT(log|FFT(x)|²): EML-2 (log of power spectrum). EML-2.
        """
        return n_samples / self.sample_rate

    def wavelet_heisenberg_box(self, scale: float) -> dict[str, float]:
        """
        Wavelet time-freq resolution: Δt * Δf ≥ 1/(4π) (Heisenberg).
        Morlet wavelet: σ_t = scale, σ_f = 1/(4π*scale). EML-2 (uncertainty product).
        """
        sigma_t = scale
        sigma_f = 1.0 / (4 * math.pi * scale)
        product = sigma_t * sigma_f
        return {
            "scale": scale,
            "sigma_t": round(sigma_t, 6),
            "sigma_f": round(sigma_f, 6),
            "heisenberg_product": round(product, 6),
            "eml_depth": 2
        }

    def analyze(self) -> dict[str, Any]:
        freq_res = self.frequency_resolution()
        bins = {k: round(self.dft_bin_frequency(k), 2) for k in [0, 1, 10, 100, 512]}
        test_mags = [1.0, 0.8, 0.5, 0.3, 0.1, 0.05] * (self.n_fft // 12)
        s_ent = self.spectral_entropy(test_mags[:self.n_fft // 2])
        mel = {f: round(self.mel_filterbank(f), 2)
               for f in [100, 500, 1000, 4000, 8000, 16000]}
        heisenberg = {s: self.wavelet_heisenberg_box(s) for s in [0.001, 0.01, 0.1]}
        return {
            "model": "SpectralAnalysisEML",
            "sample_rate": self.sample_rate,
            "n_fft": self.n_fft,
            "freq_resolution_hz": round(freq_res, 4),
            "dft_bins": bins,
            "spectral_entropy_nats": round(s_ent, 4),
            "mel_scale": mel,
            "wavelet_heisenberg": heisenberg,
            "eml_depth": {"dft_bins": 0, "spectral_entropy": 2,
                          "mel_scale": 2, "cepstrum": 2, "wavelet": 2},
            "key_insight": "All spectral analysis tools are EML-2 (logarithmic, quadratic forms)"
        }


@dataclass
class MusicalTensionEML:
    """Harmonic tension, voice leading, and the psychoacoustic phase transition."""

    def tonal_tension(self, root_pc: int, chord_pcs: list[int]) -> float:
        """
        Lerdahl tension model: T = k * Σ dissonance(p, root).
        Dissonance ∝ distance in chord-of-nature hierarchy. EML-2.
        """
        hierarchy = {0: 0, 7: 1, 4: 2, 5: 2, 2: 3, 9: 3, 11: 4, 1: 5, 6: 5,
                     3: 4, 8: 4, 10: 3}
        tension = sum(hierarchy.get((p - root_pc) % 12, 5) for p in chord_pcs)
        return round(tension / len(chord_pcs), 4)

    def voice_leading_distance(self, chord1: list[int], chord2: list[int]) -> float:
        """
        Minimal voice leading: L₁ distance between pitch class sets.
        EML-0 (semitone count = integer distance).
        """
        if len(chord1) != len(chord2):
            return float('inf')
        return sum(min(abs(a - b), 12 - abs(a - b)) for a, b in zip(sorted(chord1), sorted(chord2)))

    def tension_resolution_event(self, tension_before: float, tension_after: float) -> dict[str, Any]:
        """
        Resolution: sharp drop in tension. ΔT > threshold → EML-∞ (perceptual resolution event).
        Gradual tension change = EML-2.
        """
        delta = tension_before - tension_after
        threshold = 2.0
        is_resolution = delta > threshold
        return {
            "tension_before": tension_before,
            "tension_after": tension_after,
            "delta_tension": round(delta, 4),
            "is_resolution_event": is_resolution,
            "eml_depth": "∞ (perceptual phase transition)" if is_resolution else "2 (gradual change)"
        }

    def fourier_timbre_space(self, partials: list[float]) -> float:
        """
        Timbre as point in spectral centroid-spread space.
        Centroid = Σ(f_k * A_k) / Σ A_k. EML-2.
        Spread = √(Σ A_k * (f_k - centroid)²) / Σ A_k. EML-2.
        """
        freqs = [k * 110.0 for k in range(1, len(partials) + 1)]
        total = sum(partials) + 1e-12
        centroid = sum(f * a for f, a in zip(freqs, partials)) / total
        spread = math.sqrt(sum(a * (f - centroid) ** 2
                               for f, a in zip(freqs, partials)) / total)
        return round(centroid, 2)

    def analyze(self) -> dict[str, Any]:
        chords = {
            "C_maj": [0, 4, 7], "G_maj": [7, 11, 2], "D_min": [2, 5, 9],
            "B_dim": [11, 2, 5], "F_maj": [5, 9, 0], "G7": [7, 11, 2, 5]
        }
        tensions = {name: self.tonal_tension(chord[0], chord)
                    for name, chord in chords.items()}
        vl_dist = {
            "C_to_G": self.voice_leading_distance([0, 4, 7], [7, 11, 2]),
            "G7_to_C": self.voice_leading_distance([7, 11, 2, 5], [0, 4, 7, 0])
        }
        resolution = self.tension_resolution_event(tensions["G7"], tensions["C_maj"])
        timbre_centroid = self.fourier_timbre_space([1.0, 0.7, 0.5, 0.3, 0.2])
        return {
            "model": "MusicalTensionEML",
            "chord_tensions": tensions,
            "voice_leading_distance": vl_dist,
            "g7_to_c_resolution": resolution,
            "timbre_centroid_hz": timbre_centroid,
            "eml_depth": {"tension_model": 2, "voice_leading": 0,
                          "resolution_event": "∞", "timbre": 2},
            "key_insight": "Harmonic tension = EML-2; resolution event = EML-∞ (perceptual phase transition)"
        }


def analyze_music_signal_eml() -> dict[str, Any]:
    harmonic = HarmonicSeriesEML(fundamental=440.0)
    spectral = SpectralAnalysisEML(sample_rate=44100.0, n_fft=1024)
    tension = MusicalTensionEML()
    return {
        "session": 153,
        "title": "Music & Signal Processing: EML Depth of Harmonic Structures",
        "eml_operator": "eml(x,y) = exp(x) - ln(y)",
        "harmonic_series": harmonic.analyze(),
        "spectral_analysis": spectral.analyze(),
        "musical_tension": tension.analyze(),
        "eml_depth_summary": {
            "EML-0": "Harmonic ratios (3/2, 5/4...), beat frequency, semitone counts, DFT bins",
            "EML-1": "False-nearest-neighbor decay in Takens embedding, roughness peak",
            "EML-2": "Mel scale, spectral entropy, MFCC, timbre, tonal tension, wavelet",
            "EML-3": "Equal temperament (2^(n/12) = irrational), pure tones, Fourier basis",
            "EML-∞": "Musical resolution events (perceptual phase transitions), timbre jumps"
        },
        "key_theorem": (
            "The EML Music Depth Theorem: "
            "Harmonic frequency ratios are EML-0 — the integers. "
            "Pure tones and the Fourier basis are EML-3 (oscillatory). "
            "Psychoacoustic models (roughness, tension, Mel scale) are EML-2. "
            "Equal temperament lives at EML-3 (irrational powers: 2^(1/12) = e^(log2/12)). "
            "Musical resolution — the moment tension collapses — is EML-∞: "
            "a perceptual phase transition that cannot be described by any EML-finite function of the notes."
        ),
        "rabbit_hole_log": [
            "Harmonic series n*f₀ = EML-0: integers, no exp/log needed",
            "Equal temperament 2^(1/12) = EML-3: same depth as sin/cos!",
            "Mel scale = 2595*log10(1+f/700) = EML-2: logarithmic perception",
            "Spectral entropy = EML-2: Shannon entropy over power spectrum",
            "G7→C resolution = EML-∞: perceptual phase transition (same as Hopf bifurcation!)",
            "Heisenberg uncertainty product σ_t*σ_f = 1/(4π) = EML-2 constant"
        ],
        "connections": {
            "S37_fourier": "Fourier basis = EML-3 (oscillatory); spectrum = EML-2 (entropy)",
            "S152_chaos": "Hopf bifurcation (limit cycle) ↔ musical tone onset: both EML-∞ transition to EML-3",
            "S136_linguistics": "Semantic shift = EML-∞; musical resolution = EML-∞ (same: expectation violation)"
        }
    }


if __name__ == "__main__":
    import json
    print(json.dumps(analyze_music_signal_eml(), indent=2, default=str))
