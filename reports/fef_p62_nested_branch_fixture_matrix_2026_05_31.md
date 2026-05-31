# FEF-P62 Nested Branch Fixture Matrix

Date: 2026-05-31

Status: `FEF_P62_NESTED_BRANCH_FIXTURE_MATRIX_PASS`

Decision: `nested_branch_fixture_matrix_recorded_support_blocked`

FEF-P62 defines blocked nested-branch fixture shapes against the P60/P61 surfaces.

## Summary

- Fixtures: `4`
- C fixtures: `2`
- Rust fixtures: `2`
- Max branch depth: `2`
- Total return sites: `9`
- All fixtures blocked: `True`
- Schema fragments validate: `True`
- Nested branch support claim: `False`
- Control-flow IR implemented: `False`
- Frontend lowering changed: `False`

## Matrix

| Fixture | Source | Shape | Depth | Returns | Status |
|---|---|---|---:|---:|---|
| `c_nested_if_return_v0` | `c` | `nested_if_return` | 2 | 2 | `blocked_fixture_defined` |
| `c_nested_if_else_value_v0` | `c` | `nested_if_else_value` | 2 | 3 | `blocked_fixture_defined` |
| `rust_nested_if_expr_v0` | `rust` | `nested_if_expression` | 2 | 1 | `blocked_fixture_defined` |
| `rust_nested_if_return_v0` | `rust` | `nested_if_return` | 2 | 3 | `blocked_fixture_defined` |

## Boundary

- Fixture matrix only; no nested branch implementation.
- No frontend lowering change.
- No general branch/control-flow support claim.
- No branch re-ingest, full source roundtrip, arbitrary source-family, compiler-correctness, formal-equivalence, or runtime-performance claim.
