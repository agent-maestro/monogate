# EML-S23 Sigmoid/Logistic Dedicated Holdout

Date: 2026-05-29

Status: `EML_S23_SIGMOID_LOGISTIC_HOLDOUT_PASS`

S23 executes the S22-selected sigmoid/logistic source-family promotion.
It is private holdout evidence, not a proof, runtime benchmark, compiler correctness result, or public claim.

## Toolchain Linkage

- A13 roundtrip packets: `2`
- A13 roundtrip passes: `2`
- A13.2 semantic comparison pass: `True`
- A14 export linked: `True`
- S20 primary style: `eml_native`

## Profiles

| Profile | Noise kind | Samples | Decision | Range | Max abs error |
|---|---|---:|---|---|---:|
| `safe_sigmoid_grid` | `none` | 2048 | `bounded_transition_semantic_tie` | `4.248e-18..1.000e+00` | `0.000e+00` |
| `transition_sigmoid_grid` | `transition` | 2048 | `bounded_transition_semantic_tie` | `3.354e-04..9.997e-01` | `0.000e+00` |
| `noisy_input_sigmoid_grid` | `input_perturbation` | 2048 | `bounded_transition_semantic_tie` | `3.195e-04..9.997e-01` | `0.000e+00` |
| `overflow_boundary_sigmoid_grid` | `overflow_boundary` | 2048 | `bounded_transition_semantic_tie` | `8.757e-27..1.000e+00` | `0.000e+00` |

## Boundary

- No broad EML advantage claim.
- No source-family or sigmoid generalization claim.
- No runtime performance claim.
- No compiler correctness or formal equivalence claim.
- No proof, deployment, package publish, or public-readiness claim.
