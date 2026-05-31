# FEF-P60 Control-Flow IR Schema

Date: 2026-05-31

Status: `FEF_P60_CONTROL_FLOW_IR_SCHEMA_PASS`

Decision: `control_flow_ir_schema_recorded_implementation_blocked`

FEF-P60 turns the P59 inventory into a machine-readable schema checkpoint.

## Summary

- Schema version: `monogate.control_flow_ir.v0`
- Required fields: `11`
- Block kinds: `4`
- Statement kinds: `3`
- Terminator kinds: `4`
- Selected IR fragments: `5`
- P59 IR nodes: `10`
- P59 unsupported forms: `6`
- P59 open semantic obligations: `6`
- Control-flow IR implemented: `False`
- Frontend lowering changed: `False`

## Selected IR Fragments

| Fragment | Source | Blocks | Branch Terminators | Return Terminators |
|---|---|---:|---:|---:|
| `c_ternary_select_v0` | `c` | 2 | 0 | 1 |
| `c_if_early_return_relu_v0` | `c` | 4 | 1 | 2 |
| `c_if_else_clamp_v0` | `c` | 6 | 2 | 3 |
| `rust_if_expr_relu_v0` | `rust` | 2 | 0 | 1 |
| `rust_if_return_clamp_v0` | `rust` | 6 | 2 | 3 |

## Schema Surface

- top-level program metadata
- blocks with entry/basic/merge/exit roles
- statements for assignment, phi/select, and unsupported constructs
- terminators for branch, return, jump, and unreachable
- unsupported constructs and semantic obligations
- claim flags locked false

## Boundary

- Schema checkpoint only; no new IR implementation.
- No frontend lowering change.
- No general branch/control-flow support claim.
- No branch re-ingest, full source roundtrip, arbitrary source-family, compiler-correctness, formal-equivalence, or runtime-performance claim.
