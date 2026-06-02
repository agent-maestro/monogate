# EML-D58 Expm1 Boundary Witness Surface Review

Status: `EML_D58_EXPM1_BOUNDARY_WITNESS_SURFACE_REVIEW_PASS`

D58 surfaces the checked expm1-boundary witness privately without public copy approval.

| Surface | Status | Action |
|---|---|---|
| `machlib_witness_index_expm1_boundary` | `checked_witness_recorded_private` | record_as_private_checked_witness |
| `expm1_runtime_control_guardrail` | `protected_expm1_runtime_control_required` | keep_protected_expm1_as_runtime_control |
| `expm1_non_duplicate_exp_branch_guardrail` | `non_duplicate_of_exp_branch_witness` | keep_eml_x_exp_one_separate_from_eml_x_one |
| `advantage_lab_expm1_boundary` | `runtime_control_remains_protected_expm1` | do_not_add_runtime_advantage_row_without_new_runtime_evidence |
| `public_atlas_expm1_boundary` | `held_private` | require_human_copy_review_before_public_change |

## Summary

- selected witness: `MachLib.Real.expm1_boundary_identity_witness`
- checked statement: `eml x (exp 1) = exp x - 1`
- runtime control: `protected_expm1_remains_runtime_control`
- public copy approved: `False`
- surface updated: `False`

## Non-Claims

- EML-D58 is a private surface review over the checked D57 expm1-boundary witness; it does not update public pages or promote Atlas copy.
- The checked identity is one scoped proof/teaching-shape witness; protected expm1 remains the runtime and numerical-stability control.
- D58 does not edit MachLib, typecheck Lean, approve public copy, add Advantage Lab cases, consume laptop artifacts, touch laptop-owned repos, or claim theorem discovery, runtime advantage, protected expm1 replacement, or broad EML superiority.
