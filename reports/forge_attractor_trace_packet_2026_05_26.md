# Forge Attractor Trace Packet

Schema: `monogate.forge_attractor_trace_packet.v1`
Depth: `3`
Leaf dimension: `8`
Steps per regime: `80`

| regime | label | best loss | domain failures | overflow | saturation | finite steps |
|---|---|---:|---:|---:|---:|---:|
| naive_gradient | collapsed | 1.536e+07 | 79 | 0 | 1 | 1 |
| regularized_gradient | domain_failed | n/a | 80 | 0 | 0 | 0 |
| guarded_gradient | saturated | 4.866e+02 | 0 | 0 | 80 | 80 |
| boundary_aware_gradient | saturated | 2.472e+17 | 0 | 0 | 80 | 80 |
| random_search | saturated | 5.768e-01 | 0 | 10 | 63 | 70 |

## MachLib / Lean Obligations

- Prove V(unit_ball_d) / V([-1,1]^d) -> 0.
- Prove cube boundary-shell probability 1 - (1 - epsilon)^d -> 1.
- For independent symmetric leaves, prove raw right-child positivity probability decays exponentially by first EML layer.
- Connect guarded lowering packets to domain-preservation obligations.

This packet compares optimizer regimes against the same high-dimensional
EML terminal geometry. It is sampled evidence only and does not claim a
phantom-attractor theorem, optimizer release, hardware result, or formal
verification.
