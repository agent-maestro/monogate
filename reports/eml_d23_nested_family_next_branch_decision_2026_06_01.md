# EML-D23 Next Nested-Family Branch Decision

Status: `EML_D23_NESTED_FAMILY_NEXT_BRANCH_DECISION_PASS`

Selected option: `affine_nested_chain_witness_attempt`

D23 chooses the next private branch after the two-stage chain surface review.

| Option | Status | Score | Next artifact |
|---|---|---:|---|
| `affine_nested_chain_witness_attempt` | `selected_next` | 73 | EML-D24 subtraction-boundary affine-nested chain witness attempt |
| `three_stage_chain_witness_attempt` | `candidate_later` | 49 | Future three-stage subtraction-boundary chain witness attempt |
| `checked_witness_copy_review_packet` | `candidate_later` | 55 | Future checked-witness copy review packet |
| `pause_subtraction_family_deepening` | `candidate_later` | 44 | Future branch-pause packet |

## Summary

- selected next artifact: `EML-D24 subtraction-boundary affine-nested chain witness attempt`
- broad nested subtraction claim: `False`
- copy review started: `False`
- implementation started: `False`
- runtime lowering control: `standard_subtraction_remains_runtime_control`

## Non-Claims

- EML-D23 chooses the next private nested-family branch after D22; it does not start copy review, edit MachLib, or typecheck Lean.
- D23 does not prove a theorem, prove a broad nested subtraction family, prove broad EML advantage, prove full EML semantics, prove compiler correctness, claim runtime performance, claim formal equivalence, or promote public Atlas copy.
- The selected affine-nested branch is selector-only; standard subtraction remains the runtime lowering control.
