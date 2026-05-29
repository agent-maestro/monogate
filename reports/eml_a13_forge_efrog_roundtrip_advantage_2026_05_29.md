# EML-A13 Forge/eFrog Roundtrip Advantage Lab

Date: 2026-05-29

Status: `EML_A13_FORGE_EFROG_ROUNDTRIP_ADVANTAGE_PASS`

A13 runs existing eFrog source frontends and a small holdout slice through
Forge's Python and JavaScript targets
and records bounded roundtrip evidence for the EML toolchain thesis.

| Case | Roundtrip | Advantage class | Standard nodes | EML nodes | Shape hash |
|---|---|---|---:|---:|---|
| `python_to_forge_python_v0` | `pass` | `eml_toolchain_surface_win` | 15 | 15 | `sha256:26313228728` |
| `python_to_forge_javascript_v0` | `pass` | `eml_toolchain_surface_win` | 15 | 15 | `sha256:26313228728` |
| `c_to_forge_python_v0` | `pass` | `eml_toolchain_surface_win` | 18 | 15 | `sha256:26313228728` |
| `c_to_forge_javascript_v0` | `pass` | `eml_toolchain_surface_win` | 18 | 15 | `sha256:26313228728` |
| `javascript_to_forge_python_v0` | `pass` | `roundtrip_pass_standard_surface_smaller` | 13 | 14 | `sha256:eebcae5d9d8` |
| `javascript_to_forge_javascript_v0` | `pass` | `roundtrip_pass_standard_surface_smaller` | 13 | 14 | `sha256:eebcae5d9d8` |
| `rust_to_forge_python_v0` | `pass` | `eml_toolchain_surface_win` | 16 | 14 | `sha256:4df4106e49c` |
| `rust_to_forge_javascript_v0` | `pass` | `eml_toolchain_surface_win` | 16 | 14 | `sha256:4df4106e49c` |
| `matlab_to_forge_python_v0` | `pass` | `roundtrip_pass_standard_surface_smaller` | 11 | 14 | `sha256:4df4106e49c` |
| `matlab_to_forge_javascript_v0` | `pass` | `roundtrip_pass_standard_surface_smaller` | 11 | 14 | `sha256:4df4106e49c` |
| `java_to_forge_python_v0` | `pass` | `eml_toolchain_surface_win` | 20 | 15 | `sha256:26313228728` |
| `java_to_forge_javascript_v0` | `pass` | `eml_toolchain_surface_win` | 20 | 15 | `sha256:26313228728` |
| `go_to_forge_python_v0` | `pass` | `roundtrip_pass_standard_surface_smaller` | 5 | 9 | `sha256:e35c4db8c37` |
| `go_to_forge_javascript_v0` | `pass` | `roundtrip_pass_standard_surface_smaller` | 5 | 9 | `sha256:e35c4db8c37` |
| `kotlin_to_forge_python_v0` | `pass` | `roundtrip_pass_standard_surface_smaller` | 6 | 9 | `sha256:e35c4db8c37` |
| `kotlin_to_forge_javascript_v0` | `pass` | `roundtrip_pass_standard_surface_smaller` | 6 | 9 | `sha256:e35c4db8c37` |
| `gdscript_to_forge_python_v0` | `pass` | `roundtrip_pass_standard_surface_smaller` | 17 | 18 | `sha256:81bc3c1f621` |
| `gdscript_to_forge_javascript_v0` | `pass` | `roundtrip_pass_standard_surface_smaller` | 17 | 18 | `sha256:81bc3c1f621` |
| `lua_to_forge_python_v0` | `pass` | `roundtrip_pass_standard_surface_smaller` | 14 | 18 | `sha256:81bc3c1f621` |
| `lua_to_forge_javascript_v0` | `pass` | `roundtrip_pass_standard_surface_smaller` | 14 | 18 | `sha256:81bc3c1f621` |
| `julia_to_forge_python_v0` | `pass` | `roundtrip_pass_standard_surface_smaller` | 14 | 18 | `sha256:81bc3c1f621` |
| `julia_to_forge_javascript_v0` | `pass` | `roundtrip_pass_standard_surface_smaller` | 14 | 18 | `sha256:81bc3c1f621` |
| `solidity_to_forge_python_v0` | `pass` | `eml_toolchain_surface_win` | 14 | 14 | `sha256:c7213608e6d` |
| `solidity_to_forge_javascript_v0` | `pass` | `eml_toolchain_surface_win` | 14 | 14 | `sha256:c7213608e6d` |
| `python_holdout_gaussian_stable_to_forge_python_v0` | `pass` | `roundtrip_pass_standard_surface_smaller` | 16 | 21 | `sha256:5f7c307be3f` |
| `python_holdout_gaussian_stable_to_forge_javascript_v0` | `pass` | `roundtrip_pass_standard_surface_smaller` | 16 | 21 | `sha256:5f7c307be3f` |
| `python_holdout_rc_decay_stable_to_forge_python_v0` | `pass` | `roundtrip_pass_standard_surface_smaller` | 14 | 18 | `sha256:b26bf1e8c6a` |
| `python_holdout_rc_decay_stable_to_forge_javascript_v0` | `pass` | `roundtrip_pass_standard_surface_smaller` | 14 | 18 | `sha256:b26bf1e8c6a` |
| `python_holdout_poly_horner_to_forge_python_v0` | `pass` | `roundtrip_pass_standard_surface_smaller` | 15 | 37 | `sha256:b9c647885b5` |
| `python_holdout_poly_horner_to_forge_javascript_v0` | `pass` | `roundtrip_pass_standard_surface_smaller` | 15 | 37 | `sha256:b9c647885b5` |
| `python_holdout_voltage_divider_to_forge_python_v0` | `pass` | `roundtrip_pass_standard_surface_smaller` | 7 | 8 | `sha256:8d55824da11` |
| `python_holdout_voltage_divider_to_forge_javascript_v0` | `pass` | `roundtrip_pass_standard_surface_smaller` | 7 | 8 | `sha256:8d55824da11` |

## Summary

- Cases: `32`
- Holdout cases: `8`
- Targets: `javascript, python`
- Roundtrip passes: `32`
- EML surface wins: `10`
- Standard surface smaller: `22`

## Boundary

- Private toolchain evidence only.
- No Forge or eFrog behavior change.
- No compiler correctness or formal semantic equivalence claim.
- No broad EML advantage, runtime performance, production readiness, or public safety claim.
