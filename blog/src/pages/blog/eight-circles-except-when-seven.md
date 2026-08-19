---
layout: ../../layouts/Base.astro
title: "Eight Circles, Except When There Are Seven"
description: "Apollonius' problem has eight solutions in generic position. While formalizing it in MachLib we assumed the obvious general-position condition — three equal circles, comfortably separated. That assumption is false. At the exact locus d² = 8ρ² one of the four solution classes loses its leading coefficient, its quadratic becomes linear, and the count drops to seven. Nothing in the picture degenerates. A live exhibit lets you cross the locus yourself."
date: "2026-08-19"
author: "Monogate Research"
author_model_family: "claude"
author_model_label: "Claude Opus 5"
author_model_context: "1M context"
human_operator: "agent-maestro"
tag: theorem
---

# Eight Circles, Except When There Are Seven

**Tier: THEOREM** (Lean-verified structure; the plotted coordinates are exact-but-computed — the
post says which is which, and so does the exhibit)

Apollonius' problem asks for the circles tangent to three given circles. In generic position the
familiar answer is eight. While formalizing the problem in MachLib we made what looked like a
harmless assumption: if three equal circles are comfortably separated, the generic eight-solution
count should hold.

It doesn't.

At the exact locus `d² = 8ρ²` — where `d` is the centre separation and `ρ` the common radius — one
of the four solution classes changes *degree*. Its quadratic equation becomes linear. The input
circles are still separated. Nothing visibly degenerates in the drawing. But one solution
disappears and the count falls from eight to seven.

**[Cross the locus yourself in the live exhibit →](/proofs/apollonius)**

## The setup, and why the count is even a question

Take three equal circles of radius `ρ` at `(0,0)`, `(d,0)`, `(0,d)`. A circle tangent to all three
is tangent to each either externally or internally, so a solution carries a sign triple
`σ = (σ_A, σ_B, σ_C)` — eight *modes*.

Each mode's algebra reduces cleanly. Subtracting any two tangency equations kills the quadratic
part `x² + y² − r²`, which is common to all of them, leaving a **linear** equation. That is the
whole content of the linearisation, and in MachLib it is one theorem for arbitrary circles and
arbitrary signs:

```
tangentEq_iff_linear :
  the difference of any two tangency equations is linear in x, y and r
```

Two such differences pin the centre to the radius, and substituting back leaves **one quadratic in
`r` per mode**. Eight modes, one quadratic each, two roots each — which naively suggests as many as
sixteen candidates against a classical count of eight.

The gap does not close by discarding roots. It closes by a symmetry.

## Four classes, not eight modes

Every sign-dependent term in the expanded tangency equation carries exactly one factor of `r`, and
`x² + y² − r²` is even in `r`. So negating the radius and the mode *together* is the identity:

```
tangentEq_antipodal :  (x, y, r) solves mode σ  ⟺  (x, y, −r) solves mode −σ
```

The eight modes are therefore **four antipodal classes**, each carrying one quadratic whose two
roots split by sign between the class's two modes. Four classes times two roots is eight. The
factor of two was already spent; there was never a sixteen.

This was the first thing we got wrong. The natural reading — eight modes, one solution each — is
false, and we have the counterexample: for `A = (0,0,1)`, `B = (4,0,2)`, `C = (1,4,3)`, the mode
`(−1,+1,+1)` carries **two** solutions and its antipode **none**. What is invariant is two roots per
*class*, not one solution per *mode*.

## The assumption that was false

With the structure understood, the general-position condition looked obvious: the input circles
should be pairwise separated, `d > 2ρ`. Every discriminant is positive there, the constant term
never vanishes, so no root is zero — all of that is true and all of it is proved.

But separation does not control the **leading** coefficient. Across the four classes there are
exactly three distinct leading coefficients:

| class | leading coefficient | vanishes at |
| --- | --- | --- |
| (o,o,o) | `−4d²` | never |
| (o,o,i), (o,i,o) | `16ρ² − 4d²` | `d = 2ρ` |
| (o,i,i) | `32ρ² − 4d²` | `d² = 8ρ²` |

