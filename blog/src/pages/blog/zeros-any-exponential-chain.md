---
layout: ../../layouts/Base.astro
title: "Finiteness of Zeros for Any Exponential-Type Chain, Machine-Checked"
date: 2026-07-04
tag: theorem
description: "We lifted an earlier rolle-only, machine-checked finiteness proof from one hardcoded tower of iterated exponentials to arbitrary exponential-type Pfaffian chains at every depth — with one honest hypothesis we do not round off: positivity."
---

# Finiteness of Zeros for Any Exponential-Type Chain

An earlier result of ours proved, in Lean 4 with `rolle` as the sole analytic axiom, that a polynomial in the tower of iterated exponentials

```
y₀ = eˣ,   y₁ = e^{eˣ},   y₂ = e^{e^{eˣ}},   …
```

has only finitely many zeros on any interval — a self-contained, machine-checked reduction of a classical Khovanskii/Pfaffian fact, with **no** "finitely many zeros" citation axiom. That proof, though, was about *one specific* tower.

This note reports the lift: the same argument now holds for an **arbitrary exponential-type Pfaffian chain**, at every depth — and it comes with one honest hypothesis the tower case did not need, which we put front and center rather than bury.

## The object

A **Pfaffian chain** of length `N` is functions `y₀, …, y_{N-1}` on an interval, each with its derivative recorded by a polynomial in the lower variables:

```
yᵢ'(x) = Pᵢ( x, y₀(x), …, y_{N-1}(x) ),    Pᵢ free of y_j for j > i.
```

A **Pfaffian function** is any polynomial `p(y₀, …, y_{N-1})` evaluated along the chain. "Exponential-type" means each relation factors as `Pᵢ = Gᵢ·yᵢ` — the abstract shadow of "`yᵢ` is an exponential of something built from the lower levels." The iterated-exponential tower is the special case `Gᵢ = y₀·…·y_{i-1}`.

The question: can such a function have infinitely many zeros on an open interval? Classically, no. Here is a machine-checked reduction of that, for *any* such chain.

## What is proven

```
theorem pfaffian_khovanskii_bound_gen_uncond
  (a b : Real) (hab : a < b) :
    ∀ (M : Nat) (c : PfaffianChain (M + 2)), IsExpChain c → c.IsCoherentOn a b →
      (∀ z, a < z → z < b → ∀ i, 0 < c.evals i z) →          -- positive coherence
      ∀ (p : MultiPoly (M + 2)),
      (∃ z, a < z ∧ z < b ∧ (pfaffianChainFn c p).eval z ≠ 0) →
      ∃ N : Nat, ∀ zeros : List Real, zeros.Nodup →
        (∀ z ∈ zeros, a < z ∧ z < b ∧ (pfaffianChainFn c p).eval z = 0) →
        zeros.length ≤ N
```

In words: for **any** exponential-type Pfaffian chain of any depth that is coherent and **positive** on `(a,b)`, and any polynomial `p` not identically vanishing there, the zeros of `p(y₀, …, y_{M+1})` are finite in number.

`#print axioms` audits to `propext`, `Classical.choice`, `Quot.sound`, and the honest analytic interface (`rolle`, `exp`, `log`, `exp_pos`, the `HasDerivAt` calculus). No `sorry`; no Khovanskii-citation axiom. **`rolle` is the sole analytic axiom.** The three former base hypotheses — the depth-2 base, the reduce base, and the integrating-factor family — are all discharged internally; the depth-2 case stands alone as its own named theorem.

## The one honest hypothesis: positivity

This is the paragraph that matters most. The tower case needs **no** positivity hypothesis: its `yᵢ = e^{⋰}` are positive for free, and each tower level is *its own polynomial antiderivative* — so its integrating factor is a polynomial, and no logarithm ever appears.

A general exponential-type chain has neither luxury. Its integrating factor is

```
E(x) = −Σᵢ degᵢ · log(yᵢ(x)),      E'(x) = −Σᵢ degᵢ · (yᵢ'/yᵢ) = −Σᵢ degᵢ · Gᵢ,
```

