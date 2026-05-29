# EML-ADV-PCC2 Gap Response

Date: 2026-05-29

Status: `EML_ADV_PCC2_GAP_RESPONSE_PASS`

PCC2 responds to one EML Advantage Lab contract gap with a protected-runtime negative control.
It checks the cancellation-sensitive lane where raw `eml(x,e) = exp(x)-1` should lose to protected `expm1(x)`.

| Profile | Winner | Mean relative error improvement |
|---|---|---:|
| `tiny_symmetric_holdout` | `standard` | `8.474e+296` |
| `small_symmetric_holdout` | `standard` | `8.566e+292` |
| `one_sided_positive_edge` | `standard` | `2.858e+298` |

## Summary

- Negative controls: `1`
- Profiles: `3`
- Standard-win profiles: `3`
- All profiles favor protected standard: `True`
- Broad EML advantage claim: `False`
- Runtime performance claim: `False`

## Boundary

- Private gap response only.
- No broad EML advantage, public runtime performance, compiler correctness, formal equivalence, proof, production, or public-readiness claim.
