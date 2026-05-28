# EML-A9.1 Guard Rule Fixtures

Date: 2026-05-27

Status: `EML_A9_1_GUARD_RULE_FIXTURES_PASS`

| Fixture | Expected decision | Rules |
|---|---|---|
| `proof_shape_subtraction_boundary_fixture_v0` | `allow_proof_shape` | `prefer_eml_for_proof_shape_v0, require_positive_log_domain_guard_v0` |
| `near_zero_expm1_fixture_v0` | `recommend_protected_lowering` | `lower_expm1_near_zero_v0` |
| `softplus_logaddexp_fixture_v0` | `recommend_protected_lowering` | `lower_logaddexp_softplus_v0` |
| `missing_log_domain_guard_fixture_v0` | `block_missing_domain_guard` | `require_positive_log_domain_guard_v0` |
| `deep_tree_depth_12_fixture_v0` | `block_unstable_deep_tree` | `block_unstable_deep_tree_v0` |
| `advantage_claim_without_packets_fixture_v0` | `block_claim_until_evidence` | `require_trial_packet_before_advantage_claim_v0` |

## Boundary

- Fixtures only.
- No compiler behavior change, analyzer implementation, compiler correctness proof, runtime performance, or EML advantage claim.
