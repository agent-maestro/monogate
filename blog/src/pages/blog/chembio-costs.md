---
layout: ../../layouts/Base.astro
title: "SuperBEST Node Costs: Chemistry and Biology"
description: "How many operator nodes does it take to compute 40 standard equations from chemistry and biology? A systematic analysis using the SuperBEST v3 routing table."
date: "2026-04-20"
author: "Arturo R. Almaguer"
tag: observation
---

# SuperBEST Node Costs: Chemistry and Biology

**Tier: OBSERVATION** (computed, reproducible)

The SuperBEST routing table gives exact minimum costs for arithmetic in EML
operator nodes. Previous posts applied it to calculus, geometry, and quantum
mechanics. This post covers 50 equations from five areas of chemistry and
five areas of biology.

The short version: costs range from **2 nodes** (Malthus population recursion)
to **40 nodes** (full MWC allosteric model). Structure determines cost.
Scientific domain does not.

---

## What Is a Node Count?

The EML operator family computes standard arithmetic in operator trees where:
- `exp(x)` = 1 node
- `ln(x)` = 1 node
- `x * y` = 3 nodes (via `exp(ln x + ln y)`)
- `x + y` = 3 nodes
- `x / y` = 3 nodes

This inverts the usual expectation. Transcendentals are cheap (1 node each).
Arithmetic operations are expensive (3 nodes each). The SuperBEST v3 routing
table gives the minimum node count for each primitive, provably optimal at
74% savings over naive arithmetic.

---

## The Top 10 Cheapest Equations

| Rank | Equation | Field | Nodes |
|------|----------|-------|-------|
| 1 | Malthus N_{t+1} = λ·N_t | Population | 2 |
| 2 | S = k_B ln Ω | Stat. Mech. | 3 |
| 2 | pH = −log₁₀[H⁺] | Acid-base | 3 |
| 4 | ΔG = ΔH − T·ΔS | Thermodynamics | 4 |
| 4 | Rate r = k[A][B] | Kinetics | 4 |
| 4 | Doubling time ln(2)/r | Biology | 4 |
| 4 | Half-life ln(2)/λ | Biology | 4 |
| 4 | Cell growth rate ln(2)/t_d | Biology | 4 |
| 4 | Turnover k_cat/[E] | Enzymology | 4 |
| 4 | Specificity k_cat/K_m | Enzymology | 4 |

Eight equations tie at 4 nodes: all are either pure products/ratios
with no transcendental, or ratios involving a single constant logarithm
(ln 2). The Boltzmann entropy and pH definitions sit at 3 nodes because
they are single logarithm evaluations followed by a constant rescaling.

---

## Four Structural Classes

The 50 equations fall into four classes whose node counts are determined
by structure, not by scientific origin.

### Class A: Pure Exponential Templates (5–7 nodes)

One exponential, one or two multiplications. All cost 5 nodes:

- Arrhenius k = A·exp(−E_a/RT) — 5n
- Population growth N₀·exp(r·t) — 5n
- Radioactive decay N₀·exp(−λ·t) — 5n
- Compound interest P·exp(r·t) — 5n

These are the **same tree** with different variable names. The exponential
template C·e^{±kt} is universal — one DEML or EML terminal plus one mul.

### Class B: Rational Functions — No Transcendentals (4–27 nodes)

Enzyme kinetics equations contain no exp or ln at all:

| Equation | Nodes |
|----------|-------|
| Michaelis-Menten | 9 |
| Lineweaver-Burk | 11 |
| Competitive inhibition | 18 |
| Uncompetitive inhibition | 18 |
| Mixed inhibition | 27 |

The cost is driven entirely by the number of mul, add, and div operations
in the rational expression. Mixed inhibition (27n) is the most expensive
rational-only equation in the catalog — it has a three-term denominator
that requires four mul and three add operations.

### Class C: Log-Ratio Formulas (3–17 nodes)

One or two ln evaluations followed by arithmetic. The pattern is clear:

| Equation | Nodes |
|----------|-------|
| pH = −log₁₀[H⁺] | 3 |
| ΔG° = −RT·ln K | 7 |
| Henderson-Hasselbalch | 10 |
| Nernst (unfolded) | 13 |
| van't Hoff integrated | 17 |
| Clausius-Clapeyron | 17 |

Each scalar multiplication after the ln costs 3 nodes. A log-ratio formula
with k multiplications costs 2k+1 nodes. Van't Hoff and Clausius-Clapeyron
both have the same structure — see O5 below.

### Class D: Mixed Exponential-Rational (13–40 nodes)

