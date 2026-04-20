---
layout: ../../layouts/Base.astro
title: "The Operator Zoo: Which exp-ln Gates Are Complete?"
date: 2026-04-19
tag: theorem
description: "We applied the DEML incompleteness template to seven exp-ln operators. Six are incomplete. One is open. One surprise: a gate with the identity function built in."
---

# The Operator Zoo: Which exp-ln Gates Are Complete?

The DEML incompleteness proof gave us a template. Apply it to every operator of the form f(exp(±x), ±ln(y)) and catalog the results. Seven operators. Five sessions. One surprise.

## The Operators

| Operator | Definition | Completeness class | Key Barrier |
|----------|-----------|-------------------|-------------|
| EML | exp(x) − ln(y) | **Exactly complete** | None |
| DEML | exp(−x) − ln(y) | **Incomplete** | All linear slopes +1, neg(x) impossible |
| EMN | ln(y) − exp(x) | **Approximately complete** | Nonzero exp(·) residual — exact ln(x) unreachable |
| EAL | exp(x) + ln(y) | **Incomplete** | All slopes positive, no cancellation |
| EXL | exp(x) · ln(y) | **Incomplete** | e not constructible from {1}, blocks exp(x) |
| EDL | exp(x) / ln(y) | **Incomplete** | Cannot build addition (proved separately) |
| POW | y^x | **Incomplete** | e not constructible; but see below |

Two new operators we explored:

- **POW(x,y) = y^x**: This equals exp(x·ln(y)). Remarkable fact: `pow(1, x) = x` — the identity function in a single node. But exp(x) still requires e as a leaf, and e is not constructible from `{1}` under POW.
- **LEX(x,y) = ln(exp(x)−y)**: At y = 0: `lex(x, 0) = x` — also the identity in one node. But 0 is not constructible from `{1}` under LEX.

## The DEML Template

The DEML proof established: find all "linear mechanisms" — compositions that produce linear functions of x. If all of them have the same sign on their slope, the operator cannot build neg(x) = −x, which blocks all arithmetic.

**DEML:** emn(1, emn(x,1)) → x + 1/e (slope +1). All paths give slope +1. Incomplete.

**EAL:** eal(1, eal(x,1)) = e + x (slope +1). eal(eal(1,x), 1) = e^e · x (slope e^e). All positive. Incomplete.

## The EMN Exception

EMN(x,y) = ln(y) − exp(x) = −EML(x,y).

The slope template produces a surprise. emn(emn(1,x), 1):

```
emn(1,x) = ln(x) − e
emn(ln(x)−e, 1) = ln(1) − exp(ln(x)−e) = −exp(−e)·x = −x/e^e
```

**Slope: −1/e^e ≈ −0.066.** Negative! The DEML template cannot prove EMN incomplete.

We ran an exhaustive search over N ≤ 7 trees. The best neg(x) approximation found uses 8 nodes and achieves error ~1.5 × 10⁻⁷ at x = 1.5, growing to ~2.6 × 10⁻⁵ at x = 10. The mechanism: complex intermediate values (via ln(−e) = 1 + iπ) construct an approximate ln(x), then `emn(ln(x), 1) = −x` exactly.

Is this an exact neg(x)? No — the "approximate ln" introduces exponentially small but nonzero error. Whether EMN is exactly complete remains open.

## The Two Incompleteness Mechanisms

The census reveals two distinct reasons a gate can be incomplete:

**Type A — Wrong slope sign:** All linear mechanisms have the same slope sign. DEML and EAL both fail this way. No finite composition can produce the opposite sign.

**Type B — Missing constant:** The constant e is not constructible from the gate applied to {1}. EXL and POW both fail here. Without e, you can't build exp(+x), and without that the operator cannot generate arbitrary elementary functions.

**EMN escapes both:** It has negative slopes (Type A doesn't apply) and it CAN build nonzero constants — emn(1,1) = −e in one node.

## The EMN Question — Answered

Is EMN complete? We now have a definitive answer: **approximately complete, not exactly complete.**

**EMN is not exactly complete:** No finite EMN tree can compute ln(x) exactly for all x. The obstruction is structural — every EMN output ln(R) − exp(L) has a nonzero exp(L) residual, and driving it to zero requires infinite depth (L → −∞). Proved by the growth rate argument (sessions EMN-1 through EMN-3).

**EMN is approximately complete:** For any elementary function f and ε > 0, there exists a finite EMN tree T such that |Re(T(x)) − f(x)| < ε on any compact interval. The mechanism: complex intermediate values (via ln(−e) = 1 + iπ) route around the sign barrier. Convergence is doubly-exponential in tree depth.

The three completeness classes form a clean trichotomy: **EML** (exactly complete), **EMN** (approximately complete), **all others** (incomplete). See the [Completeness Trichotomy](/blog/completeness-trichotomy) post for the full proof.

---

*Sessions Z1–Z9 · Direction 1 of the Research Roadmap*
