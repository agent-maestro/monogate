# FEF-P27 rc_step_response_at_zero MachLib Surface Inventory

Date: 2026-05-30

Status: `FEF_P27_RC_STEP_MACHLIB_SURFACE_INVENTORY_PASS`

Decision: `rc_step_response_proof_surface_inventory_recorded`

| Identifier | Generated imports | Ring import | Needed for |
|---|---:|---:|---|
| `zero_div` | `identifier_missing` | `identifier_missing` | 0 / tau_val = 0 |
| `div_zero` | `identifier_missing` | `identifier_missing` | audit absence of named division-zero rewrite |
| `exp_zero` | `identifier_available` | `identifier_available` | Real.exp 0 = 1 |
| `mul_zero` | `identifier_available` | `identifier_available` | vin * 0 = 0 |
| `zero_mul` | `identifier_available` | `identifier_available` | 0 * vin = 0 if orientation changes |
| `sub_self` | `identifier_missing` | `identifier_available` | 1 - 1 = 0 after exp_zero |
| `sub_def` | `identifier_available` | `identifier_available` | manual subtraction rewrite fallback |
| `add_neg` | `identifier_available` | `identifier_available` | manual subtraction cancellation fallback |

## Summary

- Surface items checked: `8`
- Generated-surface available: `5`
- Generated-surface missing: `3`
- Zero-division lemma missing: `True`
- `sub_self` requires `MachLib.Ring`: `True`

## Boundary

- Identifier inventory only; no MachLib lemma or Forge/eFrog behavior change.
- `rc_step_response_at_zero` remains undischarged.
- No all-generated-file proof, compiler-correctness, formal-equivalence, or public-readiness claim.
- No package publication, checkout, performance, hardware, or all-target claim.
