# EML-A11 Mock Compiler Decision Layer

Date: 2026-05-27

Status: `EML_A11_MOCK_COMPILER_DECISION_PASS`

| Program | Guard decision | Mock compiler decision |
|---|---|---|
| `deep_fold_holdout_v0` | `block_unstable_deep_tree` | `blocked_requires_evidence` |
| `expm1_near_zero_holdout_v0` | `recommend_protected_lowering` | `protected_runtime_lowering` |
| `gaussian_reuse_holdout_v0` | `allow_proof_shape` | `proof_shape_only` |
| `logsumexp_three_holdout_v0` | `recommend_protected_lowering` | `protected_runtime_lowering` |
| `raw_eml_domain_holdout_v0` | `block_missing_domain_guard` | `blocked_requires_evidence` |
| `subtraction_boundary_holdout_v0` | `allow_proof_shape` | `proof_shape_only` |

## Boundary

- Mock compiler decision layer only.
- No real compiler behavior change, compiler correctness proof, production readiness, runtime performance, or EML advantage claim.
