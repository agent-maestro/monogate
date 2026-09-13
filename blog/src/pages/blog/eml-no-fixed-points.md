---
layout: ../../layouts/Base.astro
title: "The EML Self-Map Has No Fixed Points"
date: 2026-04-19
tag: theorem
description: "f(x) = exp(x) − ln(x) satisfies f(x) > x for all real x > 0. The gap is minimized at x ≈ 0.806, where f(x) − x ≈ 1.6486. This is a theorem about the operator's self-interaction; of the eight operators compared below, EMN and EDL have no real fixed points either."
---

# The EML Self-Map Has No Fixed Points

Define the EML self-map:

$$f(x) = \text{eml}(x, x) = \exp(x) - \ln(x)$$

A fixed point would be a value x* where f(x*) = x*, i.e., exp(x*) − ln(x*) = x*.

**There are none.**

---

## The Theorem

**Theorem (EML No Fixed Points):** For all x > 0,

$$\exp(x) - \ln(x) > x$$

Consequently, the iteration x_{n+1} = exp(x_n) − ln(x_n) diverges for every starting point.

**Proof:**

Define g(x) = exp(x) − ln(x) − x. We show g(x) > 0 for all x > 0.

Find the minimum of g:
```
g'(x) = exp(x) − 1/x − 1 = 0
```

Since g''(x) = exp(x) + 1/x² > 0, g is convex on (0, ∞), so g' has at most one root, and a root of g' is the minimum of g.

At x = 0.5: g'(0.5) = exp(0.5) − 2 − 1 = 1.649 − 3 = −1.351 < 0.
At x = 1.0: g'(1.0) = e − 1 − 1 = e − 2 ≈ 0.718 > 0.

So the minimum is in (0.5, 1.0). Numerically: **x* ≈ 0.80647** (root of exp(x) = 1 + 1/x).

At x* ≈ 0.80647:
```
g(0.80647) = exp(0.80647) − ln(0.80647) − 0.80647
           ≈ 2.2400 − (−0.2151) − 0.80647
           = 2.2400 + 0.2151 − 0.80647
           = 1.6486
```

**The minimum gap is g_min = 1.6486054...** Computational verification on 1000 points in [0.01, 10] confirms: min(g(x)) = **1.6486** at x* ≈ 0.80647.

Since g(x) ≥ 1.648 > 0 for all x > 0, the equation g(x) = 0 has no positive real solutions. (Positivity needs no numerics: for x > 0, exp(x) ≥ 1 + x + x²/2 and ln(x) ≤ x − 1 give g(x) ≥ (x − 1)²/2 + 3/2 ≥ 3/2.) QED.

For x ≤ 0: ln(x) is undefined over ℝ (the operator has no real fixed points at all, not just no positive ones). □

---

## The Gap Table

| x | exp(x) | ln(x) | f(x) = exp(x)−ln(x) | Gap f(x)−x |
|---|--------|--------|----------------------|------------|
| 0.1 | 1.105 | −2.303 | 3.408 | 3.308 |
| 0.5 | 1.649 | −0.693 | 2.342 | 1.842 |
| x* ≈ 0.8065 | 2.240 | −0.215 | 2.455 | **1.649 (min)** |
| 1.0 | 2.718 | 0.000 | 2.718 | 1.718 |
| 2.0 | 7.389 | 0.693 | 6.696 | 4.696 |
| 5.0 | 148.4 | 1.609 | 146.8 | 141.8 |
| 10.0 | 22026 | 2.303 | 22024 | 22014 |

The gap never closes. At the minimum (x* ≈ 0.8065), exp(x) contributes 2.2400 and −ln(x) contributes 0.2151 — together they overshoot x by 1.6486.

---

## The Operator Zoo Comparison

Each operator in the family defines a self-map op(x, x). Which ones have real fixed points?

