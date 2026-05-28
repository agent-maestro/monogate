# EML-A10 Expression Guard Lens

Date: 2026-05-27

Status: `EML_A10_EXPRESSION_GUARD_LENS_PASS`

| Program | Decision | Lowering |
|---|---|---|
| `deep_fold_holdout_v0` | `block_unstable_deep_tree` | `none` |
| `expm1_near_zero_holdout_v0` | `recommend_protected_lowering` | `expm1-style protected lowering` |
| `gaussian_reuse_holdout_v0` | `allow_proof_shape` | `none` |
| `logsumexp_three_holdout_v0` | `recommend_protected_lowering` | `logaddexp-style protected lowering` |
| `raw_eml_domain_holdout_v0` | `block_missing_domain_guard` | `none` |
| `subtraction_boundary_holdout_v0` | `allow_proof_shape` | `none` |

## Boundary

- Expression packet guard lens only.
- No compiler behavior change, compiler correctness proof, production readiness, runtime performance, or EML advantage claim.
