# FEF-P96 Loop Lowering Rule Packet

Date: 2026-05-31

Status: `FEF_P96_LOOP_LOWERING_RULE_PACKET_PASS`

Decision: `selected_loop_lowering_rule_recorded_runtime_blocked`

FEF-P96 records a selected loop lowering rule shape without changing compiler behavior.

## Summary

- Selected fixture: `c_while_accumulate_v0`
- Lowering rule status: `candidate_rule_recorded_runtime_blocked`
- Lowering rule scope: `selected_fixture_only_under_p92_policy`
- Semantic requirements: `5`
- Rejected surfaces: `5`
- Rule validation samples: `7`
- Rule validation pass count: `7`
- Rule validation fail count: `0`
- Rule validation max absolute error: `0.0`
- Max effective iteration count: `8`
- Compiler behavior changed: `False`
- Frontend lowering changed: `False`
- Loop lowering implemented: `False`
- Generated target executed: `False`

## Semantic Requirements

- loop bound n is integer-like for the selected fixture samples
- effective iteration count is max(0, int(n))
- effective iteration count is bounded by the P92 cap
- loop body has no side effects outside local acc/i mutation
- accumulator update is affine: acc_next = acc + x

## Rejected Surfaces

- `unknown_or_symbolic_loop_bound`
- `iteration_count_above_limit`
- `non_finite_numeric_input`
- `side_effecting_loop_body`
- `nested_or_unstructured_loop`

## Rule Validation

| Sample | Path | Effective Iterations | Expected | Rule Value | Abs Error | Pass |
|---|---|---:|---:|---:|---:|---|
| `sample_00` | `zero_iterations` | 0 | 0.0 | 0.0 | 0.0 | `True` |
| `sample_01` | `single_iteration` | 1 | 2.0 | 2.0 | 0.0 | `True` |
| `sample_02` | `multi_iteration` | 3 | 6.0 | 6.0 | 0.0 | `True` |
| `sample_03` | `multi_iteration` | 4 | -6.0 | -6.0 | 0.0 | `True` |
| `sample_04` | `multi_iteration` | 5 | 0.0 | 0.0 | 0.0 | `True` |
| `sample_05` | `zero_iterations` | 0 | 0.0 | 0.0 | 0.0 | `True` |
| `sample_06` | `multi_iteration` | 8 | 2.0 | 2.0 | 0.0 | `True` |

## Boundary

- Selected lowering-rule packet only.
- No Forge/eFrog behavior change.
- No generated target or re-ingested target execution.
- No loop/back-edge support claim.
- No compiler-correctness, formal-equivalence, or runtime-performance claim.
