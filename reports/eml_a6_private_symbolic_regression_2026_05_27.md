# EML-A6 Private Symbolic Regression Harness

Date: 2026-05-27

Status: `EML_A6_PRIVATE_SYMBOLIC_REGRESSION_PYSR_RUN_PASS`

PySR available: `True`

Full run performed: `True`

Fallback: `deterministic_template_search` / `EML_SYMBOLIC_REGRESSION_TEMPLATE_SEARCH_PASS`

## PySR Target Fixture Comparison

- EML holdout MSE: `3.638040`
- Standard holdout MSE: `3.431470`
- EML lower holdout MSE: `False`
- EML best complexity: `17`
- Standard best complexity: `16`

## Run Rows

- `psi_residual` / `eml_native`: holdout `3.638040`, complexity `17`, equation `(((logx + 3.6859266e-5) - logx) * ((eml(sqrtx, sqrtx) + 0.1608118) - (sqrtx + sqrtx))) + -2.01603`
- `psi_residual` / `standard_exp_log_trig`: holdout `3.431470`, complexity `16`, equation `-0.9114485 / (sin(exp(sqrtx / -3.185608)) + exp(-0.72518694 - sin(exp(sqrtx * 0.26826483))))`
- `shuffled_residual_control` / `eml_native`: holdout `4.358986`, complexity `17`, equation `-1.1374773 - (-0.6964453 + ((sqrtx + 1.1045513) / (sqrtx + (0.50008404 / ((sqrtx + x) + -6.683246)))))`
- `shuffled_residual_control` / `standard_exp_log_trig`: holdout `4.389154`, complexity `13`, equation `log_abs(cos(exp(-1.0454743) + sin(cos(cos(x / 0.9205446))))) + -1.0454743`
- `gaussian_bumps_control` / `eml_native`: holdout `0.572400`, complexity `17`, equation `(eml(logx / sqrtx, (sqrtx / 0.8642657) * eml(1.3506802, x)) / (logx - -0.5319307)) * logx`
- `gaussian_bumps_control` / `standard_exp_log_trig`: holdout `0.054920`, complexity `17`, equation `((cos(sqrtx) * 1.6335157) + ((sqrtx + -0.73744863) / sqrtx)) - cos((sqrtx / 0.72011274) + -1.1053488)`

## Next Run Contract

- pysr installed
- private runner only
- fixed random seed
- max runtime bound
- artifact capture

## Non-Claims

- This artifact records a bounded private PySR run.
- This artifact does not claim autonomous discovery.
- This artifact does not prove RH or discover zeta zeros.
- This artifact is private-only and does not promote Atlas entries.
