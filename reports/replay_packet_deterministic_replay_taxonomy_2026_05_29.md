# Replay Packet vs Deterministic Replay Taxonomy

Date: 2026-05-29

Status: private taxonomy. This is not a deterministic OS claim.

## Why This Exists

Monogate uses replay in multiple lanes. The word is useful, but dangerous if it
is not scoped. This taxonomy keeps replay evidence honest.

## Replay Families

| Family | Meaning | Current Monogate Example | Claim Boundary |
| --- | --- | --- | --- |
| Fixture replay | A committed fixture can be regenerated or checked. | Rescue fixture and evidence packet JSON. | Does not prove runtime determinism. |
| Sample-grid replay | Multiple outputs agree on selected inputs. | A13.2 semantic output comparison. | Does not prove formal equivalence. |
| Trace replay | A trace can be parsed and checked against hash/order rules. | OS/QEMU trace lanes. | Does not imply all nondeterminism is captured. |
| Record/replay debugging | Runtime execution is recorded enough to replay a process. | External reference: rr. | Not currently a Monogate capability. |
| System-enforced deterministic replay | OS or scheduler enforces deterministic semantics. | External reference: Determinator. | Not currently a Monogate capability. |

## Determinism Scopes

- `fixture_deterministic`: same fixture, same generated artifact.
- `tool_deterministic`: same tool inputs, same output digest.
- `sample_grid_deterministic`: same selected inputs, same selected outputs.
- `process_replay_deterministic`: process replay with captured nondeterminism.
- `system_enforced_deterministic`: scheduler or OS prevents nondeterministic
  interleavings by design.

## Immediate Monogate Rule

Every future replay packet should say which scope it satisfies. If the packet
cannot say, it must default to `fixture_deterministic` or `none`.

## Non-Claims

- No deterministic OS claim.
- No record/replay debugger claim.
- No full nondeterminism-capture claim.
- No formal equivalence claim from sample-grid agreement.
