# FEF-P122 Source-Preserving Expected Rows

Date: 2026-06-01

Status: `FEF_P122_SOURCE_PRESERVING_EXPECTED_ROWS_PASS`

Decision: `source_preserving_expected_rows_recorded_support_blocked`

FEF-P122 records expected preservation rows for one selected source-preserving fixture.

## Summary

- Selected fixture: `c_if_else_source_layout_v0`
- Expected rows: `8`
- Comment expectations: `2`
- Layout expectations: `2`
- Token expectations: `2`
- Return-path expectations: `2`
- Source parse performed: `False`
- Source re-emission performed: `False`
- Preservation oracle run: `False`
- Source fidelity validated: `False`
- Source-preserving support claim: `False`

## Expected Rows

| Row | Category | Expected kind | Source parse | Fidelity validated |
|---|---|---|---|---|
| `has_block_comment` | `comment` | `presence` | `False` | `False` |
| `comment_text_clamp` | `comment` | `exact_text` | `False` | `False` |
| `if_before_else_order` | `token_order` | `relative_order` | `False` | `False` |
| `brace_layout_multiline` | `layout` | `multiline_brace_layout` | `False` | `False` |
| `return_lo_path` | `return_path` | `exact_statement` | `False` | `False` |
| `return_x_path` | `return_path` | `exact_statement` | `False` | `False` |
| `else_token_present` | `token_presence` | `presence` | `False` | `False` |
| `line_count` | `layout` | `line_count` | `False` | `False` |

## Boundary

- Expected-row metadata only; no source parser or re-emitter execution.
- No preservation oracle or fidelity validation claim.
- No source-preserving roundtrip support claim.
- No frontend lowering change.
- No full source roundtrip, compiler-correctness, formal-equivalence, or runtime-performance claim.
