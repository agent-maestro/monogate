# FEF-P71 Compound-Condition Expected Samples

Date: 2026-05-31

Status: `FEF_P71_COMPOUND_CONDITION_EXPECTED_SAMPLES_PASS`

Decision: `compound_condition_expected_samples_recorded_support_blocked`

FEF-P71 attaches deterministic expected samples to one blocked compound-condition fixture.

## Summary

- Selected fixture: `c_and_short_circuit_guard_v0`
- Selected fixture still blocked: `True`
- Samples: `7`
- True-division samples: `3`
- Left-false short-circuit samples: `3`
- Right-false guard samples: `1`
- Right condition evaluations: `4`
- Division performed samples: `3`
- Source semantics only: `True`
- Compound-condition runtime execution claim: `False`
- Compound-condition lowering claim: `False`
- Compound-condition support claim: `False`

## Samples

| Sample | x | y | Path | Right eval | Division | Expected |
|---|---:|---:|---|---|---|---:|
| `sample_00` | 2.0 | 4.0 | `and_true_division` | `True` | `True` | 0.5 |
| `sample_01` | -2.0 | 0.0 | `left_false_short_circuit` | `False` | `False` | 0.0 |
| `sample_02` | 0.0 | 5.0 | `left_false_short_circuit` | `False` | `False` | 0.0 |
| `sample_03` | 3.0 | 0.0 | `right_false_zero_denominator_guard` | `True` | `False` | 0.0 |
| `sample_04` | 1.5 | -0.5 | `and_true_division` | `True` | `True` | -3.0 |
| `sample_05` | -1.0 | -2.0 | `left_false_short_circuit` | `False` | `False` | 0.0 |
| `sample_06` | 5.0 | 2.0 | `and_true_division` | `True` | `True` | 2.5 |

## Boundary

- Expected samples only; no compound-condition execution.
- No short-circuit implementation, lowering, or support claim.
- No frontend lowering change.
- No branch re-ingest, full source roundtrip, arbitrary source-family, compiler-correctness, formal-equivalence, or runtime-performance claim.
