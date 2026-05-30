# FEF-P10 Broader Generated-Target Re-ingest

Date: 2026-05-30

Status: `FEF_P10_BROADER_GENERATED_TARGET_REINGEST_PASS`

Decision: `broader_selected_generated_target_reingest_passed`

FEF-P10 broadens the generated-target re-ingest fixture family while
keeping the evidence private, deterministic, and bounded.

| Case | Source | Generated target | Samples | Status | Max abs error | Max rel error |
|---|---|---|---:|---|---:|---:|
| `python_gaussian_broader_reingest_v0` | `python` | `python` | 3 | `pass` | 0.000e+00 | 0.000e+00 |
| `python_gaussian_broader_reingest_v0` | `python` | `javascript` | 3 | `pass` | 0.000e+00 | 0.000e+00 |
| `python_stable_sigmoid_broader_reingest_v0` | `python` | `python` | 5 | `pass` | 0.000e+00 | 0.000e+00 |
| `python_stable_sigmoid_broader_reingest_v0` | `python` | `javascript` | 5 | `pass` | 0.000e+00 | 0.000e+00 |
| `python_voltage_divider_broader_reingest_v0` | `python` | `python` | 3 | `pass` | 0.000e+00 | 0.000e+00 |
| `python_voltage_divider_broader_reingest_v0` | `python` | `javascript` | 3 | `pass` | 0.000e+00 | 0.000e+00 |
| `python_rc_decay_stable_broader_reingest_v0` | `python` | `python` | 3 | `pass` | 0.000e+00 | 0.000e+00 |
| `python_rc_decay_stable_broader_reingest_v0` | `python` | `javascript` | 3 | `pass` | 0.000e+00 | 0.000e+00 |
| `python_stretched_exponential_broader_reingest_v0` | `python` | `python` | 3 | `pass` | 0.000e+00 | 0.000e+00 |
| `python_stretched_exponential_broader_reingest_v0` | `python` | `javascript` | 3 | `pass` | 4.441e-16 | 1.911e-16 |
| `javascript_gaussian_broader_reingest_v0` | `javascript` | `python` | 3 | `pass` | 0.000e+00 | 0.000e+00 |
| `javascript_gaussian_broader_reingest_v0` | `javascript` | `javascript` | 3 | `pass` | 0.000e+00 | 0.000e+00 |
| `javascript_circle_area_broader_reingest_v0` | `javascript` | `python` | 3 | `pass` | 0.000e+00 | 0.000e+00 |
| `javascript_circle_area_broader_reingest_v0` | `javascript` | `javascript` | 3 | `pass` | 2.132e-14 | 1.086e-15 |
| `c_gaussian_broader_reingest_v0` | `c` | `python` | 3 | `pass` | 0.000e+00 | 0.000e+00 |
| `c_gaussian_broader_reingest_v0` | `c` | `javascript` | 3 | `pass` | 0.000e+00 | 0.000e+00 |
| `rust_sigmoid_broader_reingest_v0` | `rust` | `python` | 3 | `pass` | 0.000e+00 | 0.000e+00 |
| `rust_sigmoid_broader_reingest_v0` | `rust` | `javascript` | 3 | `pass` | 0.000e+00 | 0.000e+00 |

## Summary

- Cases: `9`
- Packets: `18`
- Samples: `58`
- Passes: `18`
- Source languages: `c,javascript,python,rust`
- Generated targets: `javascript,python`
- Max abs error: `2.132e-14`
- Max rel error: `1.086e-15`

## Boundary

- Broader selected generated Python/JavaScript target re-ingest only.
- No package publication or checkout claim.
- No compiler correctness or formal semantic equivalence claim.
- No runtime performance, production, Verilog, Lean proof, zkproof, silicon, or hardware claim.
