import { describe, it, expect } from "vitest";
import { Complex } from "./complex.js";
import {
  op_c,
  E_C, ZERO_C, NEG_ONE_C,
  exp_c, ln_c,
  sub_c, neg_c, add_c, mul_c, recip_c, div_c, pow_c,
  NEG_I_PI_C, I_HALF_PI_C, I_CONST, PI_C,
  eul_c, sin_eml, cos_eml,
  IDENTITIES_C, BRANCH_CUT_NOTES,
} from "./complex_eml.js";

const TOL  = 1e-10; // EML chain results
const DTOL = 1e-12; // direct Complex arithmetic reference comparisons

const near = (a, b, tol = TOL) => Math.abs(a - b) <= tol;
const nearC = (z, re, im, tol = TOL) =>
  Math.abs(z.re - re) <= tol && Math.abs(z.im - im) <= tol;

// ─── Core constants ────────────────────────────────────────────────────────────

describe("complex EML — constants", () => {
  it("E_C ≈ e", () => {
    expect(near(E_C.re, Math.E)).toBe(true);
    expect(near(E_C.im, 0)).toBe(true);
  });

  it("ZERO_C ≈ 0", () => {
    expect(near(ZERO_C.re, 0)).toBe(true);
    expect(near(ZERO_C.im, 0)).toBe(true);
  });

  it("NEG_ONE_C ≈ −1", () => {
    expect(near(NEG_ONE_C.re, -1)).toBe(true);
    expect(near(NEG_ONE_C.im, 0)).toBe(true);
  });
});

// ─── exp_c and ln_c ───────────────────────────────────────────────────────────

describe("exp_c", () => {
  it("exp_c(0) = 1", () => {
    expect(nearC(exp_c(Complex.of(0)), 1, 0)).toBe(true);
  });

  it("exp_c(1) = e", () => {
    expect(near(exp_c(Complex.of(1)).re, Math.E)).toBe(true);
  });

  it("exp_c(iπ) ≈ −1  (Euler's identity)", () => {
    const r = exp_c(Complex.of(0, Math.PI));
    expect(near(r.re, -1)).toBe(true);
    expect(near(r.im,  0)).toBe(true);
  });
});

describe("ln_c (EML formula)", () => {
  it("ln_c(e) = 1", () => {
    const r = ln_c(Complex.of(Math.E));
    expect(near(r.re, 1)).toBe(true);
    expect(near(r.im, 0)).toBe(true);
  });

  it("ln_c(1) = 0", () => {
    const r = ln_c(Complex.of(1));
    expect(near(r.re, 0, DTOL)).toBe(true);
    expect(near(r.im, 0, DTOL)).toBe(true);
  });

  it("ln_c(−1) ≈ iπ  (principal branch, may be −iπ; check |Im| = π)", () => {
    const r = ln_c(Complex.of(-1));
    expect(near(r.re, 0)).toBe(true);
    expect(near(Math.abs(r.im), Math.PI)).toBe(true);
  });

  it("EML ln_c matches direct .ln() for various inputs (tol 1e-12)", () => {
    const inputs = [
      Complex.of(2),
      Complex.of(0.5),
      Complex.of(1, 1),
      Complex.of(-0.5, 0.5),
      Complex.of(10),
    ];
    for (const z of inputs) {
      const eml = ln_c(z);
      const direct = z.ln();
      expect(near(eml.re, direct.re, DTOL)).toBe(true);
      expect(near(eml.im, direct.im, DTOL)).toBe(true);
    }
  });

  it("exp_c(ln_c(z)) ≈ z for Im(z) ∈ (−π, π)", () => {
    const zs = [Complex.of(2, 1), Complex.of(0.5, -0.7), Complex.of(-1, 0.5)];
    for (const z of zs) {
      const r = exp_c(ln_c(z));
      expect(near(r.re, z.re)).toBe(true);
      expect(near(r.im, z.im)).toBe(true);
    }
  });
});

// ─── Arithmetic ───────────────────────────────────────────────────────────────

describe("sub_c", () => {
  it("sub_c(3, 1) ≈ 2", () => {
    expect(nearC(sub_c(Complex.of(3), Complex.of(1)), 2, 0)).toBe(true);
  });

  it("sub_c(3+4i, 1+2i) ≈ 2+2i", () => {
    const r = sub_c(Complex.of(3, 4), Complex.of(1, 2));
    expect(nearC(r, 2, 2)).toBe(true);
  });
});

