---
layout: ../../layouts/Base.astro
title: "Does tan(1) Control Everything?"
description: "A transcendence fact about tan(1) was offered as the root cause of three EML results, through a 'Depth Stability Theorem'. That theorem is withdrawn: sin has no real EML tree of any depth, but over ℂ it is one node. None of the three results uses tan(1)."
date: "2026-04-20"
author: "Monogate Research"
tag: conjecture
---

# Does tan(1) Control Everything?

<p style="color: var(--muted); font-style: italic;">Correction (2026-09-13): this post called its unification a theorem. T30's depth-3 ceiling is false: x + 1 has depth exactly 4, and ln x has depth exactly 3 on (0, ∞), not 1. T31's density argument never builds polynomials, and whether i is an accumulation point is open (C03). T29 rests on an exhaustive search over six operators with leaves x, y, 0, 1 on x, y > 0, and that search does not involve i. The sections below are corrected in place.</p>

<p style="color: var(--muted); font-style: italic;">Second correction (2026-09-13): this post was titled "Why tan(1) Controls Everything", and its unification ran through a Depth Stability Theorem: i ∉ EML_k exactly when every Atlas function has the same depth over ℂ as over ℝ. That theorem is withdrawn, and with it the five-way equivalence and the claim that the depth theory holds if and only if tan(1) is transcendental. sin has no real EML tree of any depth, but over ℂ it is the imaginary part of the one-node tree eml(ix, 1). T17's proof under strict real semantics does not use tan(1), and the argument from tan(1) under complex semantics does not work. The sections below say what each claim rests on.</p>

**Tier: CONJECTURE** (T17 is a theorem and T29 a proposition; T30 and T31 are conjectures. The unification through tan(1) is withdrawn: its Depth Stability step is false.)

---

This post traced three EML results that looked independent to one root cause: a single fact about a single number, $\tan(1)$ is transcendental. The fact is a theorem. The tracing does not hold up.

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

That one fact — $\tan(1) \notin \overline{\mathbb{Q}}$ — was offered as the root cause of
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

The harder question is whether $i$ is reachable under complex semantics, where $\ln$ accepts
negative inputs: $\ln(-r) = \ln r + i\pi$ for $r > 0$. This post argued that the transcendence of
$\tan(1)$ settles it. To build $i$ you need a tree value with imaginary part exactly 1; the imaginary
part of $e^{\alpha + i\beta}$ is $e^\alpha \sin\beta$; for $\beta = 1$ that forces $\cot(1)$ to be
EML-constructible; and $\cot(1)$ is transcendental.

The argument does not work, for two reasons:

- It tracks only the exponential. The imaginary part of $\mathrm{eml}(z, w) = e^z - \ln w$ is
  $e^{\mathrm{Re}\,z}\sin(\mathrm{Im}\,z) - \arg w$, so the logarithm moves it too.
- Being transcendental does not keep a number out of the EML values: $e = \mathrm{eml}(1, 1)$ is
  transcendental.

Under complex semantics, $i \notin \mathrm{EML}_k$ is argued on paper and has no proof.

**The nearest miss.** Among the values of depth 6 over the leaf 1 there is one with imaginary part
$0.99999524$, a gap of $4.76 \times 10^{-6}$ ([the depth-6 post](/blog/depth-6-phase-transition) prints
the search). Here $\tan(1)$ does appear. The value is $\mathrm{eml}(1, q)$ for a depth-5 value $q$
with imaginary part $-\pi$, and its imaginary part is $\operatorname{atan2}(\pi, \mathrm{Re}\,q)$. That
equals 1 exactly when $\mathrm{Re}\,q = \pi\cot(1) \approx 2.0171934$; the closest depth-5 $q$ has
$\mathrm{Re}\,q \approx 2.0172146$. A gap at depth 6 says nothing about deeper trees, and nothing shows
that no EML value equals $\pi\cot(1)$.

---

## Three results, one root cause?

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
| $\sin x$ | ∞ over ℝ | listed at 3, via Euler's formula $(e^{ix} - e^{-ix}) / 2i$, with no tree. Over ℝ no EML tree of any depth equals it, proved in Lean (MachLib, `sin_not_in_eml_any_depth_unconditional`); over ℂ it is the imaginary part of the one-node tree $\mathrm{eml}(ix, 1)$ |
| $\arctan x$ | ? | listed at 3, via $\frac{1}{2i}\ln\frac{1+ix}{1-ix}$, with no tree and no lower bound |

The hierarchy was also called strictly infinite, with the $k$-fold iterate $\exp^{(k)}$ at depth
exactly $k$. It has a $k$-node tree for every $k$, but exactly $k$ is settled only for $k \le 4$.
And a standard function does live above depth 3: $x + 1$.

The post asked why $\sin$ can't be collapsed to depth 2, and answered that the complex route
$\sin(x) = \mathrm{Im}(e^{ix})$ needs $i$ as a constructed constant, which $\tan(1)$ blocks. It called
this the **Depth Stability Theorem**: $i \notin \mathrm{EML}_k$ if and only if every EML-Atlas function
has the same depth over $\mathbb{C}$ as over $\mathbb{R}$.

That theorem is withdrawn. Its right-hand side is false for $\sin$, which has no real EML tree at any
depth but, over $\mathbb{C}$, is the imaginary part of the one-node tree $\mathrm{eml}(ix, 1)$ with $ix$
as the input. So the equivalence would make $i$ an EML value under complex semantics, the opposite of
what this post argues. Its proof fails at the step that turns a complex tree into an equally deep real
one, and $\sin$ is the counterexample there too. The complex route needs $ix$ as an input, not $i$ as a
constructed constant.

