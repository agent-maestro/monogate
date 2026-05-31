# FEF-P51 Branch/Control-Flow Blocker Gate

Date: 2026-05-31

Status: `FEF_P51_BRANCH_CONTROL_FLOW_BLOCKER_GATE_PASS`

Decision: `branch_control_flow_non_generated_c_rust_blockers_recorded`

FEF-P51 attempts selected non-generated C/Rust branch/control-flow fixtures.
The goal is blocker inventory, not branch support.

| Case | Source | Feature | Observed | Blocker class | Error |
|---|---|---|---|---|---|
| `c_if_early_return_relu_v0` | `c` | `if_early_return` | `blocked` | `c_statement_control_flow_unsupported` | If not supported in E2 (if/for/while go to E3+) |
| `c_if_else_clamp_v0` | `c` | `if_else_clamp` | `blocked` | `c_statement_control_flow_unsupported` | If not supported in E2 (if/for/while go to E3+) |
| `c_ternary_select_v0` | `c` | `ternary_select` | `blocked` | `c_conditional_expression_unsupported` | TernaryOp unsupported in C decompiler |
| `rust_if_expr_relu_v0` | `rust` | `if_expression` | `blocked` | `rust_if_expression_unsupported` | line 1: unexpected token `if` in expression |
| `rust_if_return_clamp_v0` | `rust` | `if_return_clamp` | `blocked` | `rust_if_expression_unsupported` | line 1: unexpected token `if` in expression |

## Summary

- Fixtures attempted: `5`
- Blocked fixtures: `5`
- Unexpected passes: `0`
- Source languages: `c, rust`
- Blocker classes: `c_conditional_expression_unsupported, c_statement_control_flow_unsupported, rust_if_expression_unsupported`
- P50 source-derived re-ingest pass: `True`

## Implementation Requirements

- Add C `If` statement lowering to a guarded/piecewise EML form or explicit unsupported branch packet.
- Add C `TernaryOp` lowering to a guarded selector form before using ternary fixtures as passing evidence.
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
