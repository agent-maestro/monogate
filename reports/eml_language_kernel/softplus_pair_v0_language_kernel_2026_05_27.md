# EML Language Kernel Result: softplus_pair_v0

Date: 2026-05-27

Status: `EML_LANGUAGE_KERNEL_CANDIDATE_PASS`

## Normalized Expression

`ln(exp(a) + exp(b))`

## Guards

- `positive` on `exp(a) + exp(b)`

## Emitted Packet

- Program: `softplus_pair_v0`
- Inputs: `a, b`
- Safe ranges: `2`

## Non-Claims

- No Forge/compiler behavior change.
- No public savings claim.
- No formal verification or theorem claim.
- No package publish or deploy.
