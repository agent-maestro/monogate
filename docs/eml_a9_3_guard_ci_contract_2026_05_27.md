# EML-A9.3 Guard CI Contract

Date: 2026-05-27

A9.3 locks the A9 guard fixtures and analyzer against drift.

Checks:

- fixture analyzer decisions still match expected decisions
- matched rule IDs still match expected rule IDs
- claim flags remain false
- non-claims remain present
- dev explorer guard decision copy matches generated source when present

Boundary:

A9.3 is a CI contract only. It does not change compiler behavior, prove
compiler correctness, claim production readiness, claim EML advantage, or
deploy anything.
