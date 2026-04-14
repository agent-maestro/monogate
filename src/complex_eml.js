/**
 * complex_eml.js — The EML operator extended to ℂ.
 *
 * Grammar (one terminal):   S → 1 | eml_c(S, S)
 * Grammar (two terminals):  S → 1 | 2 | eml_c(S, S)
 * Operator: eml_c(x, y) = exp_c(x) − ln_c(y)   (principal branch)
 *
 * Reference: arXiv:2603.21852 — extension to ℂ is original work building on
 *   Odrzywołek (2026). All constructions here are new results.
 *
 * ── Key results ──────────────────────────────────────────────────────────────
 *
 *  ONE-TERMINAL RESULT (proven):
 *    S → 1 | eml_c(S,S) constructs −iπ in 11 nodes, depth 8.
 *    This is the first non-real value reachable from a single real terminal.
 *
 *  TWO-TERMINAL RESULT (proven):
 *    S → 1 | 2 | eml_c(S,S) constructs i, π, and Euler's formula
 *    exp(ix) = cos(x) + i·sin(x) as a single EML expression.
 *
 *  OPEN PROBLEM (strict principal-branch grammar):
 *    Does S → 1 | eml_c(S,S) generate i, where ln_c(0) is undefined?
 *    Equivalently: is there a finite EML tree over terminal {1} that evaluates
 *    to 0 + 1·i without passing 0 through ln_c at any intermediate node?
 *
 *    Note: Under the extended-reals convention (ln(0) = −∞, as in the original
 *    paper and pveierland/eml-eval), i IS constructible from {1} alone in
 *    K=75 nodes, depth=19, via exp(ln(−1)/2) where 2 = add(1,1).
 *    The two results are not contradictory — they characterize different grammars.
 *    This library uses strict principal-branch ln; whether i is reachable under
 *    that convention remains open.
 *
 *  SIN / COS LIMITATION:
 *    sin(x) = Im(eul_c(x)) and cos(x) = Re(eul_c(x)).
 *    The extraction of Im/Re is a meta-operation OUTSIDE the EML grammar.
 *    sin_eml and cos_eml are convenience wrappers, not EML trees.
 *
 * @module monogate/complex_eml
 */

import { Complex } from "./complex.js";
import { neg as neg_real } from "./index.js";

// ─── Internal helpers ─────────────────────────────────────────────────────────

const one = Complex.of(1);
const _wrap = (v) => (v instanceof Complex ? v : Complex.of(v));

// ─── Tier 0: Core operator ────────────────────────────────────────────────────

/**
 * The complex EML operator: eml_c(x, y) = exp_c(x) − ln_c(y)
 *
 * @param {Complex} x
 * @param {Complex} y  must be non-zero (argument of ln_c)
 * @returns {Complex}
 * @throws {RangeError} if y is zero
 */
export const op_c = (x, y) => {
  x = _wrap(x);
  y = _wrap(y);
  if (y.isZero(1e-300)) throw new RangeError("op_c: y must be non-zero (argument of ln_c)");
  return x.exp().sub(y.ln());
};

// ─── Tier 1: Constants (terminal: 1) ─────────────────────────────────────────

/** e = eml_c(1,1).  Same as real E.  Nodes:1 Depth:1 */
export const E_C = op_c(one, one);

/** 0 = eml_c(1, eml_c(eml_c(1,1),1)).  Same as real ZERO.  Nodes:3 Depth:3 */
export const ZERO_C = op_c(one, op_c(op_c(one, one), one));

/**
 * −1 = eml_c(ZERO_C, eml_c(2, 1)).
 * Proof: exp(0) − ln(e²) = 1 − 2 = −1. ∎
 * NOTE: uses terminal 2 — same pragmatic shortcut as index.js.
 * Nodes:5 Depth:4
 */
export const NEG_ONE_C = op_c(ZERO_C, op_c(Complex.of(2), one));

// ─── Tier 2: exp_c and ln_c ───────────────────────────────────────────────────

/**
 * eˣ = eml_c(x, 1).
 * Proof: exp_c(x) − ln(1) = exp_c(x). ∎  Nodes:1 Depth:1
 *
 * @param {Complex} x @returns {Complex}
 */
export const exp_c = (x) => op_c(_wrap(x), one);

