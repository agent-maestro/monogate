# CPG-A5 Private Executable Lint Contract Boundary Packet

Status: `CPG_A5_PRIVATE_EXECUTABLE_LINT_CONTRACT_BOUNDARY_PACKET_PASS`

## Summary

- source artifact: `cpg-a4-private-compiler-plugin-static-fixture-review-or-lint-contract-selector`
- input field count: `4`
- output field count: `4`
- rejection obligation count: `4`
- execution gate count: `4`
- executable lint contract created: `False`
- lint engine implemented: `False`
- next recommended artifact: `CPG-A6 private lint contract boundary review or static test selector`

## Contract Input Shape

- `source_snippet`: short source expression or statement under advisory review Boundary: the snippet is not compiled, rewritten, or executed by this packet
- `expression_family`: bounded family label such as expm1_boundary or positive_log_exp_guard Boundary: family labels are hints, not completeness or theorem-discovery claims
- `evidence_pointer`: optional private witness/evidence packet id when one is known Boundary: a pointer does not establish applicability to the snippet
- `guard_context`: explicit domain or guard notes supplied by the reviewer or caller Boundary: the contract may report missing guards but does not prove guards

## Contract Output Shape

- `advisory_notice`: human-readable lint/profile/review note Blocked: automatic rewrite, replacement, or lowering instruction
- `guard_checklist_item`: explicit guard reminder tied to a bounded evidence pointer Blocked: claim that the guard is satisfied or mechanically proven
- `evidence_pointer`: private packet id, witness id, or report path for reviewer follow-up Blocked: public readiness, library completeness, or SDK stability statement
- `blocked_claim_notice`: notice that a requested compiler/performance/public claim is out of scope Blocked: soft approval wording for the blocked claim

## Rejection Obligations

- `reject_automatic_rewrite_or_lowering`: reject automatic_rewrite, automatic_lowering, replacement_patch. Reason: The advisory lane has no semantic-preservation or lowering-safety proof.
- `reject_runtime_or_training_savings_claim`: reject runtime_speedup, training_savings, benchmark_win. Reason: The contract boundary records no measurement protocol or benchmark execution.
- `reject_public_or_package_readiness_claim`: reject public_docs_ready, package_release_ready, sdk_stable. Reason: Public copy, package release, and SDK stability require separate approval.
- `reject_guard_proven_or_theorem_discovered_claim`: reject guard_proven, new_theorem_discovered, applicability_proven. Reason: A lint contract may surface guard notes but cannot prove guards or discover theorems.

## Execution Gates

- `contract_boundary_review_required`: `required_before_static_tests` - The boundary packet must be reviewed before static executable-contract tests are drafted.
- `static_test_fixtures_required`: `required_before_implementation` - Executable behavior must be checked against accepted and rejection examples before implementation.
- `implementation_hold_gate_required`: `required_before_any_lint_engine` - A separate hold gate must explicitly approve implementation scope.
- `public_docs_gate_required`: `required_before_public_copy` - Public docs or package wording requires separate approval and readiness evidence.

## Non-Claims

- CPG-A5 is a private boundary packet for a possible executable lint contract; it is not the executable contract.
- CPG-A5 records input, output, rejection, and execution-gate obligations only.
- CPG-A5 does not implement or execute a compiler plugin, lint engine, lint contract, fixture runner, rewrite engine, code generator, or runtime lowering path.
- CPG-A5 does not claim compiler correctness, semantic preservation, automatic lowering safety, runtime performance, SDK stability, public readiness, or public package release readiness.
- CPG-A5 respects the D109 hold and does not start D110, consume reviewer response, or touch laptop-owned electronics repositories.
