# FEF-P61 Unsupported Construct Blocker Gate

Date: 2026-05-31

Status: `FEF_P61_UNSUPPORTED_CONSTRUCT_BLOCKER_GATE_PASS`

Decision: `unsupported_construct_blocker_gate_recorded_support_blocked`

FEF-P61 makes the P60 control-flow IR schema fail closed for unsupported constructs.

## Summary

- P60 schema id: `monogate.control_flow_ir.v0`
- P60 selected IR fragments: `5`
- Unsupported construct probes: `6`
- P59 unsupported forms: `6`
- All P59 unsupported forms covered: `True`
- All P60 schema unsupported forms covered: `True`
- All unsupported probes blocked: `True`
- Schema fragments validate: `True`
- Unsupported constructs supported: `False`
- Control-flow IR implemented: `False`
- Frontend lowering changed: `False`

## Blocked Probes

| Construct | Source | Category | Status | Next Validator |
|---|---|---|---|---|
| `nested_statement_branches` | `c` | `grammar_breadth` | `blocked_fail_closed` | `nested_branch_fixture_matrix` |
| `boolean_compound_conditions` | `rust` | `condition_semantics` | `blocked_fail_closed` | `compound_condition_semantics_gate` |
| `mutable_assignments_across_branches` | `c` | `state_and_merge` | `blocked_fail_closed` | `assignment_phi_fixture_gate` |
| `loops_and_back_edges` | `rust` | `loops_and_back_edges` | `blocked_fail_closed` | `loop_construct_blocker_gate` |
| `side_effecting_calls_or_memory` | `c` | `effects_calls_memory` | `blocked_fail_closed` | `side_effect_boundary_inventory` |
| `source_preserving_roundtrip` | `rust` | `source_roundtrip_semantics` | `blocked_fail_closed` | `non_generated_branch_roundtrip_gate` |

## Boundary

- Blocker gate only; no unsupported construct implementation.
- No frontend lowering change.
- No general branch/control-flow support claim.
- No branch re-ingest, full source roundtrip, arbitrary source-family, compiler-correctness, formal-equivalence, or runtime-performance claim.
