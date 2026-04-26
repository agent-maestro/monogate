/**
 * Tests for `predict_precision_loss(expr)` in the JS port (monogate 1.3.0).
 *
 * Parity philosophy
 * -----------------
 * The JS port mirrors `eml_cost.predict_precision_loss` from Python
 * eml-cost 0.7.0 byte-for-byte where the parsed expression tree
 * matches between SymPy and the JS parser.
 *
 *   - STRICT_PARITY (14 cases): tree shape matches SymPy's canonical
 *     form -> predicted_max_relerr is byte-identical (rel diff < 1e-10).
 *   - DRIFT_CASES (6 cases): SymPy's automatic canonicalization
 *     (e.g. Mul(1, Pow(x,-1)) -> Pow(x,-1); Mul(-1, x) <-> Neg(x);
 *     sqrt -> Pow(x, S.Half)) shifts count_ops or tree_size by 1-2,
 *     causing the predicted relerr to drift by up to ~10x. Predictions
 *     remain within each other's 95% CI; we assert a 1-decade bound.
 *
 * Both behaviors are documented in cost.js and in the npm 1.3.0
 * CHANGELOG. For exact-parity workflows, run the JS prediction on
 * a SymPy-canonicalized expression string; the simple-form coverage
 * holds as long as the tree shape matches.
 */
import { describe, it, expect } from 'vitest';
import {
  parse,
  count_ops,
  tree_size,
  predict_precision_loss,
  precision_loss_model_metadata,
  FLOAT64_EPS,
} from './cost.js';

// ─── Python ground truth (eml-cost 0.7.0) ────────────────────────────────────
// Generated from
//   python -c "from eml_cost import predict_precision_loss as p; ..."
// against eml-cost 0.7.0 on 2026-04-26. Each entry holds the SymPy
// count_ops + tree_size + predicted_max_relerr for the EXPR.
const PY_GROUND_TRUTH = {
  // STRICT_PARITY — JS parser produces SymPy-equivalent tree.
  'x': { count_ops: 0, tree_size: 1, predicted_max_relerr: 1.3979418287320268e-16 },
  'x + 1': { count_ops: 1, tree_size: 3, predicted_max_relerr: 2.2515549350191864e-16 },
  'x**2': { count_ops: 1, tree_size: 3, predicted_max_relerr: 2.2515549350191864e-16 },
  'sin(x)': { count_ops: 1, tree_size: 2, predicted_max_relerr: 8.867265305952561e-16 },
  'exp(x)': { count_ops: 1, tree_size: 2, predicted_max_relerr: 2.508136946200148e-16 },
  'log(x)': { count_ops: 1, tree_size: 2, predicted_max_relerr: 2.508136946200148e-16 },
  'sin(x) + cos(x)': { count_ops: 3, tree_size: 5, predicted_max_relerr: 1.4281806688516342e-15 },
  'exp(x) * sin(x)': { count_ops: 3, tree_size: 5, predicted_max_relerr: 1.4281806688516342e-15 },
  'exp(exp(x))': { count_ops: 2, tree_size: 3, predicted_max_relerr: 4.0325170070603e-16 },
  'sin(sin(sin(x)))': { count_ops: 3, tree_size: 4, predicted_max_relerr: 2.8012816299735817e-14 },
  'sin(sin(sin(sin(x))))': { count_ops: 4, tree_size: 5, predicted_max_relerr: 1.5494318590140535e-13 },
  'exp(exp(x)) + sin(x**2)': { count_ops: 5, tree_size: 8, predicted_max_relerr: 2.6037828092045807e-15 },
  '(x+1)*(x+2)*(x+3)': { count_ops: 5, tree_size: 10, predicted_max_relerr: 3.4322072243869693e-16 },
  'sin(x)*cos(x)*exp(x)': { count_ops: 5, tree_size: 7, predicted_max_relerr: 1.4101255673488155e-15 },
};

