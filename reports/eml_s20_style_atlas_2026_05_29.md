# EML-S20 Style Atlas

Date: 2026-05-29

Status: `EML_S20_STYLE_ATLAS_PASS`

S20 defines a practical vocabulary for the phrase "EML style" using existing A14/PCC10 evidence.
It is a private review artifact, not a proof, benchmark, compiler change, deployment, or public claim.

## Lay Of The Land

- Evidence infrastructure is now stable enough to carry private candidate packets, saved drafts, and reviewer decisions.
- Forge/eFrog have export packets and sample-grid evidence, but not compiler-correctness or formal-equivalence proof.
- EML looks strongest as a compact semantic/search representation for exponential/log-shaped surfaces.
- Standard or protected math still owns many runtime and stability decisions.
- Guarded or piecewise behavior belongs in guard grammar before any EML lowering is considered.

## Style Classes

### `eml_native`

The core expression shape is directly represented by an EML exponential/log boundary.

Review rule: Treat EML as the search/semantic representation; still require runtime and domain evidence before claiming performance or safety.

### `eml_partial`

EML captures a meaningful substructure, but another operator family remains essential.

Review rule: Keep EML as an explanatory/search component and preserve the non-EML surface explicitly.

### `guard_owned`

Piecewise, branch, or boundary semantics dominate the artifact.

Review rule: Route to guard grammar before any EML lowering or runtime claim.

### `standard_preferred`

Standard or protected math is currently the preferred runtime or source-facing form.

Review rule: Use EML only as optional semantic annotation unless new evidence changes the decision.

### `semantic_only`

The case has sample-grid evidence but no canonical Forge/eFrog roundtrip link.

Review rule: Do not use as roundtrip evidence; require linked hash evidence before toolchain claims.

## Classified Packets

| Source case | Family | Primary style | Tags | Link | Review instruction |
|---|---|---|---|---|---|
| `gaussian_semantic_compare_v0` | `gaussian` | `eml_native` | `eml_native, standard_preferred` | `linked_by_canonical_eml_hash` | Treat EML as the search/semantic representation; still require runtime and domain evidence before claiming performance or safety. |
| `sigmoid_semantic_compare_v0` | `numpy_softplus` | `eml_partial` | `eml_partial, standard_preferred, semantic_only` | `semantic_comparison_only` | Keep EML as an explanatory/search component and preserve the non-EML surface explicitly. |
| `poly_quadratic_semantic_compare_v0` | `unmapped` | `standard_preferred` | `standard_preferred, semantic_only` | `semantic_comparison_only` | Use EML only as optional semantic annotation unless new evidence changes the decision. |
| `gaussian_stable_holdout_semantic_compare_v0` | `gaussian` | `eml_native` | `eml_native, standard_preferred` | `linked_by_canonical_eml_hash` | Treat EML as the search/semantic representation; still require runtime and domain evidence before claiming performance or safety. |
| `rc_decay_holdout_semantic_compare_v0` | `rc_decay` | `eml_native` | `eml_native, standard_preferred` | `linked_by_canonical_eml_hash` | Treat EML as the search/semantic representation; still require runtime and domain evidence before claiming performance or safety. |
| `voltage_divider_holdout_semantic_compare_v0` | `clamp_guard` | `guard_owned` | `guard_owned` | `linked_by_canonical_eml_hash` | Route to guard grammar before any EML lowering or runtime claim. |

## Summary

- Style packets: `6`
- EML-native primary cases: `3`
- EML-partial primary cases: `1`
- Guard-owned primary cases: `1`
- Standard-preferred primary cases: `1`
- Semantic-only tagged cases: `2`

## Boundary

- No broad EML advantage claim.
- No runtime performance claim.
- No compiler correctness or formal equivalence claim.
- No proof, deployment, package publish, or public-readiness claim.
