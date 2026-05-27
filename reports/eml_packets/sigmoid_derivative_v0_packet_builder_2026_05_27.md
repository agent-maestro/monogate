# EML Packet Builder Result: sigmoid_derivative_v0

Date: 2026-05-27

Status: `EML_PACKET_BUILDER_CANDIDATE_PASS`

## Source Packet

- Family: `sigmoid_logistic`
- Expression: `(1 / (1 + exp(-x))) * (1 - (1 / (1 + exp(-x))))`
- Inputs: `x`
- Source repo: `monogate`
- Meaning: Derivative-shaped logistic fixture with repeated sigmoid subexpressions for DAG reuse inspection.

## Generated Artifact

- Artifact: `sigmoid-derivative-v0`
- DAG nodes: `8`
- DAG edges: `10`
- Reused nodes: `6`
- Replay frames: `10`
- Obligation cards: `2`
- Public tree SuperBEST baseline: `17`
- Internal DAG SuperBEST candidate: `10`

## Review

- Decision: `candidate_only`
- Validation: `pass`
- Replay: `pass`
- Semantic strength: `eml_expression_packet_candidate_no_public_savings_claim`

## Obligation Cards

- Domain obligations: `1`
- Range-safety obligations: `1`
- Proved obligations: `0`

## Non-Claims

- No new public savings claim.
- No Forge/compiler behavior change.
- No theorem or formal verification claim.
- No hardware observation.
- No certified safety or production controller claim.
- No package publish or deploy.