describe("neg_c", () => {
  it("neg_c(1) ≈ −1", () => {
    expect(nearC(neg_c(Complex.of(1)), -1, 0)).toBe(true);
  });

  it("neg_c(−1) ≈ 1", () => {
    expect(nearC(neg_c(Complex.of(-1)), 1, 0)).toBe(true);
  });

  it("neg_c(3+2i) ≈ −3−2i", () => {
    const r = neg_c(Complex.of(3, 2));
    expect(nearC(r, -3, -2)).toBe(true);
  });

  it("neg_c(neg_c(z)) ≈ z", () => {
    const z = Complex.of(2, 1);
    const r = neg_c(neg_c(z));
    expect(nearC(r, z.re, z.im)).toBe(true);
  });

  it("neg_c(z).add(z).isZero()", () => {
    const z = Complex.of(1.5, 0.7);
    const r = neg_c(z).add(z);
    expect(r.isZero(TOL)).toBe(true);
  });

  it("neg_c throws for |Im(y)| > π", () => {
    expect(() => neg_c(Complex.of(0, Math.PI + 0.1))).toThrow(RangeError);
    expect(() => neg_c(Complex.of(0, -(Math.PI + 0.1)))).toThrow(RangeError);
  });

  it("neg_c does NOT throw at boundary |Im| = π", () => {
    // At Im = ±π, the formula is fragile but works in IEEE 754 practice
    expect(() => neg_c(Complex.of(0, Math.PI))).not.toThrow();
  });
});

describe("add_c", () => {
  it("add_c(2, 3) ≈ 5", () => {
    expect(nearC(add_c(Complex.of(2), Complex.of(3)), 5, 0)).toBe(true);
  });

  it("add_c(1+2i, 3+1i) ≈ 4+3i", () => {
    const r = add_c(Complex.of(1, 2), Complex.of(3, 1));
    expect(nearC(r, 4, 3)).toBe(true);
  });

  it("add_c throws when first arg is zero", () => {
    expect(() => add_c(Complex.of(0), Complex.of(1))).toThrow(RangeError);
  });
});

describe("mul_c", () => {
  it("mul_c(2, 3) ≈ 6", () => {
    expect(nearC(mul_c(Complex.of(2), Complex.of(3)), 6, 0)).toBe(true);
  });

  it("mul_c(1+i, 1-i) ≈ 2", () => {
    const r = mul_c(Complex.of(1, 1), Complex.of(1, -1));
    expect(nearC(r, 2, 0)).toBe(true);
  });

  it("mul_c(z, z.recip()) ≈ 1", () => {
    const z = Complex.of(3, 2);
    const r = mul_c(z, z.recip());
    expect(nearC(r, 1, 0)).toBe(true);
  });
});

describe("recip_c", () => {
  it("recip_c(2) ≈ 0.5", () => {
    expect(nearC(recip_c(Complex.of(2)), 0.5, 0)).toBe(true);
  });

  it("recip_c(i) ≈ −i", () => {
    const r = recip_c(Complex.of(0, 1));
    expect(nearC(r, 0, -1)).toBe(true);
  });

  it("mul_c(z, recip_c(z)) ≈ 1", () => {
    const z = Complex.of(2, 3);
    const r = mul_c(z, recip_c(z));
    expect(nearC(r, 1, 0)).toBe(true);
  });
});

describe("div_c", () => {
  it("div_c(6, 2) ≈ 3", () => {
    expect(nearC(div_c(Complex.of(6), Complex.of(2)), 3, 0)).toBe(true);
  });

  it("div_c(z, z) ≈ 1", () => {
    const z = Complex.of(2, 3);
    expect(nearC(div_c(z, z), 1, 0)).toBe(true);
  });
});

describe("pow_c", () => {
  it("pow_c(2, 3) ≈ 8", () => {
    expect(nearC(pow_c(Complex.of(2), Complex.of(3)), 8, 0)).toBe(true);
  });

  it("pow_c(i, 2) ≈ −1  (i² = −1)", () => {
    const r = pow_c(Complex.of(0, 1), Complex.of(2));
    expect(nearC(r, -1, 0)).toBe(true);
  });
});

// ─── The escape from reals ────────────────────────────────────────────────────

describe("NEG_I_PI_C — escape from reals", () => {
  it("Re(NEG_I_PI_C) ≈ 0", () => {
    expect(near(NEG_I_PI_C.re, 0)).toBe(true);
  });

  it("|Im(NEG_I_PI_C)| ≈ π", () => {
    expect(near(Math.abs(NEG_I_PI_C.im), Math.PI)).toBe(true);
  });

  it("NEG_I_PI_C is not real", () => {
    expect(NEG_I_PI_C.isReal(TOL)).toBe(false);
  });
});

// ─── i, π ────────────────────────────────────────────────────────────────────

describe("I_CONST (i)", () => {
  it("Re(i) ≈ 0", () => expect(near(I_CONST.re, 0)).toBe(true));
  it("Im(i) ≈ 1", () => expect(near(I_CONST.im, 1)).toBe(true));

  it("i² ≈ −1", () => {
    const r = mul_c(I_CONST, I_CONST);
    expect(near(r.re, -1)).toBe(true);
    expect(near(r.im,  0)).toBe(true);
  });

  it("i⁴ ≈ 1", () => {
    const i2 = mul_c(I_CONST, I_CONST);
    const i4 = mul_c(i2, i2);
    expect(near(i4.re, 1)).toBe(true);
    expect(near(i4.im, 0)).toBe(true);
  });
});

