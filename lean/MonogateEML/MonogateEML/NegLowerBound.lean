-- MonogateEML/NegLowerBound.lean
import Mathlib.Analysis.SpecialFunctions.Log.Basic
import Mathlib.Analysis.SpecialFunctions.ExpDeriv
import Mathlib.Data.Complex.ExponentialBounds

/-!
# Neg Lower Bound: SB(neg) ≥ 2

No single F16 operator, with one argument fixed to a constant, computes neg(x) = −x
for all real x. Combined with the known 2-node construction
  LEdiv(0, EML(x,1)) = 0 − log(exp(x)) = −x
this establishes SB(neg) = 2 exactly.

## Proof strategy

For a unary 1-node F16 circuit, one input is a free variable x and the other
is a fixed constant c ∈ ℝ. We must rule out BOTH argument orderings:
  (i)  op(x, c) = −x  for all x, for some c
  (ii) op(c, x) = −x  for all x, for some c

For each F16 operator op, we derive a contradiction from any such assumption
using at most two witness evaluations (x = 0 and x = 1).

Key facts used: exp(1) > 2, exp(−1) < 1, log(2) > 0.

## No sorries
-/

open Real

private lemma e_gt_two  : (2 : ℝ) < Real.exp 1 := lt_trans (by norm_num) Real.exp_one_gt_d9
private lemma eneg_lt_one : Real.exp (-1) < 1 := by
  have : Real.exp (-1) * Real.exp 1 = 1 := by
    have h := Real.exp_add (-1) 1; simp only [show (-1:ℝ)+1=0 from by norm_num, Real.exp_zero] at h; linarith
  nlinarith [Real.exp_pos (-1), e_gt_two]
private lemma log2_pos : (0:ℝ) < Real.log 2 := Real.log_pos (by norm_num)

-- ================================================================
-- Section 1: op(x, c) ≠ −x  for all c  (x in first position)
-- ================================================================

-- F1(x,c) = exp(x)−log(c). At x=0: 1−log(c)=0→c=e. At x=1: exp(1)−1=−1→exp(1)=0. ⊥
theorem N_F1_x_ne_neg : ¬ ∃ c : ℝ, ∀ x : ℝ, Real.exp x - Real.log c = -x := by
  intro ⟨c, h⟩
  have h0 := h 0; simp at h0   -- 1 − log c = 0, so log c = 1
  have h1 := h 1; simp at h1   -- exp 1 − log c = −1
  linarith [Real.exp_pos (1:ℝ)]

-- F2(x,c)=exp(x)−log(−c). At x=0 and x=1: exp(1)−1=−1→exp(1)=0. ⊥
theorem N_F2_x_ne_neg : ¬ ∃ c : ℝ, ∀ x : ℝ, Real.exp x - Real.log (-c) = -x := by
  intro ⟨c, h⟩
  have h0 := h 0; have h1 := h 1; simp at h0 h1; linarith [Real.exp_pos (1:ℝ)]

-- F3(x,c)=exp(−x)−log(c). At x=0: 1−log(c)=0. At x=1: exp(−1)−log(c)=−1→exp(−1)−1=−1→exp(−1)=0. ⊥
theorem N_F3_x_ne_neg : ¬ ∃ c : ℝ, ∀ x : ℝ, Real.exp (-x) - Real.log c = -x := by
  intro ⟨c, h⟩
  have h0 := h 0; have h1 := h 1; simp at h0 h1; linarith [Real.exp_pos (-1:ℝ)]

-- F4(x,c)=exp(−x)−log(−c). Same: exp(−1)=0. ⊥
theorem N_F4_x_ne_neg : ¬ ∃ c : ℝ, ∀ x : ℝ, Real.exp (-x) - Real.log (-c) = -x := by
  intro ⟨c, h⟩
  have h0 := h 0; have h1 := h 1; simp at h0 h1; linarith [Real.exp_pos (-1:ℝ)]

-- F9(x,c) = x−log(c). At x=0: −log(c)=0→c=1. At x=1: 1−0=1≠−1. ⊥
theorem N_F9_x_ne_neg : ¬ ∃ c : ℝ, ∀ x : ℝ, x - Real.log c = -x := by
  intro ⟨c, h⟩
  have h0 := h 0; have h1 := h 1; simp at h0 h1; linarith

-- F10(x,c)=x−log(−c). At x=0: −log(−c)=0→log(−c)=0. At x=1: 1−log(−c)=1≠−1. ⊥
theorem N_F10_x_ne_neg : ¬ ∃ c : ℝ, ∀ x : ℝ, x - Real.log (-c) = -x := by
  intro ⟨c, h⟩
  have h0 := h 0; have h1 := h 1; simp at h0 h1; linarith

