# EML-D6 Preregistered Symbolic Search Run

Status: `EML_D6_PREREGISTERED_SYMBOLIC_SEARCH_RUN_PASS`

EML-D6 runs the bounded D5-preregistered search and defers interpretation to D7.

## Summary

- run packets: 18
- psi packets: 9
- damped oscillator packets: 9
- negative control outcomes: 5
- D7 interpretation required: `True`
- EML advantage proved: `False`

## Run Packets

| Dataset | Split | Grammar | Holdout MSE | Complexity |
|---|---|---|---|---|
| `psi_residual` | `seed_20260601_a` | `eml_native_guarded_v1` | 5.46033 | 17 |
| `psi_residual` | `seed_20260601_a` | `standard_exp_log_trig_v1` | 5.52684 | 16 |
| `psi_residual` | `seed_20260601_a` | `wrong_exponent_eml_control_v1` | 5.83499 | 17 |
| `psi_residual` | `seed_20260601_b` | `eml_native_guarded_v1` | 5.29161 | 17 |
| `psi_residual` | `seed_20260601_b` | `standard_exp_log_trig_v1` | 5.19306 | 16 |
| `psi_residual` | `seed_20260601_b` | `wrong_exponent_eml_control_v1` | 6.06229 | 17 |
| `psi_residual` | `seed_20260601_c` | `eml_native_guarded_v1` | 5.26334 | 17 |
| `psi_residual` | `seed_20260601_c` | `standard_exp_log_trig_v1` | 5.57046 | 16 |
| `psi_residual` | `seed_20260601_c` | `wrong_exponent_eml_control_v1` | 6.52773 | 17 |
| `damped_oscillator` | `seed_20260601_a` | `eml_native_guarded_v1` | 0.000526953 | 17 |
| `damped_oscillator` | `seed_20260601_a` | `standard_exp_log_trig_v1` | 0.000526953 | 16 |
| `damped_oscillator` | `seed_20260601_a` | `wrong_exponent_eml_control_v1` | 0.167624 | 17 |
| `damped_oscillator` | `seed_20260601_b` | `eml_native_guarded_v1` | 0.000575219 | 17 |
| `damped_oscillator` | `seed_20260601_b` | `standard_exp_log_trig_v1` | 0.000575219 | 16 |
| `damped_oscillator` | `seed_20260601_b` | `wrong_exponent_eml_control_v1` | 0.141671 | 17 |
| `damped_oscillator` | `seed_20260601_c` | `eml_native_guarded_v1` | 0.000477855 | 17 |
| `damped_oscillator` | `seed_20260601_c` | `standard_exp_log_trig_v1` | 0.000477855 | 16 |
| `damped_oscillator` | `seed_20260601_c` | `wrong_exponent_eml_control_v1` | 0.13766 | 17 |

## Non-Claims

- EML-D6 runs a bounded deterministic preregistered search, not a full PySR campaign.
- EML-D6 does not interpret results as proof, theorem discovery, RH proof, zeta-zero discovery, EML advantage, runtime performance, compiler correctness, formal equivalence, or public readiness.
- EML-D6 preserves D5 thresholds and controls; D7 must perform the interpretation gate.
