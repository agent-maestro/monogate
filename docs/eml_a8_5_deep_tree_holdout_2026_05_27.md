# EML-A8.5 Deep Tree Holdout

Date: 2026-05-27

A8.5 stress-tests the practical weakness of EML trees: depth can amplify
finite-precision error, overflow, and blocked runtime behavior.

Result:

- Packets: `5`
- Max depth: `12`
- Blocked unstable deep trees: `3`
- Standard runtime wins: `1`
- Mixed identity supported: `1`
- EML structure supported under this stress: `0`

Interpretation:

This is an important negative result. EML remains useful as proof/search and
boundary notation, but deep runtime trees need compiler guards before public
advantage claims are allowed.

Boundary:

A8.5 does not prove deep-tree stability, EML advantage, broad EML superiority,
compiler correctness, runtime performance, theorem discovery, public Atlas
promotion, or deployment.
