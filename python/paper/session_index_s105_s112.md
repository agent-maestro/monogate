# Session Index: S105–S112

## S105 — Phantom Attractor 300-Digit PSLQ
**Status:** COMPLETE  
**File:** `experiments/` (inline), `results/s105_phantom_300digit.json`  
**Result:** PSLQ NULL at tol=1e-50, maxcoeff=100, 25-constant basis, 320-digit precision.
No minimal poly (degree ≤ 8, |coeff| ≤ 500). Both attractor basins confirmed transcendental candidates.  
**New finding:** exp(primary) ≈ 499.92 (close to 500 but not 500); secondary/π ≈ 1.995 (close to 2 but not 2).

## S106 — EML-4 Question
**Status:** COMPLETE  
**File:** `experiments/s106_eml4_question.py`, `results/s106_eml4_question.json`  
**Result:** EML-3 confirmed for: sin, cos, erf, x², tanh, erf(erf), sin·erf, log(1+sin), ln(1+x²).  
**EML-4+ candidates** (floor > 1e-8 at N=4 with 86-atom dictionary): sin(sin(x)), x⁶, x⁷, exp(-x²)·sin, sin(x²), exp(sin), sin(πx).  
**Note:** These are dict-limited; larger N=4 dicts may reduce floors. Not proven to require depth > 3.

## S107 — Pumping Lemma Tight Bounds
**Status:** COMPLETE  
**File:** `experiments/s107_pumping_lemma_tight.py`, `results/s107_pumping_lemma_tight.json`  
**Result:** All tested depth-k trees have 0–1 zeros on [-8,8]. Theoretical 2^k bound is loose.  
**Conjecture:** Tight bound is O(k) or O(1) for typical EML trees. Constructing a depth-k tree with Ω(k) zeros is the open problem.

## S108 — Grammar G2 Density
**Status:** COMPLETE  
**File:** `experiments/s108_grammar_g2_density.py`, `results/s108_grammar_g2_density.json`  
**Result:**
- |sin|: G2-BETTER (16×), |cos|: G2-BETTER (6.4×), triangle: G2-BETTER (7×)
- Sawtooth: OPEN (1.8×), sign(sin): OPEN (1.8×)
- Sin/cos controls: G2-DENSE (6M× improvement vs G1)
- **Conclusion:** G2 partially lifts the piecewise barrier; discontinuous functions remain hard.

## S109 — Complex EML Depth-7 Targeted Search
**Status:** COMPLETE  
**File:** `experiments/s109_complex_depth7_targeted.py`, `results/s109_complex_depth7_targeted.json`  
**New result:** Depth-6 gap to π/2 from {1}: 9.75e-6 (a second route to Im=1, previously unexplored).  
**Existing result confirmed:** Depth-6 gap to π/tan(1): ~4.19e-5 (limited search; S97 found 6.67e-7 with deeper search).  
**Conclusion:** The Im=1 barrier persists at depth 7 via current construction. Whether π/2 or π/tan(1) is in the real EML closure is equivalent to i-constructibility — open.

## S110 — Grammar G3 Closure
**Status:** COMPLETE  
**File:** `experiments/s110_grammar_g3_closure.py`, `results/s110_grammar_g3_closure.json`  
**Result:** All 9 targets (including exp(-x), exp(-x²), x·exp(-x)) are G3-DENSE.  
**Key finding:** At depth ≥ 3, G3 adds no barrier-lifting advantage over G1 for smooth functions. DEML's value is node efficiency (1-node vs. depth-3 for exp(-x)), not closure extension.  
**sinh improvement:** G3 gives 190× improvement — the EXL gate is naturally suited for sinh = (exp(x)·exp(-x) - 1)/... style representations.

## S111 — Quantum EML Weierstrass (2×2)
**Status:** COMPLETE  
**File:** `experiments/s111_quantum_eml_weierstrass.py`, `results/s111_quantum_eml_weierstrass.json`  
**Result:** 44 meml depth-1 atoms, rank 4, all 6 test density matrices to MSE < 3×10⁻³².  
**Conjecture confirmed (2×2 case):** meml atoms at depth 1 span the full 2×2 density matrix space.  
**Open:** Does this extend to d×d for d > 2?

