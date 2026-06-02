# EML-D31 Checked Witness Review Next Decision

Status: `EML_D31_CHECKED_WITNESS_REVIEW_NEXT_DECISION_PASS`

Selected option: `pause_subtraction_family_deepening`

D31 chooses the next private branch after the checked-witness copy review.

| Option | Status | Score | Next artifact |
|---|---|---:|---|
| `pause_subtraction_family_deepening` | `selected_next` | 78 | EML-D32 subtraction-family pause and checked-witness index freeze packet |
| `human_approved_public_copy_gate` | `candidate_later_requires_human_approval` | 59 | Future human-approved checked-witness public copy gate |
| `new_bounded_identity_branch_selector` | `candidate_later_after_pause` | 51 | Future bounded identity branch selector |

## Summary

- selected next artifact: `EML-D32 subtraction-family pause and checked-witness index freeze packet`
- family deepening pause selected: `True`
- checked witness index freeze planned: `True`
- public copy approved: `False`
- implementation started: `False`
- runtime lowering control: `standard_subtraction_remains_runtime_control`

## Non-Claims

- EML-D31 is a selector-only next decision after D30; it does not publish D30 copy, approve public wording, edit MachLib, or typecheck Lean.
- D31 selects a private pause/freeze path for the subtraction-family ladder; it does not claim a broad nested subtraction family or any arbitrary-depth theorem.
- D31 keeps standard subtraction, standard log, standard exp, and standard constants as runtime controls where applicable.
