# E5-quater — RESULT, and the E5 arm's books closed. 2026-07-31.

**Two pre-registrations (target 1 orchestrator-drafted / AI-countersigned-with-amendment; target 2
AI-drafted / uncountersigned and recorded as such). Ran 3 of the 4 sessions inherited from E5-ter's
remainder. The 4th is this write-up, which closes the arm at 6 of 6.**

## Outcomes, in the order they happened

| session | target | pre-registered exit taken | result |
|---|---|---|---|
| 1 | lower-bound invariant | **exit 3** (target falsified) | `e/x` **is** an EML tree, exactly |
| 2 | reachable constant floor | exit 1 (floor established) | the floor theorem **was already proved** |
| 3 | does the floor generalise | **halt point** | reduces to the original hard problem |

### Session 1 — `e/x ∈ EML`, by construction

```
eOverX := eml (eml (const 0) var) (const 1)
eval x = e / x                                    -- PROVED, exactly, for x > 0
```

The pre-registered invariant said every valid tree either diverges or is eventually bounded below in
absolute value by some `c > 0`. `e/x` decays to `0` and is never `0`. **Falsified in the first hour, by
the adversarial pass the pre-registration ordered to run first.**

This is the second consecutive target killed by construction rather than by proof, and both times the
constructing move was the same: *try to build the counterexample before trying to prove none exists.*

### Session 2 — the floor, and the finding that it already existed

`e/x` is `K/x` with `K = e`. The shape generalises: `kOverXTree a := eml (eml (const a) var) (const 1)`
evaluates to `exp (exp a) / x`. So the reachable constants for this shape are exactly the range of
`exp ∘ exp`, which is `(1, ∞)` — **`K = 1` is below the floor, and every `K > 1` is above it.**

The floor theorem is `1 < exp (exp a)`. **It was already proved in the same file, 44 lines up, as
`one_lt_exp_exp_local`.** The reachable-lemma index found it before it was re-derived. What was missing
was never a theorem; it was the reading.

### Session 3 — the general floor HALTS, with one branch closed

Does *every* tree of `K/x` form have `K > 1`? Chased one step: such a tree must be `eml t1 t2`; taking
`t2 = const 1` forces `t1.eval = log K − log x`; `t1` must itself be `eml s1 s2`; taking `s2 = var`
forces `exp (s1.eval) = log K`. But **`s2` need not be `var`** — in general
`s2.eval x = x · exp (exp (s1.eval x)) / K`, so the branch survives only if some EML tree evaluates to
a constant multiple of `x`. That is the question of which functions EML reaches: the original hard
problem.

**HALT, per the slot written before the session started.** The general floor does not get to smuggle in
the claim it was supposed to localise. Cost of discovery: one session — which is the number the halt
point was budgeted to cost.

What survives the halt:

```
no_exp_eq_log_of_le_one : 0 < K → K ≤ 1 → exp a ≠ log K
```

The floor as an **impossibility** rather than a bound, and it locates exactly where `K = 1` fails: not
by a hair, but because the equation asks `exp` to take a non-positive value.

## The arm's standing claim, stated at the accuracy it has actually reached

`1/x ∉ EML` **remains open.** It is better characterised than at the arm's start:

* the four-class taxonomy that was supposed to prove it **is false** (E5-ter), and cannot be patched by
  adding a fifth "eventually in `(0,1)`" class, because `1/x` lives there too — the band must split by
  **limit**, not by bound;
* the lower-bound reformulation that was supposed to replace it **is false** (session 1), because `e/x`
  is in EML;
* what separates `e/x` (in) from `1/x` (open) is a **constant floor**, and on the one shape that
  reaches `K/x` the floor is `K > 1` with `K = 1` excluded for a specific reason: `exp` cannot be
  non-positive;
* generalising that floor is **equivalent to the original problem**, which is the sharpest statement
  the arm produced about why the problem is hard.

## What the arm cost, and what it is evidence of

Six sessions. Four findings in E5-quater's three (one falsification, one closure, one dead-end, plus a
correction that prevented a duplicate proof), three in E5-ter's two. **Zero of the six produced the
theorem the arm set out to prove**, and the write-up says so in its title line.

The thing worth carrying forward is not any single result but the move that produced four of them:
**check whether the destination exists before walking to it.** Session 1 falsified a target in an hour
that a proof attempt would have chased for four. Session 2's index lookup replaced a re-derivation.
Session 3's halt point was written before the session and fired on schedule, which is the only reason
the answer cost one session instead of three.

The counter-evidence belongs here too: **the halt point fired at all.** A pre-registration that has to
stop a route is a route that was chosen badly, and the party that chose it was the AI (target 2 was
AI-drafted and uncountersigned). Target 1, the orchestrator-drafted one, was the session that produced
the falsification. n=2, so this is an observation and not a result — but it is the observation E2 exists
to test at n=10, and it points the way E2's pre-registered prediction predicts.

## Cross-reference

* `E5B_RESULT.md` — E5-ter, the taxonomy falsification.
* `E5QUATER_PREREGISTRATION.md` — both slot tables, including the halt point verbatim.
* `ledger/2026-07-31-e5quater.json` — 4 interventions, 3 findings.
* machlib `6cd6c921`, `2ee3a6a4`, `0b7fc035` — the three sessions' commits.


## The arm's signature move, named — CONSTRAIN THE DESTINATION

Added after the fact, because it took a result outside the arm to see it clearly.

The E5 arm's cheapest results have twice come from the same move, and it is not "try harder" or "get
lucky". It is: **instead of walking the candidate space, characterise the property any arrival must
have.** Stated as a method:

> Before enumerating the shapes that might reach a target, ask what is true of *every* shape that
> reaches it. If that property is cheap to state, it usually replaces the enumeration outright.

Where it has landed:

| where | the enumeration it replaced | the invariant that replaced it |
|---|---|---|
| E5-quater s1 | proving no valid tree decays to `0` | building `e/x` and reading off that it does |
| E5-quater s2 | characterising reachable `K` case-by-case | `exp ∘ exp` has range `(1, ∞)`, so `K > 1` |
| `x+1` depth 2 (2026-07-31, baseline arm) | **24 open subcases**, budgeted 2026-06-13 | **`witness_divisor_ge`** — three lines, every witness, every depth |

The third is the clearest specimen because the enumeration had a *price already on it*: the June
scoping note budgeted depth 2 at 36 subcases and shipped 8. The invariant closed the remaining 24 with
four one-line cases. **That ratio — 4 one-line cases against 24 subcases — is what the move looks like
when it lands.**

**This is "classify before grinding" graduated from a session discipline into a proof technique.** The
discipline said *check whether the destination exists before walking to it*; the technique says
*characterise what any arrival must look like, and let that do the walking*. Same idea, one level down,
now living inside the proofs rather than around them.

**And it predicts its own next step.** If it generalises to depth 3, the shape is the same one level
up: not a constant bound on the divisor but an **eventually-linear bound on the negative axis**,
against the divisor's required exponential growth. That prediction is recorded here so the depth-3
session can score it rather than discover it.
