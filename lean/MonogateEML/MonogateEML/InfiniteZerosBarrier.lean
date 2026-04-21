-- MonogateEML/InfiniteZerosBarrier.lean
import MonogateEML.EMLDepth
import Mathlib.Analysis.Analytic.Basic
import Mathlib.Analysis.Analytic.IsolatedZeros
import Mathlib.Data.Real.Basic
import Mathlib.Topology.Compactness.Compact
import Mathlib.Topology.Order.IntermediateValue

/-!
# Infinite Zeros Barrier (T01)

**Statement**: Real EML(ℝ) trees have at most finitely many zeros on any closed bounded
interval on which they are real-analytic.  sin(x) has infinitely many zeros.
Therefore sin(x) ∉ EML(ℝ).

## Proof strategy

Part A (proved here, 0 sorry):
  sin(x) has infinitely many zeros — explicitly, sin(nπ) = 0 for all n ∈ ℤ.

Part B (0 sorry — analytic_finite_zeros_compact):
  A non-zero AnalyticOnNhd function on [a,b] has finitely many zeros.
  Proved via Bolzano-Weierstrass + AnalyticOnNhd identity theorem.

Part C (1 sorry — eml_tree_analytic):
  Every EML tree is AnalyticOnNhd on (0,∞).
  Needs: AnalyticOnNhd.comp for exp and log.

Part D (1 sorry — sin_not_in_eml):
  sin ∉ EML_k. Needs quantitative zero-count bound (o-minimal theory).

## Sorry census: 2 remaining (eml_tree_analytic, sin_not_in_eml)
-/

open Real Filter Set

-- ===================================================================
-- Part A: sin(x) has infinitely many zeros (0 sorry)
-- ===================================================================

/-- sin(n · π) = 0 for every integer n. -/
theorem sin_int_pi_zero (n : ℤ) : Real.sin (n * Real.pi) = 0 :=
  Real.sin_int_mul_pi n

/-- sin has infinitely many zeros: the sequence nπ gives distinct zeros for all n ∈ ℤ. -/
theorem sin_has_infinitely_many_zeros :
    Set.Infinite {x : ℝ | Real.sin x = 0} := by
  have hrange : Set.range (fun n : ℤ => (n : ℝ) * Real.pi) ⊆ {x : ℝ | Real.sin x = 0} :=
    fun _ ⟨n, hn⟩ => hn ▸ sin_int_pi_zero n
  have hinj : Function.Injective (fun n : ℤ => (n : ℝ) * Real.pi) := by
    intro m n hmn
    have hpi : Real.pi ≠ 0 := Real.pi_ne_zero
    exact_mod_cast mul_right_cancel₀ hpi (by exact_mod_cast hmn : (m : ℝ) * Real.pi = n * Real.pi)
  exact (Set.infinite_range_of_injective hinj).mono hrange

-- ===================================================================
-- Part B: Analytic non-zero functions have finitely many zeros (0 sorry)
-- ===================================================================

/-- A non-zero real-analytic function on [a,b] has finitely many zeros.

