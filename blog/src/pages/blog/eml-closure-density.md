---
layout: ../../layouts/Base.astro
title: "Is the EML Closure Dense in ℂ?"
date: 2026-04-19
tag: conjecture
description: "We enumerated EML trees over the constant 1 with up to 7 nodes and tracked how close they get to π. The density conjecture is open, and one piece of evidence first given for it, an imaginary part equal to π, was a floating-point artifact."
---

# Is the EML Closure Dense in ℂ?

<p style="color: var(--muted); font-style: italic;">Correction (2026-09-13): this post's "depth" was the number of eml nodes, and its counts came from floating-point evaluation. Recomputed exactly: the 7-node tree it reported with imaginary part exactly π has imaginary part −π, because rounding put a logarithm's input on the wrong side of the branch cut; the value counts and gaps differ, and the largest gap is not shrinking; the closest approach to π/2 with 6 nodes is 0.098, not 0.00078; and the 20 random targets were not recorded, so that test cannot be re-run. The sections below are corrected in place, and the script is printed at the end.</p>

Let EML({1}) be the set of all complex numbers that can be computed by finite EML trees using only the constant leaf 1. We know:

- i ∉ EML({1}) under strict real semantics, Lean-checked (T17). Under the complex semantics this page uses, where ln(−e) = 1 + iπ, it is argued on paper, not proved.
- No tree with at most 7 nodes has imaginary part π; the one this post reported was a floating-point artifact (below)
- EML({1}) ∩ ℝ is not dense in ℝ (the real values grow doubly exponentially)

The question is whether EML({1}) ⊂ ℂ is dense in ℂ.

## The Evidence

### Imaginary values by number of nodes

| Nodes ≤ | Defined trees | Distinct values | Distinct Im values | Im range |
|-------|-------------|----------------|-------------------|----------|
| 4 | 21 | 19 | 1 | [0, 0] |
| 5 | 55 | 47 | 2 | [−π, 0] |
| 6 | 153 | 127 | 3 | [−π, 1.508] |
| 7 | 454 | 362 | 9 | [−π, 4.805] |

The number of distinct imaginary values jumps at 5 nodes — exactly when the first complex value appears, from the logarithm of a negative real. With 7 nodes there are 9. (This post first printed 54, 147 and 428 values, and 10 imaginary values at 7 nodes, from floating-point evaluation.)

### Gaps between imaginary values

With 7 nodes the imaginary values are −π, −0.765, 0, 0.244, 1.083, 1.481, 1.508 (two values that agree to four digits) and 4.805. The largest gap is 3.30, between 1.508 and 4.805, and the mean gap is 0.99. The largest gap is 3.14 with 5 nodes, 3.14 with 6 and 3.30 with 7, so the mesh is not shrinking yet at these sizes. (This post first gave a largest gap of 2.38 and a mean of 0.88 at 7, and called the mesh shrinking.)

### Approach to π

This post reported a 7-node tree with value exactly 2.5206 + 3.1416i: `eml(1,eml(eml(1,eml(1,eml(eml(eml(1,1),1),1))),1))`. Floating point does give 2.5206 + 3.1416i. Exactly, the value is 2.5206 − 3.1416i. Its inner value e^(r − iπ) is a negative real, floating point returns it with a tiny negative imaginary part, and the next logarithm lands on the other side of the branch cut. No tree with at most 7 nodes has imaginary part π. As a distance from the number π, the closest value is 0.171 away with 6 nodes and 0.0103 with 7.

### Approach to π/2

Distance to π/2: 0.571 with 1 node, 0.147 with 2, 0.0978 with 6 and 0.0112 with 7. (This post first gave 0.00078 at 6.)

### Random target test (20 targets, depth ≤ 6)

The 20 targets were not recorded, so this test cannot be re-run; the figures below are from the original floating-point run.

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
1. **Real:** sin(x) is impossible: no real EML tree of any depth equals it, proved in Lean by periodicity (the zero count alone does not rule it out)
2. **Complex exact:** i is not constructible (argued on paper; Lean-checked only under strict real semantics, T17)
3. **Complex approximate:** i is approachable (conjectured from density)
4. **Complex limit:** sin(x) = limit of EML trees (expected from density + Weierstrass)

EML arithmetic sits between "incomplete over ℝ" and "complete in the complex limit."

