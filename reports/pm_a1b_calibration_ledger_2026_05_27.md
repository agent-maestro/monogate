# PM-A1B Prediction Market Calibration Ledger

Date: 2026-05-27

Status: `PM_A1B_CALIBRATION_LEDGER_PASS`

PM-A1B converts read-only forecast packets into a scoring-ready
calibration ledger. Outcomes are pending unless explicit resolution
evidence is attached.

## Ledger Entries

| Market | Probability | Market price | Bucket | Outcome | Brier | Log loss |
|---|---:|---:|---|---|---:|---:|
| `kalshi-cpi-jun-2026-under-3` | 0.4936 | 0.4600 | `0.4-0.5` | `pending_resolution` | null | null |
| `polymarket-spot-eth-etf-weekly-inflow` | 0.5836 | 0.6200 | `0.5-0.6` | `pending_resolution` | null | null |
| `kalshi-fed-hold-next-meeting` | 0.7107 | 0.7100 | `0.7-0.8` | `pending_resolution` | null | null |
| `polymarket-ai-model-release-by-july` | 0.3894 | 0.3900 | `0.3-0.4` | `pending_resolution` | null | null |

## Summary

- Ledger entries: `4`
- Pending resolution: `4`
- Resolved: `0`
- Scored: `0`
- Order placement performed: `False`
- Authenticated trading used: `False`
- Calibrated forecaster claim: `False`

## Boundary

- No financial advice.
- No profitable strategy claim.
- No calibrated-skill claim.
- No order placement or authenticated trading.
- No Brier/log-loss scoring until outcomes are resolved.
