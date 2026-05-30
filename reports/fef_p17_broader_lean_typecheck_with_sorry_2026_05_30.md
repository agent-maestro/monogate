# FEF-P17 Broader Lean Typecheck With Sorry

Date: 2026-05-30

Status: `FEF_P17_BROADER_LEAN_TYPECHECK_WITH_SORRY_PASS`

Decision: `broader_selected_lean_typecheck_with_sorry_passed`

| Case | Import resolved | Typecheck status | Sorry count |
|---|---|---|---:|
| `verified_add_broader_lean_typecheck_v0` | `True` | `typecheck_with_sorry_pass` | 1 |
| `clamp_bounded_broader_lean_typecheck_v0` | `True` | `typecheck_with_sorry_pass` | 1 |
| `voltage_divider_broader_lean_typecheck_v0` | `True` | `typecheck_with_sorry_pass` | 3 |
| `pid_controller_broader_lean_typecheck_v0` | `True` | `typecheck_with_sorry_pass` | 1 |
| `rc_filter_broader_lean_typecheck_v0` | `True` | `typecheck_with_sorry_pass` | 5 |
| `sine_oscillator_broader_lean_typecheck_v0` | `True` | `typecheck_with_sorry_pass` | 1 |
| `smoothstep_broader_lean_typecheck_v0` | `True` | `typecheck_with_sorry_pass` | 1 |
| `mosfet_iv_broader_lean_typecheck_v0` | `True` | `typecheck_with_sorry_pass` | 2 |

## Summary

- Cases: `8`
- MachLib import resolved: `8`
- Typecheck-with-sorry passes: `8`
- Typecheck blocked: `0`
- Sorry placeholders: `15`

## Boundary

- Configured Broader Lean typecheck-with-sorry probe only.
- No discharged-proof, formal-equivalence, or compiler-correctness claim.
- No package publication, checkout, public-readiness, performance, hardware, or all-target claim.
