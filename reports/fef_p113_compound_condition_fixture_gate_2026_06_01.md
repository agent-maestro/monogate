# FEF-P113 Compound-Condition Fixture Gate

Date: 2026-06-01

Status: `FEF_P113_COMPOUND_CONDITION_FIXTURE_GATE_PASS`

Decision: `compound_condition_fixture_gate_recorded_support_blocked_review_hold_preserved`

FEF-P113 records selected compound-condition fixtures while keeping support blocked.

## Summary

- Fixture count: `4`
- C fixtures: `2`
- Rust fixtures: `2`
- Operator kinds: `and, or`
- Total atomic predicates: `9`
- Fixtures with short-circuit semantics: `4`
- Runtime execution performed: `False`
- Lowering implemented: `False`
- Policies implemented: `False`
- P112 reviewer decision recorded: `False`

## Fixtures

| Fixture | Language | Shape | Operators | Status |
|---|---|---|---|---|
| `c_and_guard_return_v0` | `c` | `compound_and_guard_return` | `and` | `blocked_fixture_defined` |
| `c_or_clamp_guard_v0` | `c` | `compound_or_clamp_guard` | `or` | `blocked_fixture_defined` |
| `rust_and_if_expr_v0` | `rust` | `compound_and_if_expression` | `and` | `blocked_fixture_defined` |
| `rust_mixed_and_or_return_v0` | `rust` | `compound_mixed_and_or_return` | `and, or` | `blocked_fixture_defined` |

## Boundary

- Fixture gate only.
- No runtime execution or lowering.
- No short-circuit or boolean-normalization policy.
- No compound-condition support claim.
- No compiler-correctness, formal-equivalence, or runtime-performance claim.
