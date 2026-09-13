---
layout: ../../layouts/Base.astro
title: "General Addition in 2 Nodes: The Last Gap Closes"
description: "The only operation in SuperBEST costing more than 3 nodes was general-domain addition at 11n. It now costs 2 nodes, and a Lean lower bound shows no single F16 operator does it. (This post also called the table complete; it was not.)"
pubDate: "2026-04-20"
date: "2026-04-20"
tag: theorem
---

<p style="color: var(--muted); font-style: italic;">Correction (2026-09-13): this post called SuperBEST v5 the final, complete table, with no domain splits and "the work done". It was not: later constructions cut mul to 1 node for x, y &gt; 0 and pow and sqrt to 1 node for x &gt; 0, the positive-domain total, counted in F16, is 15n, and on general inputs mul costs 3n and div 8n, against 1n and 2n on positive ones (/superbest). The 2-node addition and its Lean lower bound (ADD-T1) stand.</p>

## The Last Outlier

Nine of the ten core operations in SuperBEST v4 cost at most 3 nodes. One didn't: general-domain addition — x+y for arbitrary real x including negatives — cost 11 nodes. It was the outlier. The embarrassment. The number we couldn't improve.

Until today.

## The Construction

```
add(x, y) = lediv(x, deml(y, 1))
```

Two operators. Two nodes. All real x, y.

**Node 1**: `deml(y, 1) = exp(-y) - ln(1) = exp(-y)`

Since ln(1) = 0, this is simply exp(-y). Always positive. Always defined.

**Node 2**: `lediv(x, exp(-y)) = ln(exp(x) / exp(-y))`

`= ln(exp(x) · exp(y))` — since 1/exp(-y) = exp(y)  
`= ln(exp(x+y))`  
`= x + y`

The proof is four lines of algebra. No domain restrictions anywhere: exp(-y) > 0 always, exp(x)/exp(-y) > 0 always.

## Why Did It Take This Long?

The positive-domain path (3 nodes) uses ln(x) as an intermediate step — which requires x > 0. Every prior attempt to extend addition to negative inputs hit the same wall: you need ln of something that might be zero or negative.

The breakthrough was routing through exp(-y) instead of ln(x). The DEML operator exp(-y) is always positive, so LEdiv's ln always has a valid input. We never touch ln(x) or ln(y) directly.

## Numerical Verification

```python
import math
deml = lambda x, y: math.exp(-x) - math.log(y)
lediv = lambda x, y: math.log(math.exp(x) / y)

def add_2n(x, y):
    return lediv(x, deml(y, 1))

# Test at mixed-sign and large inputs:
print([add_2n(a, b) - (a+b) for a, b in 
       [(-3, 5), (-1, -2), (0, 0), (3, -7), (-10, 4), (100, -200)]])
# → [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
```

Six zeros. The identity is exact algebra; the snippet only spot-checks it.

## The Updated Table

| Operation | v4 | v5 |
|-----------|----|----|
| exp, ln, recip, exp(−x) | 1n each | unchanged |
| div, neg, mul, sub, sqrt | 2n each | unchanged |
| add (positive domain) | 3n | → 2n (all reals) |
| add (general domain) | 11n | → 2n (all reals) |
| pow | 3n | unchanged |

Total: 19n → 18n. Savings: 74% → 75.3%.

More importantly: the two-tier system is gone. There is no longer a distinction between positive-domain and general-domain addition. One construction handles everything.

## Cascade Effects

Every equation that previously required add_gen = 11n now drops by 9 nodes per addition:

- ELO rating: 26n → 17n
- Nash equilibrium: 19n → 10n
- Henderson-Hasselbalch (general): 16n → 7n
- Black-Scholes Theta: improves substantially
- Quaternion rotation (general): 235n → substantially reduced

## Was the Table Complete?

This section called SuperBEST v5 the final table, with no outliers, no domain splits and the work done. It was not final (see the correction above), and domain splits remain: on general inputs mul costs 3n and div 8n, against 1n and 2n for positive ones.

*Proof: `python/paper/theorems/ADD_T1_General_Addition_2n.tex`. Its claim that the table is proved complete is withdrawn; see the [errata](https://github.com/agent-maestro/monogate/blob/master/python/paper/ERRATA.md).*

---

*Monogate Research (2026). "General Addition in 2 Nodes: The Last Gap Closes." monogate research blog.*