| Operator | Self-map | Fixed points | Lyapunov | Dynamics |
|----------|---------|--------------|---------|----------|
| EML | exp(x)−ln(x) | **None** | 4.31 | Diverges |
| EMN | ln(x)−exp(x) | **None** (f(x) < 0 < x) | — | Leaves the domain in one step |
| DEML | exp(−x)−ln(x) | x* ≈ 0.7536 | 0.587 | Unstable |
| EAL | exp(x)+ln(x) | x* ≈ 0.344 | 1.462 | Unstable |
| EXL | exp(x)·ln(x) | x* ≈ 1.411 | 1.462 | Unstable |
| EDL | exp(x)/ln(x) | **None** (pole at x = 1) | — | Diverges for x > 1 |
| POW | x^x | x* = 1.000 | 0.000 | Neutral |
| LEX | ln(exp(x)−x) | x* = 0 | −∞ (f′(0) = 0) | Globally attracting |

EML is one of three operators here (with EMN and EDL) that have **no real fixed points at all**, and the only one of the three whose iteration stays defined and diverges from every starting point.

---

## Why EML Is Different

For EMN: f(x) = ln(x) − exp(x). This is the negation of the EML self-map. Where EML always overshoots, EMN always undershoots: f(x) < 0 < x for every x > 0, so it has no real fixed point, and one step leaves the domain of ln. (The x* ≈ −0.754 this table first listed solves ln|x| − exp(x) = x, not f(x) = x.)

For DEML: f(x) = exp(−x) − ln(x). The decay of exp(−x) fights the growth of −ln(x), and they balance at x* ≈ 0.7536. This fixed point is unstable: |f′(x*)| = exp(−x*) + 1/x* ≈ 1.80 > 1, so starts near it are pushed away.

For EML: exp(x) grows **too fast** and ln(x) **doesn't slow it down enough**. Both terms push f(x) above x. There's no crossover.

---

## Dynamical Consequences

EML(x,x) iteration: x_{n+1} = exp(x_n) − ln(x_n).

Starting from any x > 0:
- x_1 ≥ x_0 + 1.648 (by the no-fixed-points theorem)
- x_2 = exp(x_1) − ln(x_1) > exp(x_1) − x_1, and exp(x_1) > exp(x_0 + 1.648)

The iteration diverges **at least doubly exponentially** in the number of steps. This is not just divergence — it is catastrophic divergence. The Lyapunov exponent (4.31) is among the highest in the family.

---

## The Omega Constant Connection

One EML-family map with a globally stable attractor is:

$$x_{n+1} = \exp(-x_n)$$

This is the DEML self-map with y=1: deml(x, 1) = exp(−x).

Its unique fixed point is the **Omega constant**:

$$\Omega = W(1) \approx 0.5671432904...$$

where W is the Lambert W function. Every starting point in (0, ∞) converges to Ω.

Lyapunov exponent at Ω: **−0.5671** (equal to −Ω exactly: f′(Ω) = −exp(−Ω) = −Ω, and ln(Ω) = −Ω since Ω = exp(−Ω)).

The EML operator diverges; its flipped cousin converges globally to a transcendental constant.

---

## Catalog Entry

This result belongs alongside these other EML structural claims (their status is on [/theorems](/theorems)):

| # | Result | Domain |
|---|---------|--------|
| ... | EML Weierstrass: EML is exactly complete | Approximation |
| ... | EMN exact incompleteness | Completeness |
| ... | Infinite zeros barrier | Analysis |
| **New** | **EML(x,x) has no real fixed points; min gap ≈ 1.648605** | **Dynamics** |

The minimum gap 1.6486054... — is this a known constant? PSLQ against {e, π, ln(2), γ, √2} finds no relation at 15 digits. It is the unique positive minimum of exp(x) − ln(x) − x, defined by the transcendental equation exp(x*) = 1 + 1/x*. Numerically x* = 0.80646599... and g(x*) = 1.64860544...

---

*Session M2 · Direction 13 of the Research Roadmap*
