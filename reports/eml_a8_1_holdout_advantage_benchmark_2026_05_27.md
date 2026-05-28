# EML-A8.1 Holdout Advantage Benchmark

Date: 2026-05-27

Status: `EML_A8_1_HOLDOUT_ADVANTAGE_BENCHMARK_PASS`

A8.1 reruns the Advantage Lab cases on shifted, edge, and stress
profiles, then adds negative controls. It is a falsification layer,
not a general EML advantage claim.

| Case | Source | Holdout | Confidence | Profiles |
|---|---|---|---|---:|
| `exp_from_eml_v0` | `eml_win` | `eml_win_replicated` | `retained` | `3` |
| `subtraction_boundary_v0` | `standard_win` | `standard_win_replicated` | `retained` | `3` |
| `bose_boundary_expm1_v0` | `standard_win` | `standard_win_replicated` | `retained` | `3` |
| `ln_from_eml_v0` | `mixed` | `mixed_replicated` | `retained` | `3` |
| `softplus_pair_v0` | `standard_win` | `standard_win_replicated` | `retained` | `3` |
| `sigmoid_derivative_v0` | `standard_win` | `standard_win_replicated` | `retained` | `3` |
| `gaussian_energy_v0` | `mixed` | `mixed_replicated` | `retained` | `3` |
| `prime_signature_log_recovery_v0` | `mixed` | `mixed_replicated` | `retained` | `3` |
| `psi_residual_template_v0` | `research_only` | `research_only_retained` | `retained` | `1` |
| `gaussian_bumps_negative_control_v0` | `negative_control` | `standard_win_replicated` | `control_pass` | `1` |
| `arbitrary_polynomial_negative_control_v0` | `negative_control` | `standard_win_replicated` | `control_pass` | `1` |
| `logaddexp_negative_control_v0` | `negative_control` | `standard_win_replicated` | `control_pass` | `1` |

## Summary

- Holdout packets: `12`
- Retained: `9`
- Weakened: `0`
- Blocked: `0`
- Negative controls passed: `3`
- EML advantage proved: `False`
- General EML superiority claim: `False`

## Boundary

- No proof of EML advantage.
- No broad EML superiority claim.
- No compiler correctness, theorem discovery, RH, zeta-zero, hardware, deployment, or public performance claim.
