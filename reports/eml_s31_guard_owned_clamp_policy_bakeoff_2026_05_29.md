# EML-S31 Guard-Owned Clamp Policy Bakeoff

Date: 2026-05-29

Status: `EML_S31_GUARD_OWNED_CLAMP_POLICY_BAKEOFF_PASS`

S31 records clamp as a guard-owned policy boundary, not a generic
runtime lowering. This is private policy evidence only.

| Form | Role | Finite | Semantic mutation samples | Median ns/sample | Max error vs guard ref | Recommendation |
|---|---|---|---:|---:|---:|---|
| `guard_owned_branch_boundary_surface` | `guard_owned_policy_boundary_reference` | `True` | `9920` | `1.3` | `0.000e+00` | policy recommendation |
| `semantic_clamp_baseline` | `explicit_semantic_clamp_baseline` | `True` | `9920` | `0.4` | `0.000e+00` |  |
| `protected_branch_runtime_candidate` | `runtime_candidate_only_when_guard_owns_semantics` | `True` | `9920` | `1.3` | `0.000e+00` |  |
| `runtime_clamp_caution` | `caution_generic_lowering_changes_semantics_without_guard` | `True` | `9920` | `0.4` | `0.000e+00` |  |

## Decision

- Recommended policy form: `guard_owned_branch_boundary_surface`
- Runtime form when guard-owned: `guard_owned_branch_boundary_surface`
- Caution form: `runtime_clamp_caution`
- Decision: keep_clamp_guard_owned; do_not_apply_generic_runtime_clamp_without_guard_policy_ownership
- Anchor readiness: not ready until an engine guard policy row and anchor packet exist.

## Boundary

- No generic runtime lowering claim.
- No public or runtime performance claim.
- No compiler correctness or formal equivalence claim.
- No broad EML advantage or source-family generalization claim.
- No proof, deployment, package publish, certified-safety, or public-readiness claim.
