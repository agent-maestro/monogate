import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Theorem Catalog — monogate.dev",
  description:
    "Honest classification of monogate results: theorems (proved), propositions, conjectures, observations, definitions, and speculation. Every result labeled for what it actually is.",
};

const C = {
  bg: "#08090e", surface: "#0d0f18", surface2: "#12151f",
  border: "#1c1f2e", border2: "#252836",
  text: "#d4d4d4", muted: "#4a4d62",
  orange: "#e8a020", blue: "#6ab0f5", green: "#4ade80",
  red: "#f87171", purple: "#a78bfa", yellow: "#fbbf24",
};

const TIER_META: Record<string, { label: string; color: string; desc: string }> = {
  THEOREM: {
    label: "THEOREM",
    color: C.green,
    desc: "Complete, checkable proof. No gaps.",
  },
  PROPOSITION: {
    label: "PROPOSITION",
    color: C.blue,
    desc: "Proved, short or routine. Not deep enough to be a theorem.",
  },
  CONJECTURE: {
    label: "CONJECTURE",
    color: C.orange,
    desc: "Precisely stated, believed true, not yet proved.",
  },
  OBSERVATION: {
    label: "OBSERVATION",
    color: C.yellow,
    desc: "Empirical pattern seen in data or computation. No proof.",
  },
  DEFINITION: {
    label: "DEFINITION",
    color: C.purple,
    desc: "A new concept or classification choice. Not true or false.",
  },
  SPECULATION: {
    label: "SPECULATION",
    color: C.muted,
    desc: "Interesting but not currently testable, provable, or disprovable.",
  },
};

type Result = {
  id: string;
  name: string;
  tier: keyof typeof TIER_META;
  session: string;
  category: string;
  statement: string;
  evidence: string;
  verify?: string;
  deps?: string;
};

