# EML-S27 Export Policy Registry

Date: 2026-05-29

Status: `EML_S27_EXPORT_POLICY_REGISTRY_PASS`

S27 makes the export advisory layer systematic. It maps source families
to representation forms, runtime forms, caution forms, evidence sources,
and unresolved gaps. It does not change Forge, eFrog, generated code, or runtime behavior.

| Family | Representation | Runtime | Status | Gaps |
|---|---|---|---|---:|
| `clamp_guard` | `guard_owned_branch_boundary_surface` | `guard_owned_branch_boundary_surface` | `guard_policy_drilldown_attached` | 6 |
| `gaussian` | `eml_exponential_quadratic_envelope` | `log_domain_pdf` | `runtime_advisory_attached` | 5 |
| `numpy_softplus` | `softplus_logsumexp` | `logaddexp_softplus` | `runtime_advisory_attached` | 5 |
| `rc_decay` | `eml_exponential_decay_envelope` | `standard_or_protected_runtime_until_benchmarked` | `default_until_family_runtime_bakeoff` | 3 |
| `stable_sigmoid` | `clamp_stable_sigmoid` | `branch_stable_sigmoid` | `runtime_advisory_attached` | 5 |
| `stretched_exponential` | `eml_stretched_exponential_envelope` | `standard_or_protected_runtime_until_benchmarked` | `default_until_family_runtime_bakeoff` | 3 |
| `unmapped` | `unmapped_semantic_export_surface` | `standard_or_protected_runtime_until_benchmarked` | `review_before_runtime_policy` | 3 |

## Summary

- Policies: `7`
- Covered export packets: `8`
- Runtime advisory attached policies: `3`
- Default-until-benchmarked policies: `3`
- Stable sigmoid policy attached: `True`
- Softplus policy attached: `True`
- Gaussian policy attached: `True`
- Guard-owned clamp policy attached: `True`
- Next runtime bakeoff candidate: `stretched_exponential`

## Boundary

- No Forge/eFrog behavior change.
- No generated target code change.
- No compiler correctness or formal equivalence claim.
- No runtime or public performance claim.
- No broad EML advantage, deployment, certified-safety, or public-readiness claim.
