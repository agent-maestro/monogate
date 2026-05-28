# RH-A2 Reviewer Priority Queue

Date: 2026-05-27

Status: `RH_A2_REVIEWER_PRIORITY_QUEUE_PASS`

RH-A2 ranks RH-A1 claim review packets into a private reviewer queue.

## Queue

| Rank | Claim | Priority | Score | Next sprint | Next validator |
|---:|---|---|---:|---|---|
| 1 | `electronics-voltage-divider-hardware-observed` | `high` | 65 | `EE-A2 live capture packet` | `live_capture_packet` |
| 2 | `eml-softplus-general-speed-claim` | `medium` | 52 | `R10D implementation benchmark` | `holdout_runtime_bakeoff` |
| 3 | `r11-compiler-lowering-correctness` | `medium` | 48 | `R10F proof-assistant AST and guard model` | `proof_assistant_ast_model` |
| 4 | `pm-a1-profitable-agent-claim` | `medium` | 44 | `PM-A1C outcome resolver fixture` | `outcome_resolution_ledger` |
| 5 | `builder-robust-to-forbidden-claim-injection` | `medium` | 40 | `RT-A2 local RAMPART adapter` | `rampart_redteam_packet` |
| 6 | `machlib-subtraction-boundary-witness` | `low` | 29 | `Atlas bounded public surfacing` | `machlib_lake_build` |
| 7 | `ai-answer-ready-for-publication` | `low` | 28 | `PB-A2 sourced AI answer intake` | `source_attribution` |
| 8 | `r12-generated-stubs-validate-on-fixtures` | `low` | 28 | `R10F proof-assistant AST and guard model` | `proof_assistant_ast_model` |
| 9 | `command-cockpit-robust-to-private-leakage` | `low` | 26 | `RT-A3 red-team regression CI guard` | `adapter_coverage_review` |
| 10 | `oph-correct-theory-of-everything-claim` | `low` | 23 | `X1 external theory claim decomposition` | `claim_decomposition` |

## Summary

- Queue items: `10`
- Top claim: `electronics-voltage-divider-hardware-observed`
- Top sprint: `EE-A2 live capture packet`
- Public approval performed: `False`
- Deploy performed: `False`
- Trade performed: `False`
- Hardware action performed: `False`
- Compiler behavior changed: `False`

## Boundary

- Private planning queue only.
- No automatic reviewer approval.
- No deployment, trading, hardware operation, or compiler behavior change.
