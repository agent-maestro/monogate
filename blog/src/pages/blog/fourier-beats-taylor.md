---
layout: ../../layouts/Base.astro
title: "Fourier Beats Taylor by 100x in EML Node Count"
date: 2026-04-19
tag: observation
description: "sin(x) costs 101 nodes as an 8-term Taylor series by April's BEST-routing count, and 1 complex EML node through Euler's formula. The accuracy figures first printed beside the Taylor and Fourier counts are not reproduced."
---

# Fourier Beats Taylor by 100x in EML Node Count

<p style="color: var(--muted); font-style: italic;">Correction (2026-09-13): the node counts on this page are April BEST-routing counts. The Taylor table's MSE column is not reproduced: the exact Taylor errors are far smaller, so 10⁻⁶ is reached at 6 terms, not 8. The square-wave error falls like 1/N, not 1/N², and the Fourier table's 21 nodes for sin contradict the 1 node given in the text. /theorems lists the node-count gap as an observation (O-FOURIER), so the tag is now observation. The script is printed at the end.</p>

Every EML tree is a composition of exp and ln. To approximate sin(x) using real arithmetic, you need an infinite Taylor series — and in BEST routing, that costs 101 nodes for 8 terms.

But there's a shortcut. And it has everything to do with why the operator is called **exp-minus-ln**.

---

## The Taylor Route

sin(x) = x − x³/3! + x⁵/5! − x⁷/7! + ···

Each term requires:
- pow(x, 2k+1): **3 nodes** (EXL, best known)
- div by (2k+1)!: **1 node** (EDL, as counted in April; EDL(x, y) = eˣ/ln y is not itself a division)
- alternating sign: **6 nodes** (neg via EDL)
- sum with previous term: **3 nodes** (mixed EAL bridge)

Per term: 3 + 1 + 6 = 10 nodes. Plus 3 nodes per addition to sum them.

**Total for K terms:**

| K terms | Nodes (April count) | MSE as first printed | MSE of the Taylor polynomial |
|---------|-------|----------------|----------------|
| 2 | 23 | 2.55e+00 | 4.01e-01 |
| 4 | 49 | 8.21e-02 | 3.03e-04 |
| 6 | 75 | 4.66e-04 | 7.39e-09 |
| 8 | 101 | 7.95e-07 | 1.71e-14 |
| 10 | 127 | 5.39e-10 | 6.52e-21 |

The first-printed MSE column is not reproduced: it is far larger than the error of the Taylor polynomials themselves (script below). By their error, 6 terms, 75 nodes by this count, already pass 10⁻⁶; this post said **101 nodes**.

---

## The Fourier Route

Euler's formula: exp(ix) = cos(x) + i·sin(x).

In EML: exp(ix) = eml(ix, 1) = exp(ix) − ln(1) = exp(ix).

**This is one EML node.** The imaginary part is sin(x) exactly. No approximation.

```
sin(x) = Im(eml(ix, 1))    [1 complex EML node, exact]
cos(x) = Re(eml(ix, 1))    [same node, exact]
```

This is not an approximation — it is the exact value, to floating-point precision, in a single operator application.

The Fourier series for general periodic functions costs more:

| N terms | EML nodes (April count) | Mean-square error for a square wave |
|---------|-----------|--------------------------|
| 1 | 21 | 0.189 (exact for sin: this IS sin) |
| 2 | 37 | 0.099 |
| 4 | 69 | 0.050 |
| 8 | 133 | 0.025 (Gibbs overshoot remains) |

The error falls like 1/N, not 1/N² as this table first said (script below). The 21 nodes for N = 1 also disagree with the next line, and nothing on the page derives the node counts.

But sin(x) itself is the N=1 case: **1 complex node**.

---

## The 100x Gap

| Method | Nodes for sin(x) | Error |
|--------|-----------------|-------|
| Taylor, 8 terms | **101** | 7.95e-07 |
| Fourier, 1 term | **1** | exact |

The ratio is 101:1. One hundred times fewer nodes.

---

## Why This Happens

The Taylor approach forces sin(x) into the real number line, where EML's operator family has no native trig support. Every term is a workaround: use powers and factorials to reconstruct a function that the operators weren't designed for.

The Fourier approach uses the complex path — exactly the mechanism that makes the EAL bridge work and that EMN is conjectured to use for approximate completeness (T24). In the complex plane, exp(ix) is native. sin(x) is just its imaginary component.

**The structural fact:** EML's completeness theorem holds over ℂ. In the real line, sin(x) is unreachable: no real EML tree of any depth equals it, proved in Lean by periodicity (the zero-count route has open steps). In ℂ, it costs one node.

