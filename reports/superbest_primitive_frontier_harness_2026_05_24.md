# SuperBEST Primitive Frontier Harness

Date: 2026-05-24

Status: `SUPERBEST_PRIMITIVE_FRONTIER_HARNESS_COMPLETE`

No canonical primitive row savings unlocked by this bounded harness. The plausible wins remain domain-narrowing, sign/branch-aware variants, or approximation-method work.

## Summary

- Candidates tested: 9
- Primitive improvement candidates: 0
- Invalid/domain-limited attempts: 2
- Confirmed existing routes: 5
- Branched references only: 2

## Candidate Results

| Candidate | Domain | Nodes | Classification | Failures |
|---|---|---:|---|---:|
| `mul_positive_1n_route` | positive | 1 | CONFIRMED_EXISTING_ROUTE | 0 |
| `mul_general_positive_route_attempt` | general_nonzero | 1 | INVALID_OR_DOMAIN_LIMITED | 18 |
| `mul_general_sign_branched_reference` | general_with_zero | 4 | BRANCHED_REFERENCE_ONLY | 0 |
| `div_positive_2n_route` | positive | 2 | CONFIRMED_EXISTING_ROUTE | 0 |
| `div_general_positive_route_attempt` | general_nonzero | 2 | INVALID_OR_DOMAIN_LIMITED | 18 |
| `div_general_sign_branched_reference` | general_nonzero | 5 | BRANCHED_REFERENCE_ONLY | 0 |
| `add_general_2n_route` | general_with_zero | 2 | CONFIRMED_EXISTING_ROUTE | 0 |
| `sub_general_2n_route` | general_with_zero | 2 | CONFIRMED_EXISTING_ROUTE | 0 |
| `neg_general_2n_route` | all_real | 2 | CONFIRMED_EXISTING_ROUTE | 0 |

## Row Frontier Notes

- `mul_general`: `BLOCKED_BY_SIGN_DOMAIN` - The 1n positive route uses log(x), so it fails for x<=0. Sign-aware versions require abs/sign branching and are not single primitive trees.
- `div_general`: `BLOCKED_BY_NUMERATOR_SIGN_DOMAIN` - The 2n positive route uses log(x), so it fails for x<=0. Sign-aware division requires abs/sign branching and zero-denominator handling.
- `add_general`: `NO_1N_CANDIDATE_FOUND_IN_HARNESS` - Canonical 2n route passes all-real grid; this harness found no 1n all-real candidate.
- `sub_general`: `NO_1N_CANDIDATE_FOUND_IN_HARNESS` - Canonical 2n route passes all-real grid; this harness found no 1n all-real candidate.
- `neg_general`: `NO_1N_CANDIDATE_FOUND_IN_HARNESS` - Canonical 2n route passes all-real grid; this harness found no 1n all-real candidate.
- `sin_cos`: `NUMERICAL_METHOD_FRONTIER_NOT_PRIMITIVE_ROW` - Further sin/cos gains are likely approximation-method work, not a primitive row demotion in this harness.

## Boundary

- Internal harness only.
- No canonical row table changed.
- No new row optimality claim.
- No public theorem/proof/open-problem claim.