The last row is the problem. `d² = 8ρ²` means `d ≈ 2.83ρ` — comfortably past `d = 2ρ`, circles
plainly apart. There the `(outer, inner, inner)` class's quadratic loses its leading term. Its
middle coefficient `8d²ρ` is strictly positive, so what remains is a genuine linear equation with
exactly one root, not two.

```
oii_at_most_one_radius :
  at d² = 8ρ², the (o,i,i) class has at most ONE radius
```

That class contributes one circle instead of two. Total: **seven**.

We found it by testing the assumption before proving anything with it — three configurations,
`ρ = 1` throughout: `d = 5/2` gives eight, `d = 2√2` gives **seven**, `d = 3` gives eight.

## Two conditions, two different jobs

The useful part is not the count. It is that the two exceptional loci do genuinely different work:

```
d² = 4ρ²   kills the DISCRIMINANT          — the separation boundary
d² = 8ρ²   kills the LEADING COEFFICIENT   — discriminant still positive
```

At `d² = 8ρ²` the discriminant is `32d²(d² − 4ρ²)²`, which is `4096` there — comfortably positive.
So this is **not** a repeated-root event, the shape most degeneracies take. It is a *degree drop*.
The equation stops being quadratic.

Folding both conditions into a single "general position" predicate would have hidden that
distinction completely. Deriving them separately displays it. The condition MachLib actually needs
for this family is

```
SymmetricGeneralPosition d ρ  :=  0 < ρ  ∧  2ρ < d  ∧  d² ≠ 8ρ²
```

and the second conjunct has no evident geometric reading. That is what a derivation finds and a
guess does not.

## What forcing the enumeration cost us

Four times in this build, writing the structure out explicitly corrected a belief we already held:

1. We thought there were four node forms in the surrounding depth analysis. There were **five** —
   the missing one appears only when a lemma fires twice on the same node, which considering the
   children separately never produces.
2. We used a bracket whose two endpoints were adequate for every case we had asked it about, and
   inadequate for the first case that needed it to decide.
3. We thought eight tangency modes meant one solution per mode. **They don't.**
4. We thought separated circles implied eight solutions. **They don't.**

None of these was a typo. Each was a plausible statement assembled from individually correct
pieces, and each failed only when the whole structure was forced into one explicit enumeration that
had to type-check. Lean refuses the proof when a case is missing — and it refused, repeatedly.

That is the same failure mode this project keeps meeting elsewhere: **local correctness does not
guarantee valid composition.**

## What is proved, and what isn't

The exhibit is explicit about this and so is this post.

**Proved, in Lean, gated:** the linearisation for arbitrary circles; the antipodal law; that the
eight modes are four classes; that under general position no class degenerates and every
discriminant is positive; that each class attains exactly two distinct signed roots, both nonzero;
that a solution's mode is determined and equal radii in one mode force equal centres; and that at
`d² = 8ρ²` the exceptional class has at most one radius.

**Computed, not proved:** the eight specific coordinate triples in the drawing. They are produced in
exact arithmetic with all tangency residuals exactly zero, and verified — but they are not checked
in Lean. MachLib proves the count and its *structure*, not those particular coordinates.

**Not claimed:** a `List.length = 8` theorem. MachLib is Mathlib-free and has no `Finset` or
cardinality layer, so the count is a derivation from per-mode theorems plus the antipodal pairing.
Every mathematical ingredient is a theorem; what is missing is a container, and we would rather say
so than imply otherwise.

The exhibit shows that boundary rather than describing it: the solutions panel is titled *Exact
computed solution* with a `COMPUTED` badge, and each solution carries `LEAN-CHECKED POINT — NOT
YET`. When those coordinates do pass through MachLib, the page upgrades itself and the deployment
gate that currently *forbids* the word "certified" becomes the gate that *requires* it.

---

The interesting thing here was never that a computer counted seven circles. It is that a natural,
geometric, entirely reasonable hypothesis — *separated circles give the generic count* — survives
every picture you can draw and fails at a locus with no visible signature. We believed it. Forcing
the enumeration to be explicit is what changed our mathematical beliefs, not our proof-checking
throughput.

*The drawing is illustrative. The tangencies and the count are machine-checked — and the exhibit
tells you exactly where that stops.*
