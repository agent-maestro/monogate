# EML Visual IR Bridge Candidate

Classification: INTERNAL_DRAFT_CANDIDATE

## Candidate

The EML Visual IR Bridge is a candidate internal playbook for explaining how EML expressions move between:

- public-safe tree/cost views,
- internal IR/DAG prototype views,
- replay-style timelines,
- complex domain-coloring intuition.

## Evidence

- `explorer/src/components/EMLIRInspectorTab.jsx`
- `explorer/src/components/ComplexFieldTab.jsx`
- `explorer/src/components/LandingPage.jsx`
- `../1op/src/app/visual/domain-coloring/page.tsx`
- `../1op/src/components/games/domain-coloring.tsx`
- `../1op/src/lib/data/experiences.ts`

## Current Status

This is useful internally, but it is not a public playbook yet. The next gate is a stable IR lowering contract and public-copy review for the 1op visual lab.

## Non-Claims

This candidate does not claim safety certification, production control readiness, hardware-backed evidence, formal verification, PETAL upload, Hugging Face upload, package publication, or public theorem/proof/open-problem results.
