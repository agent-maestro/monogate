# FEF-P106 Side-Effect Expected Samples

Date: 2026-06-01

Status: `FEF_P106_SIDE_EFFECT_EXPECTED_SAMPLES_PASS`

Decision: `side_effect_expected_samples_recorded_support_blocked`

FEF-P106 records source-semantics-only expected samples for one side-effect fixture.

## Summary

- Selected fixture: `c_global_state_update_v0`
- Sample count: `7`
- Call expected count: `4`
- Guard-false no-call count: `3`
- State write expected count: `4`
- Effect boundary expected count: `8`
- Runtime execution performed: `False`
- External calls performed: `False`
- Memory writes performed: `False`
- Effect policies applied: `False`

## Samples

| Sample | x | initial state | call expected | expected return |
|---|---:|---:|---|---:|
| `sample_00` | `-2.0` | `5.0` | `False` | `5.0` |
| `sample_01` | `0.0` | `-1.0` | `False` | `-1.0` |
| `sample_02` | `0.25` | `3.0` | `True` | `1.5` |
| `sample_03` | `1.0` | `0.0` | `True` | `4.0` |
| `sample_04` | `2.5` | `-4.0` | `True` | `8.0` |
| `sample_05` | `-0.5` | `9.0` | `False` | `9.0` |
| `sample_06` | `10.0` | `1.0` | `True` | `21.0` |

## Boundary

- Expected samples only.
- No external calls performed.
- No runtime memory writes or state mutation.
- No effect-order, external-call, or memory-alias policy.
- No side-effect/call/memory support claim.
- No compiler-correctness, formal-equivalence, or runtime-performance claim.
