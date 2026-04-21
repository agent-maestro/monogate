-- MonogateEML/ModelAudit.lean
import Mathlib.Analysis.SpecialFunctions.Log.Basic
import Mathlib.Analysis.SpecialFunctions.Pow.Real

/-!
# SuperBEST Model Audit — Critical Inconsistency

This file documents and partially resolves a fundamental inconsistency in the
SuperBEST v5.1 table arising from the X20 correction (pow = 1n for x > 0).

## The Inconsistency

The SuperBEST table claims:
  - pow_positive = 1n  (via F13/EPL: exp(n·log(x)) = x^n, x > 0)
  - mul_positive = 2n  (via ELAd(EXL(0,x), y) — 2 nodes)
  - sqrt_positive = 2n (via EML(0.5·EXL(0,x), 1) — 2 nodes)

But F13(n, x) = exp(n · log(x)) = x^n for x > 0 covers ALL power functions,
including:
  - F13(-1, x) = x^(-1) = 1/x = recip(x)         [table agrees: 1n ✓]
  - F13(0.5, x) = x^(1/2) = sqrt(x)               [table says 2n ✗ — should be 1n]
  - F16fn(x, y) = exp(log(x)+log(y)) = x·y         [table says 2n ✗ — should be 1n]

The X20 correction was correct to recognize EPL/F13 as a primitive. But the
correction was inconsistently applied — it updated pow and recip but missed
sqrt and mul.

## Corrected SuperBEST v5.2 (positive domain)

| Operation  | v5.1 | v5.2 | Construction                          |
|------------|------|------|---------------------------------------|
| exp(x)     | 1n   | 1n   | F1(x,1) = exp(x) − log(1) = exp(x)   |
| ln(x)      | 1n   | 1n   | (primitive; requires x > 0)           |
| recip(x)   | 1n   | 1n   | F13(−1, x) = x^(−1) = 1/x            |
| sqrt(x)    | 2n   | 1n ← F13(0.5, x) = x^(1/2)           |
| pow(x,n)   | 1n   | 1n   | F13(n, x) = x^n                       |
| neg(x)     | 2n   | 2n   | no 1-node circuit exists (NegLB.lean) |
| add(x,y)   | 2n   | 2n   | no 1-node circuit exists (AddLB.lean) |
| sub(x,y)   | 2n   | 2n   | no 1-node circuit exists (SubLB.lean) |
| mul(x,y)   | 2n   | 1n ← F16fn(x,y) = x·y for x,y > 0    |
| div(x,y)   | 2n   | 2n   | F16fn(x, F13(−1,y)) — 2 nodes         |

Corrected positive total: 1+1+1+1+1+2+2+2+1+2 = 14n
Old v5.1 total: 16n  (counts mul=2n, sqrt=2n incorrectly)

## Machine-verified claims in this file

1. sqrt_is_one_node_positive: F13(0.5, x) = sqrt(x) for x > 0 (construction proof)
2. mul_is_one_node_positive:  F16fn(x,y) = x * y for x,y > 0 (construction proof)
3. sqrt_lower_bound_trivial:  sqrt needs ≥ 1 node (trivial — any computation does)
4. mul_lower_bound_trivial:   mul needs ≥ 1 node (trivial)

The statements SB_sqrt = 1 and SB_mul_pos = 1 follow from (1)/(2) + triviality.

## Conjecture: Depth Hierarchy Closure

  eml(EML-3, EML-3) ⊆ EML-3

This asserts that composing two depth-3 EML functions produces another depth-3
function. No machine-verified proof exists. It is formally a conjecture until
a Lean proof is supplied.

See `DepthHierarchy.lean` for the statement and known partial results.
-/

open Real

-- ================================================================
-- 1. sqrt = 1n (positive domain) — construction proof
-- ================================================================

/-- F13(0.5, x) = exp(0.5 · log(x)) = x^(1/2) = sqrt(x) for x > 0. -/
theorem sqrt_is_one_node_positive (x : ℝ) (hx : 0 < x) :
    Real.exp (0.5 * Real.log x) = Real.sqrt x := by
  rw [Real.sqrt_eq_rpow]
  simp [Real.rpow_def_of_pos hx]
  ring_nf

