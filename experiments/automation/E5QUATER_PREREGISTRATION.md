# E5-quater — the lower-bound invariant. COUNTERSIGNED WITH ONE AMENDMENT.

**Drafted by the ORCHESTRATOR 2026-07-31. Countersigned by the AI 2026-07-31, with one amendment.**

**Note the inverted provenance, which is an improvement.** Every prior slot here was AI-drafted and
human-ratified. This one is human-drafted and AI-ratified — so **the party that will be judged did not
write the bar**, which is a cleaner separation than the arrangement it replaces. The countersignature
is only worth something if it can amend, so it did.

| slot | value |
|---|---|
| **target** | Every valid EML tree either diverges or is eventually bounded below in absolute value by some `c > 0`. (`1/x ∉ EML` follows as a corollary — the coarser, better-posed form.) |
| **route** | **AMENDED — see below.** |
| **budget** | **4 sessions, INHERITED from E5-ter's unspent remainder, not fresh.** Arm total stays honest at 6. |
| **exits** | (1) *route fails* — induction doesn't go through by these means, claim stays open. (2) *claim resists* — the hard case is real mathematics exceeding budget; partials banked. (3) *target falsified* — a valid EML tree decaying to `0` exists, which would be **the largest finding of the whole arm**: EML is expressively richer than assumed and the `1/x` question reopens completely. |
| **abandon if** | session 1 hits the halt point (same-problem-in-new-clothes), **or** 4 sessions elapse with the hard case uncharacterised. |

## THE AMENDMENT — the route's constructor checklist describes a different type

As drafted, the route says to "check closure under each constructor — sums, products, composition,
exp, log — isolating exactly what the division case demands."

**`EMLTree` has none of those.** Verified against the source:

```
inductive EMLTree : Type where
  | const : Real → EMLTree
  | var   : EMLTree
  | eml   : EMLTree → EMLTree → EMLTree
```

Three constructors, and **no division constructor at all** — `eml x y = exp x − log y`. Walking a
checklist of five constructors that do not exist would have burned session 1 discovering the type,
which is exactly the "check the destination exists" lesson E5-ter just paid for.

**Route as countersigned:**

> **Session 1** — state the invariant formally; check it on the two base cases (`const`, `var`); then
> the single inductive step `eml t1 t2`, whose two argument positions are the real sub-cases:
> the **exp-argument** (`t1`, dividend) and the **log-argument** (`t2`, divisor). The difficulty is
> expected in the log-argument position, since that is where `divisor_pos` and `inner_arms_coupled`
> already live and where the dead route's indeterminacy sat.
>
> **HALT POINT** — if the log-argument case requires the original hard claim verbatim, the
> reformulation is the same problem in new clothes. **That is a recorded finding, not a failure**, and
> session 1 is the whole cost of discovering it.
>
> **Sessions 2+** — only if session 1 shows the log-argument case is genuinely weaker. Formalise the
> induction, log-argument case last.

## Adversarial pass first, per the drafter's instruction and E5-ter's evidence

**The first hour of session 1 tries to BUILD a valid EML tree decaying to `0`, before trying to prove
none exists.** Nobody has searched, because the four-class framework assumed the answer. E5-ter just
demonstrated that this project's cheapest results come from checking whether the destination exists
before walking toward it — and exit 3 is live in a way it never was for the dead conjecture.

## One risk the countersigner is recording rather than amending

The target says "bounded below in absolute value". EML trees are built from `exp` and `log` and are
not obviously oscillatory, but **nothing in the slots establishes that**, and a tree crossing zero
infinitely often would satisfy neither disjunct while still not being `1/x`. If session 1 finds the
invariant needs a non-oscillation premise, that is an amendment to record, not a route failure.
