# FEF-P127 Rust Early-Return Source-Order Checker

Date: 2026-06-01

Status: `FEF_P127_RUST_EARLY_RETURN_SOURCE_ORDER_CHECKER_PASS`

Decision: `rust_early_return_source_order_expected_rows_checker_negative_controls_recorded_support_blocked`

FEF-P127 applies the source-preserving checker discipline to a Rust early-return/fallthrough fixture.

## Summary

- Selected fixture: `rust_early_return_source_order_v0`
- Expected rows: `8`
- Checker passes: `8`
- Checker failures: `0`
- Negative controls: `3`
- Negative-control expected failures: `9`
- All negative controls fail closed: `True`
- Source parse performed: `False`
- Source re-emission performed: `False`
- Source fidelity validated: `False`
- Source-preserving support claim: `False`

## Checker Rows

| Row | Category | Status |
|---|---|---|
| `if_guard_open_line` | `layout` | `pass` |
| `return_lo_statement` | `return_path` | `pass` |
| `guard_closing_brace` | `layout` | `pass` |
| `fallthrough_comment` | `comment` | `pass` |
| `fallthrough_tail_expr` | `expression_tail` | `pass` |
| `return_before_fallthrough_order` | `token_order` | `pass` |
| `else_token_absent` | `token_absence` | `pass` |
| `line_count` | `layout` | `pass` |

## Negative Controls

| Control | Failed rows | Fail closed |
|---|---:|---|
| `missing_fallthrough_comment_negative_control_v0` | 3 | `True` |
| `changed_return_negative_control_v0` | 2 | `True` |
| `else_inserted_negative_control_v0` | 4 | `True` |

## Boundary

- Source-sketch checks only; no source parser or re-emitter execution.
- No preservation oracle or fidelity validation claim.
- No source-preserving roundtrip support claim.
- No full source roundtrip, compiler-correctness, formal-equivalence, or runtime-performance claim.
