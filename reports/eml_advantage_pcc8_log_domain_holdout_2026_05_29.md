# EML-ADV-PCC8 Log-Domain Holdout

Date: 2026-05-29

Status: `EML_ADV_PCC8_LOG_DOMAIN_HOLDOUT_PASS`

PCC8 adds `numpy_softplus.py` as a log-domain eFrog source family.
It separates safe-range EML/source agreement from overflow-prone protected lowering.

| Profile | Noise | Winner | Source finite | EML finite | Protected finite |
|---|---|---|---:|---:|---:|
| `safe_log_domain_grid` | `none` | `semantic_tie_log_domain_safe_range` | `1.000` | `1.000` | `1.000` |
| `centered_noisy_input_grid` | `input_perturbation` | `semantic_tie_log_domain_safe_range` | `1.000` | `1.000` | `1.000` |
| `noisy_output_observation_grid` | `output_observation` | `semantic_tie_log_domain_safe_range` | `1.000` | `1.000` | `1.000` |
| `negative_tail_underflow_grid` | `negative_tail` | `semantic_tie_log_domain_safe_range` | `1.000` | `1.000` | `1.000` |
| `positive_overflow_guard_grid` | `overflow_guard` | `protected_lowering_required` | `0.283` | `0.283` | `1.000` |

## Summary

- Holdouts: `1`
- Source families now referenced: `4`
- Profiles: `5`
- Safe semantic tie profiles: `4`
- Protected lowering recommended profiles: `1`
- All protected profiles finite: `True`
- Runtime recommendation: `protected_logaddexp_for_overflow_prone_ranges`

## Boundary

- Private log-domain holdout only.
- No broad EML advantage, source-family generalization, log-domain generalization, protected-lowering correctness, noise-robustness, prediction-accuracy, runtime-performance, compiler-correctness, formal-equivalence, proof, production, deployment, or public-readiness claim.
