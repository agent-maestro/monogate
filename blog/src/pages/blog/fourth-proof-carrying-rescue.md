---
layout: ../../layouts/Base.astro
title: "The Fourth Proof-Carrying Rescue"
description: "Forge now has a saturation-deshelf packet: finite clamp-shelf collapse, pre-clamp pressure replay, boundary-structure recovery, and a MachLib clamp-invariant obligation."
date: "2026-05-26"
author: "Monogate Research"
tag: "research"
featured: true
---

# The Fourth Proof-Carrying Rescue

The fourth v0 rescue lane is:

```text
saturation_shelf -> saturation_deshelf -> corner_concentration
```

This one is different from the first three. It does not move directly into an
interior-good event. It moves from a bad finite flatline back into measurable
boundary structure.

## The Function Family

The fixture is:

```text
saturated_response(x) = clamp(exp(x), 0, 1)
```

Large positive inputs are finite and bounded, but they collapse onto the same
output:

```text
output = 1
```

That is a saturation shelf. It is safe-looking, but it destroys optimizer
information.

## The Trace

Forge emits the packet with:

```text
tools/saturation_deshelf_rescue.py
```

It records:

```text
examples/saturation_deshelf_rescue.eml
```

The deshelf replay inspects pre-clamp pressure. High-pressure shelf samples move
back into boundary structure:

| x | raw value | raw event | pre-clamp pressure | deshelf event |
| ---: | ---: | --- | ---: | --- |
| `2.0` | `1.0` | `saturation_shelf` | `2.1269280110` | `saturation_shelf` |
| `4.0` | `1.0` | `saturation_shelf` | `4.0181499279` | `corner_concentration` |
| `8.0` | `1.0` | `saturation_shelf` | `8.0003354064` | `corner_concentration` |

The packet is intentionally modest. It does not claim a global optimizer win.
It claims the clamp invariant stayed intact while replay recovered measurable
boundary pressure.

## The Obligation

The packet points at:

```text
ClampInvariantObligation
```

MachLib now has the matching bridge:

```text
ValidBoundaryRunPacket p
  -> PacketHasEvent p saturationShelf
  -> PacketHasTransition p saturationShelf cornerConcentration
  -> ClampInvariantObligation p
     and a nonempty transition-graph witness
```

That completes the v0 proof-carrying rescue suite.