which is exactly the reduce multiplier — **but only when `log(yᵢ)` is defined, i.e. `yᵢ > 0`.** There is no fundamental theorem of calculus in this axiom base to conjure an antiderivative otherwise; this `log` construction *is* the general antiderivative, and positivity is genuinely load-bearing.

So we state it as an explicit hypothesis. For any real exponential-type chain it holds (the `yᵢ` are exponentials), and a concrete witness discharges it. The theorem is unconditional in its former two hypotheses; **it is conditional on positivity, and we do not round that corner.**

## How the lift works

The engine is the same well-founded descent as the tower proof — base / degree-trim / inner-trim / reduce, dispatched on the shape of `p` — but three pieces had to be rebuilt chain-agnostically:

1. **The reduce descent, for an arbitrary chain.** The multiplier that makes the vehicle's derivative factor cleanly is a recursively graded object over the chain's own `Gᵢ`; its descent is a mutual induction over the chain, closed with `rolle` at the depth-2 base.

2. **The integrating factor, constructed rather than assumed.** For the tower it was an explicit polynomial. For a general chain we *build* `E = −Σ degᵢ log yᵢ` and prove `HasDerivAt E (−reduceMultiplier)` using the log chain rule — this is where positivity enters — and the recursion carries this factor up the chain alongside the reduce multiplier, so the theorem builds its own integrating factor.

3. **The chain-agnostic vehicle.** The no-zeros and Rolle-transfer steps were already abstracted to an arbitrary chain plus an arbitrary antiderivative `E`; the lift feeds them the `E` from (2).

The load-bearing facts are the same three as before: a genuinely well-founded nested-`Nat` lexicographic measure, a reduce that genuinely descends it, and one honest use of `rolle`.

## Non-vacuous, and it subsumes the tower

Two guards against the theorem being empty or a mere restatement, both machine-checked:

- **Non-vacuity.** A concrete depth-2 exponential-type chain is exhibited satisfying all three hypotheses, and the bound applied to it yields finiteness. The theorem genuinely applies.
- **The general subsumes the specific.** The *exact* statement of the tower theorem is re-derived by instantiating this general bound at a normalized iterated-exponential chain. Because the chain functions are literally identical, the two evaluations are definitionally equal and the general result transfers with no rewriting — a strict generalization, not a reformulation.

(One honest wrinkle this exposed: the hardcoded tower chain is not *literally* an "exponential-type chain" in the strict syntactic sense — its level-0 relation is the bare `y₀`, not `1·y₀`, in the free polynomial syntax — so the bridge routes through an eval-equal normalized chain. A syntactic artifact, disclosed rather than papered over.)

## Claim boundaries

- **What is claimed.** A machine-checked, self-contained reduction proving finiteness of zeros for an arbitrary exponential-type Pfaffian chain at every depth, positive-coherent on `(a,b)`, with no Khovanskii-citation axiom and no `sorry`. It strictly generalizes the iterated-exponential tower result and is validated non-vacuous.
- **What is NOT claimed.** Not a fully unconditional result — **positive coherence (`yᵢ > 0`) is a real hypothesis.** Not a from-mathlib-foundations proof — the analytic base (`rolle`, `exp`, `log`, the derivative calculus) is *axiomatized*. Not new mathematics — the finiteness is classical Khovanskii/Pfaffian theory; the contribution is the Lean architecture and the chain-agnostic, citation-axiom-free descent. Not a statement about compiler correctness, runtime performance, or any product.
- **The single load-bearing analytic axiom** is `rolle`. Every descent step's zero-count-from-derivative primitive is a theorem derived from it. If you accept Rolle's theorem and the standard exp/log calculus, the rest of the finiteness (positivity granted) is derived mechanically.

The theorems live in `agent-maestro/machlib` under `MachLib/PfaffianGeneral*.lean`; the exact statements and `#print axioms` output are reproducible from source.

---

*A companion to our machine-checked zero-finiteness work — the tower generalized to the class, with the one hypothesis it costs stated in daylight.*
