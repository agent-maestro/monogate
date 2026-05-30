# EML-S28 Softplus Runtime Bakeoff

Date: 2026-05-29

Status: `EML_S28_SOFTPLUS_RUNTIME_BAKEOFF_PASS`

S28 compares softplus/logaddexp runtime forms after S27 marked softplus
as the next family needing a protected runtime policy. This is private
local runtime boundary evidence, not a public performance or correctness claim.

| Form | Role | Finite | Nonnegative | Dangerous exponent input | Semantic drift samples | Median ns/sample | Max abs error | Recommendation |
|---|---|---|---|---|---:|---:|---:|---|
| `naive_softplus` | `teaching_and_search_baseline` | `False` | `False` | `True` | `0` | `6.1` | `7.105e-15` |  |
| `logaddexp_softplus` | `protected_library_runtime_reference` | `True` | `True` | `False` | `0` | `6.6` | `0.000e+00` | runtime recommendation |
| `branch_stable_softplus` | `protected_branch_runtime_alternative` | `True` | `True` | `False` | `0` | `13.1` | `0.000e+00` |  |
| `clamp60_softplus_caution` | `clamped_search_caution_not_semantic_runtime` | `True` | `True` | `False` | `5120` | `7.1` | `1.140e+03` |  |

## Decision

- Recommended runtime form: `logaddexp_softplus`
- Representation form: `softplus_logsumexp`
- Teaching/search form: `naive_softplus`
- Protected alternative: `branch_stable_softplus`
- Decision: use_logaddexp_softplus_for_runtime; keep softplus/logsumexp as representation/search evidence
- Naive softplus is kept as a caution/teaching form because exponent overflow can make it non-finite.
- Clamp-based softplus is a caution form because it changes large-positive semantics.

## Boundary

- No public performance claim.
- No runtime performance claim beyond local fixture ranking.
- No broad EML advantage or source-family generalization claim.
- No compiler correctness or formal equivalence claim.
- No proof, deployment, package publish, hardware, GPU, certified-safety, or public-readiness claim.
