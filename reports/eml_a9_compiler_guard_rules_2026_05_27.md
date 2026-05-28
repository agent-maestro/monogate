# EML-A9 Compiler Guard Rules

Date: 2026-05-27

Status: `EML_A9_COMPILER_GUARD_RULES_PASS`

| Rule | Class | Evidence status |
|---|---|---|
| `prefer_eml_for_proof_shape_v0` | `proof_shape_preference` | `ready_for_compiler_fixture` |
| `lower_expm1_near_zero_v0` | `protected_runtime_lowering` | `ready_for_compiler_fixture` |
| `lower_logaddexp_softplus_v0` | `protected_runtime_lowering` | `ready_for_compiler_fixture` |
| `require_positive_log_domain_guard_v0` | `domain_guard` | `ready_for_compiler_fixture` |
| `block_unstable_deep_tree_v0` | `deep_tree_block` | `ready_for_compiler_fixture` |
| `require_trial_packet_before_advantage_claim_v0` | `claim_gate` | `documentation_rule_only` |

## Summary

- Rules: `6`
- Ready for compiler fixtures: `5`
- Compiler behavior changed: `False`
- Compiler correctness claim: `False`
- Guard rules complete: `False`

## Boundary

- Guard-rule registry only.
- No compiler behavior change, compiler correctness proof, runtime performance, EML advantage proof, broad EML superiority, public Atlas promotion, or deployment claim.
