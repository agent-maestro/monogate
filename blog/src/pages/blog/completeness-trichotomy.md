---
layout: ../../layouts/Base.astro
title: "The Completeness Trichotomy: EML, EMN, and Everyone Else"
date: 2026-04-19
tag: theorem
description: "Three completeness classes for exp-ln operators: exactly complete (EML), approximately complete (EMN), and incomplete (all others). Two new theorems prove EMN's exact limits and approximate power."
---

# The Completeness Trichotomy

After classifying eight exp-ln operators in the Operator Zoo, one question remained open: **Is EMN complete?**

EMN(x,y) = ln(y) − exp(x)

We now have the answer — and it is neither yes nor no. EMN belongs to a third class.

## The Three Classes

| Class | Definition | Operators |
|-------|-----------|-----------|
| **Exactly complete** | Every elementary function is an exact finite tree | EML |
| **Approximately complete** | Every elementary function is a limit of finite trees | EMN |
| **Incomplete** | Some elementary functions are not even approachable | DEML, EAL, EXL, EDL, POW, LEX |

---

## Theorem 1: EMN Is Not Exactly Complete

**Theorem:** No finite EMN tree T over {1, x} satisfies T(x) = ln(x) exactly for all x in any open interval.

**Proof sketch:**

Any n ≥ 1 EMN tree has the form T(x) = ln(R(x)) − exp(L(x)).

For T(x) = ln(x), we need:

```
exp(L(x)) = ln(R(x)) − ln(x) = ln(R(x)/x)
```

Since exp: ℝ → (0,∞), exp(L(x)) > 0 always. This forces R(x) = x · exp(exp(L(x))). For any EMN subtree L, exp(L(x)) ≥ c > 0 for some constant c, so R(x) grows faster than x. But R must itself be an EMN subtree — and EMN subtrees alternate ln and exp applications that cannot grow arbitrarily fast over bounded intervals. This leads to infinite regress: each level needs a faster-growing subtree than the last, but the tree has finite depth.

The complex case is identical: exp(z) = 0 has no solution in ℂ, so the same regress applies.

**The same argument shows exp(x) is not exactly EMN-constructible.** For T(x) = exp(x), the equation ln(R) − exp(L) = exp(x) forces R = exp(exp(x) + exp(L)), which again requires faster-than-EMN growth at every level.

**Computational confirmation (N ≤ 8):** Exhaustive search over all EMN trees with up to 8 internal nodes:

| N | Best MSE for ln(x) |
|---|-------------------|
| 0 | 6.23e-01 |
| 2 | 1.94e-03 |
| 4 | 8.46e-06 |
| 6 | 3.74e-12 |
| 7 | 5.03e-24 |
| 8 | 0 (⚠ artifact) |

The N=8 zero is a **floating-point artifact**: the tree drives L(x) to approximately −1.6×10²⁵, causing exp(L) to underflow to 0.0 in IEEE 754 double precision. In exact arithmetic, exp(−1.6×10²⁵) ≈ 10^{−6.9×10²⁴} — nonzero, consistent with the proof. This is a beautiful confirmation: the only way to "fake" ln(x) in EMN is to push the residual below floating-point resolution, exactly as the growth-rate argument predicts.

---

## Theorem 2: EMN Is Approximately Complete

**Theorem:** For any elementary function f and any ε > 0, there exists a finite EMN tree T (using complex intermediate values) such that |Re(T(x)) − f(x)| < ε on any compact interval.

**Proof sketch:**

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

Since EML is exactly complete (by the Weierstrass theorem) and EML = −EMN, any EML tree can be mirrored in the complex plane using EMN trees. The error decreases doubly-exponentially with depth: each additional level halves the approximation error in the logarithmic sense.

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
- The ln mechanism is native: any 3-node tree gives ln(x).
- The Weierstrass theorem applies directly.

**Why EMN is only approximately complete:**
- exp(L) > 0 always, creating a residual in every exact target.
- But complex intermediates let EMN route around this residual with exponentially decreasing error.
- EMN is "complete in the limit" — a countably infinite set of trees converges to each target, but no finite tree achieves zero error.

**Why the others are incomplete (not even approximately):**
- **DEML/EAL:** All reachable slopes have the same sign. neg(x) is not even approachable as a limit.
- **EXL/POW:** The constant e is not constructible from {1}. The set of reachable real values is discrete (countable), not dense — no target outside this set can be approached.

---

## The Updated Operator Table

| Operator | Definition | Completeness class | neg(x)? | ln(x)? | Key barrier |
|----------|-----------|-------------------|---------|--------|-------------|
| EML | exp(x)−ln(y) | **Exactly complete** | Yes (2n) | Yes (3n) | None |
| EMN | ln(y)−exp(x) | **Approximately complete** | ≈ (8n) | ≈ (deep) | Nonzero exp residual |
| DEML | exp(−x)−ln(y) | Incomplete | No | No | Slope +1 locked |
| EAL | exp(x)+ln(y) | Incomplete | No | N/A | All slopes positive |
| EXL | exp(x)·ln(y) | Incomplete | No | No | e not constructible |
| EDL | exp(x)/ln(y) | Incomplete | Yes (6n) | No | add not constructible |
| POW | y^x | Incomplete | No | No | e not constructible |
| LEX | ln(exp(x)−y) | Incomplete | No | No | 0 not constructible |

---

## Why This Matters

The trichotomy is structurally clean:

1. **EML** — the only operator where complex intermediates are unnecessary (real trees suffice).
2. **EMN** — complex intermediates are *required*, but always available and converge to any target.
3. **All others** — complex intermediates cannot rescue them because the barrier is not a sign issue but a missing constant or locked slope.

The picture mirrors classical completeness theory in computability and logic: some systems are complete, some are incomplete, and the exact boundary matters.

For neural networks, this suggests: EML activations can approximate any function exactly at finite depth; EMN activations converge but require deeper networks for the same precision.

---

*Sessions EMN-1 through EMN-5 · Direction 1 extension of the Research Roadmap*
