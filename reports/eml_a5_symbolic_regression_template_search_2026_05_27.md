# EML-A5 Symbolic Regression Template Search

Date: 2026-05-27

Status: `EML_SYMBOLIC_REGRESSION_TEMPLATE_SEARCH_PASS`

This is a deterministic fixed-template search, not a full PySR run.

| Template | Family | Nodes | Params | Best gamma | MSE | Error from first known zero |
|---|---|---:|---:|---:|---:|---:|
| `eml_critical_one_node` | `eml` | `1` | `1` | `14.087044` | `5.339289` | `0.047682` |
| `standard_profiled_sqrt_cos_sin` | `standard` | `5` | `3` | `13.929465` | `5.253005` | `0.205260` |
| `eml_wrong_exponent_03` | `negative_control` | `1` | `1` | `14.104552` | `5.814425` | `0.030173` |
| `eml_wrong_exponent_07` | `negative_control` | `1` | `1` | `20.950475` | `5.769475` | `6.815750` |
| `plain_profiled_cos_sin` | `negative_control` | `3` | `3` | `14.052026` | `5.461535` | `0.082699` |
| `constant_baseline` | `baseline` | `0` | `1` | n/a | `3.555752` | n/a |

## Rankings

- By MSE: `constant_baseline, standard_profiled_sqrt_cos_sin, eml_critical_one_node, plain_profiled_cos_sin, eml_wrong_exponent_07, eml_wrong_exponent_03`
- By localization: `eml_wrong_exponent_03, eml_critical_one_node, plain_profiled_cos_sin, standard_profiled_sqrt_cos_sin, eml_wrong_exponent_07`
- By complexity-adjusted score: `constant_baseline, eml_critical_one_node, standard_profiled_sqrt_cos_sin, plain_profiled_cos_sin, eml_wrong_exponent_07, eml_wrong_exponent_03`

## Interpretation

The EML critical-line template remains a compact candidate and leads the simple complexity-adjusted score on this fixture, but the template search is intentionally ambiguous: a wrong-exponent control localizes slightly closer, and low-MSE baselines show that MSE alone is not evidence of structure.

## Non-Claims

- This search does not prove RH.
- This search does not discover zeta zeros.
- This search is not a full PySR run.
- This search does not prove an EML grammar theorem.
- This search does not promote any Atlas entry publicly.
- This search does not change Forge/compiler behavior.
