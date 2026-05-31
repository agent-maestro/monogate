# FEF-P63 Nested Branch Expected Samples

Date: 2026-05-31

Status: `FEF_P63_NESTED_BRANCH_EXPECTED_SAMPLES_PASS`

Decision: `nested_branch_expected_samples_recorded_support_blocked`

FEF-P63 attaches deterministic expected samples to one blocked nested-branch fixture.

## Summary

- Selected fixture: `c_nested_if_return_v0`
- Selected fixture still blocked: `True`
- Samples: `7`
- Nonzero expected samples: `2`
- Zero expected samples: `5`
- Source semantics only: `True`
- Nested branch runtime execution claim: `False`
- Nested branch lowering claim: `False`
- Nested branch support claim: `False`

## Samples

| Sample | x | y | Path | Expected |
|---|---:|---:|---|---:|
| `sample_00` | 2.0 | 3.0 | `outer_true_inner_true_return_sum` | 5.0 |
| `sample_01` | 2.0 | -1.0 | `fallthrough_return_zero` | 0.0 |
| `sample_02` | -2.0 | 3.0 | `fallthrough_return_zero` | 0.0 |
| `sample_03` | 0.0 | 3.0 | `fallthrough_return_zero` | 0.0 |
| `sample_04` | 2.0 | 0.0 | `fallthrough_return_zero` | 0.0 |
| `sample_05` | 1.25 | 0.75 | `outer_true_inner_true_return_sum` | 2.0 |
| `sample_06` | -0.5 | -0.5 | `fallthrough_return_zero` | 0.0 |

## Boundary

- Expected samples only; no nested branch execution.
- No nested branch lowering or support claim.
- No frontend lowering change.
- No branch re-ingest, full source roundtrip, arbitrary source-family, compiler-correctness, formal-equivalence, or runtime-performance claim.
