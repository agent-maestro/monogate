---
layout: ../../layouts/Base.astro
title: "Negation in Two Nodes — For All Real x"
description: "The neg gap is closed: exl(0, deml(x,1)) computes −x in 2 nodes for all x ∈ ℝ, with no domain restriction. Whether one node can do it depends on the operator family; no search on record settles it."
date: "2026-04-20"
author: "Monogate Research"
tags: ["EML", "SuperBEST", "negation", "optimality"]
---

# Negation in Two Nodes — For All Real x

<p style="color: var(--muted); font-style: italic;">Correction (2026-09-13): this post called 2 nodes the minimum, citing an exhaustive 1-node search. The only 1-node neg search on record rounds each value to 6 decimals and then compares it with −x at tolerance 1e−7, so at x = π it rejects every tree, exact ones included, and its "none found" shows nothing. The 2-node construction holds for all real x. Whether 1 node can compute neg depends on the operators and constants allowed: LEpow(x, −1) = ln((eˣ)⁻¹) = −x is 1 node in a wider operator list.</p>

The negation entry in the SuperBEST routing table was the last open question.
Prior best: 4 nodes for general domain, 2 nodes for x > 0 only.

After an exhaustive N=3 search, the answer is: **2 nodes, no domain restriction.**

---

## The Construction

```
Node 1:  D = deml(x, 1)    = exp(−x) − ln(1) = exp(−x)
Node 2:  R = exl(0, D)     = exp(0) · ln(exp(−x)) = 1 · (−x) = −x
```

**Why this works for all x ∈ ℝ:**

`deml(x, 1) = exp(−x)` is always strictly positive — no logarithm of x is
ever taken. The second node then extracts −x exactly:

```
exl(0, exp(−x)) = exp(0) · ln(exp(−x)) = 1 · (−x) = −x
```

The constant 0 (a free constant in the framework) eliminates the exponential
factor. What remains is the logarithm of exp(−x), which is exactly −x.

---

## Why the Earlier 4-Node Construction Was Unnecessary

The 4-node general construction `emn(1, eml(eml(1, eml(x,1)), 1))` was correct
but not minimal. It worked by routing through:

```
eml(x,1) = exp(x) → eml(1,exp(x)) = e−x → eml(e−x,1) = exp(e−x) → emn(1,·) = −x
```

This builds a domain-free path by lifting x through exp before extracting it.
But the EXL/DEML path is shorter:

```
deml(x,1) = exp(−x)            [1 node, always positive]
exl(0, exp(−x)) = −x            [1 node, EXL logarithm extracts −x exactly]
```

DEML already produces a positive quantity from x without going through ln(x).
EXL then uses that quantity as the argument to its logarithm — no domain issue.

---

## Summary Table

| Domain | Nodes | Construction | Status |
|--------|-------|-------------|--------|
| all x ∈ ℝ | **2n** | `exl(0, deml(x,1))` | Holds for all real x; minimality unsettled (the N=1 search on record rejects exact trees) |
| x > 0 (alt) | 2n | `emn(exl(0,x), 1)` | Also 2n, domain-restricted |
| all x ∈ ℝ (old) | ~~4n~~ | `emn(1,eml(eml(1,eml(x,1)),1))` | Superseded |

Both domains take 2 nodes with these constructions. That no 1-node neg exists was
never established: the N=1 check over 54 cases rounds values and rejects exact trees,
and with a wider operator list LEpow(x, −1) = ln((eˣ)⁻¹) = −x is 1 node. The new
general construction makes the domain-restricted version obsolete.

---

## The SuperBEST Table Is Complete

With neg closed at 2n, the full routing table is:

| Op | Nodes | Construction |
|----|-------|-------------|
| exp(x) | 1 | eml(x,1) |
| exp(−x) | 1 | deml(x,1) |
| ln(x) | 1 | exl(0,x) |
| div(x,y) | 1 | edl(x,y) |
| recip(x) | **1** | **elsb(0,x)** (R16-C1) |
| **neg(x)** | **2** | **exl(0,deml(x,1))** |
| mul(x,y) | 2 | elad(exl(0,x),y) (T10u) |
| sub(x,y) | 2 | lediv(x,eml(y,1)) (T33) |
| pow(x,n) | 3 | eml(exl(ln(n),x),1) |
| add(x,y) | 3 | eal(exl(0,x),eml(y,1)) |

**Total: 18 nodes** vs 73 naive = **75.3% savings** (SuperBEST v4).

Both domains were said to converge to 21 nodes, which is the SuperBEST v1 total; this v4 table
totals 18. This post also said every entry except add (general, 11n) was optimal by exhaustive
search at the level below. That did not hold: later constructions cut pow to 1 node for x > 0,
mul to 1 node for x, y > 0, and add to 2 nodes for all real x, y (ADD-T1). The current table is on
[/superbest](/superbest).

---

## What "Optimal" Meant Here

For each entry at N nodes, optimality means:
- Exhaustive search at N−1 nodes found **zero** constructions
- The N-node construction exists and is verified

For neg: the N=1 check (54 cases: 6 operators × 9 terminal combinations
from {0,1,x}) reported no 1-node neg, but the search on record rounds each value to
6 decimals and compares it with −x at tolerance 1e−7, so at x = π it rejects every
tree, exact ones included. The 2-node construction exists; that 2n is the minimum
over those six operators rests on no working search.

---

> Monogate Research (2026). "Negation in Two Nodes — For All Real x."
> monogate research blog. Sessions N1–N10.
