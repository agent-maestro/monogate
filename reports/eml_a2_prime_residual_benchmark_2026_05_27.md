# EML-A2 Prime Residual Benchmark

Date: 2026-05-27

Status: `EML_PRIME_RESIDUAL_BENCHMARK_PASS`

This is a fixed-fixture grammar benchmark, not a theorem lane.

| Model | Grammar nodes | Free parameters | Best gamma | MSE | Error from first known zero |
|---|---:|---:|---:|---:|---:|
| EML-shaped | `1` | `1` | `14.087044` | `5.339289` | `0.047682` |
| Standard profiled | `5` | `3` | `13.929465` | `5.253005` | `0.205260` |

## Interpretation

On this fixed psi(x)-x fixture, the EML-shaped one-parameter scan lands closer to the first known zeta-zero frequency; the profiled standard basis has lower MSE because it fits two amplitudes at each frequency.

## Negative Controls

| Control | EML best gamma | Standard best gamma | Status |
|---|---:|---:|---|
| `shuffled_residual` | `25.588235` | `5.000000` | `context_only` |
| `gaussian_bumps` | `5.963705` | `5.000000` | `context_only` |

## Non-Claims

- This benchmark does not prove RH.
- This benchmark does not discover zeta zeros.
- This benchmark does not prove an EML grammar theorem.
- This benchmark does not promote any Atlas entry publicly.
- This benchmark does not change Forge/compiler behavior.
- Null results are acceptable for future runs.
