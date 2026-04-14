/**
 * complex.js — Immutable complex number type for the monogate EML system.
 *
 * This file provides standard ℂ arithmetic. It does NOT use EML grammar
 * constructions — it is the numeric substrate for complex_eml.js.
 *
 * All transcendental functions use the PRINCIPAL BRANCH of ln:
 *   arg(z) ∈ (−π, π]   (branch cut on the negative real axis)
 *
 * Precision: results accurate to machine epsilon (~1e-15) away from branch
 * cuts. Near the negative real axis (|Im| < 1e-12, Re < 0) arg() is subject
 * to the sign-of-zero ambiguity in IEEE 754 — this is the source of the
 * floating-point ±iπ sign in the EML escape-from-reals chain.
 *
 * @module monogate/complex
 */

export class Complex {
  /**
   * @param {number} re  real part
   * @param {number} im  imaginary part (default 0)
   */
  constructor(re, im = 0) {
    this.re = re;
    this.im = im;
    Object.freeze(this);
  }

  // ─── Factories ──────────────────────────────────────────────────────────────

  /** @param {number} re @param {number} [im=0] @returns {Complex} */
  static of(re, im = 0) { return new Complex(re, im); }

  /**
   * r · exp(iθ)
   * @param {number} r    magnitude (must be ≥ 0)
   * @param {number} theta argument in radians
   * @returns {Complex}
   */
  static fromPolar(r, theta) {
    return new Complex(r * Math.cos(theta), r * Math.sin(theta));
  }

  /** @param {number} x @returns {Complex} */
  static real(x) { return new Complex(x, 0); }

  // ─── Arithmetic ─────────────────────────────────────────────────────────────

  /** @param {Complex} other @returns {Complex} */
  add(other) {
    return new Complex(this.re + other.re, this.im + other.im);
  }

  /** @param {Complex} other @returns {Complex} */
  sub(other) {
    return new Complex(this.re - other.re, this.im - other.im);
  }

  /**
   * (a + bi)(c + di) = (ac − bd) + (ad + bc)i
   * @param {Complex} other @returns {Complex}
   */
  mul(other) {
    return new Complex(
      this.re * other.re - this.im * other.im,
      this.re * other.im + this.im * other.re,
    );
  }

  /**
   * Division via conjugate: this / other = (this · conj(other)) / |other|²
   * @param {Complex} other @returns {Complex}
   */
  div(other) {
    const d = other.absSquared();
    return new Complex(
      (this.re * other.re + this.im * other.im) / d,
      (this.im * other.re - this.re * other.im) / d,
    );
  }

  /** Additive inverse. @returns {Complex} */
  neg() { return new Complex(-this.re, -this.im); }

  /** Complex conjugate. @returns {Complex} */
  conj() { return new Complex(this.re, -this.im); }

  /**
   * Multiplicative inverse: 1/z = conj(z) / |z|²
   * @returns {Complex}
   */
  recip() {
    const d = this.absSquared();
    return new Complex(this.re / d, -this.im / d);
  }

  /**
   * Scale by a real scalar.
   * @param {number} r @returns {Complex}
   */
  scale(r) { return new Complex(this.re * r, this.im * r); }

  // ─── Transcendental (principal branch) ──────────────────────────────────────

  /**
   * exp(z) = e^re · (cos(im) + i·sin(im))
   * @returns {Complex}
   */
  exp() {
    return Complex.fromPolar(Math.exp(this.re), this.im);
  }

  /**
   * Principal branch of ln(z): ln|z| + i·arg(z), arg ∈ (−π, π].
   * Branch cut: negative real axis.
   * @returns {Complex}
   * @throws {RangeError} if z = 0
   */
  ln() {
    if (this.isZero()) throw new RangeError("ln_c: argument must be non-zero");
    return new Complex(Math.log(this.abs()), this.arg());
  }

  /**
   * Principal-value power: z^w = exp(w · ln(z))
   * @param {Complex} w @returns {Complex}
   */
  pow(w) {
    return this.ln().mul(w).exp();
  }

  // ─── Measurement ────────────────────────────────────────────────────────────

  /**
   * |z| = hypot(re, im)  — uses Math.hypot to avoid overflow on large components.
   * @returns {number}
   */
  abs() { return Math.hypot(this.re, this.im); }

  /**
   * arg(z) = atan2(im, re) ∈ (−π, π]
   * @returns {number}
   */
  arg() { return Math.atan2(this.im, this.re); }

  /** |z|² = re² + im²  (cheaper than abs() when only comparing magnitudes). @returns {number} */
  absSquared() { return this.re * this.re + this.im * this.im; }

  // ─── Predicates ─────────────────────────────────────────────────────────────

  /** @param {number} [tol=0] @returns {boolean} */
  isZero(tol = 0) { return this.abs() <= tol; }

  /** @param {number} [tol=0] @returns {boolean} */
  isReal(tol = 0) { return Math.abs(this.im) <= tol; }

  /** @param {number} [tol=0] @returns {boolean} */
  isPureImaginary(tol = 0) {
    return Math.abs(this.re) <= tol && !this.isZero(tol);
  }

  // ─── Equality ───────────────────────────────────────────────────────────────

  /**
   * Component-wise approximate equality.
   * @param {Complex} other
   * @param {number} [tol=1e-10]
   * @returns {boolean}
   */
  equals(other, tol = 1e-10) {
    return Math.abs(this.re - other.re) <= tol && Math.abs(this.im - other.im) <= tol;
  }

  // ─── Output ─────────────────────────────────────────────────────────────────

  /**
   * Human-readable form. Treats components with |value| < 1e-12 as zero.
   * Examples: "3", "-2i", "1+4i", "2.718-3.14i"
   * @returns {string}
   */
  toString() {
    const fmt = (v) => {
      const s = parseFloat(v.toPrecision(10)).toString();
      return s;
    };
    const EPS = 1e-12;
    const reZero = Math.abs(this.re) < EPS;
    const imZero = Math.abs(this.im) < EPS;

    if (reZero && imZero) return "0";
    if (imZero) return fmt(this.re);
    if (reZero) {
      if (Math.abs(this.im - 1) < EPS) return "i";
      if (Math.abs(this.im + 1) < EPS) return "-i";
      return `${fmt(this.im)}i`;
    }
    const sign = this.im < 0 ? "-" : "+";
    const absIm = Math.abs(this.im);
    const imStr = Math.abs(absIm - 1) < EPS ? "i" : `${fmt(absIm)}i`;
    return `${fmt(this.re)}${sign}${imStr}`;
  }

  /**
   * Fixed-decimal form for test output.
   * @param {number} digits @returns {string}
   */
  toFixed(digits) {
    return `${this.re.toFixed(digits)} + ${this.im.toFixed(digits)}i`;
  }
}

export default Complex;
