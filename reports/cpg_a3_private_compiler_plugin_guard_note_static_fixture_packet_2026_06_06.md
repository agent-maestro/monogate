# CPG-A3 Private Compiler-Plugin Guard-Note Static Fixture Packet

Status: `CPG_A3_PRIVATE_COMPILER_PLUGIN_GUARD_NOTE_STATIC_FIXTURE_PACKET_PASS`

## Summary

- source artifact: `cpg-a2-private-compiler-plugin-guard-note-fixture-or-lint-contract-selector`
- accepted fixture count: `3`
- rejection fixture count: `3`
- fixture runner executed: `False`
- compiler plugin implemented: `False`
- runtime performance claim: `False`
- next recommended artifact: `CPG-A4 private compiler-plugin static fixture review or executable lint contract selector`

## Accepted Advisory Fixtures

- `accepted_advisory_expression_surface_detection`: `lint_warning` - Advisory detection only: candidate EML-shaped expression surface for human review.
- `accepted_guard_requirement_note`: `guard_checklist_item` - Guard reminder only: positive-domain guard such as 0 < x must be reviewed.
- `accepted_evidence_packet_link_hint`: `evidence_pointer` - Evidence pointer only: related private witness packet may exist.

## Rejection Fixtures

- `rejected_automatic_rewrite_or_lowering`: blocks `automatic_rewrite_or_lowering` - Automatic replacement/lowering would exceed advisory guard-note scope.
- `rejected_runtime_performance_claim`: blocks `runtime_benchmark_claim` - Static advisory hints do not establish runtime measurements or savings.
- `rejected_public_readiness_claim`: blocks `public_docs_or_copy` - Public/docs/package readiness requires separate explicit approval and release evidence.

## Reviewer Questions

- Are the accepted fixtures visibly advisory rather than executable behavior?
- Are the rejection fixtures strong enough to block automatic lowering and performance claims?
- Should CPG-A4 review these static fixtures before any executable lint contract is drafted?

## Non-Claims

- CPG-A3 records static advisory/rejection fixtures only; it does not implement or execute a compiler plugin, lint engine, or fixture runner.
- CPG-A3 fixtures are review examples, not executable tests and not proof obligations.
- CPG-A3 does not authorize automatic rewrites, lowering, replacement, code generation, runtime mutation, public docs, or package release.
- CPG-A3 does not claim compiler correctness, semantic preservation, automatic lowering safety, runtime performance, SDK stability, public readiness, or public package release readiness.
- CPG-A3 respects the D109 hold and does not start D110, consume reviewer response, or touch laptop-owned electronics repositories.
