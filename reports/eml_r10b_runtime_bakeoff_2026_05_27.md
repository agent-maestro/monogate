# EML-R10B Runtime Bakeoff

Date: 2026-05-27

Status: `EML_R10B_RUNTIME_BAKEOFF_PASS`

R10B validates R12 generated Python stubs on broader deterministic
float64 and float32 grids. It is local runtime evidence, not compiler
correctness or formal semantic equivalence.

| Case | Runtime | Float64 max rel | Float32 max rel | Float64 ns/sample | Float32 ns/sample |
|---|---|---:|---:|---:|---:|
| `exp_from_eml_v0` | `pass` | 0.000e+00 | 5.820e-08 | 2.5 | 1.8 |
| `subtraction_boundary_v0` | `pass` | 0.000e+00 | 5.957e-08 | 0.5 | 0.5 |
| `bose_boundary_expm1_v0` | `pass` | 0.000e+00 | 5.000e-09 | 2.4 | 1.8 |
| `ln_from_eml_v0` | `pass` | 0.000e+00 | 5.543e-08 | 2.6 | 1.9 |
| `softplus_pair_v0` | `pass` | 0.000e+00 | 5.629e-08 | 4.4 | 4.2 |
| `sigmoid_derivative_v0` | `pass` | 0.000e+00 | 1.000e+00 | 11.7 | 10.2 |
| `gaussian_energy_v0` | `pass` | 0.000e+00 | 9.806e-07 | 3.8 | 5.1 |

## Summary

- Bakeoff packets: `7`
- Pass: `7`
- Fail: `0`
- Dtype runs: `14`
- Compiler behavior changed: `False`
- Compiler correctness claim: `False`

## Boundary

- Local generated Python stub bakeoff only.
- No compiler correctness claim.
- No formal semantic equivalence claim.
- No public performance, hardware, deployment, or production lowering claim.
