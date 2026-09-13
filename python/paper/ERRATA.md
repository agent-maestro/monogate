# Errata for python/paper/

The papers in this directory are kept as written. This file lists the claims in them that
monogate.org has withdrawn or corrected: where each claim appears, what changed, and the page that
carries the correction. It covers the papers the site cites or has corrected, as of 2026-09-13. Papers
the site does not rely on were not audited.

"Lean" below means a theorem registered in `blog/scripts/lean_claims.json` and re-checked before every
deploy. The current tier and evidence for each catalog entry is on https://monogate.org/theorems.

## Depth, the tan(1) obstruction, and i

### `Unifying_Obstruction_Tan1.tex`

- **§ The Depth Stability Theorem** (theorem "Depth Stability Theorem, S99 / T18", its proof sketch and
  remark).
  - *Claim:* i ∉ EML₁ if and only if depth_ℂ(f) = depth_ℝ(f) for every Atlas function; sin has real depth 3.
  - *Change:* withdrawn. sin has no real EML tree of any depth (Lean: MachLib
    `sin_not_in_eml_any_depth_unconditional`), yet it is the imaginary part of the one-node complex tree
    eml(ix, 1). The proof's step "every complex tree can be converted to an equally-deep real tree" fails
    for sin.
  - *Page:* /blog/tan1-obstruction, /blog/depth-spectrum, /blog/conditional-tan1.
- **The argument that the transcendence of tan(1) keeps i out of EML₁ under complex semantics** (the
  theorem labelled `thm:T18` and its use in the depth-stability proof).
  - *Change:* not a proof. Im eml(z, w) = e^(Re z)·sin(Im z) − arg w depends on w as well, and transcendence
    is no obstruction to being an EML value, since e = eml(1, 1). Under the complex principal branch,
    whether i is an EML value is open.
  - *Page:* /blog/tan1-obstruction.
- **§ The depth-3 ceiling** (Application 2).
  - *Claim:* every standard elementary function has EML depth ≤ 3, by depth stability.
  - *Change:* false. x + 1 has depth exactly 4 on (0, ∞) (Lean: MachLib `x_plus_one_depth_exact_four`),
    sin has no real tree, and no tree backs arctan at depth 3.
  - *Page:* /blog/tan1-obstruction.
- **§ The Five-Way Equivalence** (theorem "Five-Way Equivalence, T30-synthesis").
  - *Change:* withdrawn. Condition (1) is a theorem (Lindemann–Weierstrass) and (3) is false, so the five
    are not equivalent; (4) has no tree or lower bound behind it.
  - *Page:* /blog/tan1-obstruction.
- **§ The Collapse Theorem** (theorem "Collapse under negation of the obstruction").
  - *Change:* withdrawn. Under strict real semantics i is not an EML value whatever tan(1) is, and the F6
    multiplication bound is a finite search that never uses i.
  - *Page:* /blog/tan1-obstruction.

### `theorems/DOOR4_Conditional_Tan1.tex`

- **§ Background and Standing Results**, theorem "Depth Stability Theorem, DST": withdrawn, as above.
  *Page:* /blog/conditional-tan1.
- **§ Step C — π Would Be EML-Constructible.**
  - *Claim:* π becoming EML-constructible "is inconsistent with the transcendence of π over ℚ(e) (a
    consequence of Nesterenko 1996)"; arcsin has depth 3.
  - *Change:* being an EML value is compatible with transcendence (e = eml(1, 1)). Nesterenko's theorem is
    about π and e^π; whether π is transcendental over ℚ(e) is open. No tree backs arcsin at depth 3.
  - *Page:* /blog/conditional-tan1 (its Step D).
- **§ Step D — Depth Stability Breaks.** Rests on the withdrawn Depth Stability Theorem, and its witness
  "depth_ℝ(arctan) = 3" has no tree. *Page:* /blog/conditional-tan1 (its Step C).

### `near_miss_obstruction.tex`

- **Abstract and § The near-miss and the tan(1) obstruction**, including theorem "Transcendental
  obstruction".
  - *Claim:* exact Im = 1 needs Re(y) = π/tan(1) ≈ 2.0270, a value not constructible from {1}.
  - *Change:* π/tan(1) = 2.0171934. That it is not constructible is not established. π/tan(1) lies in the
    field of exp–log numbers (π = −i·log(−1) and tan 1 = −i(e^(2i) − 1)/(e^(2i) + 1)), and transcendence
    is no obstruction. The depth-6 value closest to i is 4.7634634×10⁻⁶ away, and a depth-7 tree has
    imaginary part within 7.9×10⁻¹² of 1; both searches are printed on the page.
  - *Page:* /blog/near-miss, /paper.

