---
layout: ../../layouts/Base.astro
title: "The Third Proof-Carrying Rescue"
description: "Forge now has a precision-escape packet for a finite phantom-attractor trace: low-precision stalling, higher-precision sensitivity, escape to an interior event, and a MachLib precision obligation."
date: "2026-05-26"
author: "Monogate Research"
tag: "research"
featured: true
---

# The Third Proof-Carrying Rescue

The first two proof-carrying rescues handled clean safety boundaries:

```text
domain_wall -> log_domain_rescue
overflow_wall -> guard_rescue
```

The third one is stranger:

```text
phantom_attractor -> precision_escape -> interior_sample
```

A phantom attractor is not a crash. The trace remains finite. That is what makes
it dangerous: the optimizer can appear stalled in a numerically plausible basin
even though higher-precision replay exposes a way out.

## The Function Family

The fixture is deliberately small:

```text
quantized_basin(x) = (x - 0.375)^2
```

The function is not exotic. The phantom comes from the optimizer trace. With a
coarse finite-difference grid, nearby probes collapse onto the same quantized
coordinate, so the low-precision gradient reads as zero.

Higher-precision replay sees the slope.

## The Trace

Forge emits the packet with:

```text
tools/precision_escape_rescue.py
```

It records:

```text
examples/precision_escape_rescue.eml
```

The generated report shows finite stalled points that escape under precision
replay:

| x | low-precision gradient | high-precision gradient | escaped x | transition |
| ---: | ---: | ---: | ---: | --- |
| `0.25` | `0.0` | `-0.25` | `0.375` | `phantom_attractor -> interior_sample` |
| `0.5` | `0.0` | `0.25` | `0.375` | `phantom_attractor -> interior_sample` |
| `0.75` | `0.0` | `0.75` | `0.375` | `phantom_attractor -> interior_sample` |

This is the important distinction: the packet does not claim these points are
true local optima. It claims they are finite, low-precision-stalled,
precision-sensitive, and escapable.

## The Obligation

The packet points at:

```text
PrecisionSensitivityObligation
```

MachLib now has a packet bridge:

```text
ValidBoundaryRunPacket p
  -> PacketHasEvent p phantomAttractor
  -> PacketHasTransition p phantomAttractor interiorSample
  -> PrecisionSensitivityObligation p
     and a nonempty transition-graph witness
```

The explicit event premise matters. A transition packet is evidence, not yet a
semantic constructor for event membership. The theorem stays honest about that
boundary while still giving Forge a formal hook.

## Why This Matters

This is the first rescue that targets a deceptive finite state rather than an
obvious invalid domain or overflow wall.

That is where high-dimensional optimization gets subtle. The failure can look
like success. A proof-carrying optimizer needs to say, "this trace is finite,
but the finite evidence is suspicious."

The third rescue gives Monogate a first packet shape for that suspicion.
