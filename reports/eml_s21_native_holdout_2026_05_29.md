# EML-S21 Native Holdout

Date: 2026-05-29

Status: `EML_S21_NATIVE_HOLDOUT_PASS`

S21 uses the S20 style atlas to select the EML-native lane and tests a new stretched-exponential surface.
It is a private semantic holdout, not a broad advantage, runtime, proof, compiler, or public claim.

## Holdout

- Source family: `stretched_exponential`
- Standard form: `amplitude * exp(-((max(t, 0) / scale)^shape))`
- EML form: `amplitude * eml(-((max(t, 0) / scale)^shape), 1)`

| Profile | Noise kind | Samples | Decision | Max abs error | Max rel error |
|---|---|---:|---|---:|---:|
| `clean_stretched_exponential_grid` | `none` | 2048 | `eml_native_semantic_tie` | `0.000e+00` | `0.000e+00` |
| `noisy_input_stretched_exponential_grid` | `input_perturbation` | 2048 | `eml_native_semantic_tie` | `0.000e+00` | `0.000e+00` |
| `long_tail_stretched_exponential_grid` | `tail_sweep` | 2048 | `eml_native_semantic_tie` | `0.000e+00` | `0.000e+00` |
| `shape_sweep_stretched_exponential_grid` | `shape_sweep` | 2048 | `eml_native_semantic_tie` | `0.000e+00` | `0.000e+00` |

## Summary

- Profiles: `4`
- Passing profiles: `4`
- Total samples: `8192`
- EML-native semantic tie: `True`

## Boundary

- No broad EML advantage claim.
- No EML-native generalization claim.
- No runtime performance claim.
- No compiler correctness or formal equivalence claim.
- No proof, deployment, package publish, or public-readiness claim.
