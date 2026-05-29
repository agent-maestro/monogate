# EML-A15 Glass Box Evidence Mount Handoff

Date: 2026-05-29

Status: `EML_A15_GLASSBOX_EVIDENCE_MOUNT_HANDOFF_PASS`

A15 prepares A14 Forge/eFrog export packets for Glass Box without touching Monogate Engine.

| Mount card | Function | Family | Link status | Slot |
|---|---|---|---|---|
| `gaussian_semantic_compare_v0_glassbox_mount_card_v0` | `gaussian` | `gaussian` | `linked_by_canonical_eml_hash` | `private_hud_evidence_card` |
| `gaussian_stable_holdout_semantic_compare_v0_glassbox_mount_card_v0` | `gaussian_stable` | `gaussian` | `linked_by_canonical_eml_hash` | `private_hud_evidence_card` |
| `poly_quadratic_semantic_compare_v0_glassbox_mount_card_v0` | `poly_quadratic` | `unmapped` | `semantic_comparison_only` | `private_hud_evidence_card` |
| `rc_decay_holdout_semantic_compare_v0_glassbox_mount_card_v0` | `rc_decay_stable` | `rc_decay` | `linked_by_canonical_eml_hash` | `private_hud_evidence_card` |
| `sigmoid_semantic_compare_v0_glassbox_mount_card_v0` | `sigmoid` | `numpy_softplus` | `semantic_comparison_only` | `private_hud_evidence_card` |
| `voltage_divider_holdout_semantic_compare_v0_glassbox_mount_card_v0` | `voltage_divider` | `clamp_guard` | `linked_by_canonical_eml_hash` | `private_hud_evidence_card` |

## Summary

- Mount cards: `6`
- Roundtrip-linked mounts: `4`
- Semantic-only mounts: `2`
- Engine dirty paths observed: `17`
- Engine files modified by A15: `0`

## Adapter Contract

- Target surface: `Monogate Engine Glass Box private HUD`
- Adapter implementation: `deferred_until_engine_worktree_is_coordinated`

## Boundary

- No Monogate Engine behavior change.
- No production runtime or certified safety claim.
- No compiler correctness or formal equivalence claim.
- No public-readiness or deployment claim.
