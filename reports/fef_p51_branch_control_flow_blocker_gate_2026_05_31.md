# FEF-P51 Branch/Control-Flow Blocker Gate

Date: 2026-05-31

Status: `FEF_P51_BRANCH_CONTROL_FLOW_BLOCKER_GATE_PASS`

Decision: `branch_control_flow_non_generated_c_rust_blockers_recorded`

FEF-P51 attempts selected non-generated C/Rust branch/control-flow fixtures.
The goal is blocker inventory, not branch support.

| Case | Source | Feature | Observed | Blocker class | Error |
|---|---|---|---|---|---|
| `c_if_early_return_relu_v0` | `c` | `if_early_return` | `unexpected_pass` | `unexpected_pass` |  |
| `c_if_else_clamp_v0` | `c` | `if_else_clamp` | `blocked` | `c_statement_control_flow_unsupported` | C if statement form not supported in E2 (only `if (cond) return a; return b;` or return-only if/else) |
| `c_ternary_select_v0` | `c` | `ternary_select` | `unexpected_pass` | `unexpected_pass` |  |
| `rust_if_expr_relu_v0` | `rust` | `if_expression` | `blocked` | `rust_if_expression_unsupported` | line 1: unexpected token `if` in expression |
| `rust_if_return_clamp_v0` | `rust` | `if_return_clamp` | `blocked` | `rust_if_expression_unsupported` | line 1: unexpected token `if` in expression |

## Summary

- Fixtures attempted: `5`
- Blocked fixtures: `3`
- Unexpected passes: `2`
- Later-phase pass cases: `c_if_early_return_relu_v0, c_ternary_select_v0`
- Source languages: `c, rust`
- Blocker classes: `c_statement_control_flow_unsupported, rust_if_expression_unsupported`
- P50 source-derived re-ingest pass: `True`

## Implementation Requirements

- Add broader C `If` statement lowering beyond the selected early-return form, or keep unsupported branch packets explicit.
- Keep C `TernaryOp` lowering evidence in the later FEF-P52 selected ternary gate, not in P51 blocker evidence.
- Keep C early-return `If` lowering evidence in the later FEF-P53 selected if early-return gate, not in P51 blocker evidence.
- Add Rust `if` expression and `if return` parsing/lowering before branch re-ingest can run.
- Add deterministic boundary samples around branch thresholds after frontend support exists.
- Keep the new branch gate separate from P50 scalar source-derived re-ingest evidence.

## Boundary

- Branch/control-flow blocker inventory only.
- No C/Rust branch/control-flow support claim.
- No branch/control-flow re-ingest claim.
- No full non-generated source roundtrip or arbitrary source-family claim.
- No reviewer decision, package publication, checkout, or public-readiness claim.
- No compiler-correctness, formal-equivalence, or runtime-performance claim.
