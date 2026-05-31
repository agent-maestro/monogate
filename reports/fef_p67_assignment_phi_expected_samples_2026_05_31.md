# FEF-P67 Assignment/Phi Expected Samples

Date: 2026-05-31

Status: `FEF_P67_ASSIGNMENT_PHI_EXPECTED_SAMPLES_PASS`

Decision: `assignment_phi_expected_samples_recorded_support_blocked`

FEF-P67 attaches deterministic expected samples to one blocked assignment/phi fixture.

## Summary

- Selected fixture: `c_branch_assignment_merge_v0`
- Selected fixture still blocked: `True`
- Samples: `7`
- Assignment taken samples: `3`
- Fallthrough samples: `4`
- Source semantics only: `True`
- Assignment/phi runtime execution claim: `False`
- Assignment/phi lowering claim: `False`
- Assignment/phi support claim: `False`

## Samples

| Sample | x | y | Path | Expected |
|---|---:|---:|---|---:|
| `sample_00` | 2.0 | 5.0 | `branch_assignment_to_y` | 5.0 |
| `sample_01` | -2.0 | 5.0 | `fallthrough_initial_x` | -2.0 |
| `sample_02` | 0.0 | 5.0 | `fallthrough_initial_x` | 0.0 |
| `sample_03` | 1.25 | -3.5 | `branch_assignment_to_y` | -3.5 |
| `sample_04` | -0.5 | -3.5 | `fallthrough_initial_x` | -0.5 |
| `sample_05` | 4.0 | 0.0 | `branch_assignment_to_y` | 0.0 |
| `sample_06` | -7.0 | 0.0 | `fallthrough_initial_x` | -7.0 |

## Boundary

- Expected samples only; no assignment/phi execution.
- No assignment/phi lowering or support claim.
- No frontend lowering change.
- No branch re-ingest, full source roundtrip, arbitrary source-family, compiler-correctness, formal-equivalence, or runtime-performance claim.
