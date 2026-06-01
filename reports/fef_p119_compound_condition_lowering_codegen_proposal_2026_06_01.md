# FEF-P119 Compound-Condition Lowering Codegen Proposal

Date: 2026-06-01

Status: `FEF_P119_COMPOUND_CONDITION_LOWERING_CODEGEN_PROPOSAL_PASS`

Decision: `selected_compound_condition_lowering_codegen_proposal_recorded_not_applied`

FEF-P119 records a selected compound-condition lowering/codegen proposal without applying it.

## Summary

- Selected fixture: `c_and_guard_return_v0`
- Proposal id: `selected_and_guard_return_lowering_codegen_proposal_v0`
- Proposal status: `proposal_recorded_not_applied`
- Pipeline hooks: `4`
- Approval gates: `6`
- Rollback criteria: `5`
- Review checks passing: `12` / `12`
- P118 generated-target gate status: `blocked_not_run`
- Proposal applied: `False`
- Implementation diff produced: `False`
- Generated fixture text produced: `False`
- Generated target executed: `False`
- Re-ingested target executed: `False`

## Intended Pipeline Hooks

| Hook | Target surface |
|---|---|
| `recognize_selected_and_guard_return` | `eFrog selected compound-condition source recognizer` |
| `emit_source_ordered_predicate_temps` | `Forge selected compound-condition normalization` |
| `emit_selected_return_phi_or_select` | `Forge selected C generated-target fixture text` |
| `require_p117_p118_evidence_before_run` | `generated target runtime gate` |

## Review Checks

| Check | Status |
|---|---|
| `proposal_scope_selected_fixture_only` | `pass` |
| `p118_gate_blocked_not_run` | `pass` |
| `p118_required_before_run_count_is_five` | `pass` |
| `p117_inherited_rows_pass` | `pass` |
| `p117_inherited_exact_agreement` | `pass` |
| `p117_inherited_short_circuit_counts` | `pass` |
| `proposal_not_applied` | `pass` |
| `implementation_diff_not_produced` | `pass` |
| `generated_fixture_text_not_produced` | `pass` |
| `generated_target_not_executed` | `pass` |
| `reingested_target_not_executed` | `pass` |
| `not_installed_in_forge_or_efrog` | `pass` |

## Boundary

- Proposal only; not applied.
- No source diff, generated fixture text, generated execution, or re-ingest execution.
- No compound-condition lowering/codegen implementation.
- No compound-condition support claim.
- No compiler-correctness, formal-equivalence, or runtime-performance claim.
