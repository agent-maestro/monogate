# FEF-P99 Loop Re-ingest Policy

Date: 2026-05-31

Status: `FEF_P99_LOOP_REINGEST_POLICY_PASS`

Decision: `selected_loop_reingest_policy_recorded_execution_blocked`

FEF-P99 records selected loop re-ingest policy without executing re-ingest.

## Summary

- Selected fixture: `c_while_accumulate_v0`
- Policy id: `selected_c_while_accumulate_loop_reingest_policy_v0`
- Policy status: `policy_recorded_execution_blocked`
- Policy scope: `selected_generated_c_loop_fixture_only`
- Required accepted surfaces: `4`
- Required rejected surfaces: `5`
- Required execution gate steps: `7`
- Required comparison rows: `7`
- Policy validation pass count: `9`
- Policy validation fail count: `0`
- Re-ingest executed: `False`
- Loop re-ingest supported: `False`
- Compiler behavior changed: `False`

## Accepted Surface

- `static_helper_loop_effective_iterations`: `static int mg_loop_effective_iterations(int n)`
- `selected_generated_loop_function`: `double c_while_accumulate_v0_generated_fixture(double x, int n)`
- `selected_effective_iteration_binding`: `int k = mg_loop_effective_iterations(n);`
- `selected_closed_form_loop_return`: `return x * (double)k;`

## Rejected Surface

- `arbitrary_while_loop`: Reject arbitrary while-loop syntax outside the selected generated closed-form fixture.
- `arbitrary_for_loop`: Reject arbitrary for-loop syntax outside the selected generated closed-form fixture.
- `side_effect_loop_body`: Reject loops with function calls, mutation beyond selected locals, volatile reads, or observable side effects.
- `unbounded_or_data_dependent_backedge`: Reject back edges without the selected P92 boundedness policy and effective-iteration cap.
- `helper_runtime_import`: Reject claims that the loop helper is installed globally in Forge/eFrog runtime packages.

## Policy Validation Rows

| Surface | Kind | Pass | Re-ingest Executed |
|---|---|---|---|
| `static_helper_loop_effective_iterations` | `required_accept` | `True` | `False` |
| `selected_generated_loop_function` | `required_accept` | `True` | `False` |
| `selected_effective_iteration_binding` | `required_accept` | `True` | `False` |
| `selected_closed_form_loop_return` | `required_accept` | `True` | `False` |
| `arbitrary_while_loop` | `required_reject` | `True` | `False` |
| `arbitrary_for_loop` | `required_reject` | `True` | `False` |
| `side_effect_loop_body` | `required_reject` | `True` | `False` |
| `unbounded_or_data_dependent_backedge` | `required_reject` | `True` | `False` |
| `helper_runtime_import` | `required_reject` | `True` | `False` |

## Boundary

- Selected loop re-ingest policy only.
- No eFrog re-ingest execution.
- No Forge/eFrog behavior change or loop lowering installation.
- No loop/back-edge support claim.
- No compiler-correctness, formal-equivalence, or runtime-performance claim.