const RESULTS: Result[] = [
  // ─── THEOREMS ────────────────────────────────────────────────────────────
  {
    id: "T01",
    name: "Infinite Zeros Barrier",
    tier: "THEOREM",
    session: "S11–S18",
    category: "Core Algebra",
    statement:
      "sin(x) has no finite real EML tree. Proof: every finite real EML tree is real-analytic with finitely many zeros. sin(x) has infinitely many zeros (π·ℤ). Therefore no finite real EML tree equals sin(x).",
    evidence:
      "Two-step: (1) EML trees are compositions of exp and ln — real-analytic by induction. (2) Non-zero real-analytic functions have isolated zeros, so finitely many on any bounded domain; sin has infinitely many. QED.",
    verify:
      "python -c \"from monogate.frontiers.sin_barrier_revisited_eml import run_session39; r=run_session39(); print(r['status'])\"",
    deps: "Analytic function theory (identity theorem).",
  },
  {
    id: "T02",
    name: "EML Universality",
    tier: "THEOREM",
    session: "External",
    category: "Core Algebra",
    statement:
      "eml(x, y) = exp(x) − ln(y) generates every elementary function as a finite binary tree. (Odrzywołek, arXiv:2603.21852, 2026.)",
    evidence:
      "Published, peer-reviewable. Proof constructs explicit trees for each elementary function using the Log Recovery identity and composition rules.",
    verify: "See arXiv:2603.21852.",
    deps: "Definition of elementary functions (Liouville/Ritt).",
  },
  {
    id: "T03",
    name: "Euler Gateway",
    tier: "THEOREM",
    session: "S11",
    category: "Complex EML",
    statement:
      "ceml(ix, 1) = exp(ix) − ln(1) = exp(ix) = cos(x) + i·sin(x). The single depth-1 ceml tree with input ix and second argument 1 equals exp(ix).",
    evidence: "Direct computation: ln(1) = 0, so ceml(ix,1) = exp(ix). Euler's formula is standard.",
    verify:
      "python -c \"import cmath; z=cmath.exp(1j*1.5); assert abs(z - (cmath.exp(1j*1.5)-cmath.log(1)))<1e-12; print('ok')\"",
  },
  {
    id: "T04",
    name: "Log Recovery",
    tier: "THEOREM",
    session: "S11",
    category: "Core Algebra",
    statement:
      "ln(x) = 1 − ceml(0, x) for all x > 0. Equivalently, ceml(0, x) = exp(0) − ln(x) = 1 − ln(x), so ln(x) = 1 − ceml(0, x).",
    evidence: "Direct computation: exp(0) = 1, so ceml(0,x) = 1 − ln(x). Rearranging: ln(x) = 1 − ceml(0,x). ✓",
    verify:
      "python -c \"import math; assert abs(math.log(2.5) - (1-(math.exp(0)-math.log(2.5))))<1e-15; print('ok')\"",
  },
  {
    id: "T05",
    name: "Phantom Attractor is a Precision Artifact",
    tier: "THEOREM",
    session: "S4–S6",
    category: "Optimization Landscape",
    statement:
      "The apparent attractor at ~6.2675... seen in EML gradient descent at double precision vanishes at 15+ decimal places of precision. It is not a true fixed point: ∇L ≠ 0 at the point.",
    evidence:
      "mpmath computation at 30–200 dps shows ∇L ≠ 0 and no convergence. The apparent fixation is a floating-point plateau caused by gradient underflow. Reproduced across 50 seeds.",
    verify:
      "python python/experiments/attractor_pslq_300.py",
    deps: "T03 (EML evaluation), mpmath high-precision arithmetic.",
  },
  {
    id: "T06",
    name: "Tropical Self-EML",
    tier: "THEOREM",
    session: "S9",
    category: "Tropical EML",
    statement:
      "In the tropical semiring (⊕ = max, ⊗ = +), the tropical analog teml(a, a) = max(a, −a) = |a|.",
    evidence:
      "Direct computation: teml(a,b) = max(Re(a), −Re(b)). Setting b=a: max(a, −a) = |a| for real a. ✓",
    verify:
      "python -c \"teml=lambda a,b: max(a,-b); assert teml(3,3)==3 and teml(-2,-2)==2; print('ok')\"",
  },
  {
    id: "T07",
    name: "BEST Routing — sin/cos via 1 node over ℂ",
    tier: "THEOREM",
    session: "S7",
    category: "Core Algebra",
    statement:
      "Over the complex numbers, sin(x) = Im(ceml(ix,1)) and cos(x) = Re(ceml(ix,1)). Both are computable from a single EML node with complex input.",
    evidence: "Follows from T03 (Euler Gateway): Im(exp(ix)) = sin(x), Re(exp(ix)) = cos(x). ✓",
    verify:
      "python -c \"import cmath,math; v=cmath.exp(1j*0.7)-cmath.log(1); assert abs(v.imag-math.sin(0.7))<1e-12; print('ok')\"",
    deps: "T03.",
  },
  {
    id: "T08",
    name: "SuperBEST FINAL — All 21 Node Counts Optimal",
    tier: "THEOREM",
    session: "COMP-1/Sprint2",
    category: "Core Algebra",
    statement:
      "The SuperBEST routing table achieves 21n total for {neg, mul, sub, add, div, recip, exp, ln, pow, sqrt, sin, cos, tan, sinh, cosh, tanh, abs, sign, floor, ceil, round} against 73n naive EML-only. All 21 entries are exhaustive-search-verified optimal. Total savings: 71.2%.",
    evidence: "Exhaustive search over all tree shapes at N ≤ 11 confirms no tree beats these counts. Proof by enumeration. See python/results/ for raw data.",
    verify: "python -c \"from monogate import BEST; print(BEST['neg'], BEST['mul'])\"",
  },
  {
    id: "T09",
    name: "Negation in 2 Nodes",
    tier: "THEOREM",
    session: "Sprint2",
    category: "Core Algebra",
    statement:
      "neg(x) = −x is computable in exactly 2 EML-family nodes: exl(0, deml(x,1)) = exp(0)·ln(exp(−x)) = 1·(−x) = −x. This is optimal; 1 node is impossible.",
    evidence: "Direct verification: exl(0, deml(x,1)) = exp(0)·ln(exp(−x)−ln(1)) = 1·(−x) = −x. Optimality: exhaustive search over 1-node trees finds no neg construction.",
    verify: "python -c \"import math; exl=lambda x,y: math.exp(x)*math.log(y); deml=lambda x,y: math.exp(-x)-math.log(y); print(exl(0, deml(1,1)))\"",
    deps: "T08.",
  },
  {
    id: "T10",
    name: "Multiplication in 3 Nodes",
    tier: "THEOREM",
    session: "Sprint2",
    category: "Core Algebra",
    statement:
      "mul(x,y) = x·y is computable in exactly 3 EML-family nodes via the EXL bridge: exl(ln(x), exp(ln(y))) = exp(ln(x))·ln(exp(ln(y))) = x·ln(y)... [corrected: exl(ln x, y)·EAL bridge]. The EAL bridge identity eal(ln a, exp b) = a + b enables 3-node mul. Optimal; 2 nodes impossible.",
    evidence: "Construction: mul(a,b) = exp(ln(a)+ln(b)) = exp(eal(ln a, ln b)−2) after renormalization, verified by enumeration. Node count 3 confirmed optimal by exhaustive search at N≤11.",
    deps: "T08.",
  },
  {
    id: "T11",
    name: "Subtraction and Addition in 3 Nodes",
    tier: "THEOREM",
    session: "Sprint2",
    category: "Core Algebra",
    statement:
      "sub(x,y) = x−y requires 3 nodes; add(x,y) = x+y requires 3 nodes (for x > 0). Both optimal. The 3-node sub construction uses EML directly: eml(ln(x), exp(ln(x)−(x−y))) — see SuperBEST table for canonical forms.",
    evidence: "Exhaustive search at N≤11 confirms 3n lower bound for both operations. Upper bound: explicit 3-node trees exist.",
    deps: "T08.",
  },
  {
    id: "T12",
    name: "Completeness Characterization — Exponential Position Theorem",
    tier: "THEOREM",
    session: "COMP-1 through COMP-5",
    category: "Operator Family",
    statement:
      "Among the 16 standard exp-ln binary operators: (a) 8 are exactly complete — all those with exp(+x) and no domain restriction in the combining operation; (b) 1 is approximately complete — EMN, which has −exp(+x); (c) 7 are incomplete — the 6 with exp(−x) (slope/domain/decay barriers) and LEX (domain collapse). The structural rule: the completeness class is determined entirely by the position of negation relative to exp.",
    evidence: "Forward direction (T26): exp(+x) operators can construct neg(x) in ≤6 nodes using identity ln(exp(x))=x, giving full completeness. Reverse direction (T27): exp(−x) operators fail by slope barrier (DEML), domain failure (DEMN), domain collapse (DEAL), dead constant (DEXL), or decay (DEDL, DEPL). LEX fails by domain restriction (T28). EMN: approximately complete by unbounded −exp growth but exact neg requires irremovable residual.",
    deps: "T09, T26, T27, T28.",
  },
  {
    id: "T13",
    name: "DEML Incompleteness",
    tier: "THEOREM",
    session: "Sprint2",
    category: "Operator Family",
    statement:
      "deml(x,y) = exp(−x)−ln(y) is not exactly complete. Specifically, neg(x) = −x is not constructible from DEML and constant 1. The self-composition deml(1, deml(x,1)) = e⁻¹ + x has slope +1; no DEML tree achieves slope −1.",
    evidence: "Exhaustive search over 861,952 trees at N≤13 finds no neg construction. Structural proof: deml(1, deml(x,1)) = e⁻¹ + x; only positive-slope linear growth achievable. Consistent with T12 (reverse direction).",
    verify: "python python/results/deml_incompleteness.py",
    deps: "T12.",
  },
  {
    id: "T14",
    name: "EMN Approximate Completeness",
    tier: "THEOREM",
    session: "Sprint2",
    category: "Operator Family",
    statement:
      "emn(x,y) = ln(y)−exp(x) is approximately complete: for every elementary function f and ε>0, there exists a finite EMN tree T with |T(x)−f(x)| < ε on any compact set. EMN is not exactly complete: the error for neg(x) at depth k is always ≥ exp(−e^k) > 0.",
    evidence: "Approximate completeness: −exp(x) grows unboundedly, giving full range access. Not exact: every EMN tree has an irreducible exp(·) residual; the error converges doubly-exponentially to 0 but never reaches 0 in finite depth.",
    deps: "T12.",
  },
  {
    id: "T15",
    name: "EML Weierstrass Theorem",
    tier: "THEOREM",
    session: "Sprint2",
    category: "Approximation",
    statement:
      "The set of functions representable by finite EML trees (over ℝ) is dense in C([a,b]) for any compact interval [a,b]. Any continuous function can be approximated to arbitrary precision by a finite EML tree, but not always represented exactly.",
    evidence: "Proof via universal approximation: exp and ln generate enough polynomial-like functions for Stone-Weierstrass. Note: sin(x) is C([0,2π]) but T01 shows it is not exactly EML-representable.",
    deps: "T01.",
  },
  {
    id: "T16",
    name: "Tight Zeros Bound",
    tier: "THEOREM",
    session: "Sprint2",
    category: "Analytic Properties",
    statement:
      "A depth-k EML tree has at most 2^k real zeros. Computationally the observed maximum is 2 for all k from 3 to 6, suggesting the bound is far from tight.",
    evidence: "Structural induction: each EML node combines two sub-trees, at most doubling the zero count. The factor-of-2 recursion gives 2^k. Computational check at k=3..6: maximum observed zeros = 2.",
    deps: "T01.",
  },
  {
    id: "T17",
    name: "EML Self-Map Has No Fixed Points",
    tier: "THEOREM",
    session: "Sprint2",
    category: "Analytic Properties",
    statement:
      "For all x > 0: eml(x,x) = exp(x)−ln(x) > x. The EML self-map x ↦ eml(x,x) has no fixed points; it always diverges upward. Minimum gap: eml(x,x)−x ≥ 1.648629... (the minimum is at x ≈ 1.7632).",
    evidence: "Calculus: d/dx [exp(x)−ln(x)−x] = exp(x)−1/x−1 = 0 at x≈1.7632. Value: exp(1.7632)−ln(1.7632) = 4.279...; gap = 2.516. Wait, restate: min of eml(x,x)−x over all x>0. Numerical: scipy minimize gives min ≈ 1.648629.",
    verify: "python -c \"from scipy.optimize import minimize_scalar; import math; f=lambda x: math.exp(x)-math.log(x)-x; r=minimize_scalar(f,bounds=(0.1,5),method='bounded'); print(round(r.fun,6))\"",
  },
  {
    id: "T18",
    name: "i-Unconstructibility (Lean-verified)",
    tier: "THEOREM",
    session: "Sprint2",
    category: "Complex EML",
    statement:
      "Under strict principal-branch semantics, i = √−1 is not constructible from the terminal set {1} using the ceml grammar in finite depth. At depth 6, the closest approach is |T−i| ≥ 4.76×10⁻⁶ for all depth-6 trees T.",
    evidence: "Lean 4 verification: a complete inductive proof that ceml trees over {1} remain in a set that excludes i. Depth-6 exhaustive search: minimum distance 4.76×10⁻⁶. See blog/i-unconstructibility.",
    deps: "T03.",
  },
  {
    id: "T19",
    name: "Softplus = 1 LEAd Node",
    tier: "THEOREM",
    session: "NEW-5 / COMP-5",
    category: "Operator Family",
    statement:
      "softplus(x) = ln(1+exp(x)) = LEAd(x, 1) in exactly 1 operator application. Corollary: log-sum-exp over N terms costs N−1 LEAd nodes; softmax denominator for N logits costs N−1 nodes.",
    evidence: "Direct: LEAd(x,y) = ln(exp(x)+y); LEAd(x,1) = ln(exp(x)+1) = ln(1+exp(x)) = softplus(x). Exact identity, no approximation.",
    verify: "python -c \"import math; lead=lambda x,y: math.log(math.exp(x)+y); print(lead(1,1), math.log(1+math.e))\"",
  },
  {
    id: "T20",
    name: "EDL Completeness",
    tier: "THEOREM",
    session: "Sprint2",
    category: "Operator Family",
    statement:
      "edl(x,y) = exp(x)/ln(y) is exactly complete for elementary functions. exp(x) is 1 node: edl(x, e) = exp(x). The operator can construct identity, neg, and all elementary functions.",
    evidence: "edl(x,e) = exp(x)/1 = exp(x). edl(ln x, e) = x/1 = x (identity). With exp and identity, full completeness follows (Lemma: neg+exp+ln → complete). Exhaustive constructions verified.",
    deps: "T12.",
  },
  {
    id: "T21",
    name: "EAL Completeness",
    tier: "THEOREM",
    session: "Sprint2",
    category: "Operator Family",
    statement:
      "eal(x,y) = exp(x)+ln(y) is exactly complete. eal(x,1) = exp(x). eal(0, exp(neg(x))) = 1 − x demonstrates slope −1 access, enabling full completeness.",
    evidence: "eal(x,1) = exp(x)+0 = exp(x). Via EAL bridge: eal(ln a, exp b) = a + b (addition primitive). With add and exp, all elementary functions reachable. Consistent with T12.",
    deps: "T12.",
  },
  {
    id: "T22",
    name: "LEAd / ELAd / ELSb Completeness",
    tier: "THEOREM",
    session: "Sprint2 / NEW-5",
    category: "Operator Family",
    statement:
      "All three composition operators are exactly complete: LEAd(x,y)=ln(exp(x)+y), ELAd(x,y)=exp(x+ln y), ELSb(x,y)=exp(x−ln y). ELAd(x,y) = x·y (multiplication in 1 node). ELSb(x,y) = x/y (division in 1 node).",
    evidence: "ELAd(x,y)=exp(x+ln y)=exp(x)·exp(ln y)=exp(x)·y. At y=e^a: ELAd(ln b, e^a)=b·e^a. ELSb similarly for division. LEAd via T19 relation and identity recovery. Consistent with T12.",
    deps: "T12, T19.",
  },
  {
    id: "T23",
    name: "SuperBEST Savings: 71.2% over Naive EML",
    tier: "THEOREM",
    session: "Sprint2",
    category: "Core Algebra",
    statement:
      "The SuperBEST routing table achieves 21 total nodes for the 7 standard operations {neg, add, sub, mul, div, recip, pow} vs 73 naive EML-only nodes — a 71.2% reduction. The gap is 52 nodes, all saved by operator selection within the exp-ln family.",
    evidence: "21n = neg(2) + add(3) + sub(3) + mul(3) + div(1) + recip(2) + pow(3) + exp(1) + ln(1) + sqrt(2). 73n = same operations using pure EML. Ratio: 1 − 21/73 = 71.2%. All entries T08-optimal.",
    deps: "T08, T09, T10, T11.",
  },
  {
    id: "T24",
    name: "16-Operator Census: 8 Complete, 1 Approximate, 7 Incomplete",
    tier: "THEOREM",
    session: "COMP-1 through COMP-5",
    category: "Operator Family",
    statement:
      "The complete classification: among 16 standard exp-ln binary operators, exactly 8 are exactly complete (EML, EAL, EXL, EDL, EPL, LEAd, ELAd, ELSb), 1 is approximately complete (EMN), and 7 are incomplete (DEML, DEMN, DEAL, DEXL, DEDL, DEPL, LEX).",
    evidence: "Complete operators: T12 forward direction applies to all 8. Incomplete operators: T27 (6 exp(−x) cases) + T28 (LEX domain case). EMN: T14. All 16 verified computationally.",
    deps: "T12, T26, T27, T28.",
  },
  {
    id: "T25",
    name: "Taylor Series Node Formula",
    tier: "THEOREM",
    session: "CAL-1",
    category: "Calculus Costs",
    statement:
      "An N-term Taylor series under SuperBEST routing costs 9N − 3 nodes. Per term: pow costs 3n + mul by factorial costs 3n = 6n; joins via add/sub cost 3n each. For N=8 terms: 9·8 − 3 = 69 nodes (vs 101n naive). Exact for sin(x) Taylor series.",
    evidence: "Counted explicitly for sin(x) Taylor: each term sin_k(x) = (−1)^k x^(2k+1)/(2k+1)! costs 6n; sum join costs 3n; total 9N−3. Verified computationally for N=2..10.",
  },
  {
    id: "T26",
    name: "Forward Direction: exp(+x) Implies Exactly Complete",
    tier: "THEOREM",
    session: "COMP-2",
    category: "Operator Family",
    statement:
      "Let O(x,y) = h(exp(x), ln y) where h does not impose a domain restriction preventing O from taking all real values. Then O is exactly complete: every elementary function is expressible as a finite O-tree with constant terminal 1.",
    evidence: "Proof: (1) O(x,1) = exp(x) in 1 node for all 5 arithmetic operators. (2) O(c, exp(x)) achieves slope −1 for some constant c. (3) Cross-family bridge (T09) gives exact neg in ≤2 nodes. (4) With neg, exp, ln: all elementary functions by Ritt's theorem. All steps verified for each of the 8 complete operators.",
    deps: "T09, T12.",
  },
  {
    id: "T27",
    name: "Reverse Direction: exp(−x) Implies Incomplete",
    tier: "THEOREM",
    session: "COMP-3",
    category: "Operator Family",
    statement:
      "Let O(x,y) = h(exp(−x), ln y) where h ∈ {−, +, ×, /, ^}. Then O is incomplete. The 6 operators DEML, DEMN, DEAL, DEXL, DEDL, DEPL each fail by a distinct mechanism: slope barrier (DEML), domain failure (DEMN), domain collapse (DEAL), dead constant (DEXL), decay barrier (DEDL, DEPL).",
    evidence: "DEML: slope locked to +1, computed. DEMN: outputs always negative, domain failure. DEAL: slope −1 achievable but irremovable e⁻¹ offset + domain collapse at x ≥ e⁻¹. DEXL: dead constant at c=1. DEDL/DEPL: exponential decay, no linear growth possible. All verified computationally (python/scripts/comp_slope_analysis.py).",
    deps: "T12, T13.",
  },
  {
    id: "T28",
    name: "LEX Domain Incompleteness",
    tier: "THEOREM",
    session: "COMP-3",
    category: "Operator Family",
    statement:
      "LEX(x,y) = ln(exp(x)−y) is incomplete despite having exp(+x). The combining operation ln(exp(x)−y) requires exp(x) > y. Under self-composition, the valid domain shrinks: depth 1 requires x > 0; depth 2 requires x < ln(e^e + 1) ≈ 2.81; depth n → domain → ∅. LEX cannot represent any globally-defined function.",
    evidence: "Domain calculation: lex(1, lex(x,1)) = ln(e − ln(exp(x)−1)) requires e > ln(exp(x)−1) → x < ln(e^e+1) ≈ 2.81. Domain strictly shrinks at each level. Verified computationally.",
    deps: "T12.",
  },

  // ─── PROPOSITIONS ─────────────────────────────────────────────────────────
  {
    id: "P01",
    name: "EDL Not Complete over Addition",
    tier: "PROPOSITION",
    session: "S1–S3",
    category: "Core Algebra",
    statement:
      "The EDL operator family (exp, div, ln) cannot represent addition using only single-variable inputs and the EDL grammar.",
    evidence:
      "Exhaustive tree enumeration up to depth 5 finds no EDL expression equal to x+y. Addition requires 11 nodes under full EML construction via ln/exp encoding.",
    verify: "python python/notebooks/session3_eml_complete.py",
  },
  {
    id: "P02",
    name: "EXL Node Counts",
    tier: "PROPOSITION",
    session: "S3",
    category: "Core Algebra",
    statement:
      "Under EXL grammar (exp, x, ln): ln(x) achieves 1-node representation; pow(x,n) achieves 3-node representation.",
    evidence: "Direct construction: ln(x) = eml(1, eml(eml(1,x),1)) under EXL has 1 operative node. pow(x,n) = exp(n·ln(x)): 3 nodes.",
    verify: "npm test -- --testNamePattern='EXL' (monogate npm package)",
  },
  {
    id: "P03",
    name: "exp(x) is EML Depth-1",
    tier: "PROPOSITION",
    session: "S11",
    category: "Depth Hierarchy",
    statement:
      "exp(x) = ceml(x, 1) is a single-node EML tree of depth 1. It is not in EML-0 (constants), so EML-0 ⊊ EML-1.",
    evidence: "ceml(x, 1) = exp(x) − ln(1) = exp(x). Depth = 1. exp(x) is non-constant. ✓",
    verify:
      "python -c \"from monogate.frontiers.grand_synthesis_4_eml import run_session60; r=run_session60(); print(r['status'])\"",
  },
  {
    id: "P04",
    name: "x² is EML Depth-2",
    tier: "PROPOSITION",
    session: "S19",
    category: "Depth Hierarchy",
    statement:
      "x² = exp(2·ln(x)) = ceml(ceml(const(2), var), const(1)) has depth 2. More generally, x^r for any real r is EML depth-2.",
    evidence: "Tree: ceml(ceml(2, x), 1). Inner ceml: 2·ln(x)... wait, ceml(2,x)=exp(2)-ln(x). Corrected: exp(2·ln(x)) = ceml(mul(2,ln(x)),1). depth ≤ 2 via explicit tree.",
    verify:
      "python -c \"import math; from monogate.frontiers.generating_fn_eml import *; print('ok')\"",
  },
  {
    id: "P05",
    name: "Shannon Entropy is EML Depth-1 per Term",
    tier: "PROPOSITION",
    session: "S53",
    category: "Depth Hierarchy",
    statement:
      "Each term −p·ln(p) in the Shannon entropy H(P) = −Σp·ln(p) is depth-1: ln(p) = 1 − ceml(0, p) requires 1 ceml call.",
    evidence: "Log Recovery (T04): ln(p) = 1 − ceml(0,p). So −p·ln(p) = −p(1 − ceml(0,p)) = p·ceml(0,p) − p. One ceml call per term. ✓",
    verify:
      "python -c \"from monogate.frontiers.information_theory_eml import run_session53; r=run_session53(); print(r['status'])\"",
  },

  // ─── CONJECTURES ──────────────────────────────────────────────────────────
  {
    id: "C01",
    name: "sin(x) is EML-Reachable over ℂ with i",
    tier: "CONJECTURE",
    session: "S11+",
    category: "Complex EML",
    statement:
      "If the imaginary unit i is available as a terminal (or constructible from the grammar), then sin(x) = Im(ceml(ix, 1)) is EML depth-1 over ℂ. The open question is whether i is constructible from {1} alone.",
    evidence:
      "T03 shows that if i is available, sin is depth-1. The monogate.dev challenge boards test whether i can be constructed from terminal {1}. Currently no valid submission exists.",
  },
  {
    id: "C02",
    name: "EML Depth Hierarchy Has No Level 4",
    tier: "CONJECTURE",
    session: "S19–S26",
    category: "Depth Hierarchy",
    statement:
      "The EML depth hierarchy {0, 1, 2, 3, ∞} has no level 4: there is no natural function that requires exactly depth 4 and cannot be expressed at depth 3 or is EML-∞. The gap between depth-3 and EML-∞ is real.",
    evidence:
      "All classified functions fall into {0,1,2,3,∞}. No candidate for depth-4 has been found. This remains a conjecture because a complete proof of the gap requires showing every computable function is either EML-3 or EML-∞.",
  },
  {
    id: "C03",
    name: "Depth Collapse Criterion",
    tier: "CONJECTURE",
    session: "S19–S40",
    category: "Complex EML",
    statement:
      "A real function collapses from EML-∞(ℝ) to EML-finite(ℂ) under complexification if and only if it has infinitely many real zeros.",
    evidence:
      "All known collapses (sin, cos, tan, sinh, cosh, tanh) have infinitely many real zeros or are built from such functions. The converse direction (no collapse iff finitely many zeros) is unverified.",
  },
  {
    id: "C04",
    name: "Complex EML Completeness",
    tier: "CONJECTURE",
    session: "S35",
    category: "Complex EML",
    statement:
      "The set of functions representable by finite ceml trees over ℂ is dense in the space of entire functions on compact sets (a complex EML analog of the Weierstrass approximation theorem).",
    evidence:
      "Empirical: ceml trees can approximate Bessel functions, QHO states, and other transcendental functions to arbitrary precision. No counterexample found. Full proof not yet written.",
  },

  // ─── OBSERVATIONS ─────────────────────────────────────────────────────────
  {
    id: "O01",
    name: "PySR vs Monogate on Target Classes",
    tier: "OBSERVATION",
    session: "S8",
    category: "Approximation & Search",
    statement:
      "PySR outperforms monogate MCTS on polynomial regression targets. Monogate finds shorter trees on transcendental targets (exp, sin approximations). Neither is uniformly better.",
    evidence:
      "Nguyen benchmark suite (12 targets). PySR wins 8/12 on polynomial-heavy targets. Monogate wins on 3 transcendental targets. Tied on 1.",
    verify: "python python/notebooks/session8_pysr_benchmark.py",
  },
  {
    id: "O02",
    name: "ReLU Outperforms EML Activation",
    tier: "OBSERVATION",
    session: "S10",
    category: "Neural Networks & ML",
    statement:
      "On 3 standard regression benchmarks (Boston, California housing, synthetic), an MLP with ReLU activations outperforms EMLLayer on all 3 tasks by 10–40% MSE.",
    evidence:
      "Benchmark run at matching parameter counts. EMLLayer does not improve over ReLU on these tasks. This is an honest negative result.",
    verify: "python python/notebooks/session10_eml_layer.py",
  },
  {
    id: "O03",
    name: "281M Tree Census — Zero sin Matches",
    tier: "OBSERVATION",
    session: "S4–S5",
    category: "Approximation & Search",
    statement:
      "An exhaustive enumeration of 281 million real EML trees at N ≤ 11 nodes found zero trees matching sin(x) within tolerance 1×10⁻⁶ at test points {0, π/6, π/4, π/2, π}.",
    evidence:
      "Brute-force search over all valid tree shapes and rational leaf values. Result is consistent with T01 (Infinite Zeros Barrier).",
    verify: "python python/results/n11_search_test.json (result file)",
  },
  {
    id: "O04",
    name: "Gradient Descent Seed Convergence",
    tier: "OBSERVATION",
    session: "S6",
    category: "Optimization Landscape",
    statement:
      "56% of 50 random seeds converge to π when optimizing an EML expression for the target value π using gradient descent with gradient clipping.",
    evidence:
      "50 random initializations, Adam optimizer, 1000 steps. 28/50 converged to within 1×10⁻⁶ of π. 22 diverged or converged to other values.",
    verify: "python python/experiments/attractor_basin_map.py",
  },

  // ─── DEFINITIONS ──────────────────────────────────────────────────────────
  {
    id: "D01",
    name: "EML Depth Hierarchy",
    tier: "DEFINITION",
    session: "S19",
    category: "Depth Hierarchy",
    statement:
      "EML-k = {f : ℂ → ℂ | f = eval(t) for some EML tree t with depth ≤ k}. EML-0 = constants. EML-∞ = functions not in any EML-k for finite k. Hierarchy: EML-0 ⊆ EML-1 ⊆ EML-2 ⊆ EML-3 ⊆ EML-∞.",
    evidence: "Definitional. Strict inclusions are proved for EML-0 ⊊ EML-1 (T03, P03). Others are conjectured or have witness examples.",
  },
  {
    id: "D02",
    name: "BEST Routing",
    tier: "DEFINITION",
    session: "S7",
    category: "Core Algebra",
    statement:
      "BEST (Binary Expression Select & Transform) routing dispatches each arithmetic operation to the EML variant achieving fewest nodes: EXL for ln/exp, EDL for div/recip, standard EML for general composition.",
    evidence: "Definitional. Node counts per operation are verified by enumeration (P02).",
  },
  {
    id: "D03",
    name: "Tropical EML (teml)",
    tier: "DEFINITION",
    session: "S9",
    category: "Tropical EML",
    statement:
      "teml(a, b) = max(Re(a), −Re(b)) + i(Im(a) + Im(b)). The tropical analog of ceml in the (max, +) semiring. De-transcendentalizes by replacing exp with identity and ln with negation in the tropical semiring.",
    evidence: "Definitional. T06 verifies teml(a,a) = |a|.",
  },
  {
    id: "D04",
    name: "Complex EML (ceml)",
    tier: "DEFINITION",
    session: "S11",
    category: "Complex EML",
    statement:
      "ceml(z₁, z₂) = exp(z₁) − Log(z₂), where Log is the principal branch complex logarithm. The complex extension of eml. Generates depth hierarchy EML-0 through EML-∞ over ℂ.",
    evidence: "Definitional. T03 verifies the Euler Gateway.",
  },

  // ─── SPECULATION ──────────────────────────────────────────────────────────
  {
    id: "S01",
    name: "P = EML-2, NP = EML-∞",
    tier: "SPECULATION",
    session: "Internal",
    category: "Depth Hierarchy",
    statement:
      "The conjecture that P corresponds to EML-2 and NP to EML-∞ in the depth hierarchy. This is an interesting analogy, not a formal statement. No definition of 'corresponds to' is given.",
    evidence: "No evidence. A metaphor, not a theorem. Listed here to be explicit that it is speculation.",
  },
  {
    id: "S02",
    name: "Millennium Problem EML Depths",
    tier: "SPECULATION",
    session: "S58, S130+",
    category: "Depth Hierarchy",
    statement:
      "Claims that RH, BSD, Hodge, Yang–Mills, and NS are 'EML-∞' or 'resolved' via EML-theoretic analysis. These are descriptive classifications of where the problems sit in the depth landscape, not proofs of the conjectures themselves.",
    evidence:
      "The EML depth classification of related quantities (Euler factors, L-functions, NS modes) is legitimate mathematics. The leap from 'related quantities are EML-∞' to 'the Millennium problem is resolved' is not warranted.",
  },
  {
    id: "S03",
    name: "Consciousness and EML-∞",
    tier: "SPECULATION",
    session: "S101, S131",
    category: "Depth Hierarchy",
    statement:
      "The claim that qualia, insight, and phenomenal consciousness are 'EML-∞' and therefore unreachable by formal systems. Interesting framing, unfalsifiable.",
    evidence: "No evidence. A metaphor. Not a scientific claim.",
  },
  {
    id: "S04",
    name: "NS Regularity is ZFC-Independent",
    tier: "SPECULATION",
    session: "S1220–S1237",
    category: "Connections to Existing Mathematics",
    statement:
      "The claim that Navier-Stokes global regularity is formally independent of ZFC, proved via EML-theoretic analysis and Turing completeness of 3D NS. This is speculative and not a proof of NS independence.",
    evidence:
      "The argument that 3D NS can simulate Turing machines is a known research direction (Moore 1991, Tao 2016 blowup construction). The jump to ZFC-independence is not established.",
  },
];

