# MonogateEML — Lean 4 Formalization

Lean 4 / Mathlib4 formalization of the Complex EML hierarchy.

## Contents

- `MonogateEML/EMLDepth.lean` — Core definitions and theorems:
  - `EMLTree` inductive type (const, var, ceml nodes)
  - `EMLTree.eval` — evaluation function
  - `EMLTree.depth` — depth measure
  - `EML_k k` — set of functions of depth ≤ k
  - CEML-T1 (Euler Gateway) — proved
  - CEML-T5 (Euler Identity) — proved
  - CEML-T40 (EML-0 ⊊ EML-1) — proved
  - CEML-T48 (sin ∉ EML-k(ℝ)) — skeleton, 2 sorries

## Sorry Census

| Location | Description | Difficulty | Blocking |
|----------|-------------|------------|---------|
| `depth1_monotone` | Case analysis of 4 depth-1 tree shapes | MEDIUM | No |
| `sin_not_in_real_EML_k` | Monotonicity induction + sign-change argument | HARD | Yes |

## Building

```bash
# Requires lake (Lean 4 build tool) and Mathlib4
lake update
lake build
```

## Toolchain

- Lean 4: v4.14.0
- Mathlib4: v4.14.0

## Research Context

Sessions 11-50 of the Complex EML research program (94 theorems).
See `python/monogate/frontiers/` for Python implementations.
