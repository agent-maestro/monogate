# FEF-P33 Free Target Fixture Matrix

Date: 2026-05-30

Status: `FEF_P33_FREE_TARGET_FIXTURE_MATRIX_PASS`

Decision: `selected_fixture_matrix_all_free_targets_emit_and_validate`

## Fixtures

- `verified_add`: `examples/verified_add.eml` (arithmetic)
- `runtime_helper_mix`: `generated/runtime_helper_mix.eml` (runtime_helper)

## Matrix

| Fixture | Target | Emission | Validation | Level | Bytes |
|---|---|---:|---:|---|---:|
| `verified_add` | `c` | `pass` | `pass` | `local_toolchain_syntax` | `693` |
| `verified_add` | `cpp` | `pass` | `pass` | `local_toolchain_syntax` | `652` |
| `verified_add` | `rust` | `pass` | `pass` | `local_toolchain_syntax` | `646` |
| `verified_add` | `python` | `pass` | `pass` | `local_toolchain_syntax` | `499` |
| `verified_add` | `go` | `pass` | `pass` | `structural_tokens` | `718` |
| `verified_add` | `java` | `pass` | `pass` | `local_toolchain_syntax` | `738` |
| `verified_add` | `kotlin` | `pass` | `pass` | `structural_tokens` | `674` |
| `verified_add` | `csharp` | `pass` | `pass` | `structural_tokens` | `1280` |
| `verified_add` | `javascript` | `pass` | `pass` | `local_toolchain_syntax` | `740` |
| `verified_add` | `wasm` | `pass` | `pass` | `wasm_llvm_ir_structural` | `851` |
| `verified_add` | `matlab` | `pass` | `pass` | `structural_tokens` | `803` |
| `verified_add` | `lean` | `pass` | `pass` | `local_toolchain_syntax_with_sorry_allowed` | `600` |
| `verified_add` | `zkproof` | `pass` | `pass` | `json_schema_structural` | `1171` |
| `runtime_helper_mix` | `c` | `pass` | `pass` | `local_toolchain_syntax` | `824` |
| `runtime_helper_mix` | `cpp` | `pass` | `pass` | `local_toolchain_syntax` | `747` |
| `runtime_helper_mix` | `rust` | `pass` | `pass` | `local_toolchain_syntax` | `779` |
| `runtime_helper_mix` | `python` | `pass` | `pass` | `local_toolchain_syntax` | `497` |
| `runtime_helper_mix` | `go` | `pass` | `pass` | `structural_tokens` | `701` |
| `runtime_helper_mix` | `java` | `pass` | `pass` | `local_toolchain_syntax` | `864` |
| `runtime_helper_mix` | `kotlin` | `pass` | `pass` | `structural_tokens` | `685` |
| `runtime_helper_mix` | `csharp` | `pass` | `pass` | `structural_tokens` | `1408` |
| `runtime_helper_mix` | `javascript` | `pass` | `pass` | `local_toolchain_syntax` | `978` |
| `runtime_helper_mix` | `wasm` | `pass` | `pass` | `wasm_llvm_ir_structural` | `1060` |
| `runtime_helper_mix` | `matlab` | `pass` | `pass` | `structural_tokens` | `616` |
| `runtime_helper_mix` | `lean` | `pass` | `pass` | `local_toolchain_syntax_with_sorry_allowed` | `725` |
| `runtime_helper_mix` | `zkproof` | `pass` | `pass` | `json_schema_structural` | `1814` |

## Summary

- Fixtures checked: `2`
- Free targets checked: `13`
- Matrix cells checked: `26`
- Emission passes: `26`
- Validation passes: `26`

## Boundary

- Selected-fixture matrix guard only.
- Structural checks are not runtime checks.
- No all-free-target public-readiness, compiler-correctness, formal-equivalence, or publication claim.
- No package publication, checkout, performance, hardware, Pro-target, or all-target claim.
