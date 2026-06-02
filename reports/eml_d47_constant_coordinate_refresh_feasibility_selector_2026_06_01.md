# EML-D47 Constant-Coordinate Refresh Feasibility Selector

Status: `EML_D47_CONSTANT_COORDINATE_REFRESH_FEASIBILITY_SELECTOR_PASS`

D47 selects one non-duplicate constant-coordinate candidate before any MachLib edit or proof attempt.

| Candidate | Statement | Duplicate status | Next artifact |
|---|---|---|---|
| `zero_coordinate_exp_two_boundary` | `eml 0 (exp 2) = -1` | `non_duplicate_of_constants_zero_one_e_boundary_witness` | EML-D48 constant-coordinate zero-exp-two witness attempt or blocker packet |

## Existing Constants Witness

- `eml 0 (exp 1) = 0`
- `eml 0 1 = 1`
- `eml 1 1 = exp 1`

## Summary

- selected proposed witness: `MachLib.Real.constant_coordinate_zero_exp_two_witness`
- duplicates existing constants witness: `False`
- implementation started: `False`
- proof attempt started: `False`
- public copy approved: `False`

## Non-Claims

- EML-D47 is a feasibility selector for one non-duplicate constant-coordinate candidate; it does not edit MachLib, typecheck Lean, or prove the candidate.
- D47 does not reopen the checked D10 constants witness or claim a public Atlas promotion.
- D47 does not approve public copy, consume laptop artifacts, touch laptop-owned repos, change runtime lowering, replace log/exp, or claim theorem discovery or broad EML superiority.
