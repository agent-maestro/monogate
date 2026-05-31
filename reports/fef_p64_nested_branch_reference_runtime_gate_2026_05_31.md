# FEF-P64 Nested Branch Reference Runtime Gate

Date: 2026-05-31

Status: `FEF_P64_NESTED_BRANCH_REFERENCE_RUNTIME_GATE_PASS`

Decision: `nested_branch_reference_runtime_gate_recorded_support_blocked`

FEF-P64 compares the P63 expected samples against a local Python reference evaluator.

## Summary

- Selected fixture: `c_nested_if_return_v0`
- Selected fixture still blocked: `True`
- Comparisons: `7`
- Pass count: `7`
- Fail count: `0`
- Max absolute error: `0.0`
- Reference runtime only: `True`
- Original/generated code executed: `False`
- Nested branch source execution claim: `False`
- Nested branch lowering claim: `False`
- Nested branch support claim: `False`

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

- Reference-runtime table consistency only.
- No original C nested branch source execution.
- No generated target or re-ingested target execution.
- No nested branch lowering or support claim.
- No frontend lowering change.
- No branch re-ingest, full source roundtrip, arbitrary source-family, compiler-correctness, formal-equivalence, or runtime-performance claim.
