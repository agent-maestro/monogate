# EML-A13.2 Semantic Output Comparison

Date: 2026-05-29

Status: `EML_A13_2_SEMANTIC_OUTPUT_COMPARISON_PASS`

A13.2 executes selected Python-source kernels after eFrog decompilation
and Forge Python/JavaScript emission, then compares fixed sample grids.

| Case | Samples | Status | Max abs error | Max rel error |
|---|---:|---|---:|---:|
| `gaussian_semantic_compare_v0` | 4 | `pass` | 0.000e+00 | 0.000e+00 |
| `sigmoid_semantic_compare_v0` | 5 | `pass` | 0.000e+00 | 0.000e+00 |
| `poly_quadratic_semantic_compare_v0` | 4 | `pass` | 1.110e-16 | 1.110e-15 |
| `gaussian_stable_holdout_semantic_compare_v0` | 4 | `pass` | 5.551e-17 | 1.570e-15 |
| `rc_decay_holdout_semantic_compare_v0` | 4 | `pass` | 0.000e+00 | 0.000e+00 |
| `voltage_divider_holdout_semantic_compare_v0` | 4 | `pass` | 0.000e+00 | 0.000e+00 |

## Summary

- Cases: `6`
- Samples: `25`
- Passes: `6`
- Max abs error: `1.110e-16`
- Max rel error: `1.570e-15`

## Boundary

- Sample-grid semantic comparison only.
- No Forge or eFrog behavior change.
- No compiler correctness or formal semantic equivalence claim.
- No broad EML advantage, runtime performance, production readiness, or public safety claim.
