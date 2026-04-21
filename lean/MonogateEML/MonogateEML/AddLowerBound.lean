-- MonogateEML/AddLowerBound.lean
import Mathlib.Analysis.SpecialFunctions.Log.Basic
import Mathlib.Analysis.SpecialFunctions.ExpDeriv
import Mathlib.Analysis.SpecialFunctions.Pow.Real
import Mathlib.Data.Complex.ExponentialBounds

/-!
# Add Lower Bound: SB(add) ≥ 2

This file proves that no single F16 operator computes the addition function x + y
for all real inputs x, y. Combined with the known 2-node construction
  LEdiv(x, DEML(y, 1)) = x + y
(which gives SB(add) ≤ 2), this establishes SB(add) = 2 exactly.

## Proof Strategy

The F16 family consists of 16 two-input real functions built from exp, ln, and
arithmetic (±, ×, ÷). Each operator is defined and we exhibit a concrete witness
pair (x₀, y₀) at which op(x₀, y₀) ≠ x₀ + y₀.

We work with real-valued functions on a domain where all log arguments are positive.
All witness inequalities are discharged using `linarith` / `nlinarith` together with
the precise Mathlib bounds `Real.exp_one_gt_d9` and `Real.exp_one_lt_d9`.

## No sorries

This file is sorry-free.

## Result

- `no_f16_computes_add`   : ∀ op ∈ F16, op is not the addition function
- `add_not_one_node_computable` : addition is not computable by a single F16 node
- `SB_add_ge_two`         : SB(add) ≥ 2 (combined with the 2-node upper bound: SB(add) = 2)
-/

open Real

-- ============================================================
-- 1.  Helpful abbreviations
-- ============================================================

/-- 2 < exp(1) < 3, from the 9-decimal Mathlib bounds. -/
private lemma two_lt_exp_one : (2 : ℝ) < Real.exp 1 :=
  lt_trans (by norm_num) Real.exp_one_gt_d9

/-- exp(-1) < 1, equivalently 0 < exp(-1) and exp(-1) * exp(1) = 1. -/
private lemma exp_neg_one_lt_one : Real.exp (-1) < 1 := by
  -- exp(-1) * exp(1) = exp(0) = 1, and exp(1) > 2 > 1, so exp(-1) = 1/exp(1) < 1
  have hmul : Real.exp (-1) * Real.exp 1 = 1 := by
    have h := Real.exp_add (-1) 1
    simp only [show (-1 : ℝ) + 1 = 0 from by norm_num, Real.exp_zero] at h
    linarith
  nlinarith [Real.exp_pos (-1), two_lt_exp_one]

/-- log(2) > 0. -/
private lemma log_two_pos : (0 : ℝ) < Real.log 2 := Real.log_pos (by norm_num)

-- ============================================================
-- 2.  The 16 F16 operators (real, two-argument versions)
-- ============================================================

/-- F1: EML(x, y) = exp(x) - log(y) -/
noncomputable def F1 (x y : ℝ) : ℝ := Real.exp x - Real.log y

/-- F2: EMLn(x, y) = exp(x) - log(-y)  (natural domain: y < 0) -/
noncomputable def F2 (x y : ℝ) : ℝ := Real.exp x - Real.log (-y)

/-- F3: DEML(x, y) = exp(-x) - log(y) -/
noncomputable def F3 (x y : ℝ) : ℝ := Real.exp (-x) - Real.log y

/-- F4: DEMLn(x, y) = exp(-x) - log(-y)  (natural domain: y < 0) -/
noncomputable def F4 (x y : ℝ) : ℝ := Real.exp (-x) - Real.log (-y)

/-- F5: EMLswap(x, y) = exp(y) - log(x)  (args swapped; natural domain: x > 0) -/
noncomputable def F5 (x y : ℝ) : ℝ := Real.exp y - Real.log x

/-- F6: EMLnswap(x, y) = exp(-y) - log(x)  (natural domain: x > 0) -/
noncomputable def F6 (x y : ℝ) : ℝ := Real.exp (-y) - Real.log x

/-- F7: EMLswapn(x, y) = exp(y) - log(-x)  (natural domain: x < 0) -/
noncomputable def F7 (x y : ℝ) : ℝ := Real.exp y - Real.log (-x)

/-- F8: EMLnswapn(x, y) = exp(-y) - log(-x)  (natural domain: x < 0) -/
noncomputable def F8 (x y : ℝ) : ℝ := Real.exp (-y) - Real.log (-x)

