---
layout: ../../layouts/Base.astro
title: "Is the Cost Theory Complete?"
description: "One accounting identity for the SuperBEST node cost of a scientific equation. The decomposition (T38) is a definition, not a theorem; several results hold only as upper bounds, and the Quadratic Ceiling Conjecture and other problems are open. The predictions were checked on 100 validation equations."
date: "2026-04-20"
tag: "research"
---

# Is the Cost Theory Complete?

<p style="color: var(--muted); font-style: italic;">Correction (2026-09-13): this post called T38 a theorem that the rest of the theory follows from, and gave an exact O(N) law. T38 is a definition: the identity holds only because PatternBonus is defined as the remainder. The exact law is false (x₁ + x₂ costs 2, not 3), the No Nesting Penalty holds only as an upper bound, and the Lean files are type signatures with sorry. The sections below are corrected in place; the blind-test figures are reported as measured.</p>

<p style="color: var(--muted); font-style: italic;">Second correction (2026-09-13): this post was titled "The Cost Theory Is Complete". It is not: T38 is a definition, several results hold only as upper bounds, and the open problems below outnumber the two it listed. It also said equations in a cross-domain family cost exactly the same, which rests on minimal DAGs that nothing establishes, and it headed its validation "Blind test: 187 equations", though the blind tests total 50.</p>

**Date:** 2026-04-20 | **Tag:** research | **Read time:** ~7 min

---

After fourteen research sessions (R1--R14), the monogate SuperBEST cost theory is written up. One identity splits the node cost of any scientific expression into three terms:

$$\operatorname{Cost}(E) = \operatorname{NaiveCost}(E) - \operatorname{SharingDiscount}(E) - \operatorname{PatternBonus}(E)$$

That is T38 (R2). It holds only because PatternBonus is defined as the remainder, so it is a definition, not a theorem, and nothing else in the theory follows from it. With PatternBonus read off a fixed pattern catalogue it fails: $e^{x_1} + e^{x_2}$ has no shared sub-expression, matches no catalogued pattern and folds no constant, yet $\mathrm{EML}(\mathrm{LEAd}(x_2, \mathrm{EML}(x_1, 1)), 1)$ computes it in 3 nodes, below its NaiveCost.

---

## What the three terms mean

**NaiveCost(E)** is the baseline: sum the SuperBEST v3 unit costs for every primitive operation in the expression, one independent sub-tree per operation, no sharing, no compression. For example, exp costs 1 node, mul costs 2, pow costs 3, and general addition was priced at 11 (an April figure: $\mathrm{LEdiv}(x, \mathrm{DEML}(y, 1)) = x + y$ takes 2 nodes for all real $x, y$). NaiveCost is always computable by inspection of the expression text.

**SharingDiscount(E)** is the saving from reuse. Two mechanisms contribute: (1) *constant folding* — any sub-expression whose inputs are all compile-time constants can be precomputed and replaced by a single leaf, saving its full NaiveCost; (2) *shared sub-expression elimination* — if a live sub-expression appears at $k \geq 2$ sites, computing it once and wiring the result saves $(k-1) \cdot \operatorname{Cost}(v)$ nodes. Empirically, 94% of textbook equations are trees over their live variables, so SharingDiscount is zero or comes only from constant folding.

**PatternBonus(E)** is the saving from compound operators. Each of the 16 operators in $\mathcal{F}_{16}$ realises a multi-primitive sub-expression as a single node at cost 1. For example, EML$(x,y) = e^x - \ln y$ replaces three primitive nodes (exp + ln + sub, naive cost 4) with one node, saving 3. The catalog lists 12 such patterns; whether that list is complete is an open problem in the paper. Greedy selection in decreasing-bonus order is argued to be globally optimal, in a proof sketch that rests on no two patterns sharing a root node.

---

## The four structural classes

Every arithmetic expression falls into exactly one of four classes, determined by whether it contains exp and/or ln nodes:

| Class | Signature | Mean cost | Example |
|-------|-----------|-----------|---------|
| **C** Log-ratio | ln only | ~9.5n | pH = $-\ln[\text{H}^+]/\ln 10$ |
| **B** Rational | neither | ~12.2n | Ohm's law $V = IR$ |
| **A** Pure Exponential | exp only | ~10.4n | Arrhenius $k = Ae^{-E_a/RT}$ |
| **D** Mixed | exp + ln | ~20.1n | Boltzmann $p_i = e^{-E_i/kT}/Z$ |

