---
layout: ../../layouts/Base.astro
title: "The Zeros Bound Conjecture: How Many Zeros Can an EML Tree Have?"
date: 2026-04-19
tag: conjecture
description: "A conjectured bound of 2k+2 real zeros for an EML tree with k internal nodes, an induction for it that does not hold, and zero counts for all 862,118 trees with at most 8 internal nodes: at most 3 sign changes on [−2, 2]."
---

# The Zeros Bound Conjecture

<p style="color: var(--muted); font-style: italic;">Correction (2026-09-13): this post said it proved a tight bound of 2k + 2 zeros. There is no proof, and nothing shows the bound is tight. The induction below fails at its Rolle step, and its own arithmetic gives 2k + 4. As first stated the bound is false: eml(x, eml(eml(x,1),1)) = eˣ − ln(e^(eˣ)) has 3 internal nodes and is zero for every real x. The search counts were misreported too; the table now follows the search record.</p>

The Infinite Zeros Barrier says: sin(x) is not a finite real EML tree because it has infinitely many zeros. That zero-counting route is not complete (InfiniteZerosBarrier.lean still has sorries in Part D), but the conclusion is proved in Lean in MachLib by a periodicity argument (`sin_not_in_eml_any_depth_unconditional`). And the zero-counting argument was qualitative — it only said "finitely many," not how many.

This note proposes a quantitative version.

## The Bound

**Conjecture (Zeros Bound):** Every EML tree over {1, x} with k internal nodes that is not identically zero has at most 2k + 2 real zeros on any bounded interval where every ln argument in the tree is positive.

**Attempted proof** (structural induction on k; it does not go through):

*Base case (k = 0):* The leaf x has 1 zero. The leaf 1 has 0 zeros. Both satisfy the bound 0 + 2 = 2. ✓

*Inductive step:* Let T = eml(L, R) with L having k_L nodes and R having k_R nodes, where k_L + k_R = k − 1.

Zeros of T occur when exp(L(x)) = ln(R(x)). Let F(x) = exp(L(x)) and G(x) = ln(R(x)).

The step cited Rolle's theorem for two claims: that the number of intersections of F and G is bounded by the number of monotone pieces of F plus those of G, and that a function with z zeros has at most z + 1 monotone pieces. Both are false. F(x) = x and G(x) = x + ½ sin x are each monotone, yet meet at every nπ; and 2 + sin x has no zeros but turns around every π. The computation built on them was:

```
zeros(T) ≤ (zeros(L) + 1) + (zeros(R) + 1)
          ≤ (2k_L + 3) + (2k_R + 3)
          = 2(k_L + k_R) + 6
          = 2(k − 1) + 6
          = 2k + 4
```

Even granting those steps, this gives 2k + 4, not 2k + 2. The tighter 2k + 2 was said to follow because the exp factor in F is positive and non-oscillatory, but exp(L) turns around exactly where L does, so that does not reduce the piece count.

## Zero Counts

We enumerated all 862,118 EML trees over {1, x} with up to 8 internal nodes and counted sign changes on [−2, 2], on a 0.01 grid with a ±0.05 dead band (so zeros outside [−2, 2], and zeros where a tree only touches 0, are missed):

| Internal nodes k | Trees evaluated | Max sign changes observed | Conjectured 2k+2 |
|---------|----------------|-------------------|------------|
| 0 | 2 | 1 | 2 |
| 1 | 4 | 0 | 4 |
| 2 | 16 | 1 | 6 |
| 3 | 80 | 2 | 8 |
| 4 | 448 | 2 | 10 |
| 5 | 2,688 | 2 | 12 |
| 6 | 16,896 | 2 | 14 |
| 7 | 109,824 | 3 | 16 |
| 8 | 732,160 | 3 | 18 |

For 3 ≤ k ≤ 6 the observed maximum is 2 sign changes, and at 7 and 8 internal nodes it is 3 — far below 2k+2, which is itself unproved. Counts up to 8 internal nodes do not show whether the maximum keeps growing with k.

## Corollaries

Corollaries 1–3 hold only if the conjectured bound does.

**Corollary 1 (Quantified Barrier):** A function with more than 2k + 2 zeros on a bounded interval cannot be represented by any EML tree with k nodes. To approximate sin(x) on [0, 100π] within less than 1, a tree must change sign between consecutive peaks, 99 times, so you need at least 49 nodes.

**Corollary 2 (Class Exclusion):** The entire class of infinitely-oscillatory functions — sin, cos, Bessel functions, and more — is excluded from real EML arithmetic at every finite depth.

**Corollary 3 (Complexity Lower Bound):** The number of zeros of a target function gives a lower bound on the EML tree size needed to represent it exactly.

**Corollary 4 (Non-density over ℝ)** does not follow, even from the bound: a zero bound for each k says nothing about trees of unbounded size (a polynomial of degree n has at most n zeros, and polynomials are dense in C[a, b]). Whether real EML trees over {1, x} are dense in C[a, b] is not settled.

## Open Questions

1. Does the 2k + 2 bound hold at all? If it does, is the maximum k + O(1), or O(1) for all k?
2. Is there a proof of 2k + 2, or of any zero-count bound for depth-k trees? In Lean, that bound is the open sorry in InfiniteZerosBarrier.lean.
3. The observed maximum rose from 2 to 3 at 7 internal nodes. Does it keep growing with k?

---

*Sessions TZ1–TZ9 · Direction 2 of the Research Roadmap*
