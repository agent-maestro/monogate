# ATLAS-A28 Private Scoped Exp-Negation Candidate Packet

Status: `ATLAS_A28_PRIVATE_SCOPED_EXP_NEGATION_CANDIDATE_PACKET_PASS`

## Summary

- source artifact: `atlas-a27-private-exp-negation-candidate-packet-selector`
- candidate id: `atlas_candidate_exp_negation_multiplicative_identity_scoped_v0`
- selected scope: `paired_pure_exp_with_eml_companion_hint`
- guard: `all real x`
- pure candidate statement: `forall x : Real, Real.exp x * Real.exp (-x) = 1`
- EML companion hint: `eml (x + (-x)) 1 = 1`
- candidate selected for proof: `False`
- candidate validity claim: `False`
- proof attempt started: `False`
- MachLib changed: `False`
- Lean typecheck performed: `False`
- next recommended artifact: `ATLAS-A29 private exp-negation proof-scope feasibility packet`

## Candidate Statements

- pure exp statement: `forall x : Real, Real.exp x * Real.exp (-x) = 1`
- pure exp status: `not_checked_not_proved_not_selected_for_proof`
- EML companion hint: `eml (x + (-x)) 1 = 1`
- EML companion status: `not_checked_not_proved_not_formal_equivalence_claim`

## Review Value

- Adds an exp-family Atlas candidate with a clean all-real guard.
- Keeps the pure exp statement separate from the EML-shaped companion hint.
- Creates a concrete next packet for proof-scope feasibility without starting proof work.

## Blockers Before Proof Selection

- decide whether A29 should scope only the pure exp statement or keep a paired scope
- perform theorem lookup before naming any Lean theorem dependency
- check exact local notation and import surface before any MachLib edit
- keep runtime exp replacement, public copy, product, and broad EML claims blocked

## Non-Claims

- ATLAS-A28 creates a private scoped candidate packet for review; it does not select the candidate for proof, prove it, edit MachLib, run Lean, or claim candidate validity.
- ATLAS-A28 records a paired scope with a pure exp statement and an EML companion hint; it does not claim that the EML hint is a checked theorem or that the pair is formally equivalent.
- ATLAS-A28 does not perform theorem lookup, claim exact theorem names, change runtime lowering, replace exp, publish or approve public copy, create SDK/compiler/course copy, touch laptop-owned repositories, or claim checked-witness status, public readiness, runtime performance, compiler correctness, formal equivalence, or broad EML advantage.
