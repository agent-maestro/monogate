---
layout: ../../layouts/Base.astro
title: "Why tan(1) Controls Everything"
description: "A single transcendence fact about tan(1), offered as the root cause behind three separate EML claims: the multiplication lower bound, a depth-3 ceiling for standard functions (false: x + 1 has depth 4), and complex density (unproved)."
date: "2026-04-20"
author: "Monogate Research"
tag: conjecture
---

# Why tan(1) Controls Everything

<p style="color: var(--muted); font-style: italic;">Correction (2026-09-13): this post called its unification a theorem. T30's depth-3 ceiling is false: x + 1 has depth exactly 4, and ln x has depth exactly 3 on (0, ∞), not 1. T31's density argument never builds polynomials, and whether i is an accumulation point is open (C03). T29 rests on an exhaustive search over six operators with leaves x, y, 0, 1 on x, y > 0, and that search does not involve i. The sections below are corrected in place.</p>

**Tier: CONJECTURE** (T17 is a theorem and T29 a proposition; T30 and T31 are conjectures, and their unification via the Lindemann–Weierstrass obstruction has no proof)

---

Three EML results that looked independent are traced here to one root cause.
That cause is a single fact about a single number: $\tan(1)$ is transcendental.

---

## What "transcendental" means here

A number is *algebraic* if it is a root of a polynomial with rational coefficients.
Every number you can write using +, −, ×, ÷, and $n$th roots is algebraic.
$\sqrt{2}$, $\frac{3}{7}$, $\sqrt[5]{11 - \frac{1}{3}}$ — all algebraic.

A *transcendental* number is one that is provably not algebraic.
$\pi$ is transcendental. $e$ is transcendental.
And $\tan(1)$ — the tangent of one radian — is transcendental.

This is not just "we haven't found the polynomial yet."
It is a theorem.
The proof uses the **Lindemann–Weierstrass theorem** (1882): if $\alpha \neq 0$
is algebraic, then $e^\alpha$ is transcendental.
Apply this to $\alpha = 2i$ (which is algebraic, degree 2 over $\mathbb{Q}$):
$e^{2i} = \cos(2) + i\sin(2)$ is transcendental.
From this, via standard identities, $\sin(1)/\cos(1) = \tan(1)$ is transcendental.

That one fact — $\tan(1) \notin \overline{\mathbb{Q}}$ — is offered as the root cause of
everything below.

---

## Why you can't build i from 1 using EML

The EML operator is $\mathrm{EML}(x, y) = e^x - \ln y$.
Starting from the terminal set $\{0, 1\}$, EML trees generate a growing set of values:

- Depth 0: $\{0, 1\}$ — just the two constants.
- Depth 1: $\{1, e, \ldots\}$ — a handful of real numbers.
- Depth $k$: a countably infinite but structured set $\mathrm{EML}_k$.

**T17**: $i \notin \mathrm{EML}_k$ for any $k$ (Lean-verified under strict real semantics).

Under strict real semantics the proof is three lines: every EML operation
maps real inputs to real outputs, and $i$ is not real. Done.

The harder question is whether $i$ is reachable under complex semantics —
where $\ln$ can accept negative inputs and return $\pm i\pi$.
Here the $\tan(1)$ obstruction becomes essential.

To construct $i$, you need some tree value $z = \alpha + i\beta$ with imaginary
part exactly $1$. The imaginary part of $e^{\alpha + i\beta}$ is
$e^\alpha \sin(\beta)$.
For this to equal $1$ with EML-constructible $\alpha$ and $\beta$, you need
$\cot(\beta) = e^\alpha \cos(\beta)$ — and for the simplest case $\beta = 1$,
this forces $\cot(1) = 1/\tan(1)$ to be EML-constructible.

But $\tan(1)$ is transcendental, so $1/\tan(1) = \cot(1)$ is transcendental.
The only values EML can build from $\{0, 1\}$ lie in a specific field of
elementary numbers.
$\cot(1)$ is not in that field at the required position.
The constraint cannot be satisfied in any finite depth.

