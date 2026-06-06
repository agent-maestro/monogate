# PROD-A4 Training Cost Estimator Schema Validator Contract

Status: `PROD_A4_TRAINING_COST_ESTIMATOR_SCHEMA_VALIDATOR_CONTRACT_PASS`

PROD-A4 defines private validation obligations for future training-cost estimate packets.
It does not implement or execute a validator.

## Required Fields

| Field | Type | Required |
|---|---|---|
| `estimate_id` | `string` | `True` |
| `input_summary` | `object` | `True` |
| `static_expression_cost` | `object|null` | `True` |
| `graph_cost_profile` | `object|null` | `True` |
| `training_budget_context` | `object|null` | `True` |
| `calibration_caveats` | `array[string]` | `True` |
| `blocked_claims` | `array[string]` | `True` |
| `reviewer_next_steps` | `array[string]` | `True` |

## Validation Obligations

| Obligation | Severity | Description |
|---|---|---|
| `required_fields_present` | `reject_if_missing` | All eight PROD-A2 output fields must be present even when nullable fields are null. |
| `at_least_one_cost_view_present` | `reject_if_absent` | At least one of static_expression_cost, graph_cost_profile, or training_budget_context must be non-null. |
| `calibration_caveats_required` | `reject_if_missing` | Packet must include not-wall-clock, not-savings, hardware-context, model-quality, and calibration-required caveats. |
| `blocked_claims_required` | `reject_if_missing` | Packet must carry blocked claims for savings, accuracy, runtime, model quality, compiler correctness, public readiness, hardware readiness, and broad EML advantage. |
| `reviewer_next_steps_required` | `reject_if_empty` | Packet must provide private reviewer next steps before implementation or public copy. |
| `no_public_or_performance_flags_true` | `reject_if_true` | Packet must not set public readiness, training savings, estimator accuracy, runtime performance, or broad EML advantage flags true. |

## Rejection Fixtures

- `missing_blocked_claims`: A packet without blocked_claims can be mistaken for public product copy.
- `missing_calibration_caveats`: A packet without calibration caveats can be mistaken for measured runtime truth.
- `all_cost_views_null`: A packet with no cost view has no estimate surface to review.
- `training_savings_true`: A savings claim is explicitly blocked by PROD-A2.
- `public_product_ready_true`: Public readiness requires separate review and approval.

## Non-Claims

- PROD-A4 is a private schema validator contract; it does not implement or execute a validator.
- PROD-A4 records validation obligations and rejection fixtures for future training-cost estimate packets.
- PROD-A4 does not implement or execute an estimator, create examples, run model training, run benchmarks, or claim training savings, estimator accuracy, runtime performance, public readiness, compiler correctness, semantic preservation, hardware readiness, silicon readiness, reviewer approval, or broad EML advantage.
- PROD-A4 respects the D109 hold and does not start D110 or consume a reviewer response.