### `theorems/Depth_Spectrum_Self_Contained.tex`

- **§ The Theorem Statement.** *Claim:* "Every standard elementary function has EML depth ≤ 3." *Change:*
  false: x + 1 has depth exactly 4 (Lean).
- **§ Growth ceiling (with division case).** *Change:* the division case bounds 1/g by applying the
  induction hypothesis to 1/g itself, with no lower bound as g → 0. That exp^k needs exactly k nodes is
  proved in Lean only for k ≤ 4 (MachLib `tower_certified_upto_four`).
- *Page:* /theorems (T30), /blog/depth-spectrum.

### `theorems/Depth_Spectrum_Final.tex`

- **Header and § Depth versus node count: a critical distinction.** *Claim:* all 10 core arithmetic
  operations have EML depth ≤ 3; the depth-3 ceiling is "confirmed definitively". *Change:* false. x + 1
  needs depth 4, so addition cannot have depth 3. *Page:* /blog/depth-spectrum.

### `theorems/Depth_Spectrum_Classification.tex`

- **§ The EML Depth Spectrum Theorem (T30) and § Depth-1 functions.**
  - *Claim:* exp(−x) and e^(cx) at depth 1; ln x, x·y, x⁻¹, sinh and cosh at depth 2; "no standard
    elementary function has depth 4".
  - *Change:*
    - exp(−x) = eml(−x, 1) needs −x as a leaf, and no depth-1 tree over {1, x} equals exp(−x);
    - ln x has depth exactly 3 (Lean);
    - no tree is given for sinh or cosh;
    - x + 1 has depth 4.
  - *Page:* /blog/depth-spectrum, /blog/complexity-census.

### `theorems/EML4_Gap_Resolution.tex`

- **Abstract and § Resolution of the "No Depth 4" Claim.** *Claim:* "no depth 4" is accurate as a statement
  about classical elementary functions. *Change:* false: x + 1 has depth exactly 4. *Page:*
  /blog/depth-spectrum, /one-operator, /paper.

### `theorems/Unified_EML_Lower_Bound_Closure.tex`

- **§ Four Threads.** *Claim:* resolves C02 and C03. *Change:* both are open.
- **§ The Depth Spectrum Theorem** (T30). *Change:* the depth-3 ceiling is false (x + 1).
- **§ The Unifying Algebraic Mechanism**, theorem "The tan(1) Obstruction Governs All Rigidity". *Change:*
  withdrawn with the Depth Stability Theorem.
- *Page:* /theorems (T30, T31, C02, C03), /blog/depth-spectrum.

### `theorems/Complex_Closure_Density.tex`

- **Header**, "Theorem T31b (C03 resolved): i is an accumulation point". *Change:* open (C03).
- **§ Supporting Lemmas**, lemma "Monomials as exact EML trees". *Change:* the boxed tree
  EML(EML(EML(0,z),1/n),1) equals n·exp(e/z), not zⁿ. Addition is never constructed and branch cuts are not
  handled, so the density statement (T31) is a conjecture.
- *Page:* /theorems (T31, C02, C03), /blog/depth-spectrum.

### `cost_theory/R13_Complex_Cost.tex`

- **Header ("Trigonometric Bypass Theorem") and § ComplexCost of sin(x) / cos(x).** *Claim:*
  ComplexCost(sin) = ComplexCost(cos) = 2 and ComplexCost(sin² + cos²) = 3. *Change:* upper bounds. The
  cost-theory paper lists matching lower bounds as open, and sin²x + cos²x is the constant 1.
- **§ The i Construction Problem**, proposition "i is an accumulation point of EML₁". *Change:* open (C03).
- *Page:* /blog/cost-theory-complete, /theorems (C03).

## Completeness of exp–ln operators

### `theorems/Sixteen_Operator_Census.tex`

- **§ Complete Operators: Forward Direction**, theorem "Forward direction — T26". *Change:* no proof. The
  argument uses other operators and the constant e, and over ℝ the EAL case is false (every real EAL tree
  is nondecreasing).
