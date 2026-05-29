# EML-ADV-PCC9 Guarded/Piecewise Holdout

Date: 2026-05-29

Status: `EML_ADV_PCC9_GUARDED_PIECEWISE_HOLDOUT_PASS`

PCC9 adds `clamp_guard.py` as a guarded/piecewise eFrog source family.
It compares source branches with a clamp-style guarded representation and blocks invalid bounds.

| Profile | Noise | Winner | Valid bounds | Max abs error |
|---|---|---|---:|---:|
| `baseline_guard_grid` | `none` | `guarded_piecewise_semantic_tie` | `True` | `0.000e+00` |
| `variable_bounds_grid` | `variable_bounds` | `guarded_piecewise_semantic_tie` | `True` | `0.000e+00` |
| `boundary_equality_grid` | `boundary_exact` | `guarded_piecewise_semantic_tie` | `True` | `0.000e+00` |
| `noisy_input_guard_grid` | `input_perturbation` | `guarded_piecewise_semantic_tie` | `True` | `0.000e+00` |
| `invalid_reversed_bounds_grid` | `invalid_bounds` | `blocked_invalid_guard_domain` | `False` | `0.000e+00` |

## Summary

- Holdouts: `1`
- Source families now referenced: `5`
- Profiles: `5`
- Valid profiles: `4`
- Passing valid profiles: `4`
- Invalid bounds blocked profiles: `1`
- Guard domain requirement: `lo <= hi`

## Boundary

- Private guarded/piecewise holdout only.
- No broad EML advantage, source-family generalization, guard-semantics generalization, branch correctness, protected-lowering correctness, noise-robustness, prediction-accuracy, runtime-performance, compiler-correctness, formal-equivalence, proof, production, deployment, or public-readiness claim.
