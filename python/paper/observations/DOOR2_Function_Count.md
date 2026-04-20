# DOOR-2: Functional Distinctness Count for EML-Family Trees

**Status:** OBSERVATION (computationally measured, depths 0–3)

---

## Setup

- **Terminals:** {1, x} (two leaves)
- **Depth k:** number of operator nodes in the binary tree (not tree height)
- **Input pool at depth k:** all distinct functions found at depths 0 through k−1
- **Equivalence criterion:** numeric agreement at 20 test points in (0.1, 5.0);
  symbolic fallback via SymPy `simplify(f − g) = 0` only for expressions with
  no valid numeric domain.

Three operators studied:

| Name | Formula |
|------|---------|
| EML  | exp(a) − ln(b) |
| EXL  | exp(a) · ln(b) |
| EAL  | exp(a) + ln(b) |

---

## Counts at Each Depth

### New distinct functions introduced at depth k

| Depth k | EML | EXL | EAL |
|---------|-----|-----|-----|
| 0       |   2 |   2 |   2 |
| 1       |   4 |   3 |   4 |
| 2       |  32 |  18 |  32 |
| 3       |1406 | 497 |1406 |

### Cumulative distinct functions through depth k

| Through depth k | EML  | EXL | EAL  |
|-----------------|------|-----|------|
| 0               |    2 |   2 |    2 |
| 1               |    6 |   5 |    6 |
| 2               |   38 |  23 |   38 |
| 3               | 1444 | 520 | 1444 |

---

## Growth Pattern

**Depth-to-depth ratios (new functions):**

| Ratio k→k+1 | EML  | EXL  | EAL  |
|-------------|------|------|------|
| 0→1         | 2.00 | 1.50 | 2.00 |
| 1→2         | 8.00 | 6.00 | 8.00 |
| 2→3         |43.94 |27.61 |43.94 |

All three operators show **super-exponential (accelerating) growth**: the
depth-to-depth ratio itself increases with each step, ruling out purely
exponential growth. The cumulative counts grow much faster than any fixed
exponential base.

**Linear?** No — ruled out by the ratios exceeding 1 at every step.

**Exponential (fixed base)?** No — the ratios are not constant; they
accelerate (2 → 8 → 44 for EML/EAL).

**Catalan-like?** No — Catalan numbers (1, 1, 2, 5, 14, 42, …) grow as
C_n ~ 4^n / (n^{3/2} √π), far below the observed counts at depth 3.

The observed growth is consistent with **doubly exponential** or
**tower-exponential** behavior, plausibly because each depth adds all
pairwise combinations of an already-large pool, giving a squaring effect.
The cumulative pool of size P at depth k generates roughly P² candidates at
depth k+1, most of which are new, so P_{k+1} ≈ P_k². This predicts:

- P_0 = 2
- P_1 ≈ 4
- P_2 ≈ 16 → 38 (observed; some collisions reduce this)
- P_3 ≈ 38² = 1444 (EML/EAL observed: exactly 1444 — near-zero collision rate)

This near-perfect squaring at depth 3 for EML and EAL is a strong
**OBSERVATION** suggesting that the depth-3 expressions are nearly all
distinct — almost no two distinct depth-2 inputs produce the same depth-3
output.

---

## Comparison Across Operators

### Combinatorial Equivalence

**EML and EAL are combinatorially equivalent:** their new-per-depth sequences
and cumulative counts are identical at all measured depths:

```
EML: new = [2, 4, 32, 1406],  cumulative = [2, 6, 38, 1444]
EAL: new = [2, 4, 32, 1406],  cumulative = [2, 6, 38, 1444]
```

This is not a coincidence: both operators take the form `exp(a) ⊕ g(b)` where
⊕ is an additive combination and g(b) = ±ln(b). The structural symmetry of the
tree enumeration, combined with the fact that {1, x} produces the same numeric
range for both operators, yields identical functional distinctness counts.

**EXL is strictly smaller:** multiplication by ln(b) introduces more
collisions (e.g., exp(a) · ln(1) = 0 for any a) and more domain restrictions
(ln(b) undefined for b ≤ 0), reducing the effective pool size at each depth.

### Summary Table

| Property | EML | EXL | EAL |
|----------|-----|-----|-----|
| Cumulative at depth 3 | 1444 | 520 | 1444 |
| Growth class | super-exponential | super-exponential | super-exponential |
| Same rate as another? | = EAL | — | = EML |
| Near-perfect squaring at depth 3? | Yes (1444 ≈ 38²) | Partial (520 < 23²=529) | Yes |

---

## Classification

| Claim | Classification |
|-------|---------------|
| Counts at depths 0–3 for EML, EXL, EAL | **OBSERVATION** (computed) |
| Growth is super-exponential (accelerating ratios) | **OBSERVATION** |
| EML and EAL have identical functional-distinctness sequences | **OBSERVATION** |
| Depth-k cumulative count ≈ (depth k−1 count)² for EML/EAL | **OBSERVATION** |
| This squaring behavior holds at all depths | **CONJECTURE** (unproven) |
| The growth rate is Θ(2^{2^k}) | **CONJECTURE** |

---

## Notes

- "Zoo" (complex infinity) appears in several EXL sample expressions; these are
  treated as having no valid numeric signature and are retained as distinct
  entries via the symbolic fallback only if they cannot be equated symbolically.
  The presence of zoo entries at depth 2 onward reflects that EXL produces
  expressions with singularities on the positive reals (e.g., exp(a) · ln(1) = 0
  entering as a log argument).

- Script: `python/scripts/door2_function_count.py`
- Data: `python/results/s103_door2_function_count.json`
