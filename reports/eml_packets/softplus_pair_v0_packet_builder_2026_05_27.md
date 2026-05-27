# EML Packet Builder Result: softplus_pair_v0

Date: 2026-05-27

Status: `EML_PACKET_BUILDER_CANDIDATE_PASS`

## Source Packet

- Family: `softplus_logsumexp`
- Expression: `ln(exp(a) + exp(b))`
- Inputs: `a, b`
- Source repo: `monogate`
- Meaning: Small log-sum-exp style expression for EML IR packet-builder intake.

## Generated Artifact

- Artifact: `softplus-pair-v0`
- DAG nodes: `6`
- DAG edges: `5`
- Reused nodes: `0`
- Replay frames: `8`
- Obligation cards: `3`
- Domain requirements: `1`
- Range assumptions: `2`
- Public tree SuperBEST baseline: `5`
- Internal DAG SuperBEST candidate: `5`

## Review

- Decision: `candidate_only`
- Validation: `pass`
- Replay: `pass`
- Semantic strength: `eml_expression_packet_candidate_no_public_savings_claim`

## Obligation Cards

- Domain obligations: `1`
- Range-safety obligations: `2`
- Proved obligations: `1`

## Domain Safety Lens

- Unresolved obligations: `2`
- Checked obligations: `1`
- Candidate safe rewrites: `3`
- Blocked public claims: `7`

## Non-Claims

- No new public savings claim.
- No Forge/compiler behavior change.
- No theorem or formal verification claim.
- No hardware observation.
- No certified safety or production controller claim.
- No package publish or deploy.
