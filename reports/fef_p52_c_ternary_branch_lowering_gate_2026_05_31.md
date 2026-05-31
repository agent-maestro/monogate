# FEF-P52 C Ternary Branch Lowering Gate

Date: 2026-05-31

Status: `FEF_P52_C_TERNARY_BRANCH_LOWERING_GATE_PASS`

Decision: `selected_c_ternary_lowering_reingest_passed_general_branch_blocked`

FEF-P52 closes one narrow branch blocker: selected C ternary expressions.

| Case | Generated target | Samples | Status | Max abs error | Max rel error |
|---|---|---:|---|---:|---:|
| `c_ternary_select_pos_v0` | `c` | 5 | `pass` | 0.000e+00 | 0.000e+00 |
| `c_ternary_select_pos_v0` | `rust` | 5 | `pass` | 0.000e+00 | 0.000e+00 |

## Summary

- Selected C ternary lowering pass: `True`
- Source cases: `1`
- Re-ingest packets: `2`
- Packet samples: `10`
- Generated targets: `c, rust`
- Recompiled targets: `python`
- Max abs error: `0.000e+00`
- Max rel error: `0.000e+00`

## Allowed Private Claims

- One selected C ternary fixture now lowers to a guarded affine selector.
- The selected C ternary fixture emits generated C/Rust targets that re-ingest through eFrog and recompile to Python.
- The selected C/Rust generated target runtimes match re-ingested Python outputs over 10 packet-sample comparisons.
- P52 closes the P51 C ternary blocker only; C if-statements and Rust if remain blocked.

## Blocked Claims

- general C branch/control-flow support is established
- C if-statement support is established
- Rust if support is established
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

- Selected C ternary lowering and re-ingest only.
- No general C branch/control-flow support claim.
- No C if-statement or Rust if support claim.
- No full non-generated source roundtrip or arbitrary source-family claim.
- No reviewer decision, package publication, checkout, or public-readiness claim.
- No compiler-correctness, formal-equivalence, or runtime-performance claim.
