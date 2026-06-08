# ATLAS-A30 Private Exp-Negation Theorem-Lookup Gate

Status: `ATLAS_A30_PRIVATE_EXP_NEGATION_THEOREM_LOOKUP_GATE_PASS`

## Summary

- source artifact: `atlas-a29-private-exp-negation-proof-scope-feasibility-packet`
- source candidate: `atlas_candidate_exp_negation_multiplicative_identity_scoped_v0`
- lookup scope: `forall x : Real, Real.exp x * Real.exp (-x) = 1`
- lookup guard: `all real x`
- primary observed identifier: `MachLib.Real.exp_mul_exp_neg`
- observed identifier claimed as dependency: `False`
- candidate selected for proof: `False`
- proof attempt started: `False`
- MachLib changed: `False`
- Lean typecheck performed: `False`
- next recommended artifact: `ATLAS-A31 private exp-negation witness-wrapper readiness selector`

## Observed Identifier Candidates

| Identifier | File | Line hint | Status |
|---|---|---:|---|
| `MachLib.Real.exp_mul_exp_neg` | `/home/monogate/monogate/machlib/foundations/MachLib/HyperbolicPreservation.lean` | `114` | `primary_shape_match_observed_not_typechecked_this_phase` |
| `MachLib.Real.exp_neg_self_mul` | `/home/monogate/monogate/machlib/foundations/MachLib/Exp.lean` | `45` | `related_reversed_product_shape_observed_not_typechecked_this_phase` |
| `MachLib.Real.exp_add` | `/home/monogate/monogate/machlib/foundations/MachLib/Exp.lean` | `31` | `supporting_shape_observed_not_typechecked_this_phase` |

## Readiness Reasons

- A local theorem already has the same pure exp multiplication shape.
- The related reversed-product theorem and exp-add axiom are nearby local surfaces.
- A future readiness selector can decide whether to wrap the observed theorem as an Atlas witness without starting proof work here.

## Blockers Before Witness Attempt

- confirm import path and namespace in the exact future witness file before editing MachLib
- decide whether a future artifact should be a wrapper theorem, a theorem alias, or a parked candidate
- run Lean only in a separately gated future phase
- keep the EML companion deferred until local EML notation and definition are rechecked
- keep runtime exp replacement, public copy, product, and broad EML claims blocked

## Non-Claims

- ATLAS-A30 is a private theorem-lookup gate; it records observed local identifier candidates but does not select a proof dependency, edit MachLib, run Lean, or claim candidate validity.
- ATLAS-A30 records `MachLib.Real.exp_mul_exp_neg` as the primary observed identifier candidate for the pure exp statement; it does not claim that this identifier has been imported, typechecked in a new witness context, or used as a proof.
- ATLAS-A30 keeps the EML companion hint deferred and does not claim a checked EML theorem, formal equivalence, runtime exp replacement, public readiness, runtime performance, compiler correctness, or broad EML advantage.
