# ACT-A5 Negative Rejection Fixtures

Status: `ACT_A5_NEGATIVE_REJECTION_FIXTURES_PASS`

ACT-A5 records synthetic alpha/gamma rejection fixtures without implementing a production validator.

| Count | Value |
|---|---|
| negative fixtures | `5` |
| rejection checks | `5` |
| expected rejects | `5` |
| unexpected accepts | `0` |

## Failure Modes

- `claim_escalation`
- `trace_gap`
- `public_gate_bypass`
- `runtime_drift`
- `lane_owner_drift`

## Non-Claims

- ACT-A5 records synthetic negative/rejection fixtures only; it is not a production alpha/gamma validator.
- ACT-A5 expected rejections exercise claim escalation, trace gaps, public gate bypass, runtime drift, and lane-owner drift without proving validator soundness, a Galois connection, abstract interpretation correctness, compiler correctness, formal equivalence, or full EML semantics.
- ACT-A5 does not update public surfaces, runtime behavior, MachLib, visualization tooling, laptop-owned repos, or electronics repos.
