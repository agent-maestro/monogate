---
layout: ../../layouts/Base.astro
title: "Proof-Carrying Rescue Status"
description: "A compact status table for Monogate's boundary rescue operators: Forge evidence, MachLib bridge status, and publication state."
date: "2026-05-26"
author: "Monogate Research"
tag: "research"
featured: false
---

# Proof-Carrying Rescue Status

Monogate's high-dimensional optimizer work is organized around named boundary
events and named rescue operators. This is the current status table.

| Boundary event | Rescue operator | Rescue event | Forge evidence | MachLib bridge | Public note |
| --- | --- | --- | --- | --- | --- |
| `domain_wall` | `log_domain_lift` | `log_domain_rescue` | packet + tests | closed packet bridge | [first rescue](/blog/first-proof-carrying-rescue) |
| `overflow_wall` | `guard_clamp` | `guard_rescue` | packet + tests | closed packet bridge | [second rescue](/blog/second-proof-carrying-rescue) |
| `phantom_attractor` | `precision_escape` | `interior_sample` | packet + tests | closed packet bridge with explicit event witness | [third rescue](/blog/third-proof-carrying-rescue) |
| `saturation_shelf` | `saturation_deshelf` | `corner_concentration` | intervention benchmark only | pair obligation bridge | next target |

## Reading The Table

`packet + tests` means Forge has a dedicated source fixture, trace tool,
generated report, and regression tests.

`closed packet bridge` means MachLib has a theorem connecting a valid packet
transition to its obligation and a nonempty transition-graph witness, without
adding a new `sorry`.

`closed packet bridge with explicit event witness` means the bridge is closed,
but the theorem requires both the event witness and transition witness. That is
the current honest shape for phantom-attractor evidence.

`pair obligation bridge` means the named intervention is present in the broader
paired benchmark and MachLib obligation map, but it does not yet have the
narrow source-fixture packet that the first three rescues have.

## Next Frontier

The next target is:

```text
saturation_shelf -> saturation_deshelf -> corner_concentration
```

That one should show a finite output collapsed onto a clamp shelf, then a
deshelf replay that restores measurable boundary structure without claiming a
global optimizer win.
