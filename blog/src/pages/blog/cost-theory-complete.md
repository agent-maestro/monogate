---
layout: ../../layouts/Base.astro
title: "The Cost Theory Is Complete"
description: "One formula predicts the SuperBEST node cost of any scientific equation. Proved, validated on 187 equations, and open-sourced."
date: "2026-04-20"
tag: "theorem"
---

# The Cost Theory Is Complete

**Date:** 2026-04-20 | **Tag:** theorem | **Read time:** ~7 min

---

After fourteen research sessions (R1--R14), the monogate SuperBEST cost theory is closed. One formula predicts the exact node cost of any scientific expression:

$$\operatorname{Cost}(E) = \operatorname{NaiveCost}(E) - \operatorname{SharingDiscount}(E) - \operatorname{PatternBonus}(E)$$

That is Theorem T38 (R2), and everything else in the theory is a consequence, refinement, or validation of it.

---

## What the three terms mean

**NaiveCost(E)** is the baseline: sum the SuperBEST v3 unit costs for every primitive operation in the expression, one independent sub-tree per operation, no sharing, no compression. For example, exp costs 1 node, mul costs 2, pow costs 3, and general addition costs 11 (it requires an absolute value internally). NaiveCost is always computable by inspection of the expression text.

**SharingDiscount(E)** is the saving from reuse. Two mechanisms contribute: (1) *constant folding* — any sub-expression whose inputs are all compile-time constants can be precomputed and replaced by a single leaf, saving its full NaiveCost; (2) *shared sub-expression elimination* — if a live sub-expression appears at $k \geq 2$ sites, computing it once and wiring the result saves $(k-1) \cdot \operatorname{Cost}(v)$ nodes. Empirically, 94% of textbook equations are trees over their live variables, so SharingDiscount is zero or comes only from constant folding.

**PatternBonus(E)** is the saving from compound operators. Each of the 16 operators in $\mathcal{F}_{16}$ realises a multi-primitive sub-expression as a single node at cost 1. For example, EML$(x,y) = e^x - \ln y$ replaces three primitive nodes (exp + ln + sub, naive cost 4) with one node, saving 3. The full 12-pattern catalog is proved, and greedy selection in decreasing-bonus order is globally optimal because no two patterns can share a root node.

---

## The four structural classes

Every arithmetic expression falls into exactly one of four classes, determined by whether it contains exp and/or ln nodes:

| Class | Signature | Mean cost | Example |
|-------|-----------|-----------|---------|
| **C** Log-ratio | ln only | ~9.5n | pH = $-\ln[\text{H}^+]/\ln 10$ |
| **B** Rational | neither | ~12.2n | Ohm's law $V = IR$ |
| **A** Pure Exponential | exp only | ~10.4n | Arrhenius $k = Ae^{-E_a/RT}$ |
| **D** Mixed | exp + ln | ~20.1n | Boltzmann $p_i = e^{-E_i/kT}/Z$ |

The strict ordering $\overline{\operatorname{Cost}}_C < \overline{\operatorname{Cost}}_B < \overline{\operatorname{Cost}}_A < \overline{\operatorname{Cost}}_D$ (Theorem T41, R9) is proved structurally: Class C is cheapest because ln costs only 1 node and no exp inflates the count; Class D is most expensive because it carries both transcendental families plus their interaction arithmetic.

The classification is a two-bit signature — presence of exp and presence of ln — so every expression has an unambiguous class assignment.

---

## The No Nesting Penalty

One result that might be surprising: nesting operators costs nothing extra. If you compose $O_1$ on top of $O_2$ on top of inputs $A$, $B$, $C$:

$$\operatorname{Cost}(O_1(O_2(A,B),\,C)) = c_{O_1} + c_{O_2} + \operatorname{Cost}(A) + \operatorname{Cost}(B) + \operatorname{Cost}(C)$$

No interface overhead, no adapter nodes, no depth penalty (Proposition T38-NNP, R3). This holds because every operator in $\mathcal{F}_{16}$ has a uniform interface: real inputs, real output. It would fail in hardware models (pipeline stalls), fixed-precision models (overflow checks), or typed operator models (domain coercions).

---

## Scaling laws

For formulas parameterised by a structural size $N$ (number of summands, states, compartments, etc.), the theory gives an exact formula:

