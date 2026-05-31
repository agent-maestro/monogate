# FEF-P55 Rust If Expression Branch Lowering Gate

Date: 2026-05-31

Status: `FEF_P55_RUST_IF_EXPRESSION_BRANCH_LOWERING_GATE_PASS`

Decision: `selected_rust_if_expression_lowering_reingest_passed_general_branch_blocked`

FEF-P55 closes one narrow branch blocker: selected Rust if expressions.

| Case | Generated target | Samples | Status | Max abs error | Max rel error |
|---|---|---:|---|---:|---:|
| `rust_if_expr_relu_v0` | `c` | 5 | `pass` | 0.000e+00 | 0.000e+00 |
| `rust_if_expr_relu_v0` | `rust` | 5 | `pass` | 0.000e+00 | 0.000e+00 |

## Summary

- Selected Rust if expression lowering pass: `True`
- Source cases: `1`
- Re-ingest packets: `2`
- Packet samples: `10`
- Generated targets: `c, rust`
- Recompiled targets: `python`
- Max abs error: `0.000e+00`
- Max rel error: `0.000e+00`

## Allowed Private Claims

- One selected Rust if expression fixture now lowers to a guarded affine selector.
- The selected Rust if expression fixture emits generated C/Rust targets that re-ingest through eFrog and recompile to Python.
- The selected C/Rust generated target runtimes match re-ingested Python outputs over 10 packet-sample comparisons.
- P55 closes the P51 selected Rust if-expression blocker only; Rust if-return remains blocked.

## Blocked Claims

- general C branch/control-flow support is established
- arbitrary C if-statement support is established
- general Rust if support is established
- Rust if-return support is established
- branch/control-flow re-ingest is generally supported
- full non-generated source roundtrip is supported
- full arbitrary C/Rust source roundtrip is supported
- arbitrary C/Rust source-family support is established
- Forge/eFrog is public-ready
- a package has been published
- checkout is enabled
- compiler correctness has been proved
- formal semantic equivalence has been proved
- runtime performance has been established

## Boundary

- Selected Rust if expression lowering and re-ingest only.
- No general Rust branch/control-flow support claim.
- No Rust if-return support claim.
- No full non-generated source roundtrip or arbitrary source-family claim.
- No reviewer decision, package publication, checkout, or public-readiness claim.
- No compiler-correctness, formal-equivalence, or runtime-performance claim.
