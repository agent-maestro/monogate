---
layout: ../../layouts/Base.astro
title: "How to Read the Rescue Suite"
description: "A practical guide to the proof-carrying rescue suite manifest: what the packets mean, what they prove, and what they deliberately do not claim."
date: "2026-05-26"
author: "Monogate Research"
tag: "research"
featured: false
---

# How to Read the Rescue Suite

The proof-carrying rescue suite is a replayable evidence artifact. It is not a
marketing diagram and not a finished optimizer release.

The Forge manifest lives at:

```text
reports/proof_carrying_rescue_suite_v0_2026_05_26.json
```

The human-facing Explorer lives at:

```text
https://monogate.dev/explorer/rescue-suite
```

It can be replayed with:

```text
forge rescue --suite --strict
```

That emits the manifest, the replay result, the markdown summary, and the
generated fixture consumed by the Explorer.

## What the Manifest Says

The manifest says four boundary-event rescue lanes exist and each has a
transition witness:

| Lane | Meaning |
| --- | --- |
| `domain_wall -> log_domain_rescue` | positive-coordinate rescue |
| `overflow_wall -> guard_rescue` | output-safety rescue |
| `phantom_attractor -> interior_sample` | precision-sensitivity escape |
| `saturation_shelf -> corner_concentration` | clamp-shelf deshelf replay |

Each lane points at a MachLib obligation name. That lets Forge, MachLib, and the
public research notes use the same event language.

## What the Replay Checks

The replay validator checks:

- all four lanes exist
- every lane has the expected transition
- every lane names the expected MachLib obligation
- embedded packets agree with the lane summaries
- every lane has a transition witness
- conservative boundary flags remain false

Those false flags matter. The suite does not claim:

- semantic rewrites
- optimizer release behavior
- hardware observation
- completed formal proofs

## What MachLib Adds

MachLib has lane-level bridge theorems and now a suite-level structural theorem.
At the current abstraction level, the theorem says:

```text
four valid lane witnesses
  -> all four obligation witnesses
```

That is not the final semantic proof of every rescue. It is the formal hook that
turns the manifest from a table into a replay object MachLib can talk about.

## Why v0 Matters

v0 is the first time the Monogate stack has a complete loop:

```text
source fixture
  -> boundary event
  -> rescue operator
  -> packet witness
  -> replay validator
  -> MachLib obligation bridge
  -> public research page
```

The next surface should be an Explorer/dashboard view over this exact manifest.
That surface is now live; the broader frontier map is at
[`/research/frontier`](/research/frontier).
