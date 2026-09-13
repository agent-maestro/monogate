---
layout: ../../layouts/Base.astro
title: "Does exp(+x) Mean Complete? A Structural Conjecture for exp-ln Operators"
date: 2026-04-20
tag: conjecture
description: "16 operators, one proposed structural rule: exp(+x) with no domain restriction implies exactly complete, exp(-x) incomplete, -exp(x) approximately complete. The Exponential Position Theorem would explain all 16 classifications at once, but none of its directions has a proof, and over ℝ it fails for EAL."
---

# Does exp(+x) Mean Complete?

<p style="color: var(--muted); font-style: italic;">Correction (2026-09-13): this post called the rule below a theorem with structural proofs. None of its directions has a proof. The forward argument (T26) borrows other operators and constants, the LEX argument (T28) is refuted by explicit trees, and the EMN (T24) and exp(−x) (T27) cases are sketches. Over ℝ the rule is false for EAL: every real EAL tree is nondecreasing, so none approximates −x. Over ℂ it is an open conjecture.</p>

**Tier: CONJECTURE** (T26–T28, structural arguments with gaps; T12 updated from Trichotomy to full characterization)

---

There are exactly 16 natural ways to combine $\exp(\pm x)$ with $\ln(y)$ using one arithmetic
operation. Classifying all 16 for completeness — the ability to represent every elementary function
as a finite tree — reveals a single structural rule that explains every case.

---

## The Rule

> **Conjecture: an exp-ln operator is exactly complete if and only if its exponential term
> is exp(+x) and the combining operation does not introduce a domain restriction.**

That's it. One sentence. If it holds, all 16 operators follow.

---

## The Conjectured Classification

| Completeness | Operators | Structural feature |
|---|---|---|
| **Exactly complete (8)** | EML, EAL, EXL, EDL, EPL, LEAd, ELAd, ELSb | exp(+x), no domain restriction |
| **Approximately complete (1)** | EMN | −exp(+x) (negation outside) |
| **Incomplete (7)** | DEML, DEMN, DEAL, DEXL, DEDL, DEPL, LEX | exp(−x) or domain-restricted |

The old "Completeness Trichotomy" (T12) described this as "1 complete / 1 approximate / 6 incomplete"
because only EML was known to be complete at the time. The full census (T25) proposes **8 complete**
operators — all of them structurally equivalent in the dimension that matters.

---

## Why exp(+x) Should Work: The Forward Direction (T26)

The argument: every complete operator can construct exp(x) in 1 node and a slope-−1 linear function
in 2 nodes. The slope-−1 construction is the key: it gives negation up to a constant offset.
That works for EML (below), but for EXL, EDL and EPL the census used the constant e, which is
not a leaf, and for LEAd it reached the identity only as a limit.

For EML specifically: `eml(c, exp(x)) = exp(c) − x`. At `c = 0`: `eml(0, exp(x)) = 1 − x`.
That's slope −1 with offset 1.

To get exact neg(x) = −x, we use the SuperBEST cross-family bridge (T09):
```
neg(x) = exl(0, deml(x,1)) = exp(0) · ln(exp(−x) − ln(1)) = 1 · (−x) = −x
```
Two nodes. Exact. But it uses EXL, DEML and the constant 0, not the operator being classified,
so it shows nothing about what any one operator can build.

