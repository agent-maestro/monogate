---
layout: ../../layouts/Base.astro
title: "Why EML Optimization Lives on the Boundary"
description: "High-dimensional volume collapse explains why EML tree search hits corners, log-domain cliffs, overflow walls, and phantom-attractor behavior. The Monogate stack now has Forge traces, IR evidence, and MachLib theorem targets for it."
date: "2026-05-26"
author: "Monogate Research"
tag: "research"
featured: true
---

# Why EML Optimization Lives on the Boundary

The high-dimensional geometry story is not decorative. It is the reason EML tree
search becomes strange so quickly.

A complete depth-`k` EML tree starts with `2^k` terminal coordinates. Before the
optimizer has even evaluated the first internal node, it is already moving
through a high-dimensional cube. In that geometry, the center becomes a tiny
event and the boundary dominates.

The classical warning sign is:

```text
V(unit_ball_d) / V([-1,1]^d) -> 0
```

The Monogate high-D packets show the same pressure in EML tree space:

```text
terminal dimension -> boundary concentration -> log-domain cliffs -> exp overflow -> saturation
```

## Evidence Surface

The current evidence suite emits:

- high-dimensional corner-concentration packets
- Forge attractor trace packets
- Forge heuristic frontier packets
- useful-volume census packets
- EML IR evidence packets
- MachLib theorem-target stubs

The packets are intentionally conservative. They are sampled evidence, not a
phantom-attractor proof, not a hardware claim, and not a formal verification
claim.

## What Changed

Forge now has a log-domain optimizer branch in the real optimizer pipeline. It
is opt-in and analysis-only:

```python
optimize_module(module, log_domain=True, optimizer_trace_path="trace.json")
```

The branch identifies functions whose expression shape is likely to benefit from
positive, exp-mapped search coordinates. It exports an audit trace instead of
rewriting user semantics. That is deliberate: log-domain search changes
optimizer coordinates, not the user's mathematical function signature.

The first stdlib/examples benchmark currently finds 9 candidate functions across
82 analyzed functions. The candidates are concentrated in high-drift examples,
softplus/mish, logarithmic base conversion, and Box-Muller transforms.

## Why This Matters

Most symbolic optimizers treat tree search as if useful expressions are spread
through the interior. The high-D packets say the opposite: useful, finite,
non-saturated EML behavior is a narrow subset of a search space dominated by
faces, corners, and invalid domains.

That is the strategic reason for the Monogate stack:

- EML gives a uniform one-operator kernel.
- Forge records when search enters domain, overflow, and saturation pressure.
- IR replay packets make the lowering path inspectable.
- MachLib turns the evidence trail into theorem obligations.

This is the path from experimental optimization to verifiable compilation.

## The Formal Queue

MachLib now has a compile-checked high-dimensional theorem queue. Two obligations
are closed over explicit foothold axioms:

- cube boundary-shell probability tends to one
- first-layer raw log-domain survival decays exponentially

The harder targets remain:

- ball/cube volume collapse
- guarded lowering domain preservation

## Next Target

The next frontier is not a bigger random search. It is a proof-carrying
log-domain search discipline:

```text
positive coordinate transform
  -> guarded EML evaluation
  -> replay packet
  -> MachLib domain-preservation obligation
  -> Explorer audit surface
```

That is the line where EML stops being only a beautiful single-operator trick and
becomes an optimizer architecture for the high-dimensional world.
