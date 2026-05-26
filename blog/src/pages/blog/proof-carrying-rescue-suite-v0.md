---
layout: ../../layouts/Base.astro
title: "Proof-Carrying Rescue Suite v0"
description: "The Monogate boundary-event rescue suite now has four packet-backed lanes and a unified Forge manifest."
date: "2026-05-26"
author: "Monogate Research"
tag: "research"
featured: true
---

# Proof-Carrying Rescue Suite v0

The v0 rescue suite is complete.

Forge now emits one manifest for all four proof-carrying rescue lanes:

```text
tools/proof_carrying_rescue_suite.py
```

Forge also replays that manifest with:

```text
tools/proof_carrying_rescue_replay.py
```

The manifest is:

```text
reports/proof_carrying_rescue_suite_v0_2026_05_26.json
reports/proof_carrying_rescue_suite_v0_2026_05_26.md
```

## The Four Lanes

| Boundary event | Rescue operator | Rescue event | Obligation |
| --- | --- | --- | --- |
| `domain_wall` | `log_domain_lift` | `log_domain_rescue` | `PositiveCoordinateObligation` |
| `overflow_wall` | `guard_clamp` | `guard_rescue` | `OutputSafetyObligation` |
| `phantom_attractor` | `precision_escape` | `interior_sample` | `PrecisionSensitivityObligation` |
| `saturation_shelf` | `saturation_deshelf` | `corner_concentration` | `ClampInvariantObligation` |

Each lane has:

- a Forge EML source fixture
- a trace-emitting tool
- a generated JSON/Markdown report
- tests
- a MachLib packet bridge
- a public research note

## What v0 Means

v0 does not mean the optimizer is production-rewriting programs through these
rescues. It means Monogate now has a complete evidence vocabulary for the first
four boundary events:

```text
raw boundary event
  -> named rescue operator
  -> packet witness
  -> MachLib obligation bridge
```

The next phase is unification: use the manifest as the stable artifact for
Explorer, dashboards, future electronics courseware, and deeper MachLib proofs.

For the practical contract, see
[`How to Read the Rescue Suite`](/blog/how-to-read-the-rescue-suite).
