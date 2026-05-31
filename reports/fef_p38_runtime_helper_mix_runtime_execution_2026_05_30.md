# FEF-P38 Runtime Helper Mix Runtime Execution

Date: 2026-05-30

Status: `FEF_P38_RUNTIME_HELPER_MIX_RUNTIME_EXECUTION_PASS`

Decision: `selected_runtime_helper_mix_generated_targets_execute_and_match_reference`

Source fixture: `generated/runtime_helper_mix.eml`

| Target | Emission | Runtime | Agreement | Samples | Max Abs Error |
|---|---:|---:|---:|---:|---:|
| `c` | `pass` | `pass` | `pass` | `5` | `0.000e+00` |
| `cpp` | `pass` | `pass` | `pass` | `5` | `0.000e+00` |
| `rust` | `pass` | `pass` | `pass` | `5` | `0.000e+00` |
| `python` | `pass` | `pass` | `pass` | `5` | `0.000e+00` |
| `javascript` | `pass` | `pass` | `pass` | `5` | `0.000e+00` |
| `java` | `pass` | `pass` | `pass` | `5` | `4.441e-16` |

## Summary

- Runtime targets checked: `6`
- Samples per target: `5`
- Total sample executions: `30`
- Runtime passes: `6`
- Agreement passes: `6`
- Max absolute error: `4.441e-16`

## Boundary

- Selected generated-target runtime execution only.
- This guard does not execute all 13 free targets.
- No all-free-target public-readiness, compiler-correctness, formal-equivalence, or publication claim.
- No runtime performance, package publication, checkout, hardware, Pro-target, or all-target claim.