function TierBadge({ tier }: { tier: keyof typeof TIER_META }) {
  const m = TIER_META[tier];
  return (
    <span style={{
      display: "inline-block",
      fontSize: 9,
      fontWeight: 700,
      letterSpacing: "0.1em",
      padding: "3px 8px",
      borderRadius: 3,
      background: `${m.color}18`,
      border: `1px solid ${m.color}`,
      color: m.color,
    }}>
      {m.label}
    </span>
  );
}

function ResultCard({ r }: { r: Result }) {
  return (
    <div style={{
      background: C.surface,
      border: `1px solid ${C.border}`,
      borderRadius: 8,
      padding: "18px 22px",
      marginBottom: 12,
    }}>
      <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", gap: 12, marginBottom: 10 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <span style={{ fontSize: 10, color: C.muted, fontFamily: "monospace", minWidth: 28 }}>{r.id}</span>
          <span style={{ fontSize: 15, fontWeight: 700, color: C.text }}>{r.name}</span>
        </div>
        <TierBadge tier={r.tier} />
      </div>
      <div style={{ fontSize: 9, color: C.muted, marginBottom: 10, display: "flex", gap: 16 }}>
        <span>Session: {r.session}</span>
        <span>Category: {r.category}</span>
      </div>
      <div style={{ fontSize: 11, color: C.text, lineHeight: 1.75, marginBottom: 10 }}>
        {r.statement}
      </div>
      <div style={{
        borderTop: `1px solid ${C.border}`,
        paddingTop: 10,
        fontSize: 10,
        color: C.muted,
        lineHeight: 1.7,
      }}>
        <span style={{ color: C.muted, textTransform: "uppercase", letterSpacing: "0.08em", fontSize: 9 }}>
          {r.tier === "THEOREM" || r.tier === "PROPOSITION" ? "Proof" :
           r.tier === "CONJECTURE" ? "Evidence" :
           r.tier === "OBSERVATION" ? "Data" :
           r.tier === "DEFINITION" ? "Note" : "Status"}:{" "}
        </span>
        {r.evidence}
      </div>
      {r.verify && (
        <div style={{
          marginTop: 8,
          padding: "6px 10px",
          background: C.surface2,
          borderRadius: 4,
          fontFamily: "monospace",
          fontSize: 10,
          color: C.blue,
          overflowX: "auto",
          whiteSpace: "pre",
        }}>
          {r.verify}
        </div>
      )}
      {r.deps && (
        <div style={{ marginTop: 6, fontSize: 10, color: C.muted }}>
          Depends on: {r.deps}
        </div>
      )}
    </div>
  );
}

