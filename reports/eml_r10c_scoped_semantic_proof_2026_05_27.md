# EML-R10C Scoped Semantic Proof

Date: 2026-05-27

Status: `EML_R10C_SCOPED_SEMANTIC_PROOF_PASS`

R10C records narrow rewrite certificates for selected lowered forms.
It does not prove compiler correctness or full EML semantics.

| Case | Status | Guards | Steps |
|---|---|---|---:|
| `exp_from_eml_v0` | `scoped_proof_pass` | x is real | 3 |
| `subtraction_boundary_v0` | `scoped_proof_pass` | v > 0; u is real | 3 |
| `bose_boundary_expm1_v0` | `scoped_proof_pass` | x is real | 3 |
| `ln_from_eml_v0` | `scoped_proof_pass` | y > 0 | 5 |

## Summary

- Proof packets: `4`
- Scoped proof pass: `4`
- Blocked: `0`
- Compiler correctness claim: `False`
- Formal compiler proof claim: `False`

## Boundary

- Scoped rewrite certificates only.
- No compiler correctness claim.
- No full EML semantics claim.
- No production lowering or deployment claim.
