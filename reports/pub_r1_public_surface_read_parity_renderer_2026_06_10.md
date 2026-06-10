# PUB-R1 Public-Surface Read Parity Renderer

Status: `PUB_R1_PUBLIC_SURFACE_READ_PARITY_PASS`

## Summary

- PUB-R0 source: `pub-r0-brake-side-ledger-generator`
- page relative path: `evidence-status/index.html`
- live URL: `https://monogate.net/evidence-status/`
- content classes: `5`
- expected HTML SHA-256: `9e27aeaaafa0…`
- expected HTML bytes: `8942`
- build-time drift: `False`
- live deploy executed: `False`
- post-deploy probe passed: `False`
- public surface updated: `False`

## Content Classes (exhaustive per r2 §2)

- `held_lanes`
- `retracted_claims`
- `negative_results`
- `standing_claim_rule`
- `lean_status_line`

## Guardrails

- static no-JS HTML, byte-derived from PUB-R0 canonical JSON
- build-time drift guard: sha256 of rendered HTML matches committed page bytes
- post-deploy probe: fetch live URL, sha256 compare; not run by this artifact
- no live deploy without E5 authorization + explicit per-action operator confirmation
- no sixth content class; no adjectives; no prose beyond canonical one-liners
- no held-lane reopen; no laptop-owned repo touch

## Non-Claims

- PUB-R1 renders a static no-JS HTML page from the PUB-R0 canonical JSON ledger and implements a two-stage drift guard; it does not execute a live public deploy.
- PUB-R1 does not push to monogate-net's remote; the operator's per-action deploy confirmation is a separate step recorded in the E5 authorization artifact.
- PUB-R1 does not add a sixth content class, add adjectives, add prose beyond the canonical one-liners, or paraphrase any ledger text — every sentence on the page is either a quote of the standing rule, a ledger fact with artifact ID, or navigation.
- PUB-R1 does not introduce JavaScript or any dynamic content; the page must be fully readable to a no-JS reader.
- PUB-R1 does not reopen training-cost, Atlas, public-math, product-roadmap, or electronics lanes; it merely displays that they are held.
- PUB-R1 does not edit MachLib, run Lean type-check, change runtime lowering, touch laptop-owned repos, approve public copy beyond this page, or claim ledger completeness, renderer correctness, runtime performance, compiler correctness, hardware readiness, silicon readiness, or broad EML advantage.