-- F11(x,c)=log(exp(x)+c). At x=0: log(1+c)=0→c=0. Then F11(1,0)=log(exp(1))=1≠−1. ⊥
theorem N_F11_x_ne_neg : ¬ ∃ c : ℝ, ∀ x : ℝ, Real.log (Real.exp x + c) = -x := by
  intro ⟨c, h⟩
  have h0 := h 0; simp at h0
  -- h0 : log(1+c) = 0, so 1+c = 1 (since log 1 = 0 and log is injective on positives), c = 0
  have hc : c = 0 := by
    have hpos : 0 < 1 + c := by
      have := Real.log_eq_zero.mp h0; linarith [Real.exp_pos (0:ℝ)]
    have := Real.log_eq_zero.mp h0
    linarith
  have h1 := h 1; rw [hc] at h1; simp at h1
  -- h1 : log(exp 1) = −1, i.e., 1 = −1. ⊥
  linarith

-- F12(x,c)=log(exp(x)−c). At x=0: log(1−c)=0→c=0. Then F12(1,0)=log(exp(1))=1≠−1. ⊥
theorem N_F12_x_ne_neg : ¬ ∃ c : ℝ, ∀ x : ℝ, Real.log (Real.exp x - c) = -x := by
  intro ⟨c, h⟩
  have h0 := h 0; simp at h0
  have hc : c = 0 := by
    have := Real.log_eq_zero.mp h0; linarith [Real.exp_pos (0:ℝ)]
  have h1 := h 1; rw [hc] at h1; simp at h1; linarith

-- F13(x,c)=exp(x·log(c))=c^x. At x=0: exp(0)=1=0. ⊥  (1≠0)
theorem N_F13_x_ne_neg : ¬ ∃ c : ℝ, ∀ x : ℝ, Real.exp (x * Real.log c) = -x := by
  intro ⟨c, h⟩
  have h0 := h 0; simp at h0
  -- h0 : exp(0) = 0, i.e., 1 = 0. ⊥
  linarith [Real.exp_pos (0:ℝ)]

-- F14(x,c)=exp(x+log(c))=c·exp(x). At x=0: c=0. Then F14(1,0)=0≠−1. ⊥
theorem N_F14_x_ne_neg : ¬ ∃ c : ℝ, ∀ x : ℝ, Real.exp (x + Real.log c) = -x := by
  intro ⟨c, h⟩
  have h0 := h 0; simp at h0
  -- h0 : exp(log c) = 0. But exp is always positive. ⊥
  linarith [Real.exp_pos (Real.log c)]

-- F15(x,c)=exp(x+log(−c)). exp is always positive, so exp(...)≠−x for x>0.
-- At x=1: exp(...) > 0 > −1. ⊥
theorem N_F15_x_ne_neg : ¬ ∃ c : ℝ, ∀ x : ℝ, Real.exp (x + Real.log (-c)) = -x := by
  intro ⟨c, h⟩
  have h1 := h 1; simp at h1; linarith [Real.exp_pos (1 + Real.log (-c))]

-- F16(x,c)=exp(log(x)+log(c))=x·c for x>0 (log(x)=0 for x≤0 by convention).
-- At x=1: exp(0+log(c))=exp(log(c))>0≠−1. ⊥ (exp always positive)
theorem N_F16_x_ne_neg : ¬ ∃ c : ℝ, ∀ x : ℝ, Real.exp (Real.log x + Real.log c) = -x := by
  intro ⟨c, h⟩
  have h1 := h 1; simp [Real.log_one] at h1
  linarith [Real.exp_pos (Real.log c)]

-- ================================================================
-- Section 2: op(c, x) ≠ −x  for all c  (x in second position)
-- ================================================================

-- F5(c,x)=exp(x)−log(c). Same as F1(x,c). ⊥
theorem N_F5_cx_ne_neg : ¬ ∃ c : ℝ, ∀ x : ℝ, Real.exp x - Real.log c = -x := N_F1_x_ne_neg

-- F6(c,x)=exp(−x)−log(c). Same as F3(x,c). ⊥
theorem N_F6_cx_ne_neg : ¬ ∃ c : ℝ, ∀ x : ℝ, Real.exp (-x) - Real.log c = -x := N_F3_x_ne_neg

