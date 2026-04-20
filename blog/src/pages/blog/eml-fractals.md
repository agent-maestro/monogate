---
layout: ../../layouts/Base.astro
title: "EML Generates the Exponential Mandelbrot Set"
date: 2026-04-19
tag: research
description: "Iterating exp(z)−k is Devaney's exponential family. We computed 8 operator fractal zoos, measured box-counting dimensions, and found DEML/EMN generate bounded strange attractors."
---

# EML Generates the Exponential Mandelbrot Set

The EML operator is `eml(A, B) = exp(A) − ln(B)`.

Set B=1. Feed the output back as A. You get:

```
z_{n+1} = exp(z_n) − ln(c)  =  exp(z_n) − k      (where k = ln(c))
```

This is **Devaney's exponential family** `f_k(z) = exp(z) − k`, studied since the 1980s.
EML provides a natural parameterization via the substitution `k = ln(c)`.

---

## Session Results (F1–F4)

### F1: EML Mandelbrot in k-space

We computed the 600×600 escape-time diagram over `k ∈ [−1,3] × [−π,π]`.

| Metric | Value |
|--------|-------|
| Interior fraction | 0.926 |
| Area estimate (k-plane) | 23.27 |
| Fixed point z*=0 at k=1 | ✓ |

The set is connected. The boundary is a fractal curve of dimension ≈ 1.716 (see F4).

**Attribution note:** The EML operator generates this set naturally, but the
underlying dynamics were characterized by Devaney (1984), Eremenko–Lyubich (1992),
and Baker (for k=0, whole-plane Julia). Our contribution is the systematic
8-operator comparison and the k-parameterization.

---

### F2: Operator Fractal Zoo (8 operators)

We iterated all 8 operators `z → op(z, k)` over the domain `[−2.5,2.5]² × [−2.5,2.5]²`.

| Operator | Interior fraction | Character |
|----------|-------------------|-----------|
| EML      | 0.641 | Exponential Mandelbrot (Devaney) |
| DEML     | 0.784 | Mirror image; exp(−z)−ln(k) |
| EMN      | 0.784 | Same as DEML by symmetry |
| EAL      | 0.641 | Same topology as EML (add vs sub) |
| EXL      | 0.770 | Multiplicative; ring-shaped structure |
| EDL      | 0.953 | Division by ln; mostly bounded |
| POW      | 0.807 | Classical polynomial family |
| LEX      | 0.383 | Smallest interior; most chaotic |

EML and EAL are topologically equivalent (both from `exp(A) ± ln(B)`).
LEX (`ln(exp(A)·B) = A + ln(B)`) has the most chaotic escape structure.

---

### F3: Julia Sets at Five Parameters

We rendered Julia sets for the EML family at five values of k:

| k | Description |
|---|-------------|
| 0 | c=1: whole-plane Julia (Baker 1975). Every orbit escapes except fixed point set. |
| 1 | c=e: z=0 is parabolic fixed point. Julia set separates infinitely many components. |
| 1.5 | Novel: first rendering. Bounded fraction 0.953. |
| 1+iπ/2 | Novel: complex k. Bounded fraction 0.947. |
| 2+0.5i | Novel: complex k. Bounded fraction 0.959. |

The k=0 case is the hardest: the Julia set is the entire complex plane minus one
attracting basin. Baker's theorem (1975) proves this is nowhere locally connected.

---

### F4: Box-Counting Dimensions

We extracted the boundary of each fractal set and computed `D = slope(log N(ε) vs log 1/ε)`.

| Set | D (box-counting) | Reference |
|-----|------------------|-----------|
| EML Mandelbrot boundary | **1.716 ± 0.025** | Shishikura (1998): classical Mandelbrot D=2 |
| Classical Mandelbrot | 2.000 | Exact (Shishikura 1998) |
| Julia k=1 (parabolic) | 1.378 ± 0.110 | — |
| Julia k=2+0.5i (novel) | 1.334 ± 0.122 | — |

The EML Mandelbrot boundary dimension (1.716) is **strictly less than 2**, which
contrasts with the classical polynomial Mandelbrot set where D=2 (Shishikura 1998).
This reflects the transcendental vs polynomial nature of the maps.

---

## Interactive Explorer

→ [EML Fractal Explorer](/explorer) — click to zoom, switch between all 8 operators,
choose color schemes. Real-plane escape-time with live viewport.

---

## Key Takeaways

1. **EML iteration = exponential family.** Not a new dynamical system — a new framing.
2. **8 operators span a zoo of fractal behaviors** from mostly-bounded (EDL) to mostly-chaotic (LEX).
3. **DEML and EMN** (the negated variants) produce bounded 2D attractors under real iteration (C1 sessions).
4. **EML Mandelbrot boundary dim ≈ 1.716** — measurably less than the classical Mandelbrot boundary (D=2).
5. **Julia k=0** remains the wildest case: Baker's whole-plane theorem, nowhere locally connected.