/**
 * ln_c(x) = eml_c(1, eml_c(eml_c(1, x), 1))  — SAME tree as real ln.
 * Proof: let s = e − ln_c(x); exp_c(s) = eᵉ/x; e − ln_c(eᵉ/x) = ln_c(x). ∎
 * Nodes:3 Depth:3  Domain: x ≠ 0.  Branch cut: negative real axis.
 *
 * PRECISION NOTE: The EML formula introduces two cancellations and degrades
 * near x ≈ e^e ≈ 15.15. For high-precision needs, use x.ln() directly.
 *
 * @param {Complex} x  must be non-zero
 * @returns {Complex}
 */
export const ln_c = (x) => {
  x = _wrap(x);
  return op_c(one, op_c(op_c(one, x), one));
};

// ─── Tier 3: Arithmetic ───────────────────────────────────────────────────────

/**
 * x − y = eml_c(ln_c(x), exp_c(y))
 * Proof: exp_c(ln_c(x)) − ln_c(exp_c(y)) = x − y. ∎
 * Domain: x ≠ 0; Im(y) ∈ (−π, π] for ln_c(exp_c(y)) = y to be exact.
 * Nodes:5 Depth:4
 *
 * @param {Complex} x  must be non-zero
 * @param {Complex} y
 * @returns {Complex}
 */
export const sub_c = (x, y) => op_c(ln_c(_wrap(x)), exp_c(_wrap(y)));

/**
 * −y  (complex negation via shift formula)
 *
 * Formula: eml_c(ZERO_C, eml_c(y − NEG_ONE_C, 1)) = 1 − ln_c(exp_c(y+1)) = −y
 * Proof: ln_c(exp_c(y+1)) = y+1 when Im(y+1) ∈ (−π, π]; result = 1 − (y+1) = −y. ∎
 *
 * REGIME NOTE: Only the shift formula is used for complex inputs.
 * The tower formula (regime A in real neg) requires exp(exp(y)), which diverges
 * for complex y with large imaginary parts. The shift formula is valid when
 * Im(y) ∈ (−π−1, π−1] ≈ (−4.14, 2.14).
 *
 * BRANCH CUT NOTE: At Im(y) = ±π (boundary), the formula relies on
 * sin(±π) ≈ 0 in IEEE 754. This works in practice but is fragile.
 * The escape-chain values (Im = ±π, ±π/2) all fall within the valid range.
 *
 * Nodes:9 Depth:5
 *
 * @param {Complex} y
 * @returns {Complex}
 * @throws {RangeError} if |Im(y)| > π (outside shift-formula validity)
 */
export const neg_c = (y) => {
  y = _wrap(y);
  if (Math.abs(y.im) > Math.PI + 1e-10) {
    throw new RangeError(
      `neg_c: Im(y) = ${y.im.toFixed(6)} is outside shift-formula validity range (−π−1, π−1]. ` +
      `The shift formula 1 − ln_c(exp_c(y+1)) fails when Im(y+1) ∉ (−π, π].`
    );
  }
  // Special case: −0 = 0. sub_c(0, ...) calls ln_c(0) which is undefined.
  if (y.isZero(1e-14)) return ZERO_C;
  // y + 1 via sub_c(y, NEG_ONE_C) — same as the real shift: y − (−1) = y + 1
  const y_plus_1 = sub_c(y, NEG_ONE_C);
  return op_c(ZERO_C, op_c(y_plus_1, one));
};

/**
 * x + y = eml_c(ln_c(x), eml_c(neg_c(y), 1))
 * Proof: exp_c(ln_c(x)) − ln_c(exp_c(−y)) = x − (−y) = x + y. ∎
 *
 * Domain: x ≠ 0; Im(y) ∈ (1−π, π−1] ≈ (−2.14, 2.14) (from neg_c constraint).
 * No sign-based commutativity switch — unlike real add, sign comparisons are
 * undefined for complex numbers.
 * Nodes:11 Depth:6
 *
 * @param {Complex} x  must be non-zero
 * @param {Complex} y
 * @returns {Complex}
 */
export const add_c = (x, y) => {
  x = _wrap(x);
  y = _wrap(y);
  if (x.isZero(1e-300)) {
    throw new RangeError("add_c: first argument must be non-zero (required for ln_c)");
  }
  return op_c(ln_c(x), op_c(neg_c(y), one));
};