The intended mechanism: **exp(+x) grows without bound as x → +∞**. This unbounded upward growth,
combined with ln (which maps ℝ⁺ → ℝ), gives the operator the full real line as output range.
The hoped-for chain: from full range comes identity; from identity comes negation; from negation comes completeness
(Ritt's theorem). Over ℝ it breaks at EAL: every real EAL tree T = exp(A) + ln(B) has
T′ = A′e^A + B′/B ≥ 0, so no EAL tree builds negation.

---

## Why exp(−x) Should Fail: The Reverse Direction (T27)

The exp(−x) operators each appear to fail by a different mechanism:

| Operator | Mechanism | Core barrier |
|---|---|---|
| **DEML** | Slope barrier | Self-composition always has slope +1; neg requires −1 |
| **DEMN** | Domain failure | deml(x,1) < 0 for all x; can't feed into ln |
| **DEAL** | Domain collapse | Achieves slope −1 but offset e⁻¹ is irremovable; deeper compositions lose domain |
| **DEXL** | Dead constant | dexl(x,1) = exp(−x)·ln(1) = 0 for all x |
| **DEDL** | Decay barrier | Self-composition gives −e⁻¹/x → 0; no linear growth |
| **DEPL** | Decay barrier | exp(−x)^(ln y) ≤ 1 for x ≥ 0; bounded above |

The unifying feature: **exp(−x) decays to 0 as x → +∞**. A decaying term cannot provide
unbounded growth in either direction. The only source of growth in h(exp(−x), ln(y)) is
the ln(y) branch — which grows logarithmically, not linearly. So slope ±1 is either
unreachable or achievable only with irremovable constant offsets.

**DEAL is the subtlest case.** It achieves slope −1 (DEAL(1, DEAL(x,1)) = e⁻¹ − x).
But the offset e⁻¹ cannot be removed: doing so requires neg (circular), and using
e⁻¹ − x as a right-branch input requires it to be positive, which restricts x < e⁻¹ ≈ 0.368.
The domain collapses at the second level of nesting.

---

## The Exception: LEX (T28)

LEX(x, y) = ln(exp(x) − y) has **exp(+x)**, yet it is conjectured to be incomplete.

The reason given was a domain restriction in the combining operation: ln(exp(x) − y) requires
exp(x) > y. With y = 1, this means x > 0. Nesting on the right, lex(1, lex(x, 1)) also needs
x < ln(e^e + 1) ≈ 2.782, and deeper right-nested trees settle on about (3.97×10⁻⁶, 2.782):
the domain does not approach the empty set under iteration.

Other LEX trees are defined on all of ℝ: lex(x, lex(lex(1,1),1)) = ln(e^x − ln(e − 2)) is defined
for every x, at depth 3. So the domain argument does not show incompleteness. The statement
this post gave for LEX (T28) was:

> *LEX is incomplete because its domain under self-composition collapses to a set of
> measure approaching 0 as depth increases.*

Its reason is false, and whether LEX is incomplete is an open conjecture. It was meant as a
different mechanism from exp(−x) incompleteness: failure at the domain level, not the growth level.

---

## The Bridge Case: EMN

EMN(x, y) = ln(y) − exp(x) has **−exp(x)** (negation outside, not inside).

The difference from exp(−x) is crucial:
- exp(−x) decays: bounded above, approaches 0
- −exp(x) grows without bound (negatively): → −∞ as x → +∞

This unbounded negative growth was meant to let EMN approximate any target to arbitrary precision (T24, a conjecture).
For approximate negation, the sketch used `emn(0, e^(e^k))`, which is e^k − 1 (not k − e^0 as first
written), and said variations get arbitrarily close to −x with error of order exp(−e^k). No such
family is written down; exhaustive search to 8 nodes finds neg(x) errors consistent with doubly-exponential decay.

The suggested obstruction to exact completeness: every EMN tree has an exp(·) residual in the
subtracted term that cannot be made exactly zero. Neither that nor approximate completeness
has a proof (T24).

---

## The Exponential Position Theorem

**Statement (a conjecture; T12 has no proof):**
An exp-ln operator's completeness class is determined entirely by the position
of negation relative to exp:

| Negation position | Growth type | Completeness class |
|---|---|---|
| exp(+x) (no negation, no domain restriction) | Unbounded upward | Exactly complete |
| −exp(x) (negation outside) | Unbounded downward | Approximately complete |
| exp(−x) (negation inside) | Bounded, decaying | Incomplete |
| exp(+x) with domain restriction | Restricted domain | Incomplete |

This is the updated T12 (was: Completeness Trichotomy with 1/1/6 split;
now: 8/1/7 split with structural explanation).

---

## What Changed from the Trichotomy

The [Completeness Trichotomy post](/blog/completeness-trichotomy) identified three classes
with 1 exactly complete operator (EML), 1 approximately complete (EMN), and 6 incomplete.
The full census proposes:
- **8 complete** operators, not 1 — EML would not be special in the dimension that matters
- **7 incomplete** operators, not 6 — LEX was added, though its domain mechanism is refuted (above)

The catalog count goes from T07 to T28 with this sprint. T12 became the Completeness
Characterization (Exponential Position Theorem), a conjecture citing T26 (forward), T27 (reverse),
and T28 (LEX domain).

---

## New Result: Softplus = 1 LEAd Node (T19)

The softplus activation function ln(1 + exp(x)) is exactly LEAd(x, 1):
```
LEAd(x, y) = ln(exp(x) + y)
LEAd(x, 1) = ln(exp(x) + 1) = softplus(x)
```

One node. The entire softplus function — ubiquitous in neural networks and smooth
approximations of ReLU — is a single LEAd application with constant 1.

Corollary: log-sum-exp of N terms costs N−1 LEAd nodes. The denominator of a
softmax over N logits: N−1 nodes.

---

*Monogate Research (2026). "Does exp(+x) Mean Complete? A Structural Conjecture for
Exponential-Logarithmic Operators." monogate research blog.
https://monogate.org/blog/completeness-characterization*

*Session COMP-1 through COMP-5 · T12 updated, T26–T28 added · Catalog count: 28*
