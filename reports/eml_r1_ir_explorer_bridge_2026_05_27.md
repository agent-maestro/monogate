# EML-R1 IR Explorer Bridge

Date: 2026-05-27

Status: `EML_R1_IR_EXPLORER_BRIDGE_CANDIDATE_PASS`

This sprint reconnects the EML phase to the evidence engine by turning one existing EML IR substrate artifact into an inspectable candidate fixture.

## Selected Program

- Program: `attention_three_logits_three_outputs_v0`
- Family: `softmax_attention`
- Expression: `exp(q*k1) / (exp(q*k1) + exp(q*k2) + exp(q*k3)) + exp(q*k2) / (exp(q*k1) + exp(q*k2) + exp(q*k3)) + exp(q*k3) / (exp(q*k1) + exp(q*k2) + exp(q*k3))`

## Inspector Metrics

- DAG nodes: `17`
- DAG edges: `23`
- Reused nodes: `12`
- Replay frames: `17`
- Public tree SuperBEST baseline: `46`
- Internal DAG SuperBEST candidate: `20`
- Internal extra DAG savings nodes: `26`

## Claim Boundary

EML-R1 surfaces an existing IR/replay artifact for inspection. DAG savings remain internal candidate evidence, not a new public savings claim.

- No new public savings claim.
- No Forge/compiler behavior change.
- No formal verification claim.
- No package publish or deploy.

## Evidence Packet

- Artifact: `eml-r1-ir-explorer-bridge`
- Reviewer decision: `candidate_only`
- Validation status: `pass`
- Replay status: `pass`

## Next EML Step

Use this bridge as the first public-dev cockpit for EML IR, then extend EML-R2 toward a small IR packet builder that lets a reviewer choose expressions and inspect tree, DAG, replay, and non-claims before anything is surfaced.
