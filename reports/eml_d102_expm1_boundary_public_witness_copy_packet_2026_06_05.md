# EML-D102 Expm1 Boundary Public-Witness Copy Packet

Status: `EML_D102_EXPM1_BOUNDARY_PUBLIC_WITNESS_COPY_PACKET_PASS`

D102 drafts private review copy for one checked expm1-boundary witness and keeps publication blocked.

## Summary

- witness: `MachLib.Real.expm1_boundary_identity_witness`
- statement: `eml x (exp 1) = exp x - 1`
- guard summary: `no extra real-domain guard recorded`
- runtime control: `protected_expm1_remains_runtime_control`
- public copy drafted for review: `True`
- public copy approved: `False`
- public page created: `False`

## Private Draft Markdown

# One Checked MachLib Witness: expm1 Boundary

This private draft describes one narrow checked witness from MachLib. It is not a
public announcement, not a library overview, and not an approval to publish.

## Original EML-Shaped Statement

```text
eml x (exp 1) = exp x - 1
```

## Checked Lean / MachLib Witness

```text
MachLib.Real.expm1_boundary_identity_witness
```

Checked statement:

```text
eml x (exp 1) = exp x - 1
```

## Guards / Domain Conditions

```text
no extra real-domain guard recorded
```

## Plain-English Reading

This witness records that, inside this scoped MachLib statement, the EML-shaped
expression `eml x (exp 1)` matches the boundary identity `exp x - 1`.

The artifact is useful because it gives reviewers one exact theorem name, one
exact statement, and one exact runtime boundary to inspect. Protected `expm1`
remains the runtime and numerical-stability control.

## Claim Boundaries

What is being claimed:

- One named MachLib witness exists for the statement above.
- This packet preserves the exact checked statement and the recorded guard
  summary.
- The packet is suitable for private review as a candidate public-witness page.

What is not being claimed:

- No public copy is approved.
- No public page or Atlas row has been published.
- No EML advantage is claimed.
- No runtime performance claim is made.
- No compiler correctness claim is made.
- No formal equivalence claim is made.
- No full EML semantics claim is made.
- No claim is made that EML replaces protected `expm1`.
- No claim is made that this witness covers all expm1 identities.
- No public readiness claim is made.


## Non-Claims

- EML-D102 drafts a private review packet for one checked witness; it does not approve, publish, or create public copy.
- D102 preserves protected expm1 as the runtime and numerical-stability control; it does not claim EML replaces expm1.
- D102 does not edit MachLib, typecheck Lean, start proof work, change runtime lowering, add Advantage Lab cases, create SDK/compiler docs, create course material, consume laptop artifacts, touch laptop-owned repos, or claim theorem discovery, runtime performance, compiler correctness, formal equivalence, catalog completeness, public readiness, full EML semantics, or broad EML advantage.
