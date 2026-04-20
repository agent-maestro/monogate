---
layout: ../../layouts/Base.astro
title: "Is the EML Closure Dense in ℂ?"
date: 2026-04-19
tag: conjecture
description: "We enumerated EML constant trees to depth 7, tested 20 random complex targets, and tracked how close EML gets to π. Strong evidence for a density conjecture — but not yet a theorem."
---

# Is the EML Closure Dense in ℂ?

Let EML({1}) be the set of all complex numbers that can be computed by finite EML trees using only the constant leaf 1. We know:

- i ∉ EML({1}) (proved — the strict i-unconstructibility barrier)
- π ∈ Im(EML({1})) at depth 7 (a tree exists with imaginary part exactly π)
- EML({1}) ∩ ℝ is not dense in ℝ (the real values grow doubly exponentially)

The question is whether EML({1}) ⊂ ℂ is dense in ℂ.

## The Evidence

### Imaginary values at each depth

| Depth | Total values | Distinct Im values | Im range |
|-------|-------------|-------------------|----------|
| 0–4 | 1–21 | 1 | [0, 0] |
| 5 | 54 | 2 | [−π, 0] |
| 6 | 147 | 3 | [−π, 1.508] |
| 7 | 428 | 10 | [−π, 4.805] |

The number of distinct imaginary values jumps sharply at depth 5 — exactly when the first complex value appears via ln(−e) = 1 + iπ. At depth 7 we have 10 distinct Im values ranging over a growing interval.

### Max gap (mesh) is decreasing

The maximum gap between consecutive Im values drops from 3.14 at depth 5 to 2.38 at depth 7. Average gap per depth: ≈ 0.88 at depth 7, versus 3.14 at depth 5. The mesh is shrinking.

### Approach to π

At depth 7, one EML tree evaluates to exactly **2.5206 + 3.1416i** — with imaginary part equal to π to machine precision. Distance to π on the imaginary axis: 0.

At depth 6, closest to π: distance 0.171. At depth 7: 0.000. **π appears as an Im-part value at depth 7.** (This follows from ln(−exp(x)) = x + iπ for real x.)

### Approach to π/2

Distance to π/2: 0.570 at depth 1, 0.147 at depth 2, 0.00078 at depth 6. Approaching.

### Random target test (20 targets, depth ≤ 6)

We sampled 20 complex numbers uniformly from the region [−3,3] × [−3,3]i and measured the distance to the nearest depth-6 EML value.

| Target region | Median dist at d≤6 | Max dist |
|--------------|-------------------|----------|
| Real axis | 0.064 | 0.200 |
| Imaginary axis | 0.530 | 1.784 |
| Complex | 0.660 | 1.615 |

Real targets are approached well. Imaginary and complex targets are harder at depth 6 — the Im-value set is still sparse. Maximum distance across all 20 targets: 1.784.

## The Conjecture

**Conjecture (EML Complex Closure Density):** The topological closure of EML({1}) in ℂ is all of ℂ. Equivalently, every open ball in ℂ contains an EML constant value.

### Why we believe it

The imaginary part of eml(c, v) is:

```
Im(eml(c,v)) = exp(Re(c))·sin(Im(c)) − arg(v)
```

The argument function arg(v) ranges continuously over (−π, π] as v varies over ℂ. By composing enough EML operations, the imaginary parts should cover all of ℝ (and hence ℂ via real part control).

### Why it's not yet proved

This argument is circular: to show EML({1}) hits all argument values, we need to know EML({1}) is rich enough to produce all angles — which is essentially what we're trying to prove.

The key gap: showing that Im(EML({1})) is dense in ℝ. This requires the argument function arg(v) to be dense in (−π, π] over v ∈ EML({1}), which requires EML({1}) to have elements in every angular sector of ℂ.

## The Irrational Analogy

If the conjecture is true, the picture of i's status becomes sharp:

> ℚ is dense in ℝ, but √2 ∉ ℚ. Similarly: EML({1}) is dense in ℂ, but i ∉ EML({1}).

The EML barrier hierarchy:
1. **Real:** sin(x) is impossible (infinitely many zeros)
2. **Complex exact:** i is not constructible (proved)
3. **Complex approximate:** i is approachable (conjectured from density)
4. **Complex limit:** sin(x) = limit of EML trees (expected from density + Weierstrass)

EML arithmetic sits between "incomplete over ℝ" and "complete in the complex limit."

## What Would Prove It

A proof of the Im-density lemma: every open interval in ℝ contains a value Im(T) for some EML tree T over {1}. One route: show EML({1}) contains elements in every angular sector — then the argument function gives dense Im values automatically.

This is Direction 3, session CD8. Status: open.

---

*Sessions CD1–CD11 · Direction 3 of the Research Roadmap*
