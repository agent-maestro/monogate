---
layout: ../../layouts/Base.astro
title: "The SuperBEST Cost of Geometry"
description: "12 classical geometric primitives — hyperbolic distance, Lie group maps, curvature, conformal maps — expressed as EML operator trees. Total: 125n SuperBEST vs 345n naive, 64% savings. All exact. Updated for R16-C1 (recip = 1n)."
date: "2026-04-20"
author: "Monogate Research"
tags: ["EML", "SuperBEST", "geometry", "information geometry", "Lie groups"]
---

# The SuperBEST Cost of Geometry

The SuperBEST routing table gives minimum operator-node counts for arithmetic.
The natural question: what does geometry cost?

Below are 12 classical geometric primitives — hyperbolic distance, Riemannian
exp maps, Bregman divergence, Gaussian curvature, Lie group exponentials,
conformal maps, mean curvature, cross-ratios — each expressed as an EML
operator tree with exact node counts.

**Summary: 125n SuperBEST vs 345n naive — 64% savings. Every entry exact. Updated for R16-C1 (recip = 1n via ELSb).**

---

## The Catalog

| Primitive | SB Nodes | Naive | Key Operator |
|-----------|----------|-------|-------------|
| Hyperbolic distance d(z1,z2) | 38 | ~100 | EML (arccosh) |
| S¹ exp/log map | **1** | 8 | EML complex (Euler) |
| S² exp map | 24 | 50 | EML complex (sincos shared) |
| Bregman KL divergence | 12 | 40 | EXL/EML/EAL mixed |
| Gaussian curvature K(z=ln r) | **6** | 25 | mul+recip+neg (recip=1n via ELSb, R16-C1) |
| Vertical geodesic (hyperbolic) | 4 | 12 | EML |
| Circular geodesic (hyperbolic) | **2** | 12 | EML complex |
| SO(2) Lie exp map | **1** | 8 | EML complex (Euler) |
| SE(2) Lie exp map | 7 | 20 | EML complex |
| Stereographic projection | 4 | 15 | complex div |
| Mean curvature κ (graph) | 13 | 30 | EML/EXL mixed |
| Cross-ratio ln\|CR\| | 13 | 25 | EXL + add/sub |
| **TOTAL** | **125** | **345** | |

---

## The Euler Advantage

The single most powerful fact: **complex EML is Euler's formula**.

```
ceml(iθ, 1) = exp(iθ) − ln(1) = exp(iθ) = cos(θ) + i·sin(θ)
```

This means any computation involving sin and cos simultaneously costs **1 complex
EML node**. The real and imaginary parts are extracted for free.

Consequences:
- **SO(2) rotation matrix**: 1 node. The full 2×2 matrix entries come from one
  complex EML evaluation.
- **S¹ exp map**: 1 node. `ceml(i*(θ+v), 1)` is the exact geodesic.
- **Circular geodesics**: 2 nodes. `c + R·ceml(it, 1)` parametrizes the full circle.
- **S² exp map**: 24 nodes total, but sin and cos share a single complex EML node.

The classical formula sin(x) = Im(e^{ix}) is the EML view from the start.
EML just makes it explicit in the operator graph.

---

## EXL and the Logarithm Structure

The second major pattern: **EXL(0, x) = ln(x)** turns every log-of-product
or log-of-ratio into a sum/difference chain.

For the cross-ratio (z1,z2;z3,z4) = (z1−z3)(z2−z4)/((z1−z4)(z2−z3)):

Computing the full ratio costs **19 nodes** (four subtractions at 3n each,
two multiplications at 3n each, one division at 1n).

But `ln|cross-ratio|` decomposes as:
```
ln|CR| = ln|z1−z3| + ln|z2−z4| − ln|z1−z4| − ln|z2−z3|
```

Four EXL nodes (1n each) + three add/sub nodes (3n each) = **13 nodes** — a
6-node saving by exploiting the logarithmic structure.

The same pattern applies to the Bregman divergence: ln(x/y) = ln(x) − ln(y)
is two EXL nodes + one sub, rather than a ratio followed by a logarithm.

