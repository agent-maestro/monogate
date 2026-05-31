# FEF-P40 Affine Polynomial Fixture Runtime Guard

Date: 2026-05-30

Status: `FEF_P40_AFFINE_POLY_FIXTURE_RUNTIME_GUARD_PASS`

Decision: `selected_affine_poly_fixture_emits_validates_and_runtime_executes`

Source fixture: `generated/affine_poly_mix.eml`

## Target Validation

| Target | Emission | Validation | Level | Bytes |
|---|---:|---:|---|---:|
| `c` | `pass` | `pass` | `local_toolchain_syntax` | `576` |
| `cpp` | `pass` | `pass` | `local_toolchain_syntax` | `659` |
| `rust` | `pass` | `pass` | `local_toolchain_syntax` | `555` |
| `python` | `pass` | `pass` | `local_toolchain_syntax` | `365` |
| `go` | `pass` | `pass` | `structural_tokens_tool_unavailable` | `587` |
| `java` | `pass` | `pass` | `local_toolchain_syntax` | `715` |
| `kotlin` | `pass` | `pass` | `structural_tokens_tool_unavailable` | `521` |
| `csharp` | `pass` | `pass` | `structural_tokens_tool_unavailable` | `1239` |
| `javascript` | `pass` | `pass` | `local_toolchain_syntax` | `561` |
| `wasm` | `pass` | `pass` | `wasm_llvm_ir_structural` | `672` |
| `matlab` | `pass` | `pass` | `structural_tokens_tool_unavailable` | `504` |
| `lean` | `pass` | `pass` | `local_toolchain_syntax_with_sorry_allowed` | `613` |
| `zkproof` | `pass` | `pass` | `json_schema_structural_arithmetic_gates` | `1788` |

## Runtime Execution

| Target | Runtime | Agreement | Samples | Max Abs Error |
|---|---:|---:|---:|---:|
| `c` | `pass` | `pass` | `6` | `0.000e+00` |
| `cpp` | `pass` | `pass` | `6` | `0.000e+00` |
| `rust` | `pass` | `pass` | `6` | `0.000e+00` |
| `python` | `pass` | `pass` | `6` | `0.000e+00` |
| `javascript` | `pass` | `pass` | `6` | `0.000e+00` |
| `java` | `pass` | `pass` | `6` | `0.000e+00` |

## Summary

- Free targets checked: `13`
- Emission passes: `13`
- Validation passes: `13`
- Runtime targets checked: `6`
- Runtime sample executions: `36`
- Runtime max absolute error: `0.000e+00`

## Boundary

- Selected affine-polynomial fixture evidence only.
- Runtime execution covers selected installed software targets only.
- This guard does not execute all 13 free targets.
- No all-free-target public-readiness, compiler-correctness, formal-equivalence, publication, runtime-performance, hardware, Pro-target, or all-target claim.
