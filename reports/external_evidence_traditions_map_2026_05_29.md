# External Evidence Traditions Map

Date: 2026-05-29

Status: `EXTERNAL_EVIDENCE_TRADITIONS_MAP_RECORDED`

This map looks outward from Monogate's A13 toolchain pause. It is a research
orientation artifact, not a proof, product claim, or public positioning claim.

## Why This Matters

Monogate's current evidence spine says:

`artifact -> trace/replay/packet -> reviewer boundary -> optional surface`

The outside world has several older, deeper traditions that rhyme with this:

- proof-carrying code
- high-assurance formal methods
- deterministic replay and reversible debugging
- Lean/AI proof formalization
- Pfaffian and holographic algorithms

The useful question is not "did we invent all of this?" We did not. The useful
question is: what can Monogate learn from these traditions, and where does EML
give us a distinct toolchain surface?

## Map

| Tradition | Core Idea | Monogate Relevance | Suggested Sprint |
|---|---|---|---|
| Proof-Carrying Code / Foundational PCC | Code carries a proof or foundational evidence checked by a small trusted base. | Strongest conceptual ancestor for evidence packets attached to generated artifacts. | PCC-M1: map Evidence Packet v0 to PCC roles: producer, consumer, policy, checker, trusted base. |
| High-Assurance Formal Methods / Galois | Build systems with formal specs, DSLs, proofs, and assurance cases. | Useful model for Forge/eFrog as DSL plus generated code plus bounded assurance case. | HA-M1: create an assurance-case skeleton for A13. |
| Sandia Digital Foundations / PROOF | Formal verification, modeling, simulation, binary analysis, and extreme-environment digital systems. | Useful for electronics and OS lanes: simulation evidence must stay distinct from hardware truth. | DF-M1: build a simulation-vs-observation evidence taxonomy. |
| Determinator / Deterministic OS | OS-level deterministic execution enables reproducibility, debugging, fault tolerance, and accountability. | Directly relevant to Monogate OS replay frames and scheduler traces. | DR-M1: compare Monogate replay packets to deterministic-execution obligations. |
| rr / Record-Replay Debugging | Record nondeterministic execution once; replay deterministically for debugging. | Practical cousin of evidence replay: execution traces become reviewable artifacts. | RR-M1: design a record/replay packet adapter vocabulary. |
| Lean / AI Proof Workflows | AI helps generate/formalize proofs, but Lean checks them and humans digest them. | Matches Monogate's "proof digestion before public claim" posture. | LP-M1: add proof-digestion fields to Understanding Packet v0. |
| Pfaffian / Holographic Algorithms | Constraint transformations can make certain counting problems tractable through matchgate/Pfaffian structure. | Interesting for EML operator-tree search and Pfaffian-boundary exploration, but not an immediate product lane. | PF-M1: literature-only map; no Monogate claim expansion. |

## Source Anchors

- Appel / Princeton Foundational PCC:
  - https://www.cs.princeton.edu/~appel/fpcc.html
  - https://www.cs.princeton.edu/~appel/papers/fpcc.pdf
- Necula PCC background:
  - https://www.cs.cmu.edu/~necula/pcc.html
- Galois:
  - https://www.galois.com/
  - https://www.galois.com/project/hacms
  - https://www.galois.com/project/shave
- Sandia Digital Foundations / PROOF:
  - https://proof.sandia.gov/
- Determinator:
  - https://arxiv.org/abs/1005.3450
- rr:
  - https://rr-project.org/
  - https://arxiv.org/abs/1705.05937
- Lean / AI proof workflows:
  - https://www.math.inc/gauss
  - https://reservoir.lean-lang.org/%40vltanh/lean4-analysis-tao
- Holographic / Pfaffian algorithms:
  - https://arxiv.org/abs/1307.7430
  - https://pages.cs.wisc.edu/~jyc/papers/HA-survey.pdf
  - https://arxiv.org/abs/2508.11634

## Recommendations

Do the next sprint in this order:

1. PCC-M1: Evidence Packet as Proof-Carrying Artifact Contract.
2. DR-M1: Replay Packet vs Deterministic Replay Taxonomy.
3. HA-M1: A13 Assurance Case Skeleton.
4. LP-M1: Proof Digestion Fields for Understanding Packets.
5. PF-M1: Pfaffian/Holographic Literature Map only.

## Boundary

- No claim that Monogate is PCC-complete.
- No claim that Forge/eFrog has compiler correctness.
- No claim that sample-grid agreement is formal equivalence.
- No claim that Monogate OS enforces deterministic execution.
- No claim that Monogate has high-assurance certification.
- No claim that Pfaffian/holographic algorithms currently power EML.

## Clean Pause Decision

The A13 toolchain lane can pause here. The next work should not expand A13
until PCC-M1 and DR-M1 define a stronger vocabulary for what an evidence
packet is supposed to carry and what replay evidence is supposed to mean.
