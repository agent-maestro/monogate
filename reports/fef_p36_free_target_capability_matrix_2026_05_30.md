# FEF-P36 Free Target Capability Matrix

Date: 2026-05-30

Status: `FEF_P36_FREE_TARGET_CAPABILITY_MATRIX_PASS`

Decision: `selected_free_target_capability_matrix_with_runtime_overlay`

## Fixtures

- `verified_add`: `examples/verified_add.eml` (arithmetic)
- `runtime_helper_mix`: `generated/runtime_helper_mix.eml` (runtime_helper)
- `clamp_guard_mix`: `generated/clamp_guard_mix.eml` (clamp_guard)

## Matrix

| Fixture | Target | Emission | Validation | Runtime | Samples | Max Abs Error |
|---|---|---:|---:|---:|---:|---:|
| `verified_add` | `c` | `pass` | `pass` | `not_attempted` | `0` | `n/a` |
| `verified_add` | `cpp` | `pass` | `pass` | `not_attempted` | `0` | `n/a` |
| `verified_add` | `rust` | `pass` | `pass` | `not_attempted` | `0` | `n/a` |
| `verified_add` | `python` | `pass` | `pass` | `not_attempted` | `0` | `n/a` |
| `verified_add` | `go` | `pass` | `pass` | `not_attempted` | `0` | `n/a` |
| `verified_add` | `java` | `pass` | `pass` | `not_attempted` | `0` | `n/a` |
| `verified_add` | `kotlin` | `pass` | `pass` | `not_attempted` | `0` | `n/a` |
| `verified_add` | `csharp` | `pass` | `pass` | `not_attempted` | `0` | `n/a` |
| `verified_add` | `javascript` | `pass` | `pass` | `not_attempted` | `0` | `n/a` |
| `verified_add` | `wasm` | `pass` | `pass` | `not_attempted` | `0` | `n/a` |
| `verified_add` | `matlab` | `pass` | `pass` | `not_attempted` | `0` | `n/a` |
| `verified_add` | `lean` | `pass` | `pass` | `not_attempted` | `0` | `n/a` |
| `verified_add` | `zkproof` | `pass` | `pass` | `not_attempted` | `0` | `n/a` |
| `runtime_helper_mix` | `c` | `pass` | `pass` | `not_attempted` | `0` | `n/a` |
| `runtime_helper_mix` | `cpp` | `pass` | `pass` | `not_attempted` | `0` | `n/a` |
| `runtime_helper_mix` | `rust` | `pass` | `pass` | `not_attempted` | `0` | `n/a` |
| `runtime_helper_mix` | `python` | `pass` | `pass` | `not_attempted` | `0` | `n/a` |
| `runtime_helper_mix` | `go` | `pass` | `pass` | `not_attempted` | `0` | `n/a` |
| `runtime_helper_mix` | `java` | `pass` | `pass` | `not_attempted` | `0` | `n/a` |
| `runtime_helper_mix` | `kotlin` | `pass` | `pass` | `not_attempted` | `0` | `n/a` |
| `runtime_helper_mix` | `csharp` | `pass` | `pass` | `not_attempted` | `0` | `n/a` |
| `runtime_helper_mix` | `javascript` | `pass` | `pass` | `not_attempted` | `0` | `n/a` |
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

## Summary

- Fixtures checked: `3`
- Free targets checked: `13`
- Matrix cells checked: `39`
- Emission passes: `39`
- Validation passes: `39`
- Runtime overlay cells: `6`
- Runtime overlay sample executions: `42`
- Runtime overlay max absolute error: `0.000e+00`

## Boundary

- Selected fixture capability matrix only.
- Runtime overlay covers selected clamp_guard_mix software targets only.
- This guard does not execute all 13 free targets.
- No arbitrary branch/control-flow support claim.
- No all-free-target public-readiness, compiler-correctness, formal-equivalence, or publication claim.
- No runtime performance, package publication, checkout, hardware, Pro-target, or all-target claim.
