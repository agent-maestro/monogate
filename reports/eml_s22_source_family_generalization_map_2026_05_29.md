# EML-S22 Source-Family Generalization Map

Date: 2026-05-29

Status: `EML_S22_SOURCE_FAMILY_MAP_PASS`

S22 turns the next EML research question into a deterministic source-family map.
It is private triage over existing evidence, not a proof, benchmark, compiler change, or public claim.

## Decision Rule

Formula: `representationCompactness + searchFriendliness + semanticPreservation + runtimeStability + lowGuardBurden + decompilerReadability + roundtripMaturity`

| Family | Kind | Score | Lane | EML role | Runtime recommendation |
|---|---|---:|---|---|---|
| `sigmoid_logistic` | `bounded_transition` | `30` | `promote_next_source_family_holdout` | `bounded_exponential_transition_representation` | `standard_or_protected_sigmoid_runtime_until_large_range_benchmark` |
| `damped_oscillator` | `oscillatory_envelope` | `26` | `keep_as_review_candidate` | `exponential_damping_envelope_only` | `keep_sine_surface_standard_and_use_eml_for_envelope_search` |
| `softplus_logsumexp` | `log_domain_protected` | `26` | `keep_as_review_candidate` | `log_domain_semantic_representation_with_protected_runtime_requirement` | `protected_logaddexp_runtime_for_overflow_prone_ranges` |

## Promoted Candidate

- Family: `sigmoid_logistic`
- Promotion id: `sigmoid_logistic_next_holdout_candidate_v0`
- Next action: `promote_sigmoid_logistic_to_dedicated_source_holdout_with_overflow_guard_profile`

Required next evidence:

- dedicated eFrog holdout trial for examples/sigmoid.py or stable_sigmoid.py
- large positive/negative range profile to expose overflow boundaries
- Forge/eFrog roundtrip hash link for the dedicated holdout fixture
- semantic sample-grid packet distinct from the existing basic sigmoid example
- claim guard that keeps runtime and generalization claims false

## Boundary

- No broad EML advantage claim.
- No source-family generalization claim.
- No runtime performance claim.
- No compiler correctness or formal equivalence claim.
- No proof, deployment, package publish, or public-readiness claim.
