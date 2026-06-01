# FEF-P117 Compound-Condition Original C Runtime Gate

Date: 2026-06-01

Status: `FEF_P117_COMPOUND_CONDITION_ORIGINAL_C_RUNTIME_GATE_PASS`

Decision: `compound_condition_original_c_runtime_recorded_support_blocked`

FEF-P117 compiles and runs the selected original C compound-condition fixture against the P114 expected samples.

## Summary

- Selected fixture: `c_and_guard_return_v0`
- Selected fixture still blocked: `True`
- Comparisons: `7`
- Pass count: `7`
- Fail count: `0`
- Right predicate evaluated rows: `4`
- Short-circuit rows: `3`
- Max absolute error: `0.0`
- Original C source executed: `True`
- Generated target executed: `False`
- Re-ingested target executed: `False`
- Compound-condition lowering implemented: `False`
- Compound-condition support claim: `False`

## Comparisons

| Sample | x | y | Expected | Observed | Abs Error | Pass |
|---|---:|---:|---:|---:|---:|---|
| `sample_00` | 2.0 | 3.0 | 5.0 | 5.0 | 0.0 | `True` |
| `sample_01` | 2.0 | -1.0 | 0.0 | 0.0 | 0.0 | `True` |
| `sample_02` | -2.0 | 3.0 | 0.0 | 0.0 | 0.0 | `True` |
| `sample_03` | 0.0 | 3.0 | 0.0 | 0.0 | 0.0 | `True` |
| `sample_04` | 2.0 | 0.0 | 0.0 | 0.0 | 0.0 | `True` |
| `sample_05` | 1.25 | 0.75 | 2.0 | 2.0 | 0.0 | `True` |
| `sample_06` | -0.5 | -0.5 | 0.0 | 0.0 | 0.0 | `True` |

## Boundary

- Selected original C runtime evidence only.
- No generated target or re-ingested target execution.
- No compound-condition lowering or support claim.
- No frontend lowering change.
- No branch re-ingest, full source roundtrip, arbitrary source-family, compiler-correctness, formal-equivalence, or runtime-performance claim.
