# EML-A14 Forge/eFrog Evidence Export UX

Date: 2026-05-29

Status: `EML_A14_FORGE_EFROG_EXPORT_UX_PASS`

A14 turns existing A13/A13.2/PCC10 evidence into private developer-facing export packets.
It is not a compiler, decompiler, proof, runtime, or public product claim.

| Export | Function | Family | Semantic status | Samples | Runtime advisory | Roundtrip targets |
|---|---|---|---|---:|---|---|
| `gaussian_semantic_compare_v0_export_packet_v0` | `gaussian` | `gaussian` | `pass` | 4 | `standard_or_protected_runtime_until_benchmarked` | `javascript,python` |
| `sigmoid_semantic_compare_v0_export_packet_v0` | `sigmoid` | `numpy_softplus` | `pass` | 5 | `standard_or_protected_runtime_until_benchmarked` | `javascript,python` |
| `poly_quadratic_semantic_compare_v0_export_packet_v0` | `poly_quadratic` | `unmapped` | `pass` | 4 | `standard_or_protected_runtime_until_benchmarked` | `javascript,python` |
| `gaussian_stable_holdout_semantic_compare_v0_export_packet_v0` | `gaussian_stable` | `gaussian` | `pass` | 4 | `standard_or_protected_runtime_until_benchmarked` | `javascript,python` |
| `rc_decay_holdout_semantic_compare_v0_export_packet_v0` | `rc_decay_stable` | `rc_decay` | `pass` | 4 | `standard_or_protected_runtime_until_benchmarked` | `javascript,python` |
| `stretched_exponential_holdout_semantic_compare_v0_export_packet_v0` | `stretched_exponential` | `stretched_exponential` | `pass` | 5 | `standard_or_protected_runtime_until_benchmarked` | `javascript,python` |
| `stable_sigmoid_holdout_semantic_compare_v0_export_packet_v0` | `stable_sigmoid` | `stable_sigmoid` | `pass` | 7 | `branch_stable_sigmoid` | `javascript,python` |
| `voltage_divider_holdout_semantic_compare_v0_export_packet_v0` | `voltage_divider` | `clamp_guard` | `pass` | 4 | `standard_or_protected_runtime_until_benchmarked` | `javascript,python` |

## Summary

- Export packets: `8`
- Semantic cases: `8`
- Semantic passes: `8`
- Roundtrip cases available: `36`
- Roundtrip passes available: `36`
- Runtime advisories attached: `1`
- S24 sigmoid runtime recommendation attached: `True`

## Boundary

- No Forge/eFrog behavior change.
- No compiler correctness or formal equivalence claim.
- No broad EML advantage or runtime performance claim.
- No deployment or public-readiness claim.