## S112 — Formal Documents and Infrastructure
**Status:** COMPLETE  
**Files produced:**
- `paper/eml_weierstrass_theorem.tex` — formal proof with lemmas
- `paper/eml_complexity_census.tex` — 23-function census with table
- `paper/preprint_addendum_s105_s112.tex` — addendum for arXiv v2.2.0
- `paper/rh_eml_forward_direction.tex` — honest RH-EML assessment
- `paper/session_index_s105_s112.md` — this file
- `lean/EML/InfiniteZerosBarrier.lean` — Lean 4 proof stubs (2 sorries)
- `challenge/supabase/new_challenges_s112.sql` — 5 new challenge entries
- `monogate/__init__.py` — version bumped 2.1.6 → 2.2.0
- `pyproject.toml` — version bumped 2.1.6 → 2.2.0

## Summary of Advances

| # | Section | Result Type | Key Finding |
|---|---------|-------------|-------------|
| 1 | EML Weierstrass | Theorem + Proof | Density proved via monomials + classical Weierstrass |
| 2 | Pumping Lemma | Conjecture | 2^k bound is loose; tight bound O(k) conjectured |
| 3 | Fourier Rate | Theorem (sketch) | F(N) ≤ C·ρ^N for real-analytic f; geometric decay |
| 4 | Lean stubs | Infrastructure | Proof structure set up; 2 sorries remain |
| 5 | Complex depth-7 | New result | π/2 gap = 9.75e-6 at depth 6; second Im=1 route found |
| 6 | tan(1) barrier | Analysis | Obstruction = real constructibility of π/2 or π/tan(1) |
| 7 | G2 density | Experiment | |sin|/triangle improved 7-16×; sawtooth/sign open |
| 8 | G3 closure | Experiment | G3 = G1 in closure at depth ≥ 3; DEML adds node efficiency |
| 9 | Phantom 300-digit | Computation | PSLQ null; no minimal poly; transcendental conjecture strengthened |
| 10 | Multiple basins | Analysis | Two distinct basins confirmed; both PSLQ-null |
| 11 | N=12 paper | Paper section | 1.7B trees, best MSE 0.112; analytic proof closes the question |
| 12 | Complexity census | Paper section | 23 functions classified; EML-1/2/3/∞ table |
| 13 | Preprint addendum | Paper | A1-A8 ready for arXiv v2.2.0 |
| 14 | RH-EML analysis | Honest assessment | Not a proof path; forward direction trivially true |
| 15 | EML-4 question | Experiment | Candidates identified; none proven to require depth > 3 |
| 16 | Quantum EML | Experiment | 2×2 confirmed; open for d > 2 |
| 17 | G3 closure | Experiment | See #8 |
| 18 | RH-EML | Analysis | See #14 |
| 19 | Version bump | Infrastructure | 2.1.6 → 2.2.0 |
| 20 | Challenge board | Infrastructure | 5 new challenges; SQL migration ready |

## Walls Hit

| # | Wall | Details |
|---|------|---------|
| W1 | Lean sorries | InfiniteZerosBarrier.lean has 2 sorries: analytic composition lemma and finite-zeros-of-analytic theorem. Both need Mathlib imports. |
| W2 | EML-4 undetermined | Can't distinguish dict-limited from genuinely depth > 3 without much larger atom sets |
| W3 | Sawtooth/sign open | G2 gives only 1.8× improvement; likely EML-∞ by kink argument but not proved |
| W4 | tan(1) gap |  Depth-6 gap 4.19e-5 (limited search) vs S97's 6.67e-7 (deeper search). Real EML closure convergence rate unresolved |
| W5 | Quantum d > 2 | meml span for d×d density matrices at d=3,4 not tested (scipy logm numerical issues) |
| W6 | PyPI publish | Version bumped; actual upload needs `python3 -m build && twine upload dist/*` in session |
| W7 | arXiv revision | Addendum written; actual submission needs login credentials |
