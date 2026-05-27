# EML-R11 Hybrid Lowering Planner

Date: 2026-05-27

Status: `EML_R11_HYBRID_LOWERING_PLANNER_PASS`

Monogate does not compile beauty directly. It routes symbolic forms
through evidence before choosing EML, standard, hybrid, or blocked
lowering.

| Case | R10 recommendation | Lowering decision | Selected implementation |
|---|---|---|---|
| `exp_from_eml_v0` | `use_hybrid` | `emit_hybrid` | `preserve EML packet identity; lower runtime call to exp(x)` |
| `subtraction_boundary_v0` | `use_standard` | `emit_standard` | `v - u` |
| `bose_boundary_expm1_v0` | `use_standard` | `emit_standard` | `expm1(x)` |
| `ln_from_eml_v0` | `use_standard` | `emit_standard` | `log(y)` |
| `softplus_pair_v0` | `use_standard` | `emit_standard` | `logaddexp(a, b)` |
| `sigmoid_derivative_v0` | `use_standard` | `emit_standard` | `stable_sigmoid(x) * (1 - stable_sigmoid(x))` |
| `gaussian_energy_v0` | `use_standard` | `emit_standard` | `2 * exp(-(x * x))` |

## Summary

- Plans: `7`
- `emit_eml`: `0`
- `emit_standard`: `6`
- `emit_hybrid`: `1`
- `block_lowering`: `0`

## Boundary

- Candidate plans only.
- Forge/compiler behavior is unchanged.
- No public savings, proof, or production lowering claim is made.
