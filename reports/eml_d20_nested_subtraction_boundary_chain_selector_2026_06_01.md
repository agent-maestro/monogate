# EML-D20 Nested Subtraction Boundary Chain Selector

Status: `EML_D20_NESTED_SUBTRACTION_BOUNDARY_CHAIN_SELECTOR_PASS`

Selected statement: `subtraction_boundary_two_stage_chain_v1`

D20 chooses the smallest nested subtraction-boundary chain before any MachLib proof attempt.

| Statement | Status | Score | Proof target |
|---|---|---:|---|
| `subtraction_boundary_two_stage_chain_v1` | `selected_next` | 76 | `MachLib.Real.subtraction_boundary_two_stage_chain_witness` |
| `subtraction_boundary_affine_nested_chain_v1` | `candidate_later` | 63 | `MachLib.Real.subtraction_boundary_affine_nested_chain_witness` |
| `subtraction_boundary_three_stage_chain_v1` | `candidate_later` | 45 | `MachLib.Real.subtraction_boundary_three_stage_chain_witness` |
| `subtraction_boundary_nested_unguarded_negative_control_v1` | `blocked_negative_control` | 5 | `none` |

## Summary

- negative control blocked: `True`
- affine nested chain parked: `True`
- deeper chain parked: `True`
- implementation started: `False`
- Lean typecheck performed: `False`
- runtime lowering control: `standard_subtraction_remains_runtime_control`

## Non-Claims

- EML-D20 selects a nested subtraction-boundary chain statement only; it does not edit MachLib or typecheck Lean.
- D20 does not prove a theorem, prove a broad nested subtraction family, prove broad EML advantage, prove full EML semantics, prove compiler correctness, claim runtime performance, claim formal equivalence, or promote public Atlas copy.
- The selected nested chain remains proof/teaching-shape work; standard subtraction remains the runtime lowering control.
