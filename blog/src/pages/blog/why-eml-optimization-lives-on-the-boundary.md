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

- Course 006 optimization-boundary simulator packets
- Forge boundary-optimizer benchmark packets
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

There is now also a Course 006 simulator contract:

```text
dimension/depth input
  -> EML tree-space sampler
  -> boundary classifier
  -> guard/log-domain mode
  -> replay packet
```

The public electronics lab treats the Trainer Board as a tactile control
surface for this experiment: the potentiometer selects dimension, a mode switch
selects raw/guarded/log-domain candidate behavior, LEDs/OLED-style readouts show
finite survival and guard pressure, and the dashboard exports an evidence
packet. It remains simulated courseware until a separate hardware runbook and
capture packet exist.

Forge backs the same contract with
`tools/boundary_optimizer_benchmark.py`. That benchmark runs the same dimensions,
modes, seeds, and packet fields as the simulator, so the UI is no longer just an
illustration. It is a replay surface for a reproducible research packet.

The next step was to stop calling every failure a generic boundary hit. Forge
and the simulator now share a boundary-event taxonomy:

| Event | Meaning | Obligation direction |
| --- | --- | --- |
| `corner_concentration` | sample lives near a cube face/corner | boundary-dominance counting |
| `domain_wall` | evaluation crosses a declared input domain | domain preservation |
| `overflow_wall` | evaluation pressure predicts non-finite behavior | bounded evaluation |
| `saturation_shelf` | finite output collapses onto a clamp plateau | clamp invariant |
| `phantom_attractor` | suspicious finite interior trap candidate | precision sensitivity |
| `guard_rescue` | guarded mode survives a raw-mode failure | output safety |
| `log_domain_rescue` | log-domain candidate survives a raw-mode failure | positive-coordinate preservation |

Every Course 006 trace preview frame now carries `event_class`, and every run
packet carries `event_counts`. That makes the simulator timeline, Forge
benchmark table, and MachLib obligation map talk about the same object.

The new layer is the transition graph. Instead of only counting event classes,
packets now count flows:

```text
from_event -> to_event -> count
```

They also export `transition_entropy` and `dominant_transition`. This is the
first hint of a boundary dynamics substrate: healthy guarded runs should not
only have different event counts; they should have different transition weather.
The research question becomes whether successful EML optimization is a process
of moving unsafe boundary events into proof-carrying rescue events.

Forge now names those moves as rescue operators:

| Operator | Target transition | Obligation |
| --- | --- | --- |
| `log_domain_lift` | `domain_wall -> log_domain_rescue` | positive-coordinate preservation |
| `guard_clamp` | `overflow_wall -> guard_rescue` | output safety |
| `precision_escape` | `phantom_attractor -> interior_sample` | precision sensitivity |
| `saturation_deshelf` | `saturation_shelf -> corner_concentration` | clamp invariant |

The paired intervention benchmark runs a raw baseline and an intervened run with
the same dimension, depth, sample count, and seed. It compares survival,
bad-event count, rescued-event count, transition entropy, and dominant flow.
This is still conservative: simulated, analysis-only, and not an optimizer
release claim. But it changes the research object from "what did the optimizer
hit?" to "can Forge steer boundary dynamics?"

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

The queue also has packet-level bridge obligations for the new Course 006
contract:

- valid guarded boundary packets expose a nonnegative finite-survival metric
- valid log-domain candidate packets expose a nonnegative finite-survival metric
- benchmark counts can witness the `BoundaryDominatesCenter` predicate
- `domain_wall` maps to domain preservation
- `overflow_wall` maps to bounded evaluation
- `saturation_shelf` maps to clamp invariants
- `phantom_attractor` maps to precision-sensitivity obligations
- `guard_rescue` maps to output safety
- `log_domain_rescue` maps to positive-coordinate preservation
- valid transition graphs map to boundary-dynamics obligations
- `domain_wall -> log_domain_rescue` maps to positive-coordinate preservation
- `overflow_wall -> guard_rescue` maps to output safety
- `log_domain_lift` intervention pairs map to positive-coordinate obligations
- `guard_clamp` intervention pairs map to output-safety obligations
- `precision_escape` intervention pairs map to precision obligations
- `saturation_deshelf` intervention pairs map to clamp obligations

## Next Target

The next frontier is not a bigger random search. It is control over
boundary-event dynamics:

```text
raw boundary event
  -> rescue operator
  -> transformed transition graph
  -> replay packet
  -> MachLib intervention obligation
  -> Explorer / electronics audit surface
```

That is the line where EML stops being only a beautiful single-operator trick and
becomes an optimizer architecture for the high-dimensional world.

Put sharply: EML optimization is not merely search over expressions; it is
control over boundary-event dynamics.
