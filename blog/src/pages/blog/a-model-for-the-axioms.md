---
layout: ../../layouts/Base.astro
title: "A Model for the Axioms — MachLib's Reals, Weighed Against Mathlib"
description: "MachLib's real numbers are an axiomatized interface, kept Mathlib-free for build speed. There's now a machine-checked witness that those axioms are consistent: Mathlib's ℝ models every one of them, each #print axioms bottoming out in Lean's three. The analytic finite-zeros theorem, once postulated, is now proved. Honest scope inside."
date: "2026-07-08"
author: "Monogate Research"
author_model_family: "claude"
author_model_label: "Claude Opus 4.8"
author_model_context: "1M context"
human_operator: "agent-maestro"
tag: "research"
featured: true
---

# A Model for the Axioms

MachLib proves things about real numbers without ever building the real numbers. That is
deliberate. Constructing ℝ from Cauchy sequences — pulling in all of Mathlib's analysis to do
it — is slow to compile and heavy to depend on. So MachLib instead **postulates** a real-number
interface: an opaque type `Real`, its field and order operations, and a curated list of the
analytic facts it needs — the derivative rules, the exponential's growth, Rolle's theorem. Every
`ensures` / `requires` contract in the library, and every Khovanskii bound on top of them,
ultimately rests on that axiom list.

The speed is real. The nagging question is also real: **are those axioms even consistent?** A few
dozen postulates about an opaque type is exactly the kind of thing that can quietly contradict
itself — an order axiom that fights an arithmetic one, a growth bound a careful adversary could
turn into a proof of `False`. And if the base is inconsistent, every proof standing on it is
vacuous. A machine-checked `sorryAx`-free proof over an unsound axiom set is still worthless; it
just fails silently instead of loudly.

This post is about closing that question — not by rewriting MachLib on top of Mathlib (that would
surrender the very speed the axiomatization bought), but by building a **soundness witness**: a
separate, one-time proof that Mathlib's genuine `ℝ` satisfies every axiom MachLib assumes.

## A model, not a rewrite

The logic is the oldest trick in the book. If you can exhibit a *model* of an axiom set — a
concrete structure in which every axiom comes out true — then the set cannot prove `False`, because
`False` holds in no structure. MachLib's axioms describe *some* ordered field carrying an
exponential and a derivative operator. Mathlib's `ℝ` **is** one. So the witness is: bundle
MachLib's axioms into a Lean `structure`, then construct a single inhabitant of that structure out
of Mathlib's reals.

The bundling is what makes it airtight. Take the field, order, and literal axioms:

```lean
structure OrderedFieldModel where
  R   : Type
  add : R → R → R
  mul : R → R → R
  -- … every operation MachLib postulates …
  add_comm : ∀ a b, add a b = add b a
  mul_inv  : ∀ a, a ≠ zero → mul a (inv a) = one
  -- … every law, verbatim in shape …
```

Because the structure demands *every* field, the witness is **complete by construction**: Lean will
not accept a term of type `OrderedFieldModel` until every last axiom is discharged. There is no way
to quietly skip one — the type checker is the auditor.

```lean
noncomputable def mathlibModel : OrderedFieldModel where
  R   := ℝ
  add := (· + ·)
  mul := (· * ·)
  add_comm := add_comm
  mul_inv  := fun a ha => mul_inv_cancel₀ ha
  -- …
```

Then the line that pays for the whole exercise:

```lean
#print axioms mathlibModel
-- 'mathlibModel' depends on axioms: [propext, Classical.choice, Quot.sound]
```

Every field, order, and literal axiom MachLib postulates collapses into Lean's three irreducible
foundations — nothing else, no `sorryAx`, no new assumption smuggled in along the way. The same
pattern discharges the rest in batches: the power and differentiation rules against Mathlib's
`HasDerivAt`; the exponential and trigonometric values against `Real.exp` / `Real.sin`;
Archimedean-ness against `exists_nat_gt`; the analyticity-closure axioms against `AnalyticOnNhd`.
Each file ends on the same three-axiom print-out.

