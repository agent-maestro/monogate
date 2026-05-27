# EML-R10 Cost and Stability Lab

Date: 2026-05-27

Status: `EML_R10_COST_STABILITY_LAB_PASS`

This lab compares EML-shaped implementations against standard or protected
implementations under deterministic finite-precision sampling. It is a
research filter, not a public savings or proof claim.

| Case | EML finite | EML max rel err | Std max rel err | EML ns/sample | Std ns/sample | Recommendation |
|---|---:|---:|---:|---:|---:|---|
| `exp_from_eml_v0` | `1.000` | `0.000e+00` | `0.000e+00` | `3.1` | `2.5` | `use_hybrid` |
| `subtraction_boundary_v0` | `1.000` | `4.380e-16` | `0.000e+00` | `10.0` | `0.6` | `use_standard` |
| `bose_boundary_expm1_v0` | `1.000` | `1.126e-06` | `0.000e+00` | `3.1` | `2.5` | `use_standard` |
| `ln_from_eml_v0` | `1.000` | `0.000e+00` | `0.000e+00` | `14.2` | `2.6` | `use_standard` |
| `softplus_pair_v0` | `1.000` | `1.136e-15` | `0.000e+00` | `7.2` | `4.7` | `use_standard` |
| `sigmoid_derivative_v0` | `1.000` | `3.494e-16` | `0.000e+00` | `6.8` | `11.9` | `use_standard` |
| `gaussian_energy_v0` | `1.000` | `0.000e+00` | `0.000e+00` | `7.0` | `3.8` | `use_standard` |

## Summary

- Cost packets: `7`
- `use_eml`: `0`
- `use_standard`: `6`
- `use_hybrid`: `1`
- `research_only`: `0`

## Boundary

- This does not benchmark CPU/GPU/embedded energy or cache behavior.
- This does not prove semantic equivalence.
- This does not change Forge/compiler behavior.
- This intentionally blocks broad EML-superiority claims.
