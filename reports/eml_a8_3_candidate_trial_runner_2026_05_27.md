# EML-A8.3 Candidate Trial Runner

Date: 2026-05-27

Status: `EML_A8_3_CANDIDATE_TRIAL_RUNNER_PASS`

A8.3 runs the first bounded trials from the A8.2 discovery queue.
It keeps the result private/research-oriented and does not promote any
candidate to a public Atlas claim.

| Candidate | Trial class | Profiles | Interpretation |
|---|---|---:|---|
| `safe_log_domain_lift_v0` | `eml_proof_shape_supported` | `3` | Trial supports the bounded proof-shape claim: exp(theta) produces positive internal log-domain coordinates on all profiles. |
| `ln_from_eml_boundary_v0` | `mixed_identity_supported` | `3` | Trial supports the identity/teaching lane, while standard log remains the runtime form. |
| `expm1_runtime_anti_example_v1` | `standard_runtime_win_confirmed` | `3` | Trial confirms the expected anti-example: protected expm1 beats raw exp(x)-1 near zero. |

## Summary

- Trials: `3`
- Proof-shape supported: `1`
- Mixed identity supported: `1`
- Standard runtime win confirmed: `1`
- Blocked: `0`
- Candidate proved: `False`
- EML advantage proved: `False`

## Boundary

- Bounded deterministic candidate trials only.
- No public Atlas promotion, theorem discovery, compiler correctness, runtime performance, broad EML superiority, or deployment claim.