// DRIFT_CASES — JS parser literal tree differs from SymPy canonical
// form. JS prediction stays within ~1 decade of Python.
const PY_DRIFT_GROUND_TRUTH = {
  '1/(1 + exp(-x))': { predicted_max_relerr: 1.3147826013e-16 },
  'tanh(x/2)/2 + 1/2': { predicted_max_relerr: 1.5993155017e-15 },
  'sqrt(x**2 + 1)': { predicted_max_relerr: 7.290336e-16 },
  'log(x + sqrt(x**2 + 1))': { predicted_max_relerr: 2.2854e-15 },
  'exp(-x**2 / 2)': { predicted_max_relerr: 8.7600e-16 },
  'cos(x) - sin(x)/x': { predicted_max_relerr: 1.66311e-15 },
};

// ─── Coefficient parity ──────────────────────────────────────────────────────

describe('coefficient parity with eml-cost 0.7.0', () => {
  it('ships byte-identical Python coefficients', () => {
    const meta = precision_loss_model_metadata();
    expect(meta.n).toBe(379);
    expect(meta.session).toBe('E-193');
    expect(meta.cv_r2_mean).toBeCloseTo(0.27115107880804, 12);
    expect(meta.residual_log10_std).toBeCloseTo(0.7720847093601771, 12);
    expect(meta.relerr_floor).toBeCloseTo(FLOAT64_EPS, 16);
    expect(meta.headline_partial_r).toBeCloseTo(0.357, 6);
    expect(meta.headline_partial_q).toBeCloseTo(1.6e-11, 14);
  });

  it('FLOAT64_EPS matches numpy.finfo(float64).eps', () => {
    expect(FLOAT64_EPS).toBe(2.220446049250313e-16);
  });

  it('honest_note flags the modest CV R^2 and rejects form-recommender use', () => {
    const meta = precision_loss_model_metadata();
    expect(meta.honest_note).toMatch(/Modest predictor/);
    expect(meta.honest_note).toMatch(/NOT a form recommender/);
  });
});

// ─── Strict byte-identical parity (14 cases) ────────────────────────────────

describe('strict parity with Python eml-cost 0.7.0 (14/20 cases)', () => {
  for (const [expr, py] of Object.entries(PY_GROUND_TRUTH)) {
    it(`${expr} matches Python byte-for-byte`, () => {
      const node = parse(expr);
      expect(count_ops(node)).toBe(py.count_ops);
      expect(tree_size(node)).toBe(py.tree_size);
      const r = predict_precision_loss(node);
      const relDiff = Math.abs(r.predicted_max_relerr - py.predicted_max_relerr) /
        py.predicted_max_relerr;
      expect(relDiff).toBeLessThan(1e-10);
    });
  }
});

// ─── Drift-tolerance cases (6 cases) ────────────────────────────────────────

describe('drift-tolerance cases (SymPy canonicalization differences)', () => {
  for (const [expr, py] of Object.entries(PY_DRIFT_GROUND_TRUTH)) {
    it(`${expr} stays within 1 decade of Python`, () => {
      const node = parse(expr);
      const r = predict_precision_loss(node);
      const ratio = r.predicted_max_relerr / py.predicted_max_relerr;
      expect(ratio).toBeGreaterThan(0.1);
      expect(ratio).toBeLessThan(10);
    });
  }
});

// ─── Surface contract ───────────────────────────────────────────────────────