Theorem T41 (R9) stated a strict ordering $\overline{\operatorname{Cost}}_C < \overline{\operatorname{Cost}}_B < \overline{\operatorname{Cost}}_A < \overline{\operatorname{Cost}}_D$ and argued for it structurally. The table's own means contradict it: they order as C < A < B < D (9.5n, 10.4n, 12.2n, 20.1n, from the paper's 50-equation COST-4 subset), so the ordering is not a theorem. The means do put Class C cheapest and Class D most expensive, which fits the structural reading: ln costs only 1 node, and Class D carries both transcendental families plus their interaction arithmetic.

The classification is a two-bit signature — presence of exp and presence of ln — so every expression has an unambiguous class assignment.

---

## The No Nesting Penalty

One result that might be surprising: nesting operators costs nothing extra. If you compose $O_1$ on top of $O_2$ on top of inputs $A$, $B$, $C$:

$$\operatorname{Cost}(O_1(O_2(A,B),\,C)) \le c_{O_1} + c_{O_2} + \operatorname{Cost}(A) + \operatorname{Cost}(B) + \operatorname{Cost}(C)$$

No interface overhead, no adapter nodes, no depth penalty (Proposition T38-NNP, R3). The bound holds because every operator in $\mathcal{F}_{16}$ has a uniform interface: real inputs, real output. Equality does not: a minimal DAG need not contain the sub-DAGs, and $\mathrm{LEdiv}(\mathrm{LEdiv}(x, 1), 1) = x$ costs 0, not 2. The bound would fail in hardware models (pipeline stalls), fixed-precision models (overflow checks), or typed operator models (domain coercions).

---

## Scaling laws

For formulas parameterised by a structural size $N$ (number of summands, states, compartments, etc.), the theory gives a count and an upper bound:

