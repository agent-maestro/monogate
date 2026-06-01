# FEF-P114 Compound-Condition Expected Samples

Date: 2026-06-01

Status: `FEF_P114_COMPOUND_CONDITION_EXPECTED_SAMPLES_PASS`

Decision: `compound_condition_expected_samples_recorded_support_blocked`

FEF-P114 attaches deterministic expected samples to one blocked compound-condition fixture.

## Summary

- Selected fixture: `c_and_guard_return_v0`
- Selected fixture still blocked: `True`
- Samples: `7`
- Nonzero expected samples: `2`
- Zero expected samples: `5`
- Right predicate evaluated samples: `4`
- Short-circuit expected samples: `3`
- Source semantics only: `True`
- Compound-condition runtime execution claim: `False`
- Compound-condition lowering implemented: `False`
- Compound-condition support claim: `False`

## Samples

| Sample | x | y | Path | Right evaluated | Expected |
|---|---:|---:|---|---|---:|
| `sample_00` | `2.0` | `3.0` | `left_true_right_true_return_sum` | `True` | `5.0` |
| `sample_01` | `2.0` | `-1.0` | `left_true_right_false_return_zero` | `True` | `0.0` |
| `sample_02` | `-2.0` | `3.0` | `left_false_short_circuit_return_zero` | `False` | `0.0` |
| `sample_03` | `0.0` | `3.0` | `left_false_short_circuit_return_zero` | `False` | `0.0` |
| `sample_04` | `2.0` | `0.0` | `left_true_right_false_return_zero` | `True` | `0.0` |
| `sample_05` | `1.25` | `0.75` | `left_true_right_true_return_sum` | `True` | `2.0` |
| `sample_06` | `-0.5` | `-0.5` | `left_false_short_circuit_return_zero` | `False` | `0.0` |

## Boundary

- Expected samples only; no compound-condition execution.
- No short-circuit or boolean-normalization policy is applied.
- No compound-condition lowering or support claim.
- No frontend lowering change.
- No branch re-ingest, full source roundtrip, arbitrary source-family, compiler-correctness, formal-equivalence, or runtime-performance claim.
