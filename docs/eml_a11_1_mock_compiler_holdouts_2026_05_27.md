# EML-A11.1 Mock Compiler Holdouts

Date: 2026-05-27

Status: `EML_A11_1_MOCK_COMPILER_HOLDOUTS_PASS`

A11.1 adds a holdout packet set for the mock compiler decision layer. The goal
is to test the guard-to-decision mapping outside the original three seed
packets.

Holdout coverage:

- protected lowerings: `expm1_near_zero_holdout_v0`,
  `logsumexp_three_holdout_v0`
- blocked requires-evidence decisions: `raw_eml_domain_holdout_v0`,
  `deep_fold_holdout_v0`
- proof-shape controls: `subtraction_boundary_holdout_v0`,
  `gaussian_reuse_holdout_v0`

## Boundary

- Holdout packet set for mock compiler decisions only.
- No real compiler implementation.
- No real compiler behavior change.
- No compiler correctness proof.
- No production readiness, runtime performance, public Atlas promotion, or EML advantage claim.
