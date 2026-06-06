# PROD-A2 Training Cost Estimator Private Spec

Status: `PROD_A2_TRAINING_COST_ESTIMATOR_PRIVATE_SPEC_PASS`

PROD-A2 defines a private advisory specification for a training cost estimator.
It does not implement or execute an estimator.

## Supported Inputs

| Input | Status | Boundary |
|---|---|---|
| `sympy_expression_or_expression_list` | `supported_for_static_cost_shape_spec` | Static expression cost shape only; no runtime measurement or training outcome prediction. |
| `torch_fx_graph_summary` | `supported_for_private_profiler_spec` | Profiler-shape input only; no guarantee that traced graph captures all runtime work. |
| `training_loop_metadata` | `supported_for_budget_context_spec` | Budget-context metadata only; no claim that training dynamics, convergence, or data pipeline cost are fully modeled. |
| `manual_operation_count_packet` | `supported_for_reviewer_supplied_estimate_spec` | Reviewer-supplied rows must remain labeled as supplied estimates, not measured truth. |

## Output Fields

| Field | Type | Meaning |
|---|---|---|
| `estimate_id` | `string` | Stable identifier for the private estimate packet. |
| `input_summary` | `object` | Compact description of accepted inputs and missing optional context. |
| `static_expression_cost` | `object|null` | Expression-level cost profile when symbolic expressions are supplied. |
| `graph_cost_profile` | `object|null` | Layer/node-level profile when graph-summary input is supplied. |
| `training_budget_context` | `object|null` | Epoch/batch/parameter context used to scale a private advisory estimate. |
| `calibration_caveats` | `array[string]` | Required caveats attached to the estimate. |
| `blocked_claims` | `array[string]` | Claims that the estimate must not imply. |
| `reviewer_next_steps` | `array[string]` | Private reviewer actions before implementation or public copy. |

## Calibration Caveats

- `not_wall_clock_runtime`: The estimate is not a wall-clock runtime benchmark.
- `not_training_savings`: The estimate does not claim lower cost, lower spend, or faster training.
- `hardware_context_missing`: Hardware, kernel fusion, memory bandwidth, dataloader, and compiler effects may dominate real runtime.
- `model_quality_out_of_scope`: The estimate says nothing about accuracy, convergence, stability, or scientific validity.
- `calibration_required`: Any numeric estimator implementation must later carry calibration source, version, and residual/error notes.

## Blocked Claims

- training cost savings
- estimator accuracy
- wall-clock runtime performance
- model quality improvement
- scientific correctness
- compiler correctness
- semantic preservation
- public product readiness
- SDK stability
- hardware readiness
- silicon readiness
- broad EML advantage

## Summary

- source artifact: `prod-a1-private-product-evidence-surface-seed`
- selected lane: `training_cost_estimator`
- next recommended artifact: `PROD-A3 training cost estimator schema validator or example packet selector`
- estimator implemented: `False`
- training savings claim: `False`
- runtime performance claim: `False`

## Non-Claims

- PROD-A2 is a private specification for a training cost estimator; it does not implement or execute an estimator.
- PROD-A2 defines supported inputs, output fields, calibration caveats, example boundaries, and blocked claims only.
- PROD-A2 does not claim training savings, estimator accuracy, runtime performance, model-quality improvement, compiler correctness, semantic preservation, public product readiness, hardware readiness, silicon readiness, reviewer approval, or broad EML advantage.
- PROD-A2 respects the D109 hold and does not start D110 or consume a reviewer response.
