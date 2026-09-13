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

<p style="color: var(--muted); font-style: italic;">Second correction (2026-09-13): the depth table listed functions at depths with no EML tree behind them. exp(−x) and exp(cx) are not depth-1 EML trees, the sinh tree used a −x leaf and a division by 2, and arctan, x^r and add had no depth-3 tree (add cannot have one, since x + 1 needs depth 4). The "unifying mechanism" section rested on a Depth Stability Theorem that sin refutes, and is withdrawn. The table now says what backs each row.</p>

**Tier: CONJECTURE (T30, T31) — neither has a proof; T30 is refuted in part (x + 1 has depth 4)**

Every function computable by EML trees has a *depth*: the fewest levels of eml nodes, counted along
the longest path from the root to a leaf, in a tree that computes it exactly. Leaves are x and
constants. (For a chain such as exp^k, the depth is also the node count.) Four sessions set out the
picture below.

---

## The Spectrum

| Depth | Functions | What backs it |
|-------|-----------|-------|
| 0 | constants, x | leaves, no operator |
| 1 | exp(x) | eml(x,1) = exp(x) |
| 1 | sin(x), cos(x) over ℂ | the imaginary and real parts of eml(ix, 1), taking ix as the input (T_EULER_LEAN) |
| ? | exp(−x), exp(cx) | listed at 1, but eml(−x, 1) and eml(cx, 1) are not EML trees: −x and cx are not leaves. No depth-1 tree equals exp(−x): each is a constant, eᶜ − ln x, eˣ − ln c or eˣ − ln x |
| ? | tan(x) over ℂ | listed at 1 ("T07 Euler gateway"); no tree is given |
| — | 1/x, **x·y**, x/y | F16 node counts, not EML depth: 1/x = ELSb(0,x) is **1 node** (R16-C1), and x·y is 2 nodes by the construction below |
| 3 | ln(x) on (0, ∞) | eml(1, eml(eml(1,x),1)); no EML tree of depth ≤ 2 (listed at 2 before 2026-09-13) |
| ? | sinh(x), cosh(x) | listed at 3 (see the corrections below); no EML tree is given |
| ? | arctan, x^r | listed at 3; no tree is given, and x^r = exp(r·ln x) passes through ln x, which already needs depth 3 |
| 4 | x + 1 on (0, ∞) | no EML tree of depth ≤ 3 |
| ≥ 4 | add | listed at 3; setting y = 1 in a depth-3 tree for x + y would give x + 1 at depth 3 |
| ? | sub | listed at 3; no tree is given |
| k | exp^k(x) | iterated exponential, k nested nodes; exactly k is settled only for k ≤ 4 (below) |
| ∞ | sin(x), cos(x) over ℝ | no real EML tree at any depth, proved in Lean by periodicity (MachLib); the zero-count route (T01) has open steps |

> **Correction (2026-04-20):** sinh(x) and cosh(x) were previously listed at depth 2. This note moved
> them to 3, said no 2-node EML tree can produce sinh or cosh, and gave the tree
> `eml(x, eml(eml(-x,1), 1)) / 2 = (eˣ − e⁻ˣ)/2` for sinh.
> The claim T30(c) — all standard functions have depth ≤ 3 — was later refuted: x + 1 has depth exactly 4.

> **Correction (2026-09-13):** that sinh tree is not an EML tree. It uses −x as a leaf and divides by 2,
> and neither is an eml node; its three eml nodes do compute eˣ − e⁻ˣ once −x is allowed as a leaf.
> No EML tree for sinh or cosh is given, and nothing backs "no 2-node tree", so both depths are unknown.

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
`python/scripts/mul_lower_bound_search.py` (removed from this repository in bec74da7; see Reproduce).
The search found exactly 4 matching trees (two symmetric pairs), all using ELAd as the outer
operator. It is not the minimum in the current F16: exp(ln x + ln y) = x·y is 1 node for x, y > 0.

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
1. T01 (EML Universality): every elementary function is an exact EML tree
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

Empirical data from the depth-6 search (printed on the depth-6 post): 13,598 distinct positive imaginary parts, not 700, closest approach
Im = 0.999995 (gap 4.76×10⁻⁶). That bounds the approach at depth 6; it does not show the
gap goes to 0. Over leaves {1, z} the density claim above would imply it, but that claim is open too.

---

## The unifying mechanism (withdrawn)

This section said the hierarchy stays rigid because of the **tan(1) obstruction** (the "Depth Stability
Theorem", S99): tan(1) is transcendental, so i cannot be reached from {1} by EML₁ trees, so no function
collapses to a lower depth under complexification, so depth_ℂ(f) = depth_ℝ(f) for every f in the EML
Atlas. It called the impossibility of constructing i the single source of all rigidity in the hierarchy.

The last step is false. sin has no real EML tree at any depth, while over ℂ it is the imaginary part of
the one-node tree eml(ix, 1), so its depths over ℂ and over ℝ differ with i still unbuilt. The "(T18)" on
the middle arrow cited nothing in the catalog. The depth results that stand (ln x at 3, x + 1 at 4,
exp^k for k ≤ 4, sin with no real tree) are about real trees, and their proofs do not use tan(1). See
[Does tan(1) Control Everything?](/blog/tan1-obstruction).

---

## Updated SuperBEST table (F16 routing)

| Operation | Nodes (F6) | Nodes (F16) | Savings |
|-----------|-----------|------------|---------|
| mul(x,y)  | 3         | **2** (new) | 85% |
| All other operations | unchanged | unchanged | — |
| **Total** | **21** | **20** | **72.6%** |

Savings are measured against the naive costs in `python/monogate/superbest.py`: 13 nodes for mul and
73 for the whole table. 1 − 2/13 = 84.6% and 1 − 20/73 = 72.6%.

The F16 figure is from April. In the current F16, x·y is 1 node for x, y > 0: exp(ln x + ln y).

---

## Documents

- `python/paper/theorems/Depth_Spectrum_Self_Contained.tex` — self-contained T30 argument; it reports GAP-3 + GAP-4 closed, but x + 1 refutes its depth-3 claim and its general lower bound has a gap
- `python/paper/cost_theory/R17_T30_Hardy_Field_Verification.tex` — gap analysis; Lemma 4.2 repair
- `python/paper/theorems/Mul_Lower_Bound_Tightened.tex` — exhaustive search + structural argument
- `python/paper/theorems/Complex_Closure_Density.tex` — Runge + density argument (incomplete; see above)
- `python/paper/theorems/EML4_Gap_Resolution.tex` — strict hierarchy, depth-4 witness
- `python/paper/theorems/Unified_EML_Lower_Bound_Closure.tex` — the unified T30/T31

**Reproduce:** the three scripts this post ran were removed from this public repository in bec74da7
(research scripts now live in the private monogate-research repository). They remain in its history.
The multiplication search was re-run on 2026-09-13 and reproduces the counts above; the other two
were not re-run.
```bash
git show b7ffdb0a:python/scripts/mul_lower_bound_search.py > mul_lower_bound_search.py
python mul_lower_bound_search.py
git show b7ffdb0a:python/scripts/eml4_gap_search.py > eml4_gap_search.py
git show b7ffdb0a:python/scripts/complex_density_search.py > complex_density_search.py
```

---

**Cite:** Monogate Research (2026). "The Depth Spectrum of EML."
monogate research blog. https://monogate.org/blog/depth-spectrum
