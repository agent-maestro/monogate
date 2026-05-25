# EML IR Substrate Pipeline v0

Date: 2026-05-25

Status: `EML_IR_SUBSTRATE_PIPELINE_READY`

This pass does not recreate the EML substrate work from scratch. It connects existing SuperBEST DAG lowering to an explicit EML IR shape and a replay packet shape.

## Existing Work Reused

- `reused_superbest_dag_lowering`: `python/scripts/superbest_dag_lowering.py`
- `reused_superbest_frontier`: `python/scripts/superbest_expression_frontier.py`
- `related_research_rfc`: `monogate-research/rfcs/eml_kernel_contract_v0`
- `related_replay_runtime`: `monogate-research/exploration/monogate_os_replay_frame_runtime_v0_2026_05_24`
- `related_engine_eml`: `monogate-engine/docs/book/src/architecture-eml.md`

## Program Summary

| Program | Family | Tree BEST | DAG BEST | Extra DAG Savings | Frames |
|---|---|---:|---:|---:|---:|
| `sigmoid_v0` | sigmoid_logistic | 7 | 7 | 0 | 8 |
| `sigmoid_value_and_derivative_v0` | sigmoid_logistic | 26 | 12 | 14 | 11 |
| `softmax_denominator_3_v0` | softmax_attention | 7 | 7 | 0 | 9 |
| `attention_three_logits_three_outputs_v0` | softmax_attention | 46 | 20 | 26 | 17 |
| `rational_shared_denominator_v0` | rational_shared_denominator | 22 | 16 | 6 | 13 |
| `polynomial_basis_degree5_v0` | polynomial_basis_reuse | 16 | 10 | 6 | 11 |
| `voltage_divider_v0` | trainer_board_math | 5 | 5 | 0 | 7 |
| `threshold_reflex_target_v0` | trainer_board_math | 6 | 6 | 0 | 7 |
| `gaussian_v0` | forge_efrog_fixture | 4 | 4 | 0 | 7 |
| `log_sum_exp_pair_v0` | softplus_logsumexp | 5 | 5 | 0 | 8 |

## What This Unlocks

- A canonical JSON shape for EML expressions as inspectable DAG programs.
- SuperBEST Tree vs DAG costs on the same artifact.
- Replay-native frames over expression nodes.
- A bridge to future browser inspector and Monogate OS packet tooling.

## Boundaries

- Internal prototype only.
- No Forge/compiler behavior changed.
- No canonical SuperBEST row table changed.
- No new public theorem/proof/open-problem claim.
- No package publish or deploy.
