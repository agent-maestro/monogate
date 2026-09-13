---
layout: ../../layouts/Base.astro
title: "We Found a Faster Multiplication: 3 Nodes"
date: 2026-04-19
tag: research
description: "The BEST router's mul entry drops to 3 nodes via exl(ln(x), exp(y)) = x·y. A search confirms 3 is the minimum over four operators (EML, EXL, EAL, EDL); with more operators multiplication takes 2 nodes, and 1 for x, y > 0."
---

# We Found a Faster Multiplication

<p style="color: var(--muted); font-style: italic;">Correction (2026-09-13): the 3-node lower bound holds only over EML, EXL, EAL and EDL with leaves {0, 1, x, y}; the re-run search is printed at the end. With ELAd, x·y = ELAd(EXL(0,x), y) is 2 nodes (T10u), and exp(ln x + ln y) is 1 node for x, y &gt; 0 (F16 on /framework; T_SUPERBEST_UB). EXL is not the only operator whose two arguments cancel: EAL(ln x, eʸ) = x + y and EDL(ln x, eʸ) = x/y do the same, and EML(ln x, eʸ) is x − y, not eˣ/y. The routing table's rows sum to 24 nodes, not the 25 printed.</p>

The BEST router had one obvious weakness: multiplication.

Every other routing entry was at 1–5 nodes. Mul was stuck at **7 nodes** via EDL.
The structural lower bound was 3. The gap was 4.

It's now closed — **exactly** at 3 nodes.

---

## The Old Construction — 7 Nodes via EDL

The EDL route computed mul(x, y) as div(x, recip(y)):

```
Node 1: edl(y, e)       = exp(y) / ln(e) = exp(y)
Node 2: edl(0, edl₁)   = exp(0) / ln(exp(y)) = 1 / y      [recip(y)]
...
Node 7: edl(ln(x), ...) = x / (1/y) = xy
```

The bottleneck: extracting ln(x) costs 3 nodes in EDL; recip costs 2 more.

---

## The Intermediate Result — 4 Nodes via EAL Bridge (MUL-10)

Sessions MUL-1 through MUL-10 discovered the EAL bridge identity:

```
eal(ln(a), exp(b)) = exp(ln(a)) + ln(exp(b)) = a + b
```

This led to a 4-node mixed construction:

```
Node 1: exl(0, x)          = ln(x)
Node 2: exl(0, ln(x))      = ln(ln(x))
Node 3: eal(ln(ln(x)), y)  = ln(x) + ln(y)
Node 4: eml(ln(x)+ln(y),1) = xy
```

A genuine improvement — 7n to 4n. But was 3n achievable?

---

## The Final Construction — 3 Nodes

EXL is defined as:

```
exl(A, B) = exp(A) · ln(B)
```

Feed it the right inputs:

```
exl(ln(x), exp(y)) = exp(ln(x)) · ln(exp(y)) = x · y
```

The encoding (ln) and decoding (exp) cancel in **both arguments simultaneously**. EXL does the combination and the decode in a single node.

**Full 3-node tree:**

```
Node 1: L = exl(0, x)    = ln(x)    [EXL; 0 is EXL's native constant exl(1,1)=0]
Node 2: E = eml(y, 1)    = exp(y)   [EML]
Node 3: R = exl(L, E)    = x · y    [EXL: exp(ln(x))·ln(exp(y)) = x·y]
```

**Proof:**

```
exl(ln(x), exp(y))
  = exp(ln(x)) · ln(exp(y))
  = x · y                    □
```

**Verification:**

| x | y | Result | Expected | Error |
|---|---|--------|----------|-------|
| 2 | 3 | 6.000000 | 6.000000 | 0 |
| 5 | 7 | 35.000000 | 35.000000 | < 10⁻¹⁴ |
| π | e | 8.539734 | 8.539734 | 0 |
| 0.5 | 4 | 2.000000 | 2.000000 | 0 |
| 3 | 0.1 | 0.300000 | 0.300000 | 0 |

All exact.

---

## The Lower Bound — 3n Among Four Operators

Can we do it in 2 nodes?

**Exhaustive N=2 search** over all mixed-operator trees (EML, EXL, EAL, EDL) with both strict leaves {1, x, y} and EXL-extended leaves {0, 1, x, y}: **no exact multiplication found.**

| N | Leaf set | Result |
|---|---------|--------|
| 2 | strict {1,x,y} | no exact mul |
| 2 | EXL-extended {0,1,x,y} | no exact mul |
| 3 | EXL-extended | **exact mul found** ← this construction |

**Conclusion:** among EML, EXL, EAL and EDL, the minimum multiplication tree has **3 nodes**. With more operators it is smaller (see the correction above).

---

## Why EXL and Not the Others?

EXL is the operator among these four whose double cancellation yields a product:

- `exl(A, B) = exp(A) · ln(B)`
- Left arg contribution: `exp(A)` — cancels a preceding `ln`
- Right arg contribution: `ln(B)` — cancels a preceding `exp`

When A = ln(x) and B = exp(y), both cancellations happen at once, yielding x · y in one node. The other three cancel the same way but combine differently: EAL gives x + y and EDL gives x/y.

