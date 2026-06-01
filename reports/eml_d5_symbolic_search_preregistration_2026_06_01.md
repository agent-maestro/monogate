# EML-D5 Symbolic Search Preregistration

Status: `EML_D5_SYMBOLIC_SEARCH_PREREGISTRATION_PASS`

EML-D5 locks the next symbolic-search plan before any A6.1-style run.

## Targets

- `psi_residual_two_zero_holdout_v1`
- `damped_oscillator_eml_phase_v0`

## Required Criteria

- `holdout_mse_improvement_replicated`: eml_holdout_mse <= 0.95 * standard_holdout_mse on every split
- `complexity_not_higher`: eml_best_complexity <= standard_best_complexity
- `wrong_exponent_control_not_better`: wrong_exponent_score > eml_score on target fixture
- `negative_controls_do_not_promote_eml`: standard_or_control_label wins on non-EML controls
- `protected_runtime_controls_respected`: no accepted expression violates D4 protected operator policy
- `localization_and_mse_both_reported`: both metrics present in every target run packet

## Negative Controls

- `wrong_exponent_two_zero_v0`: wrong-exponent controls must not outperform the preregistered EML target grammar
- `shuffled_residual_control_v1`: no grammar should receive positive structural interpretation on shuffled residuals
- `gaussian_bumps_control_v1`: standard/protected grammar should remain competitive or win
- `ordinary_polynomial_failure_v0`: standard Horner representation remains the control
- `expm1_logaddexp_runtime_controls_v1`: protected expm1/logaddexp policies from D4 must not be violated

## Summary

- experiment run performed: `False`
- success criteria: 6
- negative controls: 5
- null result accepted: `True`
- EML advantage proved: `False`

## Non-Claims

- EML-D5 preregisters a future symbolic-search experiment; it does not run the experiment.
- EML-D5 does not prove EML advantage, theorem discovery, RH, zeta-zero discovery, compiler correctness, runtime performance, formal equivalence, or public Atlas promotion.
- EML-D5 success criteria are private research gates, not public claims.
- Null results are explicitly allowed and must be recorded without reinterpretation.