- **§ Mechanism A: Slope barrier (DEML)**, theorems "DEML incompleteness — T27/T13" and "Reverse direction —
  T27". *Change:* the slope argument has a gap, since deml(x, 1) = e^(−x) decreases.
- **§ Mechanism B: Domain restriction (LEX)**, theorem "LEX domain incompleteness — T28". *Claim:* the domain
  shrinks to ∅ under self-composition. *Change:* false. lex(x, lex(lex(1,1),1)) = ln(eˣ − ln(e − 2)) is
  defined on all of ℝ.
- **§ The Approximate Operator: EMN**, theorem "EMN approximate completeness", and the "Exponential Position
  Theorem". *Change:* conjectures (T24, T12).
- *Page:* /theorems (T12, T13, T24, T26–T28), /blog/completeness-characterization, /blog/deml-is-incomplete.

### `preprint_addendum_emn_mul_math.tex`

- **§ B1. The Completeness Trichotomy**, theorems "EMN Exact Incompleteness" and "EMN Approximate
  Completeness". *Change:* sketches, not proofs. The mirroring step through EML = −EMN negates only the root
  node. *Page:* /blog/completeness-trichotomy, /theorems (T24).

### `eml_weierstrass_theorem.tex`

- **§ Main Theorem**, theorem "EML Weierstrass Theorem". *Change:* the argument reaches the linear span of EML
  trees (sums with coefficients), not a single tree, and builds monomials only for x > 0. No proof. *Page:*
  /blog/weierstrass-theorem.

## Zeros and analysis

### `infinite_zeros_barrier.tex` and `preprint.tex`

- **`infinite_zeros_barrier.tex` § Introduction (theorem "Infinite Zeros Barrier") and § The Proof (the lemma
  on isolated zeros); `preprint.tex` § The Infinite Zeros Barrier (theorem `thm:barrier`).**
  - *Change:* the proof does not work. sin is also real-analytic with isolated zeros, finitely many on each
    bounded interval, so nothing is contradicted. The zero-count route needs a bound on the zeros of a tree,
    which is open (T14).
  - The theorem holds: it is proved in Lean by periodicity (MachLib
    `sin_not_in_eml_any_depth_unconditional`).
  - *Page:* /blog/infinite-zeros-barrier.

### `preprint_addendum_s105_s112.tex`

- **§ A8. Pumping Lemma: Tight Bound Conjecture.**
  - *Claim:* a depth-k EML tree has at most 2^k zeros on any compact interval, "proof by repeated application
    of Rolle's theorem".
  - *Change:* the doubling induction is not valid, and without the hypothesis that the tree is not
    identically zero the statement is false: eml(x, eml(eml(x,1),1)) ≡ 0 at depth 3.
  - *Page:* /theorems (T14), /blog/pumping-lemma, /blog/tight-zeros-bound.

### `eml_complexity_census.tex`

- **§ Census Results.** *Change:* its EML-k figures are least-squares fits over sums of trees (for example
  ln x at EML-1), not the exact single-tree depth the site uses; ln x has exact depth 3 (Lean). *Page:*
  /blog/complexity-census.

## SuperBEST node counts

### `theorems/SuperBEST_v3.tex`

- **Abstract, § The SuperBEST v3 Table** (theorem "SuperBEST v3 is globally optimal") **and § Why 74.0%
  Cannot Be Exceeded** ("neg … 1-node lower bound certified").
  - *Change:* the entries are constructions, not all optimal: add takes 2n for all reals, pow and sqrt 1n for
    x > 0, and mul 1n for x, y > 0.
  - The only 1-node neg search on record rounds values to 6 decimals and rejects exact trees at x = π.
  - *Page:* /theorems (T08, T09).

### `theorems/SuperBEST_v4_Structural_Audit.tex`

- **"(c) Lower bound" for add (≥ 3), pow (≥ 3) and sqrt (≥ 2).** *Change:* each is beaten by a construction
  in the same family. *Page:* /theorems (T08).

### `theorems/ADD_T1_General_Addition_2n.tex`

- **§ Completeness of the table.** *Claim:* the table "is proved complete". *Change:* later constructions
  lowered mul, pow and sqrt; the current positive-domain total is 14n. *Page:* /blog/add-gen-2n.