-- F7(c,x)=exp(x)−log(−c). Same as F2. ⊥
theorem N_F7_cx_ne_neg : ¬ ∃ c : ℝ, ∀ x : ℝ, Real.exp x - Real.log (-c) = -x := N_F2_x_ne_neg

-- F8(c,x)=exp(−x)−log(−c). Same as F4. ⊥
theorem N_F8_cx_ne_neg : ¬ ∃ c : ℝ, ∀ x : ℝ, Real.exp (-x) - Real.log (-c) = -x := N_F4_x_ne_neg

-- For F1 with x in second position: F1(c,x)=exp(c)−log(x).
-- At x=1: exp(c)−0=exp(c)=−1. But exp always positive. ⊥
theorem N_F1_cx_ne_neg : ¬ ∃ c : ℝ, ∀ x : ℝ, Real.exp c - Real.log x = -x := by
  intro ⟨c, h⟩
  have h1 := h 1; simp [Real.log_one] at h1; linarith [Real.exp_pos c]

-- F2(c,x)=exp(c)−log(−x). At x=−1: exp(c)−log(1)=exp(c)=1. At x=−2: exp(c)−log(2)=2.
-- So exp(c)=1 and exp(c)=2+log(2). But exp(c)=1 → log(2)=−1 → contradiction log(2)>0.
theorem N_F2_cx_ne_neg : ¬ ∃ c : ℝ, ∀ x : ℝ, Real.exp c - Real.log (-x) = -x := by
  intro ⟨c, h⟩
  have hm1 := h (-1); simp [Real.log_one] at hm1  -- exp(c) = 1
  have hm2 := h (-2); simp at hm2                  -- exp(c) − log(2) = 2
  linarith [log2_pos]

-- F3(c,x)=exp(−c)−log(x). At x=1: exp(−c)=−1. But exp>0. ⊥
theorem N_F3_cx_ne_neg : ¬ ∃ c : ℝ, ∀ x : ℝ, Real.exp (-c) - Real.log x = -x := by
  intro ⟨c, h⟩
  have h1 := h 1; simp [Real.log_one] at h1; linarith [Real.exp_pos (-c)]

-- F4(c,x)=exp(−c)−log(−x). At x=−1: exp(−c)=1. At x=−2: exp(−c)−log(2)=2. So log(2)=−1. ⊥
theorem N_F4_cx_ne_neg : ¬ ∃ c : ℝ, ∀ x : ℝ, Real.exp (-c) - Real.log (-x) = -x := by
  intro ⟨c, h⟩
  have hm1 := h (-1); simp [Real.log_one] at hm1
  have hm2 := h (-2); simp at hm2
  linarith [log2_pos]

-- F9(c,x)=c−log(x). At x=1: c=−1. At x=2: −1−log(2)=−2→log(2)=1→exp(1)=2. ⊥
theorem N_F9_cx_ne_neg : ¬ ∃ c : ℝ, ∀ x : ℝ, c - Real.log x = -x := by
  intro ⟨c, h⟩
  have h1 := h 1; simp [Real.log_one] at h1  -- c = −1
  have h2 := h 2; simp at h2                  -- c − log 2 = −2
  have hlog : Real.log 2 = 1 := by linarith
  have hexp : Real.exp 1 = 2 := by
    have := Real.exp_log (show (0:ℝ) < 2 by norm_num); rw [hlog] at this; linarith
  linarith [e_gt_two]

-- F10(c,x)=c−log(−x). At x=−1: c=1. At x=−2: 1−log(2)=2→log(2)=−1. ⊥
theorem N_F10_cx_ne_neg : ¬ ∃ c : ℝ, ∀ x : ℝ, c - Real.log (-x) = -x := by
  intro ⟨c, h⟩
  have hm1 := h (-1); simp [Real.log_one] at hm1  -- c = 1
  have hm2 := h (-2); simp at hm2                  -- c − log 2 = 2
  linarith [log2_pos]

-- F11(c,x)=log(exp(c)+x). At x=0: log(exp(c))=c=0. At x=1: log(exp(0)+1)=log(2)=−1. ⊥
theorem N_F11_cx_ne_neg : ¬ ∃ c : ℝ, ∀ x : ℝ, Real.log (Real.exp c + x) = -x := by
  intro ⟨c, h⟩
  have h0 := h 0; simp at h0  -- log(exp c) = 0, so exp c = 1, so c = 0
  have hc : c = 0 := by
    have hpos : (0:ℝ) < Real.exp c := Real.exp_pos c
    rw [add_zero] at h0
    have := Real.log_eq_one_iff_exp_eq.mp  -- actually just use exp(log(exp c)) = exp c
    rw [Real.log_exp] at h0; exact h0
  have h1 := h 1; rw [hc] at h1; simp [Real.exp_zero] at h1
  -- log(1+1) = log 2 = −1. But log 2 > 0. ⊥
  linarith [log2_pos]