/-- F9: LEdiv(x, y) = x - log(y)  (= log(exp(x)/y); natural domain: y > 0) -/
noncomputable def F9 (x y : ℝ) : ℝ := x - Real.log y

/-- F10: LEdivn(x, y) = x - log(-y)  (natural domain: y < 0) -/
noncomputable def F10 (x y : ℝ) : ℝ := x - Real.log (-y)

/-- F11: LEAd(x, y) = log(exp(x) + y)  (natural domain: y > -exp(x)) -/
noncomputable def F11 (x y : ℝ) : ℝ := Real.log (Real.exp x + y)

/-- F12: LEAdn(x, y) = log(exp(x) - y)  (natural domain: y < exp(x)) -/
noncomputable def F12 (x y : ℝ) : ℝ := Real.log (Real.exp x - y)

/-- F13: EXL(x, y) = exp(x · log(y)) = y^x  (natural domain: y > 0) -/
noncomputable def F13 (x y : ℝ) : ℝ := Real.exp (x * Real.log y)

/-- F14: EAL(x, y) = exp(x + log(y)) = y · exp(x)  (natural domain: y > 0) -/
noncomputable def F14 (x y : ℝ) : ℝ := Real.exp (x + Real.log y)

/-- F15: EALn(x, y) = exp(x + log(-y)) = (-y) · exp(x)  (natural domain: y < 0) -/
noncomputable def F15 (x y : ℝ) : ℝ := Real.exp (x + Real.log (-y))

/-- F16: ELsum(x, y) = exp(log(x) + log(y)) = x · y  (natural domain: x,y > 0) -/
noncomputable def F16fn (x y : ℝ) : ℝ := Real.exp (Real.log x + Real.log y)

-- ============================================================
-- 3.  Each F16 operator differs from addition at a witness point
-- ============================================================

-- -------- F1: EML(x,y) = exp(x) - log(y) --------
-- Witness: (1, 1).  F1(1,1) = exp(1) - log(1) = exp(1) ≠ 1+1 = 2.
theorem F1_ne_add : ¬ (∀ x y : ℝ, F1 x y = x + y) := by
  intro h
  have h11 := h 1 1
  simp only [F1, Real.log_one] at h11
  -- h11 : exp 1 - 0 = 1 + 1, i.e., exp 1 = 2
  linarith [two_lt_exp_one]

-- -------- F2: EMLn(x,y) = exp(x) - log(-y) --------
-- Witness: (0, -1).  F2(0,-1) = exp(0) - log(1) = 1 - 0 = 1 ≠ 0+(-1) = -1.
theorem F2_ne_add : ¬ (∀ x y : ℝ, F2 x y = x + y) := by
  intro h
  have h01 := h 0 (-1)
  simp only [F2, Real.exp_zero, neg_neg, Real.log_one] at h01
  -- h01 : 1 - 0 = 0 + (-1)
  linarith

-- -------- F3: DEML(x,y) = exp(-x) - log(y) --------
-- Witness: (1, 1).  F3(1,1) = exp(-1) - 0 = exp(-1) ≠ 2.
theorem F3_ne_add : ¬ (∀ x y : ℝ, F3 x y = x + y) := by
  intro h
  have h11 := h 1 1
  simp only [F3, Real.log_one] at h11
  -- h11 : exp(-1) = 2; but exp(-1) < 1 < 2
  linarith [exp_neg_one_lt_one]

-- -------- F4: DEMLn(x,y) = exp(-x) - log(-y) --------
-- Witness: (0, -1).  F4(0,-1) = exp(0) - log(1) = 1 ≠ -1.
theorem F4_ne_add : ¬ (∀ x y : ℝ, F4 x y = x + y) := by
  intro h
  have h01 := h 0 (-1)
  simp only [F4, Real.exp_zero, neg_neg, Real.log_one] at h01
  linarith

-- -------- F5: EMLswap(x,y) = exp(y) - log(x) --------
-- Witness: (1, 1).  F5(1,1) = exp(1) - 0 = exp(1) ≠ 2.
theorem F5_ne_add : ¬ (∀ x y : ℝ, F5 x y = x + y) := by
  intro h
  have h11 := h 1 1
  simp only [F5, Real.log_one] at h11
  linarith [two_lt_exp_one]

