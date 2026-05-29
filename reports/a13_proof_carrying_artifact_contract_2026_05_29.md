# A13 Proof-Carrying Artifact Contract

Date: 2026-05-29

Status: private contract instance.

This applies the Proof-Carrying Artifact Contract v0 to the A13 Forge/eFrog
lane. It does not claim Foundational PCC, compiler correctness, formal
equivalence, production readiness, public readiness, or runtime performance.

## Contract Shape

A13 is now represented as:

payload -> evidence references -> obligations -> claim boundary -> reviewer decision

The payload is the A13 toolchain pause report. The evidence references are the
roundtrip packet, semantic sample-grid packet, generated result JSON, and packet
schemas.

## Obligations

| Obligation | Status | Meaning |
| --- | --- | --- |
| Roundtrip packet schema validation | discharged | The A13 roundtrip evidence packet is valid JSON and has the expected boundary fields. |
| Semantic comparison packet schema validation | discharged | The A13.2 sample-grid packet is valid JSON and has the expected boundary fields. |
| Deterministic roundtrip generation | partial | Current corpus regenerated deterministically, but this is not compiler correctness. |
| Selected sample-grid agreement | partial | Six selected scalar kernels agree on fixed samples, but this is not formal equivalence. |
| Claim-boundary review | discharged | A13 closure explicitly blocks public/correctness/performance claims. |
| Formal compiler correctness witness | blocked | No formal source/IR/target semantics or proof exists yet. |
| Non-Python source semantic comparison | unresolved | Needed before expanding semantic evidence beyond selected Python-source cases. |
| Generated-target re-ingest | unresolved | Needed before claiming stronger target stability. |

## Why This Matters

This is the first place Monogate's evidence packets start to behave like
proof-carrying artifacts. The artifact is not trusted because it sounds
promising; it carries a checkable set of obligations and gaps.

## Next Step

`PCC-M3` should add a small validator that checks contract instances against
the schema and verifies that every blocked claim has a matching non-claim.

## Non-Claims

- No Foundational PCC claim.
- No compiler correctness claim.
- No formal equivalence claim.
- No production toolchain claim.
- No broad EML advantage claim.
- No runtime performance claim.
- No public deployment or publication claim.
