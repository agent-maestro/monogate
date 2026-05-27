# EML-R12 Generated Lowering Stubs

Date: 2026-05-27

Status: `EML_R12_GENERATED_LOWERING_STUBS_PASS`

R12 turns R11 candidate lowering plans into generated fixture stubs and
validates the generated Python stubs on deterministic grids.

## Stub Packets

| Case | Decision | Lowered expression | Validation | Max abs error | Max rel error |
|---|---|---|---|---:|---:|
| `exp_from_eml_v0` | `emit_hybrid` | `np.exp(x)` | `pass` | 0.000e+00 | 0.000e+00 |
| `subtraction_boundary_v0` | `emit_standard` | `v - u` | `pass` | 0.000e+00 | 0.000e+00 |
| `bose_boundary_expm1_v0` | `emit_standard` | `np.expm1(x)` | `pass` | 0.000e+00 | 0.000e+00 |
| `ln_from_eml_v0` | `emit_standard` | `np.log(y)` | `pass` | 0.000e+00 | 0.000e+00 |
| `softplus_pair_v0` | `emit_standard` | `np.logaddexp(a, b)` | `pass` | 0.000e+00 | 0.000e+00 |
| `sigmoid_derivative_v0` | `emit_standard` | `stable_sigmoid(x) * (1.0 - stable_sigmoid(x))` | `pass` | 0.000e+00 | 0.000e+00 |
| `gaussian_energy_v0` | `emit_standard` | `2.0 * np.exp(-(x * x))` | `pass` | 0.000e+00 | 0.000e+00 |

## Summary

- Stub packets: `7`
- Validation pass: `7`
- Validation fail: `0`
- Compiler behavior changed: `False`
- Production lowering claim: `False`

## Boundary

- Generated fixture stubs only.
- No compiler correctness claim.
- No formal semantic equivalence claim.
- No deployment or production lowering claim.