EML (`exp(A) − ln(B)`) cancels left and right too — but the operation is subtraction, so the result is x − y, not x·y.

---

## The Bonus: Cheaper Addition (Unchanged at 3n)

The EAL bridge still gives addition in 3 nodes:

```
eal(exl(0, a), eml(b, 1)) = eal(ln(a), exp(b)) = a + b   [a > 0]
```

Both mul and add are now at 3 nodes. The BEST routing table is symmetric at the top.

---

## Updated BEST Routing Table

| Operation | Operator | Nodes | Status |
|-----------|---------|-------|--------|
| exp | EML | 1n | Proved optimal (one node is the minimum) |
| ln | EXL | 1n | Proved optimal (one node is the minimum) |
| div | EDL | 1n | **Wrong:** EDL(x,y) = eˣ/ln y is not x/y, and no single F16 node computes x/y for all real x, y (T_DIV_GEN_LB) |
| recip | ELSb | **1n** | **Proved optimal** (R16-C1; one node is the minimum, for x > 0) |
| pow | EXL | 3n | Best known |
| **add** | **Mixed(EXL/EML/EAL)** | **3n** (a>0) | **Improved from 11n** |
| **mul** | **Mixed(EXL/EML)** | **3n** | **Improved from 7n; lower bound TIGHT** |
| sub | EML | 5n | Best known |
| neg | EDL | 6n | Best known |

Total as first printed: 25 nodes across 9 operations (was 73 naive), **65.8% node reduction**; the rows above sum to 24. These are April counts; /superbest has the current table.

---

## Why This Matters

The old structural argument said mul needs 4 separate roles: extract x, extract y, combine, decode. That implied a 4-node lower bound.

The EXL construction shows the argument was wrong: combine and decode can happen **simultaneously**. The `exl` operator multiplies exp(left) by ln(right) — it extracts from both arguments and combines in one step.

This is the BEST router's core principle made explicit: optimal routing isn't about finding a better algorithm. It's about finding the operator whose native computation coincidentally matches the target, with the encoding and decoding folded in.

## Reproduce

Every tree with 1, 2 or 3 nodes over EML, EXL, EAL and EDL, with leaves {1, x, y} and with {0, 1, x, y}, checked against x·y at 12 random points in (0.3, 3)²:

```python
import itertools, numpy as np                          # pip install numpy
np.seterr(all='ignore')
rng = np.random.default_rng(1); X, Y = rng.uniform(0.3, 3.0, size=(2, 12))
ops = {'EML': lambda a, b: np.exp(a) - np.log(b), 'EXL': lambda a, b: np.exp(a) * np.log(b),
       'EAL': lambda a, b: np.exp(a) + np.log(b), 'EDL': lambda a, b: np.exp(a) / np.log(b)}
for leaves in (('1', 'x', 'y'), ('0', '1', 'x', 'y')):
    L = {'0': np.zeros(12), '1': np.ones(12), 'x': X, 'y': Y}
    trees = [[(l, L[l]) for l in leaves]]               # trees[n]: every tree with n nodes, no pruning
    for n in (1, 2, 3):
        trees.append([(f'{o}({ta},{tb})', f(a, b)) for i in range(n) for ta, a in trees[i]
                      for tb, b in trees[n - 1 - i] for o, f in ops.items()])
        exact = [t for t, v in trees[n] if np.all(np.isfinite(v)) and np.max(np.abs(v - X * Y)) < 1e-9]
        print(f'leaves {leaves}, {n} nodes: {len(trees[n])} trees, exact x*y: {exact}')
print('eml(ln x, e^y) - (x - y):', np.max(np.abs(np.exp(np.log(X)) - np.log(np.exp(Y)) - (X - Y))),
      ' eal(ln x, e^y) - (x + y):', np.max(np.abs(np.exp(np.log(X)) + np.log(np.exp(Y)) - (X + Y))),
      ' edl(ln x, e^y) - x/y:', np.max(np.abs(np.exp(np.log(X)) / np.log(np.exp(Y)) - X / Y)))
```

Output:

```
leaves ('1', 'x', 'y'), 1 nodes: 36 trees, exact x*y: []
leaves ('1', 'x', 'y'), 2 nodes: 864 trees, exact x*y: []
leaves ('1', 'x', 'y'), 3 nodes: 25920 trees, exact x*y: []
leaves ('0', '1', 'x', 'y'), 1 nodes: 64 trees, exact x*y: []
leaves ('0', '1', 'x', 'y'), 2 nodes: 2048 trees, exact x*y: []
leaves ('0', '1', 'x', 'y'), 3 nodes: 81920 trees, exact x*y: ['EXL(EXL(0,x),EML(y,1))', 'EXL(EXL(0,x),EAL(y,1))', 'EXL(EXL(0,y),EML(x,1))', 'EXL(EXL(0,y),EAL(x,1))']
eml(ln x, e^y) - (x - y): 0.0  eal(ln x, e^y) - (x + y): 0.0  edl(ln x, e^y) - x/y: 4.440892098500626e-16
```

---

*Sessions MUL-1 through MUL-11 · Directions 12 and 14 of the Research Roadmap*