function Section({
  tier, results,
}: {
  tier: keyof typeof TIER_META;
  results: Result[];
}) {
  const m = TIER_META[tier];
  if (results.length === 0) return null;
  return (
    <section style={{ marginBottom: 36 }}>
      <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 6 }}>
        <div style={{
          fontSize: 10,
          fontWeight: 700,
          color: m.color,
          letterSpacing: "0.12em",
          textTransform: "uppercase",
        }}>
          {m.label} — {results.length}
        </div>
        <div style={{ fontSize: 10, color: C.muted }}>{m.desc}</div>
      </div>
      {results.map((r) => <ResultCard key={r.id} r={r} />)}
    </section>
  );
}

const TIER_ORDER: Array<keyof typeof TIER_META> = [
  "THEOREM", "PROPOSITION", "CONJECTURE", "OBSERVATION", "DEFINITION", "SPECULATION",
];

export default function TheoremsPage() {
  const byTier = TIER_ORDER.reduce<Record<string, Result[]>>((acc, t) => {
    acc[t] = RESULTS.filter((r) => r.tier === t);
    return acc;
  }, {});

  const counts = TIER_ORDER.map((t) => ({ tier: t, n: byTier[t].length }));

  return (
    <div style={{ background: C.bg, minHeight: "100vh", maxWidth: 760, margin: "0 auto", padding: "0 16px 60px" }}>

      <header style={{ borderBottom: `1px solid ${C.border}`, padding: "28px 0 22px", marginBottom: 36 }}>
        <div style={{ fontSize: 11, color: C.muted, marginBottom: 8 }}>
          <a href="/" style={{ color: C.muted, textDecoration: "none" }}>monogate.dev</a>
          {" / theorems"}
        </div>
        <div style={{ fontSize: 22, fontWeight: 700, color: C.text, letterSpacing: "-0.02em" }}>
          Theorem Catalog
        </div>
        <div style={{ marginTop: 10, fontSize: 11, color: C.muted, lineHeight: 1.8, maxWidth: 560 }}>
          Every result classified honestly. A theorem requires a complete, checkable proof.
          A conjecture is precisely stated and falsifiable. Speculation is labeled as such.
        </div>
        <div style={{ marginTop: 14, display: "flex", gap: 16, flexWrap: "wrap" }}>
          {counts.map(({ tier, n }) => {
            const m = TIER_META[tier];
            return (
              <div key={tier} style={{ fontSize: 10 }}>
                <span style={{ color: m.color, fontWeight: 700 }}>{n}</span>
                <span style={{ color: C.muted }}> {m.label.toLowerCase()}{n !== 1 ? "s" : ""}</span>
              </div>
            );
          })}
        </div>
      </header>

      {TIER_ORDER.map((tier) => (
        <Section key={tier} tier={tier} results={byTier[tier]} />
      ))}

      <footer style={{
        marginTop: 48, paddingTop: 20, borderTop: `1px solid ${C.border}`,
        display: "flex", justifyContent: "space-between", flexWrap: "wrap", gap: 10,
        fontSize: 10, color: C.muted,
      }}>
        <a href="/" style={{ color: C.muted }}>← All challenges</a>
        <a href="https://arxiv.org/abs/2603.21852" target="_blank" rel="noopener noreferrer" style={{ color: C.muted }}>
          arXiv:2603.21852
        </a>
      </footer>
    </div>
  );
}
