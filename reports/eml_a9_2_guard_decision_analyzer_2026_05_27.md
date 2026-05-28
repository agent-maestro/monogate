# EML-A9.2 Guard Decision Analyzer

Date: 2026-05-27

Status: `EML_A9_2_GUARD_DECISION_ANALYZER_PASS`

| Fixture | Decision | Rules matched |
|---|---|---|
| `proof_shape_subtraction_boundary_fixture_v0` | `allow_proof_shape` | `True` |
| `near_zero_expm1_fixture_v0` | `recommend_protected_lowering` | `True` |
| `softplus_logaddexp_fixture_v0` | `recommend_protected_lowering` | `True` |
| `missing_log_domain_guard_fixture_v0` | `block_missing_domain_guard` | `True` |
| `deep_tree_depth_12_fixture_v0` | `block_unstable_deep_tree` | `True` |
| `advantage_claim_without_packets_fixture_v0` | `block_claim_until_evidence` | `True` |

## Boundary

- Fixture analyzer only.
- No compiler behavior change, compiler correctness proof, production readiness, runtime performance, or EML advantage claim.
