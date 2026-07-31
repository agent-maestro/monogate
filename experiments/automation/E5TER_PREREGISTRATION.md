# E5-ter — the general-depth claim. PRE-REGISTRATION, COUNTERSIGNED AND BINDING

**Drafted by AI 2026-07-31; COUNTERSIGNED WITHOUT AMENDMENT by the orchestrator, 2026-07-31. Binding.**
Route, budget (6 sessions) and both exits stand exactly as drafted. Session 1 may begin. Same provenance split as E5 and E5-bis,
and for the same reason: a bar set and met by one party measures nothing about either.

## The claim

> `1/x ∉ EML` at any depth — no `EMLTree`'s eval is eventually `1/x`.

## ROUTE — stated relative to what exists, and naming what it consumes

The proof shape already exists in `EMLAsymptoticClass.lean` and has for some time:

```
EMLGoodClass f := EventuallyConstant f ∨ EventuallyAboveOne f ∨ EventuallyNegative f ∨ EventuallyMinusLog f
EMLGoodClass.not_eventually_K_over_x_one : EMLGoodClass f → ¬ EventuallyKOverX 1 f     -- ALREADY PROVED
```

So the claim reduces to one statement: **every valid `EMLTree.eval` is in `EMLGoodClass`**, by structural
induction. The base cases are trivial. **The induction step IS the closure matrix** — each cell says
"dividend in class A, divisor in class B ⟹ result in class C".

**What the route consumes, honestly counted:**

| asset | consumed? |
|---|---|
| the 18-cell conditioned matrix | **partly — see below** |
| `EventuallyAtMost` / `EventuallyAtLeast` | **yes**, they carry six cells |
| `EMLTreeValid.divisor_pos` | **yes, and decisively** |
| the four Weierstrass theorems | **no.** Different line (T2.C smoothing). Not scaffolding for this; simply unrelated, and the route should say so rather than imply a tidier story |

**`divisor_pos` shrinks the obligation, and this is the route's one real gift.** A valid tree's divisor
is strictly positive, so a divisor can never be `Negative` or `MinusLog`. **Only three columns are
needed** — `Const`, `AboveOne`, `Dominates` — i.e. 15 cells, not 25. Of those 15:

* **12 closed** (phases ≤25 plus the pre-existing rules);
* **3 open**, and here is the problem:
  * `Negative × AboveOne` — open, ordinary;
  * `AboveOne × Dominates` — **provably indeterminate**;
  * `Dominates × Dominates` — **provably indeterminate**.

## THE RISK, PRE-REGISTERED BECAUSE IT MAY BE THE RESULT

**Two cells the induction requires are provably indeterminate.** If that stands, `EMLGoodClass` is
**not closed under `eml`**, the induction cannot be completed as stated, and the route fails —
*not because the claim is false, but because the class taxonomy is too coarse to carry it.*

Three live possibilities, all pre-registered as acceptable outcomes:

1. **The taxonomy needs refining** — split `Dominates`, or add a class, so the indeterminate cells
   resolve. The claim survives; the instrument changes.
2. **Validity supplies more than positivity** — `EMLTreeValid` carries an error-margin condition that
   the class abstraction discards. The indeterminate cells may be determinate *for valid trees*, which
   would be the same move `divisor_pos` already made once.
3. **The claim is false at some depth, or needs a strengthened hypothesis.** `1/x ∉ EML` is a
   conjecture, and a counterexample at depth `d` would be **the better finding** — larger than the
   theorem, and it would explain twenty-plus sessions of resistance. A pre-registration that only
   imagines proving the theorem will read a counterexample as failure. This one does not.

## BUDGET — derived from the only honest comparable

**6 sessions.** The comparable is the phase-17→phase-25 segment: 8 sessions producing 7 cells *and* two
predicates *and* one classification finding. The 0.88 cells/session rate is **explicitly not used** —
the degenerate-cell finding demoted it (it was earned on positive-divisor cells and the population has
since changed), and cells are the wrong unit here anyway: this route needs 3 cells, two of which may be
unreachable in principle. Sessions are budgeted against *obligations discharged*, not cells closed.

## ABANDONMENT — two exits, and they mean different things

| exit | condition | verdict recorded |
|---|---|---|
| **THE ROUTE FAILED** | after 6 sessions the two indeterminate cells are neither resolved, nor shown determinate-for-valid-trees, nor eliminated by a refined taxonomy | The *class-induction route* is closed off. **The claim is untouched** — it was never tested. Record as a dead end for the route and a `TODO` for a different attack. |
| **THE CLAIM RESISTED** | the induction completes for every reachable cell **and the claim still does not follow** — or a counterexample appears | This is information *about the mathematics*. Record as `falsification` if a counterexample, `dead_end` with the obstruction characterised otherwise. |

**These are not the same outcome and must not be summarised as one.** A route failing says the tool was
wrong; a claim resisting says the world is. The record is built to tell them apart **from day one**,
not at the post-mortem — which is the E5-bis amendment applied before it has to be.

## Standing exception to the machinery moratorium

Instrument-building is halted for this route. **Obeying instruments is not.** If a gate fires or a
specimen convicts mid-route, the line halts and the failure is attributed before work continues. The
moratorium is on building, never on listening.

~~`TODO: orchestrator` — countersign, amend, or replace.~~ **DONE 2026-07-31, without amendment.**
