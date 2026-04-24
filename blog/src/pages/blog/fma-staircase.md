---
layout: ../../layouts/Base.astro
title: "FMA Is the Only Primitive That Matters"
description: "We measured the node-cost decay across seven basis states on 222 elementary-function equations. One primitive dominates: fused-multiply-add."
date: "2026-04-23"
author: "Monogate Research"
tag: observation
---

# FMA Is the Only Primitive That Matters

**Tier: OBSERVATION** (empirical, reproducible)

The question: as we grow the SuperBEST primitive basis, where do the savings actually come from? We measured aggregate node cost across seven basis states on 222 parseable equations drawn from a 265-row catalog of chemistry, physics, biology, neuroscience, and economics. TREE semantics, sympy-canonical form.

## The staircase

| basis                      | total nodes | savings vs naive | Δ from previous |
|----------------------------|------------:|-----------------:|----------------:|
| naive (no primitives)      |        1125 |             0.0% |        —        |
| F16 (16 canonical ops)     |        1041 |             7.5% |     −7.5 pp     |
| 23-op (F16 + Layer-2)      |        1031 |             8.4% |     −0.9 pp     |
| **23-op + FMA**            |         951 |        **15.5%** |   **−7.1 pp**   |
| + exp-affine + log-affine  |         948 |            15.7% |     −0.2 pp     |
| + sigmoid (unary)          |         939 |            16.6% |     −0.8 pp     |
| + bilinear-FMA (quaternary)|         919 |            18.6% |     −1.8 pp     |

One step dominates. FMA — `a·b + c` — contributes **7.1 percentage points** on its own. The seven Layer-2 extensions combined add 0.9 pp. Every other tested primitive adds between 0.2 and 1.8 pp. A staircase decay model wins AIC comparison (ΔAIC = 3.45) against exponential and polynomial alternatives.

## Where FMA lives

FMA matched in 52 of 222 equations across nine domains. Breakdown of marginal FMA savings by field:

- Geology: +15.3 pp (radioactive decay, geothermal gradients)
- Neuroscience: +14.1 pp (Hodgkin-Huxley, FitzHugh-Nagumo, cable equation)
- Economics: +9.1 pp (CAPM, Phillips curve, Black-Scholes d₁)
- Biology: +6.3 pp
- Chemistry: +3.4 pp
- Astrophysics: +1.6 pp
- **Electromagnetism: 0.0 pp** — structural absence

Electromagnetism has no affine-shifted structure to absorb. Maxwell's equations are products and curls. FMA catches nothing there. Other fields see FMA as their dominant structural primitive.

## What this doesn't say

The 15.5% figure is aggregate savings on this catalog. Individual equations range from 0% (most equations see nothing from FMA) to over 50% local savings (polynomial-heavy neuroscience). The claim is structural: on a representative sample of elementary-function science, FMA absorbs more cost than the entire bivariate Layer-2 extension.

It also doesn't say FMA is the unique primitive worth adopting. Bilinear-FMA adds another 1.8 pp — a second, smaller step. Softmax-style patterns would matter for ML workloads not in this catalog. But no single additional primitive we tested approaches FMA's 7.1 pp jump.

## Reproduce

Raw data: 222 per-row parsed costs under each basis state are in the private exploration repo (`exploration/deep10/catalog_parsed_v4.json`). The parse rate reflects sympy's reach on ASCII-math formulas; the remaining 43 rows are mostly summations and matrix-notation expressions outside elementary closure.

Source: 265-equation catalog (`exploration/deep-sessions/data/expanded_genome.json`). Public capcard holds the toy-basket 14n / 80.8% headline; this post is the catalog-aggregate complement.

---

*Monogate Research (2026). "FMA Is the Only Primitive That Matters." monogate research blog. https://monogate.org/blog/fma-staircase*
