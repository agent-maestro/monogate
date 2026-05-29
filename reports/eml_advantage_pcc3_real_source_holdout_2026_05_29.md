# EML-ADV-PCC3 Real-Source Holdout

Date: 2026-05-29

Status: `EML_ADV_PCC3_REAL_SOURCE_HOLDOUT_PASS`

PCC3 links the EML Advantage proof-carrying contract to a real eFrog holdout source.
The selected source is `examples/rc_decay_stable.py`.

| Profile | Winner | Max abs error | Max rel error |
|---|---|---:|---:|
| `nominal_decay_grid` | `semantic_tie` | `0.000e+00` | `0.000e+00` |
| `long_tail_decay_grid` | `semantic_tie` | `0.000e+00` | `0.000e+00` |
| `small_tau_edge_grid` | `semantic_tie` | `0.000e+00` | `0.000e+00` |

## Summary

- Holdouts: `1`
- Profiles: `3`
- Passing profiles: `3`
- Source linked: `True`
- Broad EML advantage claim: `False`
- Runtime performance claim: `False`

## Boundary

- Private real-source holdout only.
- No broad EML advantage, runtime performance, compiler correctness, formal equivalence, proof, production, deployment, or public-readiness claim.
