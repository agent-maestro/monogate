# EML-R10F Proof-Assistant AST and Guard Model

Date: 2026-05-27

Status: `EML_R10F_PROOF_ASSISTANT_AST_GUARD_MODEL_PASS`

R10F freezes a small AST, guard vocabulary, and lowering relation
model for future proof-assistant work.

## Model Counts

- AST nodes: `10`
- Guards: `5`
- Lowering rules: `4`
- Open compiler obligations inherited from R10E: `5`
- A12 interpreter linked: `True`

## Lowering Rules

| Rule | Source | Target | Status |
|---|---|---|---|
| `lower-exp-minus-one-to-expm1` | `Sub(Exp(x), Const(1))` | `ProtectedExpm1(x)` | `model_stub_not_formalized` |
| `lower-log-sum-exp-to-protected` | `Log(Sum(map Exp xs))` | `ProtectedLogSumExp(xs)` | `model_stub_not_formalized` |
| `preserve-eml-proof-shape` | `Eml(x,y)` | `Eml(x,y)` | `model_stub_not_formalized` |
| `block-unsupported-lowering` | `UnsupportedOrUnstableTree` | `BlockedReview` | `routing_stub_not_formalized` |

## Boundary

- Model stub only.
- No complete proof-assistant formalization.
- No compiler correctness or full EML semantics claim.
- No Forge/compiler behavior change.