### `theorems/recip_One_Node.tex`

- **Abstract.** *Claim:* R16-C1 moves SuperBEST from 19 (v3) to 18 nodes (v4). *Change:* the site's version
  history has v4 = 19 nodes with recip already 1n (/theorems T08), and 18 is v5.
- **§ Corollaries**, corollary "Division is still 2 nodes". *Change:* its statement says division "was already
  1 node via EDL(ln x, ln y)", contradicting its title and proof. EDL(x, y) = eˣ/ln y is not a division.
- *Page:* /blog/recip-one-node.

### `theorems/Mul_Lower_Bound_Tightened.tex` and `theorems/Mul_Tightening_and_SuperBEST_v2.tex`

- **`Mul_Lower_Bound_Tightened.tex` § Lower Bound: Six-Operator Library** ("|F6|² × 4³ × 2 = 12,288") and
  **`Mul_Tightening_and_SuperBEST_v2.tex` § Enumerating all candidate trees**, lemma "Counting 2-node
  candidates" ("exactly 12 288"). *Change:* the product is 36 × 64 × 2 = 4,608, which is what the search
  enumerates. *Page:* /theorems (T29).
- **`Mul_Lower_Bound_Tightened.tex` § New 2-Node Construction**, theorem "Mul = 2 nodes in F16". *Change:* holds
  in the April 16-operator set on x, y > 0; exp(ln x + ln y) = x·y is 1 node (F16 on /framework). *Page:*
  /theorems (T10u).

### `theorems/T32_Mul_Absolute_Optimality.tex`

- **§ Main Theorem**, theorem "T32 — Irreducibility of Multiplication".
  - *Claim:* no single node of any operator h(e^(εx), ε′ ln y) computes x·y.
  - *Change:* false. h(u, v) = ln(u)·exp(v) gives x·y in one node for y > 0. The Lean bound covers the 16
    operators defined in MonogateEML/MulLowerBound.lean.
  - *Page:* /theorems (T32).

### `exploration/SuperBEST_Final_Taxonomy_Lock.tex` and `exploration/CONJ_NO_OP_24_Closure.tex`

- **Taxonomy Lock abstract, theorem "Final taxonomy — proved closed", § Final Lock Statement item 1; CONJ_NO_OP_24
  § Main Theorem**, theorem "CONJ_NO_OP_24 = Theorem". *Change:* argued on paper; a conjecture.
- **Taxonomy Lock § High-Impact Expressions**, "Special functions (all = ∞ in F16, proved)". *Change:* Lean
  covers sin and cos for single-operator EML trees only; the rest is argued.
- **Taxonomy Lock § Honest Savings Summary.**
  - *Change:* "ML functions (6 items)" → 5, matching the paper's own table.
  - The ~% figures do not follow from the paper's rows. Pooled over them: ML 35% / 62%, quantum 19% / 44%,
    physics 29% / 40%. The aggregate names no rows.
- **Taxonomy Lock § Final Lock Statement items 3–4** (LSE 4n, softplus 2n). *Change:* these count the paper's
  "F16 orbit", which leaves out LEAd (`exploration/LEAd_Architectural_Decision.tex`). LEAd is F11 in the
  site's F16 (/framework), and with it softplus is 1 node (LEAd(x, 1)) and two-term log-sum-exp 2 nodes
  (LEAd(x, EML(y, 1))).
- *Page:* /superbest.

## Cost theory

### `cost_theory/Cost_Theory_Complete.tex`

- **Abstract** ("validated on 187 equations"). *Change:* 187 is the 157-equation corpus plus R12's 30 blind-test
  equations; the blind tests total 50 (COST-8's 20 and R12's 30).
- **§ Theorem T38: Cost Decomposition.** *Change:* a definition. PatternBonus is defined as the remainder, and
  with a pattern catalogue the identity fails on e^(x₁) + e^(x₂).
- **§ The No Nesting Penalty (T38-NNP)** and **§ Additive Cost Law (T40-ADD).** *Change:* upper bounds only.
  LEdiv(LEdiv(x,1),1) = x costs 0, and LEdiv(EML(x,2),1) costs 1.
- **§ Sharing Discount Formula (T38-SD).** *Change:* false under R4's own definition SD = NC − Cost.
- **§ Linear Cost Law (T40).** *Change:* (α₀+3)N − 3 is not exact (x₁ + x₂ costs 2). The bound is
  (α₀+2)N − 2, and a softmax denominator takes at most 2N − 1 nodes.
