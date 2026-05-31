# FEF-P50 Non-Generated Source Re-ingest Gate

Date: 2026-05-31

Status: `FEF_P50_NON_GENERATED_SOURCE_REINGEST_GATE_PASS`

Decision: `selected_non_generated_source_derived_reingest_passed_full_roundtrip_blocked`

FEF-P50 runs selected non-generated C/Rust source-derived re-ingest checks.
The source fixtures decompile through eFrog, compile through Forge to C/Rust,
re-ingest through eFrog, recompile to Python, and compare generated target runtime
outputs against the re-ingested Python outputs over deterministic samples.

| Case | Source | Generated target | Samples | Status | Max abs error | Max rel error |
|---|---|---|---:|---|---:|---:|
| `c_gaussian_original_runtime_semantic_compare_v0` | `c` | `c` | 4 | `pass` | 0.000e+00 | 0.000e+00 |
| `c_gaussian_original_runtime_semantic_compare_v0` | `c` | `rust` | 4 | `pass` | 0.000e+00 | 0.000e+00 |
| `c_circle_area_original_runtime_semantic_compare_v0` | `c` | `c` | 5 | `pass` | 3.411e-13 | 1.086e-15 |
| `c_circle_area_original_runtime_semantic_compare_v0` | `c` | `rust` | 5 | `pass` | 3.411e-13 | 1.086e-15 |
| `rust_gaussian_original_runtime_semantic_compare_v0` | `rust` | `c` | 4 | `pass` | 0.000e+00 | 0.000e+00 |
| `rust_gaussian_original_runtime_semantic_compare_v0` | `rust` | `rust` | 4 | `pass` | 0.000e+00 | 0.000e+00 |
| `rust_sigmoid_original_runtime_semantic_compare_v0` | `rust` | `c` | 5 | `pass` | 0.000e+00 | 0.000e+00 |
| `rust_sigmoid_original_runtime_semantic_compare_v0` | `rust` | `rust` | 5 | `pass` | 0.000e+00 | 0.000e+00 |
| `rust_circle_area_original_runtime_semantic_compare_v0` | `rust` | `c` | 5 | `pass` | 3.411e-13 | 1.086e-15 |
| `rust_circle_area_original_runtime_semantic_compare_v0` | `rust` | `rust` | 5 | `pass` | 3.411e-13 | 1.086e-15 |

## Summary

- Source cases: `5`
- Re-ingest packets: `10`
- Packet samples: `46`
- Passes: `10`
- Source languages: `c, rust`
- Generated targets: `c, rust`
- Recompiled targets: `python`
- Max abs error: `3.411e-13`
- Max rel error: `1.086e-15`

## Allowed Private Claims

- Selected non-generated C/Rust source fixtures produce source-derived generated C/Rust targets that re-ingest through eFrog.
- The selected source-derived re-ingest gate covers 5 source cases, 10 generated-target packets, and 46 packet-sample comparisons.
- Generated C/Rust target runtimes match re-ingested-and-recompiled Python outputs over deterministic samples.
- This is private selected-fixture evidence only, not full arbitrary C/Rust source roundtrip.

## Blocked Claims

- full non-generated source roundtrip is supported
- full arbitrary C/Rust source roundtrip is supported
- arbitrary C/Rust source-family support is established
- Forge/eFrog is public-ready
- a package has been published
- checkout is enabled
- compiler correctness has been proved
- formal semantic equivalence has been proved
- runtime performance has been established
- all 13 free targets runtime-execute
- all 13 free targets roundtrip
- hardware, silicon, Lean-proof, zkproof, Pro-target, production, or all-target readiness is established

## Boundary

- Selected non-generated source-derived generated C/Rust target re-ingest only.
- No full non-generated source roundtrip claim.
- No arbitrary C/Rust source-family claim.
- No reviewer decision, package publication, checkout, or public-readiness claim.
- No compiler-correctness, formal-equivalence, or runtime-performance claim.
- No all-free-target runtime, all-free-target roundtrip, hardware, silicon, or proof claim.