-- F12(c,x)=log(exp(c)−x). At x=0: log(exp(c))=c=0. At x=1: log(exp(0)−1)=log(0)=−1.
-- But log(0) = 0 in Lean/Mathlib, so 0 = −1. ⊥
theorem N_F12_cx_ne_neg : ¬ ∃ c : ℝ, ∀ x : ℝ, Real.log (Real.exp c - x) = -x := by
  intro ⟨c, h⟩
  have h0 := h 0; simp [Real.log_exp] at h0  -- c = 0
  have h1 := h 1; rw [h0] at h1; simp [Real.exp_zero] at h1
  -- log(1 − 1) = log(0) = 0 (Lean convention) but eq says = −1. ⊥
  simp [Real.log_zero] at h1; linarith

-- F13(c,x)=exp(c·log(x))=x^c. At x=0: exp(0)=1=0 (neg(0)=0). ⊥ (1≠0)
theorem N_F13_cx_ne_neg : ¬ ∃ c : ℝ, ∀ x : ℝ, Real.exp (c * Real.log x) = -x := by
  intro ⟨c, h⟩
  have h0 := h 0; simp at h0; linarith [Real.exp_pos (0:ℝ)]

-- F14(c,x)=exp(c+log(x))=x·exp(c). x·exp(c)=−x → exp(c)=−1. But exp>0. ⊥
theorem N_F14_cx_ne_neg : ¬ ∃ c : ℝ, ∀ x : ℝ, Real.exp (c + Real.log x) = -x := by
  intro ⟨c, h⟩
  have h1 := h 1; simp [Real.log_one, add_zero] at h1
  linarith [Real.exp_pos c]

