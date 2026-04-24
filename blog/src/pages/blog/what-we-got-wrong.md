---
layout: ../../layouts/Base.astro
title: "What We Got Wrong"
description: "Four things we retracted, corrected, or demoted during the 2026-04 foundation audit. What survived is stronger for it."
date: "2026-04-23"
author: "Monogate Research"
tag: observation
---

# What We Got Wrong

**Tier: OBSERVATION** (retractions + corrections from the foundation audit)

Research programs accumulate claims faster than they verify them. In April 2026 we audited every headline number in the project. Four things didn't survive. This post is the ledger.

## 1. ML-12: retracted

Original claim: a minimal EML-only neural network beats ReLU on a polynomial-regression task by about 8 percentage points. The original script ran three seeds, kept the median, discarded the others, and reported no standard deviation.

Rerun: 10 seeds, Welch t-test. Mean gap EML vs ReLU: +1.5 pp, **p = 0.64** — not significant. **The claim is retracted.** EML does not measurably beat ReLU on this task.

## 2. Catalog drift: 144/265 rows corrected

The 265-equation catalog has a `nodes_folded` field giving each equation's SuperBEST cost. A spot-check found 2 of 5 random rows didn't reconstruct from the op-count table. Full sweep: **144 of 265 rows (54.3%) had drifted from the v5.2 cost table**. Cause: the catalog was built before v5.2's mul 2→1 and div 3→2 simplifications, and was never rebuilt.

Fix: `recost_catalog.py` recomputes from `op_counts` under v5.2 TREE semantics. Downstream survivors: Zipf α ≈ 1.978, ELC-interior fraction ≈ 90%, log-normal T ≈ 5.69 (corrected from 9.46). Downstream correction: "Biology runs hottest at 12.55n" → **"Neuroscience runs hottest at 7.19n"**.

## 3. MNIST training cost: 7.92e12 → 4.358e12

The NN-10 session reported 7.92×10¹² EML nodes for 60K × 100-epochs MNIST. Under v5.2 TREE with sigmoid = 6n strict and Adam = 37n per param-step strict, recomputation gives **4.358×10¹² nodes** — the original was ~1.8× too high. The 7.92e12 number never reached a public surface. It's deprecated.

## 4. Softplus 17× over tanh on PINNs: demoted to UNVERIFIED

Earlier claim: softplus beats tanh on physics-informed neural networks by ~17× on some efficiency metric. A batch50b mini-retrain measured **~2× instead of 17×**. That measurement was on a tiny network; it doesn't invalidate the original but doesn't reproduce it either. Status: **UNVERIFIED**. No citation of 17× until a proper large-scale replication confirms or refutes.

## What survived

Six findings held up across the audit and can be cited:

- **FMA staircase**: 15.5% aggregate savings on 222 parseable of 265 equations; AIC-preferred staircase. See `/blog/fma-staircase`.
- **SuperBEST 14n / 80.8%** on the 10-op positive-domain basket. Lean-verified via `UpperBounds.lean`.
- **Oscillation boundary φ = 1.0** across 314 of 315 equations. See `/blog/oscillation-boundary`.
- **Zipf α ≈ 1.978** on catalog cost distribution.
- **Log-normal asymptotic T ≈ 5.69**.
- **68% of science fits in ELC₁₀**.

## Why publish the misses

If we retract only quietly, accumulated false positives crowd out the real results. The FMA finding reads stronger because we also know softplus and ML-12 didn't survive. The catalog audit is what made the foundation trustworthy.

---

*Monogate Research (2026). "What We Got Wrong." monogate research blog. https://monogate.org/blog/what-we-got-wrong*
