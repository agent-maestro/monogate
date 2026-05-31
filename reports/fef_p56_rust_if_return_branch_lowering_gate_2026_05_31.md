# FEF-P56 Rust If-Return Branch Lowering Gate

Date: 2026-05-31

Status: `FEF_P56_RUST_IF_RETURN_BRANCH_LOWERING_GATE_PASS`

Decision: `selected_rust_if_return_clamp_lowering_reingest_passed_general_branch_blocked`

FEF-P56 closes one narrow branch blocker: selected Rust if-return expressions.

| Case | Generated target | Samples | Status | Max abs error | Max rel error |
|---|---|---:|---|---:|---:|
| `rust_if_return_clamp_v0` | `c` | 7 | `pass` | 0.000e+00 | 0.000e+00 |
| `rust_if_return_clamp_v0` | `rust` | 7 | `pass` | 0.000e+00 | 0.000e+00 |

## Summary

- Selected Rust if-return lowering pass: `True`
- Source cases: `1`
- Re-ingest packets: `2`
- Packet samples: `14`
- Generated targets: `c, rust`
- Recompiled targets: `python`
- Max abs error: `0.000e+00`
- Max rel error: `0.000e+00`

## Allowed Private Claims

- One selected Rust if-return fixture now lowers to a guarded affine selector.
- The selected Rust if-return fixture emits generated C/Rust targets that re-ingest through eFrog and recompile to Python.
- The selected C/Rust generated target runtimes match re-ingested Python outputs over 14 packet-sample comparisons.
- P56 closes the final selected P51 Rust if-return blocker only; arbitrary branch/control-flow support remains blocked.

## Blocked Claims

- general Rust branch/control-flow support is established
- arbitrary Rust if support is established
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

- Selected Rust if-return lowering and re-ingest only.
- No general Rust branch/control-flow support claim.
- No full non-generated source roundtrip or arbitrary source-family claim.
- No reviewer decision, package publication, checkout, or public-readiness claim.
- No compiler-correctness, formal-equivalence, or runtime-performance claim.
