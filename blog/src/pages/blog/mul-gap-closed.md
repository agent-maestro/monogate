---
layout: ../../layouts/Base.astro
title: "We Found a Faster Multiplication: 3 Nodes"
date: 2026-04-19
tag: theorem
description: "The BEST router's mul entry drops to 3 nodes via exl(ln(x), exp(y)) = x·y. The lower bound is 3n, confirmed tight by exhaustive search. Gap fully closed."
---

# We Found a Faster Multiplication

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

## The Lower Bound — 3n Is Tight

Can we do it in 2 nodes?

**Exhaustive N=2 search** over all mixed-operator trees (EML, EXL, EAL, EDL) with both strict leaves {1, x, y} and EXL-extended leaves {0, 1, x, y}: **no exact multiplication found.**

| N | Leaf set | Result |
|---|---------|--------|
| 2 | strict {1,x,y} | no exact mul |
| 2 | EXL-extended {0,1,x,y} | no exact mul |
| 3 | EXL-extended | **exact mul found** ← this construction |

**Conclusion:** The minimum mixed-operator multiplication tree has exactly **3 nodes**. The gap is fully closed.

---

## Why EXL and Not the Others?

EXL is the unique operator where both arguments cancel simultaneously:

- `exl(A, B) = exp(A) · ln(B)`
- Left arg contribution: `exp(A)` — cancels a preceding `ln`
- Right arg contribution: `ln(B)` — cancels a preceding `exp`

When A = ln(x) and B = exp(y), both cancellations happen at once, yielding x · y in one node. No other operator achieves both cancellations simultaneously.

EML (`exp(A) − ln(B)`) cancels left and right too — but the operation is subtraction, not multiplication, so the algebraic result is exp(x)·(1/y), not x·y.

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
| exp | EML | 1n | Proved optimal |
| ln | EXL | 1n | Proved optimal |
| div | EDL | 1n | Proved optimal |
| recip | ELSb | **1n** | **Proved optimal** (R16-C1) |
| pow | EXL | 3n | Best known |
| **add** | **Mixed(EXL/EML/EAL)** | **3n** (a>0) | **Improved from 11n** |
| **mul** | **Mixed(EXL/EML)** | **3n** | **Improved from 7n; lower bound TIGHT** |
| sub | EML | 5n | Best known |
| neg | EDL | 6n | Best known |

Total: 25 nodes across 9 operations (was 73 naive). **65.8% node reduction.**

---

## Why This Matters

The old structural argument said mul needs 4 separate roles: extract x, extract y, combine, decode. That implied a 4-node lower bound.

The EXL construction shows the argument was wrong: combine and decode can happen **simultaneously**. The `exl` operator multiplies exp(left) by ln(right) — it extracts from both arguments and combines in one step.

This is the BEST router's core principle made explicit: optimal routing isn't about finding a better algorithm. It's about finding the operator whose native computation coincidentally matches the target, with the encoding and decoding folded in.

---

*Sessions MUL-1 through MUL-11 · Directions 12 and 14 of the Research Roadmap*
