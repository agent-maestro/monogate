# EML-A13 Forge/eFrog Roundtrip Advantage Lab

Date: 2026-05-29

Status: `EML_A13_FORGE_EFROG_ROUNDTRIP_ADVANTAGE_PASS`

A13 runs existing eFrog source frontends through Forge's Python target
and records bounded roundtrip evidence for the EML toolchain thesis.

| Case | Roundtrip | Advantage class | Standard nodes | EML nodes | Shape hash |
|---|---|---|---:|---:|---|
| `python_to_forge_python_v0` | `pass` | `eml_toolchain_surface_win` | 15 | 15 | `sha256:26313228728` |
| `c_to_forge_python_v0` | `pass` | `eml_toolchain_surface_win` | 18 | 15 | `sha256:26313228728` |
| `javascript_to_forge_python_v0` | `pass` | `roundtrip_pass_standard_surface_smaller` | 13 | 14 | `sha256:eebcae5d9d8` |
| `rust_to_forge_python_v0` | `pass` | `eml_toolchain_surface_win` | 16 | 14 | `sha256:4df4106e49c` |
| `matlab_to_forge_python_v0` | `pass` | `roundtrip_pass_standard_surface_smaller` | 11 | 14 | `sha256:4df4106e49c` |
| `java_to_forge_python_v0` | `pass` | `eml_toolchain_surface_win` | 20 | 15 | `sha256:26313228728` |
| `go_to_forge_python_v0` | `pass` | `roundtrip_pass_standard_surface_smaller` | 5 | 9 | `sha256:e35c4db8c37` |
| `kotlin_to_forge_python_v0` | `pass` | `roundtrip_pass_standard_surface_smaller` | 6 | 9 | `sha256:e35c4db8c37` |
| `gdscript_to_forge_python_v0` | `pass` | `roundtrip_pass_standard_surface_smaller` | 17 | 18 | `sha256:81bc3c1f621` |
| `lua_to_forge_python_v0` | `pass` | `roundtrip_pass_standard_surface_smaller` | 14 | 18 | `sha256:81bc3c1f621` |
| `julia_to_forge_python_v0` | `pass` | `roundtrip_pass_standard_surface_smaller` | 14 | 18 | `sha256:81bc3c1f621` |
| `solidity_to_forge_python_v0` | `pass` | `eml_toolchain_surface_win` | 14 | 14 | `sha256:c7213608e6d` |

## Summary

- Cases: `12`
- Roundtrip passes: `12`
- EML surface wins: `5`
- Standard surface smaller: `7`

## Boundary

- Private toolchain evidence only.
- No Forge or eFrog behavior change.
- No compiler correctness or formal semantic equivalence claim.
- No broad EML advantage, runtime performance, production readiness, or public safety claim.
