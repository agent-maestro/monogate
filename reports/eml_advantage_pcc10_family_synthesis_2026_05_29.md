# EML-ADV-PCC10 Family-Level Synthesis

Date: 2026-05-29

Status: `EML_ADV_PCC10_FAMILY_SYNTHESIS_PASS`

PCC10 summarizes the current EML Advantage source-family phase.
It is a private synthesis artifact, not a broad EML advantage claim.

| Family | Surface | Finding | EML role | Runtime recommendation | Profiles |
|---|---|---|---|---|---:|
| `rc_decay` | `smooth_exponential_decay` | `semantic_search_representation_tie` | `full_exponential_envelope_representation` | `standard_or_protected_runtime_until_benchmarked` | `4` |
| `gaussian` | `quadratic_exponent_gaussian` | `semantic_search_representation_tie` | `full_exponential_kernel_representation` | `standard_or_protected_runtime_until_benchmarked` | `4` |
| `damped_wave` | `oscillatory_with_decay` | `partial_eml_coverage` | `damping_envelope_only` | `standard_sine_surface_still_required` | `4` |
| `numpy_softplus` | `log_domain_softplus` | `semantic_tie_with_protected_lowering_guard` | `safe_range_representation` | `protected_logaddexp_for_overflow_prone_ranges` | `5` |
| `clamp_guard` | `guarded_piecewise_branching` | `guard_semantics_not_eml_operator_win` | `none_guard_grammar_role` | `preserve_guard_domains_before_lowering` | `5` |

## Summary

- Source families: `5`
- Profiles: `22`
- Representation helpful families: `4`
- Full EML coverage families: `2`
- Partial EML coverage families: `2`
- Protected runtime required families: `1`
- Guard grammar required families: `1`
- Runtime win families: `0`
- Recommended pause point: `True`

## Boundary

- Private family-level synthesis only.
- No broad EML advantage, source-family generalization, runtime-performance, compiler-correctness, formal-equivalence, proof, production, deployment, or public-readiness claim.