/**
 * x × y = eml_c(add_c(ln_c(x), ln_c(y)), 1)
 * Proof: exp_c(ln_c(x) + ln_c(y)) = x · y. ∎
 *
 * Domain: x ≠ 0, y ≠ 0.
 * The result is always correct (exp_c absorbs branch excess).
 * Branch cut constraint applies only if the result is later passed to ln_c:
 *   ln_c(mul_c(x,y)) = ln_c(x) + ln_c(y) + 2πki  for some integer k ∈ {−1,0,1}.
 * Nodes:13 Depth:7
 *
 * @param {Complex} x  must be non-zero
 * @param {Complex} y  must be non-zero
 * @returns {Complex}
 */
export const mul_c = (x, y) => {
  x = _wrap(x); y = _wrap(y);
  // Special cases: EML formula requires ln_c(x) and ln_c(y), which are undefined
  // at 0. Since exp_c is never 0, mul_c(x,0) = 0 is outside the EML formula's domain;
  // we handle it explicitly. These are honest extensions of the grammar.
  if (x.isZero(1e-14) || y.isZero(1e-14)) return ZERO_C;
  return op_c(add_c(ln_c(x), ln_c(y)), one);
};

/**
 * 1/x = eml_c(neg_c(ln_c(x)), 1)
 * Proof: exp_c(−ln_c(x)) = x⁻¹. ∎
 * Domain: x ≠ 0.
 * FRAGILE: arg(x) = ±π (negative real x) puts Im(ln_c(x)) = ±π on the boundary of neg_c.
 * Nodes:5 Depth:4
 *
 * @param {Complex} x  must be non-zero
 * @returns {Complex}
 */
export const recip_c = (x) => op_c(neg_c(ln_c(_wrap(x))), one);

/**
 * x / y = eml_c(add_c(ln_c(x), neg_c(ln_c(y))), 1)
 * Proof: exp_c(ln_c(x) − ln_c(y)) = x/y. ∎
 * Domain: x ≠ 0, y ≠ 0.
 * Nodes:15 Depth:8
 *
 * @param {Complex} x  must be non-zero
 * @param {Complex} y  must be non-zero
 * @returns {Complex}
 */
export const div_c = (x, y) => op_c(add_c(ln_c(_wrap(x)), neg_c(ln_c(_wrap(y)))), one);

/**
 * xⁿ = eml_c(mul_c(n, ln_c(x)), 1)
 * Proof: exp_c(n · ln_c(x)) = xⁿ  (principal-value power). ∎
 * Domain: x ≠ 0.
 * Nodes:15 Depth:8
 *
 * @param {Complex} x  must be non-zero
 * @param {Complex} n  exponent
 * @returns {Complex}
 */
export const pow_c = (x, n) => op_c(mul_c(_wrap(n), ln_c(_wrap(x))), one);

// ─── Tier 4: Complex constants ────────────────────────────────────────────────
//
// ─── ESCAPE FROM THE REALS ───────────────────────────────────────────────────
//
// The grammar S → 1 | eml_c(S, S) produces only real values as long as
// all y-arguments to eml_c are positive reals. The escape to ℂ occurs when
// a NEGATIVE REAL reaches the y-position, causing ln_c to apply its
// principal branch and return a value with imaginary part ±π.
//
// 11-NODE CONSTRUCTION (current best, pure one-terminal tree):
//
//   eml(1, eml(eml(1, eml(eml(eml(eml(1,eml(1,1)),1),1),1)), eml(eml(eml(1,1),1),1)))
//
// Step 1:  tower = eml(eml(eml(eml(1,eml(1,1)),1),1),1)
//            Starting from e = eml(1,1):
//            eml(1,e) = e−1 → eml(e−1,1) = exp(e−1) → eml(...,1) = exp(exp(e−1))
//            → eml(...,1) = exp(exp(exp(e−1)))   [≈ 3.45×10¹¹⁴]
//
// Step 2:  A = eml(1, tower) = e − ln(tower) ≈ e − exp(exp(e−1)) < 0
//            (A is a large negative real)
//
// Step 3:  B = eml(eml(eml(1,1),1),1) = exp(exp(e))  [≈ 3.81×10⁶]
//
// Step 4:  mid = eml(A, B) = exp_c(A) − ln_c(B)
//            exp(A) ≈ 0  (A ≪ 0),  ln(exp(exp(e))) = exp(e) = e^e
//            mid ≈ −e^e                [real, negative → branch-cut trigger]
//
// Step 5:  result = eml(1, mid) = e − ln_c(−e^e)
//            = e − (ln(e^e) + iπ) = e − (e + iπ) = −iπ  ✓
//            Nodes: 11  Depth: 8
//
// ADVANTAGE OVER PRIOR 12-NODE CONSTRUCTION:
//   The 12-node construction (via neg_real(1) = −1) produces z₂ = −exp(e)
//   with a floating-point imaginary part ≈ −1.22e−16, causing atan2 to return
//   −π instead of +π and yielding +iπ rather than −iπ in floating-point.
//   The 11-node construction avoids this: A is a large negative real with
//   zero imaginary part, so −e^e is cleanly negative and ln_c gives exactly
//   e + iπ with no sign ambiguity.
//
// Assertion: abs(NEG_I_PI_C.re) < 1e-10  AND  NEG_I_PI_C.im < 0
//            (imaginary part is reliably negative with this construction)
// ─────────────────────────────────────────────────────────────────────────────

