# FEF-P49 Non-Generated C/Rust Fixture Gate

Date: 2026-05-31

Status: `FEF_P49_NON_GENERATED_C_RUST_FIXTURE_GATE_PASS`

Decision: `selected_non_generated_c_rust_semantic_evidence_attached_roundtrip_blocked`

## Attachment

| Attachment | Status | Evidence kind | Cases | Samples | Blocked scope |
|---|---|---|---:|---:|---|
| `non_generated_c_rust_source_semantic_evidence` | `pass_attached` | `selected_original_runtime_semantic_comparison` | 5 | 23 | `non-generated source roundtrip, full arbitrary C/Rust source roundtrip` |

## Allowed Private Claims

- Selected non-generated C/Rust source fixtures have original-runtime semantic comparison evidence.
- The attached non-generated source fixture evidence covers 5 cases and 23 deterministic samples.
- The evidence compares original C/Rust runtimes against Forge Python/JavaScript outputs after eFrog decompilation.
- This evidence can inform private reviewer assessment of the Rust/C/Python hero lane.

## Blocked Claims

- non-generated source roundtrip is supported
- full arbitrary C/Rust source roundtrip is supported
- Forge/eFrog is public-ready
- a package has been published
- checkout is enabled
- compiler correctness has been proved
- formal semantic equivalence has been proved
- runtime performance has been established
- all 13 free targets runtime-execute
- all 13 free targets roundtrip
- hardware, silicon, Lean-proof, zkproof, Pro-target, production, or all-target readiness is established

## Summary

- Hero targets: `rust, c, python`
- Selected generated roundtrip attachment packets: `10`
- Selected generated roundtrip attachment samples: `34`
- Non-generated source cases: `5`
- Non-generated source samples: `23`
- Non-generated source languages: `c, rust`
- Non-generated target languages: `python, javascript`
- Non-generated max abs error: `3.411e-13`
- Non-generated max rel error: `1.086e-15`

## Boundary

- Selected non-generated C/Rust source semantic evidence attachment only.
- No non-generated source roundtrip claim.
- No full arbitrary C/Rust source roundtrip claim.
- No reviewer decision, package publication, checkout, or public-readiness claim.
- No compiler-correctness, formal-equivalence, or runtime-performance claim.
- No all-free-target runtime, all-free-target roundtrip, hardware, silicon, or proof claim.
