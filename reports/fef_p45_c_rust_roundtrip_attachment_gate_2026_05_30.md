# FEF-P45 C/Rust Roundtrip Attachment Gate

Date: 2026-05-30

Status: `FEF_P45_C_RUST_ROUNDTRIP_ATTACHMENT_GATE_PASS`

Decision: `selected_c_rust_generated_target_roundtrip_attached_publication_blocked`

## Attachment Rows

| Target | Attachment | Packets | Samples | Max Abs Error | Max Rel Error | Allowed Claim |
|---|---|---:|---:|---:|---:|---|
| `c` | `pass_selected_generated_target_reingest` | `5` | `17` | `2.132e-14` | `1.086e-15` | c: selected Forge-generated c target outputs re-ingest through eFrog, recompile to Python, and match generated target runtime outputs on deterministic samples. |
| `rust` | `pass_selected_generated_target_reingest` | `5` | `17` | `2.132e-14` | `1.086e-15` | rust: selected Forge-generated rust target outputs re-ingest through eFrog, recompile to Python, and match generated target runtime outputs on deterministic samples. |

## Summary

- Attached targets: `c, rust`
- Attachment packets: `10`
- Attachment passes: `10`
- Attachment samples: `34`
- Attachment max absolute error: `2.132e-14`
- Attachment max relative error: `1.086e-15`
- Full C roundtrip claim: `False`
- Full Rust roundtrip claim: `False`

## Boundary

- Selected generated-target C/Rust re-ingest attachment only.
- No full arbitrary C/Rust source roundtrip claim.
- No all-free-target roundtrip or runtime execution claim.
- No package publication, checkout, public-readiness, compiler-correctness, formal-equivalence, runtime-performance, hardware, silicon, or proof claim.