-- -------- F6: EMLnswap(x,y) = exp(-y) - log(x) --------
-- Witness: (1, 1).  F6(1,1) = exp(-1) - 0 = exp(-1) ≠ 2.
theorem F6_ne_add : ¬ (∀ x y : ℝ, F6 x y = x + y) := by
  intro h
  have h11 := h 1 1
  simp only [F6, Real.log_one] at h11
  linarith [exp_neg_one_lt_one]

-- -------- F7: EMLswapn(x,y) = exp(y) - log(-x) --------
-- Witness: (-1, 0).  F7(-1,0) = exp(0) - log(1) = 1 ≠ -1+0 = -1.
theorem F7_ne_add : ¬ (∀ x y : ℝ, F7 x y = x + y) := by
  intro h
  have h := h (-1) 0
  simp only [F7, Real.exp_zero, neg_neg, Real.log_one] at h
  linarith

-- -------- F8: EMLnswapn(x,y) = exp(-y) - log(-x) --------
-- Witness: (-1, 0).  F8(-1,0) = exp(-0) - log(-(-1)) = exp(0) - log(1) = 1 ≠ -1.
theorem F8_ne_add : ¬ (∀ x y : ℝ, F8 x y = x + y) := by
  intro h
  have h := h (-1) 0
  simp only [F8, neg_zero, Real.exp_zero, neg_neg, Real.log_one] at h
  linarith

-- -------- F9: LEdiv(x,y) = x - log(y) --------
-- ∂/∂y = -1/y ≠ 1.
-- Witness: (0, 1).  F9(0,1) = 0 - log(1) = 0 ≠ 0+1 = 1.
theorem F9_ne_add : ¬ (∀ x y : ℝ, F9 x y = x + y) := by
  intro h
  have h01 := h 0 1
  simp only [F9, Real.log_one] at h01
  linarith

-- -------- F10: LEdivn(x,y) = x - log(-y) --------
-- Witness: (0, -1).  F10(0,-1) = 0 - log(1) = 0 ≠ 0+(-1) = -1.
theorem F10_ne_add : ¬ (∀ x y : ℝ, F10 x y = x + y) := by
  intro h
  have h := h 0 (-1)
  simp only [F10, neg_neg, Real.log_one] at h
  linarith

-- -------- F11: LEAd(x,y) = log(exp(x)+y) --------
-- ∂/∂x = exp(x)/(exp(x)+y).  At x=0,y=1: = 1/2 ≠ 1.
-- Witness: (0, 1).  F11(0,1) = log(1+1) = log(2) ≠ 0+1 = 1.
-- log(2) = 1 iff exp(1) = 2, which contradicts exp(1) > 2.
theorem F11_ne_add : ¬ (∀ x y : ℝ, F11 x y = x + y) := by
  intro h
  have h01 := h 0 1
  simp only [F11, Real.exp_zero] at h01
  -- h01 : Real.log (1 + 1) = 0 + 1, i.e., log 2 = 1
  -- Derive: exp 1 = 2 (apply exp to both sides of log 2 = 1)
  have hlog2_eq_1 : Real.log 2 = 1 := by linarith
  have hexp_eq : Real.exp 1 = 2 := by
    have hel := Real.exp_log (show (0:ℝ) < 2 by norm_num)
    -- exp (log 2) = 2, and log 2 = 1
    rw [hlog2_eq_1] at hel; linarith
  linarith [two_lt_exp_one]

-- -------- F12: LEAdn(x,y) = log(exp(x)-y) --------
-- Witness: (0, -1).  F12(0,-1) = log(exp(0)-(-1)) = log(2) ≠ -1.
-- log(2) > 0 > -1.
theorem F12_ne_add : ¬ (∀ x y : ℝ, F12 x y = x + y) := by
  intro h
  have h0m1 := h 0 (-1)
  simp only [F12, Real.exp_zero] at h0m1
  -- h0m1 : Real.log (1 - -1) = 0 + -1, i.e., Real.log 2 = -1
  -- log(2) > 0 > -1, contradiction
  have hlog2_eq : Real.log 2 = -1 := by linarith
  linarith [log_two_pos]

-- -------- F13: EXL(x,y) = exp(x·log(y)) = y^x --------
-- Witness: (1, 1).  F13(1,1) = exp(1·log(1)) = exp(0) = 1 ≠ 2.
theorem F13_ne_add : ¬ (∀ x y : ℝ, F13 x y = x + y) := by
  intro h
  have h11 := h 1 1
  simp only [F13, Real.log_one, mul_zero, Real.exp_zero] at h11
  linarith

