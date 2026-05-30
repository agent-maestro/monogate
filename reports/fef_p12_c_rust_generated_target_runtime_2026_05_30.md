# FEF-P12 C/Rust Generated-Target Runtime

Date: 2026-05-30

Status: `FEF_P12_C_RUST_GENERATED_TARGET_RUNTIME_PASS`

Decision: `selected_c_rust_generated_target_runtime_passed`

FEF-P12 turns selected C and Rust generated targets from policy-defined evidence-open
into bounded local-runtime sample-grid evidence.

| Case | Source | Generated target | Samples | Status | Max abs error | Max rel error |
|---|---|---|---:|---|---:|---:|
| `python_stable_sigmoid_broader_reingest_v0` | `python` | `c` | 5 | `pass` | 0.000e+00 | 0.000e+00 |
| `python_stable_sigmoid_broader_reingest_v0` | `python` | `rust` | 5 | `pass` | 0.000e+00 | 0.000e+00 |
| `python_voltage_divider_broader_reingest_v0` | `python` | `c` | 3 | `pass` | 0.000e+00 | 0.000e+00 |
| `python_voltage_divider_broader_reingest_v0` | `python` | `rust` | 3 | `pass` | 0.000e+00 | 0.000e+00 |
| `javascript_circle_area_broader_reingest_v0` | `javascript` | `c` | 3 | `pass` | 2.132e-14 | 1.086e-15 |
| `javascript_circle_area_broader_reingest_v0` | `javascript` | `rust` | 3 | `pass` | 2.132e-14 | 1.086e-15 |
| `c_gaussian_broader_reingest_v0` | `c` | `c` | 3 | `pass` | 0.000e+00 | 0.000e+00 |
| `c_gaussian_broader_reingest_v0` | `c` | `rust` | 3 | `pass` | 0.000e+00 | 0.000e+00 |
| `rust_sigmoid_broader_reingest_v0` | `rust` | `c` | 3 | `pass` | 0.000e+00 | 0.000e+00 |
| `rust_sigmoid_broader_reingest_v0` | `rust` | `rust` | 3 | `pass` | 0.000e+00 | 0.000e+00 |

## Summary

- Cases: `5`
- Packets: `10`
- Samples: `34`
- Passes: `10`
- Source languages: `c,javascript,python,rust`
- Generated targets: `c,rust`
- Max abs error: `2.132e-14`
- Max rel error: `1.086e-15`

## Boundary

- Selected generated C/Rust local-runtime sample-grid comparison only.
- Rust runtime execution uses a local compatibility shim for Forge runtime math calls to keep the guard offline-reproducible.
- No package publication or checkout claim.
- No all-target readiness, compiler correctness, or formal semantic equivalence claim.
- No runtime performance, production, Verilog, Lean proof, zkproof, silicon, or hardware claim.