- **§ Theorem T41: … Four Structural Classes.** *Change:* the strict ordering C < B < A < D contradicts the
  paper's own class means (9.5, 10.4, 12.2, 20.1 give C < A < B < D).
- **§ Isomorphism Theorem (T41-ISO).** *Change:* "Cost(E₁) = Cost(E₂) exactly" rests on minimal DAGs that
  nothing establishes; the members of a family cost at most the same.
- **§ Complex Extension (T43).** *Change:* the equalities are upper bounds.
- **§ Open Problems, item 2.** *Change:* the Lean signatures carry `sorry`, and several of the statements are
  false as written (P2, the equality forms of T38-NNP and T40, the T41 ordering).
- *Page:* /blog/cost-theory-complete, /theorems.

### Other cost-theory papers

- **`cost_theory/R2_Decomposition_Theorem.tex`** (§ Statement, § Uniqueness Theorem) and
  **`cost_theory/COST6_Decomposition_Theorem.tex`** (§ Theorem T38): T38 is a definition. *Page:*
  /theorems (T38).
- **`cost_theory/R3_No_Nesting_Penalty.tex`** (§ Proposition): equality is false. *Page:* /theorems (P-NNP).
- **`cost_theory/R6_Additive_Cost_Law.tex`** (§ Proposition R6): equality is false. *Page:* /theorems
  (P-ACL).
- **`cost_theory/R5_Linear_Cost_Law.tex`** (§ Theorem T40 and its instances: softmax 4N − 3, Shannon entropy
  6N − 3, pharmacokinetic sum 10N − 3) and **`cost_theory/R14_Scaling_Laws.tex`** (§ The O(N) Scaling Law,
  theorem T_SL1): the exact law is false, as above. *Page:* /theorems (T40), /blog/cost-theory-complete,
  /blog/157-equations.
- **`cost_theory/R4_Sharing_Discount.tex`** (§ The Main Theorem; § Empirical Finding from COST-5, "47 of 50"):
  false under its own definition, and 47/50 contradicts the paper's 30 and 20. *Page:* /theorems (P-SD).
- **`cost_theory/COST2_Naive_Upper_Bound.tex`** (§ Corollary and Tightness Characterization): the tightness
  "iff" is false, since e^(x₁) + e^(x₂) costs 3 < naive 4 with no sharing or pattern. *Page:* /theorems
  (T34).
- **`cost_theory/COST3_Lower_Bound.tex`**: § Theorem T35 fails for LEdiv(x, 1) = x; § Theorem T37 is false,
  since EML(x, y) is one node holding both exp and ln; § Theorem T36's depth form is false, while its
  intermediate-value bound stands. *Page:* /theorems (T35).
- **`cost_theory/R9_Structural_Classes.tex`** (§ Theorem T41 — Cost Ordering): contradicted by the paper's §
  Empirical Confirmation. *Page:* /blog/cost-theory-complete.
- **`cost_theory/R10_Isomorphism_Theorem.tex`** (§ The SuperBEST Isomorphism Theorem): equal cost within a
  family is not shown. *Page:* /theorems (O-ISO), /blog/cost-theory-complete.

## Names that mean different things

- **EMN.** On the site, EMN(x, y) = ln(y) − exp(x), as in `theorems/Sixteen_Operator_Census.tex` and
  `preprint.tex`. `cost_theory/R7_Pattern_Bonus.tex` (pattern P12) uses "EMN" for a product of two
  exponentials, and so does `python/monogate/predict_cost.py`. *Page:* /glossary, /blog/negative-exponent.
- **F16.** Three different lists of sixteen operators carry the name:
  - `theorems/Sixteen_Operator_Census.tex` (EML, EMN, EAL, EXL, EDL, EPL and their exp(−x) versions, with
    LEAd, ELAd, ELSb and LEX);
  - the "F16 orbit" of `exploration/CONJ_NO_OP_24_Closure.tex` and the Taxonomy Lock, which leaves out LEAd;
  - the list F1–F16 of MonogateEML/AddLowerBound.lean, which the site's Lean lower bounds use.

  On monogate.org "F16" means the last one, listed on /framework. *Page:* /glossary, /framework, /superbest.