describe('predict_precision_loss surface contract', () => {
  it('accepts a string and parses it', () => {
    const r = predict_precision_loss('exp(x)');
    expect(r.predicted_max_relerr).toBeGreaterThan(0);
  });

  it('accepts a pre-parsed tree', () => {
    const tree = parse('exp(x)');
    const r = predict_precision_loss(tree);
    expect(r.predicted_max_relerr).toBeGreaterThan(0);
  });

  it('returns the documented dataclass shape', () => {
    const r = predict_precision_loss('sin(x)');
    expect(r).toHaveProperty('predicted_max_relerr');
    expect(r).toHaveProperty('predicted_digits_lost');
    expect(r).toHaveProperty('ci95');
    expect(r).toHaveProperty('log10_relerr');
    expect(r).toHaveProperty('log10_std');
    expect(r).toHaveProperty('features');
    expect(r).toHaveProperty('cv_r2');
    expect(Array.isArray(r.ci95)).toBe(true);
    expect(r.ci95).toHaveLength(2);
  });

  it('features include the four expected keys', () => {
    const r = predict_precision_loss('sin(x) + cos(x)');
    expect(Object.keys(r.features).sort()).toEqual(
      ['eml_depth', 'log_count_ops', 'log_tree_size', 'max_path_r']
    );
  });

  it('CI95 brackets the point prediction', () => {
    const r = predict_precision_loss('exp(exp(x)) + sin(x**2)');
    const [low, high] = r.ci95;
    expect(low).toBeLessThanOrEqual(r.predicted_max_relerr);
    expect(r.predicted_max_relerr).toBeLessThanOrEqual(high);
  });

  it('CI95 spans roughly factor 30 either way (sigma ~ 0.77)', () => {
    const r = predict_precision_loss('exp(exp(x)) + sin(x**2)');
    const [low, high] = r.ci95;
    expect(high / low).toBeGreaterThan(100);
  });

  it('log10_relerr is consistent with predicted_max_relerr', () => {
    const r = predict_precision_loss('sin(x)*cos(x)*exp(x)');
    expect(Math.pow(10, r.log10_relerr)).toBeCloseTo(r.predicted_max_relerr, 12);
  });

  it('predicted_digits_lost is non-negative', () => {
    const r = predict_precision_loss('x');
    expect(r.predicted_digits_lost).toBeGreaterThanOrEqual(0);
  });
});

// ─── Monotonicity sanity ─────────────────────────────────────────────────────

describe('monotonicity intent of the model', () => {
  it('deeper sin-composition predicts more relerr', () => {
    const shallow = predict_precision_loss('sin(x) + sin(x) + sin(x) + sin(x)');
    const deep = predict_precision_loss('sin(sin(sin(sin(x))))');
    expect(deep.predicted_max_relerr).toBeGreaterThan(shallow.predicted_max_relerr);
  });

  it('nested-sin ladder rank-orders monotonically (>= 70% concordance)', () => {
    const cases = [
      'x',
      'sin(x)',
      'sin(sin(x))',
      'sin(sin(sin(x)))',
      'sin(sin(sin(sin(x))))',
      'sin(sin(sin(sin(sin(x)))))',
    ];
    const preds = cases.map((s) => predict_precision_loss(s).predicted_max_relerr);
    let concordant = 0, total = 0;
    for (let i = 0; i < preds.length; i++) {
      for (let j = i + 1; j < preds.length; j++) {
        total++;
        if (preds[j] > preds[i]) concordant++;
      }
    }
    expect(concordant / total).toBeGreaterThanOrEqual(0.7);
  });
});

// ─── count_ops + tree_size primitives ───────────────────────────────────────

describe('count_ops + tree_size SymPy parity', () => {
  it('count_ops returns 0 for atoms', () => {
    expect(count_ops(parse('x'))).toBe(0);
    expect(count_ops(parse('42'))).toBe(0);
  });

  it('tree_size returns 1 for atoms', () => {
    expect(tree_size(parse('x'))).toBe(1);
    expect(tree_size(parse('42'))).toBe(1);
  });

  it('count_ops counts n-ary add as (k-1) ops', () => {
    expect(count_ops(parse('x + y + z'))).toBe(2);
    expect(count_ops(parse('a + b + c + d'))).toBe(3);
  });

  it('count_ops counts n-ary mul as (k-1) ops', () => {
    expect(count_ops(parse('x * y * z'))).toBe(2);
  });
});
