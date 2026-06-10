# PUB-R1 E5 Deploy Authorization

Date: 2026-06-10
Artifact ID: `pub-r1-e5-deploy-authorization`
Status: `DEPLOY_AUTHORIZATION_RECORDED_PENDING_OPERATOR_PER_ACTION_CONFIRMATION`

## Authorizing party

Monogate operator (`almaguer1986@gmail.com`), attended.

## Authorizing message (verbatim)

> lets do all of it please

Sent in the same session that produced commits `4d7ba2f8 Add EH A9 readability
queue contract`, `61dfa739 Add EH A10 readability queue item selector`, and
`13e79c3a Add PUB R0 brake-side ledger generator`. The CLAUDE.md
broad-delegation rule (research repo commit `8c5236c`) was in effect.

## Scope

This authorization unlocks exactly:

1. The initial public deploy of `monogate.net/evidence-status/` as rendered by
   the PUB-R1 renderer from the PUB-R0 canonical JSON ledger.
2. Subsequent redeploys whose page bytes are derived from a current PUB-R0
   output **with no new content classes** (the five classes below are
   exhaustive).

Anything outside this scope — adding a content class, changing page scope,
deploying any other page, or deploying any other surface — requires a fresh
human-authored authorization artifact. The general no-public-deploy rail
stays up.

## Exhaustive content classes (per PUB-R1 r2 §2)

1. `held_lanes`
2. `retracted_claims`
3. `negative_results`
4. `standing_claim_rule`
5. `lean_status_line`

A sixth class added to the page invalidates this authorization.

## Bound page identity

- Page relative path: `evidence-status/index.html` in `monogate-net` repo.
- Live URL: `https://monogate.net/evidence-status/`.
- Page bytes SHA-256 (from PUB-R1 renderer, current ledger):
  `47d906bf6bd3657f44004a5591d7af18a21cd8d9406a692677a9c87dcb1eb097`.
- PUB-R0 source artifact: `pub-r0-brake-side-ledger-generator` (commit
  `13e79c3a` in monogate core).
- PUB-R1 source artifact: `pub-r1-public-surface-read-parity` (this
  monogate core commit).

## What this authorization does NOT do

- It does NOT itself execute the live deploy. The actual `git push` to the
  monogate-net remote is a separate per-action operator confirmation, which
  the agent must request explicitly (system-prompt-level rail on
  irreversible actions visible to others).
- It does NOT pre-authorize any other public surface, repo, or deploy
  target.
- It does NOT reopen any held lane.
- It does NOT promote the public math draft.
- It does NOT touch monogate-dev, monogate-electronics, or `/electronics`.
- It does NOT introduce JavaScript or any dynamic content; the page is
  static no-JS HTML.
- It does NOT claim ledger completeness, renderer correctness, runtime
  performance, compiler correctness, hardware readiness, silicon readiness,
  or broad EML advantage.

## Drift discipline

If a future PUB-R0 run changes the ledger (new retraction, new held lane,
updated Lean status), the PUB-R1 renderer must be re-run, the build-time
drift guard re-checked, the new page bytes committed to monogate-net, and
the post-deploy probe re-run after deploy. This authorization continues to
cover those byte-derived redeploys provided the five content classes remain
the same.

If the page bytes ever diverge from a fresh PUB-R1 render of the current
PUB-R0 ledger, the drift guard fails and the page must be either
re-rendered or rolled back; the authorization does not cover serving a
drifted page.