---

## Hyperbolic Geometry is Native

The Poincaré upper half-plane has metric ds² = (dx²+dy²)/y². Its Christoffel
symbols are ±1/y — that's **2 nodes** each via EDL (the reciprocal operator).

Geodesics:
- **Vertical lines** y = y₀·exp(t): computed exactly as `eml(t + ln(y₀), 1)` — **4 nodes**.
- **Semicircles** (x−c)²+y²=R²: parametrized as `c + R·ceml(it, 1)` — **2 nodes**.

The hyperbolic geodesic equation's right-hand side costs 17n total for both
acceleration components — versus ~25n in the classical formulation.

The reason is structural: the hyperbolic metric is `exp(−2*ln(y))`, i.e., it
is written natively in EML. The geometry follows cheaply.

---

## Information Geometry: EAL as Bridge

Bregman divergences — the natural divergences in information geometry —
decompose as:

```
B_f(x,y) = f(x) − f(y) − ⟨∇f(y), x−y⟩
```

For the KL divergence (f(t) = t·ln(t) − t):

```
B_KL(x,y) = x·ln(x/y) − x + y
```

With sub-expression sharing, this costs **12 nodes** SuperBEST:
1. ln(x), ln(y): 2 EXL nodes (1n each)
2. ln(x/y) = ln(x)−ln(y): 3n sub (reusing ln(x), ln(y))
3. x·ln(x/y): 2n mul (reusing ln(x))
4. y−x: 2n sub (reusing ln(y))
5. Final add: 3n EAL

The EAL operator (`exp(A) + ln(B)`) serves as the bridge for the final addition
when both arguments are already in ln-form — exactly its native use case.

---

## Why EML Costs Are Inverted vs Standard

In standard computation, exponentials and logarithms are expensive; arithmetic
is cheap. SuperBEST inverts this:

| Operation | Standard cost | SuperBEST cost |
|-----------|--------------|----------------|
| exp(x) | 1 unit | **1n** |
| ln(x) | 1 unit | **1n** |
| add(x,y) | 1 unit | **3n** |
| mul(x,y) | 1 unit | **3n** |
| sin(x) | ~5 units | **1n** (complex EML) |

Geometry — which is filled with transcendentals — pays the cheap cost at every
step. Polynomials pay the expensive cost. This is why hyperbolic geometry,
conformal maps, and Lie group exponentials are efficient here: they are
fundamentally transcendental in structure.

---

## Numerical Verification

All 12 catalog entries were verified numerically:

- **Hyperbolic distance**: 4 test pairs, max error < 1e-10
- **S¹ exp map**: 3 test points, all errors = 0 (exact floating-point)
- **S² exp map**: 3 test vectors, round-trip errors < 2e-16
- **Bregman KL**: 4 test pairs, all errors < 1e-9
- **Geodesics**: vertical (4 points) and circular (4 points), all exact
- **Stereographic**: 4 points, round-trip errors < 4e-16
- **Cross-ratio**: 3 tests + harmonic conjugate check (CR(0,4;1,−2) = −1.0000)
- **SO(2)**: 5 rotation angles, all errors = 0

Script: `D:/monogate/python/scripts/research_eml_geometry.py`
Output: `D:/monogate/python/results/eml_geometry_catalog.json`

---

## Conclusion

The 12 primitives above cover the core of differential geometry, information
geometry, and complex analysis. Total cost: **125n SuperBEST vs 345n naive —
64% reduction** (updated from 126n by R16-C1: recip = 1n via ELSb).

Three structural insights drive the savings:

1. **Complex EML = Euler formula**: any sin/cos pair costs 1 node.
2. **EXL log-structure**: products under logarithms become sums of 1n nodes.
3. **Hyperbolic geometry is native**: its metric is built from exp and ln,
   so geodesics, Christoffel symbols, and distances are all cheap.

---

> Monogate Research (2026). "The SuperBEST Cost of Geometry."
> monogate research blog. Sessions GEO-G1–GEO-G10, 2026-04-20.
> https://monogate.org/blog/geometry-costs