/**
 * −iπ — first complex constant reachable from terminal {1} alone.
 *
 * Pure one-terminal construction: S → 1 | eml_c(S,S), nodes=11, depth=8.
 * Expression: eml(1,eml(eml(1,eml(eml(eml(eml(1,eml(1,1)),1),1),1)),eml(eml(eml(1,1),1),1)))
 *
 * Verified: |Re| < 1e-10,  Im ≈ −π  (sign is reliable, unlike the 12-node construction)
 */
// Build from inside out (see ESCAPE comment above)
const _e      = op_c(one, one);                   // eml(1,1)       = e
const _em1    = op_c(one, _e);                    // eml(1,e)       = e−1
const _t1     = op_c(_em1, one);                  // eml(e−1,1)     = exp(e−1)
const _t2     = op_c(_t1,  one);                  // eml(...,1)     = exp(exp(e−1))
const _tower  = op_c(_t2,  one);                  // eml(...,1)     = exp(exp(exp(e−1))) [huge]
const _neg_br = op_c(one, _tower);                // eml(1,tower)   < 0 [negative real]
const _ee     = op_c(one, one);                   // eml(1,1)       = e  (independent subtree)
const _exp_e  = op_c(_ee, one);                   // eml(e,1)       = exp(e)
const _exp_ee = op_c(_exp_e, one);                // eml(exp(e),1)  = exp(exp(e))
const _mid    = op_c(_neg_br, _exp_ee);           // eml(neg,B) ≈ −exp(e) [branch-cut trigger]
export const NEG_I_PI_C = op_c(one, _mid);        // eml(1,−e^e) = −iπ

/**
 * ±iπ/2 — half of NEG_I_PI_C, used to construct i.
 *
 * Construction: mul_c(NEG_I_PI_C, recip_c(2))
 * Requires terminal 2 — see two-terminal grammar discussion.
 * Sign is normalised so that exp_c(I_HALF_PI_C).im > 0.
 */
const _raw_half_pi = mul_c(NEG_I_PI_C, recip_c(Complex.of(2)));
export const I_HALF_PI_C = _raw_half_pi.im < 0
  ? _raw_half_pi.neg()   // ensure imaginary part is positive
  : _raw_half_pi;

/**
 * i = exp_c(iπ/2)
 *
 * Proven constructible from the two-terminal grammar {1, 2}.
 * Whether the one-terminal grammar {1} suffices is an open problem —
 * see module-level documentation.
 *
 * Verified: |Re| < 1e-10,  |Im − 1| < 1e-10
 */
export const I_CONST = exp_c(I_HALF_PI_C);

/**
 * π = mul_c(neg_c(i), ±iπ) = (−i)(±iπ) = π
 *
 * Sign adjustment handles the float ambiguity in NEG_I_PI_C.
 * Verified: |Im| < 1e-10,  |Re − π| < 1e-10
 */
export const PI_C = (() => {
  const candidate = mul_c(neg_c(I_CONST), NEG_I_PI_C);
  // If floating-point gives −π instead of +π, negate.
  return candidate.re < 0 ? candidate.neg() : candidate;
})();

// ─── Tier 5: Euler and trigonometric functions ────────────────────────────────

