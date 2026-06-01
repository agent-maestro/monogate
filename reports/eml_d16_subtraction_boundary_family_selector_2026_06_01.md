# EML-D16 Subtraction Boundary Family Selector

Status: `EML_D16_SUBTRACTION_BOUNDARY_FAMILY_SELECTOR_PASS`

Selected statement: `subtraction_boundary_affine_offset_family_v1`

D16 chooses a precise family-shaped statement before any MachLib proof attempt.

| Statement | Status | Score | Proof target |
|---|---|---:|---|
| `subtraction_boundary_base_duplicate_v0` | `rejected_duplicate_checked_base` | 30 | `MachLib.Real.atlas_subtraction_boundary_witness` |
| `subtraction_boundary_affine_offset_family_v1` | `selected_next` | 72 | `MachLib.Real.subtraction_boundary_affine_offset_witness` |
| `subtraction_boundary_two_stage_chain_v1` | `candidate_later` | 51 | `MachLib.Real.subtraction_boundary_two_stage_chain_witness` |
| `subtraction_boundary_unguarded_negative_control_v1` | `blocked_negative_control` | 5 | `none` |

## Summary

- duplicate base rejected: `True`
- negative control blocked: `True`
- implementation started: `False`
- Lean typecheck performed: `False`
- runtime lowering control: `standard_subtraction_remains_runtime_control`

## Non-Claims

- EML-D16 selects a subtraction-boundary family statement only; it does not edit MachLib or typecheck Lean.
- D16 does not prove a new theorem, prove broad EML advantage, prove full EML semantics, prove compiler correctness, claim runtime performance, claim formal equivalence, or promote public Atlas copy.
- The selected statement remains proof/teaching-shape work; standard subtraction remains the runtime lowering control.
