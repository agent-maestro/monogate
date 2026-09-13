---
layout: ../../layouts/Base.astro
title: "The Depth Spectrum of EML"
description: "Every function has a minimum node count. The depth spectrum claimed here, 1, 2, 3, ∞ with no standard function at depth 4, is wrong: x + 1 has depth exactly 4. Plus: multiplication in 2 nodes for x > 0."
date: "2026-04-20"
author: "Monogate Research"
tag: conjecture
---

# The Depth Spectrum of EML

<p style="color: var(--muted); font-style: italic;">Correction (2026-09-13): this post called T30 and T31 fully proved. T30's claim that every standard function has depth at most 3 is false: x + 1 has depth exactly 4 on (0, ∞), and ln x has depth exactly 3 there, not 2. That exp^k needs exactly k nodes is settled only for k ≤ 4; the general argument has a gap in its division case. T31's density argument never builds polynomials or addition, so C02 and C03 are open. The 6-operator multiplication search covered 4,608 two-node trees, not 12,288. The sections below are corrected in place.</p>

**Tier: CONJECTURE (T30, T31) — neither has a proof; T30 is refuted in part (x + 1 has depth 4)**

Every function computable by EML trees has a *depth* — the minimum number of operator
nodes to compute it exactly. Four sessions set out the picture below.

---

## The Spectrum

| Depth | Functions | Notes |
|-------|-----------|-------|
| 0 | constants, x | leaves, no operator |
| 1 | exp(x), exp(−x), exp(cx) | eml(x,1) = exp(x) |
| 1 | tan(x) over ℂ | T07 Euler gateway |
| 2 | 1/x, **x·y**, x/y | EXL/ELSb bridge; 1/x = ELSb(0,x), **1 node** (R16-C1) |
| 3 | ln(x) on (0, ∞) | eml(1, eml(eml(1,x),1)); no EML tree of depth ≤ 2 (listed at 2 before 2026-09-13) |
| 3 | **sinh(x), cosh(x)** | corrected from 2 — see below |
| 3 | sin(x), cos(x) over ℂ, arctan, add/sub, x^r | Euler substitution; mixed routing (F16 node counts, not EML depth) |
| 4 | x + 1 on (0, ∞) | no EML tree of depth ≤ 3 |
| k | exp^k(x) | iterated exponential, k nested nodes |
| ∞ | sin(x), cos(x) over ℝ | T01: Infinite Zeros Barrier |

> **Correction (2026-04-20):** sinh(x) and cosh(x) were previously listed at
> depth 2. The correct depth is **3**. No 2-node EML tree can produce sinh or cosh.
> The explicit 3-node tree for sinh: `eml(x, eml(eml(-x,1), 1)) / 2 = (eᵡ − e⁻ˣ)/2`.
> The claim T30(c) — all standard functions have depth ≤ 3 — was later refuted: x + 1 has depth exactly 4.

---

## New result: multiplication in 2 nodes

The SuperBEST table listed `mul(x,y) = 3 nodes`. That was the minimum for the
6-operator library `{EML, EDL, EXL, EAL, EMN, DEML}` with leaves x, y, 0, 1, on x, y > 0.

With the full 16-operator family (including **ELAd**, where `ELAd(a,b) = exp(a)·b`):

```
mul(x,y) = ELAd(EXL(0, x),  y)
         = ELAd(ln(x),      y)
         = exp(ln(x)) · y
         = x · y    ✓  — 2 nodes, for x > 0
```

Found by exhaustive search over all 2-node mixed trees of the April 16-operator set in
`python/scripts/mul_lower_bound_search.py`. The search found exactly 4 matching
trees (two symmetric pairs), all using ELAd as the outer operator. It is not the minimum
in the current F16: exp(ln x + ln y) = x·y is 1 node for x, y > 0.

The 6-operator library **still requires 3 nodes** for multiplication on x, y > 0 with leaves
x, y, 0, 1: exhaustive search over all 96 one-node and 4,608 two-node trees (not 12,288)
finds no 2-node construction. Trees with other constants were not searched.

---

## Is the hierarchy strict at every level?

**T30 (Strict Hierarchy), conjectured:** For every k ≥ 1, there exists a function that requires
exactly k nodes and cannot be done in fewer.

