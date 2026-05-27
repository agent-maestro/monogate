# RT-A2 Local RAMPART Adapter

Date: 2026-05-27

RT-A2 is the first local red-team adapter run for the private command cockpit
boundary. It uses RAMPART-shaped scenarios against a deterministic fake adapter
and emits Monogate red-team evidence packets.

It does not execute the external RAMPART package, call live models, read API
keys, inspect environment secrets, deploy, trade, operate hardware, or claim
certified safety.

## Adapter Boundary

The fake adapter accepts a prompt and returns a public-safe command-cockpit
summary. It refuses attempts to:

- reveal private reviewer notes
- mark public/deploy/safety claim flags true
- exfiltrate API keys or environment secrets
- authorize autonomous trading or order placement

## Scenario Set

RT-A2 covers:

- private reviewer leakage
- public deployment approval injection
- secret/token exfiltration
- autonomous trading permission injection
- benign public-safe status request

## Result

The 2026-05-27 run generated five red-team packets. All five passed the local
adapter evaluator. The result is candidate robustness evidence only.

The RH-A1 command-cockpit leakage claim now moves from adapter-missing failure
to candidate-only local red-team evidence. RH-A2 therefore advances the top
queue item to PM-A1B calibration ledger.

## Non-Claims

- No certified safety claim.
- No comprehensive robustness claim.
- No production security claim.
- No external RAMPART execution claim.
- No live model or secret handling claim.
- No public deployment approval.
