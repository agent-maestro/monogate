# EML-D19 Next Proof-Family Branch Decision

Status: `EML_D19_NEXT_PROOF_FAMILY_BRANCH_DECISION_PASS`

Selected option: `nested_subtraction_boundary_chain_selector`

D19 chooses the next private branch after the affine-offset witness surface review.

| Option | Status | Score | Next artifact |
|---|---|---:|---|
| `nested_subtraction_boundary_chain_selector` | `selected_next` | 71 | EML-D20 nested subtraction-boundary chain selector |
| `fresh_identity_family_selector` | `candidate_later` | 58 | Future small identity-family selector |
| `checked_witness_copy_review_packet` | `candidate_later` | 53 | Future checked-witness copy review packet |
| `prime_signature_log_recovery_feasibility_selector` | `candidate_later` | 41 | Future prime-signature witness feasibility selector |

## Summary

- selected next artifact: `EML-D20 nested subtraction-boundary chain selector`
- broad subtraction-family claim: `False`
- copy review started: `False`
- implementation started: `False`
- runtime lowering control: `standard_subtraction_remains_runtime_control`

## Non-Claims

- EML-D19 chooses the next private proof-family branch after D18; it does not start copy review, edit MachLib, or typecheck Lean.
- D19 does not prove a theorem, prove broad EML advantage, prove full EML semantics, prove compiler correctness, claim runtime performance, claim formal equivalence, or promote public Atlas copy.
- The selected nested-chain branch is selector-only; standard subtraction remains the runtime lowering control.
