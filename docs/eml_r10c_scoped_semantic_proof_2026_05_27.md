# EML-R10C Scoped Semantic Proof

Date: 2026-05-27

R10C records scoped rewrite certificates for selected R12 lowered forms after
the R10B runtime bakeoff.

It is intentionally narrow. The certificates cover named expressions under
listed domain guards. They do not prove compiler correctness or full EML
semantics.

## Covered Cases

- `exp_from_eml_v0`
- `subtraction_boundary_v0`
- `bose_boundary_expm1_v0`
- `ln_from_eml_v0`

## Result

The 2026-05-27 run created four scoped semantic proof packets. All four passed.

## Review Impact

RH-A1 now classifies the R11 compiler-lowering claim and R12 generated-stub
claim as `scoped_semantic_proof`.

RH-A2 now routes both to `R10E formal compiler proof skeleton`.

## Non-Claims

- No compiler correctness claim.
- No full EML semantics claim.
- No formal compiler proof claim.
- No production lowering claim.
- No deployment or package publishing.
