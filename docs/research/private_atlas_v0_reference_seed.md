# Private EML Atlas v0 Reference Seed

Status: private seed, not public copy
Date: 2026-06-08

## Purpose

This seed collects the currently reviewable private Atlas rows into one
reader-facing reference document. It is meant to reduce the cost of
reviewing scattered evidence packets and handoff notes.

It is not a public Atlas, not a completeness claim, and not SDK/course
copy. Each row remains bounded by its source artifact and non-claims.

## Current Count

- private rows recorded: `15`
- target range: `15`-`25`
- additional artifacts needed for lower-bound observation: `0`
- catalog completeness claim: `false`
- public readiness claim: `false`

## Rows

| # | Witness | Family | Guard | Runtime Boundary | Source |
|---:|---|---|---|---|---|
| 1 | `MachLib.Real.constants_zero_one_e_boundary_witness` | constants boundary | constant-domain boundary | standard constants remain runtime controls | `atlas-a1-private-checked-witness-table` |
| 2 | `MachLib.Real.ln_from_eml_boundary_witness` | log boundary | positive logarithm domain guard | standard log/exp remains the runtime control | `atlas-a1-private-checked-witness-table` |
| 3 | `MachLib.Real.subtraction_boundary_affine_offset_witness` | subtraction boundary | `0 < x + y` | standard subtraction remains the runtime control | `atlas-a1-private-checked-witness-table` |
| 4 | `MachLib.Real.subtraction_boundary_two_stage_chain_witness` | nested subtraction boundary | positive log-input guards | standard subtraction remains the runtime control | `atlas-a1-private-checked-witness-table` |
| 5 | `MachLib.Real.subtraction_boundary_affine_nested_chain_witness` | nested subtraction boundary | `0 < x + y` and `0 < z` | standard subtraction remains the runtime control | `atlas-a1-private-checked-witness-table` |
| 6 | `MachLib.Real.subtraction_boundary_three_stage_chain_witness` | nested subtraction boundary | positive log-input guards | standard subtraction remains the runtime control | `atlas-a1-private-checked-witness-table` |
| 7 | `MachLib.Real.positive_log_exp_roundtrip_witness` | positive log/exp roundtrip | `0 < x` | standard log/exp remains the runtime control | `atlas-a1-private-checked-witness-table` |
| 8 | `MachLib.Real.expm1_boundary_identity_witness` | expm1 boundary | no extra real-domain guard recorded | protected `expm1` remains the runtime control | `atlas-a1-private-checked-witness-table` |
| 9 | `MachLib.Real.constant_coordinate_zero_exp_two_witness` | constant coordinate | local `exp (1 + 1)` spelling boundary | standard constants remain runtime controls | `atlas-a1-private-checked-witness-table` |
| 10 | `MachLib.Real.probability_logit_boundary_coordinate_witness` | probability-logit boundary | `0 < p` and `p < 1` | protected `log` and `log1p` remain the runtime controls | `atlas-a1-private-checked-witness-table` |
| 11 | `MachLib.Real.log1p_shifted_boundary_coordinate_witness` | log1p shifted boundary | `0 < 1 + x` | protected `log` and `log1p` remain the runtime controls | `atlas-a1-private-checked-witness-table` |
| 12 | `MachLib.Real.log1m_shifted_boundary_coordinate_witness` | log1m shifted boundary | `0 < 1 - x` | protected `log` and `log1p` remain the runtime controls | `atlas-a1-private-checked-witness-table` |
| 13 | `MachLib.Real.log1p_affine_scaled_boundary_coordinate_witness` | log1p affine-scaled boundary | `0 < 1 + a * x` | protected `log` and `log1p` remain the runtime controls | `atlas-a1-private-checked-witness-table` |
| 14 | `MachLib.Real.exp_negation_multiplicative_identity_witness` | exp algebra boundary | all real inputs; no extra guard | standard `exp` remains the runtime control | `atlas-a33-private-exp-negation-bounded-wrapper-attempt-artifact` |
| 15 | `MachLib.Real.trig_pythagorean_unit_identity_witness` | trig boundary | all real inputs; no extra guard | standard trig functions remain the runtime controls | `atlas-a43-private-trig-pythagorean-bounded-wrapper-attempt-artifact` |

## Usefulness Notes

- Public witness candidates: expm1 boundary, positive log-exp roundtrip, exp-negation wrapper, and trig Pythagorean wrapper need separate copy gates before use.
- SDK/compiler guard-note candidates should be extracted only after private review confirms the row wording and non-claims.
- Course references should cite guards and runtime boundaries, not broad EML advantage.

## Non-Claims

- No public Atlas or public math page is created by this seed.
- No catalog completeness or target-lower-bound promotion is claimed.
- No runtime replacement, runtime performance, compiler correctness, or formal equivalence is claimed.
- No SDK/compiler documentation, course material, product implementation, or electronics/laptop artifact is created or consumed.

## Next Review Questions

- Are all row labels clear enough for a reviewer?
- Which rows are strongest public-witness candidates after a separate copy gate?
- Which rows have useful SDK/course guard-note hooks without overstating runtime behavior?
- Should any row be parked before a future private Atlas v0 review packet?
