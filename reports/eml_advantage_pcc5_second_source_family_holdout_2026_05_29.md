# EML-ADV-PCC5 Second Source-Family Holdout

Date: 2026-05-29

Status: `EML_ADV_PCC5_SECOND_SOURCE_FAMILY_HOLDOUT_PASS`

PCC5 adds `gaussian_stable.py` as a second eFrog source family for the EML Advantage contract.
It reports source agreement separately from noisy-observation residuals.

| Profile | Noise | Winner | Max abs agreement error | Observation RMSE |
|---|---|---|---:|---:|
| `clean_gaussian_grid` | `none` | `semantic_tie_for_second_source_family` | `0.000e+00` | `0.000e+00` |
| `noisy_input_gaussian_grid` | `input_perturbation` | `semantic_tie_for_second_source_family` | `0.000e+00` | `0.000e+00` |
| `noisy_output_gaussian_observation_grid` | `output_observation` | `semantic_tie_for_second_source_family` | `0.000e+00` | `1.000e-03` |
| `narrow_sigma_noisy_edge_grid` | `input_edge_perturbation` | `semantic_tie_for_second_source_family` | `0.000e+00` | `0.000e+00` |

## Summary

- Holdouts: `1`
- Source families now referenced: `2`
- Profiles: `4`
- Passing profiles: `4`
- Noisy output profiles: `1`
- Broad EML advantage claim: `False`
- Source-family generalization claim: `False`
- Runtime performance claim: `False`

## Boundary

- Private second-source-family holdout only.
- No broad EML advantage, source-family generalization, noise-robustness, prediction-accuracy, runtime-performance, compiler-correctness, formal-equivalence, proof, production, deployment, or public-readiness claim.