Proof: If the zero set Z is infinite, Bolzano-Weierstrass gives an accumulation point
x₀ ∈ [a,b] (Set.Infinite.exists_accPt_of_subset_isCompact). Then f is frequently zero
near x₀. By the analytic identity theorem (AnalyticOnNhd.eqOn_zero_of_preconnected_of
_frequently_eq_zero) f = 0 on all of [a,b], contradicting hf_nonzero. -/
lemma analytic_finite_zeros_compact (f : ℝ → ℝ) (a b : ℝ) (hab : a < b)
    (hf_analytic : AnalyticOnNhd ℝ f (Set.Icc a b))
    (hf_nonzero : ∃ x ∈ Set.Ioo a b, f x ≠ 0) :
    Set.Finite {x ∈ Set.Icc a b | f x = 0} := by
  by_contra h_inf
  rw [Set.not_finite] at h_inf
  -- Bolzano-Weierstrass: infinite subset of compact [a,b] has an accumulation point
  obtain ⟨x₀, hx₀_mem, hx₀_acc⟩ :=
    h_inf.exists_accPt_of_subset_isCompact isCompact_Icc (Set.sep_subset _ _)
  -- Lift AccPt from the sep-set to the f-zero set
  have haccf : AccPt x₀ (𝓟 {z | f z = 0}) :=
    hx₀_acc.mono (Filter.principal_mono.mpr fun y hy => hy.2)
  -- AccPt (𝓟 {f=0}) = (𝓝[≠] ⊓ 𝓟 {f=0}).NeBot = ∃ᶠ in 𝓝[≠]
  have hfreq : ∃ᶠ z in 𝓝[≠] x₀, f z = 0 :=
    frequently_iff_neBot.mpr haccf
  -- Identity theorem: f analytic + frequently zero at x₀ ∈ [a,b] → f = 0 on [a,b]
  have heqon : Set.EqOn f 0 (Set.Icc a b) :=
    hf_analytic.eqOn_zero_of_preconnected_of_frequently_eq_zero
      isPreconnected_Icc hx₀_mem hfreq
  -- Contradiction: hf_nonzero says f ≠ 0 somewhere in (a,b) ⊆ [a,b]
  obtain ⟨x₁, hx₁_mem, hfx₁⟩ := hf_nonzero
  exact hfx₁ (heqon (Set.Ioo_subset_Icc_self hx₁_mem))

-- ===================================================================
-- Part C: EML tree functions are real-analytic on (0, ∞) (1 sorry)
-- ===================================================================

open EMLTree in
/-- Every real EML tree function is real-analytic on (0, ∞).

Sorry: the proof goes by induction on t using:
  • analyticOnNhd_const, analyticOnNhd_id for base cases
  • AnalyticOnNhd.sub and AnalyticOnNhd.comp for the ceml step
  • Complex.analyticOnNhd_exp (entire) and Real.analyticOnNhd_log on Ioi 0
The difficulty is tracking that t2.eval maps (0,∞) to a domain where Complex.log is analytic.
Required import: Mathlib.Analysis.Analytic.Composition -/
lemma eml_tree_analytic (t : EMLTree) :
    AnalyticOnNhd ℝ t.evalReal (Set.Ioi 0) := by
  sorry

-- ===================================================================
-- Part D: sin ∉ EML_k (1 sorry — genuine mathematical challenge)
-- ===================================================================

open EMLTree in
/-- T01 (Infinite Zeros Barrier): sin is not representable by any finite EML tree.

Sorry: To convert analytic_finite_zeros_compact into a contradiction with sin's infinite
zeros, we need a QUANTITATIVE bound: EML-k trees have at most B(k) zeros on ℝ total.
Then sin (with arbitrarily many zeros) exceeds B(k). This bound requires either:
  (a) O-minimal structure theory (ℝ_exp is o-minimal),
  (b) Direct inductive bound on EML-k zero sets.
Both are beyond current Lean formalization scope. -/
theorem sin_not_in_eml (k : ℕ) :
    ∀ t : EMLTree, t.depth ≤ k →
      ¬ (∀ x : ℝ, t.evalReal x = Real.sin x) := by
  sorry

-- ===================================================================
-- Verified: sin(x) has zeros at all integer multiples of π
-- ===================================================================

example : Real.sin 0 = 0 := Real.sin_zero
example : Real.sin Real.pi = 0 := Real.sin_pi
example : Real.sin (2 * Real.pi) = 0 := by
  rw [show (2 : ℝ) * Real.pi = Real.pi + Real.pi from by ring]
  rw [Real.sin_add, Real.sin_pi, Real.cos_pi]; ring
example : Real.sin (3 * Real.pi) = 0 := by
  have := sin_int_pi_zero 3; push_cast at this; exact this
