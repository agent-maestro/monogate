# EML-A11 Mock Compiler Decision Layer

Date: 2026-05-27

Status: `EML_A11_MOCK_COMPILER_DECISION_PASS`

A11 routes A10 guard-lens packets into explicit mock compiler decisions:

- `allow_proof_shape` -> `proof_shape_only`
- `recommend_protected_lowering` -> `protected_runtime_lowering`
- `block_*` -> `blocked_requires_evidence`

Initial fixture counts:

- mock compiler decisions: 3
- protected runtime lowerings: 1
- blocked requires-evidence decisions: 1
- proof-shape-only decisions: 1

## Boundary

- Mock compiler decision layer only.
- No real compiler implementation.
- No real compiler behavior change.
- No compiler correctness proof.
- No production readiness, runtime performance, public Atlas promotion, or EML advantage claim.