**O(N) single sums (R14's T42; T40 on /theorems):** Take a flat sum of $N$ terms, each of naive cost $\alpha_0$ (a valid upper bound, T34), joined by $N - 1$ additions. With the 2-node addition $\mathrm{LEdiv}(x, \mathrm{DEML}(y, 1)) = x + y$, valid for all real inputs:

$$\operatorname{Cost}(f_N) \le (\alpha_0 + 2)N - 2$$

This post stated $\operatorname{Cost}(f_N) = (\alpha_0 + 3)N - 3$ exactly, in the positive domain. That is false: $x_1 + x_2$ costs 2, not 3, and the softmax denominator $\sum_i e^{x_i}$ costs at most $2N - 1$ ($S_1 = \mathrm{EML}(x_1, 1)$, $S_{k+1} = \mathrm{EML}(\mathrm{LEAd}(x_{k+1}, S_k), 1)$). The coefficients it gave for $\alpha_0 + 3$, from 7 (Shannon entropy, Fourier) to 11 (pharmacokinetic multi-compartment sums), are April counts from that formula, upper-bound estimates at best. Every standard single-sum scientific formula with bounded per-term cost is O(N).

**O(N²) nested double sums:** Pairwise interaction models such as the Hopfield network energy $E = -\frac{1}{2}\sum_i\sum_j w_{ij}s_is_j$ scale as $\Theta(N^2)$.

**The Quadratic Ceiling Conjecture (T42-QCC):** No standard scientific closed-form formula exceeds O(N²). This is unproved but consistent with the 187 equations the paper counts (its 157-equation corpus plus the 30-equation R12 blind test), checked by hand in April, and with the physical principle that fundamental interactions are at most pairwise.

---

## Cross-domain isomorphism

Equations from completely different scientific fields can share the same tree shape. The paper's T41-ISO (R10), which it calls a theorem, names eight cross-domain families:

- Arrhenius ≅ Eyring (chemistry, kinetics)
- Boltzmann weight ≅ Logistic sigmoid (stat. mech., ML)
- Shannon entropy ≅ Cross-entropy (information theory, ML)
- pH ≅ pKa ≅ Nernst (acid-base, electrochemistry)
- Radioactive decay ≅ RC discharge ≅ First-order kinetics (nuclear, circuit, chemical)
- Gaussian ≅ Maxwell-Boltzmann speed PDF (statistics, kinetic theory)
- Michaelis-Menten ≅ Hill equation (enzyme kinetics)
- Beer-Lambert ≅ Weber-Fechner ≅ Decibel (optics, psychophysics, acoustics)

The paper defines a family by isomorphic *minimal* DAGs and concludes that within each family Cost is exactly equal. Nothing establishes that any of these DAGs is minimal: most node counts are constructions, which bound Cost from above, and lower bounds exist only for a few single operations. What a family shares is a construction, so its members cost at most the same number of nodes; equal cost is not shown. A construction found for one equation transfers to the others by relabelling leaves. A lower bound need not, since a leaf that is a constant in one equation can fold. /theorems lists these families as an observation (O-ISO), with a different list of eight.

---

## Complex extension

Trigonometric functions have infinite real cost: no finite real EML tree computes $\sin$ or $\cos$ exactly, proved in Lean by periodicity (MachLib), and the same is argued for mixed $\mathcal{F}_{16}$ trees, with no proof. But in the complex extension (Proposition T43, R13), admitting $i$ as a free terminal and Euler's formula $e^{ix} = \cos x + i\sin x$:

$$\operatorname{ComplexCost}(\sin x) \le 2, \qquad \operatorname{ComplexCost}(\cos x) \le 2$$
$$\operatorname{ComplexCost}(\sin^2 x + \cos^2 x) \le 3$$

These are upper bounds: the paper printed them as equalities but lists matching lower bounds for trigonometric expressions as open. As a function, $\sin^2 x + \cos^2 x$ is the constant 1, which needs no node; the 3 counts the expression as written.

ComplexCost ≤ RealCost for all expressions representable over the reals.

---

## Validation: 100 equations in three corpora

The theory was validated on three independent corpora:

- **COST-1 regression** (50 equations, 10 domains): $R^2 = 0.92$
- **COST-8 blind test** (20 equations, 4 new domains): 0 prediction errors — no equation had catalogued sharing or patterns, so each prediction was its NaiveCost
- **R12 blind test** (30 equations, 5 new domains — fluid dynamics, optics, acoustics, materials science, epidemiology): 27/30 exact (90%), MAE = 0.20

The 3 discrepancies in R12 were not theory failures: they arose from condensed operator counting in the study prompt. Under fully-expanded trees, all 30 predictions are exact.

The paper's cumulative figure of 187+ equations adds R12's 30 to its 157-equation corpus. That is the set the ceiling conjectures were checked against by hand, not a blind test.

---

## What is still open

The paper lists five open problems, and the corrections on this page add more. Among them:

**The Quadratic Ceiling Conjecture.** Prove that no standard scientific closed-form formula ever exceeds O(N²) SuperBEST cost. A proof would require showing that no textbook formula encodes the algebraic equivalent of a nested double sum without explicitly writing one. A counterexample would be a formula with a single summation whose terms have intrinsic algebraic dependencies that force super-linear cost. Neither has been found.

**Lean 4 formalisation.** R1 and R3 give Lean 4 type signatures, with `sorry` in place of every proof, for the four basic properties (P1--P4), T38, the No Nesting Penalty, T40, and T41. None of it is mechanised, and several of those statements are false as written (P2, the equality forms of the No Nesting Penalty and T40, the T41 ordering), so only corrected forms could be.

**Patterns.** Whether the 12-pattern catalogue is complete, and whether greedy pattern selection is optimal; the argument for greedy selection is a sketch that assumes no two patterns share a root node.

**Isomorphism families.** Whether the eight families are all there are, and whether members of a family really cost the same, since no family's minimal DAG is established.

**Lower bounds.** Matching lower bounds for complex cost, which the paper leaves open, and for most real costs: only sub, add, mul and div have lower bounds in Lean.

---

## Citation

Monogate Research (2026). "Is the Cost Theory Complete?" (first published as "The Cost Theory Is Complete"). monogate research. [https://monogate.org/blog/cost-theory-complete](https://monogate.org/blog/cost-theory-complete)

The full technical paper (including its proof arguments and the theorem index T34--T43; [/theorems](/theorems) says which of them hold) is available at:
`python/paper/cost_theory/Cost_Theory_Complete.tex` in the [monogate repository](https://github.com/monogate-dev/monogate).
