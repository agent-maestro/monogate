-- MonogateEML/SubLowerBound.lean
import Mathlib.Analysis.SpecialFunctions.Log.Basic
import Mathlib.Analysis.SpecialFunctions.ExpDeriv
import Mathlib.Analysis.SpecialFunctions.Pow.Real
import Mathlib.Data.Complex.ExponentialBounds

/-!
# Sub Lower Bound: SB(sub) ≥ 2

No single F16 operator computes subtraction x − y for all real x, y.
Combined with the known 2-node construction
  LEdiv(x, EML(y,1)) = x − log(exp(y)) = x − y
this establishes SB(sub) = 2 exactly.

## Proof strategy
Enumerate all 16 F16 operators; exhibit a concrete witness pair (x₀, y₀)
at which op(x₀, y₀) ≠ x₀ − y₀. All inequalities discharged by `linarith` /
`nlinarith` together with `Real.exp_one_gt_d9` and `Real.exp_one_lt_d9`.

## No sorries
-/

open Real

private lemma two_lt_exp_one' : (2 : ℝ) < Real.exp 1 :=
  lt_trans (by norm_num) Real.exp_one_gt_d9

private lemma exp_neg_one_lt_one' : Real.exp (-1) < 1 := by
  have hmul : Real.exp (-1) * Real.exp 1 = 1 := by
    have h := Real.exp_add (-1) 1
    simp only [show (-1 : ℝ) + 1 = 0 from by norm_num, Real.exp_zero] at h
    linarith
  nlinarith [Real.exp_pos (-1), two_lt_exp_one']

private lemma log_two_pos' : (0 : ℝ) < Real.log 2 := Real.log_pos (by norm_num)

noncomputable def S_F1  (x y : ℝ) : ℝ := Real.exp x - Real.log y
noncomputable def S_F2  (x y : ℝ) : ℝ := Real.exp x - Real.log (-y)
noncomputable def S_F3  (x y : ℝ) : ℝ := Real.exp (-x) - Real.log y
noncomputable def S_F4  (x y : ℝ) : ℝ := Real.exp (-x) - Real.log (-y)
noncomputable def S_F5  (x y : ℝ) : ℝ := Real.exp y - Real.log x
noncomputable def S_F6  (x y : ℝ) : ℝ := Real.exp (-y) - Real.log x
noncomputable def S_F7  (x y : ℝ) : ℝ := Real.exp y - Real.log (-x)
noncomputable def S_F8  (x y : ℝ) : ℝ := Real.exp (-y) - Real.log (-x)
noncomputable def S_F9  (x y : ℝ) : ℝ := x - Real.log y
noncomputable def S_F10 (x y : ℝ) : ℝ := x - Real.log (-y)
noncomputable def S_F11 (x y : ℝ) : ℝ := Real.log (Real.exp x + y)
noncomputable def S_F12 (x y : ℝ) : ℝ := Real.log (Real.exp x - y)
noncomputable def S_F13 (x y : ℝ) : ℝ := Real.exp (x * Real.log y)
noncomputable def S_F14 (x y : ℝ) : ℝ := Real.exp (x + Real.log y)
noncomputable def S_F15 (x y : ℝ) : ℝ := Real.exp (x + Real.log (-y))
noncomputable def S_F16 (x y : ℝ) : ℝ := Real.exp (Real.log x + Real.log y)

-- F1(1,1) = exp(1) ≠ 0 = 1−1
theorem S_F1_ne_sub : ¬ (∀ x y : ℝ, S_F1 x y = x - y) := by
  intro h; have := h 1 1; simp [S_F1, Real.log_one] at this; linarith [two_lt_exp_one']

-- F2(0,−1) = exp(0)−log(1) = 1 ≠ 0−(−1) = 1 ... actually let's use (1,−1)
-- sub(1,−1) = 2. F2(1,−1) = exp(1)−log(1) = exp(1). exp(1) ≠ 2.
theorem S_F2_ne_sub : ¬ (∀ x y : ℝ, S_F2 x y = x - y) := by
  intro h; have := h 1 (-1); simp [S_F2, neg_neg, Real.log_one] at this
  linarith [two_lt_exp_one']

-- F3(1,1) = exp(−1) ≠ 0 = 1−1
theorem S_F3_ne_sub : ¬ (∀ x y : ℝ, S_F3 x y = x - y) := by
  intro h; have := h 1 1; simp [S_F3, Real.log_one] at this; linarith [exp_neg_one_lt_one']

-- F4(0,−1) = exp(0)−log(1) = 1 ≠ 0−(−1) = 1 ... use (1,−1): F4(1,−1)=exp(−1) ≠ 2
theorem S_F4_ne_sub : ¬ (∀ x y : ℝ, S_F4 x y = x - y) := by
  intro h; have := h 1 (-1); simp [S_F4, neg_neg, Real.log_one] at this
  linarith [exp_neg_one_lt_one']

-- F5(1,1) = exp(1)−log(1) = exp(1) ≠ 0 = 1−1
theorem S_F5_ne_sub : ¬ (∀ x y : ℝ, S_F5 x y = x - y) := by
  intro h; have := h 1 1; simp [S_F5, Real.log_one] at this; linarith [two_lt_exp_one']

-- F6(1,1) = exp(−1) ≠ 0
theorem S_F6_ne_sub : ¬ (∀ x y : ℝ, S_F6 x y = x - y) := by
  intro h; have := h 1 1; simp [S_F6, Real.log_one] at this; linarith [exp_neg_one_lt_one']

-- F7(−1,0) = exp(0)−log(1) = 1 ≠ −1−0 = −1
theorem S_F7_ne_sub : ¬ (∀ x y : ℝ, S_F7 x y = x - y) := by
  intro h; have := h (-1) 0; simp [S_F7, Real.exp_zero, neg_neg, Real.log_one] at this; linarith

-- F8(−1,0) = exp(0)−log(1) = 1 ≠ −1
theorem S_F8_ne_sub : ¬ (∀ x y : ℝ, S_F8 x y = x - y) := by
  intro h; have := h (-1) 0; simp [S_F8, neg_zero, Real.exp_zero, neg_neg, Real.log_one] at this; linarith

-- F9(0,1) = 0−log(1) = 0 ≠ 0−1 = −1
theorem S_F9_ne_sub : ¬ (∀ x y : ℝ, S_F9 x y = x - y) := by
  intro h; have := h 0 1; simp [S_F9, Real.log_one] at this; linarith

-- F10(0,−1) = 0−log(1) = 0 ≠ 0−(−1) = 1
theorem S_F10_ne_sub : ¬ (∀ x y : ℝ, S_F10 x y = x - y) := by
  intro h; have := h 0 (-1); simp [S_F10, neg_neg, Real.log_one] at this; linarith

-- F11(0,1) = log(2) ≠ −1 = 0−1. log(2)>0>−1.
theorem S_F11_ne_sub : ¬ (∀ x y : ℝ, S_F11 x y = x - y) := by
  intro h; have h01 := h 0 1; simp [S_F11, Real.exp_zero] at h01
  have : Real.log 2 = -1 := by linarith
  linarith [log_two_pos']

-- F12(0,−1) = log(1−(−1)) = log(2) ≠ 0−(−1) = 1. log(2)≠1 ↔ exp(1)≠2.
theorem S_F12_ne_sub : ¬ (∀ x y : ℝ, S_F12 x y = x - y) := by
  intro h; have h0 := h 0 (-1); simp [S_F12, Real.exp_zero] at h0
  have hlog : Real.log 2 = 1 := by linarith
  have hexp : Real.exp 1 = 2 := by
    have := Real.exp_log (show (0:ℝ) < 2 by norm_num)
    rw [hlog] at this; linarith
  linarith [two_lt_exp_one']

-- F13(1,1) = exp(1·log(1)) = exp(0) = 1 ≠ 0 = 1−1
theorem S_F13_ne_sub : ¬ (∀ x y : ℝ, S_F13 x y = x - y) := by
  intro h; have := h 1 1; simp [S_F13, Real.log_one, mul_zero, Real.exp_zero] at this; linarith

-- F14(1,1) = exp(1+log(1)) = exp(1) ≠ 0
theorem S_F14_ne_sub : ¬ (∀ x y : ℝ, S_F14 x y = x - y) := by
  intro h; have := h 1 1; simp [S_F14, Real.log_one, add_zero] at this; linarith [two_lt_exp_one']

-- F15(0,−1) = exp(0+log(1)) = exp(0) = 1 ≠ 0−(−1) = 1 ... use (1,−1)
-- sub(1,−1)=2. F15(1,−1)=exp(1+log(1))=exp(1)≠2
theorem S_F15_ne_sub : ¬ (∀ x y : ℝ, S_F15 x y = x - y) := by
  intro h; have := h 1 (-1); simp [S_F15, neg_neg, Real.log_one, add_zero] at this
  linarith [two_lt_exp_one']

-- F16(1,1) = exp(log(1)+log(1)) = exp(0) = 1 ≠ 0 = 1−1
theorem S_F16_ne_sub : ¬ (∀ x y : ℝ, S_F16 x y = x - y) := by
  intro h; have := h 1 1; simp [S_F16, Real.log_one, add_zero, Real.exp_zero] at this; linarith

def s_f16_ops : List (ℝ → ℝ → ℝ) :=
  [S_F1, S_F2, S_F3, S_F4, S_F5, S_F6, S_F7, S_F8,
   S_F9, S_F10, S_F11, S_F12, S_F13, S_F14, S_F15, S_F16]

theorem no_f16_computes_sub :
    ∀ op ∈ s_f16_ops, ¬ (∀ x y : ℝ, op x y = x - y) := by
  intro op hmem
  simp only [s_f16_ops, List.mem_cons, List.mem_nil_iff, or_false] at hmem
  rcases hmem with rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl |
                   rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl
  · exact S_F1_ne_sub
  · exact S_F2_ne_sub
  · exact S_F3_ne_sub
  · exact S_F4_ne_sub
  · exact S_F5_ne_sub
  · exact S_F6_ne_sub
  · exact S_F7_ne_sub
  · exact S_F8_ne_sub
  · exact S_F9_ne_sub
  · exact S_F10_ne_sub
  · exact S_F11_ne_sub
  · exact S_F12_ne_sub
  · exact S_F13_ne_sub
  · exact S_F14_ne_sub
  · exact S_F15_ne_sub
  · exact S_F16_ne_sub

def one_node_computable_sub (f : ℝ → ℝ → ℝ) : Prop :=
  ∃ op ∈ s_f16_ops, ∀ x y : ℝ, f x y = op x y

/-- **Main result**: SB(sub) ≥ 2 — subtraction cannot be computed by a single F16 node. -/
theorem SB_sub_ge_two : ¬ one_node_computable_sub (· - ·) := by
  intro ⟨op, hmem, heq⟩
  exact no_f16_computes_sub op hmem (fun x y => (heq x y).symm)
