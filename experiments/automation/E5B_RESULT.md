# E5-ter — RESULT. Arm's first completed run. Books closed 2026-07-31.

**Pre-registered 2026-07-31, countersigned without amendment. Ran 2 of 6 budgeted sessions.**

## Outcome: PRE-REGISTERED TARGET FALSIFIED

The route was structural induction proving `∀ t : EMLTree, EMLGoodClass t.eval` — the Phase 15B
frontier, stated in `EMLAsymptoticClass.lean` since 2026-06 and never shipped.

**It is false.** Witness, formalised:

```
t := eml (eml (const 0) var) (const (exp (−1/2)))
eval x = e/x + 1/2                                   -- PROVED for x > 0
```

Eventually trapped strictly inside `(0,1)`: not constant, not above one, not negative, not `−log x`.

**The taxonomy cannot be completed, and the reason is sharp.** `EMLGoodClass` exists to be disjoint
from `EventuallyKOverX 1`. `1/x` is itself eventually in `(0,1)`. So the omitted band cannot be
patched with a fifth "eventually in `(0,1)`" class — that class would contain `1/x` and disjointness
would collapse. The band must split by **limit**: limit in `(0,1)` is safe, limit `0` is where `1/x`
lives.

## What survives

* the **18-cell matrix** — true theorems about `eml`'s asymptotic behaviour, insufficient for the dead
  induction, most of them portable to a corrected taxonomy;
* `EventuallyAtMost` / `EventuallyAtLeast`;
* `EMLTreeValid.divisor_pos` and `inner_arms_coupled` — the latter showing validity couples the two
  arms **by position**, which no class induction can express.

## The causal correction, which the record must carry

**The twenty-five prior sessions built the falsifier, they did not chase a delusion.** The conjecture
became *checkable* only once the totalization finding (E5-bis) established what `log`'s junk branch
does and `divisor_pos` established what validity forbids. Without those, the counterexample's
construction — `exp` of something tending to `−∞`, offset by a constant divisor — had no frame in
which to be recognised as a counterexample rather than as a cell to close. Reading this result as
"twenty-five wasted sessions" would invert the causation.

## Method finding, for the retrospective

**The exit vocabulary was incomplete.** The pre-registration named two exits — *route failed* and
*claim resisted*. The actual outcome was **neither**: the route did not fail and the claim did not
resist; **the destination turned out not to exist.** A third exit, *target falsified*, was missing and
has been added to the successor's slots. Found by using the vocabulary, not by inspecting it.

## Public sentence

> The E5 arm's first completed run killed its own pre-registered target, honestly and in two of six
> sessions — which is what the arm was built to be capable of. `1/x ∉ EML` remains open and untouched.
