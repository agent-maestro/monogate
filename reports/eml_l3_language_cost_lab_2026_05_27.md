# EML-L3 Language Cost Lab

Date: 2026-05-27

Status: `EML_LANGUAGE_COST_LAB_PASS`

This is an internal language cost lab. It compares surface EML syntax,
expanded expression trees, canonical trees, and DAG-style unique subtree
counts. It does not change public SuperBEST claims.

| Program | Surface ops | Expanded ops | DAG unique ops | Repeated subtrees | Obligations | Checked witnesses |
|---|---:|---:|---:|---:|---:|---:|
| `gaussian_energy_v0` | `7` | `7` | `4` | `3` | `1` | `0` |
| `guarded_eml_softplus_v0` | `1` | `6` | `6` | `0` | `4` | `0` |
| `raw_eml_primitive_v0` | `1` | `3` | `3` | `0` | `3` | `0` |
| `sigmoid_derivative_v0` | `10` | `10` | `6` | `4` | `2` | `1` |
| `softplus_pair_v0` | `4` | `4` | `4` | `0` | `3` | `1` |

## Boundary

- Internal DAG reuse is a measurement aid, not a public savings claim.
- Surface-to-expanded deltas are language expansion facts, not proof claims.
- Obligation and checked-witness counts come from the existing packet builder.
- Forge/compiler behavior is unchanged.
