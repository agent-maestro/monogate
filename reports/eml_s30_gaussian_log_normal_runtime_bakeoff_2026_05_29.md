# EML-S30 Gaussian / Log-Normal Runtime Bakeoff

Date: 2026-05-29

Status: `EML_S30_GAUSSIAN_LOG_NORMAL_RUNTIME_BAKEOFF_PASS`

S30 compares Gaussian/log-normal PDF runtime forms after S27 left the
Gaussian family on a default policy. This is private local runtime boundary
evidence, not a public performance or correctness claim.

| Form | Role | Finite | Nonnegative | Clamped tail samples | Semantic drift samples | Median ns/sample | Max abs error | Recommendation |
|---|---|---|---|---:|---:|---:|---:|---|
| `standard_pdf` | `standard_runtime_baseline` | `True` | `True` | `0` | `0` | `3.5` | `3.331e-16` |  |
| `log_domain_pdf` | `protected_log_domain_runtime_reference` | `True` | `True` | `0` | `0` | `3.5` | `0.000e+00` | runtime recommendation |
| `eml_exponential_quadratic_envelope` | `representation_and_search_form` | `True` | `True` | `0` | `0` | `3.5` | `3.331e-16` |  |
| `clamp_exponent_caution` | `clamped_runtime_caution_not_semantic_runtime` | `True` | `True` | `11312` | `1122` | `4.0` | `3.192e-01` |  |

## Decision

- Recommended runtime form: `log_domain_pdf`
- Representation form: `eml_exponential_quadratic_envelope`
- Teaching/search form: `eml_exponential_quadratic_envelope`
- Protected alternative: `standard_pdf`
- Decision: use_log_domain_pdf_for_gaussian_and_log_normal_runtime; keep EML exponential-quadratic envelope as representation/search evidence
- Clamp-based exponent protection is a caution form because it changes small-tail semantics.

## Boundary

- No public performance claim.
- No runtime performance claim beyond local fixture ranking.
- No broad EML advantage or source-family generalization claim.
- No compiler correctness or formal equivalence claim.
- No proof, deployment, package publish, hardware, GPU, certified-safety, or public-readiness claim.
