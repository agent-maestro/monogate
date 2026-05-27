# EML Language Kernel Result: sigmoid_derivative_v0

Date: 2026-05-27

Status: `EML_LANGUAGE_KERNEL_CANDIDATE_PASS`

## Normalized Expression

`1 / (1 + exp(-x)) * (1 - 1 / (1 + exp(-x)))`

## Canonical Form

- Canonical hash: `sha256:6eda998b3070f828b704bcef4476dfc764d8f4fe76ea0ee985036fb6b699606a`
- Expansion tags: `0`

## Guards

- `nonzero` on `1 + exp(-x)`

## Emitted Packet

- Program: `sigmoid_derivative_v0`
- Inputs: `x`
- Safe ranges: `1`

## Non-Claims

- No Forge/compiler behavior change.
- No public savings claim.
- No formal verification or theorem claim.
- No package publish or deploy.