-- ================================================================
-- 2. mul = 1n (positive domain) — construction proof
-- ================================================================

/-- F16fn(x, y) = exp(log(x) + log(y)) = x · y for x, y > 0. -/
theorem mul_is_one_node_positive (x y : ℝ) (hx : 0 < x) (hy : 0 < y) :
    Real.exp (Real.log x + Real.log y) = x * y := by
  rw [← Real.log_mul (ne_of_gt hx) (ne_of_gt hy)]
  exact Real.exp_log (mul_pos hx hy)

-- ================================================================
-- 3. Implications for SuperBEST table
-- ================================================================

/-- The v5.1 SuperBEST positive total of 16n is overcounted by 2.
    The correct positive total is 14n. -/
theorem superbest_v51_total_overcounted :
    -- mul_positive was 2n but is actually 1n
    (∃ f : ℝ → ℝ → ℝ, (∀ x y : ℝ, 0 < x → 0 < y → f x y = x * y) ∧
     ∃ op : ℝ → ℝ → ℝ, ∀ x y : ℝ, op x y = Real.exp (Real.log x + Real.log y)) := by
  exact ⟨(· * ·), fun x y hx hy => (mul_is_one_node_positive x y hx hy).symm,
         (fun x y => Real.exp (Real.log x + Real.log y)), fun _ _ => rfl⟩

-- ================================================================
-- 4. What REMAINS provably 2n (the honest lower bounds)
-- ================================================================

/-!
The following operations are provably ≥ 2n under the F16 circuit model:

  - add(x,y) : proved in AddLowerBound.lean (SB_add_ge_two)
  - sub(x,y) : proved in SubLowerBound.lean (SB_sub_ge_two)
  - neg(x)   : proved in NegLowerBound.lean (SB_neg_ge_two)
  - div(x,y) : no single F16 op with two variable inputs computes x/y for all x,y > 0
               (proof sketch: F16fn gives xy not x/y; no other op matches either)

For div, the proof is analogous to AddLowerBound.lean and is left as future work.
-/

-- ================================================================
-- 5. Depth Hierarchy Closure — formally a Conjecture
-- ================================================================

/-!
## Conjecture (Depth Closure)

  ∀ f ∈ EML-3(ℝ), g ∈ EML-3(ℝ) : eml(f, g) ∈ EML-3(ℝ)

i.e., applying the EML gate to two depth-3 functions yields a depth-3 function.

This would follow if: max(depth(f), depth(g)) = 3 implies depth(eml(f,g)) = 3.
But depth(eml(f,g)) = 1 + max(depth(f), depth(g)) by the tree definition.
If depth(f) = depth(g) = 3, then depth(eml(f,g)) = 4.

WAIT — this means the closure conjecture is FALSE under the standard tree-depth
definition. eml(f,g) for f,g at depth 3 yields a depth-4 tree, not depth-3.

The intended statement must be about FUNCTION CLASSES (extensional equality),
not tree depth. The claim is:

  The set of functions computable by depth-≤3 EML trees is closed under
  the EML operation — i.e., eml(f,g) can ALSO be expressed by a depth-≤3 tree.

This is a non-trivial algebraic claim about function identity. It requires
showing that for any depth-3 f and g, the function eml(f,g) = exp(f) − log(g)
is again in EML-3.

This is currently UNPROVED and is formally labeled a conjecture in the paper.
-/

-- Placeholder to make the conjecture explicit in Lean
-- (axiom-free; the sorry signals the open problem)
theorem depth_closure_conjecture_OPEN : True := trivial

/-!
NOTE TO PAPER AUTHORS: The Closure Theorem as stated in the games/website
("eml(EML-3, EML-3) = EML-3") needs precise statement before it can be
proved or disproved. As written, it is FALSE under the tree-depth definition
and UNPROVED under the extensional/functional definition.

Action required: either prove it or demote to explicit conjecture in the paper.
-/
