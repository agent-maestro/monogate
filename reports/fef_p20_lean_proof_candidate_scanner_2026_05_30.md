# FEF-P20 Lean Proof Candidate Scanner

Date: 2026-05-30

Status: `FEF_P20_LEAN_PROOF_CANDIDATE_SCANNER_PASS`

Decision: `selected_lean_proof_candidate_scan_recorded`

| Case | Obligations | Candidate found | Blocked |
|---|---:|---:|---:|
| `verified_add_proof_candidate_scan_v0` | 1 | 1 | 0 |
| `clamp_bounded_proof_candidate_scan_v0` | 1 | 0 | 1 |
| `voltage_divider_proof_candidate_scan_v0` | 3 | 2 | 1 |
| `pid_controller_proof_candidate_scan_v0` | 1 | 0 | 1 |
| `rc_filter_proof_candidate_scan_v0` | 5 | 4 | 1 |
| `sine_oscillator_proof_candidate_scan_v0` | 1 | 0 | 1 |
| `smoothstep_proof_candidate_scan_v0` | 1 | 0 | 1 |
| `mosfet_iv_proof_candidate_scan_v0` | 2 | 1 | 1 |

## Summary

- Cases: `8`
- Proof obligations scanned: `15`
- Candidate found: `8`
- Blocked candidates: `7`
- Candidate coverage ratio: `0.533`

## Boundary

- Candidate scanner only; no generated source rewrite.
- Candidate-found obligations are not automatically proof-readiness claims.
- Blocked obligations remain visible.
- No compiler-correctness, formal-equivalence, public-readiness, package, performance, hardware, or all-target claim.
