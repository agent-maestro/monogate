---
layout: ../../layouts/Base.astro
title: "The SuperBEST Table Is Complete"
description: "SuperBEST v1 (2026-04-20): 21 nodes, 71.2% savings vs naive. It called every entry optimal; later results improved on five entries and showed a sixth was wrong. The table now says what holds."
date: "2026-04-20"
author: "Monogate Research"
tags: ["EML", "SuperBEST", "optimality", "routing"]
---

# The SuperBEST Table Is Complete

> **Update 2026-04-20 (R16-C1):** This post documents SuperBEST v1 (21 nodes, 71.2%). Three subsequent results lowered the total further: T10u (mul: 3→2), T33 (sub: 3→2), and R16-C1 (recip: 2→1 via ELSb). SuperBEST v4 totalled **18 nodes, 75.3% savings** at that update. It has since been superseded; [/superbest](/superbest) carries the later table.

> **Correction 2026-09-12:** This post called every entry below optimal. Most were not. Its exhaustive searches covered six operators, not the whole F16 family, and later constructions beat recip, mul, sub, pow and add; its div entry was wrong from the start. The Optimality column now says what holds.

The SuperBEST routing table — the minimum-node dispatch table for arithmetic
operations over the exp-ln binary operator family — is now fully characterized.

This post claimed every entry was either proved optimal by exhaustive search, or bounded by
the best known cross-operator construction with no improvement found below it. Most were not
optimal; the Optimality column says what holds.

---

## The Complete Table

| Op | Nodes | Construction | Domain | Optimality |
|----|-------|-------------|--------|------------|
| exp(x) | 1 | eml(x,1) | all x | **PROVED** (one node is the minimum) |
| exp(−x) | 1 | deml(x,1) | all x | **PROVED** (one node is the minimum) |
| ln(x) | 1 | exl(0,x) | x>0 | **PROVED** (one node is the minimum) |
| div(x,y) | 1 | edl(x,y) | y≠0 | **Wrong.** edl(x,y) = eˣ/ln y is not x/y, and no single F16 node computes x/y for all real x, y (`SB_div_ge_two`, Lean-verified) |
| recip(x) | 2 | edl(0,eml(x,1)) | x≠0 | **Not optimal** for x>0: ELSb gives 1 node (R16-C1). The N=1 search covered six operators |
| neg(x) | 2 | exl(0,deml(x,1)) | all x | **Searched** (N=1 exhaustive, six operators): no 1-node construction |
| mul(x,y) | 3 | exl(exl(0,x),eml(y,1)) | x>0 | **Not optimal:** ELAd(EXL(0,x), y) is 2 nodes (T10u), and exp(ln x + ln y) is 1 node for x, y > 0 (`mul_one_node_positive`, Lean-verified) |
| sub(x,y) | 3 | eml(exl(0,x),eml(y,1)) | x>0 | **Not optimal:** LEdiv(x, EML(y,1)) is 2 nodes for all real x, y (T33), and 2 is the minimum (`SB_sub_ge_two`, Lean-verified) |
| pow(x,n) | 3 | eml(exl(ln(n),x),1) | x>0 | **Not optimal:** EPL(n,x) = exp(n·ln x) is 1 node (`rpow_one_node_positive`, Lean-verified) |
| add(x,y) | 3 | eal(exl(0,x),eml(y,1)) | x>0 | **Not optimal:** LEdiv(x, DEML(y,1)) is 2 nodes for all real x, y (ADD-T1), and 2 is the minimum (`SB_add_ge_two`, Lean-verified) |
| add(x,y) | 11 | EML-only | all x | **Not proved:** the best EML-only construction found, with no lower bound |

**Total (9 standard ops): 21 nodes** vs 73n naive = **71.2% savings**

Both the general real domain and the positive real domain converge to **21 nodes**.
The "two-tier" table has collapsed to a single tier for all operations except add.

---

## How Each Entry Was Argued

**1-node entries** (exp, exp(−x), ln, div): trivial lower bound. Any arithmetic
operation requires at least one operator gate. exp, exp(−x) and ln are achievable in one;
div is not, because edl(x,y) = eˣ/ln y is not x/y.

**2-node entries** (recip, neg): checked by N=1 exhaustive search. 6 operators ×
9 terminal combinations from {0, 1, x} = 54 cases per operation. Zero 1-node
constructions found. 2-node constructions exist → 2n exact minimum.

**3-node entries** (mul, sub, pow, add): checked by N=2 exhaustive search. All
two-node trees over {EML, DEML, EMN, EAL, EXL, EDL} and terminals {0, 1, x, y}
searched. Zero 2-node constructions found, so 3n was called exact. It was not: operators
outside these six (ELAd, LEdiv, EPL) reach 2 nodes or fewer.

**add (general domain, 11n)**: this said EML is the unique operator capable of general
addition and 11n the minimum for single-operator EML trees; neither was proved. No mixed
cross-operator construction below 11n was found at N≤5, but one exists: LEdiv(x, DEML(y,1)) = x + y
in 2 nodes for all real x, y (ADD-T1).

---

## The Key Identity That Closed neg

The breakthrough was `exl(0, deml(x, 1))`:

```
deml(x, 1) = exp(−x)                 [always > 0, no domain restriction]
exl(0, exp(−x)) = 1 · ln(exp(−x)) = −x  [exact, all x ∈ ℝ]
```

Prior to this, neg was thought to cost 4 nodes for general domain. The exhaustive
N=3 search (87,480 trees) found 6 constructions achieving neg in 3 nodes — all
variants of this core identity with 0 computed as an intermediate instead of free.
With 0 as a free constant, the construction collapses to 2 nodes.

---

## What This Means

**For expression optimization:** A compiler using SuperBEST routing achieves 71.2%
node reduction vs naive single-operator evaluation. For expressions containing
negation, the reduction is now identical whether or not inputs are restricted to
positive reals — the general construction is as efficient as the positive-domain one.

**For the theory:** The routing table is the most complete optimization result for
any universal operator family. No other framework has:
1. A single binary operator that generates all elementary functions, AND
2. A fully characterized minimum-cost dispatch table for that family

The addendum claimed:
- The 2n neg identity as a specific construction
- A positive-domain completeness theorem (all entries proved)
- A general-domain optimality theorem (all proved except add general)

Only the first held; the table shows where the other two fail.

---

## Journey to 71.2%

| Milestone | Gen total | Savings |
|-----------|-----------|---------|
| Naive single-op | 73n | 0% |
| BEST (pre-MUL-11) | 26n | 64.4% |
| SuperBEST (mul=3n, neg=4n) | 23n | 68.5% |
| **SuperBEST FINAL (neg=2n)** | **21n** | **71.2%** |

The final 2.7% improvement came from discovering that DEML — the "negative
exponent" operator, defined as exp(−A) − ln(B) — provides a domain-free path
to exp(−x), which EXL then converts to −x in one multiplication with ln.

The table was not complete; see the correction at the top.

---

> Monogate Research (2026). "The SuperBEST Table Is Complete."
> monogate research blog. Sessions N1–N10, 2026-04-20.
> https://monogate.org/blog/superbest-complete