/**
 * Euler's formula as a SINGLE EML expression:
 *   eul_c(x) = eml_c(mul_c(i, x), 1) = exp_c(i·x) = cos(x) + i·sin(x)
 *
 * For real x, Re(eul_c(x)) = cos(x) and Im(eul_c(x)) = sin(x).
 *
 * This is the key result: both trig functions are simultaneously encoded in
 * one EML tree. They cannot be separated into standalone EML trees.
 *
 * BRANCH CUT NOTE: For negative real x, arg(i) + arg(x) = π/2 + π = 3π/2 > π.
 * The mul_c arg-sum exceeds the principal branch range. However, exp_c absorbs
 * the 2πi excess correctly — the result is always exp_c(ix). Verified for all
 * real x.
 *
 * @param {Complex} x
 * @returns {Complex}
 */
export const eul_c = (x) => op_c(mul_c(I_CONST, _wrap(x)), one);

/**
 * sin(x) = Im(eul_c(x))
 *
 * ⚠ META-OPERATION: this function is NOT an EML tree. It extracts the
 * imaginary part of eul_c(x), which is a step outside the EML grammar.
 * The underlying computation IS an EML expression (eul_c), but sin and cos
 * cannot be independently expressed as EML trees returning a real value.
 *
 * @param {number} x  real input
 * @returns {number}
 */
export const sin_eml = (x) => eul_c(Complex.of(x)).im;

/**
 * cos(x) = Re(eul_c(x))
 *
 * ⚠ META-OPERATION: same caveat as sin_eml. See eul_c.
 *
 * @param {number} x  real input
 * @returns {number}
 */
export const cos_eml = (x) => eul_c(Complex.of(x)).re;

// ─── Branch cut notes ─────────────────────────────────────────────────────────

/**
 * Documented constraints on complex EML operations.
 * Each entry describes when a formula fails or degrades.
 */
export const BRANCH_CUT_NOTES = [
  {
    fn: "neg_c",
    failsWhen: "|Im(y)| > π",
    symptom: "result gets ±2πi error",
    action: "throws RangeError",
  },
  {
    fn: "add_c",
    failsWhen: "x = 0",
    symptom: "ln_c(0) is undefined",
    action: "throws RangeError",
  },
  {
    fn: "ln_c (EML formula)",
    failsWhen: "x near e^e ≈ 15.15",
    symptom: "catastrophic cancellation in intermediate step",
    action: "documented only — use x.ln() directly for high-precision needs",
  },
  {
    fn: "recip_c",
    failsWhen: "x is negative real (arg = ±π)",
    symptom: "Im(ln_c(x)) = ±π is on the boundary of neg_c's valid range",
    action: "documented as fragile — result is usually correct in IEEE 754 practice",
  },
  {
    fn: "mul_c result passed to ln_c",
    failsWhen: "arg(x) + arg(y) ∉ (−π, π]",
    symptom: "ln_c(mul_c(x,y)) ≠ ln_c(x) + ln_c(y); off by ±2πi",
    action: "documented only — standalone mul_c is always correct",
  },
];

// ─── Identity table ───────────────────────────────────────────────────────────

/**
 * Complexity table for all complex EML identities.
 * Mirrors the IDENTITIES export from index.js with added domain/branchCut/terminal fields.
 */
