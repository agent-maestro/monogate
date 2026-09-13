---
layout: ../../layouts/Base.astro
title: "The Completeness Trichotomy: EML, EMN, and Everyone Else"
date: 2026-04-19
tag: conjecture
description: "Three completeness classes for exp-ln operators: exactly complete (EML), approximately complete (EMN), and incomplete (all others). Two conjectures about EMN's exact limits and approximate power, with sketches that stop short of proofs."
---

# The Completeness Trichotomy

<p style="color: var(--muted); font-style: italic;">Correction (2026-09-13): this post presented two theorems about EMN with proofs. Both are conjectures (T24): the sketch for the first stops at "infinite regress", and the second mirrors EML trees through EML = −EMN, which negates only the root node. The reasons given for the other operators being incomplete are unproved too, except that over ℝ no EAL tree approximates −x.</p>

<p style="color: var(--muted); font-style: italic;">Second correction (2026-09-13): the operator table said EML builds neg(x) in 2 nodes. The 2-node tree, exl(0, deml(x, 1)), uses EXL and DEML, and no EML tree with at most 2 nodes over {1, x} equals −x (none comes within 2.7 of it on [0.5, 3]); EML builds neg(x) by the published universality result (T01), in more nodes. The EXL row said EXL cannot build ln(x), but exl(exl(1, 1), x) = e⁰·ln x = ln x. The class tables record April's classification, in which only EML is complete. The later 16-operator census conjectures EAL (over ℂ), EXL, EDL and POW (which is EPL) exactly complete as well (T26), and neither classification is proved. The table's other cells are April's and were not re-checked.</p>

> **Updated:** The full 16-operator census (sessions COMP-1 through COMP-5; T12 on /theorems) extends this result. The trichotomy
> (1 complete / 1 approximate / 6 incomplete) is superseded by the
> **Exponential Position Theorem** (T12, T26–T28), a conjecture: **8 complete / 1 approximate / 7 incomplete** over ℂ.
> It proposes that EML is not the only complete operator — that 7 others share the same structural property.
> Over ℝ that fails for EAL, whose real trees are all nondecreasing.
> See [Does exp(+x) Mean Complete?](/blog/completeness-characterization) for the argument, which has gaps.

After classifying eight exp-ln operators in the Operator Zoo, one question remained open: **Is EMN complete?**

EMN(x,y) = ln(y) − exp(x)

We now have a conjectured answer — and it is neither yes nor no. EMN would belong to a third class.

## The Three Classes

| Class | Definition | Operators |
|-------|-----------|-----------|
| **Exactly complete** | Every elementary function is an exact finite tree | EML (the published result, T01). The later census conjectures EAL (over ℂ), EXL, EDL and POW exactly complete too (T26) |
| **Approximately complete** | Every elementary function is a limit of finite trees | EMN |
| **Incomplete** | Some elementary functions are not even approachable | DEML and LEX (conjectured: T13, T28); EAL over ℝ. This post also listed EAL, EXL, EDL and POW here |

---

## Conjecture 1: EMN Is Not Exactly Complete

**Conjecture:** No finite EMN tree T over {1, x} satisfies T(x) = ln(x) exactly for all x in any open interval.

**Sketch (incomplete):**

Any n ≥ 1 EMN tree has the form T(x) = ln(R(x)) − exp(L(x)).

For T(x) = ln(x), we need:

```
exp(L(x)) = ln(R(x)) − ln(x) = ln(R(x)/x)
```

Since exp: ℝ → (0,∞), exp(L(x)) > 0 always. This forces R(x) = x · exp(exp(L(x))). For any EMN subtree L, exp(L(x)) ≥ c > 0 for some constant c, so R(x) grows faster than x. But R must itself be an EMN subtree — and EMN subtrees alternate ln and exp applications that cannot grow arbitrarily fast over bounded intervals. This leads to infinite regress: each level needs a faster-growing subtree than the last, but the tree has finite depth. The sketch stops there: it does not show that no finite tree escapes the regress.

The complex case is identical: exp(z) = 0 has no solution in ℂ, so the same regress applies.

**The same argument would show exp(x) is not exactly EMN-constructible.** For T(x) = exp(x), the equation ln(R) − exp(L) = exp(x) forces R = exp(exp(x) + exp(L)), which again requires faster-than-EMN growth at every level.

**Computational evidence (N ≤ 8):** Exhaustive search over all EMN trees with up to 8 internal nodes:

| N | Best MSE for ln(x) |
|---|-------------------|
| 0 | 6.23e-01 |
| 2 | 1.94e-03 |
| 4 | 8.46e-06 |
| 6 | 3.74e-12 |
| 7 | 5.03e-24 |
| 8 | 0 (⚠ artifact) |

The N=8 zero is a **floating-point artifact**: the tree drives L(x) to approximately −1.6×10²⁵, causing exp(L) to underflow to 0.0 in IEEE 754 double precision. In exact arithmetic, exp(−1.6×10²⁵) ≈ 10^{−6.9×10²⁴} — nonzero, consistent with the conjecture. It fits the growth-rate argument: this tree "fakes" ln(x) by pushing the residual below floating-point resolution.

