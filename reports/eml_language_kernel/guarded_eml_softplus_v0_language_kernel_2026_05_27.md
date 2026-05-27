# EML Language Kernel Result: guarded_eml_softplus_v0

Date: 2026-05-27

Status: `EML_LANGUAGE_KERNEL_CANDIDATE_PASS`

## Normalized Expression

`exp(x) - ln(ln(1 + exp(y)))`

## Canonical Form

- Canonical hash: `sha256:6a6fbd514b2283fdb15e2b1a58bf1a84ddbe379bf2b63c013f48860b636ca2f3`
- Expansion tags: `2`

## Guards

- `positive` on `ln(1 + exp(y))`

## Emitted Packet

- Program: `guarded_eml_softplus_v0`
- Inputs: `x, y`
- Safe ranges: `2`

## Non-Claims

- No Forge/compiler behavior change.
- No public savings claim.
- No formal verification or theorem claim.
- No package publish or deploy.
