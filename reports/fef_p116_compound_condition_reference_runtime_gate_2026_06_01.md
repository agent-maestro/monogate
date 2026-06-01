# FEF-P116 Compound-Condition Reference Runtime Gate

Date: 2026-06-01

Status: `FEF_P116_COMPOUND_CONDITION_REFERENCE_RUNTIME_GATE_PASS`

Decision: `compound_condition_reference_runtime_gate_recorded_support_blocked`

FEF-P116 runs a modeled local reference evaluator for selected compound-condition samples.

## Summary

- Selected fixture: `c_and_guard_return_v0`
- Comparison count: `7`
- Pass count: `7`
- Fail count: `0`
- Right predicate evaluated rows: `4`
- Short-circuit rows: `3`
- Max absolute error: `0.0`
- Reference runtime only: `True`
- Original source executed: `False`
- Generated target executed: `False`
- Re-ingested target executed: `False`
- Compound-condition support claim: `False`

## Comparisons

| Sample | Path | Expected | Observed | Right Evaluated | Pass |
|---|---|---:|---:|---|---|
| `sample_00` | `left_true_right_true_return_sum` | `5.0` | `5.0` | `True` | `True` |
| `sample_01` | `left_true_right_false_return_zero` | `0.0` | `0.0` | `True` | `True` |
| `sample_02` | `left_false_short_circuit_return_zero` | `0.0` | `0.0` | `False` | `True` |
| `sample_03` | `left_false_short_circuit_return_zero` | `0.0` | `0.0` | `False` | `True` |
| `sample_04` | `left_true_right_false_return_zero` | `0.0` | `0.0` | `True` | `True` |
| `sample_05` | `left_true_right_true_return_sum` | `2.0` | `2.0` | `True` | `True` |
| `sample_06` | `left_false_short_circuit_return_zero` | `0.0` | `0.0` | `False` | `True` |

## Boundary

- Reference-runtime table consistency only.
- No original C compound-condition source execution.
- No generated target or re-ingested target execution.
- No applied short-circuit or boolean-normalization policy.
- No compound-condition lowering or support claim.
- No compiler-correctness, formal-equivalence, or runtime-performance claim.