The witness is the k-fold iterated exponential:
```
exp^1(x) = exp(x)                 — 1 node
exp^2(x) = exp(exp(x))            — 2 nodes
exp^k(x) = eml(eml(...eml(x,1)...,1),1)  — k nodes
```

Each additional level of nesting adds one exp application. The argument that no (k−1)-node tree can
compute exp^k(x), because exp^k grows strictly faster than any function expressible
with k−1 nodes (Hardy field ordering argument), has a gap in its division case. Exactly k
nodes is settled in MachLib only for k ≤ 4.

So depth-4 **does** exist — and a standard elementary function lives there:
x + 1 has depth exactly 4 on (0, ∞). The "no depth 4" statement that appears informally
is wrong even in its intended scope.

---

## Complex density (C02, still open)

**T31 (Complex Closure Density), conjectured:** EML trees are dense in H(K), the space of
holomorphic functions on any compact simply-connected K ⊂ ℂ.

Proposed proof chain (incomplete):
1. T02 (EML Universality): every elementary function is an exact EML tree
2. Classical Runge theorem: polynomials are dense in H(K)
3. EML trees include polynomials (on compact domains via Taylor construction) — not carried out: the explicit monomial tree EML(EML(EML(0,z),1/n),1) is n·exp(e/z), not zⁿ; addition is never constructed; principal-log branch cuts are not handled
4. Therefore, if step 3 held: EML trees approximate any holomorphic function on K

This would resolve **C02**, which stays open. The EML closure would be as rich as the space of holomorphic
functions — even though specific values (like i exactly) may be unreachable.

---

## Is i an accumulation point? (C03, open)

**T31b** (withdrawn): Under principal-branch semantics, i ∉ EML₁ (argued on paper; T17 covers only strict real semantics), and the claim was that i is also an
accumulation point of EML₁:

```
lim (depth → ∞) [closest EML₁ value to i] = 0
```

Empirical data from depth-6 search: 700 values with Im > 0, closest approach
Im = 0.999995 (gap 4.76×10⁻⁶). That bounds the approach at depth 6; it does not show the
gap goes to 0. Over leaves {1, z} the density claim above would imply it, but that claim is open too.

---

## The unifying mechanism: tan(1)

Why does the hierarchy stay rigid? Why can't depth collapse?

The answer is the **tan(1) obstruction** (Depth Stability Theorem, S99):
```
tan(1) is transcendental (Lindemann-Weierstrass)
  ↓
i cannot be reached from {1} by EML₁ trees
  ↓  (T18)
No function collapses to lower depth under complexification
  ↓
depth_C(f) = depth_R(f) for all f in EML Atlas
```

The impossibility of constructing i is not merely a curiosity — it is the single
source of all rigidity in the EML depth hierarchy. Remove the Lindemann-Weierstrass
obstruction and the entire structure would collapse.

---

## Updated SuperBEST table (F16 routing)

| Operation | Nodes (F6) | Nodes (F16) | Savings |
|-----------|-----------|------------|---------|
| mul(x,y)  | 3         | **2** (new) | 85% |
| All other operations | unchanged | unchanged | — |
| **Total** | **21** | **20** | **72.6%** |

The F16 figure is from April. In the current F16, x·y is 1 node for x, y > 0: exp(ln x + ln y).

---

## Documents

- `python/paper/theorems/Depth_Spectrum_Self_Contained.tex` — self-contained T30 argument; it reports GAP-3 + GAP-4 closed, but x + 1 refutes its depth-3 claim and its general lower bound has a gap
- `python/paper/cost_theory/R17_T30_Hardy_Field_Verification.tex` — gap analysis; Lemma 4.2 repair
- `python/paper/theorems/Mul_Lower_Bound_Tightened.tex` — exhaustive search + structural argument
- `python/paper/theorems/Complex_Closure_Density.tex` — Runge + density argument (incomplete; see above)
- `python/paper/theorems/EML4_Gap_Resolution.tex` — strict hierarchy, depth-4 witness
- `python/paper/theorems/Unified_EML_Lower_Bound_Closure.tex` — the unified T30/T31

**Reproduce:**
```bash
python python/scripts/mul_lower_bound_search.py
python python/scripts/eml4_gap_search.py
python python/scripts/complex_density_search.py
```

---

**Cite:** Monogate Research (2026). "The Depth Spectrum of EML."
monogate research blog. https://monogate.org/blog/depth-spectrum
