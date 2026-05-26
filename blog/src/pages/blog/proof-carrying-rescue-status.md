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

| Boundary event | Rescue operator | Rescue event | Forge evidence | MachLib bridge | Semantic tier |
| --- | --- | --- | --- | --- | --- |
| `domain_wall` | `log_domain_lift` | `log_domain_rescue` | packet + tests + registry | concrete witness + closed packet bridge | `concrete_sample_invariant` |
| `overflow_wall` | `guard_clamp` | `guard_rescue` | packet + tests + registry | concrete witness + closed packet bridge | `concrete_sample_invariant` |
| `phantom_attractor` | `precision_escape` | `interior_sample` | packet + tests + registry | concrete witness + closed packet bridge with explicit event witness | `concrete_sample_invariant` |
| `saturation_shelf` | `saturation_deshelf` | `corner_concentration` | packet + tests + registry | concrete witness + closed packet bridge with explicit event witness | `concrete_sample_invariant` |

## Reading The Table

`packet + tests` means Forge has a dedicated source fixture, trace tool,
generated report, and regression tests.

`concrete witness + closed packet bridge` means MachLib has both a theorem
connecting a valid packet transition to its obligation and a sample-level
theorem that discharges the concrete local obligation. The log-domain lane has
a positive-coordinate witness. The guard-clamp lane now has an output-safety
witness. The precision-escape lane has a local precision-sensitivity witness.
The saturation-deshelf lane has a clamp-invariant witness.

`closed packet bridge with explicit event witness` means the bridge is closed,
but the theorem requires both the event witness and transition witness. That is
the current honest shape for phantom-attractor evidence.

The saturation-deshelf lane also has a concrete clamp-invariant witness now,
but it remains more cautious in public copy because deshelf moves a trace off a
saturation shelf rather than simply ending in a rescue-normal event.

The precision-escape witness is local: it records that low precision reported a
stalled gradient, while the higher-precision replay exposed a nonzero escape
signal and moved the sample from `phantom_attractor` to `interior_sample`. It
does not claim a convergence theorem.

The four-lane suite manifest is published as
[`Proof-Carrying Rescue Suite v0`](/blog/proof-carrying-rescue-suite-v0).
The manifest reading guide is
[`How to Read the Rescue Suite`](/blog/how-to-read-the-rescue-suite).

## Next Frontier

The next target is no longer another one-off rescue. It is governed
unification:

```text
four packets -> one manifest -> obligation registry -> approval gate -> Explorer/dashboard/replay surface
```

The registry says which obligations are routed, witnessed, concretely proven,
CI guarded, public-copy safe, semantically tiered, or blocked. The approval gate
decides whether the generated artifacts may be surfaced or deployed while
keeping the full semantic-rewrite claim false.
