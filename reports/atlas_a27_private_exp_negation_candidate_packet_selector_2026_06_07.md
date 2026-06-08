# ATLAS-A27 Private Exp-Negation Candidate Packet Selector

Status: `ATLAS_A27_PRIVATE_EXP_NEGATION_CANDIDATE_PACKET_SELECTOR_PASS`

## Summary

- source artifact: `atlas-a26-private-exp-negation-boundary-feasibility-packet`
- reviewed direction: `exp_negation_multiplicative_identity_direction`
- selected option: `recommend_future_scoped_exp_negation_candidate_packet`
- selected decision: `recommend_scoped_candidate_packet_without_creating_it`
- source guard: `all real x`
- source pure shape: `exp x * exp (-x) = 1`
- source EML hint: `eml (x + (-x)) 1 = 1`
- new candidate packet created: `False`
- proof attempt started: `False`
- MachLib changed: `False`
- Lean typecheck performed: `False`
- next recommended artifact: `ATLAS-A28 private scoped exp-negation candidate packet`

## Readiness Reasons

- A26 recorded a clean all-real guard surface.
- A26 recorded both pure and possible EML-shaped hints without conflating them.
- A26 recorded explicit blockers before any packet, making a scoped packet selector appropriate.

## Future Packet Scope Requirements

- choose pure exp statement, EML-shaped statement, or paired statement scope
- state that candidate validity remains blocked
- carry forward runtime exp replacement and public-copy non-claims

## Options

| Option | Status | Decision |
|---|---|---|
| `recommend_future_scoped_exp_negation_candidate_packet` | `selected_next` | `recommend_scoped_candidate_packet_without_creating_it` |
| `hold_for_statement_scope_clarification` | `available_if_human_wants_scope_decision_first` | `pause_before_candidate_packet_for_scope_clarification` |
| `pause_for_atlas_v0_document` | `available_if_human_prefers_consolidation` | `pause_exp_negation_path_for_atlas_v0_doc` |

## Non-Claims

- ATLAS-A27 is a private selector; it recommends a future scoped candidate packet but does not create that packet, select a proof target, edit MachLib, run Lean, or claim candidate validity.
- ATLAS-A27 requires the future packet to choose pure exp, EML-shaped, or paired statement scope; it does not resolve that statement scope in this phase.
- ATLAS-A27 does not perform theorem lookup, claim exact theorem names, change runtime lowering, replace exp, publish or approve public copy, create SDK/compiler/course copy, touch laptop-owned repositories, or claim checked-witness status, public readiness, runtime performance, compiler correctness, formal equivalence, or broad EML advantage.
