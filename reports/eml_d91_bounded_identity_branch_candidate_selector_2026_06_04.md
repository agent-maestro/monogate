# EML-D91 Bounded Identity Branch Candidate Selector

Status: `EML_D91_BOUNDED_IDENTITY_BRANCH_CANDIDATE_SELECTOR_PASS`

D91 selects one fresh bounded identity candidate after D90 and leaves feasibility, proof, runtime, public copy, and reviewer intake for later phases.

| Candidate | Status | Score | Next artifact |
|---|---|---:|---|
| `log1p_affine_scaled_boundary_coordinate` | `selected_next_feasibility_packet` | 92 | EML-D92 log1p affine-scaled boundary coordinate feasibility packet |
| `log1p_shifted_boundary_coordinate` | `blocked_duplicate_checked_witness` | 0 | not_selected_duplicate_checked_witness |
| `log1m_shifted_boundary_coordinate` | `blocked_duplicate_checked_witness` | 0 | not_selected_duplicate_checked_witness |
| `bounded_trig_identity_feasibility_selector` | `candidate_later` | 58 | future bounded trig identity feasibility selector |
| `private_reviewer_response_intake` | `candidate_later_requires_real_response` | 44 | future private reviewer response intake |

## Summary

- selected candidate: `log1p_affine_scaled_boundary_coordinate`
- proposed statement: `0 < 1 + a * x -> eml (log (1 + a * x)) (exp 1) = a * x`
- selected next artifact: `EML-D92 log1p affine-scaled boundary coordinate feasibility packet`
- blocked duplicates: `log1p_shifted_boundary_coordinate, log1m_shifted_boundary_coordinate`
- source frozen witness: `MachLib.Real.log1m_shifted_boundary_coordinate_witness`
- runtime control: `protected_log_and_log1p_remain_runtime_controls`
- public copy approved: `False`

## Non-Claims

- EML-D91 is a selector-only private candidate packet after D90; it selects one fresh bounded identity candidate for later feasibility review.
- D91 does not prove the selected affine-scaled shifted-log statement, edit MachLib, typecheck Lean, start implementation, or change runtime lowering.
- D91 explicitly does not reselect the already checked log1p-shifted or log1m-shifted witnesses as fresh work.
- D91 does not record reviewer approval or rejection, approve public copy, promote public surfaces, consume laptop artifacts, touch laptop-owned repos, or claim theorem discovery, runtime advantage, log/log1p replacement, or broad EML superiority.
