# External Evidence Traditions: Next Sprints

Date: 2026-05-29

Status: private research planning packet.

This closes the first pass after the External Evidence Traditions Map. It turns
the map into five bounded work lanes. These are contracts and taxonomies, not
claims that Monogate already implements Foundational PCC, deterministic OS
replay, high-assurance certification, automated proof digestion, or
Pfaffian/holographic EML mechanisms.

## PCC-M1: Evidence Packet as Proof-Carrying Artifact Contract

Proof-carrying code says a consumer should not trust a payload by reputation
alone. The payload carries evidence that can be checked against a policy. For
Monogate, the analogous artifact is not yet machine-code safety. It is:

payload -> evidence references -> obligations -> claim boundary -> reviewer decision

Deliverable:

- `schemas/proof_carrying_artifact_contract_v0.json`

Immediate use:

- Wrap Forge/eFrog outputs, rescue packets, replay traces, and understanding
  packets with explicit obligations.
- Keep each obligation status separate: discharged, partial, blocked,
  unresolved, or not applicable.

Non-claim:

- This is not Foundational PCC and does not prove compiler correctness.

## DR-M1: Replay Packet vs Deterministic Replay Taxonomy

Monogate currently uses several meanings of replay: fixture replay, sample-grid
comparison, trace replay, and QEMU-style runtime traces. Determinator and rr
show why this distinction matters. A record/replay debugger is not the same as a
system-enforced deterministic OS; a deterministic fixture is not the same as
capturing all runtime nondeterminism.

Deliverable:

- `schemas/replay_taxonomy_packet_v0.json`
- `reports/replay_packet_deterministic_replay_taxonomy_2026_05_29.md`

Immediate use:

- Label every replay artifact with its determinism scope.
- Prevent "replay passed" from inflating into "the system is deterministic."

Non-claim:

- No deterministic OS claim.

## HA-M1: A13 Assurance Case Skeleton

High-assurance groups tend to make the argument structure explicit: top-level
claim, subclaims, evidence, assumptions, and gaps. A13 now has enough private
evidence to deserve this shape, but not enough to claim correctness.

Deliverable:

- `schemas/assurance_case_skeleton_v0.json`
- `reports/a13_assurance_case_skeleton_2026_05_29.md`

Immediate use:

- Show exactly what A13 supports today: roundtrip pass counts and selected
  sample-grid agreement.
- Show exactly what is missing: formal equivalence, compiler correctness,
  larger holdouts, non-Python semantic checks, and generated-target re-ingest.

Non-claim:

- No high-assurance certification claim.

## LP-M1: Proof Digestion Fields for Understanding Packets

Lean/AI proof workflows make the distinction obvious: verification is not the
same as understanding. Understanding Packets already carry digest reviews; the
next schema pass adds explicit proof-digestion metadata so a reviewer can ask:

- what can be taught?
- what can be reused?
- what remains expert-only?
- what would be dangerous to overclaim?

Deliverable:

- `monogate-research/schemas/understanding_packet_v0.schema.json` gains an
  optional `proofDigestion` object.
- `monogate-research/reports/understanding_packet_proof_digestion_fields_2026_05_29.md`
  records the field intent.

Non-claim:

- Digestion does not add proof strength.

## PF-M1: Pfaffian/Holographic Literature Map Only

Pfaffian and holographic algorithms are worth keeping in the research orbit
because they are about compressed structure and unexpected tractability. That is
philosophically adjacent to EML advantage, but not yet mechanically connected.

Deliverable:

- `reports/pfaffian_holographic_literature_map_2026_05_29.md`

Immediate use:

- Keep a clean lane for future comparison against EML operator trees.
- Block premature claims that Pfaffians, matchgates, or holographic reductions
  explain EML.

Non-claim:

- No Pfaffian/EML mechanism claim.

## Recommended Next Action

The next implementation sprint should be PCC-M2: apply the
Proof-Carrying Artifact Contract to one live artifact family. My vote is A13,
because it already has clear obligations and gaps.

## Source Anchors

- Appel / Princeton Foundational PCC:
  `https://www.cs.princeton.edu/~appel/fpcc.html`
- Necula PCC:
  `https://www.cs.cmu.edu/~necula/pcc.html`
- Galois HACMS:
  `https://www.galois.com/project/hacms`
- Sandia PROOF:
  `https://proof.sandia.gov/`
- Determinator:
  `https://arxiv.org/abs/1005.3450`
- rr:
  `https://rr-project.org/`
- Lean / AI proof workflow examples:
  `https://www.math.inc/gauss`
- Holographic algorithms:
  `https://arxiv.org/abs/1307.7430`