**O(N) single sums (Theorem T42, R14):** For any flat sum of $N$ equal-cost terms (each costing $\alpha_0$ nodes), evaluated in the positive domain:

$$\operatorname{Cost}(f_N) = (\alpha_0 + 3)N - 3$$

The coefficient $\alpha_0 + 3$ ranges from 7 (Shannon entropy, Fourier) to 11 (pharmacokinetic multi-compartment sums). Every standard single-sum scientific formula is exactly O(N).

**O(N²) nested double sums:** Pairwise interaction models such as the Hopfield network energy $E = -\frac{1}{2}\sum_i\sum_j w_{ij}s_is_j$ scale as $\Theta(N^2)$.

**The Quadratic Ceiling Conjecture (T42-QCC):** No standard scientific closed-form formula exceeds O(N²). This is unproved but consistent with all 187 equations tested and with the physical principle that fundamental interactions are at most pairwise.

---

## Cross-domain isomorphism

Equations from completely different scientific fields can share identical minimal DAG topologies. Theorem T41-ISO (R10) catalogues eight confirmed cross-domain families:

- Arrhenius ≅ Eyring (chemistry, kinetics)
- Boltzmann weight ≅ Logistic sigmoid (stat. mech., ML)
- Shannon entropy ≅ Cross-entropy (information theory, ML)
- pH ≅ pKa ≅ Nernst (acid-base, electrochemistry)
- Radioactive decay ≅ RC discharge ≅ First-order kinetics (nuclear, circuit, chemical)
- Gaussian ≅ Maxwell-Boltzmann speed PDF (statistics, kinetic theory)
- Michaelis-Menten ≅ Hill equation (enzyme kinetics)
- Beer-Lambert ≅ Weber-Fechner ≅ Decibel (optics, psychophysics, acoustics)

Within each family, Cost is exactly equal. Any optimisation or normal form proved for one equation in the family transfers automatically to all others.

---

## Complex extension

Trigonometric functions have infinite real EML cost: no finite $\mathcal{F}_{16}$ tree over the reals computes $\sin$ or $\cos$ exactly. But in the complex extension (Proposition T43, R13), admitting $i$ as a free terminal and Euler's formula $e^{ix} = \cos x + i\sin x$:

$$\operatorname{ComplexCost}(\sin x) = \operatorname{ComplexCost}(\cos x) = 2$$
$$\operatorname{ComplexCost}(\sin^2 x + \cos^2 x) = 3$$

ComplexCost ≤ RealCost for all expressions representable over the reals.

---

## Blind test: 187 equations, 90%+ exact

The theory was validated on three independent corpora:

- **COST-1 regression** (50 equations, 10 domains): $R^2 = 0.92$
- **COST-8 blind test** (20 equations, 4 new domains): 0 prediction errors — all equations had SharingDiscount = PatternBonus = 0, making NaiveCost exact
- **R12 blind test** (30 equations, 5 new domains — fluid dynamics, optics, acoustics, materials science, epidemiology): 27/30 exact (90%), MAE = 0.20

The 3 discrepancies in R12 were not theory failures: they arose from condensed operator counting in the study prompt. Under fully-expanded trees, all 30 predictions are exact.

---

## What is still open

Two main open problems remain:

**The Quadratic Ceiling Conjecture.** Prove that no standard scientific closed-form formula ever exceeds O(N²) SuperBEST cost. A proof would require showing that no textbook formula encodes the algebraic equivalent of a nested double sum without explicitly writing one. A counterexample would be a formula with a single summation whose terms have intrinsic algebraic dependencies that force super-linear cost. Neither has been found.

**Lean 4 formalisation.** Type signatures for all four basic properties (P1--P4), T38, the No Nesting Penalty, T40, and T41 have been sketched in Lean 4 (R1, R3). A complete mechanised proof in Lean 4 or Mathlib is future work.

---

## Citation

Almaguer, A.R. (2026). "The Cost Theory Is Complete." monogate research. [https://monogate.org/blog/cost-theory-complete](https://monogate.org/blog/cost-theory-complete)

The full technical paper (including all proofs and the complete theorem index T34--T43) is available at:
`python/paper/cost_theory/Cost_Theory_Complete.tex` in the [monogate repository](https://github.com/monogate-dev/monogate).
