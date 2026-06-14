---
layout: ../../layouts/Base.astro
title: "A Constructive Khovanskii Reduction"
description: "MachLib now ships a finite zero-count bound for polynomial-in-(x, eˣ), proven modulo an axiomatized analytic base. A Forge-emitted Butler-Volmer kernel obligation closes on top of it. Honest scope inside."
date: "2026-06-14"
author: "Monogate Research"
tag: "research"
featured: true
---

# A Constructive Khovanskii Reduction

MachLib's current foundations capstone is a constructive zero-count bound for
functions of the form

```text
f(x) = Σ_{k=0}^d a_k(x) · exp(k·x)
```

— polynomials in `(x, eˣ)` — on any open interval `(a, b)`. The bound is
finite, explicit, and the framework ships with three resolution paths and a
worked Forge-kernel application on top.

The theorem itself is classical — it is the standard Rolle/derivative reduction
behind Khovanskii's fewnomial bounds for exponential polynomials. The
contribution here is the Lean formalization, the proof architecture, and the
application to a real safety-critical kernel obligation.

This post is the research record for the closure. The code lives at
[agent-maestro/machlib](https://github.com/agent-maestro/machlib).

## The Reduction

The reduction runs through a Rolle vehicle:

```text
mulNegExpX ep c := f(x) · exp(-c·x)
```

whose derivative is `exp(-c·x) · scaledReduction(ep, c)` and which shares zeros
with `f` (since `exp > 0`). That gives the chain-step inequality

```text
zeros(f) ≤ zeros(scaledReduction f c) + 1
```

One thing worth flagging because it cost real time: the operator that works is
`scaledReduction c f := f' - c·f`, **not** the textbook
`f' - c·yₙ'·f`. The textbook variant does not drop degree in single-exp chains.
We documented the discovery in the git history; if anyone recognizes the
textbook operator from a chain setup where it *is* the right thing, we'd
genuinely like to know what we were missing.

## Three Resolution Paths

All three converge on the same bound.

**Parametric capstone** — `expPoly_khovanskii_bound`. The user supplies an
`IsKhovanskiiReducibleExp` witness (a chain of `step` and `drop` constructors)
and gets the explicit numeric bound.

**Auto-bound with propagation** — `expPoly_auto_bound_with_propagation_aux`.
A strong induction over

```text
length + Σ degreeUpper(polySimplify coeffs)
```

handles the algebra given a propagation hypothesis.

**ODE corner case** — `expPoly_ode_no_zeros`. When `f' - c·f ≡ 0` on `(a, b)`,
an MVT argument shows `f` is a pure exponential, hence zero-free. This covers
the case the propagation hypothesis can't.

Three paths, one bound.

## A Forge Kernel Closes On Top

The Forge kernel-emission pipeline ships verify obligations as `sorry` stubs
for downstream Lean discharge. One such kernel is `butler_volmer/current_density`:

```text
i(η) = i₀ · (exp(α_a · F·η/RT) - exp(-α_c · F·η/RT))
```

— the Butler-Volmer electrode-kinetics rate equation. Domain: battery
management systems, fuel cell controllers, corrosion engineering. The Forge
verify obligation is `butler_volmer_zero_at_zero_overpotential`. The
clinically meaningful statement is the iff:

```text
current = 0 ↔ overpotential = 0
```

This is a zero-count obligation. The framework closes it. A BMS or fuel-cell
controller observing zero current can now rely on the equilibrium reading
because the contradiction direction is proven, not assumed.

The proof lives at
`foundations/MachLib/Applications/ButlerVolmerKhovanskii.lean` and replaces the
`True` placeholder in `MachLib/Discovered/butler_volmer.lean`.

## Honest Foundations

We need to be plain about what is and isn't done.

MachLib axiomatizes its analytic layer rather than proving it from a smaller
base. The closure session added no assumptions beyond that documented base,
but the base itself includes:

```text
zero_count_bound_by_deriv   (Rolle zero-counting corollary, N(f) ≤ N(f') + 1)
HasDerivAt + HasDerivAt_unique + the rule axioms
exp_pos, exp_zero
MachLib.Real arithmetic and order
```

In mathlib every one of those is a theorem. The first one,
`zero_count_bound_by_deriv`, is doing the core analytic work of the reduction.
The Khovanskii layer added here is the reduction structure and the
explicit-bound bookkeeping on top of it.

Grounding the analytic base in mathlib is open work, not done in this release.

`foundations/AxiomAudit.lean` makes the full dependency set visible. Run via
`lake env lean AxiomAudit.lean`; it prints `#print axioms` for every headline
theorem. The reader does not have to take our word.

A second honesty note: `expPoly_ode_no_zeros` does not invoke
`Classical.choice` in its Lean dependency closure. We are **not** claiming it
is constructive in the analyst's sense — the MVT it rests on is classical in
spirit and only escapes the dependency list because the MVT itself is
axiomatized here.

## Non-Claims

The Khovanskii closure does not claim:

- a from-mathlib-foundations verification (the analytic base is axiomatized)
- a new mathematical result (the classical theorem precedes us)
- a tighter bound than the classical literature
- a porting of the analytic base to mathlib (open work)
- safety certification of the Butler-Volmer kernel beyond the named contract
- production deployment of the Forge proof artifact
- universally fast auto-witness construction for arbitrary ExpPoly inputs

It is a bounded formalization with one named kernel application.

## What's In The Repo

- `foundations/MachLib/SingleExpKhovanskii.lean` — three resolution paths.
- `foundations/MachLib/KhovanskiiReduction.lean` — `khovanskii_bound_full` for
  general triangular Pfaffian chains, parametric in a reduction witness.
- `foundations/MachLib/Applications/ButlerVolmerKhovanskii.lean` — the
  Forge-kernel proof.
- `foundations/AxiomAudit.lean` — reproducible audit.
- `foundations/KhovanskiiExamples.lean` — three worked applications.
- `CHANGELOG.md` — the per-release entry.

Headline files build clean with zero `sorry`. The repo contains 3
`sorry`-warnings in two non-headline modules (`MachLib.ForgeTest` and
`MachLib.HighDimensional` — work-in-progress queues unrelated to this
release). The transitive-import closure of the headline theorems and the
audit does not touch either; verified by import walk.

## Why This Matters

The constructive Khovanskii reduction is one rung on a longer ladder. The
ladder is:

```text
axiomatized analytic base
  -> constructive zero-count framework over poly-in-(x, eˣ)
  -> Forge-kernel verify obligation closures
  -> downstream safety-critical certification evidence
```

This release moves one rung. The next is grounding the analytic base in
mathlib, which converts the modulo-the-base claim into an unconditional one.
That work is not done, and we want to be plain about it.

The Butler-Volmer kernel is one application. Other Forge kernels with the
same shape — multi-exp pharmacokinetics, control-loop oscillators, corrosion
sensors — share the same proof structure, which is part of why the
framework was worth building rather than the kernel alone.

---

*Attribution: the formalization was developed by an AI agent (Claude Code)
driving MachLib commits. Coordination on behalf of the Monogate research
team. The audit log and git history are the authoritative record.*

---

*Monogate Research (2026). "A Constructive Khovanskii Reduction." monogate research blog. https://monogate.org/blog/constructive-khovanskii*
