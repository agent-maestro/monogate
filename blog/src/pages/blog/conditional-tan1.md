---
layout: ../../layouts/Base.astro
title: "What If tan(1) Were Constructible?"
description: "A thought experiment: if tan(1) could be built from EML trees, what would follow? The conditional chain connects to Schanuel's conjecture. The collapse of the depth hierarchy it once predicted rested on a Depth Stability Theorem that is withdrawn."
date: "2026-04-20"
author: "Monogate Research"
tag: conjecture
---

# What If tan(1) Were Constructible?

<p style="color: var(--muted); font-style: italic;">Correction (2026-09-13): Step C leaned on a Depth Stability Theorem that is withdrawn (sin has no real EML tree of any depth, but over ℂ it is one node), Step D treated transcendence as a bar to being an EML value (e is both), and the five-way equivalence near the end is withdrawn. Those sections are corrected in place.</p>

**Tier: CONJECTURE** — everything below the horizontal rule in Section 1 is conditional. The contrapositive at the end, *tan(1) is not constructible* (DOOR-4), does not assume the hypothesis, but it is only as strong as the Steps A and B it reverses: argued on paper, with no Lean proof.

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

But that directly contradicts **T17**: $i \notin \mathrm{EML}_1$. This is the wall. (T17 is Lean-verified only under strict real semantics. The complex-semantics form this step needs is argued on paper; see [Does tan(1) Control Everything?](/blog/tan1-obstruction).)

**Step C: The depth hierarchy would collapse.**

This step leaned on the **Depth Stability Theorem** (DST): that $i \notin \mathrm{EML}_1$ is equivalent to every EML Atlas function having the same depth in the real and complex grammar. The DST is withdrawn. $\sin$ has no real EML tree at any depth, yet over $\mathbb{C}$ it is the imaginary part of the one-node tree $\mathrm{eml}(ix, 1)$, so its two depths differ whatever happens to $i$. Nothing collapses through the DST.

The step also said that $\arctan(x)$ sits at depth 3 in the EML Atlas and could drop to depth 2 once $\pi/4$ became constructible, ending the depth-3 ceiling on standard functions. No tree backs $\arctan$ at depth 3, and that ceiling is false already: $x + 1$ has depth exactly 4.

**Step D: $\pi$ would be EML-constructible.**

$\pi/2 = \arcsin(1)$, so if $\arcsin$ were an EML tree, applying it to 1 would give $\pi/2$, and hence $\pi$. The post called that a contradiction with the transcendence of $\pi$. It is not one: transcendental numbers can be EML values, since $e = \mathrm{eml}(1, 1)$ is transcendental. This step shows nothing.

---

## The Contrapositive: An Actual Theorem

The conditional chain has the form:

> $\tan(1) \in \mathrm{EML}_1 \;\Rightarrow\; i \in \mathrm{EML}_1$

Theorem T17 says $i \notin \mathrm{EML}_1$. Contrapositive:

> $i \notin \mathrm{EML}_1 \;\Rightarrow\; \tan(1) \notin \mathrm{EML}_1$

**This is DOOR-4: $\tan(1) \notin \mathrm{EML}_1$.** It reverses Steps A and B, so it has their standing: argued on paper, with no Lean proof.

A direct check gives the same answer: the only depth-1 values over $\{0, 1\}$ are $1$ and $e$. Transcendence alone is no barrier, since $e$ is transcendental. The T17 contrapositive would tie the obstruction to $\tan(1)$ to the one that excludes $i$, but under complex semantics that link is only argued.

---

## The Schanuel Angle

Schanuel's conjecture is one of the major open problems in transcendence theory. It states: if $z_1, \ldots, z_n$ are $\mathbb{Q}$-linearly independent, then the transcendence degree of $\{z_1, \ldots, z_n, e^{z_1}, \ldots, e^{z_n}\}$ over $\mathbb{Q}$ is at least $n$.

Take $z_1 = 1$, $z_2 = i$. These are $\mathbb{Q}$-linearly independent (one is real, one is not). Schanuel would then give:

$$\mathrm{trdeg}_{\mathbb{Q}}\bigl(e,\ \cos(1),\ \sin(1)\bigr) \;\geq\; 2.$$

In plain terms: $\{e, \cos(1), \sin(1)\}$ contains at least two algebraically independent numbers. This implies that $\tan(1) = \sin(1)/\cos(1)$ does not lie in any algebraic extension of $\mathbb{Q}(e)$ — a strictly stronger statement than mere transcendence over $\mathbb{Q}$.

Schanuel is not proved. But conditionally, it says the barrier to $\tan(1)$ being constructible is not just transcendence — it is independence from the entire tower above $e$.

---

## Why Five Things Would Break at Once (withdrawn)

The five-way equivalence at the heart of the monogate capstone paper said these five properties all hold or all fail together:

1. The EML grammar is complete (every function is expressible)
2. The Depth Stability Theorem holds
3. $i \notin \mathrm{EML}_1$ (T17)
4. The depth-3 ceiling on standard functions holds
5. Lindemann–Weierstrass provides valid transcendence obstructions

That equivalence is withdrawn. Item 2 is false ($\sin$, above), item 4 is false ($x + 1$ has depth 4), and item 5 is a theorem, so the five do not hold or fail together. If $\tan(1)$ were in $\mathrm{EML}_1$, the chain above would still make item 3 fail under complex semantics, but nothing else on the list would follow.

The question is still a fair thought experiment. It is not load-bearing for the depth results, which concern real trees.

---

## What This Is and Is Not

This post is a **conditional analysis**, not a new theorem. The contrapositive at the end (DOOR-4) is no exception: it is argued on paper, and no Lean proof of it exists.

The conditionals — Steps A and B — are informal logical derivations; Steps C and D are withdrawn above. Step B in particular (recovering $i$ from $\cos(1)$ and $\sin(1)$ via the complex EML grammar) has not been formalised in Lean. Formalising it would require a definition of complex EML depth, an algebraic closure lemma for EML-reachable values, and a depth-transfer argument from complex to real semantics.

The Schanuel connection is doubly conditional: it requires both Hypothesis H (which is false) and Schanuel's conjecture (which is open).

The one statement here that does not assume Hypothesis H is DOOR-4, $\tan(1) \notin \mathrm{EML}_1$. It still rests on Steps A and B, so it stands where they do: argued on paper, with no Lean proof.

---

*Technical reference: `python/paper/theorems/DOOR4_Conditional_Tan1.tex`. Its Depth Stability Theorem and its π and depth-stability steps are corrected in the [errata](https://github.com/agent-maestro/monogate/blob/master/python/paper/ERRATA.md).*
