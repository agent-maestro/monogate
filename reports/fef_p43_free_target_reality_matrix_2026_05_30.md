# FEF-P43 Free Target Reality Matrix

Date: 2026-05-30

Status: `FEF_P43_FREE_TARGET_REALITY_MATRIX_PASS`

Decision: `free_target_reality_matrix_recorded_publication_blocked`

## Target Matrix

| Target | Priority | Codegen | Validation | Runtime | Runtime Samples | Roundtrip | Allowed Claim |
|---|---|---:|---:|---:|---:|---:|---|
| `c` | `hero_runtime_lane` | `pass` | `pass` | `pass_selected_fixture_runtime` | `24` | `not_attempted` | c: selected emission and validation pass for four fixture families, with selected runtime execution evidence. |
| `cpp` | `detected_toolchain_followup` | `pass` | `pass` | `pass_selected_fixture_runtime` | `24` | `not_attempted` | cpp: selected emission and validation pass for four fixture families, with selected runtime execution evidence. |
| `rust` | `hero_runtime_lane` | `pass` | `pass` | `pass_selected_fixture_runtime` | `24` | `not_attempted` | rust: selected emission and validation pass for four fixture families, with selected runtime execution evidence. |
| `python` | `hero_runtime_lane` | `pass` | `pass` | `pass_selected_fixture_runtime` | `24` | `pass_selected_roundtrip_evidence` | python: selected emission and validation pass for four fixture families, with selected runtime execution evidence. |
| `go` | `future_toolchain_or_semantics_followup` | `pass` | `pass` | `not_attempted_missing_or_unclaimed_toolchain` | `0` | `not_attempted` | go: selected emission and validation pass for four fixture families, without selected runtime execution evidence. |
| `java` | `detected_toolchain_followup` | `pass` | `pass` | `pass_selected_fixture_runtime` | `24` | `not_attempted` | java: selected emission and validation pass for four fixture families, with selected runtime execution evidence. |
| `kotlin` | `future_toolchain_or_semantics_followup` | `pass` | `pass` | `not_attempted_missing_or_unclaimed_toolchain` | `0` | `not_attempted` | kotlin: selected emission and validation pass for four fixture families, without selected runtime execution evidence. |
| `csharp` | `future_toolchain_or_semantics_followup` | `pass` | `pass` | `not_attempted_missing_or_unclaimed_toolchain` | `0` | `not_attempted` | csharp: selected emission and validation pass for four fixture families, without selected runtime execution evidence. |
| `javascript` | `roundtrip_lane` | `pass` | `pass` | `pass_selected_fixture_runtime` | `24` | `pass_selected_roundtrip_evidence` | javascript: selected emission and validation pass for four fixture families, with selected runtime execution evidence. |
| `wasm` | `future_toolchain_or_semantics_followup` | `pass` | `pass` | `not_attempted_missing_or_unclaimed_toolchain` | `0` | `not_attempted` | wasm: selected emission and validation pass for four fixture families, without selected runtime execution evidence. |
| `matlab` | `future_toolchain_or_semantics_followup` | `pass` | `pass` | `not_attempted_missing_or_unclaimed_toolchain` | `0` | `not_attempted` | matlab: selected emission and validation pass for four fixture families, without selected runtime execution evidence. |
| `lean` | `detected_toolchain_followup` | `pass` | `pass` | `toolchain_detected_runtime_not_wired_or_not_claimed` | `0` | `not_attempted` | lean: selected emission and validation pass for four fixture families, without selected runtime execution evidence. |
| `zkproof` | `future_toolchain_or_semantics_followup` | `pass` | `pass` | `not_attempted_missing_or_unclaimed_toolchain` | `0` | `not_attempted` | zkproof: selected emission and validation pass for four fixture families, without selected runtime execution evidence. |

## Summary

- Free targets checked: `13`
- Fixtures per target: `4`
- Matrix cells checked: `52`
- Runtime pass targets: `c, cpp, rust, python, java, javascript`
- Runtime overlay sample executions: `144`
- Runtime overlay max absolute error: `4.441e-16`
- Roundtrip pass targets: `python, javascript`
- Hero hardening targets: `rust, c, python`

## Boundary

- Target-level reality matrix only.
- No new runtime execution is performed by this pass.
- No package publication, checkout, or public-readiness claim.
- No all-free-target runtime or all-free-target roundtrip claim.
- No compiler correctness, formal semantic equivalence, runtime performance, hardware, silicon, or proof claim.
