# PM-A1B Calibration Ledger

Date: 2026-05-27

PM-A1B converts the PM-A1 read-only forecast packets into a scoring-ready
calibration ledger.

The purpose is narrow: preserve every forecast probability, market price,
resolution source, probability bucket, edge bucket, and future scoring slot so
resolved outcomes can later be attached without changing the packet grammar.

## Result

The 2026-05-27 run created four ledger entries, one for each PM-A1 fixture
market.

All four entries are pending resolution. Brier score and log loss are null for
every entry because no outcome evidence has been attached.

## What Changed

RH-A1 now treats the prediction-market profitability claim as
`calibration_ready_no_outcomes`.

RH-A2 now routes that claim to `PM-A1C outcome resolver fixture` instead of
asking for another calibration ledger.

## Non-Claims

- No financial advice.
- No profitable strategy claim.
- No calibrated forecaster claim.
- No order placement.
- No authenticated trading.
- No live market ingestion.
- No outcome scoring before resolution evidence exists.
