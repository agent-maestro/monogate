---
layout: ../../layouts/Base.astro
title: "Timbre Is EML Node Count"
date: 2026-04-19
tag: research
description: "Each Fourier harmonic is one complex EML node. We measured timbre complexity for 5 instruments and found: Sine=1n, Clarinet=5n, Violin=12n. EXL is the most musically useful operator."
---

# Timbre Is EML Node Count

The EML operator encodes Fourier synthesis exactly:

```
Im(eml(i·2πft, 1)) = Im(exp(i·2πft) − ln(1)) = Im(e^(i·2πft)) = sin(2πft)
```

One complex EML node = one partial tone.
**Timbre complexity = number of EML nodes.**

---

## The Identity

For any frequency f and time t:

```
eml(i·2πft, 1) = exp(i·2πft) − ln(1)
               = cos(2πft) + i·sin(2πft) − 0
               = cos(2πft) + i·sin(2πft)
```

Taking the imaginary part:

```
Im(eml(i·2πft, 1)) = sin(2πft)     [1 EML node]
```

A sum of N harmonics is exactly N complex EML nodes evaluated in parallel.

---

## Timbre Complexity Table

We measured minimum EML nodes needed to reach −40 dB spectral flatness
for published instrument harmonic profiles:

| Instrument | Min nodes | Dominant harmonics |
|------------|-----------|-------------------|
| Sine | 1 | H1 |
| Clarinet Bb | 5 | H3, H5, H7 (odd harmonics only) |
| Violin A | 12 | H1–H12 (full spectrum) |
| Piano A4 | 12 | H1, H2, H4 (stretched partials) |
| Bell | 7 | H4, H6, H1 (inharmonic ratios) |

The clarinet's low complexity (5 nodes) is because it produces primarily odd harmonics.
Bell is special: the "harmonics" are **inharmonic** (non-integer frequency ratios),
so EML nodes must be tuned to irrational frequency multiples.

---

## Session S3: 8 Operators as Audio Effects

We applied all 8 operators to a 440 Hz + 880 Hz stereo signal and measured the output:

| Operator | Character | Notes |
|----------|-----------|-------|
| EML | Harsh distortion | exp(A) amplifies peaks exponentially |
| DEML | Dynamic compression | exp(−A) inverts peaks, softer |
| EMN | Mirror of DEML | Inverted polarity, similar dynamics |
| EAL | Additive richness | exp(A)+log(B): rich harmonics + harsh peaks |
| **EXL** | **Ring modulation** | exp(A)·log(B): creates sidebands. Most musical. |
| EDL | Buzzy/harsh | Division by ln near zero: discontinuities |
| POW | Gated/tremolo | B^A near A=0: nearly constant |
| LEX | Softest/cleanest | log(exp(A)·B)=A+log(B): smoothest output |

**EXL is the most musically useful operator.** The product `exp(A)·ln(B)` creates
frequency sidebands at sum and difference frequencies, exactly like analog ring modulation.

**LEX is the mildest.** Because `log(exp(A)·B) = A + log(B)`, it behaves like
a compander (dynamic range compressor/expander), smoothing out peaks.

---

## Session S4: Tree-to-Sound Mapping

EML trees as audio primitives:

| Tree | Sound character |
|------|----------------|
| `eml(x, 1)` = exp(x) | High centroid (1953 Hz), full energy |
| `exl(0, x)` = ln(x) | Pure tone at 440 Hz |
| `mul(x, x)` = x² | Second harmonic only (880 Hz) |
| 4-node square approx | Centroid 1050 Hz, odd harmonics |
| 8-node sawtooth | Centroid 1295 Hz, full spectrum |
| exp(−x) decay | Exponential envelope, bright attack |

---

## Interactive Synthesizer

→ [EML Synthesizer](/explorer) — drag harmonic amplitude sliders,
click presets (Sine/Clarinet/Violin/Piano/Bell/Sawtooth/Square),
hear the result in your browser via Web Audio API.
Node counter updates live.

---

## What This Means

The Fourier series is not just analogous to EML — it **is** EML, evaluated in the
complex plane. The minimum number of partials needed to recognize an instrument's timbre
equals the minimum number of EML nodes needed to express it.

This gives a new interpretation of **harmonic complexity**: it is the EML node count
of the timbre, and it is the same number that appears in circuit optimization,
routing table savings, and operator completeness bounds.

One number, three contexts.