## What Would Prove It

A proof of the Im-density lemma: every open interval in ℝ contains a value Im(T) for some EML tree T over {1}. One route: show EML({1}) contains elements in every angular sector — then the argument function gives dense Im values automatically.

This is Direction 3, session CD8. Status: open.

## Reproduce

Every tree over the leaf 1 with at most 7 nodes, evaluated exactly with the principal complex logarithm (mpmath, 50 digits), and the floating-point evaluation of the tree first reported:

```python
import cmath, mpmath as mp                          # pip install mpmath
mp.mp.dps = 50
REL = mp.mpf(10) ** -30
def eml(a, b):                                      # exact principal branch; None where ln 0 or e^a is out of reach
    if b == 0 or mp.re(a) > 1e5: return None
    ea, lb = mp.e**a, mp.log(b)
    if abs(mp.im(ea)) <= REL * abs(ea): ea = mp.re(ea)   # e^(r - i*pi) is real
    z = ea - lb
    return mp.mpf(0) if abs(z) <= REL * max(abs(ea), abs(lb)) else z
N = {0: [mp.mpf(1)]}                                # every tree over the leaf 1, by number of eml nodes
for n in range(1, 8):
    N[n] = [z for i in range(n) for a in N[i] for b in N[n - 1 - i] for z in [eml(a, b)] if z is not None]
    vals = {mp.nstr(z, 25): z for k in range(n + 1) for z in N[k]}.values()
    ims = sorted({float(mp.im(z)) for z in vals})
    print(f"<= {n} nodes: {sum(len(N[k]) for k in range(n + 1))} defined trees, {len(vals)} distinct values, "
          f"{len(ims)} distinct Im in [{ims[0]:.4f}, {ims[-1]:.4f}]; min |z - pi/2| {mp.nstr(min(abs(z - mp.pi/2) for z in vals), 3)}, "
          f"min |z - pi| {mp.nstr(min(abs(z - mp.pi) for z in vals), 3)}")
gaps = [b - a for a, b in zip(ims, ims[1:])]
print("Im values with <= 7 nodes:", [round(v, 4) for v in ims], " max gap", round(max(gaps), 4), " mean gap", round(sum(gaps) / len(gaps), 4))
t = 'eml(1,eml(eml(1,eml(1,eml(eml(eml(1,1),1),1))),1))'    # the tree first reported as 2.5206 + 3.1416i
fe = lambda a, b: cmath.exp(a) - cmath.log(b)
print("floating point:", eval(t, {'eml': fe}), "  exact:", mp.nstr(eval(t, {'eml': eml}), 12))
```

Output:

```
<= 1 nodes: 2 defined trees, 2 distinct values, 1 distinct Im in [0.0000, 0.0000]; min |z - pi/2| 0.571, min |z - pi| 0.423
<= 2 nodes: 4 defined trees, 4 distinct values, 1 distinct Im in [0.0000, 0.0000]; min |z - pi/2| 0.147, min |z - pi| 0.423
<= 3 nodes: 9 defined trees, 9 distinct values, 1 distinct Im in [0.0000, 0.0000]; min |z - pi/2| 0.147, min |z - pi| 0.423
<= 4 nodes: 21 defined trees, 19 distinct values, 1 distinct Im in [0.0000, 0.0000]; min |z - pi/2| 0.147, min |z - pi| 0.423
<= 5 nodes: 55 defined trees, 47 distinct values, 2 distinct Im in [-3.1416, 0.0000]; min |z - pi/2| 0.147, min |z - pi| 0.285
<= 6 nodes: 153 defined trees, 127 distinct values, 3 distinct Im in [-3.1416, 1.5080]; min |z - pi/2| 0.0978, min |z - pi| 0.171
<= 7 nodes: 454 defined trees, 362 distinct values, 9 distinct Im in [-3.1416, 4.8047]; min |z - pi/2| 0.0112, min |z - pi| 0.0103
Im values with <= 7 nodes: [-3.1416, -0.7647, 0.0, 0.2437, 1.0825, 1.4814, 1.508, 1.508, 4.8047]  max gap 3.2968  mean gap 0.9933
floating point: (2.520593917172769+3.141592653589793j)   exact: (2.52059391717 - 3.14159265359j)
```

---

*Sessions CD1–CD11 · Direction 3 of the Research Roadmap*
