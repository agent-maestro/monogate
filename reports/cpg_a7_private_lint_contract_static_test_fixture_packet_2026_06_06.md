# CPG-A7 Private Lint Contract Static Test Fixture Packet

Status: `CPG_A7_PRIVATE_LINT_CONTRACT_STATIC_TEST_FIXTURE_PACKET_PASS`

## Summary

- source artifact: `cpg-a6-private-lint-contract-boundary-review-or-static-test-selector`
- accepted static fixture count: `4`
- rejection static fixture count: `4`
- static fixture count: `8`
- static tests created: `False`
- static tests executed: `False`
- next recommended artifact: `CPG-A8 private lint contract static fixture review or implementation hold selector`

## Accepted Static Fixtures

- `accepted_boundary_advisory_notice`: `advisory_notice` - human review note only; no rewrite or lowering instruction
- `accepted_positive_guard_checklist_item`: `guard_checklist_item` - guard reminder only; no claim that the guard is proven
- `accepted_private_evidence_pointer`: `evidence_pointer` - pointer for reviewer follow-up only; no public readiness claim
- `accepted_blocked_claim_notice`: `blocked_claim_notice` - explicitly block performance/public/compiler claims

## Rejection Static Fixtures

- `rejected_automatic_rewrite_output`: block `automatic_rewrite` - Automatic rewrite exceeds advisory lint-contract scope.
- `rejected_runtime_speedup_output`: block `runtime_speedup` - No benchmark protocol or runtime measurement is recorded.
- `rejected_public_package_ready_output`: block `package_release_ready` - Public/package readiness requires separate approval and evidence.
- `rejected_guard_proven_output`: block `guard_proven` - The lint-contract boundary may surface guard notes but cannot prove guards.

## Reviewer Questions

- Do the accepted static fixtures exercise every allowed output kind from CPG-A5?
- Do the rejection static fixtures cover the four rejection obligations from CPG-A5?
- Should CPG-A8 review these fixture shapes before any executable static tests are drafted?

## Non-Claims

- CPG-A7 records static fixture shapes only; it does not create or execute executable static tests.
- CPG-A7 fixtures are private review examples, not a lint engine, compiler plugin, or proof obligation.
- CPG-A7 does not implement or execute a compiler plugin, lint engine, lint contract, fixture runner, rewrite engine, code generator, or runtime lowering path.
- CPG-A7 does not claim compiler correctness, semantic preservation, automatic lowering safety, runtime performance, SDK stability, public readiness, or public package release readiness.
- CPG-A7 respects the D109 hold and does not start D110, consume reviewer response, or touch laptop-owned electronics repositories.
