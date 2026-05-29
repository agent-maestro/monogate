# EML-ADV-PCC4 Noisy Real-Source Holdout

Date: 2026-05-29

Status: `EML_ADV_PCC4_NOISY_REAL_SOURCE_HOLDOUT_PASS`

PCC4 adds controlled perturbations around the eFrog RC decay holdout.
It reports semantic agreement separately from noisy-observation residuals.

| Profile | Noise | Winner | Max abs agreement error | Observation RMSE |
|---|---|---|---:|---:|
| `clean_baseline` | `none` | `semantic_tie_under_noise` | `0.000e+00` | `0.000e+00` |
| `noisy_input_grid` | `input_perturbation` | `semantic_tie_under_noise` | `0.000e+00` | `0.000e+00` |
| `noisy_output_observation_grid` | `output_observation` | `semantic_tie_under_noise` | `0.000e+00` | `1.968e-03` |
| `small_tau_noisy_edge_grid` | `input_edge_perturbation` | `semantic_tie_under_noise` | `0.000e+00` | `0.000e+00` |

## Summary

- Holdouts: `1`
- Profiles: `4`
- Passing profiles: `4`
- Noisy output profiles: `1`
- Broad EML advantage claim: `False`
- Prediction accuracy claim: `False`
- Runtime performance claim: `False`

## Boundary

- Private noisy real-source holdout only.
- No broad EML advantage, noise-robustness, prediction-accuracy, runtime-performance, compiler-correctness, formal-equivalence, proof, production, deployment, or public-readiness claim.
