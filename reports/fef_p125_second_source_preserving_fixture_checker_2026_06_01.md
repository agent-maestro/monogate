# FEF-P125 Second Source-Preserving Fixture Checker

Date: 2026-06-01

Status: `FEF_P125_SECOND_SOURCE_PRESERVING_FIXTURE_CHECKER_PASS`

Decision: `second_source_preserving_fixture_expected_rows_checker_negative_controls_recorded_support_blocked`

FEF-P125 applies the source-preserving expected-row/checker/negative-control discipline to a second fixture.

## Summary

- Selected fixture: `c_nested_source_order_v0`
- Expected rows: `7`
- Checker passes: `7`
- Checker failures: `0`
- Negative controls: `3`
- Negative-control expected failures: `6`
- All negative controls fail closed: `True`
- Source parse performed: `False`
- Source re-emission performed: `False`
- Source fidelity validated: `False`
- Source-preserving support claim: `False`

## Checker Rows

| Row | Category | Status |
|---|---|---|
| `outer_if_line` | `layout` | `pass` |
| `inner_if_single_line_return` | `nested_order` | `pass` |
| `outer_before_inner_if` | `token_order` | `pass` |
| `closing_brace_before_fallthrough` | `token_order` | `pass` |
| `fallthrough_return_zero` | `return_path` | `pass` |
| `else_token_absent` | `token_absence` | `pass` |
| `line_count` | `layout` | `pass` |

## Negative Controls

| Control | Failed rows | Fail closed |
|---|---:|---|
| `missing_fallthrough_return_negative_control_v0` | 3 | `True` |
| `changed_inner_return_negative_control_v0` | 1 | `True` |
| `else_inserted_negative_control_v0` | 2 | `True` |

## Boundary

- Source-sketch checks only; no source parser or re-emitter execution.
- No preservation oracle or fidelity validation claim.
- No source-preserving roundtrip support claim.
- No full source roundtrip, compiler-correctness, formal-equivalence, or runtime-performance claim.
