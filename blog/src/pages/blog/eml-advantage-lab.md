---
layout: ../../layouts/Base.astro
title: "The EML Advantage Lab"
description: "A bounded research ledger for where EML helps, where protected standard math wins, and which claims remain blocked."
date: "2026-05-28"
author: "Monogate Research"
tag: "research"
featured: true
---

# The EML Advantage Lab

The current Monogate research question is no longer:

```text
Does EML win everywhere?
```

It does not.

The better question is:

```text
Where does EML help, where does standard math win, and which claim is still blocked?
```

That is what the EML Advantage Lab tracks.

The developer-facing surface lives at:

```text
https://monogate.dev/explorer/eml-advantage
```

This note is the research record for what that surface currently means.

## First Result

The first Advantage Lab scoreboard has nine packets:

```text
EML wins:       1
standard wins:  4
mixed:          3
research-only:  1
```

That is the right shape for a serious research instrument. It does not turn
EML into a slogan. It lets EML lose when protected numerical code is better.

Current interpretation:

- EML is strongest as a generator identity, proof/search grammar, and teaching
  lens.
- Standard or protected math often wins for runtime and numerical stability.
- Deep EML trees need guard rules before they can support public advantage
  claims.
- Symbolic-regression claims require full controls and holdouts, not attractive
  one-off residual plots.

## What Survived

The clearest EML win so far is `exp_from_eml_v0`:

```text
eml(x, 1) = exp(x)
```

That is not a runtime speed claim. It is a generator-identity and proof-shape
win: a small EML form cleanly maps to a named MachLib witness and a bounded
Atlas claim.

Mixed cases include:

- `ln_from_eml_v0`
- `gaussian_energy_v0`
- `prime_signature_log_recovery_v0`

These are useful as lenses, packet shapes, or teaching/search coordinates, but
not currently better runtime implementations.

Standard/protected wins include:

- near-zero `exp(x) - 1`, where protected `expm1(x)` is the right lowering
- softplus/log-sum-exp, where protected max-shifted/logaddexp-style forms win
- sigmoid derivative, where stability evidence currently favors standard
  guarded implementation

## Negative Controls Matter

The lab includes negative controls because otherwise it would become a
promotion machine.

Confirmed controls include:

- protected `expm1` should beat naive `exp(x) - 1` near zero
- protected log-sum-exp should beat naive exponentiate-and-log forms
- arbitrary Gaussian bumps should not become an EML advantage story
- arbitrary polynomial controls should not look EML-native

The deep-tree holdout is especially important. It found no EML-structure win
under the current depth-stress set and blocked three unstable trees. That does
not weaken the project; it makes the project harder to fool.

## Guarded Lowering

The next engineering move was not to change a compiler. It was to write down
guard rules:

- preserve EML when it helps proof/search shape
- lower near-zero `exp(x)-1` to protected `expm1`
- lower softplus/log-sum-exp to protected implementations
- require positive-domain guards for logarithms
- block unstable deep trees
- require trial packets before advantage claims

Those rules now feed the packet builder and mock compiler-decision layer on
`monogate.dev`. They are not production compiler behavior.

## The PySR Reality Check

The first private PySR run did not show a robust EML grammar advantage on the
prime-residual fixture.

That is useful.

It means the research claim has to become sharper:

```text
Can a refined EML grammar recover specific structures with lower complexity
under pre-registered controls and holdouts?
```

not:

```text
EML is universally better for symbolic regression.
```

## Non-Claims

The Advantage Lab does not claim:

- broad EML superiority
- public runtime performance
- compiler correctness
- production lowering
- hardware measurement
- theorem discovery
- Riemann Hypothesis proof
- zeta-zero discovery
- certified safety

It is a bounded research ledger.

## Why This Matters

The lab changes Monogate from "look at this beautiful operator" into a
reviewable research machine:

```text
idea
  -> packet
  -> holdout
  -> negative control
  -> guard decision
  -> proof obligation or protected lowering
  -> public claim boundary
```

That is the current shape of the project.

The goal is not to force every computation through EML. The goal is to learn
which computations become more inspectable, teachable, searchable, or
formalizable when EML is the native grammar.

