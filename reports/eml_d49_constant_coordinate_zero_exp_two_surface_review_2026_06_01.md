# EML-D49 Constant-Coordinate Zero-Exp-Two Surface Review

Status: `EML_D49_CONSTANT_COORDINATE_ZERO_EXP_TWO_SURFACE_REVIEW_PASS`

D49 surfaces the checked constant-coordinate witness privately without public copy approval.

| Surface | Status | Action |
|---|---|---|
| `machlib_witness_index_constant_coordinate_zero_exp_two` | `checked_witness_recorded_private` | record_as_private_checked_witness |
| `constant_coordinate_local_spelling_guardrail` | `one_plus_one_spelling_required` | preserve_exp_two_to_exp_one_plus_one_note |
| `constant_coordinate_non_duplicate_guardrail` | `non_duplicate_of_d10_constants_bundle` | keep_d10_bundle_and_d48_witness_separate |
| `advantage_lab_constant_coordinate_zero_exp_two` | `runtime_control_remains_standard_log_exp_and_arithmetic` | do_not_add_runtime_advantage_row_without_new_runtime_evidence |
| `public_atlas_constant_coordinate_zero_exp_two` | `held_private` | require_human_copy_review_before_public_change |

## Summary

- selected witness: `MachLib.Real.constant_coordinate_zero_exp_two_witness`
- source statement: `eml 0 (exp 2) = -1`
- checked Lean statement: `eml 0 (exp (1 + 1)) = -1`
- local spelling preserved: `True`
- duplicates existing constants witness: `False`
- public copy approved: `False`
- surface updated: `False`

## Non-Claims

- EML-D49 is a private surface review over the checked D48 constant-coordinate witness; it does not update public pages or promote Atlas copy.
- The checked identity is one scoped proof/teaching-shape witness using MachLib's local `1 + 1` spelling; it is not a new runtime lowering or log/exp replacement.
- D49 does not edit MachLib, typecheck Lean, approve public copy, add Advantage Lab cases, consume laptop artifacts, touch laptop-owned repos, or claim theorem discovery or broad EML superiority.
