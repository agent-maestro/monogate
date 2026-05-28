# EML-A10 Expression Guard Lens

Date: 2026-05-27

A10 applies the A9 guard decision vocabulary to existing EML expression packet
fixtures.

First result:

- expression packets analyzed: `3`
- protected lowering recommendations: `1`
- blocked decisions: `1`
- proof-shape allowed: `1`

Interpretation:

The guard lens now gives packet-level decisions before any compiler behavior
changes. `softplus_pair_v0` recommends protected logaddexp-style lowering,
`sigmoid_derivative_v0` blocks until denominator guard evidence is explicit,
and `gaussian_energy_v0` remains proof/search-shape only.

Boundary:

A10 is a packet analyzer only. It does not change compiler behavior, prove
compiler correctness, claim production readiness, claim EML advantage, or
deploy anything.