describe("PI_C (π)", () => {
  it("Im(π) ≈ 0", () => expect(near(PI_C.im, 0)).toBe(true));
  it("Re(π) ≈ Math.PI", () => expect(near(PI_C.re, Math.PI)).toBe(true));
});

// ─── Euler's formula ──────────────────────────────────────────────────────────

describe("eul_c — Euler's formula", () => {
  it("eul_c(0) = 1", () => {
    expect(nearC(eul_c(Complex.of(0)), 1, 0)).toBe(true);
  });

  it("eul_c(π) ≈ −1  (Euler's identity)", () => {
    const r = eul_c(Complex.of(Math.PI));
    expect(near(r.re, -1)).toBe(true);
    expect(near(r.im,  0)).toBe(true);
  });

  it("eul_c(π/2) ≈ i", () => {
    const r = eul_c(Complex.of(Math.PI / 2));
    expect(near(r.re, 0)).toBe(true);
    expect(near(r.im, 1)).toBe(true);
  });

  it("eul_c(−π/2) ≈ −i", () => {
    const r = eul_c(Complex.of(-Math.PI / 2));
    expect(near(r.re,  0)).toBe(true);
    expect(near(r.im, -1)).toBe(true);
  });

  it("|eul_c(x)| = 1 for real x", () => {
    for (const x of [0, 1, 2, -1, Math.PI, -Math.PI / 3]) {
      expect(near(eul_c(Complex.of(x)).abs(), 1)).toBe(true);
    }
  });
});

// ─── sin_eml and cos_eml ──────────────────────────────────────────────────────

describe("sin_eml / cos_eml", () => {
  const cases = [
    [0, 0, 1],
    [Math.PI / 6, 0.5, Math.sqrt(3) / 2],
    [Math.PI / 4, Math.SQRT1_2, Math.SQRT1_2],
    [Math.PI / 3, Math.sqrt(3) / 2, 0.5],
    [Math.PI / 2, 1, 0],
    [Math.PI, 0, -1],
    [-1, -Math.sin(1), Math.cos(1)],
    [2, Math.sin(2), Math.cos(2)],
  ];

  for (const [x, sinX, cosX] of cases) {
    it(`sin_eml(${x.toFixed(4)}) ≈ ${sinX.toFixed(4)}`, () => {
      expect(near(sin_eml(x), sinX)).toBe(true);
    });

    it(`cos_eml(${x.toFixed(4)}) ≈ ${cosX.toFixed(4)}`, () => {
      expect(near(cos_eml(x), cosX)).toBe(true);
    });
  }

  it("sin² + cos² = 1 for x ∈ {0.3, 1, 2, π}", () => {
    for (const x of [0.3, 1, 2, Math.PI]) {
      const s = sin_eml(x);
      const c = cos_eml(x);
      expect(near(s * s + c * c, 1)).toBe(true);
    }
  });
});

// ─── IDENTITIES_C completeness ────────────────────────────────────────────────

describe("IDENTITIES_C", () => {
  it("has at least 15 entries", () => {
    expect(IDENTITIES_C.length).toBeGreaterThanOrEqual(15);
  });

  it("every entry has name, emlForm, domain, terminal, status", () => {
    for (const id of IDENTITIES_C) {
      expect(id).toHaveProperty("name");
      expect(id).toHaveProperty("emlForm");
      expect(id).toHaveProperty("domain");
      expect(id).toHaveProperty("terminal");
      expect(id).toHaveProperty("status");
    }
  });

  it("NEG_I_PI entry uses terminal {1}", () => {
    const entry = IDENTITIES_C.find((e) => e.name === "−iπ");
    expect(entry).toBeDefined();
    expect(entry.terminal).toBe("{1}");
  });

  it("i and π entries use terminal {1, 2}", () => {
    const iEntry  = IDENTITIES_C.find((e) => e.name === "i");
    const piEntry = IDENTITIES_C.find((e) => e.name === "π");
    expect(iEntry?.terminal).toBe("{1, 2}");
    expect(piEntry?.terminal).toBe("{1, 2}");
  });

  it("sin and cos are marked as meta-operations", () => {
    const sin = IDENTITIES_C.find((e) => e.name === "sin(x)");
    const cos = IDENTITIES_C.find((e) => e.name === "cos(x)");
    expect(sin?.status).toBe("meta-operation");
    expect(cos?.status).toBe("meta-operation");
  });
});

describe("BRANCH_CUT_NOTES", () => {
  it("is an array with at least 4 entries", () => {
    expect(Array.isArray(BRANCH_CUT_NOTES)).toBe(true);
    expect(BRANCH_CUT_NOTES.length).toBeGreaterThanOrEqual(4);
  });

  it("every entry has fn, failsWhen, symptom, action", () => {
    for (const note of BRANCH_CUT_NOTES) {
      expect(note).toHaveProperty("fn");
      expect(note).toHaveProperty("failsWhen");
      expect(note).toHaveProperty("symptom");
      expect(note).toHaveProperty("action");
    }
  });
});
