# EML-ADV-PCC7 Oscillatory Holdout

Date: 2026-05-29

Status: `EML_ADV_PCC7_OSCILLATORY_HOLDOUT_PASS`

PCC7 adds `damped_wave.py` as a non-pure-exponential eFrog source family.
EML represents the damping envelope; sine remains standard math.

| Profile | Noise | Winner | Max abs agreement error | Observation RMSE |
|---|---|---|---:|---:|
| `clean_damped_wave_grid` | `none` | `partial_eml_envelope_semantic_tie` | `0.000e+00` | `0.000e+00` |
| `high_frequency_phase_grid` | `phase_sweep` | `partial_eml_envelope_semantic_tie` | `0.000e+00` | `0.000e+00` |
| `noisy_input_damped_wave_grid` | `input_perturbation` | `partial_eml_envelope_semantic_tie` | `0.000e+00` | `0.000e+00` |
| `noisy_output_damped_wave_observation_grid` | `output_observation` | `partial_eml_envelope_semantic_tie` | `0.000e+00` | `1.505e-03` |

## Summary

- Holdouts: `1`
- Source families now referenced: `3`
- Profiles: `4`
- Passing profiles: `4`
- Partial EML coverage: `exponential_damping_envelope_only`
- Standard runtime surface still required: `True`
- Runtime performance claim: `False`

## Boundary

- Private oscillatory holdout only.
- No broad EML advantage, source-family generalization, oscillatory generalization, noise-robustness, prediction-accuracy, runtime-performance, compiler-correctness, formal-equivalence, proof, production, deployment, or public-readiness claim.