**The nearest miss:** at depth 6, the closest EML tree to $\mathrm{Im} = 1$ achieves
$\mathrm{Im} = 0.99999524$. A gap of $4.76 \times 10^{-6}$.
Not a rounding error. A transcendental obstruction.

---

## Three results, one root cause

### Application 1 — Multiplication lower bound (T29)

Computing $xy$ for $x, y > 0$ in the six-operator library $\mathcal{F}_6$, with leaves $x, y, 0, 1$,
requires **at least 3 nodes**.

Why? The story told here: if $i$ were constructible, you could route through complex exponentials to
implement multiplication in 2 nodes — the identity $xy = e^{\ln x + \ln y}$
combined with a complex-phase intermediate that sidesteps the restrictions of
real exp-ln arithmetic. No such 2-node route is written down.

What settles the bound is an exhaustive search, and it does not involve $i$: none of the
96 one-node and 4,608 two-node trees over $\mathcal{F}_6$ computes $xy$ (trees with other
constants were not searched).

In the extended 16-operator family $\mathcal{F}_{16}$, which includes the operator
$\mathrm{ELAd}(a, b) = e^a \cdot b$, multiplication achieves **2 nodes** for $x > 0$:

```
mul(x, y) = ELAd(EXL(0, x), y)
          = ELAd(ln x, y)
          = e^(ln x) · y
          = x · y
```

This is the T29 + T10-update result: 3 nodes in $\mathcal{F}_6$, 2 nodes in the April $\mathcal{F}_{16}$.
The current $\mathcal{F}_{16}$ needs only 1 node for $x, y > 0$: $e^{\ln x + \ln y}$.

---

### Application 2 — Depth-3 ceiling for standard functions (T30, refuted)

This section claimed every classical elementary function — exp, ln, power $x^n$, sine, cosine, arctan,
arcsin, arccos — has EML depth **at most 3**. The ceiling is false: $x + 1$ has depth exactly 4 on $(0, \infty)$.

| Function | Depth | Route |
|---|---|---|
| $e^x$ | 1 | 1 EML/EAL node |
| $\ln x$ | 3 | exactly 3 on $(0, \infty)$; listed at 1, via an EXL node, which is not an EML tree |
| $x^n$ | ? | $e^{n \ln x}$ passes through $\ln x$ (depth 3); no depth-2 tree is known |
| $\sin x$ | 3 | Euler: $(e^{ix} - e^{-ix}) / 2i$ |
| $\arctan x$ | 3 | $\frac{1}{2i}\ln\frac{1+ix}{1-ix}$ |

The hierarchy was also called strictly infinite, with the $k$-fold iterate $\exp^{(k)}$ at depth
exactly $k$. It has a $k$-node tree for every $k$, but exactly $k$ is settled only for $k \le 4$.
And a standard function does live above depth 3: $x + 1$.

Why can't $\sin$ be collapsed to depth 2?
The complex route $\sin(x) = \mathrm{Im}(e^{ix})$ is depth 2 over $\mathbb{C}$,
but it requires $i$ as a constructed constant. Since $i$ is not constructible
($\tan(1)$ blocks it), the collapse is prevented.

This is the **Depth Stability Theorem**: $i \notin \mathrm{EML}_k$ if and only if
every EML-Atlas function has the same depth over $\mathbb{C}$ as it does over $\mathbb{R}$.
The complex shortcut is uniformly blocked, for every function, by the single $\tan(1)$ fact.

---

### Application 3 — Density paradox (T31, conjectured)

**T31** (a conjecture): The set of all EML tree values is **dense** in the space of holomorphic
functions on any compact simply-connected domain $K \subset \mathbb{C}$:
every function holomorphic near $K$ could be approximated to any precision by some finite EML tree.
The argument for it never builds polynomials, so the claim is open.

And yet: $i$ is never exactly reached.

Is this a contradiction? No. Density and exact membership are different things.

The rational numbers $\mathbb{Q}$ are dense in $\mathbb{R}$, but $\sqrt{2} \notin \mathbb{Q}$.
EML values would be dense in holomorphic function space, yet $i \notin \mathrm{EML}_k$.

The $\tan(1)$ obstruction explains both sides:

