---
layout: ../../layouts/Base.astro
title: "The First Proof-Carrying Rescue"
description: "A narrow Forge trace now demonstrates the Monogate stack's first end-to-end boundary rescue shape: raw domain-wall failure, log-domain lift, rescue packet, and MachLib positive-coordinate obligation."
date: "2026-05-26"
author: "Monogate Research"
tag: "research"
featured: true
---

# The First Proof-Carrying Rescue

The next Monogate milestone is not a larger random search. It is one complete
rescue chain:

```text
raw EML optimization failure
  -> named boundary event
  -> Forge rescue operator
  -> replay packet
  -> MachLib obligation
```

Forge now has the first narrow artifact for that chain.

## The Function Family

The fixture is intentionally plain:

```text
positive_log_energy(x) = ln(x) + sqrt(x) + 1 / x
requires x > 0
```

Raw optimizer coordinates can cross `x <= 0`. When they do, this function hits a
domain wall: `ln(x)`, `sqrt(x)`, and `1 / x` no longer share a valid positive
input domain.

The rescue operator is `log_domain_lift`:

```text
x = exp(theta)
```

The public function boundary is unchanged. Only the internal search coordinate
changes. Since `exp(theta) > 0`, the lifted coordinate path preserves the
positive-domain obligation.

## The Trace

The Forge packet is emitted by:

```text
tools/proof_carrying_rescue.py
```

It records the EML source fixture:

```text
examples/proof_carrying_rescue.eml
```

The central transition is:

```text
domain_wall -> log_domain_rescue
```

In the generated report, three raw coordinates fail the positive-domain
boundary:

| raw coordinate | raw event | lifted coordinate | lifted event |
| ---: | --- | ---: | --- |
| `-2.0` | `domain_wall` | `0.13533528` | `log_domain_rescue` |
| `-0.5` | `domain_wall` | `0.60653066` | `log_domain_rescue` |
| `0.0` | `domain_wall` | `1.00000000` | `log_domain_rescue` |

The lifted trace has positive coordinates, finite evaluation, and a concrete
transition witness. That is the important part: the packet does not merely say
"the optimizer improved." It names the boundary event, the rescue operator, and
the proof obligation.

## The Obligation

The packet points at:

```text
PositiveCoordinateObligation
```

MachLib now has the corresponding bridge theorem:

```text
ValidBoundaryRunPacket p
  -> LogDomainBoundaryMode p
  -> PacketHasTransition p domainWall logDomainRescue
  -> PositiveCoordinateObligation p
     and a nonempty transition-graph witness
```

This theorem is still built over the current packet-level obligation interface,
but the bridge itself is closed: it does not add a new `sorry`.

## What This Is Not

This is not a production optimizer rewrite. It is not a hardware claim. It is
not a completed proof that every log-domain candidate is safe.

It is the first auditable end-to-end shape:

```text
source fixture
  -> raw domain failure
  -> log-domain lift
  -> rescue transition packet
  -> MachLib obligation bridge
```

That is the direction Monogate is building toward: optimization that emits
evidence, not just output.