The complex plane is not a trick — it is where EML lives natively.

---

## What This Means for BEST Routing

The BEST routing table currently tracks single-variable operations. Adding `sin` and `cos`:

| Operation | BEST operator | Nodes (April count) | Notes |
|-----------|--------------|-------|-------|
| exp(x) | EML | 1n | real |
| ln(x) | EXL | 1n | real |
| sin(x) | EML | 1n | complex path |
| cos(x) | EML | 1n | complex path |
| sinh(x) | EML | 3n | (exp(x)−exp(−x))/2 |
| cosh(x) | EML | 3n | (exp(x)+exp(−x))/2 |

exp, ln, sin, and cos all cost **1 node** in BEST. The trig functions are not special — they are Euler's formula applied once.

---

## Why the Lab Uses This

The sound engine in the Monogate lab synthesized waveforms by computing exp(iωt) for each harmonic frequency ω. Each harmonic is one EML node. A 16-harmonic instrument timbre is 16 nodes — one per frequency component.

This is exactly the Fourier representation, implemented as EML trees. The lab wasn't using Fourier synthesis as an analogy — it was literally computing EML trees, one per harmonic, taking the imaginary part.

When you heard a note in the sound experience, you were hearing the output of an EML tree.

---

## Caveat: Taylor Still Wins for Exponentials

For exp(x) itself, the identity tree costs 1 node and is exact. Taylor can only approximate exp(x) with K terms:

| K terms Taylor exp(x) | Nodes (April count) |
|-----------------------|-------|
| 2 | 11 |
| 4 | 25 |
| 8 | 53 |

Taylor approximates what EML already knows exactly. The 1-node EML identity tree for exp(x) beats every finite Taylor series — because exp is the operator's native operation.

The lesson generalizes: **EML native operations cost 1 node. Non-native operations (real trig) are expensive. Complex-path operations recover native cost.**

## Reproduce

The error of the Taylor polynomials of sin on [−π, π], and of square-wave Fourier partial sums:

```python
import math, numpy as np                                # pip install numpy
x = np.linspace(-math.pi, math.pi, 200001)
for K in range(1, 11):                                  # Taylor polynomial of sin with K nonzero terms
    T = sum((-1) ** k * x ** (2 * k + 1) / math.factorial(2 * k + 1) for k in range(K))
    print(f'Taylor K={K:2d}: MSE {np.mean((np.sin(x) - T) ** 2):.3g}  (post counts 13K-3 = {13 * K - 3} nodes)')
sq = np.sign(np.sin(x))
for N in (1, 2, 4, 8, 16):                              # square-wave Fourier partial sums
    S = 4 / math.pi * sum(np.sin((2 * k - 1) * x) / (2 * k - 1) for k in range(1, N + 1))
    m = np.mean((sq - S) ** 2)
    print(f'square wave N={N:2d}: MSE {m:.4f}, N*MSE {N * m:.3f}, N^2*MSE {N * N * m:.3f}')
```

Output:

```
Taylor K= 1: MSE 1.79  (post counts 13K-3 = 10 nodes)
Taylor K= 2: MSE 0.401  (post counts 13K-3 = 23 nodes)
Taylor K= 3: MSE 0.0189  (post counts 13K-3 = 36 nodes)
Taylor K= 4: MSE 0.000303  (post counts 13K-3 = 49 nodes)
Taylor K= 5: MSE 2.11e-06  (post counts 13K-3 = 62 nodes)
Taylor K= 6: MSE 7.39e-09  (post counts 13K-3 = 75 nodes)
Taylor K= 7: MSE 1.45e-11  (post counts 13K-3 = 88 nodes)
Taylor K= 8: MSE 1.71e-14  (post counts 13K-3 = 101 nodes)
Taylor K= 9: MSE 1.29e-17  (post counts 13K-3 = 114 nodes)
Taylor K=10: MSE 6.52e-21  (post counts 13K-3 = 127 nodes)
square wave N= 1: MSE 0.1894, N*MSE 0.189, N^2*MSE 0.189
square wave N= 2: MSE 0.0994, N*MSE 0.199, N^2*MSE 0.397
square wave N= 4: MSE 0.0504, N*MSE 0.202, N^2*MSE 0.807
square wave N= 8: MSE 0.0253, N*MSE 0.202, N^2*MSE 1.619
square wave N=16: MSE 0.0127, N*MSE 0.203, N^2*MSE 3.242
```

---

*Session M8 · Direction 13 of the Research Roadmap*
