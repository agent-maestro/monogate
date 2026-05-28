# EML-A8.5 Deep Tree Holdout

Date: 2026-05-27

Status: `EML_A8_5_DEEP_TREE_HOLDOUT_PASS`

| Case | Depth | Holdout class |
|---|---:|---|
| `deep_expm1_chain_near_zero_v0` | `8` | `standard_runtime_win` |
| `deep_expm1_chain_wide_v0` | `5` | `blocked_unstable_deep_tree` |
| `nested_ln_from_eml_positive_v0` | `6` | `mixed_identity_supported` |
| `subtraction_boundary_chain_v0` | `6` | `blocked_unstable_deep_tree` |
| `unstable_deep_tree_negative_control_v0` | `12` | `blocked_unstable_deep_tree` |

## Summary

- Packets: `5`
- Max tree depth: `12`
- Blocked: `3`
- Standard runtime wins: `1`
- EML structure supported: `0`
- Deep-tree stability claim: `False`

## Boundary

- Deep-tree holdout only.
- No broad EML advantage, deep-tree stability proof, runtime performance, compiler correctness, theorem discovery, public Atlas promotion, or deployment claim.
