import { describe, it, expect } from "vitest";
import { Complex } from "./complex.js";

const TIGHT = 1e-14; // direct arithmetic
const TOL   = 1e-10; // EML chains

const near = (a, b, tol = TIGHT) => Math.abs(a - b) <= tol;

describe("Complex — factories", () => {
  it("of(re, im)", () => {
    const z = Complex.of(3, -4);
    expect(z.re).toBe(3);
    expect(z.im).toBe(-4);
  });

  it("of(re) defaults im to 0", () => {
    expect(Complex.of(5).im).toBe(0);
  });

  it("fromPolar(r, theta)", () => {
    const z = Complex.fromPolar(2, Math.PI / 2);
    expect(near(z.re, 0)).toBe(true);
    expect(near(z.im, 2)).toBe(true);
  });

  it("real(x) alias", () => {
    const z = Complex.real(7);
    expect(z.re).toBe(7);
    expect(z.im).toBe(0);
  });

  it("is frozen / immutable", () => {
    const z = Complex.of(1, 2);
    expect(() => { z.re = 99; }).toThrow();
  });
});

describe("Complex — arithmetic", () => {
  const a = Complex.of(3, 4);
  const b = Complex.of(1, -2);

  it("add", () => {
    const r = a.add(b);
    expect(r.re).toBe(4);
    expect(r.im).toBe(2);
  });

  it("sub", () => {
    const r = a.sub(b);
    expect(r.re).toBe(2);
    expect(r.im).toBe(6);
  });

  it("mul: (3+4i)(1-2i) = 11-2i", () => {
    const r = a.mul(b);
    expect(r.re).toBe(11);
    expect(r.im).toBe(-2);
  });

  it("div: (3+4i)/(1-2i) = -1+2i", () => {
    const r = a.div(b);
    expect(near(r.re, -1)).toBe(true);
    expect(near(r.im,  2)).toBe(true);
  });

  it("neg", () => {
    expect(a.neg().re).toBe(-3);
    expect(a.neg().im).toBe(-4);
  });

  it("conj", () => {
    expect(a.conj().re).toBe(3);
    expect(a.conj().im).toBe(-4);
  });

  it("recip: 1/(3+4i) = 3/25 - 4/25·i", () => {
    const r = a.recip();
    expect(near(r.re, 3/25)).toBe(true);
    expect(near(r.im, -4/25)).toBe(true);
  });

  it("scale", () => {
    const r = a.scale(2);
    expect(r.re).toBe(6);
    expect(r.im).toBe(8);
  });

  it("z · z.recip() ≈ 1", () => {
    const r = a.mul(a.recip());
    expect(near(r.re, 1)).toBe(true);
    expect(near(r.im, 0)).toBe(true);
  });
});

describe("Complex — measurement", () => {
  it("abs of 3+4i = 5", () => {
    expect(near(Complex.of(3, 4).abs(), 5)).toBe(true);
  });

  it("arg of i = π/2", () => {
    expect(near(Complex.of(0, 1).arg(), Math.PI / 2)).toBe(true);
  });

  it("arg of −1 = π", () => {
    expect(near(Complex.of(-1, 0).arg(), Math.PI)).toBe(true);
  });

  it("absSquared", () => {
    expect(Complex.of(3, 4).absSquared()).toBe(25);
  });
});

describe("Complex — transcendental", () => {
  it("exp(0) = 1", () => {
    const r = Complex.of(0).exp();
    expect(near(r.re, 1)).toBe(true);
    expect(near(r.im, 0)).toBe(true);
  });

  it("exp(1) = e", () => {
    expect(near(Complex.of(1).exp().re, Math.E)).toBe(true);
  });

  it("exp(iπ) = −1  (Euler's identity)", () => {
    const r = Complex.of(0, Math.PI).exp();
    expect(near(r.re, -1)).toBe(true);
    expect(near(r.im,  0)).toBe(true);
  });

  it("ln(e) = 1", () => {
    const r = Complex.of(Math.E).ln();
    expect(near(r.re, 1)).toBe(true);
    expect(near(r.im, 0)).toBe(true);
  });

  it("ln(−1) = iπ  (principal branch)", () => {
    const r = Complex.of(-1).ln();
    expect(near(r.re, 0)).toBe(true);
    expect(near(r.im, Math.PI)).toBe(true);
  });

  it("ln(i) = iπ/2", () => {
    const r = Complex.of(0, 1).ln();
    expect(near(r.re, 0)).toBe(true);
    expect(near(r.im, Math.PI / 2)).toBe(true);
  });

  it("exp(ln(z)) = z for various z", () => {
    const zs = [
      Complex.of(2, 3),
      Complex.of(-1, 1),
      Complex.of(0.5, -0.7),
    ];
    for (const z of zs) {
      const r = z.ln().exp();
      expect(near(r.re, z.re)).toBe(true);
      expect(near(r.im, z.im)).toBe(true);
    }
  });

  it("ln(0) throws", () => {
    expect(() => Complex.of(0).ln()).toThrow(RangeError);
  });

  it("pow: i² = −1", () => {
    const i = Complex.of(0, 1);
    const r = i.pow(Complex.of(2));
    expect(near(r.re, -1)).toBe(true);
    expect(near(r.im,  0)).toBe(true);
  });
});

describe("Complex — predicates and equality", () => {
  it("isZero", () => {
    expect(Complex.of(0, 0).isZero()).toBe(true);
    expect(Complex.of(1e-15).isZero(1e-14)).toBe(true);
    expect(Complex.of(1).isZero()).toBe(false);
  });

  it("isReal", () => {
    expect(Complex.of(5).isReal()).toBe(true);
    expect(Complex.of(5, 1e-13).isReal(1e-12)).toBe(true);
    expect(Complex.of(5, 1).isReal()).toBe(false);
  });

  it("isPureImaginary", () => {
    expect(Complex.of(0, 3).isPureImaginary()).toBe(true);
    expect(Complex.of(1, 3).isPureImaginary()).toBe(false);
    expect(Complex.of(0).isPureImaginary()).toBe(false);
  });

  it("equals with tolerance", () => {
    expect(Complex.of(1, 2).equals(Complex.of(1 + 1e-11, 2))).toBe(true);
    expect(Complex.of(1, 2).equals(Complex.of(1 + 1e-9, 2))).toBe(false);
  });
});

describe("Complex — toString", () => {
  it("real-only", () => expect(Complex.of(3).toString()).toBe("3"));
  it("imaginary-only", () => expect(Complex.of(0, 2).toString()).toBe("2i"));
  it("pure i", () => expect(Complex.of(0, 1).toString()).toBe("i"));
  it("negative imaginary", () => expect(Complex.of(0, -1).toString()).toBe("-i"));
  it("a+bi", () => expect(Complex.of(3, 4).toString()).toBe("3+4i"));
  it("a-bi", () => expect(Complex.of(3, -4).toString()).toBe("3-4i"));
  it("zero", () => expect(Complex.of(0, 0).toString()).toBe("0"));
});
