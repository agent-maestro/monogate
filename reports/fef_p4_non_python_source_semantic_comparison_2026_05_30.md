# FEF-P4 Non-Python Source Semantic Comparison

Date: 2026-05-30

Status: `FEF_P4_NON_PYTHON_SOURCE_SEMANTIC_COMPARISON_PASS`

Decision: `javascript_source_semantic_comparison_passed`

FEF-P4 runs selected JavaScript source fixtures through eFrog and Forge,
then compares original JavaScript runtime output with generated Python
and JavaScript target outputs over fixed sample grids.

| Case | Source | Samples | Status | Max abs error | Max rel error |
|---|---|---:|---|---:|---:|
| `javascript_gaussian_semantic_compare_v0` | `javascript` | 4 | `pass` | 0.000e+00 | 0.000e+00 |
| `javascript_sigmoid_semantic_compare_v0` | `javascript` | 5 | `pass` | 0.000e+00 | 0.000e+00 |
| `javascript_circle_area_semantic_compare_v0` | `javascript` | 5 | `pass` | 3.411e-13 | 1.086e-15 |

## Summary

- Cases: `3`
- Samples: `14`
- Passes: `3`
- Max abs error: `3.411e-13`
- Max rel error: `1.086e-15`

## Boundary

- JavaScript-source sample-grid comparison only.
- No package publication or checkout claim.
- No compiler correctness or formal semantic equivalence claim.
- No runtime performance, production, Verilog, Lean proof, zkproof, or silicon claim.