---

## Conjecture 2: EMN Is Approximately Complete

**Conjecture:** For any elementary function f and any ε > 0, there exists a finite EMN tree T (using complex intermediate values) such that |Re(T(x)) − f(x)| < ε on any compact interval.

**Sketch (incomplete):**

The mechanism: EMN uses complex intermediates to route around the exp(·) > 0 barrier.

The key example is neg(x). The 8-node tree:
```
emn(emn(emn(emn(emn(emn(x, emn(1,1)), emn(1,1)), 1), x), x), 1)
```
achieves error ~10⁻⁷ at x = 1.5 by:
1. Building emn(1,1) = −e (a negative constant)
2. Using ln(−e) = 1 + iπ to generate complex phase
3. Cancelling imaginary parts through symmetric application
4. Extracting an approximation to ln(x) (error ~ e^{−depth})
5. Applying emn(·, 1) = −(·) to negate it

The sketch then argued: since EML is exactly complete (T01) and EML = −EMN, any EML tree can be mirrored in the complex plane using EMN trees. That step fails: emn(x, y) = −eml(x, y) negates only the root node, so it does not turn an EML tree into an EMN tree. In the searches, the error decreases doubly-exponentially with tree size.

**For neg(x) specifically** — the error sequence (best MSE vs. tree size):

| N | Best MSE (neg(x)) |
|---|------------------|
| 0 | 1.43 |
| 2 | 1.14e-01 |
| 3 | 1.55e-03 |
| 5 | 6.73e-06 |
| 7 | 1.44e-12 |
| 8 | 5.86e-24 |
| 9 | 0 (IEEE 754 underflow) |

The error drops by roughly 10⁶–10⁹ every two additional nodes — consistent with the doubly-exponential decay predicted by the complex-phase cancellation mechanism.

---

## What Separates the Three Classes

**Why EML is exactly complete:**
- The ln mechanism is native: a 3-node tree gives ln(x).
- Exactness is the published universality result (T01), not a consequence of the Weierstrass argument, which has a gap.

**Why EMN would be only approximately complete:**
- exp(L) > 0 always, creating a residual in every exact target.
- But complex intermediates let EMN route around this residual with exponentially decreasing error.
- EMN is "complete in the limit" — a countably infinite set of trees converges to each target, but no finite tree achieves zero error.

**Why the others were counted incomplete (not even approximately):**
- **DEML/EAL:** All reachable slopes were said to have the same sign, so neg(x) is not even approachable as a limit. Over ℝ that holds for EAL: every real EAL tree T = exp(A) + ln(B) has T′ = A′e^A + B′/B ≥ 0. For DEML the slope argument has a gap (deml(x, 1) = exp(−x) decreases), and the claim is a conjecture (T13).
- **EXL/POW:** The constant e is not constructible from {1}, and the constants reachable from {1} alone form a discrete set. That does not settle which functions trees over {1, x} can approach, so these cases are unproved too.

---

## The Updated Operator Table

| Operator | Definition | Completeness class | neg(x)? | ln(x)? | Key barrier |
|----------|-----------|-------------------|---------|--------|-------------|
| EML | exp(x)−ln(y) | **Exactly complete** | Yes (T01), not in 2 nodes | Yes (3n) | None |
| EMN | ln(y)−exp(x) | **Approximately complete** | ≈ (8n) | ≈ (deep) | Nonzero exp residual |
| DEML | exp(−x)−ln(y) | Incomplete | No | No | Slope +1 locked |
| EAL | exp(x)+ln(y) | Incomplete over ℝ; conjectured complete over ℂ (T26) | No | N/A | All slopes positive (over ℝ) |
| EXL | exp(x)·ln(y) | Incomplete (April); conjectured complete over ℂ (T26) | No | Yes (2n): exl(exl(1,1), x) | e not constructible |
| EDL | exp(x)/ln(y) | Incomplete (April); conjectured complete over ℂ (T26) | Yes (6n) | No | add not constructible: conjecture C1 of the preprint |
| POW | y^x | Incomplete (April); POW = EPL, conjectured complete over ℂ (T26) | No | No | e not constructible |
| LEX | ln(exp(x)−y) | Incomplete | No | No | 0 not constructible |

---

## Why This Matters

The trichotomy is structurally clean:

1. **EML** — the only operator here with a proof of exact completeness (T01); it still needs complex intermediates for some targets, since sin(x) is not a real EML tree.
2. **EMN** — complex intermediates are *required*, and conjectured to converge to any target.
3. **All others** — the claim is that complex intermediates cannot rescue them, because the barrier is not a sign issue but a missing constant or locked slope; that is unproved. The later census conjectures the opposite for EAL, EXL, EDL and POW over ℂ (T26).

The picture mirrors classical completeness theory in computability and logic: some systems are complete, some are incomplete, and the exact boundary matters.

For neural networks, this suggests: EML activations can approximate any function exactly at finite depth; EMN activations converge but require deeper networks for the same precision.

---

*Sessions EMN-1 through EMN-5 · Direction 1 extension of the Research Roadmap*
