# ATLAS-A24 Private Reference-Value Gap Pool Refresh

Status: `ATLAS_A24_PRIVATE_REFERENCE_VALUE_GAP_POOL_REFRESH_PASS`

## Summary

- source artifact: `atlas-a23-private-atlas-gap-strategy-selector`
- pool id: `atlas_a24_reference_value_gap_pool_v0`
- candidate directions: `4`
- excluded paths: `2`
- highest reference-value entry: `square_nonnegative_guard_direction`
- candidate selected for packet: `False`
- new candidate packet created: `False`
- proof attempt started: `False`
- MachLib changed: `False`
- Lean typecheck performed: `False`
- next recommended artifact: `ATLAS-A25 private refreshed gap candidate value selector`

## Excluded Paths

- `blocked_eml_sqrt_boundary_path`: excluded_from_a24_pool_unless_new_precise_statement (A21/A22 recorded that the EML boundary alignment is not justified by the current local EML definition.)
- `deferred_reciprocal_positive_boundary_path`: deferred_not_rejected (Earlier review found reciprocal feasible but lower reference value for Atlas diversity.)

## Candidate Directions

| Direction | Family | Guard | Score |
|---|---|---|---|
| `square_nonnegative_guard_direction` | `polynomial_guard_boundary` | `all real x` | `22` |
| `trig_pythagorean_unit_identity_direction` | `trig_boundary` | `all real x` | `21` |
| `exp_negation_multiplicative_identity_direction` | `exp_algebra_boundary` | `all real x` | `21` |
| `logistic_symmetry_boundary_direction` | `sigmoid_probability_boundary` | `all real x after sigma definition is fixed` | `18` |

## Non-Claims

- ATLAS-A24 creates a private refreshed candidate-direction pool only; it does not create a candidate packet, select a proof target, prove a witness, or claim candidate validity.
- ATLAS-A24 records scored directions for future review, not checked statements, theorem names, Lean-ready claims, runtime lowering changes, public copy, SDK/compiler/course copy, product implementation, or broad EML advantage.
- ATLAS-A24 keeps the blocked EML-shaped sqrt path excluded unless a new precise statement appears and keeps reciprocal deferred rather than rejected or disproved.