-- F15(c,x)=exp(c+log(−x)). At x=−1: exp(c+log(1))=exp(c)=1. At x=−2: exp(c+log(2))=2.
-- exp(c)=1 and exp(c)·exp(log 2)=2 → exp(log 2)=2 → log 2 is log base e of 2 = 1 exactly?
-- exp(log 2) = 2 is TRUE (that's the definition). So exp(c)*2=2 → exp(c)=1 → c=0.
-- But F15(0,x)=exp(0+log(−x))=exp(log(−x))=−x for x<0? Real.exp(Real.log(−x))=−x when −x>0, i.e., x<0.
-- For x>0: F15(0,x)=exp(log(−x)) and log(−x)=log of negative = 0 by Lean convention.
-- So F15(0,x)=exp(0)=1≠−x for x≠−1.
-- Witness: x=1: F15(0,1)=exp(0+log(−1))=exp(0+0)=1≠−1. ⊥
theorem N_F15_cx_ne_neg : ¬ ∃ c : ℝ, ∀ x : ℝ, Real.exp (c + Real.log (-x)) = -x := by
  intro ⟨c, h⟩
  have h1 := h 1; simp at h1; linarith [Real.exp_pos (c + Real.log (-1))]

-- F16(c,x)=exp(log(c)+log(x)). At x=1: exp(log(c)+0)=exp(log(c))>0≠−1. ⊥
theorem N_F16_cx_ne_neg : ¬ ∃ c : ℝ, ∀ x : ℝ, Real.exp (Real.log c + Real.log x) = -x := by
  intro ⟨c, h⟩
  have h1 := h 1; simp [Real.log_one] at h1
  linarith [Real.exp_pos (Real.log c)]

-- ================================================================
-- Main theorem: neg is not 1-node computable
-- ================================================================

/-- A unary function f is F16 1-node computable if some F16 op with one constant
    computes it (either constant-first or constant-second). -/
def neg_one_node_computable : Prop :=
  (∃ c : ℝ, ∀ x : ℝ, Real.exp x - Real.log c = -x)                   ∨  -- F1(x,c)
  (∃ c : ℝ, ∀ x : ℝ, Real.exp x - Real.log (-c) = -x)                 ∨  -- F2(x,c)
  (∃ c : ℝ, ∀ x : ℝ, Real.exp (-x) - Real.log c = -x)                 ∨  -- F3(x,c)
  (∃ c : ℝ, ∀ x : ℝ, Real.exp (-x) - Real.log (-c) = -x)              ∨  -- F4(x,c)
  (∃ c : ℝ, ∀ x : ℝ, Real.exp x - Real.log c = -x)                    ∨  -- F5(c,x) same
  (∃ c : ℝ, ∀ x : ℝ, Real.exp (-x) - Real.log c = -x)                 ∨  -- F6(c,x) same
  (∃ c : ℝ, ∀ x : ℝ, Real.exp x - Real.log (-c) = -x)                 ∨  -- F7(c,x) same
  (∃ c : ℝ, ∀ x : ℝ, Real.exp (-x) - Real.log (-c) = -x)              ∨  -- F8(c,x) same
  (∃ c : ℝ, ∀ x : ℝ, x - Real.log c = -x)                             ∨  -- F9(x,c)
  (∃ c : ℝ, ∀ x : ℝ, x - Real.log (-c) = -x)                          ∨  -- F10(x,c)
  (∃ c : ℝ, ∀ x : ℝ, Real.log (Real.exp x + c) = -x)                  ∨  -- F11(x,c)
  (∃ c : ℝ, ∀ x : ℝ, Real.log (Real.exp x - c) = -x)                  ∨  -- F12(x,c)
  (∃ c : ℝ, ∀ x : ℝ, Real.exp (x * Real.log c) = -x)                  ∨  -- F13(x,c)
  (∃ c : ℝ, ∀ x : ℝ, Real.exp (x + Real.log c) = -x)                  ∨  -- F14(x,c)
  (∃ c : ℝ, ∀ x : ℝ, Real.exp (x + Real.log (-c)) = -x)               ∨  -- F15(x,c)
  (∃ c : ℝ, ∀ x : ℝ, Real.exp (Real.log x + Real.log c) = -x)         ∨  -- F16(x,c)
  (∃ c : ℝ, ∀ x : ℝ, Real.exp c - Real.log x = -x)                    ∨  -- F1(c,x)
  (∃ c : ℝ, ∀ x : ℝ, Real.exp c - Real.log (-x) = -x)                 ∨  -- F2(c,x)
  (∃ c : ℝ, ∀ x : ℝ, Real.exp (-c) - Real.log x = -x)                 ∨  -- F3(c,x)
  (∃ c : ℝ, ∀ x : ℝ, Real.exp (-c) - Real.log (-x) = -x)              ∨  -- F4(c,x)
  (∃ c : ℝ, ∀ x : ℝ, c - Real.log x = -x)                             ∨  -- F9(c,x)
  (∃ c : ℝ, ∀ x : ℝ, c - Real.log (-x) = -x)                          ∨  -- F10(c,x)
  (∃ c : ℝ, ∀ x : ℝ, Real.log (Real.exp c + x) = -x)                  ∨  -- F11(c,x)
  (∃ c : ℝ, ∀ x : ℝ, Real.log (Real.exp c - x) = -x)                  ∨  -- F12(c,x)
  (∃ c : ℝ, ∀ x : ℝ, Real.exp (c * Real.log x) = -x)                  ∨  -- F13(c,x)
  (∃ c : ℝ, ∀ x : ℝ, Real.exp (c + Real.log x) = -x)                  ∨  -- F14(c,x)
  (∃ c : ℝ, ∀ x : ℝ, Real.exp (c + Real.log (-x)) = -x)               ∨  -- F15(c,x)
  (∃ c : ℝ, ∀ x : ℝ, Real.exp (Real.log c + Real.log x) = -x)            -- F16(c,x)

/-- **Main result**: SB(neg) ≥ 2. Negation cannot be computed by a single F16 node. -/
theorem SB_neg_ge_two : ¬ neg_one_node_computable := by
  unfold neg_one_node_computable
  push_neg
  exact ⟨N_F1_x_ne_neg, N_F2_x_ne_neg, N_F3_x_ne_neg, N_F4_x_ne_neg,
         N_F5_cx_ne_neg, N_F6_cx_ne_neg, N_F7_cx_ne_neg, N_F8_cx_ne_neg,
         N_F9_x_ne_neg, N_F10_x_ne_neg, N_F11_x_ne_neg, N_F12_x_ne_neg,
         N_F13_x_ne_neg, N_F14_x_ne_neg, N_F15_x_ne_neg, N_F16_x_ne_neg,
         N_F1_cx_ne_neg, N_F2_cx_ne_neg, N_F3_cx_ne_neg, N_F4_cx_ne_neg,
         N_F9_cx_ne_neg, N_F10_cx_ne_neg, N_F11_cx_ne_neg, N_F12_cx_ne_neg,
         N_F13_cx_ne_neg, N_F14_cx_ne_neg, N_F15_cx_ne_neg, N_F16_cx_ne_neg⟩
