# EML Language Kernel Result: sigmoid_derivative_v0

Date: 2026-05-27

Status: `EML_LANGUAGE_KERNEL_CANDIDATE_PASS`

## Normalized Expression

`1 / (1 + exp(-x)) * (1 - 1 / (1 + exp(-x)))`

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
