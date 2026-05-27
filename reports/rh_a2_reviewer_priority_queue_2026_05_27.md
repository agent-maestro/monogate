# RH-A2 Reviewer Priority Queue

Date: 2026-05-27

Status: `RH_A2_REVIEWER_PRIORITY_QUEUE_PASS`

RH-A2 ranks RH-A1 claim review packets into a private reviewer queue.

## Queue

| Rank | Claim | Priority | Score | Next sprint | Next validator |
|---:|---|---|---:|---|---|
| 1 | `r11-compiler-lowering-correctness` | `high` | 78 | `R12 generated lowering stubs` | `generated_stub_validation` |
| 2 | `command-cockpit-robust-to-private-leakage` | `high` | 72 | `RT-A2 local RAMPART adapter` | `rampart_redteam_packet` |
| 3 | `pm-a1-profitable-agent-claim` | `high` | 68 | `PM-A1B calibration ledger` | `pm_a1_forecast_packet` |
| 4 | `electronics-voltage-divider-hardware-observed` | `high` | 65 | `EE-A2 live capture packet` | `live_capture_packet` |
| 5 | `eml-softplus-general-speed-claim` | `high` | 64 | `R10B runtime bakeoff` | `r10_cost_stability` |
| 6 | `builder-robust-to-forbidden-claim-injection` | `medium` | 40 | `RT-A2 local RAMPART adapter` | `rampart_redteam_packet` |
| 7 | `machlib-subtraction-boundary-witness` | `low` | 29 | `Atlas bounded public surfacing` | `machlib_lake_build` |
| 8 | `ai-answer-ready-for-publication` | `low` | 28 | `PB-A2 sourced AI answer intake` | `source_attribution` |
| 9 | `oph-correct-theory-of-everything-claim` | `low` | 23 | `X1 external theory claim decomposition` | `claim_decomposition` |

## Summary

- Queue items: `9`
- Top claim: `r11-compiler-lowering-correctness`
- Top sprint: `R12 generated lowering stubs`
- Public approval performed: `False`
- Deploy performed: `False`
- Trade performed: `False`
- Hardware action performed: `False`
- Compiler behavior changed: `False`

## Boundary

- Private planning queue only.
- No automatic reviewer approval.
- No deployment, trading, hardware operation, or compiler behavior change.
