# FEF-P25 Selected Zero-Sorry File Index

Date: 2026-05-30

Status: `FEF_P25_SELECTED_ZERO_SORRY_FILE_INDEX_PASS`

Decision: `selected_generated_lean_zero_sorry_file_index_recorded`

| Selected file | Status | Discharged | Remaining | Evidence |
|---|---:|---:|---:|---|
| `verified_add` | `selected_file_zero_sorry` | `1` | `0` | `reports/evidence_packets/fef_p18_selected_lean_proof_discharge.json` |
| `rc_filter` | `selected_file_remaining_sorry` | `4` | `1` | `reports/evidence_packets/fef_p21_rc_filter_lean_proof_discharge.json` |
| `voltage_divider` | `selected_file_zero_sorry` | `3` | `0` | `reports/evidence_packets/fef_p23_voltage_divider_full_lean_proof_discharge.json` |
| `mosfet_iv` | `selected_file_zero_sorry` | `2` | `0` | `reports/evidence_packets/fef_p24_mosfet_full_lean_proof_discharge.json` |

## Summary

- Indexed selected files: `4`
- Selected zero-sorry files: `3`
- Selected files with remaining placeholders: `1`
- Remaining placeholders in indexed files: `1`

## Boundary

- Index over prior selected-file evidence only.
- `rc_filter` remains blocked by `rc_step_response_at_zero`.
- No all-generated-file proof, compiler-correctness, formal-equivalence, or public-readiness claim.
- No package publication, checkout, performance, hardware, or all-target claim.
