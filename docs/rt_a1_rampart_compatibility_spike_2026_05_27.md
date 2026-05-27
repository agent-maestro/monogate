# RT-A1 RAMPART Compatibility Spike

Date: 2026-05-27

## Purpose

RT-A1 tests whether Monogate can ingest RAMPART-style red-team outcomes as
evidence artifacts.

RAMPART-style role:

```text
agent behavior
-> adversarial probe
-> observed outcome
-> evaluator verdict
-> structured result
```

Monogate role:

```text
structured red-team result
-> evidence packet
-> RH-A1 claim review packet
-> blocked claim or bounded candidate
```

## Boundary

RT-A1 is fixture-first. It does not install or execute RAMPART, call live
models, use API keys, run private agents, deploy, or publish results.

The RAMPART project is treated as an external red-team framework whose outputs
could later be converted into Monogate evidence packets. RT-A1 only defines and
tests the compatibility shape.

## Fixture Categories

- Forbidden claim flag injection against the Evidence Packet Builder.
- Financial advice / autonomous trading pressure against PM-A1.
- External theory overclaim pressure against OPH-style claims.
- Private command cockpit leakage pressure.

## Claim Rule

Passing red-team fixtures may support candidate robustness claims only.
Failing red-team fixtures must block public robustness claims and route the
next validator.

RT-A1 never claims certified safety, production security, or comprehensive
agent robustness.
