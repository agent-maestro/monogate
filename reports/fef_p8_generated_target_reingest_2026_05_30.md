# FEF-P8 Generated-Target Re-ingest

Date: 2026-05-30

Status: `FEF_P8_GENERATED_TARGET_REINGEST_PASS`

Decision: `selected_generated_target_reingest_passed`

FEF-P8 re-ingests selected generated Python and JavaScript outputs
through eFrog, recompiles the re-ingested EML to Python, and compares
those outputs against the generated target outputs over fixed samples.

| Case | Source | Generated target | Samples | Status | Max abs error | Max rel error |
|---|---|---|---:|---|---:|---:|
| `javascript_sigmoid_generated_target_reingest_v0` | `javascript` | `python` | 5 | `pass` | 0.000e+00 | 0.000e+00 |
| `javascript_sigmoid_generated_target_reingest_v0` | `javascript` | `javascript` | 5 | `pass` | 0.000e+00 | 0.000e+00 |
| `c_poly_horner_generated_target_reingest_v0` | `c` | `python` | 4 | `pass` | 0.000e+00 | 0.000e+00 |
| `c_poly_horner_generated_target_reingest_v0` | `c` | `javascript` | 4 | `pass` | 0.000e+00 | 0.000e+00 |
| `rust_poly_horner_generated_target_reingest_v0` | `rust` | `python` | 4 | `pass` | 0.000e+00 | 0.000e+00 |
| `rust_poly_horner_generated_target_reingest_v0` | `rust` | `javascript` | 4 | `pass` | 0.000e+00 | 0.000e+00 |

## Summary

- Packets: `6`
- Samples: `26`
- Passes: `6`
- Source languages: `c,javascript,rust`
- Generated targets: `javascript,python`
- Max abs error: `0.000e+00`
- Max rel error: `0.000e+00`

## Boundary

- Selected generated Python/JavaScript target re-ingest only.
- Power-expression generated target re-ingest remains held out.
- No package publication or checkout claim.
- No compiler correctness or formal semantic equivalence claim.
- No runtime performance, production, Verilog, Lean proof, zkproof, silicon, or hardware claim.
