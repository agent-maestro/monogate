# EML IR Inspector v0

Date: 2026-05-25

Status: `EML_IR_INSPECTOR_READY`

This is the first local viewer packet for EML IR as inspectable bytecode. It turns the existing expression -> DAG -> replay pipeline into a static browser artifact.

## Summary

- Programs: 10
- Total replay frames: 98
- Best internal prototype savings fixture: `attention_three_logits_three_outputs_v0`
- Extra DAG savings for best fixture: 26 SuperBEST nodes

## Program Table

| Program | Family | Tree BEST | DAG BEST | Extra DAG Savings | Reused Nodes | Frames |
|---|---|---:|---:|---:|---:|---:|
| `sigmoid_v0` | sigmoid_logistic | 7 | 7 | 0 | 1 | 8 |
| `sigmoid_value_and_derivative_v0` | sigmoid_logistic | 26 | 12 | 14 | 6 | 11 |
| `softmax_denominator_3_v0` | softmax_attention | 7 | 7 | 0 | 0 | 9 |
| `attention_three_logits_three_outputs_v0` | softmax_attention | 46 | 20 | 26 | 12 | 17 |
| `rational_shared_denominator_v0` | rational_shared_denominator | 22 | 16 | 6 | 3 | 13 |
| `polynomial_basis_degree5_v0` | polynomial_basis_reuse | 16 | 10 | 6 | 3 | 11 |
| `voltage_divider_v0` | trainer_board_math | 5 | 5 | 0 | 1 | 7 |
| `threshold_reflex_target_v0` | trainer_board_math | 6 | 6 | 0 | 0 | 7 |
| `gaussian_v0` | forge_efrog_fixture | 4 | 4 | 0 | 1 | 7 |
| `log_sum_exp_pair_v0` | softplus_logsumexp | 5 | 5 | 0 | 0 | 8 |

## What The Inspector Shows

- Expression source and family.
- IR DAG node cards and dependency edges.
- Reused subexpressions and why they matter.
- Replay timeline with lifecycle states, guard annotations, and hash neighborhoods.
- Lowered Python and JavaScript sketches from the existing lowering pass.

## Public Copy Boundary

Tree SuperBEST costs remain the public-safe baseline. DAG/IR savings in this packet are internal prototype evidence and should not become public headline claims until the lowering contract and product surface are reviewed.

## Files

- `demo/eml_ir_inspector_v0_2026_05_25/index.html`
- `demo/eml_ir_inspector_v0_2026_05_25/inspector_model_2026_05_25.json`
- `demo/eml_ir_inspector_v0_2026_05_25/observatory_card_2026_05_25.json`
- `demo/eml_ir_inspector_v0_2026_05_25/action_queue_2026_05_25.json`

## Boundaries

- Internal local static viewer only.
- No deploy.
- No package publish.
- No compiler behavior changed.
- No canonical SuperBEST row table changed.
- No production marketplace modification.
- No public theorem/proof/open-problem claim.
