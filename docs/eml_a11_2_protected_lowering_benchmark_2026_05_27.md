# EML-A11.2 Protected Lowering Benchmark

Date: 2026-05-27

Status: `EML_A11_2_PROTECTED_LOWERING_BENCHMARK_PASS`

A11.2 records deterministic numeric-stability evidence for the protected
lowerings recommended by the guard/mock-compiler path.

Cases:

- `expm1_near_zero`: compares `exp(x) - 1` against `expm1(x)` on a near-zero
  edge grid.
- `logsumexp_edge_grid`: compares naive `ln(sum(exp(x_i)))` against a
  max-shifted protected log-sum-exp form on large positive/negative edge
  grids.

## Boundary

- Numeric stability fixture only.
- No speed, latency, energy, throughput, compiler implementation, compiler correctness, production readiness, or EML advantage claim.
