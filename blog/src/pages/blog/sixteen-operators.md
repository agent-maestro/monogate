---
layout: ../../layouts/Base.astro
title: "16 Operators: The Complete exp-ln Census"
description: "Every binary combination of exp(±x) with ln(y) via arithmetic — completeness classification of all 16 operators."
date: 2026-04-20
---

# 16 Operators: The Complete exp-ln Census

<p style="color: var(--muted); font-style: italic;">Correction (2026-09-13): this post marked its completeness classification partly THEOREM-tier. Apart from EML's YES, the published universality result, no entry in the Complete? columns below has a proof, and over ℝ EAL's YES is false: every real EAL tree is nondecreasing, so none approximates −x. The rest is the conjectured 8/1/7 split (T12).</p>

**Tier: OBSERVATION** (computed) + **CONJECTURE** (completeness classification)

The EML family starts with one idea: combine exp(x) and ln(y) using arithmetic. There are exactly 16 natural binary combinations. This post classifies all of them.

---

## The 16 Operators

Every binary exp-ln operator has the form: combine exp(±x) with ln(y) using one of {−, +, ×, ÷, ^}.

**Subtraction family (EML, EMN, DEML, DEMN):**

| Operator | Formula | f(1,2) | Complete? |
|---------|---------|--------|-----------|
| EML | exp(x) − ln(y) | 2.025 | **YES** — T01 foundation |
| EMN | ln(y) − exp(x) | −2.025 | APPROXIMATE (conjectured) — T24 |
| DEML | exp(−x) − ln(y) | −0.325 | NO — T13 |
| DEMN | ln(y) − exp(−x) | 0.325 | NO |

**Addition family (EAL, DEAL):**

| Operator | Formula | f(1,2) | Complete? |
|---------|---------|--------|-----------|
| EAL | exp(x) + ln(y) | 3.411 | NO over ℝ (every real tree is nondecreasing); YES over ℂ conjectured — add(x,y)=3n |
| DEAL | exp(−x) + ln(y) | 1.061 | NO |

**Multiplication family (EXL, DEXL):**

| Operator | Formula | f(1,2) | Complete? |
|---------|---------|--------|-----------|
| EXL | exp(x) · ln(y) | 1.884 | **YES** (conjectured; the argument uses the constant e) — ln=1n, pow=3n |
| DEXL | exp(−x) · ln(y) | 0.255 | NO |

**Division family (EDL, DEDL):**

| Operator | Formula | f(1,2) | Complete? |
|---------|---------|--------|-----------|
| EDL | exp(x) / ln(y) | 3.922 | **YES** — div=1n |
| DEDL | exp(−x) / ln(y) | 0.531 | NO |

**Power family (EPL, DEPL):**

| Operator | Formula | f(1,2) | Complete? |
|---------|---------|--------|-----------|
| EPL | exp(x) ^ ln(y) | 2.000 | **YES** |
| DEPL | exp(−x) ^ ln(y) | 0.500 | NO |

**Reversed-argument family:**

| Operator | Formula | f(1,2) | Complete? |
|---------|---------|--------|-----------|
| LEX | ln(exp(x) − y) | −0.331 | NO — undefined when exp(x) ≤ y |
| LEAd | ln(exp(x) + y) | 1.551 | **YES** — softplus = 1 node |
| ELAd | exp(x + ln(y)) | 5.437 | **YES** — equals y·exp(x) |
| ELSb | exp(x − ln(y)) | 1.359 | **YES** — equals exp(x)/y |

---

## The Structural Insight

**8 complete, 1 approximate, 7 incomplete** — conjectured, over ℂ.

The conjectured pattern: **negating the exponent breaks completeness**.

All 6 operators with exp(−x) — DEML, DEMN, DEAL, DEXL, DEDL, DEPL — are classed incomplete. The only other operator classed incomplete is LEX. The reason given was that it is undefined on a non-negligible domain, but lex(x, lex(lex(1,1),1)) = ln(exp(x) − ln(e − 2)) is defined on all of ℝ (T28).

Why would exp(−x) break completeness? The range of exp(−x) is (0,∞) — identical to exp(x). But when negated, DEML(x,y) = exp(−x) − ln(y) is bounded above by exp(−x) for y ≥ 1, and exp(−x) *decreases* as x grows. This prevents DEML trees from growing large, limiting their ability to represent functions with unbounded output (like ln(x) itself).

---

## Softplus: The Hidden 1-Node Result

Among the reversed-argument operators, LEAd computes:

**LEAd(x, y) = ln(exp(x) + y)**

Setting y = 1: **ln(1 + exp(x)) = softplus(x)** in exactly 1 EML-family node.

Softplus is used throughout machine learning as a smooth approximation to ReLU. The fact that it costs 1 node (not 4-5 as commonly assumed) is a new result.

| Function | Expected cost | Actual EML cost |
|---------|--------------|----------------|
| ReLU(x) = max(x,0) | — | ∞ (not elementary) |
| Softplus(x) = ln(1+eˣ) | ~4n | **1n** via LEAd |
| Sigmoid(x) = 1/(1+e^{−x}) | ~4n | 2n (recip + DEML) |

---

## Reproduce

```bash
python python/scripts/research_new_operators.py
```

Results in `python/results/new_operators_results.json`.

---

**Cite:** Monogate Research (2026). "16 Operators: The Complete exp-ln Census." monogate research blog. https://monogate.org/blog/sixteen-operators
