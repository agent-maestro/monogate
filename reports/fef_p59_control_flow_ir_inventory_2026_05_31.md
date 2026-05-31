# FEF-P59 Control-Flow IR Inventory

Date: 2026-05-31

Status: `FEF_P59_CONTROL_FLOW_IR_INVENTORY_PASS`

Decision: `control_flow_ir_inventory_recorded_general_support_blocked`

FEF-P59 maps the gap between selected branch closures and real branch/control-flow support.

## Summary

- Source packets: `3`
- Selected branch closures: `5`
- P51 selected blockers remaining: `0`
- Candidate IR nodes: `10`
- Selected closure mappings: `5`
- Unsupported forms: `6`
- Open semantic obligations: `6`
- Control-flow IR implemented: `False`

## Candidate IR Nodes

| Node | Category | Purpose | Required |
|---|---|---|---:|
| `cfg_entry` | `structure` | single entry point for a lifted function body | `True` |
| `cfg_exit` | `structure` | single normalized exit for return-value comparison and source roundtrip | `True` |
| `basic_block` | `structure` | ordered side-effect-aware statement container | `True` |
| `condition_expr` | `predicate` | typed boolean expression with explicit numeric comparison semantics | `True` |
| `branch` | `control` | conditional edge from one block to true/false successors | `True` |
| `merge` | `control` | join point for branch outcomes, fallthrough, and else-if chains | `True` |
| `return_value` | `control` | explicit return edge and returned expression | `True` |
| `assignment` | `state` | mutable local update needed before general branches or loops | `True` |
| `phi_or_select` | `state` | merged scalar value after branch alternatives | `True` |
| `unsupported_construct` | `boundary` | fail-closed marker for loops, effects, calls, memory, labels, and unsupported branch forms | `True` |

## Selected Closure Mappings

| Case | Source | Feature | Current Lowering | Candidate IR Path |
|---|---|---|---|---|
| `c_ternary_select_v0` | `c` | `ternary_select` | `guarded_affine_selector_step01` | `condition_expr, phi_or_select, return_value` |
| `c_if_early_return_relu_v0` | `c` | `if_early_return` | `guarded_affine_selector_step01` | `cfg_entry, condition_expr, branch, return_value, cfg_exit` |
| `c_if_else_clamp_v0` | `c` | `if_else_clamp` | `nested_guarded_affine_selector_step01` | `condition_expr, branch, merge, phi_or_select, return_value` |
| `rust_if_expr_relu_v0` | `rust` | `if_expression` | `guarded_affine_selector_step01` | `condition_expr, phi_or_select, return_value` |
| `rust_if_return_clamp_v0` | `rust` | `if_return_clamp` | `nested_guarded_affine_selector_step01` | `cfg_entry, condition_expr, branch, return_value, merge, cfg_exit` |

## Unsupported Forms

| Unsupported Form | Status | Reason | Next Validator |
|---|---|---|---|
| `nested_statement_branches` | `blocked` | selected closures do not cover arbitrary nested statement bodies | `nested_branch_fixture_matrix` |
| `boolean_compound_conditions` | `blocked` | selected closures do not cover short-circuit and/or condition semantics | `compound_condition_semantics_gate` |
| `mutable_assignments_across_branches` | `blocked` | selected closures are scalar return-only or expression-valued cases | `assignment_phi_fixture_gate` |
| `loops_and_back_edges` | `blocked` | candidate IR needs loop headers, latches, variants, and boundedness policy | `loop_construct_blocker_gate` |
| `side_effecting_calls_or_memory` | `blocked` | current selected branch evidence is side-effect free | `side_effect_boundary_inventory` |
| `source_preserving_roundtrip` | `blocked` | generated-target re-ingest exists, but non-generated source-preserving branch roundtrip does not | `non_generated_branch_roundtrip_gate` |

## Semantic Obligations

- `condition_truth_semantics`: C/Rust comparison and boolean semantics must be explicit before branch equivalence claims. (open)
- `dominance_and_merge_preservation`: Each selected value must come from a dominating definition or explicit phi/select merge. (open)
- `return_and_fallthrough_preservation`: Early returns and fallthrough returns must normalize to equivalent exit behavior. (open)
- `assignment_order_preservation`: Mutable updates must preserve statement order and branch-local state. (open)
- `unsupported_construct_fail_closed`: Loops, labels, effects, calls, and memory must fail closed until separately validated. (open)
- `source_ast_roundtrip_boundary`: Non-generated source branches need a source AST boundary before full roundtrip claims. (open)

## Boundary

- Inventory only; no new IR implementation.
- No general branch/control-flow support claim.
- No branch re-ingest, full source roundtrip, arbitrary source-family, compiler-correctness, formal-equivalence, or runtime-performance claim.
