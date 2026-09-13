---
layout: ../../layouts/Base.astro
title: "The Operator Zoo: Which exp-ln Gates Are Complete?"
date: 2026-04-19
tag: conjecture
description: "We applied the DEML incompleteness template to seven exp-ln operators. It suggests six are incomplete and leaves one open, but the template has a gap. One surprise: a gate with the identity function built in."
---

# The Operator Zoo: Which exp-ln Gates Are Complete?

<p style="color: var(--muted); font-style: italic;">Correction (2026-09-13): this post said the EMN question below has a definitive answer. It does not: that EMN is approximately but not exactly complete is a conjecture (T24), and the sketches for both halves stop short. The DEML template has a gap too (T13), so the Incomplete entries are conjectures, except that over ℝ no EAL tree approximates −x.</p>

<p style="color: var(--muted); font-style: italic;">Second correction (2026-09-13): the Type A paragraph said DEML fails the way EAL does, by slope sign. For DEML that argument has a gap: deml(x, 1) = exp(−x) has negative slope. EDL's "cannot build addition" is conjecture C1 of the preprint, not a result. And the later 16-operator census conjectures the opposite of this table for EXL, EDL and POW (which is EPL), and for EAL over ℂ: exactly complete (T26). Neither classification is proved.</p>

The DEML incompleteness argument gave us a template. Apply it to every operator of the form f(exp(±x), ±ln(y)) and catalog the results. Seven operators. Five sessions. One surprise.

## The Operators

| Operator | Definition | Completeness class | Key Barrier |
|----------|-----------|-------------------|-------------|
| EML | exp(x) − ln(y) | **Exactly complete** | None |
| DEML | exp(−x) − ln(y) | **Incomplete** (conjectured, T13) | Said: all linear slopes +1, so neg(x) is impossible; that argument has a gap |
| EMN | ln(y) − exp(x) | **Approximately complete** | Nonzero exp(·) residual — exact ln(x) unreachable |
| EAL | exp(x) + ln(y) | **Incomplete** over ℝ | All slopes positive, no cancellation (over ℝ; T26 conjectures EAL complete over ℂ) |
| EXL | exp(x) · ln(y) | **Incomplete** (April; T26 conjectures it complete over ℂ) | e not constructible from {1}, blocks exp(x) |
| EDL | exp(x) / ln(y) | **Incomplete** (April; T26 conjectures it complete over ℂ) | Cannot build addition: the preprint's conjecture C1, which it supports with a search to N ≤ 6 (not re-run) |
| POW | y^x | **Incomplete** (April; POW is EPL, which T26 conjectures complete over ℂ) | e not constructible; but see below |

Two new operators we explored:

- **POW(x,y) = y^x**: This equals exp(x·ln(y)). Remarkable fact: `pow(1, x) = x` — the identity function in a single node. But exp(x) still requires e as a leaf, and e is not constructible from `{1}` under POW.
- **LEX(x,y) = ln(exp(x)−y)**: At y = 0: `lex(x, 0) = x` — also the identity in one node. But 0 is not constructible from `{1}` under LEX.

## The DEML Template

The DEML argument proposed: find all "linear mechanisms" — compositions that produce linear functions of x. If all of them have the same sign on their slope, the operator cannot build neg(x) = −x, which blocks all arithmetic.

**DEML:** deml(1, deml(x,1)) → x + 1/e (slope +1). The argument says all paths give slope +1, but that step has a gap (T13). Conjectured incomplete.

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

**Type A — Wrong slope sign:** All linear mechanisms have the same slope sign, so no finite composition can produce the opposite sign. EAL fails this way over ℝ: every real EAL tree T = exp(A) + ln(B) has T′ = A′e^A + B′/B ≥ 0. DEML was counted here too, but deml(x, 1) = exp(−x) has negative slope, so for DEML the argument has a gap (T13).

**Type B — Missing constant:** The constant e is not constructible from the gate applied to {1}. EXL and POW both fail here. Without e, you can't build exp(+x), and without that the operator cannot generate arbitrary elementary functions. (The later census conjectures both complete over ℂ, with e as a constant: T26.)

**EMN escapes both:** It has negative slopes (Type A doesn't apply) and it CAN build nonzero constants — emn(1,1) = −e in one node.

## The EMN Question — A Conjectured Answer

Is EMN complete? The conjectured answer: **approximately complete, not exactly complete.** Neither half has a proof (T24).

**EMN is not exactly complete (conjectured):** No finite EMN tree should compute ln(x) exactly for all x. The suggested obstruction is structural — every EMN output ln(R) − exp(L) has a nonzero exp(L) residual, and driving it to zero requires infinite depth (L → −∞). The growth-rate argument for this (sessions EMN-1 through EMN-3) is on paper, stops at an "infinite regress", and has no Lean proof.

**EMN is approximately complete (conjectured):** For any elementary function f and ε > 0, there exists a finite EMN tree T such that |Re(T(x)) − f(x)| < ε on any compact interval. The mechanism: complex intermediate values (via ln(−e) = 1 + iπ) route around the sign barrier. In the searches up to 8 nodes, the error falls doubly-exponentially with tree size.

The three completeness classes would form a clean trichotomy: **EML** (exactly complete), **EMN** (approximately complete), **all others** (incomplete). See the [Completeness Trichotomy](/blog/completeness-trichotomy) post for the sketches.

---

*Sessions Z1–Z9 · Direction 1 of the Research Roadmap*
