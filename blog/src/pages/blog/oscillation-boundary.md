---
layout: ../../layouts/Base.astro
title: "The Oscillation Boundary"
description: "Across 315 tested equations, a clean dichotomy: oscillatory functions sit outside ELC with one exception — a non-elementary token."
date: "2026-04-23"
author: "Monogate Research"
tag: observation
---

# The Oscillation Boundary

**Tier: OBSERVATION** (empirical, two datasets)

The Infinite Zeros Barrier (T01) says any function with infinitely many zeros on every compact interval has no finite real EML tree. `sin` and `cos` are the canonical examples. Prediction: any equation whose closed form contains genuine oscillation sits outside the ELC (Elementary Logarithmic Closure) interior.

We tested it on two datasets.

## The measurement

**Dataset 1:** the 265-equation natural-science catalog from the foundation audit. Each row tagged ELC-interior (admits a finite real EML tree under F16 routing) or boundary/exterior.

**Dataset 2:** 50 additional stress-test equations curated for oscillatory content — pendulum solutions, Fourier series terms, quantum wavefunctions, acoustic modes, control transfer functions.

Result: **φ = P(oscillatory ⇔ outside-ELC) = 1.0** across both datasets, with one off-diagonal.

## The exception

The Dirac delta `δ(x)`. Oscillatory in the Fourier sense; classically a distribution, not a function. Our framework treats `δ` as a non-elementary token — it has no closed-form EML tree, so it's outside the framework entirely rather than inside or on the boundary.

Dropping that case: φ = 1.0 exactly across 314 of 315 equations.

## What this says

On this catalog, **oscillation and ELC-exterior-ness are empirically co-extensive**. Every equation involving genuine oscillation lives outside or on the boundary. Every non-oscillatory equation lives inside. T01 predicts this function-by-function; the new finding is the frequency on real science: 314 of 315.

## What this doesn't say

It doesn't say every oscillatory function is EML-infinite in all senses. The complex EML gateway brings `sin` and `cos` into 1-node reach via `Im(eml(ix, 1))`. "Outside ELC over the reals" is consistent with "1 node over the complex numbers".

It doesn't claim the correlation is necessary — a catalog weighted toward Fourier analysis would show the same pattern more densely; pure-arithmetic ones would show neither side.

## Physics interpretation

Oscillation is the signature of periodic phenomena — eigenmodes, standing waves, cycles. Real EML filters these out; complex EML admits them via `ix` as a leaf. Structural reading: **EML over the reals is the algebra of non-oscillatory systems; EML over the complex numbers is the algebra of eigenstructure**. The 1-to-1 correspondence on this catalog is that distinction viewed from the equation-counting side.

## Reproduce

Catalog + ELC tags: `exploration/deep-sessions/data/expanded_genome.json`. Stress-test set and off-diagonal flag: `exploration/batch50b/B21_*`.

---

*Monogate Research (2026). "The Oscillation Boundary." monogate research blog. https://monogate.org/blog/oscillation-boundary*
