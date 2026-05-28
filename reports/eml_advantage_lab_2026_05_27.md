# EML Advantage Lab

Date: 2026-05-27

Status: `EML_ADVANTAGE_LAB_PASS`

The Advantage Lab compares EML-native and standard representations across
compression, runtime, stability, lowering, proof, and search evidence.
It is a bounded research surface, not a general superiority claim.

| Case | Class | Compression | Runtime | Stability | Lowering | Proof |
|---|---|---|---|---|---|---|
| `exp_from_eml_v0` | `eml_win` | `same_surface_count` | `standard_faster_local` | `similar_or_mixed` | `lower_to_hybrid` | `scoped_certificate_present` |
| `subtraction_boundary_v0` | `standard_win` | `standard_smaller_surface` | `standard_faster_local` | `standard_more_stable` | `lower_to_standard` | `scoped_certificate_present` |
| `bose_boundary_expm1_v0` | `standard_win` | `same_surface_count` | `standard_faster_local` | `standard_more_stable` | `lower_to_standard` | `scoped_certificate_present` |
| `ln_from_eml_v0` | `mixed` | `standard_smaller_surface` | `standard_faster_local` | `similar_or_mixed` | `lower_to_standard` | `scoped_certificate_present` |
| `softplus_pair_v0` | `standard_win` | `standard_smaller_surface` | `standard_faster_local` | `standard_more_stable` | `lower_to_standard` | `proof_obligations_open` |
| `sigmoid_derivative_v0` | `standard_win` | `standard_smaller_surface` | `eml_faster_local` | `standard_more_stable` | `lower_to_standard` | `proof_obligations_open` |
| `gaussian_energy_v0` | `mixed` | `standard_smaller_surface` | `standard_faster_local` | `similar_or_mixed` | `lower_to_standard` | `proof_obligations_open` |
| `prime_signature_log_recovery_v0` | `mixed` | `standard_smaller_surface` | `not_benchmarked` | `identity_numeric_match_but_standard_simpler` | `lower_to_standard` | `proof_obligations_open` |
| `psi_residual_template_v0` | `research_only` | `eml_smaller_template` | `not_runtime_fixture` | `not_finite_precision_fixture` | `research_only` | `not_a_proof_fixture` |

## Summary

- Packets: `9`
- EML wins: `1`
- Standard wins: `4`
- Mixed: `3`
- Research-only: `1`
- General EML superiority claim: `False`
- Compiler correctness claim: `False`

## Boundary

- No general EML superiority claim.
- No public performance or savings claim.
- No compiler correctness claim.
- No theorem discovery, RH, zeta-zero, hardware, or deployment claim.
