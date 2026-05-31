# FEF-P41 Four-Fixture Capability Matrix Refresh

Date: 2026-05-30

Status: `FEF_P41_FOUR_FIXTURE_CAPABILITY_MATRIX_REFRESH_PASS`

Decision: `selected_four_fixture_capability_matrix_refreshed`

## Runtime Sources

- `verified_add`: `examples/verified_add.eml` (`36` samples, max abs error `0.000e+00`)
- `runtime_helper_mix`: `generated/runtime_helper_mix.eml` (`30` samples, max abs error `4.441e-16`)
- `clamp_guard_mix`: `generated/clamp_guard_mix.eml` (`42` samples, max abs error `0.000e+00`)
- `affine_poly_mix`: `generated/affine_poly_mix.eml` (`36` samples, max abs error `0.000e+00`)

## Matrix

| Fixture | Target | Emission | Validation | Runtime | Samples | Max Abs Error |
|---|---|---:|---:|---:|---:|---:|
| `verified_add` | `c` | `pass` | `pass` | `pass` | `6` | `0.000e+00` |
| `verified_add` | `cpp` | `pass` | `pass` | `pass` | `6` | `0.000e+00` |
| `verified_add` | `rust` | `pass` | `pass` | `pass` | `6` | `0.000e+00` |
| `verified_add` | `python` | `pass` | `pass` | `pass` | `6` | `0.000e+00` |
| `verified_add` | `go` | `pass` | `pass` | `not_attempted` | `0` | `n/a` |
| `verified_add` | `java` | `pass` | `pass` | `pass` | `6` | `0.000e+00` |
| `verified_add` | `kotlin` | `pass` | `pass` | `not_attempted` | `0` | `n/a` |
| `verified_add` | `csharp` | `pass` | `pass` | `not_attempted` | `0` | `n/a` |
| `verified_add` | `javascript` | `pass` | `pass` | `pass` | `6` | `0.000e+00` |
| `verified_add` | `wasm` | `pass` | `pass` | `not_attempted` | `0` | `n/a` |
| `verified_add` | `matlab` | `pass` | `pass` | `not_attempted` | `0` | `n/a` |
| `verified_add` | `lean` | `pass` | `pass` | `not_attempted` | `0` | `n/a` |
| `verified_add` | `zkproof` | `pass` | `pass` | `not_attempted` | `0` | `n/a` |
| `runtime_helper_mix` | `c` | `pass` | `pass` | `pass` | `5` | `0.000e+00` |
| `runtime_helper_mix` | `cpp` | `pass` | `pass` | `pass` | `5` | `0.000e+00` |
| `runtime_helper_mix` | `rust` | `pass` | `pass` | `pass` | `5` | `0.000e+00` |
| `runtime_helper_mix` | `python` | `pass` | `pass` | `pass` | `5` | `0.000e+00` |
| `runtime_helper_mix` | `go` | `pass` | `pass` | `not_attempted` | `0` | `n/a` |
| `runtime_helper_mix` | `java` | `pass` | `pass` | `pass` | `5` | `4.441e-16` |
| `runtime_helper_mix` | `kotlin` | `pass` | `pass` | `not_attempted` | `0` | `n/a` |
| `runtime_helper_mix` | `csharp` | `pass` | `pass` | `not_attempted` | `0` | `n/a` |
| `runtime_helper_mix` | `javascript` | `pass` | `pass` | `pass` | `5` | `0.000e+00` |
| `runtime_helper_mix` | `wasm` | `pass` | `pass` | `not_attempted` | `0` | `n/a` |
| `runtime_helper_mix` | `matlab` | `pass` | `pass` | `not_attempted` | `0` | `n/a` |
| `runtime_helper_mix` | `lean` | `pass` | `pass` | `not_attempted` | `0` | `n/a` |
| `runtime_helper_mix` | `zkproof` | `pass` | `pass` | `not_attempted` | `0` | `n/a` |
| `clamp_guard_mix` | `c` | `pass` | `pass` | `pass` | `7` | `0.000e+00` |
| `clamp_guard_mix` | `cpp` | `pass` | `pass` | `pass` | `7` | `0.000e+00` |
| `clamp_guard_mix` | `rust` | `pass` | `pass` | `pass` | `7` | `0.000e+00` |
| `clamp_guard_mix` | `python` | `pass` | `pass` | `pass` | `7` | `0.000e+00` |
| `clamp_guard_mix` | `go` | `pass` | `pass` | `not_attempted` | `0` | `n/a` |
| `clamp_guard_mix` | `java` | `pass` | `pass` | `pass` | `7` | `0.000e+00` |
| `clamp_guard_mix` | `kotlin` | `pass` | `pass` | `not_attempted` | `0` | `n/a` |
| `clamp_guard_mix` | `csharp` | `pass` | `pass` | `not_attempted` | `0` | `n/a` |
| `clamp_guard_mix` | `javascript` | `pass` | `pass` | `pass` | `7` | `0.000e+00` |
| `clamp_guard_mix` | `wasm` | `pass` | `pass` | `not_attempted` | `0` | `n/a` |
| `clamp_guard_mix` | `matlab` | `pass` | `pass` | `not_attempted` | `0` | `n/a` |
| `clamp_guard_mix` | `lean` | `pass` | `pass` | `not_attempted` | `0` | `n/a` |
| `clamp_guard_mix` | `zkproof` | `pass` | `pass` | `not_attempted` | `0` | `n/a` |
| `affine_poly_mix` | `c` | `pass` | `pass` | `pass` | `6` | `0.000e+00` |
| `affine_poly_mix` | `cpp` | `pass` | `pass` | `pass` | `6` | `0.000e+00` |
| `affine_poly_mix` | `rust` | `pass` | `pass` | `pass` | `6` | `0.000e+00` |
| `affine_poly_mix` | `python` | `pass` | `pass` | `pass` | `6` | `0.000e+00` |
| `affine_poly_mix` | `go` | `pass` | `pass` | `not_attempted` | `0` | `n/a` |
| `affine_poly_mix` | `java` | `pass` | `pass` | `pass` | `6` | `0.000e+00` |
| `affine_poly_mix` | `kotlin` | `pass` | `pass` | `not_attempted` | `0` | `n/a` |
| `affine_poly_mix` | `csharp` | `pass` | `pass` | `not_attempted` | `0` | `n/a` |
| `affine_poly_mix` | `javascript` | `pass` | `pass` | `pass` | `6` | `0.000e+00` |
| `affine_poly_mix` | `wasm` | `pass` | `pass` | `not_attempted` | `0` | `n/a` |
| `affine_poly_mix` | `matlab` | `pass` | `pass` | `not_attempted` | `0` | `n/a` |
| `affine_poly_mix` | `lean` | `pass` | `pass` | `not_attempted` | `0` | `n/a` |
| `affine_poly_mix` | `zkproof` | `pass` | `pass` | `not_attempted` | `0` | `n/a` |

## Summary

- Fixtures checked: `4`
- Free targets checked: `13`
- Matrix cells checked: `52`
- Emission passes: `52`
- Validation passes: `52`
- Runtime overlay fixtures: `4`
- Runtime overlay cells: `24`
- Runtime overlay sample executions: `144`
- Runtime overlay max absolute error: `4.441e-16`

## Boundary

- Selected four-fixture capability matrix refresh only.
- Runtime overlays cover selected C, C++, Rust, Python, JavaScript, and Java generated targets only.
- This refresh does not execute all 13 free targets.
- No arbitrary branch/control-flow support claim.
- No all-free-target public-readiness, compiler-correctness, formal-equivalence, or publication claim.
- No runtime performance, package publication, checkout, hardware, Pro-target, or all-target claim.
