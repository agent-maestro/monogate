# EML-R10B Runtime Bakeoff

Date: 2026-05-27

R10B consumes the R12 generated lowering stubs and runs broader deterministic
float64 and float32 grids against reference math.

This closes the immediate runtime-bakeoff blocker for the generated stubs. It
does not close compiler correctness or semantic equivalence.

## Result

The 2026-05-27 run produced seven runtime bakeoff packets:

- `exp_from_eml_v0`
- `subtraction_boundary_v0`
- `bose_boundary_expm1_v0`
- `ln_from_eml_v0`
- `softplus_pair_v0`
- `sigmoid_derivative_v0`
- `gaussian_energy_v0`

All seven passed the local float64/float32 bakeoff.

## Review Impact

RH-A1 now classifies the R11/R12 compiler claim and R12 generated-stub claim as
`runtime_bakeoff_local`.

RH-A2 now routes:

- compiler correctness to `R10C scoped semantic proof`
- generated stub validation to `R10C scoped semantic proof`
- softplus performance to `R10D implementation benchmark`

## Non-Claims

- No compiler correctness claim.
- No formal semantic equivalence claim.
- No public performance or savings claim.
- No GPU, embedded, hardware, cache, or energy measurement claim.
- No Forge/compiler behavior change.
- No deployment or production lowering claim.
