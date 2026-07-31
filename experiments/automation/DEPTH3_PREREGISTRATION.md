# Depth 3 for `x + 1` — pre-registration. AI-DRAFTED, AWAITING COUNTERSIGNATURE.

**Drafted 2026-07-31, before any depth-3 work. Not yet countersigned; recorded as such.**

**Why this one is drafted by the AI and why that is weaker here than it was for the constant floor.**
The E5-quater target-2 precedent was that an AI may draft its own slots when the outcome is binary and
machine-checked, leaving no room to fudge a verdict. **That does not fully apply here.** Exit 2 below
("the bound resists") is a judgement call about whether an obstruction is real mathematics or a failed
route — exactly the discretion the provenance rule exists to constrain. **So this needs a signature
before it runs**, and if the orchestrator rejects the slots the work is discardable.

| slot | value |
|---|---|
| **target** | `x_plus_one_not_in_eml_3` — close depth 3, upgrading "witness at depth 4, none below depth 3" to **`x + 1` first appears at depth 4**. |
| **budget** | **1 session.** Not renewable without a fresh pre-registration. |
| **route** | fixed below, **decided before the session starts** |
| **halt** | if the linear bound needs a case analysis over depth-≤2 shapes (36 combinations), **stop** — that is the enumeration `witness_divisor_ge` exists to avoid, and reaching for it means the method did not generalise. |
| **exits** | (1) **closed** — depth 3 falls, minimality established. (2) **bound resists** — the eventually-linear bound is real mathematics beyond one session; partials banked, claim stays at "none below depth 3". (3) **falsified** — a depth-3 witness exists, minimality is 3 and the depth-2 proof needs re-reading. |

## THE ROUTE DECISION, MADE NOW — substitute, don't mirror

`witness_divisor_ge` already supplies the enumeration-free half: any witness's divisor satisfies
`t2.eval x ≥ exp (−x − 1)`. The missing half is

> `∀ t, t.depth ≤ 2 → ∃ A N, ∀ x ≤ N, t.eval x ≤ A − x`

— at most **linear** growth as `x → −∞`, against the divisor's required **exponential** growth. This is
an *eventually*-shaped claim at `−∞`, and MachLib's asymptotic vocabulary faces `+∞`.

**Decision: substitute `x ↦ −x`, do not mirror the vocabulary.** Define the reflected evaluation and a
congruence lemma, then reuse the existing `+∞` machinery wholesale. The alternative — adding
`EventuallyAtMostNeg`-style definitions and re-proving the facts about them — duplicates a vocabulary
to use it once.

**This was flagged in `EMLAdditionClosureFailure.lean` before this file existed**, precisely so it would
not be discovered mid-proof on top of sunk lemmas. **Recorded as a prediction to be scored:** the
substitution is cheaper. If the session finds otherwise, that is a scored miss, not a route failure.

## What the session does, in order

1. **Adversarial pass first**, per the arm's standing result. Try to *build* a depth-3 witness before
   trying to prove none exists. Pen-and-paper analysis says no — `exp(A)` at depth ≤ 2 is a positive
   constant, `e^x`, `K/x`, or doubly-exponential, and none is `x + 1 + log(B)` for depth-≤2 `B` — **but
   that analysis has not been checked and the same reasoning shape was wrong twice this week.**
2. The reflection definition and congruence lemma.
3. The dividend half: `exp` is monotone, so `depth_le_one_bounded_above` bounds `exp (t1.eval x)` by a
   constant. Expected cheap.
4. The divisor half: `log (t2.eval x) ≥ x + C` for depth-≤1 `t2` beyond a threshold `N`. **This is where
   the session will actually be spent.** The `N` is necessary, not cosmetic: `t2 = eml var (const b)`
   with `log b > 0` gives `exp x − log b`, which crosses zero at a finite `x` and sends `log` to `−∞`
   there. The bound holds only once the clamp has taken over.
5. Assemble; or halt per above.

## Pre-registered prediction, with its disconfirming observation named

> **The session closes depth 3 (exit 1), and step 4 is where ≥ half the effort goes.**

**Disconfirming observation, named in advance:** if the effort concentrates in step 2 — the reflection
plumbing — then the route decision above was the wrong one, and "mirror the vocabulary" was the cheaper
branch. That is a scored miss on this file's central choice and should be reported as one.

## The two prior sessions' record on predictions, stated so this one is read with it

E2 session 1 predicted `closure`, got `falsification`, and was wrong about the mechanism as well.
E5-quater target 2's slots were AI-drafted and its route hit the halt point. **The AI's record at
predicting its own sessions is, at n=2, zero for two.** This prediction should be read against that,
and a countersigner has grounds to tighten the budget rather than accept it.
