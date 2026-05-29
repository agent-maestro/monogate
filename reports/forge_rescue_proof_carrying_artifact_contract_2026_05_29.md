# Forge Rescue Proof-Carrying Artifact Contract

Date: 2026-05-29

Status: second contract-family validation target for PCC-M4.

This applies the Proof-Carrying Artifact Contract v0 to the existing Forge
Rescue Suite surface. This is not a new public deployment decision and does not
expand the claim boundary.

## Contract Shape

Forge Rescue is represented as:

payload -> evidence references -> obligations -> claim boundary -> reviewer decision

The payload is the existing Forge rescue suite report. The evidence references
include the suite JSON, replay result, approval packet, obligation registry,
Explorer fixture, and research artifact contract.

## Obligations

| Obligation | Status | Meaning |
| --- | --- | --- |
| Suite JSON validation | discharged | The existing suite artifact is present and parseable. |
| Replay validation | discharged | The existing replay result is present as contract evidence. |
| Obligation registry complete | discharged | The registry records four rescue lanes. |
| Conservative claim flags | discharged | Existing approval preserves bounded public claims. |
| Concrete MachLib witness coverage | partial | Concrete witness coverage exists, but this is not optimizer-wide correctness. |
| Log-domain restricted semantic rewrite | partial | The log-domain lane has restricted semantic strength only. |
| Public copy boundary | partial | Three lanes are public-copy safe; saturation_deshelf remains bounded/private. |
| Optimizer-wide correctness | blocked | No optimizer-wide correctness theorem exists. |
| Certified safety or production controller | blocked | No certified safety, hardware, or controller evidence exists. |

## Why This Matters

PCC-M3 validated A13. PCC-M4 checks whether the same contract grammar works on a
different artifact family: optimizer rescue evidence. It does. This reduces the
chance that the contract validator is merely an A13-shaped tool.

## Next Step

`PCC-M5` should add a small command that scans all contract instances in
`reports/proof_carrying_artifacts/` and validates them together.

## Non-Claims

- No Foundational PCC claim.
- No optimizer-wide correctness claim.
- No compiler correctness claim.
- No formal equivalence claim.
- No certified safety or production-controller claim.
- No hardware observation claim.
- No unrestricted semantic rewrite claim.
- No runtime performance claim.