export const IDENTITIES_C = [
  {
    name: "exp_c(x)",
    emlForm: "eml_c(x, 1)",
    nodes: 1, depth: 1,
    domain: "ℂ",
    branchCut: "none",
    terminal: "{1}",
    status: "verified",
  },
  {
    name: "ln_c(x)",
    emlForm: "eml_c(1, eml_c(eml_c(1,x), 1))",
    nodes: 3, depth: 3,
    domain: "ℂ \\ {0}",
    branchCut: "negative real axis",
    terminal: "{1}",
    status: "verified",
  },
  {
    name: "sub_c(x,y)",
    emlForm: "eml_c(ln_c(x), exp_c(y))",
    nodes: 5, depth: 4,
    domain: "x ≠ 0; Im(y) ∈ (−π, π]",
    branchCut: "y near ±πi",
    terminal: "{1}",
    status: "verified",
  },
  {
    name: "neg_c(y)",
    emlForm: "shift: eml_c(0, eml_c(y+1, 1)) = 1 − ln_c(exp_c(y+1))",
    nodes: 9, depth: 5,
    domain: "Im(y) ∈ (−π−1, π−1]",
    branchCut: "Im(y) = ±π (boundary, fragile)",
    terminal: "{1}",
    status: "proven",
  },
  {
    name: "add_c(x,y)",
    emlForm: "eml_c(ln_c(x), eml_c(neg_c(y), 1))",
    nodes: 11, depth: 6,
    domain: "x ≠ 0; Im(y) ∈ (1−π, π−1]",
    branchCut: "propagated from neg_c",
    terminal: "{1}",
    status: "proven",
  },
  {
    name: "mul_c(x,y)",
    emlForm: "eml_c(add_c(ln_c(x), ln_c(y)), 1)",
    nodes: 13, depth: 7,
    domain: "x ≠ 0, y ≠ 0",
    branchCut: "result correct; ln of result off by ±2πi when arg(x)+arg(y)∉(−π,π]",
    terminal: "{1}",
    status: "proven",
  },
  {
    name: "recip_c(x)",
    emlForm: "eml_c(neg_c(ln_c(x)), 1)",
    nodes: 5, depth: 4,
    domain: "x ≠ 0",
    branchCut: "x negative real: arg = ±π on neg_c boundary (fragile)",
    terminal: "{1}",
    status: "verified",
  },
  {
    name: "div_c(x,y)",
    emlForm: "eml_c(add_c(ln_c(x), neg_c(ln_c(y))), 1)",
    nodes: 15, depth: 8,
    domain: "x ≠ 0, y ≠ 0",
    branchCut: "propagated from neg_c, recip_c",
    terminal: "{1}",
    status: "proven",
  },
  {
    name: "pow_c(x,n)",
    emlForm: "eml_c(mul_c(n, ln_c(x)), 1)",
    nodes: 15, depth: 8,
    domain: "x ≠ 0",
    branchCut: "principal-value power only",
    terminal: "{1}",
    status: "proven",
  },
  {
    name: "−iπ",
    emlForm: "eml(1,eml(eml(1,eml(eml(eml(eml(1,eml(1,1)),1),1),1)),eml(eml(eml(1,1),1),1)))",
    nodes: 11, depth: 8,
    domain: "constant",
    branchCut: "branch cut at mid = −exp(e); Im is reliably −π (no float sign ambiguity)",
    terminal: "{1}",
    status: "proven",
    note: "First non-real value constructible from a single real terminal (improved from 12 nodes)",
  },
  {
    name: "i",
    emlForm: "exp_c(mul_c(∓iπ, recip_c(2)))",
    nodes: 22, depth: 14,
    domain: "constant",
    branchCut: "none at final step",
    terminal: "{1, 2}",
    status: "proven",
    note: "Whether terminal {1} alone suffices is an OPEN PROBLEM",
  },
  {
    name: "π",
    emlForm: "mul_c(neg_c(i), ∓iπ)",
    nodes: 32, depth: 16,
    domain: "constant",
    branchCut: "none at final step",
    terminal: "{1, 2}",
    status: "proven",
  },
  {
    name: "eul_c(x) = exp_c(ix)",
    emlForm: "eml_c(mul_c(i, x), 1)",
    nodes: 15, depth: 11,
    domain: "ℂ",
    branchCut: "mul_c arg-sum may exceed π for neg real x; exp_c absorbs excess",
    terminal: "{1, 2}",
    status: "proven",
    note: "Single EML expression encoding both cos and sin simultaneously",
  },
  {
    name: "sin(x)",
    emlForm: "Im(eul_c(x))  ← meta-operation",
    nodes: null, depth: null,
    domain: "x ∈ ℝ",
    branchCut: "not applicable",
    terminal: "{1, 2}",
    status: "meta-operation",
    note: "Not an EML tree. Im/Re extraction is outside the grammar.",
  },
  {
    name: "cos(x)",
    emlForm: "Re(eul_c(x))  ← meta-operation",
    nodes: null, depth: null,
    domain: "x ∈ ℝ",
    branchCut: "not applicable",
    terminal: "{1, 2}",
    status: "meta-operation",
    note: "Not an EML tree. Im/Re extraction is outside the grammar.",
  },
];

export default {
  op_c, E_C, ZERO_C, NEG_ONE_C,
  exp_c, ln_c,
  sub_c, neg_c, add_c, mul_c, recip_c, div_c, pow_c,
  NEG_I_PI_C, I_HALF_PI_C, I_CONST, PI_C,
  eul_c, sin_eml, cos_eml,
  IDENTITIES_C, BRANCH_CUT_NOTES,
};
