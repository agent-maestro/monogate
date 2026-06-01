# FEF-P93 Loop Reference Runtime Gate

Date: 2026-05-31

Status: `FEF_P93_LOOP_REFERENCE_RUNTIME_GATE_PASS`

Decision: `loop_reference_runtime_gate_recorded_support_blocked`

FEF-P93 runs a local reference evaluator over selected loop samples under the P92 policy.

## Summary

- Selected fixture: `c_while_accumulate_v0`
- Comparisons: `7`
- Pass count: `7`
- Fail count: `0`
- Max absolute error: `0.0`
- Max iteration count: `8`
- Total back-edge taken count: `21`
- Reference runtime only: `True`
- Original source executed: `False`
- Generated target executed: `False`
- Re-ingested target executed: `False`

## Rows

| Sample | x | n | Expected | Observed | Abs Error | Pass |
|---|---:|---:|---:|---:|---:|---|
| `sample_00` | 2.0 | 0 | 0.0 | 0.0 | 0.0 | `True` |
| `sample_01` | 2.0 | 1 | 2.0 | 2.0 | 0.0 | `True` |
| `sample_02` | 2.0 | 3 | 6.0 | 6.0 | 0.0 | `True` |
| `sample_03` | -1.5 | 4 | -6.0 | -6.0 | 0.0 | `True` |
| `sample_04` | 0.0 | 5 | 0.0 | 0.0 | 0.0 | `True` |
| `sample_05` | 3.0 | -2 | 0.0 | 0.0 | 0.0 | `True` |
| `sample_06` | 0.25 | 8 | 2.0 | 2.0 | 0.0 | `True` |

## Boundary

- Reference runtime table consistency only.
- No original C, generated target, or re-ingested execution.
- No loop lowering or loop/back-edge support claim.
- No general boundedness policy claim.
- No frontend lowering change.
- No compiler-correctness, formal-equivalence, or runtime-performance claim.
