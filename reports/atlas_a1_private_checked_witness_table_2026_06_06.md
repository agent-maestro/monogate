# ATLAS-A1 Private Checked Witness Table

Status: `ATLAS_A1_PRIVATE_CHECKED_WITNESS_TABLE_PASS`

## Summary

- source artifact: `eml-d100-bounded-artifact-target-set-consolidation-review`
- Atlas rows: `13`
- families: `11`
- target range: `15-25`
- additional artifacts needed for lower bound: `2`
- public promotion allowed: `False`
- next recommended artifact: `ATLAS-A2 private Atlas gap review or pause selector`

## Family Counts

| Family | Count |
|---|---:|
| `constant_coordinate` | 1 |
| `constants_boundary` | 1 |
| `expm1_boundary` | 1 |
| `log1m_shifted_boundary` | 1 |
| `log1p_affine_scaled_boundary` | 1 |
| `log1p_shifted_boundary` | 1 |
| `log_boundary` | 1 |
| `nested_subtraction_boundary` | 3 |
| `positive_log_exp` | 1 |
| `probability_logit_boundary` | 1 |
| `subtraction_boundary` | 1 |

## Private Atlas Rows

| Witness | Family | Guard | Runtime control |
|---|---|---|---|
| `constants_zero_one_e_boundary` | `constants_boundary` | constant-domain boundary | standard constants remain runtime controls |
| `ln_from_eml_boundary` | `log_boundary` | positive logarithm domain guard | standard_log_exp_remains_runtime_control |
| `subtraction_boundary_affine_offset` | `subtraction_boundary` | 0 < x + y | standard_subtraction_remains_runtime_control |
| `subtraction_boundary_two_stage_chain` | `nested_subtraction_boundary` | positive log-input guards | standard_subtraction_remains_runtime_control |
| `subtraction_boundary_affine_nested_chain` | `nested_subtraction_boundary` | 0 < x + y and 0 < z | standard_subtraction_remains_runtime_control |
| `subtraction_boundary_three_stage_chain` | `nested_subtraction_boundary` | positive log-input guards | standard_subtraction_remains_runtime_control |
| `positive_log_exp_roundtrip` | `positive_log_exp` | 0 < x | standard_log_exp_remains_runtime_control |
| `expm1_boundary_identity` | `expm1_boundary` | no extra real-domain guard recorded | protected_expm1_remains_runtime_control |
| `constant_coordinate_zero_exp_two` | `constant_coordinate` | local exp (1 + 1) spelling boundary | standard constants remain runtime controls |
| `probability_logit_boundary_coordinate` | `probability_logit_boundary` | 0 < p and p < 1 | protected_log_and_log1p_remain_runtime_controls |
| `log1p_shifted_boundary_coordinate` | `log1p_shifted_boundary` | 0 < 1 + x | protected_log_and_log1p_remain_runtime_controls |
| `log1m_shifted_boundary_coordinate` | `log1m_shifted_boundary` | 0 < 1 - x | protected_log_and_log1p_remain_runtime_controls |
| `log1p_affine_scaled_boundary_coordinate` | `log1p_affine_scaled_boundary` | 0 < 1 + a * x | protected_log_and_log1p_remain_runtime_controls |

## Non-Claims

- ATLAS-A1 is a private table over the already consolidated D100 checked-witness rows; it is not a public Atlas page or public-copy approval.
- ATLAS-A1 records families, guards, runtime controls, and target-set status for reviewer legibility; it does not claim the witness catalog is complete.
- ATLAS-A1 does not select a new identity, edit MachLib, typecheck Lean, start proof work, change runtime lowering, create SDK/compiler/course copy, implement a visualization, consume reviewer responses, touch laptop-owned repositories, or claim runtime performance, compiler correctness, formal equivalence, public readiness, or broad EML advantage.
