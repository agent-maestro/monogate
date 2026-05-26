# Forge Heuristic Frontier

Schema: `monogate.forge_heuristic_frontier.v1`
Steps per run: `60`
Seeds per case: `5`

| depth | regime | converged | mean best loss | finite | saturation | domain fail |
|---:|---|---:|---:|---:|---:|---:|
| 2 | guarded_gradient | 2/5 | 3.624e-02 | 1.00 | 0.01 | 0.00 |
| 2 | boundary_aware_gradient | 0/5 | 1.257e-01 | 1.00 | 0.01 | 0.00 |
| 2 | log_domain_gradient | 0/5 | 6.364e-02 | 1.00 | 0.01 | 0.00 |
| 2 | random_search | 0/5 | 1.849e-01 | 1.00 | 0.68 | 0.00 |
| 3 | guarded_gradient | 0/5 | 9.415e+16 | 1.00 | 0.99 | 0.00 |
| 3 | boundary_aware_gradient | 0/5 | 9.886e+16 | 1.00 | 0.62 | 0.00 |
| 3 | log_domain_gradient | 0/5 | 9.886e+16 | 1.00 | 0.95 | 0.00 |
| 3 | random_search | 0/5 | 6.991e-01 | 0.85 | 0.72 | 0.00 |
| 4 | guarded_gradient | 0/5 | 1.883e+17 | 1.00 | 1.00 | 0.00 |
| 4 | boundary_aware_gradient | 0/5 | 1.977e+17 | 1.00 | 1.00 | 0.00 |
| 4 | log_domain_gradient | 0/5 | 1.977e+17 | 1.00 | 1.00 | 0.00 |
| 4 | random_search | 0/5 | 8.197e+01 | 0.22 | 0.20 | 0.05 |
| 5 | guarded_gradient | 0/5 | 1.883e+17 | 1.00 | 1.00 | 0.00 |
| 5 | boundary_aware_gradient | 0/5 | 1.977e+17 | 1.00 | 1.00 | 0.00 |
| 5 | log_domain_gradient | 0/5 | 1.977e+17 | 1.00 | 1.00 | 0.00 |
| 5 | random_search | 0/5 | 8.393e+02 | 0.01 | 0.01 | 0.06 |

## Recommendations

- Treat log-domain parameterization as the next Forge baseline candidate when saturation dominates guarded search.
- Prefer boundary-aware guarded search when formal domain preservation matters and log-domain transforms are unavailable.
- Keep random search as a control, not as a release heuristic.
- Broaden depth only after replay packets show reduced saturation pressure.

This packet is sampled evidence only. It compares candidate Forge
heuristics; it does not promote any optimizer to release status.
