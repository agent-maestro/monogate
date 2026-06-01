# EML-D26 Next Nested-Family Branch Decision

Status: `EML_D26_NESTED_FAMILY_NEXT_BRANCH_DECISION_PASS`

Selected option: `three_stage_chain_witness_attempt`

D26 chooses the next private branch after the affine-nested chain surface review.

| Option | Status | Score | Next artifact |
|---|---|---:|---|
| `three_stage_chain_witness_attempt` | `selected_next` | 68 | EML-D27 subtraction-boundary three-stage chain witness attempt |
| `checked_witness_copy_review_packet` | `candidate_later` | 61 | Future checked-witness copy review packet |
| `pause_subtraction_family_deepening` | `candidate_later` | 52 | Future branch-pause packet |

## Summary

- selected next artifact: `EML-D27 subtraction-boundary three-stage chain witness attempt`
- broad nested subtraction claim: `False`
- copy review started: `False`
- implementation started: `False`
- runtime lowering control: `standard_subtraction_remains_runtime_control`

## Non-Claims

- EML-D26 chooses the next private nested-family branch after D25; it does not start copy review, edit MachLib, or typecheck Lean.
- D26 does not prove a theorem, prove a broad nested subtraction family, prove broad EML advantage, prove full EML semantics, prove compiler correctness, claim runtime performance, claim formal equivalence, or promote public Atlas copy.
- The selected three-stage branch is selector-only; standard subtraction remains the runtime lowering control.
