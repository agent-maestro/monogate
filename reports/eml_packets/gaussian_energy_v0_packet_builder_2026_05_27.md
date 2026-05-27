# EML Packet Builder Result: gaussian_energy_v0

Date: 2026-05-27

Status: `EML_PACKET_BUILDER_CANDIDATE_PASS`

## Source Packet

- Family: `forge_efrog_fixture`
- Expression: `exp(-(x * x)) + exp(-(x * x))`
- Inputs: `x`
- Source repo: `monogate`
- Meaning: Gaussian-like repeated energy fixture for shared-node and replay inspection.

## Generated Artifact

- Artifact: `gaussian-energy-v0`
- DAG nodes: `5`
- DAG edges: `6`
- Reused nodes: `4`
- Replay frames: `8`
- Obligation cards: `1`
- Domain requirements: `0`
- Range assumptions: `1`
- Public tree SuperBEST baseline: `10`
- Internal DAG SuperBEST candidate: `6`

## Review

- Decision: `candidate_only`
- Validation: `pass`
- Replay: `pass`
- Semantic strength: `eml_expression_packet_candidate_no_public_savings_claim`

## Obligation Cards

- Domain obligations: `0`
- Range-safety obligations: `1`
- Proved obligations: `0`

## Domain Safety Lens

- Unresolved obligations: `1`
- Checked obligations: `0`
- Candidate safe rewrites: `1`
- Blocked public claims: `7`

## Non-Claims

- No new public savings claim.
- No Forge/compiler behavior change.
- No theorem or formal verification claim.
- No hardware observation.
- No certified safety or production controller claim.
- No package publish or deploy.
