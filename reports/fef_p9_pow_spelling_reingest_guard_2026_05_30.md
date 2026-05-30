# FEF-P9 Pow-Spelling Re-ingest Guard

Date: 2026-05-30

Status: `FEF_P9_POW_SPELLING_REINGEST_GUARD_PASS`

Decision: `pow_spelling_reingest_guard_passed`

FEF-P9 closes the selected power-expression generated-target
re-ingest holdout from FEF-P8 by requiring re-ingested EML to use
`pow(...)` rather than caret power.

| Case | Source | Generated target | Samples | Pow guard | Status | Max abs error |
|---|---|---|---:|---|---|---:|
| `javascript_gaussian_pow_spelling_reingest_v0` | `javascript` | `python` | 4 | `pass` | `pass` | 0.000e+00 |
| `javascript_gaussian_pow_spelling_reingest_v0` | `javascript` | `javascript` | 4 | `pass` | `pass` | 0.000e+00 |
| `javascript_circle_area_pow_spelling_reingest_v0` | `javascript` | `python` | 5 | `pass` | `pass` | 0.000e+00 |
| `javascript_circle_area_pow_spelling_reingest_v0` | `javascript` | `javascript` | 5 | `pass` | `pass` | 3.411e-13 |
| `c_circle_area_pow_spelling_reingest_v0` | `c` | `python` | 5 | `pass` | `pass` | 0.000e+00 |
| `c_circle_area_pow_spelling_reingest_v0` | `c` | `javascript` | 5 | `pass` | `pass` | 3.411e-13 |
| `rust_circle_area_pow_spelling_reingest_v0` | `rust` | `python` | 5 | `pass` | `pass` | 0.000e+00 |
| `rust_circle_area_pow_spelling_reingest_v0` | `rust` | `javascript` | 5 | `pass` | `pass` | 3.411e-13 |

## Summary

- Packets: `8`
- Samples: `38`
- Passes: `8`
- Pow spelling guard pass: `True`
- Caret power token count: `0`
- Max abs error: `3.411e-13`
- Max rel error: `1.086e-15`

## Boundary

- Selected power-shaped generated-target re-ingest only.
- No package publication or checkout claim.
- No compiler correctness or formal semantic equivalence claim.
- No runtime performance, production, Verilog, Lean proof, zkproof, silicon, or hardware claim.