---

### Application 3 — Density paradox (T31, conjectured)

**T31** (a conjecture): The set of all EML tree values is **dense** in the space of holomorphic
functions on any compact simply-connected domain $K \subset \mathbb{C}$:
every function holomorphic near $K$ could be approximated to any precision by some finite EML tree.
The argument for it never builds polynomials, so the claim is open.

And yet $i$ is not known to be reached exactly.

Is this a contradiction? No. Density and exact membership are different things.

The rational numbers $\mathbb{Q}$ are dense in $\mathbb{R}$, but $\sqrt{2} \notin \mathbb{Q}$.
EML values would be dense in holomorphic function space, yet $i \notin \mathrm{EML}_k$.

The post explained both sides by $\tan(1)$: constructible pairs $(\alpha, \beta)$ could satisfy
$e^\alpha \sin\beta = 1$ ever more nearly, while transcendence would stop them from satisfying it
exactly at any finite depth. Neither half is shown. The first is the density claim itself, which is
open. The second is the complex-semantics argument above, which does not work.

Whether $i$ is an accumulation point of $\mathrm{EML}_1$ is open (C03); depth 6 gets within
$4.76 \times 10^{-6}$. Whether it is an element of $\mathrm{EML}_k$ under complex semantics is argued on
paper, with no proof. The two would coexist without contradiction.

---

## The five-way equivalence (withdrawn)

The post claimed that these five conditions all hold together or all fail together:

| # | Condition | Status |
|---|---|---|
| (1) | $\tan(1) \notin \overline{\mathbb{Q}}$ (Lindemann–Weierstrass) | **Theorem (proven 1882)** |
| (2) | $i \notin \mathrm{EML}_k$ for all $k$ (T17) | Does not use (1). Lean-verified for real semantics, where every value is real; under complex semantics, argued on paper with no proof |
| (3) | $\mathrm{depth}_\mathbb{C}(f) = \mathrm{depth}_\mathbb{R}(f)$ for all Atlas functions | False: $\sin$ has no real EML tree, and a one-node complex one |
| (4) | $\mathrm{depth}(\arctan) = \mathrm{depth}(\arcsin) = \mathrm{depth}(\arccos) = 3$ | No tree and no lower bound is given for any of the three |
| (5) | Every EML-Atlas function has a stable, well-defined depth stratum | Not a precise statement; read as "no depth drops over ℂ", it is (3) |

(1) is a theorem and (3) is false, so the five are not equivalent. The post also said **(5) implies (1)**. That holds only because (1) is a theorem, and the argument given for it went through the Depth Stability Theorem. The claim that the EML depth theory holds if and only if $\tan(1)$ is transcendental is withdrawn.

The depth results that are proved in Lean, that $\ln x$ has depth exactly 3 and $x + 1$ depth exactly 4 on $(0, \infty)$ and that $\sin$ has no real EML tree, concern real trees, and their proofs do not use $\tan(1)$.

---

## What if Lindemann–Weierstrass failed?

The post supposed that $\tan(1)$ were algebraic and listed what would collapse: $i$ constructible from
$\{0, 1\}$, $\sin(x)$ at depth 2, $\arctan$ below depth 3, multiplication in $\mathcal{F}_6$ in 2 nodes,
and every lower bound in the EML Atlas depth table at once, "a single house of cards resting on one
transcendence fact".

None of that follows. $\tan(1)$ is transcendental, so the supposition is false and settles nothing
about EML trees. Under strict real semantics $i$ is not an EML value whatever $\tan(1)$ is. The
$\mathcal{F}_6$ multiplication bound is a finite search that never uses $i$. The real depth lower bounds
do not mention $\tan(1)$.

---

## Summary

What each claim rests on:

- $\tan(1) \notin \overline{\mathbb{Q}}$: Lindemann–Weierstrass (1882).
- $i \notin \mathrm{EML}_k$ (T17, Lean-verified for real semantics): every strict real value is real,
  and $i$ is not. Under complex semantics it is argued on paper.
- T29, $xy$ needs at least 3 nodes in $\mathcal{F}_6$ (leaves $x, y, 0, 1$, on $x, y > 0$): an
  exhaustive search.
- T30, standard functions have depth at most 3: false ($x + 1$).
- T31, EML trees dense in $H(K)$: open, and so is whether $i$ is a limit point (C03).
- The Depth Stability Theorem and the five-way equivalence: withdrawn.

None of the four results is derived from $\tan(1)$. It enters only the near miss, as the target
$\pi\cot(1)$.

---

*Monogate Research (2026). "Does tan(1) Control Everything?" (first published as "Why tan(1) Controls Everything").
monogate research blog. https://monogate.org/blog/tan1-obstruction*

*Paper: `python/paper/Unifying_Obstruction_Tan1.tex`, whose Depth Stability Theorem and Five-Way Equivalence are withdrawn above · Sessions S93–S99 + Unified synthesis*

*Reproduce the near miss's arithmetic:*
```python
pip install mpmath
python -c "
import mpmath as mp
mp.mp.dps = 30
q = mp.mpf('2.01721457679406991430741964108')  # Re of the closest depth-5 value with Im = -pi
print('pi*cot(1)      =', mp.pi / mp.tan(1))
print('Im eml(1, q-pi*i) =', mp.im(mp.e - mp.log(mp.mpc(q, -mp.pi))))
"
```
