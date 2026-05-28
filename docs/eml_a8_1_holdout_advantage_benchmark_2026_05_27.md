# EML-A8.1 Holdout Advantage Benchmark

Date: 2026-05-27

A8.1 makes the EML Advantage Lab harder to fool. It keeps the first advantage
scoreboard as the baseline, then tests whether those classifications survive
shifted, edge, and stress profiles.

## What It Adds

- `EML Advantage Holdout Packet v0`
- shifted/edge/stress profiles for R10/R10B runtime cases
- holdout checks for prime-signature log recovery
- research-only retention for the psi residual template
- three negative controls:
  - Gaussian bumps
  - arbitrary polynomial
  - logaddexp stable runtime

## Boundary

A8.1 does not prove EML advantage. It does not claim broad EML superiority,
compiler correctness, theorem discovery, RH proof, zeta-zero discovery,
hardware measurement, deployment, public savings, or public performance.

The goal is narrower and better: preserve only advantage labels that survive
new profiles and make weakened labels visible.

