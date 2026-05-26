---
layout: ../../layouts/Base.astro
title: "The Second Proof-Carrying Rescue"
description: "Forge now has a guard-clamp overflow rescue packet: raw overflow-wall failure, bounded guarded evaluation, guard-rescue transition, and MachLib output-safety obligation."
date: "2026-05-26"
author: "Monogate Research"
tag: "research"
featured: true
---

# The Second Proof-Carrying Rescue

The first proof-carrying rescue was the clean positivity case:

```text
domain_wall -> log_domain_lift -> log_domain_rescue
```

The second one is closer to embedded and hardware reality:

```text
overflow_wall -> guard_clamp -> guard_rescue
```

This is the rescue shape for functions that are mathematically valid but can
drive finite evaluators into overflow pressure.

## The Function Family

The fixture is:

```text
exp_pressure(x) = exp(x) + exp(x * x)
```

For large positive `x`, `exp(x * x)` overwhelms finite evaluation. The raw trace
therefore emits `overflow_wall`.

The rescue operator is `guard_clamp`: bound the internal evaluation coordinate
before evaluating the pressure path. In the current packet this is still
analysis-only evidence. It does not rewrite the user's public function
semantics.

## The Trace

Forge emits the packet with:

```text
tools/guard_clamp_rescue.py
```

It records the source fixture:

```text
examples/guard_clamp_rescue.eml
```

The central transition is:

```text
overflow_wall -> guard_rescue
```

The generated report shows the raw overflow samples recover under the guarded
coordinate:

| raw coordinate | raw event | guarded coordinate | guarded event |
| ---: | --- | ---: | --- |
| `30.0` | `overflow_wall` | `8.0` | `guard_rescue` |
| `710.0` | `overflow_wall` | `8.0` | `guard_rescue` |
| `800.0` | `overflow_wall` | `8.0` | `guard_rescue` |

The guarded trace stays finite and carries an output-safety direction.

## The Obligation

The packet points at:

```text
OutputSafetyObligation
```

MachLib now has the matching bridge:

```text
ValidBoundaryRunPacket p
  -> GuardedBoundaryMode p
  -> PacketHasTransition p overflowWall guardRescue
  -> OutputSafetyObligation p
     and a nonempty transition-graph witness
```

Like the first bridge, this theorem is closed over the existing packet
interface. It adds no new `sorry`.

## Why This Matters

The first rescue proved this was not just hand-wavy theory. The second rescue
shows the architecture is not only about positivity tricks. It can also name and
control finite-evaluation pressure.

That matters for every future backend where unbounded mathematical elegance
eventually meets fixed hardware: microcontrollers, FPGAs, DSP kernels, and
eventually ASIC paths.

Next in the series: [`The Third Proof-Carrying Rescue`](/blog/third-proof-carrying-rescue).
