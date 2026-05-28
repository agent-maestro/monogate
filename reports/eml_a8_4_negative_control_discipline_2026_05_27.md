# EML-A8.4 Negative-Control Discipline

Date: 2026-05-27

Status: `EML_A8_4_NEGATIVE_CONTROL_DISCIPLINE_PASS`

A8.4 records the cases where EML should lose or remain blocked.
This prevents the Advantage Lab from becoming a one-way promotion tool.

| Control | Class | Expected winner | Evidence status |
|---|---|---|---|
| `expm1_runtime_anti_example_v1` | `protected_runtime` | `standard` | `confirmed` |
| `logaddexp_negative_control_v0` | `protected_runtime` | `standard` | `confirmed` |
| `gaussian_bumps_negative_control_v0` | `non_eml_structure` | `standard` | `confirmed` |
| `arbitrary_polynomial_negative_control_v0` | `non_eml_structure` | `standard` | `confirmed` |
| `unstable_deep_tree_negative_control_v0` | `unstable_deep_tree` | `blocked` | `registered_for_next_holdout` |

## Summary

- Controls: `5`
- Confirmed controls: `4`
- Registered for next holdout: `1`
- Negative controls exhaustive: `False`
- EML advantage proved: `False`

## Boundary

- Negative-control guard only.
- No exhaustive falsification, public promotion, broad EML superiority, runtime performance, theorem discovery, or compiler correctness claim.