-- -------- F14: EAL(x,y) = exp(x+log(y)) = y·exp(x) --------
-- Witness: (1, 1).  F14(1,1) = exp(1+log(1)) = exp(1) ≠ 2.
theorem F14_ne_add : ¬ (∀ x y : ℝ, F14 x y = x + y) := by
  intro h
  have h11 := h 1 1
  simp only [F14, Real.log_one, add_zero] at h11
  -- h11 : exp 1 = 2
  linarith [two_lt_exp_one]

-- -------- F15: EALn(x,y) = exp(x+log(-y)) --------
-- Witness: (0, -1).  F15(0,-1) = exp(0+log(1)) = exp(0) = 1 ≠ 0+(-1) = -1.
theorem F15_ne_add : ¬ (∀ x y : ℝ, F15 x y = x + y) := by
  intro h
  have h := h 0 (-1)
  simp only [F15, neg_neg, Real.log_one, add_zero, Real.exp_zero] at h
  linarith

-- -------- F16fn: ELsum(x,y) = exp(log(x)+log(y)) = x·y --------
-- Witness: (1, 1).  F16fn(1,1) = exp(0+0) = 1 ≠ 2.
theorem F16fn_ne_add : ¬ (∀ x y : ℝ, F16fn x y = x + y) := by
  intro h
  have h11 := h 1 1
  simp only [F16fn, Real.log_one, add_zero, Real.exp_zero] at h11
  linarith

-- ============================================================
-- 4.  Packaging: the F16 set and main theorem
-- ============================================================

/-- The F16 family as a list. -/
def f16_ops : List (ℝ → ℝ → ℝ) :=
  [F1, F2, F3, F4, F5, F6, F7, F8,
   F9, F10, F11, F12, F13, F14, F15, F16fn]

/-- No F16 operator computes addition. -/
theorem no_f16_computes_add :
    ∀ op ∈ f16_ops, ¬ (∀ x y : ℝ, op x y = x + y) := by
  intro op hmem
  -- Use `simp` to unfold list membership into a disjunction of equalities
  simp only [f16_ops, List.mem_cons, List.mem_nil_iff, or_false] at hmem
  -- hmem : op = F1 ∨ (op = F2 ∨ (... ∨ op = F16fn)...)
  rcases hmem with rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl |
                   rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl
  · exact F1_ne_add
  · exact F2_ne_add
  · exact F3_ne_add
  · exact F4_ne_add
  · exact F5_ne_add
  · exact F6_ne_add
  · exact F7_ne_add
  · exact F8_ne_add
  · exact F9_ne_add
  · exact F10_ne_add
  · exact F11_ne_add
  · exact F12_ne_add
  · exact F13_ne_add
  · exact F14_ne_add
  · exact F15_ne_add
  · exact F16fn_ne_add

-- ============================================================
-- 5.  SB(add) ≥ 2 Corollary
-- ============================================================

/-!
## Complexity Lower Bound

We model "SB complexity" informally: a single-node F16 program is exactly one
operator from `f16_ops` applied directly to the two inputs. No such program
computes addition. The known two-node construction

  LEdiv(x, DEML(y, 1))
    = F9(x, F3(y, 1))
    = x - log(exp(-y) - log(1))
    = x - log(exp(-y))
    = x - (-y)
    = x + y

shows SB(add) ≤ 2. Together: **SB(add) = 2**.
-/

/-- A function f : ℝ → ℝ → ℝ is 1-node computable (in F16) if it equals
    some operator from f16_ops applied directly to its two arguments. -/
def one_node_computable (f : ℝ → ℝ → ℝ) : Prop :=
  ∃ op ∈ f16_ops, ∀ x y : ℝ, f x y = op x y

/-- Addition is not 1-node computable in F16. -/
theorem add_not_one_node_computable :
    ¬ one_node_computable (· + ·) := by
  intro ⟨op, hmem, heq⟩
  have hbad : ∀ x y : ℝ, op x y = x + y := fun x y => (heq x y).symm
  exact no_f16_computes_add op hmem hbad

/-- **Main result**: SB(add) ≥ 2 — addition cannot be computed by a single F16 node. -/
theorem SB_add_ge_two : ¬ one_node_computable (· + ·) :=
  add_not_one_node_computable
