# EML-S24 Sigmoid Runtime Bakeoff

Date: 2026-05-29

Status: `EML_S24_SIGMOID_RUNTIME_BAKEOFF_PASS`

S24 compares sigmoid/logistic runtime forms after S23 established the
dedicated stable sigmoid holdout. This is private local runtime boundary
evidence, not a public performance or correctness claim.

| Form | Role | Finite | Bounded | Dangerous exponent input | Median ns/sample | Max abs error | Recommendation |
|---|---|---|---|---|---:|---:|---|
| `naive_sigmoid` | `teaching_and_search_baseline` | `True` | `True` | `True` | `3.0` | `1.110e-16` |  |
| `clamp_stable_sigmoid` | `S23_toolchain_stable_representation` | `True` | `True` | `False` | `4.1` | `9.992e-16` |  |
| `branch_stable_sigmoid` | `protected_branch_runtime_reference` | `True` | `True` | `False` | `4.7` | `0.000e+00` | runtime recommendation |
| `logaddexp_protected_sigmoid` | `protected_library_style_runtime` | `True` | `True` | `False` | `9.1` | `1.110e-16` |  |

## Decision

- Recommended runtime form: `branch_stable_sigmoid`
- Representation form: `clamp_stable_sigmoid`
- Teaching/search form: `naive_sigmoid`
- Decision: use_protected_or_branch_stable_runtime; keep EML/clamp form as representation/search evidence
- Naive sigmoid is kept as a caution/teaching form because the output can remain finite after exponent overflow.

## Boundary

- No public performance claim.
- No runtime performance claim beyond local fixture ranking.
- No broad EML advantage or source-family generalization claim.
- No compiler correctness or formal equivalence claim.
- No proof, deployment, package publish, hardware, GPU, certified-safety, or public-readiness claim.
