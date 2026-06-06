# CPG-A1 Private Compiler-Plugin Guard-Note Packet

Status: `CPG_A1_PRIVATE_COMPILER_PLUGIN_GUARD_NOTE_PACKET_PASS`

## Summary

- source artifact: `prod-a7-private-product-roadmap-return-selector`
- selected lane: `eml_compiler_plugin`
- advisory capability count: `5`
- blocked compiler claim count: `8`
- compiler plugin implemented: `False`
- compiler correctness claim: `False`
- runtime performance claim: `False`
- next recommended artifact: `CPG-A2 private compiler-plugin guard-note fixture packet or executable lint contract selector`

## Advisory Capabilities

- `expression_surface_detection`: may do: Detect candidate EML-shaped expressions or elementary-function surfaces for human review. must say: Advisory detection only; no completeness, correctness, or target-readiness claim.
- `static_cost_profile_hint`: may do: Record static cost/profile hints when local metadata is available. must say: Static hint only; no measured runtime, savings, or performance claim.
- `rewrite_opportunity_hint`: may do: Suggest that a reviewer inspect a candidate rewrite or guard-bearing identity. must say: Review suggestion only; no automatic rewrite or semantic-preservation claim.
- `guard_requirement_note`: may do: Surface domain, guard, and blocked-claim obligations next to a candidate expression. must say: Guard reminder only; no proof or proof-carrying artifact claim.
- `evidence_packet_link_hint`: may do: Link a candidate expression to existing private evidence packets or checked witnesses when present. must say: Evidence pointer only; no completeness, public readiness, or library coverage claim.

## Blocked Compiler Claims

- `compiler_correctness`: The plugin or EML compiler is correct. Reason: CPG-A1 contains no compiler implementation, proof, or end-to-end compiler validation.
- `semantic_preservation`: Suggested rewrites preserve program semantics. Reason: Guard notes and rewrite hints are advisory and require separate checked evidence.
- `automatic_lowering_safety`: Automatic lowering or replacement is safe. Reason: CPG-A1 authorizes no automatic lowering, replacement, or runtime mutation.
- `runtime_performance`: The plugin improves runtime, training cost, or performance. Reason: Static hints are not runtime measurements and do not establish savings.
- `code_generation_correctness`: Generated code is correct. Reason: CPG-A1 defines no code-generation path.
- `all_target_readiness`: The plugin is ready across Python, Lean, hardware, or other targets. Reason: Target readiness must be shown by target-specific evidence.
- `public_package_release_readiness`: The plugin is public/package-ready. Reason: This artifact is private-first and contains no release validation.
- `broad_eml_advantage`: EML is broadly advantaged over ordinary implementations. Reason: One guard-note packet cannot establish broad comparative advantage.

## Allowed Outputs

- `lint_warning`: A private advisory warning for reviewer attention.
- `review_note`: A short private note explaining why the expression may need review.
- `cost_profile_hint`: A static hint, clearly marked as non-runtime evidence.
- `guard_checklist_item`: A reminder that domain conditions or guards must be reviewed.
- `evidence_pointer`: A link or id for an existing private evidence packet or witness.

## Blocked Outputs

- `generated_code_replacement`: Any emitted replacement code presented as safe.
- `automatic_rewrite_or_lowering`: Any automatic program rewrite/lowering action.
- `proof_certificate`: Any proof or checked certificate claim created by the plugin.
- `runtime_benchmark_claim`: Any runtime, training-cost, or performance measurement claim.
- `public_docs_or_copy`: Any public-facing product or documentation claim.

## Reviewer Questions

- Which expression surfaces should produce advisory-only lint notes?
- Which guard fields must exist before the plugin can suggest a rewrite review?
- Which wording prevents users from reading advisory hints as compiler, proof, or performance claims?
- Which existing evidence packet ids should be allowed as private evidence pointers?

## Non-Claims

- CPG-A1 is a private guard-note packet only; it does not implement or execute a compiler plugin.
- CPG-A1 records advisory lint/profile/guard-note boundaries only.
- CPG-A1 does not claim compiler correctness, semantic preservation, automatic lowering safety, code generation correctness, runtime lowering safety, runtime performance, SDK stability, public readiness, or public package release readiness.
- CPG-A1 does not claim training savings, estimator accuracy, scientific correctness, hardware readiness, silicon readiness, IP license readiness, accelerator-card readiness, reviewer approval, or broad EML advantage.
- CPG-A1 respects the D109 hold and does not start D110, consume reviewer response, or touch laptop-owned electronics repositories.
