# EML-D8 Discovery Branch Decision

Status: `EML_D8_DISCOVERY_BRANCH_DECISION_PASS`

Selected branch: `machlib_identity_witness_lane_v0`

D8 chooses the next frontier branch after D7's no-replicated-holdout-gain label.

| Branch | Decision | Score | Next artifact |
|---|---|---|---|
| `park_psi_residual_search_v0` | `park_as_ambiguous_until_new_hypothesis` | 42 | D8 records parking decision; no new psi search run. |
| `machlib_identity_witness_lane_v0` | `selected_next` | 64 | EML-D9 MachLib identity witness selector |
| `fresh_non_psi_holdout_family_v0` | `candidate_later` | 46 | Future D-series holdout-family queue |
| `broaden_negative_controls_v0` | `candidate_later` | 50 | Future failure/control expansion packet |

## Summary

- psi search parked: `True`
- deeper psi search allowed: `False`
- implementation started: `False`
- EML advantage proved: `False`

## Non-Claims

- EML-D8 is a private research branch decision, not a proof, experiment, implementation, or public promotion.
- EML-D8 does not prove EML advantage, theorem discovery, RH, zeta-zero discovery, compiler correctness, runtime performance, formal equivalence, or public readiness.
- D7's no_replicated_holdout_gain label blocks deeper psi-residual search unless a later explicit branch decision reopens it.
