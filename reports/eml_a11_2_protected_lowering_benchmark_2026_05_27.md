# EML-A11.2 Protected Lowering Benchmark

Date: 2026-05-27

Status: `EML_A11_2_PROTECTED_LOWERING_BENCHMARK_PASS`

| Case | Samples | Protected better | Protected no worse | Naive non-finite | Protected non-finite |
|---|---:|---:|---:|---:|---:|
| `expm1_near_zero` | 11 | 10 | 11 | 0 | 0 |
| `logsumexp_edge_grid` | 9 | 5 | 9 | 4 | 0 |

## Boundary

- Numeric stability fixture only.
- No speed, latency, energy, throughput, compiler implementation, compiler correctness, production readiness, or EML advantage claim.
