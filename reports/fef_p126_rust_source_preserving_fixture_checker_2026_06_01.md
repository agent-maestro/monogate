# FEF-P126 Rust Source-Preserving Fixture Checker

Date: 2026-06-01

Status: `FEF_P126_RUST_SOURCE_PRESERVING_FIXTURE_CHECKER_PASS`

Decision: `rust_source_preserving_fixture_expected_rows_checker_negative_controls_recorded_support_blocked`

FEF-P126 applies the source-preserving checker discipline to a Rust if-expression fixture.

## Summary

- Selected fixture: `rust_if_expr_source_layout_v0`
- Expected rows: `7`
- Checker passes: `7`
- Checker failures: `0`
- Negative controls: `3`
- Negative-control expected failures: `10`
- All negative controls fail closed: `True`
- Source parse performed: `False`
- Source re-emission performed: `False`
- Source fidelity validated: `False`
- Source-preserving support claim: `False`

## Checker Rows

| Row | Category | Status |
|---|---|---|
| `if_expression_open_line` | `layout` | `pass` |
| `then_tail_expr_line` | `expression_tail` | `pass` |
| `else_opening_line` | `layout` | `pass` |
| `else_tail_expr_line` | `expression_tail` | `pass` |
| `if_before_else_order` | `token_order` | `pass` |
| `else_token_present` | `token_presence` | `pass` |
| `line_count` | `layout` | `pass` |

## Negative Controls

| Control | Failed rows | Fail closed |
|---|---:|---|
| `missing_else_negative_control_v0` | 4 | `True` |
| `changed_then_tail_negative_control_v0` | 1 | `True` |
| `single_line_rust_layout_negative_control_v0` | 5 | `True` |

## Boundary

- Source-sketch checks only; no source parser or re-emitter execution.
- No preservation oracle or fidelity validation claim.
- No source-preserving roundtrip support claim.
- No full source roundtrip, compiler-correctness, formal-equivalence, or runtime-performance claim.
