// Source of truth for the /proofs page and /proofs.lean.txt dump.
// Every `source` is a verbatim copy from monogate-lean/MonogateEML/*.lean.
// Line numbers point at the first line of the theorem in that file.

export interface Flagship {
  name: string;
  line: number;
  hook: string;
  source: string;
  hasSorry?: boolean;
}

export interface ProofFile {
  file: string;
  thm: string;
  what: string;
  original: number;
  total: number;
  sorries: number;
  ok: boolean;
  flagships: Flagship[];
}

export const leanRepo = 'https://github.com/almaguer1986/monogate-lean';
export const leanBranch = 'master';

export const ghFile = (file: string, line?: number): string =>
  `${leanRepo}/blob/${leanBranch}/MonogateEML/${file}${line ? `#L${line}` : ''}`;

export const files: ProofFile[] = [
  {
    file: 'AddLowerBound.lean',
    thm: 'SB(add) ≥ 2',
    what: 'No single F16 operator computes addition over all ℝ². Exhaustive witness over all 16 operators.',
    original: 2, total: 37, sorries: 0, ok: true,
    flagships: [
      {
        name: 'no_f16_computes_add',
        line: 269,
        hook: 'Direct enumeration: every one of the 16 F-operators is refuted by a concrete witness pair. The proof is a 16-branch case split.',
        source: `theorem no_f16_computes_add :
    ∀ op ∈ f16_ops, ¬ (∀ x y : ℝ, op x y = x + y) := by
  intro op hmem
  simp only [f16_ops, List.mem_cons, List.mem_nil_iff, or_false] at hmem
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
  · exact F16fn_ne_add`
      },
      {
        name: 'SB_add_ge_two',
        line: 328,
        hook: 'The headline: SB(add) ≥ 2. Addition cannot be computed by any single F16 node.',
        source: `/-- **Main result**: SB(add) ≥ 2 — addition cannot be computed by a single F16 node. -/
theorem SB_add_ge_two : ¬ one_node_computable (· + ·) :=
  add_not_one_node_computable`
      }
    ]
  },
  {
    file: 'SubLowerBound.lean',
    thm: 'SB(sub) ≥ 2',
    what: 'No single F16 operator computes subtraction over all ℝ².',
    original: 2, total: 34, sorries: 0, ok: true,
    flagships: [
      {
        name: 'SB_sub_ge_two',
        line: 163,
        hook: 'SB(sub) ≥ 2. Chains the 16-case enumeration (no_f16_computes_sub) into the one-node-computable impossibility.',
        source: `/-- **Main result**: SB(sub) ≥ 2 — subtraction cannot be computed by a single F16 node. -/
theorem SB_sub_ge_two : ¬ one_node_computable_sub (· - ·) := by
  intro ⟨op, hmem, heq⟩
  exact no_f16_computes_sub op hmem (fun x y => (heq x y).symm)`
      }
    ]
  },
  {
    file: 'MulLowerBound.lean',
    thm: 'SB(mul) ≥ 2 (general)',
    what: 'No single F16 operator computes multiplication over all ℝ². (Over positives, mul is 1n — see UpperBounds.)',
    original: 2, total: 37, sorries: 0, ok: true,
    flagships: [
      {
        name: 'SB_mul_ge_two',
        line: 160,
        hook: 'SB(mul, general) ≥ 2. The general-domain lower bound that sits opposite the 1-node positive-domain witness.',
        source: `/-- **Main result**: SB(mul) ≥ 2 — multiplication cannot be computed by a single F16 node
    for all real inputs. -/
theorem SB_mul_ge_two : ¬ mul_one_node_computable (· * ·) := by
  intro ⟨op, hmem, heq⟩
  exact no_f16_computes_mul op hmem (fun x y => (heq x y).symm)`
      }
    ]
  },
  {
    file: 'DivLowerBound.lean',
    thm: 'SB(div) ≥ 2 (general)',
    what: 'No single F16 operator computes division over all ℝ².',
    original: 2, total: 36, sorries: 0, ok: true,
    flagships: [
      {
        name: 'SB_div_ge_two',
        line: 161,
        hook: 'SB(div, general) ≥ 2. The 1-node positive-domain witness lives in DivLowerBound3 (2-node upper bound).',
        source: `/-- **Main result**: SB(div) ≥ 2 — division cannot be computed by a single F16 node
    for all real inputs. -/
theorem SB_div_ge_two : ¬ div_one_node_computable (· / ·) := by
  intro ⟨op, hmem, heq⟩
  exact no_f16_computes_div op hmem (fun x y => (heq x y).symm)`
      }
    ]
  },
  {
    file: 'DivLowerBound3.lean',
    thm: 'No exp-outer 2-node div + positive-domain 2-node upper bound',
    what: 'Rules out exp-type outer 2-node circuits for division (structural positivity argument), and exhibits the matching 2-node construction on (0,∞)².',
    original: 2, total: 21, sorries: 0, ok: true,
    flagships: [
      {
        name: 'no_exp_outer_2node_div',
        line: 98,
        hook: 'T_DIV_EXP_OUTER_LB — covers all 1024 circuits with F13/F14/F15/F16 as outer node. The wedge: these always return exp(...) > 0, but x/y at (−1, 2) is −1/2 < 0.',
        source: `/-- **T_DIV_EXP_OUTER_LB** — No 2-node F16 circuit with exp-type outer operator
    (F13, F14, F15, or F16) computes general division on ℝ².

    Covers all 1024 such circuits (4 outer ops × 16 inner ops × 16 wire configs).
    The g and h parameters encode any inner F16 operator applied to any wire selection from {x,y}. -/
theorem no_exp_outer_2node_div
    (outer g h : ℝ → ℝ → ℝ)
    (houter : outer ∈ ([D_F13, D_F14, D_F15, D_F16] : List (ℝ → ℝ → ℝ))) :
    ¬ (∀ x y : ℝ, outer (g x y) (h x y) = x / y) := by
  simp only [List.mem_cons, List.mem_nil_iff, or_false] at houter
  rcases houter with rfl | rfl | rfl | rfl
  · exact no_F13_outer_2node_div g h
  · exact no_F14_outer_2node_div g h
  · exact no_F15_outer_2node_div g h
  · exact no_F16fn_outer_2node_div g h`
      },
      {
        name: 'div_two_node_pos_domain',
        line: 119,
        hook: 'T_DIV_TWO_NODE_POS — the 2-node upper bound: D_F16(x, D_F13(−1, y)) = x/y for x, y > 0. Exactly one wire of reciprocal, exactly one wire of product.',
        source: `/-- **T_DIV_TWO_NODE_POS** — Division is computable by a 2-node F16 circuit on (0,∞)²:
      D_F16(x, D_F13(−1, y)) = x/y  for all x, y > 0.

    Proof:
      D_F13(−1, y) = exp(−log y) = y⁻¹
      D_F16(x, y⁻¹) = exp(log x + log y⁻¹) = exp(log x − log y) = exp(log(x/y)) = x/y. -/
theorem div_two_node_pos_domain (x y : ℝ) (hx : 0 < x) (hy : 0 < y) :
    D_F16 x (D_F13 (-1) y) = x / y := by
  have hinv : D_F13 (-1 : ℝ) y = y⁻¹ := by
    unfold D_F13
    rw [show (-1 : ℝ) * Real.log y = -(Real.log y) from by ring]
    rw [Real.exp_neg, Real.exp_log hy]
  rw [hinv]
  unfold D_F16
  rw [show Real.log y⁻¹ = -(Real.log y) from Real.log_inv y]
  rw [Real.exp_add, Real.exp_log hx, Real.exp_neg, Real.exp_log hy]
  field_simp`
      }
    ]
  },
  {
    file: 'UpperBounds.lean',
    thm: 'Five positive-domain operations at 1 node',
    what: 'exp, mul, pow, recip, sqrt each admit a single-F16-node construction on x > 0.',
    original: 10, total: 186, sorries: 0, ok: true,
    flagships: [
      {
        name: 'mul_one_node_positive',
        line: 44,
        hook: 'Multiplication on positives: one F16 node. The identity exp(log x + log y) = x·y is three Mathlib rewrites.',
        source: `/-- Multiplication is a single F16 node on the positive domain:
    F16fn(x,y) = exp(log(x) + log(y)) = x · y for x,y > 0. -/
theorem mul_one_node_positive (x y : ℝ) (hx : 0 < x) (hy : 0 < y) :
    Real.exp (Real.log x + Real.log y) = x * y := by
  rw [Real.exp_add, Real.exp_log hx, Real.exp_log hy]`
      },
      {
        name: 'rpow_one_node_positive',
        line: 54,
        hook: 'Real power x^n as a single F13 node: exp(n · log x) = x^n for x > 0. Covers recip (n = −1), sqrt (n = 1/2), general powers.',
        source: `/-- Real power x^n is a single F16 node via EPL:
    F13(n, x) = exp(n · log(x)) = x^n for x > 0. -/
theorem rpow_one_node_positive (n x : ℝ) (hx : 0 < x) :
    Real.exp (n * Real.log x) = x ^ n := by
  rw [Real.rpow_def_of_pos hx]; ring_nf`
      },
      {
        name: 'ln_one_node_via_exl',
        line: 96,
        hook: 'ln via EXL: exp(0) · log(x) = log(x). The extended-EXL operator makes ln a single node, closing the SuperBEST 14n positive-domain count.',
        source: `/-- EXL identity: exp(0) * log(x) = log(x) for all real x.

    Justifies the SuperBEST 1-node accounting of \`ln(x)\` via the extended
    operator EXL(a, b) := exp(a) * log(b), with EXL(0, x) = log(x). -/
theorem ln_one_node_via_exl (x : ℝ) :
    Real.exp 0 * Real.log x = Real.log x := by
  rw [Real.exp_zero, one_mul]`
      }
    ]
  },
  {
    file: 'ModelAudit.lean',
    thm: 'v5.1 → v5.3 SuperBEST correction',
    what: 'sqrt via EPL(0.5, x) and mul via F16fn drop the positive-domain SuperBEST total to 14n (80.8% savings).',
    original: 6, total: 13, sorries: 0, ok: true,
    flagships: [
      {
        name: 'sqrt_is_one_node_positive',
        line: 53,
        hook: 'sqrt = EPL(0.5, x) = exp(0.5 · log x). Same mechanism as recip (−1) and pow. This is the witness that collapsed sqrt from 2n to 1n.',
        source: `/-- EPL(0.5, x) = exp(0.5 · log(x)) = x^(1/2) = sqrt(x) for x > 0.
    Same mechanism as pow = 1n and recip = 1n via the EPL/F13 primitive. -/
theorem sqrt_is_one_node_positive (x : ℝ) (hx : 0 < x) :
    Real.exp (0.5 * Real.log x) = Real.sqrt x := by
  rw [Real.sqrt_eq_rpow]
  simp [Real.rpow_def_of_pos hx]
  ring_nf`
      },
      {
        name: 'mul_is_one_node_positive',
        line: 65,
        hook: 'The ModelAudit companion to mul_one_node_positive (UpperBounds.lean:44). Duplicate statement, cross-referenced in the audit narrative.',
        source: `/-- F16fn(x,y) = exp(log(x) + log(y)) = x · y for x,y > 0.
    Multiplication is a single F16 node on the positive domain. -/
theorem mul_is_one_node_positive (x y : ℝ) (hx : 0 < x) (hy : 0 < y) :
    Real.exp (Real.log x + Real.log y) = x * y := by
  rw [Real.exp_add, Real.exp_log hx, Real.exp_log hy]`
      }
    ]
  },
  {
    file: 'EMLDepth.lean',
    thm: 'Depth hierarchy is strict',
    what: 'Euler gateway ceml(ix, 1) = exp(ix) as an EMLTree; EML-0 ⊊ EML-1 witnessed by exp being non-constant.',
    original: 10, total: 23, sorries: 0, ok: true,
    flagships: [
      {
        name: 'euler_identity',
        line: 60,
        hook: 'CEML-T5 — Euler\'s identity inside the EMLTree inductive type. The tree ceml(iπ, 1) evaluates to e^(iπ) = −1, so the tree +1 equals 0.',
        source: `/-- CEML-T5: Euler Identity (principal branch).
    ceml(iπ, 1) = exp(iπ) = -1, so ceml(iπ, 1) + 1 = 0. -/
theorem euler_identity :
    EMLTree.eval (.ceml (.const (Complex.I * Real.pi)) (.const 1)) 0 + 1 = 0 := by
  simp only [EMLTree.eval, Complex.log_one, sub_zero]
  rw [show Complex.I * ↑Real.pi = ↑Real.pi * Complex.I from mul_comm _ _,
      Complex.exp_pi_mul_I]
  norm_num`
      },
      {
        name: 'exp_not_constant',
        line: 82,
        hook: 'EML-0 ⊊ EML-1. The depth-1 tree computing exp cannot be constant, proved by evaluating at 0 and 1 and invoking Real.exp_one_gt_d9.',
        source: `/-- expTree is not constant (EML-0 ⊊ EML-1). -/
theorem exp_not_constant : ¬ (∃ c : ℂ, ∀ x, expTree.eval x = c) := by
  intro ⟨c, hc⟩
  have h0 : Complex.exp 0 = c := by simpa [expTree_eval] using hc 0
  have h1 : Complex.exp 1 = c := by simpa [expTree_eval] using hc 1
  have heq : Complex.exp (1 : ℂ) = 1 := by rw [h1, ← h0]; simp
  have hre : Real.exp 1 = 1 := by
    have := congr_arg Complex.re heq
    simp only [Complex.one_re] at this
    rwa [show (Complex.exp (1:ℂ)).re = Real.exp 1 from by
      have : (1:ℂ) = ((1:ℝ):ℂ) := by norm_cast
      rw [this, Complex.exp_ofReal_re]] at this
  linarith [Real.exp_one_gt_d9]`
      }
    ]
  },
  {
    file: 'EMLDuality.lean',
    thm: 'exp-log duality at fixed points',
    what: 'At any fixed point z* ∈ slitPlane of Complex.exp, the multiplier product (exp)\'(z*) · (log)\'(z*) equals 1.',
    original: 2, total: 18, sorries: 0, ok: true,
    flagships: [
      {
        name: 'exp_log_multiplier_product_at_fixed_point',
        line: 52,
        hook: 'PROP 02-B — the Blind Session 02 observation formalised. If exp(z) = z (a Lambert fixed point), then deriv(exp) · deriv(log) at z is exactly 1.',
        source: `/-- **PROP 02-B**: The multiplier product \`(exp)'(z) · (log)'(z)\` equals 1
    at any fixed point of \`exp\` lying in the slit plane (where \`log\` is
    differentiable).

    Empirically verified in Blind Session 02 for the Lambert fixed points
    \`z_k* = -W_k(-1)\`: they are all repelling under exp (|mult| = |z_k*| > 1)
    and attracting under log (|mult| = 1/|z_k*| < 1), with product exactly 1. -/
theorem exp_log_multiplier_product_at_fixed_point
    {z : ℂ} (hz : Complex.exp z = z) (hdom : z ∈ Complex.slitPlane) :
    deriv Complex.exp z * deriv Complex.log z = 1 := by
  have hne : z ≠ 0 := exp_fixed_point_ne_zero hz
  rw [deriv_exp_at, deriv_log_at hdom, hz]
  field_simp`
      }
    ]
  },
  {
    file: 'HyperbolicPreservation.lean',
    thm: 'Hyperbolic functions preserve ELC',
    what: 'sinh/cosh/tanh are arithmetic combinations of exp(±x); hyperbolic functions stay inside ELC(ℝ). Pythagorean witness at x = ln 2.',
    original: 3, total: 34, sorries: 0, ok: true,
    flagships: [
      {
        name: 'sinh_log_two',
        line: 47,
        hook: 'OBS 08-C — sinh(ln 2) = 3/4. One half of the 3-4-5 Pythagorean triple that lives on the hyperbolic unit curve at x = ln 2.',
        source: `/-- Numeric witness used in the session: \`sinh(ln 2) = 3/4\`.
    Part of the 3-4-5 Pythagorean-triple observation (OBS 08-C). -/
theorem sinh_log_two : Real.sinh (Real.log 2) = 3 / 4 := by
  rw [Real.sinh_eq, Real.exp_log (by norm_num : (2:ℝ) > 0), Real.exp_neg,
      Real.exp_log (by norm_num : (2:ℝ) > 0)]
  norm_num`
      },
      {
        name: 'pythagorean_triple_at_log_two',
        line: 60,
        hook: 'The 3-4-5 Pythagorean triple witnessed inside the hyperbolic identity cosh² − sinh² = 1 at x = ln 2. (5/4)² − (3/4)² = 1.',
        source: `/-- The 3-4-5 Pythagorean triple witness at \`x = ln 2\` in the hyperbolic
    identity (OBS 08-C, proved). -/
theorem pythagorean_triple_at_log_two :
    (Real.cosh (Real.log 2)) ^ 2 - (Real.sinh (Real.log 2)) ^ 2 = 1 := by
  exact cosh_sq_sub_sinh_sq (Real.log 2)`
      }
    ]
  },
  {
    file: 'SelfMapConjugacy.lean',
    thm: 'EAL ↔ EXL and EML ↔ EDL self-maps conjugate via exp',
    what: 'Prop A-1 from the Blind omnibus — additive and multiplicative F16 self-maps are topologically conjugate via the real exponential.',
    original: 4, total: 12, sorries: 0, ok: true,
    flagships: [
      {
        name: 'eal_exl_conjugacy',
        line: 31,
        hook: 'g ∘ exp = exp ∘ f on (0,∞), where f(x) = exp(x) + ln(x) is the EAL self-map and g(y) = exp(y) · ln(y) is the EXL self-map.',
        source: `/-- **EAL↔EXL conjugacy via exp.** Let \`f(x) = exp(x) + ln(x)\` be the EAL
self-map (the value of the F16 operator \`EAL\` evaluated on the diagonal)
and \`g(y) = exp(y) · ln(y)\` the EXL self-map. Then on the positive reals,
\`g(exp(x)) = exp(f(x))\`.

This is the identity \`exp(exp(x) + ln(x)) = exp(exp(x)) · x = exp(exp(x)) · ln(exp(x))\`.
-/
theorem eal_exl_conjugacy (x : ℝ) (hx : 0 < x) :
    Real.exp (Real.exp x) * Real.log (Real.exp x)
      = Real.exp (Real.exp x + Real.log x) := by
  rw [Real.exp_add, Real.log_exp, Real.exp_log hx]`
      },
      {
        name: 'eml_edl_conjugacy',
        line: 42,
        hook: 'The subtractive / divisive partner: exp(y) / ln(y) and exp(x) − ln(x) conjugate via exp on (0,∞) \\ {1}.',
        source: `/-- **EML↔EDL conjugacy via exp.** Let \`f(x) = exp(x) − ln(x)\` be the EML
self-map and \`g(y) = exp(y) / ln(y)\` the EDL self-map. Then on the
positive reals with \`x ≠ 1\` (so \`ln(x) ≠ 0\`), \`g(exp(x)) = exp(f(x))\`.

This is the identity \`exp(exp(x) − ln(x)) = exp(exp(x)) / x = exp(exp(x)) / ln(exp(x))\`.
-/
theorem eml_edl_conjugacy (x : ℝ) (hx : 0 < x) (hx1 : x ≠ 1) :
    Real.exp (Real.exp x) / Real.log (Real.exp x)
      = Real.exp (Real.exp x - Real.log x) := by
  have h_log_ne : Real.log x ≠ 0 := Real.log_ne_zero_of_pos_of_ne_one hx hx1
  rw [Real.exp_sub, Real.log_exp, Real.exp_log hx]`
      }
    ]
  },
  {
    file: 'InfiniteZerosBarrier.lean',
    thm: 'T01 (partial) — sin ∉ EML, substrate proved',
    what: 'sin has no finite real EML tree. Parts A (infinite zeros), B (analytic ⇒ finite zeros on compacts), C (EML trees are real-analytic), and C\' (depth-1 closed) all at 0 sorries. The depth-k zero-count bound (sin_not_in_eml, sin_not_in_real_EML_k) awaits o-minimal structure theory.',
    original: 4, total: 10, sorries: 2, ok: false,
    flagships: [
      {
        name: 'analytic_finite_zeros_compact',
        line: 92,
        hook: 'Part B of T01 — a non-zero real-analytic function on [a,b] has finitely many zeros there. Bolzano-Weierstrass + Mathlib\'s analytic identity theorem.',
        source: `/-- A non-zero real-analytic function on [a,b] has finitely many zeros.

Proof: If the zero set Z is infinite, Bolzano-Weierstrass gives an accumulation point
x₀ ∈ [a,b] (Set.Infinite.exists_accPt_of_subset_isCompact). Then f is frequently zero
near x₀. By the analytic identity theorem f = 0 on all of [a,b], contradicting hf_nonzero. -/
lemma analytic_finite_zeros_compact (f : ℝ → ℝ) (a b : ℝ) (hab : a < b)
    (hf_analytic : AnalyticOnNhd ℝ f (Set.Icc a b))
    (hf_nonzero : ∃ x ∈ Set.Ioo a b, f x ≠ 0) :
    Set.Finite {x ∈ Set.Icc a b | f x = 0} := by
  by_contra h_not_fin
  have h_inf : Set.Infinite {x ∈ Set.Icc a b | f x = 0} := h_not_fin
  obtain ⟨x₀, hx₀_mem, hx₀_acc⟩ :=
    h_inf.exists_accPt_of_subset_isCompact isCompact_Icc (Set.sep_subset _ _)
  have haccf : AccPt x₀ (𝓟 {z | f z = 0}) :=
    hx₀_acc.mono (Filter.principal_mono.mpr fun y hy => hy.2)
  have hfreq : ∃ᶠ z in 𝓝[≠] x₀, f z = 0 :=
    frequently_iff_neBot.mpr haccf
  have heqon : Set.EqOn f 0 (Set.Icc a b) :=
    hf_analytic.eqOn_zero_of_preconnected_of_frequently_eq_zero
      isPreconnected_Icc hx₀_mem hfreq
  obtain ⟨x₁, hx₁_mem, hfx₁⟩ := hf_nonzero
  exact hfx₁ (heqon (Set.Ioo_subset_Icc_self hx₁_mem))`
      },
      {
        name: 'eml_tree_analytic',
        line: 195,
        hook: 'Part C of T01 — every well-formed real EML tree is real-analytic on (0, ∞). Lifted from ℝ→ℂ analyticity via Complex.reCLM.',
        source: `/-- Every well-formed real EML tree function is real-analytic on (0, ∞).

Requires WellFormedPos: all log arguments must evaluate to positive reals on (0,∞).
This is necessary — without it the ceml/ceml slit-plane condition can fail.

Derived from \`eml_tree_eval_analyticOnNhd\` (ℝ→ℂ analyticity of t.eval ∘ (↑·))
by composing with Complex.reCLM (continuous ℝ-linear map ℂ →L[ℝ] ℝ). (0 sorry) -/
lemma eml_tree_analytic (t : EMLTree)
    (hwf : ∀ x ∈ Set.Ioi 0, t.WellFormedPos x) :
    AnalyticOnNhd ℝ t.evalReal (Set.Ioi 0) := by
  have hcomplex := eml_tree_eval_analyticOnNhd t hwf
  have heq : t.evalReal = Complex.reCLM ∘ (fun x : ℝ => t.eval (↑x : ℂ)) := by
    ext x; simp [EMLTree.evalReal, Complex.reCLM]
  rw [heq]
  exact (Complex.reCLM.analyticOnNhd Set.univ).comp hcomplex (Set.mapsTo_univ _ _)`
      },
      {
        name: 'sin_not_in_eml',
        line: 323,
        hasSorry: true,
        hook: 'The honest partial. T01 at depth k. The final step — "EML-k trees have at most B(k) real zeros" — needs o-minimal structure theory (Wilkie 1996). Documented as a single sorry, not hidden.',
        source: `/-- T01 (Infinite Zeros Barrier): sin is not representable by any finite EML tree.

Sorry: quantitative zero-count bound needed — EML-k trees have ≤ B(k) zeros on ℝ.
This requires o-minimal structure theory (ℝ_exp is o-minimal). -/
theorem sin_not_in_eml (k : ℕ) :
    ∀ t : EMLTree, t.depth ≤ k →
      ¬ (∀ x : ℝ, t.evalReal x = Real.sin x) := by
  sorry`
      }
    ]
  }
];

// Aggregate counters (derived, so the page doesn't have to reproduce them).
export const aggregates = {
  verifiedOriginal: files.reduce((n, f) => n + f.original, 0),
  totalStatements: files.reduce((n, f) => n + f.total, 0),
  mathlibWrappers: 173,
  supportingLemmas: 237,
  cleanFiles: files.filter(f => f.sorries === 0).length,
  partialFiles: files.filter(f => f.sorries > 0).length,
  sorriesTotal: files.reduce((n, f) => n + f.sorries, 0),
  flagshipCount: files.reduce((n, f) => n + f.flagships.length, 0),
  totalFiles: files.length,
} as const;