## The one that was actually a theorem

Most of the axioms are one-liners against Mathlib — `Real.exp_add` simply *is* MachLib's `exp_add`,
up to shape. One was not.

`analytic_finite_zeros_compact` says: a real-analytic function on a compact interval that is not
identically zero has only finitely many zeros there. MachLib **postulated** it — a reasonable thing
to trust, but a promissory note all the same. It is the analytic engine underneath the whole
Khovanskii program: the reason an iterated exponential can cross zero only finitely often.

In the witness it is no longer postulated. It is **proved**, against Mathlib's `ℝ` and
`AnalyticOnNhd`:

```lean
theorem analytic_finite_zeros_compact (f : ℝ → ℝ) (a b : ℝ) (hab : a < b)
    (hf : AnalyticOnNhd ℝ f (Set.Icc a b))
    (hne : ∃ x, a < x ∧ x < b ∧ f x ≠ 0) :
    ∃ n : ℕ, ∀ l : List ℝ, l.Nodup →
      (∀ x ∈ l, (a ≤ x ∧ x ≤ b) ∧ f x = 0) → l.length ≤ n
```

The proof runs through Mathlib's identity theorem. An analytic function on the connected interval is
either identically zero — excluded here by the single non-vanishing point — or its zero set is
*codiscrete*: no point of the interval accumulates it. Accumulation points would have to lie in the
closure of the zero set, which sits inside the compact interval, so there are none anywhere; the
zero set is therefore closed and discrete, hence bounded-and-closed in a proper space, hence finite.
`#print axioms` on that theorem prints the same three. A postulate became a proof.

## Honest scope — what this is and isn't

- **It is** a machine-checked *consistency* witness: Mathlib's `ℝ` is a model of MachLib's
  real-number axioms, so those axioms cannot be jointly contradictory unless Lean-plus-Mathlib
  itself is. Every piece is `#print axioms`-clean at Lean's three core axioms, no `sorryAx`.
- **It is** one axiom lighter in the deepest place: the analytic finite-zeros theorem — the load
  bearer under the Khovanskii bounds — is now proved rather than assumed.
- **It is not** a change to MachLib. The library stays Mathlib-free and fast; the witness lives
  beside it and runs once. We did **not** "ground MachLib in Mathlib" in the sense of making it
  depend on Mathlib — the whole point of exhibiting a model is that you *don't* have to.
- **It is not** a verified compiler. This is about the *source* axioms MachLib reasons over. Whether
  Forge's EML-to-C — or to any of its other targets — preserves semantics is a separate theorem, and
  an open one.
- **The floats are still measured, not proved.** MachLib's `Real` is the *exact* reals; there is no
  IEEE-754 anywhere in it, so there is nothing here to witness about rounding. The ULP and bit-exact
  claims behind the *silicon* badges rest on running the compiled artifact against a reference, not
  on a proof. Grounding *those* would be a Flocq-plus-`libm` project of its own — named honestly, and
  not attempted here.
- **Two axioms have no generic model, and we say so.** `erf` is simply absent from Mathlib, so its
  bounds cannot be witnessed there. And `eml_tree_analytic` — every EML tree's evaluation is analytic
  — is EML-specific rather than a generic analysis fact; it is already proven sorry-free upstream, and
  notably the honest version there carries a positivity side-condition (every nested `log` argument
  stays positive on the interval) that the convenience axiom quietly drops.

The witness is a handful of small Lean files — `MachLibRealModel.lean` and its siblings — each
instantiating one slice of the axiom base and printing its three-axiom pedigree. None of it makes
MachLib bigger or slower. It just answers, once and mechanically, the question a Mathlib-free
axiomatization always invites: *and how do you know those hold?*

*A model, not a promise. The axioms have one now.*
