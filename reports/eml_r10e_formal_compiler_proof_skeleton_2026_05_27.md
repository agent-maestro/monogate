# EML-R10E Formal Compiler Proof Skeleton

Date: 2026-05-27

Status: `EML_R10E_FORMAL_COMPILER_PROOF_SKELETON_PASS`

R10E records the proof skeleton required for future EML lowering
correctness. It maps R10C scoped certificates into one obligation lane
and leaves compiler-wide obligations open.

## Obligations

| Obligation | Status | Needed artifact |
|---|---|---|
| `syntax-preservation` | `open` | formal AST/lowering relation |
| `domain-guard-preservation` | `open` | guard calculus and proof assistant model |
| `per-case-semantic-preservation` | `covered_by_scoped_certificate` | R10C scoped certificates for currently covered cases |
| `unsupported-case-routing` | `open` | total decision procedure over lowering cases |
| `runtime-implementation-correspondence` | `open` | codegen semantics for Python/Rust/C fixtures |
| `compiler-wide-induction` | `open` | structural induction over EML AST |

## Summary

- Obligations: `6`
- Covered obligations: `1`
- Open obligations: `5`
- Covered cases: `4`
- Compiler correctness proved: `False`
- Formal compiler proof complete: `False`

## Boundary

- Proof skeleton only.
- No compiler correctness claim.
- No full EML semantics claim.
- No compiler behavior change.
- No deployment or production lowering claim.
