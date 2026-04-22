---
layout: ../../layouts/Base.astro
title: "What If tan(1) Were Constructible?"
description: "A thought experiment: if tan(1) could be built from EML trees, what would follow? The conditional chain connects to Schanuel's conjecture and would collapse the depth hierarchy."
date: "2026-04-20"
author: "Monogate Research"
tag: conjecture
---

# What If tan(1) Were Constructible?

**Tier: CONJECTURE** — everything below the horizontal rule in Section 1 is conditional. The only unconditional result is at the end: *tan(1) is not constructible*, proved by contrapositive from T18.

---

## The EML Grammar in One Line

The EML operator is `eml(x, y) = exp(x) − ln(y)`. A depth-1 EML tree applies this once to terminals from `{0, 1}`. A depth-2 tree nests two such applications. The EML Atlas assigns a depth to each standard mathematical function: how many EML nodes does the smallest tree that computes it require?

The question at the center of this post: can `tan(1)` — the tangent of one radian — be produced by a depth-1 tree?

Spoiler: no. But tracing *why not* reveals a surprisingly deep chain.

---

## What tan(1) Actually Is

From Lindemann–Weierstrass (1882), the number $e^i = \cos(1) + i\sin(1)$ is transcendental. That means $\cos(1)$ and $\sin(1)$ are not roots of any polynomial with rational coefficients. Their ratio $\tan(1) = \sin(1)/\cos(1)$ is therefore transcendental over $\mathbb{Q}$.

A depth-1 EML tree with terminals `{0,1}` can only return values like $e^1 - \ln(1) = e - 0 = e$, or $e^0 - \ln(1) = 1$, or combinations of these. None of these equal $\tan(1)$. This is already enough to rule it out — but we can say something stronger.

---

## The Conditional Chain: If tan(1) ∈ EML₁, Then...

Suppose, hypothetically, that some depth-1 EML tree produced $\tan(1)$.

**Step A: sin(1) and cos(1) would be EML-constructible.**

From $\tan(1)$, you can recover $\cos(1)$ via the identity $\cos^2(1) = 1/(1 + \tan^2(1))$, and then $\sin(1) = \tan(1) \cdot \cos(1)$. These are algebraic operations on $\tan(1)$. If $\tan(1)$ is depth-1 EML, then $\sin(1)$ and $\cos(1)$ become EML-constructible at bounded depth.

**Step B: i would be EML-constructible.**

Once you have $\cos(1)$ and $\sin(1)$, you have $e^i = \cos(1) + i\sin(1)$. Taking the complex logarithm: $\ln(e^i) = i$. Under the complex EML grammar (the Euler gateway), this means $i$ would be reachable from a bounded-depth EML tree.

But that directly contradicts **T18** — the proved, Lean-verified theorem that $i \notin \mathrm{EML}_1$. This is the wall.

**Step C: The depth hierarchy would collapse.**

By the **Depth Stability Theorem** (DST), $i \notin \mathrm{EML}_1$ is equivalent to the statement that every EML Atlas function has the same depth in the real and complex grammar. If $i$ became constructible, this equivalence would break simultaneously for every Atlas function.

Concretely: $\arctan(x)$ currently sits at depth 3 in the EML Atlas. Since $\arctan(1) = \pi/4$, and $\pi/4$ would become constructible once $i$ is accessible, $\arctan$ could potentially drop to depth 2. The clean depth-3 ceiling on all standard functions would no longer hold.

**Step D: $\pi$ would be EML-constructible.**

$\pi/2 = \arcsin(1)$. If $\arcsin$ (at depth 3 in the Atlas) is applied to the terminal value 1, we get $\pi/2$, and hence $\pi$. The transcendence of $\pi$ would then need to be reconciled with its constructibility — a contradiction under standard transcendence theory.

---

## The Contrapositive: An Actual Theorem

The conditional chain has the form:

> $\tan(1) \in \mathrm{EML}_1 \;\Rightarrow\; i \in \mathrm{EML}_1$

Theorem T18 says $i \notin \mathrm{EML}_1$. Contrapositive:

> $i \notin \mathrm{EML}_1 \;\Rightarrow\; \tan(1) \notin \mathrm{EML}_1$

**This is DOOR-4: $\tan(1) \notin \mathrm{EML}_1$.** A real theorem, not a conjecture.

The Lindemann–Weierstrass route gives the same answer (transcendence is already a barrier), but the T18 contrapositive is structurally cleaner: it shows that the obstruction to $\tan(1)$ is the same obstruction that excludes $i$ — a fundamental property of the real-valued EML grammar.

---

## The Schanuel Angle

Schanuel's conjecture is one of the major open problems in transcendence theory. It states: if $z_1, \ldots, z_n$ are $\mathbb{Q}$-linearly independent, then the transcendence degree of $\{z_1, \ldots, z_n, e^{z_1}, \ldots, e^{z_n}\}$ over $\mathbb{Q}$ is at least $n$.

Take $z_1 = 1$, $z_2 = i$. These are $\mathbb{Q}$-linearly independent (one is real, one is not). Schanuel would then give:

$$\mathrm{trdeg}_{\mathbb{Q}}\bigl(e,\ \cos(1),\ \sin(1)\bigr) \;\geq\; 2.$$

In plain terms: $\{e, \cos(1), \sin(1)\}$ contains at least two algebraically independent numbers. This implies that $\tan(1) = \sin(1)/\cos(1)$ does not lie in any algebraic extension of $\mathbb{Q}(e)$ — a strictly stronger statement than mere transcendence over $\mathbb{Q}$.

Schanuel is not proved. But conditionally, it says the barrier to $\tan(1)$ being constructible is not just transcendence — it is independence from the entire tower above $e$.

---

## Why Five Things Would Break at Once

The five-way equivalence at the heart of the monogate capstone paper says these five properties all hold or all fail together:

1. The EML grammar is complete (every function is expressible)
2. The Depth Stability Theorem holds
3. $i \notin \mathrm{EML}_1$ (T18)
4. The depth-3 ceiling on standard functions holds
5. Lindemann–Weierstrass provides valid transcendence obstructions

If $\tan(1) \in \mathrm{EML}_1$, then item 3 fails (by the chain above), and therefore all five fail simultaneously. The depth hierarchy, the completeness proof, and the transcendence machinery would all need to be rebuilt.

This is what makes the question interesting as a thought experiment: $\tan(1)$ is not a marginal case. It is load-bearing.

---

## What This Is and Is Not

This post is a **conditional analysis**, not a new theorem (except for the contrapositive at the end, which is DOOR-4 and is proved).

The conditionals — Steps A through D — are informal logical derivations. Step B in particular (recovering $i$ from $\cos(1)$ and $\sin(1)$ via the complex EML grammar) has not been formalised in Lean. Formalising it would require a definition of complex EML depth, an algebraic closure lemma for EML-reachable values, and a depth-transfer argument from complex to real semantics.

The Schanuel connection is doubly conditional: it requires both Hypothesis H (which is false) and Schanuel's conjecture (which is open).

The one thing that is not conditional: $\tan(1) \notin \mathrm{EML}_1$. That is DOOR-4, and it holds.

---

*Technical reference: `python/paper/theorems/DOOR4_Conditional_Tan1.tex`*
