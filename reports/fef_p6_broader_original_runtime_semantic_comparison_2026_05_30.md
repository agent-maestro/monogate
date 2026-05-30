# FEF-P6 Broader Original-Runtime Semantic Comparison

Date: 2026-05-30

Status: `FEF_P6_BROADER_ORIGINAL_RUNTIME_SEMANTIC_COMPARISON_PASS`

Decision: `c_rust_original_runtime_semantic_comparison_passed`

FEF-P6 executes selected C and Rust source fixtures through their local
original runtimes, then compares those outputs with Forge Python and
Forge JavaScript targets over fixed sample grids.

| Case | Source | Samples | Status | Max abs error | Max rel error |
|---|---|---:|---|---:|---:|
| `c_gaussian_original_runtime_semantic_compare_v0` | `c` | 4 | `pass` | 0.000e+00 | 0.000e+00 |
| `c_circle_area_original_runtime_semantic_compare_v0` | `c` | 5 | `pass` | 3.411e-13 | 1.086e-15 |
| `rust_gaussian_original_runtime_semantic_compare_v0` | `rust` | 4 | `pass` | 0.000e+00 | 0.000e+00 |
| `rust_sigmoid_original_runtime_semantic_compare_v0` | `rust` | 5 | `pass` | 0.000e+00 | 0.000e+00 |
| `rust_circle_area_original_runtime_semantic_compare_v0` | `rust` | 5 | `pass` | 3.411e-13 | 1.086e-15 |

## Summary

- Cases: `5`
- Samples: `23`
- Passes: `5`
- Source languages: `c,rust`
- Max abs error: `3.411e-13`
- Max rel error: `1.086e-15`
- MATLAB/Octave original runtime: `not_executed`

## Boundary

- C/Rust original-runtime sample-grid comparison only.
- MATLAB/Octave was not executed because no local runtime is available.
- No package publication or checkout claim.
- No compiler correctness or formal semantic equivalence claim.
- No runtime performance, production, Verilog, Lean proof, zkproof, silicon, or hardware claim.
