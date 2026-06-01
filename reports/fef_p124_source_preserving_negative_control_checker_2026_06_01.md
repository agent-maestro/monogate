# FEF-P124 Source-Preserving Negative-Control Checker

Date: 2026-06-01

Status: `FEF_P124_SOURCE_PRESERVING_NEGATIVE_CONTROL_CHECKER_PASS`

Decision: `source_preserving_negative_controls_fail_closed_support_blocked`

FEF-P124 runs negative controls against the P123 expected-row checker.

## Summary

- Selected fixture: `c_if_else_source_layout_v0`
- Negative controls: `4`
- Row checks: `32`
- Expected failures: `12`
- Passing rows inside controls: `20`
- All controls fail closed: `True`
- All expected failures matched: `True`
- Source parse performed: `False`
- Source re-emission performed: `False`
- Preservation oracle run: `False`
- Source fidelity validated: `False`
- Source-preserving support claim: `False`

## Negative Controls

| Control | Mutation | Failed rows | Fail closed |
|---|---|---:|---|
| `missing_comment_negative_control_v0` | `remove_leading_block_comment` | 3 | `True` |
| `missing_else_negative_control_v0` | `remove_else_token_and_block_layout` | 4 | `True` |
| `changed_return_path_negative_control_v0` | `change_low_return_statement` | 1 | `True` |
| `single_line_layout_negative_control_v0` | `collapse_multiline_layout` | 4 | `True` |

## Boundary

- Negative-control source-sketch checks only; no source parser or re-emitter execution.
- No preservation oracle or fidelity validation claim.
- No source-preserving roundtrip support claim.
- No frontend lowering change.
- No full source roundtrip, compiler-correctness, formal-equivalence, or runtime-performance claim.