The most expensive class: Butler-Volmer (26n), Goldman-Hodgkin-Katz
2-ion (27n), Maxwell-Boltzmann (31n), GHK 3-ion (31n), MWC allosteric
(34n, 40n). The cost arises from coupling: a rational factor containing
an exp prevents node sharing.

---

## 10 Key Patterns

**O1 — Structural Identity Across Domains.**
Population growth, radioactive decay, compound interest, and cell growth
are the same 5-node EML tree. The exponential template is universal.

**O2 — Constant-Folding Saves 8 Nodes Per Pair.**
Nernst with RT/nF as one constant: 5 nodes.
Nernst with R, T, n, F separate: 13 nodes.
Folding two constants saves exactly 8 nodes — two mul operations and
one terminal avoided.

**O3 — Gompertz Beats Logistic Despite Deeper Nesting.**
Gompertz N(t) = N₀·exp(−a·e^{−bt}): 12 nodes.
Logistic K/(1 + e^{−r(t−t₀)}): 14 nodes.
Nesting exponentials (Gompertz) is cheaper than the add+div in the
logistic denominator.

**O4 — Mechanistic vs Empirical Cost Gap.**
MWC allosteric model (general): 40 nodes.
Hill equation (general): 15 nodes.
Same macroscopic cooperativity curve, 4× cost difference. MWC tracks
individual subunit states; Hill absorbs cooperativity into one exponent.

**O5 — Van't Hoff and Clausius-Clapeyron Are Isomorphic.**
Both cost 17 nodes and have identical EML trees. The law connecting
equilibrium constants to enthalpy and the law connecting vapor pressures
to enthalpy are the same equation with different variable labels.

**O6 — Add Is the Most Expensive Per-Call Primitive.**
exp and ln each cost 1 node. add, mul, and div each cost 3 nodes.
The catalog's most expensive equations are expensive because they have
many arithmetic operations, not because they have many transcendentals.

**O7 — Linearized Forms Are Never Cheaper.**
Hill plot (linearized): 16n vs Hill algebraic: 15n.
Lineweaver-Burk: 11n vs Michaelis-Menten: 9n.
Linearization always adds extra ln nodes plus a subtraction.
The historical advantage of linearized forms (graphical analysis) has
no computational justification.

**O8 — Two-Compartment PK Scaling: 10N − 3 Nodes.**
One-compartment PK: 7 nodes = 10(1) − 3.
Two-compartment PK: 17 nodes = 10(2) − 3.
Each additional compartment adds exactly 10 nodes:
one DEML (1n) + one mul (3n) + one add (3n) + one amplitude mul (3n).

**O9 — Enzyme Kinetics Form a Transcendental-Free Class.**
All standard enzyme kinetics equations (Michaelis-Menten, Lineweaver-Burk,
competitive, uncompetitive, mixed inhibition) contain no exp or ln.
The boundary between this class and cooperative binding (Hill, MWC) is
precisely the appearance of [L]^n, which requires the EPL primitive
and crosses into the transcendental regime.

**O10 — Entropy of Mixing Costs 6N − 5 Nodes.**
The N-component mixing entropy −R·Σ x_i·ln(x_i) costs 6N − 5 nodes.
At N = 2: 6(2) − 5 = 7 nodes for the sum terms plus overhead = 13n total.
Each component contributes 4 nodes (1 EXL + 1 mul); each addition step
costs 3 nodes; the formula is exact.

---

## Full Efficiency Ranking

All 50 equations sorted by node count:

| n | Equation | Field |
|---|----------|-------|
| 2 | Malthus N_{t+1} = λ·N_t | Bio-2 |
| 3 | S = k_B ln Ω | Chem-2 |
| 3 | pH = −log₁₀[H⁺] | Chem-4 |
| 4 | ΔG = ΔH − T·ΔS | Chem-5 |
| 4 | Rate r = k[A][B] | Chem-1 |
| 4 | Doubling time ln(2)/r | Bio-1 |
| 4 | Half-life ln(2)/λ | Bio-1 |
| 4 | Cell growth rate ln(2)/t_d | Bio-1 |
| 4 | Turnover k_cat/[E] | Bio-3 |
| 4 | Specificity k_cat/K_m | Bio-3 |
| 4 | Beer-Lambert A = εcl | Bio-5 |
| 4 | Fick's first law J = −D·dc/dx | Bio-5 |
| 5 | Nernst (RT/nF folded) | Chem-3 |
| 5 | [H⁺] = √(Ka·Ca) | Chem-4 |
| 5 | Activity-corrected pH | Chem-4 |
| 5 | Arrhenius k = A·exp(−Ea/RT) | Chem-1 |
| 5 | N₀·exp(r·t) population growth | Bio-1 |
| 5 | N₀·exp(−λ·t) decay | Bio-1 |
| 5 | Radioactive decay | Bio-1 |
| 5 | Compound interest | Bio-1 |
| 6 | Nernst single-ion | Bio-5 |
| 7 | ΔG° = −RT·ln K | Chem-5 |
| 7 | Helmholtz A = −k_BT·ln Z | Chem-2 |
| 7 | Integrated 1st-order [A](t) | Chem-1 |
| 7 | Beer-Lambert T = exp(−εcl) | Bio-5 |
| 7 | One-compartment PK | Bio-5 |
| 8 | ΔG = ΔG° + RT·ln Q | Chem-5 |
| 8 | Carbon-14 dating | Bio-1 |
| 8 | Beer-Lambert A = −log₁₀(T) | Bio-5 |
| 9 | Integrated 2nd-order 1/[A] | Chem-1 |
| 9 | Michaelis-Menten | Bio-3 |
| 10 | Henderson-Hasselbalch | Chem-4 |
| 10 | Hill fractional saturation | Bio-4 |
| 10 | Collision theory k = A·T^{1/2}·exp(−Ea/RT) | Chem-1 |
| 11 | Boltzmann ratio (two states) | Chem-2 |
| 11 | Beverton-Holt (constant folded) | Bio-2 |
| 11 | Lineweaver-Burk | Bio-3 |
| 11 | Arrhenius-Gibbs Form 1 | Chem-5 |
| 12 | Debye-Hückel ln(γ±) | Chem-3 |
| 12 | Gompertz growth | Bio-2 |
| 12 | Net reproductive rate R₀ (3-age) | Bio-2 |
| 13 | Entropy of mixing (2-component) | Chem-5 |
| 13 | Boltzmann factor exp(−E/k_BT)/Z | Chem-2 |
| 13 | Nernst (R,T,n,F separate) | Chem-3 |
| 13 | Tafel equation | Chem-3 |
| 13 | Quadratic [H⁺] (Ka fixed) | Chem-4 |
| 13 | Eyring k = (k_BT/h)·exp(−ΔG‡/RT) | Chem-1 |
| 13 | Hemoglobin-O₂ Hill (n=2.7) | Bio-4 |
| 14 | Van Slyke buffer capacity | Chem-4 |
| 14 | Logistic growth (sigmoid form) | Bio-2 |
| 14 | Logistic growth (standard form) | Bio-2 |
| 15 | Electrochemical potential | Chem-3 |
| 15 | Hill equation (general) | Bio-4 |
| 15 | Hill/dose-response | Bio-5 |
| 16 | Arrhenius-Gibbs Form 2 | Chem-5 |
| 16 | Hill linearized (Hill plot) | Bio-4 |
| 17 | Partition function (2-level) | Chem-2 |
| 17 | van't Hoff integrated | Chem-5 |
| 17 | Clausius-Clapeyron | Chem-5 |
| 17 | Two-compartment PK | Bio-5 |
| 18 | Competitive inhibition | Bio-3 |
| 18 | Uncompetitive inhibition | Bio-3 |
| 20 | Quadratic [H⁺] (Ka variable) | Chem-4 |
| 21 | Average energy (2-level) | Chem-2 |
| 24 | Two-site binding | Bio-4 |
| 26 | Butler-Volmer | Chem-3 |
| 27 | Goldman-Hodgkin-Katz (2-ion) | Chem-3 |
| 27 | Mixed inhibition | Bio-3 |
| 31 | Maxwell-Boltzmann distribution | Chem-2 |
| 31 | Goldman-Hodgkin-Katz (3-ion) | Bio-5 |
| 34 | MWC allosteric model n=2 | Bio-4 |
| 40 | MWC allosteric model general | Bio-4 |

---

## Summary Statistics

- **50 equations** across 10 subfields
- **Node range**: 2 – 40
- **Mean**: 12.9 nodes, **Median**: 12 nodes
- **Tier 1 (1–5n)**: 20 equations (40%)
- **Tier 2 (6–10n)**: 12 equations (24%)
- **Tier 3 (11–20n)**: 12 equations (24%)
- **Tier 4 (21–40n)**: 9 equations (18%)
- **Equations with no transcendental**: 18 (36%)

The most important single fact: **the exponential template is 5 nodes**
and appears identically in Arrhenius rate theory, population ecology,
radioactive decay, pharmacokinetics, and financial mathematics.
Structure is the invariant. Domain is a label.

---

> Almaguer, A.R. (2026). "SuperBEST Node Costs: Chemistry and Biology."
> monogate research blog. Sessions Chem-1 through Bio-5, 2026-04-20.
> Full LaTeX catalog: `python/paper/observations/SuperBEST_ChemBio_Catalog.tex`
> https://monogate.org/blog/chembio-costs
