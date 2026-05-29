# EML-A14 Forge/eFrog Evidence Export UX

Date: 2026-05-29

Status: `EML_A14_FORGE_EFROG_EXPORT_UX_PASS`

A14 turns existing A13/A13.2/PCC10 evidence into private developer-facing export packets.
It is not a compiler, decompiler, proof, runtime, or public product claim.

| Export | Function | Family | Semantic status | Samples | Roundtrip targets |
|---|---|---|---|---:|---|
| `gaussian_semantic_compare_v0_export_packet_v0` | `gaussian` | `gaussian` | `pass` | 4 | `javascript,python` |
| `sigmoid_semantic_compare_v0_export_packet_v0` | `sigmoid` | `numpy_softplus` | `pass` | 5 | `javascript,python` |
| `poly_quadratic_semantic_compare_v0_export_packet_v0` | `poly_quadratic` | `unmapped` | `pass` | 4 | `javascript,python` |
| `gaussian_stable_holdout_semantic_compare_v0_export_packet_v0` | `gaussian_stable` | `gaussian` | `pass` | 4 | `javascript,python` |
| `rc_decay_holdout_semantic_compare_v0_export_packet_v0` | `rc_decay_stable` | `rc_decay` | `pass` | 4 | `javascript,python` |
| `voltage_divider_holdout_semantic_compare_v0_export_packet_v0` | `voltage_divider` | `clamp_guard` | `pass` | 4 | `javascript,python` |

## Summary

- Export packets: `6`
- Semantic cases: `6`
- Semantic passes: `6`
- Roundtrip cases available: `32`
- Roundtrip passes available: `32`

## Boundary

- No Forge/eFrog behavior change.
- No compiler correctness or formal equivalence claim.
- No broad EML advantage or runtime performance claim.
- No deployment or public-readiness claim.
