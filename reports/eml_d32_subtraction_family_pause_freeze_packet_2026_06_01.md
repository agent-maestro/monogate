# EML-D32 Subtraction-Family Pause Freeze Packet

Status: `EML_D32_SUBTRACTION_FAMILY_PAUSE_FREEZE_PACKET_PASS`

D32 pauses subtraction-family deepening and freezes the checked-witness index for private handoff stability.

| Witness | Freeze status | Runtime control |
|---|---|---|
| `constants_zero_one_e_boundary` | `frozen_for_private_handoff` | standard constants and exp remain runtime controls |
| `ln_from_eml_boundary` | `frozen_for_private_handoff` | standard log(y) remains runtime control |
| `subtraction_boundary_affine_offset` | `frozen_for_private_handoff` | standard subtraction remains runtime control |
| `subtraction_boundary_two_stage_chain` | `frozen_for_private_handoff` | standard subtraction remains runtime control |
| `subtraction_boundary_affine_nested_chain` | `frozen_for_private_handoff` | standard subtraction remains runtime control |
| `subtraction_boundary_three_stage_chain` | `frozen_for_private_handoff` | standard subtraction remains runtime control |

## Summary

- family deepening paused: `True`
- checked witness index frozen: `True`
- frozen witnesses: `6`
- public copy approved: `False`
- implementation started: `False`
- runtime lowering changed: `False`

## Non-Claims

- EML-D32 is a private pause/freeze packet; it does not publish D30 copy or approve public wording.
- D32 freezes the currently checked witness index for handoff stability; it does not prove a broad nested subtraction family or arbitrary-depth theorem.
- D32 starts no MachLib edit, Lean typecheck, implementation, runtime-lowering change, public surface update, or Advantage Lab case.