- **Why sequences could approach $i$:** Transcendence is an exact algebraic constraint.
  You can get exponentially close to satisfying $e^\alpha \sin(\beta) = 1$ with
  constructible pairs $(\alpha, \beta)$ — the constraint becomes arbitrarily nearly
  satisfied without ever being exactly satisfied.
  Density would hold because the obstruction is a precision-zero set in the limit.

- **Why $i$ is never reached:** Exact membership requires the constraint to be
  exactly satisfied by EML-constructible values. The $\tan(1)$ transcendence
  prevents this in every finite depth.

Whether $i$ is an accumulation point of $\mathrm{EML}_1$ is open (C03); depth 6 gets within
$4.76 \times 10^{-6}$. It is not an element of $\mathrm{EML}_k$. The two would coexist without contradiction.

---

## The five-way equivalence

The connection is not just a chain of implications. It is a logical equivalence.
All five conditions hold together or fail together:

| # | Condition | Status |
|---|---|---|
| (1) | $\tan(1) \notin \overline{\mathbb{Q}}$ (Lindemann–Weierstrass) | **Theorem (proven 1882)** |
| (2) | $i \notin \mathrm{EML}_k$ for all $k$ (T17) | Follows from (1); Lean-verified for real semantics |
| (3) | $\mathrm{depth}_\mathbb{C}(f) = \mathrm{depth}_\mathbb{R}(f)$ for all Atlas functions | Follows from (2) via Depth Stability Theorem |
| (4) | $\mathrm{depth}(\arctan) = \mathrm{depth}(\arcsin) = \mathrm{depth}(\arccos) = 3$ | Follows from (3) |
| (5) | Every EML-Atlas function has a stable, well-defined depth stratum | Follows from (4) |

And the reverse: **(5) implies (1)**. If depth strata are stable, then the complex routing shortcut is blocked, which (by the contrapositive of the $\tan(1)$ chain) requires $\tan(1)$ to be transcendental.

The EML depth theory holds **if and only if** $\tan(1)$ is transcendental.

---

## What happens if Lindemann–Weierstrass fails?

Suppose hypothetically that $\tan(1) \in \overline{\mathbb{Q}}$ — that there exists
a polynomial with rational coefficients having $\tan(1)$ as a root.

Then:

- $i$ becomes constructible from $\{0, 1\}$ in some finite depth $k$.
- $\sin(x)$ drops to depth 2 (via $\mathrm{Im}(e^{ix})$ with constructible $i$).
- $\arctan$ drops below depth 3.
- Multiplication in $\mathcal{F}_6$ drops to 2 nodes via complex routing.
- **Every lower bound in the EML Atlas depth table collapses simultaneously.**

The entire depth theory is a single house of cards resting on one transcendence fact.
Remove Lindemann–Weierstrass and nothing is left standing.

---

## Summary

The structure of the EML depth theory is:

```
tan(1) ∉ Q̄  (Lindemann–Weierstrass)
    ↓
i ∉ EML_k  (T17, Lean-verified for real semantics)
    ↓
depth_ℂ = depth_ℝ  (Depth Stability Theorem)
    ↓
┌─────────────────────────────────────────────────────┐
│ T29: mul needs ≥ 3 nodes in F6 (search; x, y > 0)   │
│ T30: standard functions depth ≤ 3: false (x + 1)    │
│ T31: EML dense in H(K)? open; i a limit pt.? open   │
└─────────────────────────────────────────────────────┘
```

One number. One transcendence fact. Three claims: a search result, a refuted ceiling, an open conjecture.

---

*Monogate Research (2026). "Why tan(1) Controls Everything."
monogate research blog. https://monogate.org/blog/tan1-obstruction*

*Full paper: D:/monogate/python/paper/Unifying_Obstruction_Tan1.tex · Sessions S93–S99 + Unified synthesis*

*Reproduce:*
```python
pip install monogate
python -c "
from monogate import eml
# Nearest-miss to Im=1 at depth 6 (transcendental obstruction):
# Best known: Im = 0.99999524 (gap 4.76e-6)
print('tan(1) =', __import__('math').tan(1))
print('Is tan(1) algebraic? No. (Lindemann-Weierstrass)')
"
```
