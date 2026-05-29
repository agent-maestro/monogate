# EML-ADV-PCC6 Source-Family Comparison

Date: 2026-05-29

Status: `EML_ADV_PCC6_SOURCE_FAMILY_COMPARISON_PASS`

PCC6 compares the RC decay and Gaussian stable eFrog holdouts.
It is a private synthesis artifact, not a broad EML advantage claim.

| Family | Shape | Profiles | Passing | Max abs agreement error | Noisy RMSE max | Classification |
|---|---|---:|---:|---:|---:|---|
| `rc_decay_stable` | single exponential decay envelope | `4` | `4` | `0.000e+00` | `1.968e-03` | `semantic_search_representation_tie_not_runtime_win` |
| `gaussian_stable` | quadratic exponent with sigma normalization | `4` | `4` | `0.000e+00` | `1.000e-03` | `semantic_search_representation_tie_not_runtime_win` |

## Summary

- Source families: `2`
- Profiles: `8`
- Passing profiles: `8`
- Semantic/search representation tie families: `2`
- Runtime win families: `0`
- Standard/protected runtime recommended families: `2`
- Next holdout family: `oscillatory_damped_wave`

## Boundary

- Private two-family comparison only.
- No broad EML advantage, source-family generalization, noise-robustness, prediction-accuracy, runtime-performance, compiler-correctness, formal-equivalence, proof, production, deployment, or public-readiness claim.
