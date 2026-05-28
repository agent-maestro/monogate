# EML-A10 Expression Guard Lens

Date: 2026-05-27

Status: `EML_A10_EXPRESSION_GUARD_LENS_PASS`

| Program | Decision | Lowering |
|---|---|---|
| `gaussian_energy_v0` | `allow_proof_shape` | `none` |
| `sigmoid_derivative_v0` | `block_missing_domain_guard` | `none` |
| `softplus_pair_v0` | `recommend_protected_lowering` | `logaddexp-style protected lowering` |

## Boundary

- Expression packet guard lens only.
- No compiler behavior change, compiler correctness proof, production readiness, runtime performance, or EML advantage claim.
