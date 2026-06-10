# PUB-R0 Canonical Brake-Side Ledger Generator

Status: `PUB_R0_BRAKE_SIDE_LEDGER_GENERATOR_PASS`

## Summary

- held lanes: `5`
- retracted claims: `8`
- negative results: `5`
- Lean theorems: `468`
- Lean sorries: `5`
- MachLib core sorries: `0`
- MachLib discovered sorries: `222`
- page rendered: `False`
- page published: `False`
- public surface updated: `False`

## Held Lanes

- `electronics-inbox`: held by `ee_bridge_a4_electronics_artifact_inbox_gate_feed`; pending_no_artifact
- `private-atlas-v0`: held by `atlas_a51_private_atlas_reviewer_response_hold_selector_feed`; held_pending_reviewer_response_or_explicit_redirect
- `product-roadmap`: held by `prod_a10_private_product_roadmap_pause_digest_feed`; paused_by_product_roadmap_pause_digest
- `public-math-review`: held by `eml_d109_private_reviewer_response_availability_guard_feed`; held_pending_actual_reviewer_response
- `training-cost-estimator`: held by `prod_a21_training_cost_estimator_skeleton_hold_digest_feed`; held_by_prod_a21

## Retracted Claims

- `claim:C259_cross_genome_3` @ `exploration/C259_cross_genome/FINDINGS.md:93`: ## Falsifiability — what would have killed the claim
- `claim:E196_algorithmic_corpus_5` @ `exploration/E196_algorithmic_corpus/FINDINGS.md:116`: prediction in the session prompt is rejected. Real-world
- `claim:E196_algorithmic_corpus_16` @ `exploration/E196_algorithmic_corpus/FINDINGS.md:224`: **Verdict: REJECTED.** Median `max_path_r` is 1.0 for BOTH groups.
- `claim:Frontier_A_resolution_096_097_2026_05_11_1` @ `exploration/Frontier_A_resolution_096_097_2026_05_11/FINDINGS.md:70`: guess to 2×10⁻⁵ /t is **RETRACTED.**
- `claim:Frontier_A_sigma099_T1e6_2026_05_10_1` @ `exploration/Frontier_A_sigma099_T1e6_2026_05_10/FINDINGS.md:10`: (PARTIAL_OBSERVATIONS only — killed to free CPU for this run).
- `claim:Frontier_A_sigma099_T1e6_2026_05_10_4` @ `exploration/Frontier_A_sigma099_T1e6_2026_05_10/FINDINGS.md:43`: killed T=10⁵ probe earlier today.
- `claim:Frontier_D_hd_vs_chain_2026_05_10_1` @ `exploration/Frontier_D_hd_vs_chain_2026_05_10/FINDINGS.md:99`: spectrum) is **rejected at this resolution and corpus size**. The
- `claim:alpha-6.214-recheck-2026-04-27_2` @ `exploration/alpha-6.214-recheck-2026-04-27/FINDINGS.md:5`: **Status:** REJECTED-IN-CURRENT-SETUP (the value does not appear at any

## Negative Results

- `claim:E193_numerical_stability_1` @ `exploration/E193_numerical_stability/FINDINGS.md:5`: **Outcome.** Partial signal (good case). Tool prototype NOT shipped.
- `claim:E193_numerical_stability_3` @ `exploration/E193_numerical_stability/FINDINGS.md:108`: negative, **two-sided p = 0.69 (not significant)**.
- `claim:E193_numerical_stability_4` @ `exploration/E193_numerical_stability/FINDINGS.md:162`: (NOT significant at alpha=0.05). Sample size at c=-1 is small (n=19).
- `claim:E199_superbest_stability_2` @ `exploration/E199_superbest_stability/FINDINGS.md:11`: tested. **30% accuracy is below the 70% threshold for a generic
- `claim:cat_vision_2` @ `exploration/cat_vision/FINDINGS.md:56`: intensity. Below human cone threshold; only rod-driven luminance

## Standing Claim Rule (verbatim)

> No training-cost estimate, training-savings, estimator-accuracy, runtime performance, compiler-correctness, SDK-stability, hardware-readiness, silicon-readiness, catalog-completeness, or broad EML-advantage claim unless a bounded artifact proves that exact claim.

## Lean Status (from builder_v2.py summary)

- Lean theorems: 468
- Lean sorries: 5
- MachLib core sorries: 0
- MachLib discovered sorries: 222

## Guardrails

- canonical JSON only; no HTML render, no deploy, no public surface
- all ledger fields byte-derived from canonical sources
- ledger completeness is not claimed; source drift surfaces as ledger drift
- no laptop-owned repo touch

## Non-Claims

- PUB-R0 generates one canonical JSON ledger; it does not render markdown or HTML, publish, deploy, or update any public surface.
- PUB-R0 does not implement PUB-R1, the drift guard, the post-deploy probe, or the deploy authorization artifact.
- PUB-R0 does not claim ledger completeness; it enumerates the brake-side rows currently visible in canonical state (graph.json status, EH-A7 lane states, WELCOME.md standing rule, builder_v2.py summary Lean line). Sources that drift will surface as ledger drift, not as silent omission.
- PUB-R0 does not reopen training-cost, Atlas, public-math, product-roadmap, or electronics lanes; it merely records that they are held.
- PUB-R0 does not publish, approve public copy, update public/dev surfaces, create SDK/course material, consume reviewer response, record reviewer approval, start D110, edit MachLib, run Lean type-checking against MachLib, change runtime lowering, or touch laptop-owned repositories.
- PUB-R0 does not claim estimator accuracy, training savings, runtime performance, compiler correctness, hardware readiness, silicon readiness, public readiness, catalog completeness, or broad EML advantage.
