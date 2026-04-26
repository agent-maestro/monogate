/**
 * monogate/cost — Pfaffian cost analysis for symbolic expression trees.
 *
 * Port of the Python eml-cost package to JavaScript.
 * Works on expression trees represented as plain objects:
 *
 *   { type: 'exp', arg: subtree }
 *   { type: 'sin', arg: subtree }
 *   { type: 'add', args: [left, right] }
 *   { type: 'mul', args: [left, right] }
 *   { type: 'pow', base: subtree, exponent: subtree }
 *   { type: 'num', value: 3.14 }
 *   { type: 'sym', name: 'x' }
 *
 * Usage:
 *   import { analyze, parse } from 'monogate/cost';
 *
 *   const result = analyze(parse('exp(sin(x))'));
 *   console.log(result);
 *   // { pfaffian_r: 3, max_path_r: 3, eml_depth: 4,
 *   //   structural_overhead: 0, corrections: { c_osc: 1, c_composite: 0, delta_fused: 0 },
 *   //   predicted_depth: 4, is_pfaffian_not_eml: false,
 *   //   cost_class: 'p3-d4-w0-c1' }
 *
 * Reference: arXiv:2603.21852 (Odrzywołek 2026)
 * Pfaffian chain theory: Khovanskii fewnomials (1991)
 *
 * @module monogate/cost
 */

// ─── Expression tree types ───────────────────────────────────────────────────

const UNARY_TRANSCENDENTAL = new Set([
  'exp', 'log', 'ln',
  'sin', 'cos', 'tan',
  'sinh', 'cosh', 'tanh',
  'asin', 'acos', 'atan',
  'asinh', 'acosh', 'atanh',
]);

const SIN_LIKE = new Set(['sin', 'cos']);
const TANH_LIKE = new Set(['tanh', 'atan', 'asinh', 'acosh', 'atanh']);
const HYPER_PAIR = new Set(['sinh', 'cosh']);

// Pfaffian-not-EML primitives with their chain orders (Khovanskii convention)
const PFAFFIAN_NOT_EML_R = {
  // Bessel family
  besselj: 3, bessely: 5, besseli: 3, besselk: 3,
  hankel1: 3, hankel2: 3,
  // Airy family
  airyai: 3, airybi: 3, airyaiprime: 3, airybiprime: 3,
  // Hypergeometric / Lambert W
  hyper: 3, lambertw: 2,
  // erf family
  erf: 2, erfc: 2, erfi: 2, fresnels: 3, fresnelc: 3,
  // Gamma family
  gamma: 2, loggamma: 2, polygamma: 3, beta: 3,
  // Integral functions
  ei: 3, li: 3, si: 3, ci: 3,
};

// ─── Expression tree helpers ─────────────────────────────────────────────────

function isAtom(node) {
  return node.type === 'num' || node.type === 'sym';
}

function getChildren(node) {
  if (node.arg) return [node.arg];
  if (node.args) return node.args;
  if (node.base) return [node.base, node.exponent];
  return [];
}

function isIntegerExponent(node) {
  return node.type === 'pow' &&
    node.exponent.type === 'num' &&
    Number.isInteger(node.exponent.value);
}

function isConstant(node) {
  if (node.type === 'num') return true;
  if (node.type === 'sym') return false;
  return getChildren(node).every(isConstant);
}

// ─── Parser ──────────────────────────────────────────────────────────────────

/**
 * Parse a string expression into a tree.
 *
 * Supports: x, y, z (symbols), numbers, +, -, *, /, ^,
 * and function calls: exp(), ln(), log(), sin(), cos(), tan(),
 * sinh(), cosh(), tanh(), sqrt(), erf(), etc.
 *
 * @param {string} input
 * @returns {object} expression tree
 */
export function parse(input) {
  let pos = 0;
  const s = input.replace(/\s+/g, '');

  function peek() { return s[pos]; }
  function consume(ch) {
    if (s[pos] !== ch) throw new Error(`Expected '${ch}' at position ${pos}, got '${s[pos]}' in "${input}"`);
    pos++;
  }

  function parseExpr() { return parseAdd(); }

  function parseAdd() {
    const terms = [parseMul()];
    while (pos < s.length && (peek() === '+' || peek() === '-')) {
      const op = peek();
      pos++;
      const right = parseMul();
      if (op === '+') {
        terms.push(right);
      } else {
        terms.push({ type: 'neg', arg: right });
      }
    }
    if (terms.length === 1) return terms[0];
    return { type: 'add', args: terms };
  }

  function parseMul() {
    let left = parsePow();
    while (pos < s.length && (peek() === '*' || peek() === '/')) {
      // Distinguish '*' from '**' (power) — '**' must be handled at pow level
      if (peek() === '*' && s[pos + 1] === '*') break;
      const op = peek();
      pos++;
      const right = parsePow();
      if (op === '*') {
        // Flatten into n-ary mul
        if (left.type === 'mul') {
          left = { type: 'mul', args: [...left.args, right] };
        } else {
          left = { type: 'mul', args: [left, right] };
        }
      } else {
        // Parse a/b as mul(a, pow(b, -1)) — matches sympy's canonical
        // form so depth/structural metrics align with Python eml-cost.
        // Hand-built trees with type:'div' are still handled by every
        // metric below for backwards compat.
        const inverse = {
          type: 'pow',
          base: right,
          exponent: { type: 'num', value: -1 },
        };
        if (left.type === 'mul') {
          left = { type: 'mul', args: [...left.args, inverse] };
        } else {
          left = { type: 'mul', args: [left, inverse] };
        }
      }
    }
    return left;
  }

  function parsePow() {
    let base = parseUnary();
    if (pos < s.length && (peek() === '^' || s.slice(pos, pos + 2) === '**')) {
      if (peek() === '*') pos += 2; else pos++;
      const exp = parseUnary();
      return { type: 'pow', base, exponent: exp };
    }
    return base;
  }

  function parseUnary() {
    if (peek() === '-') {
      pos++;
      const inner = parseUnary();
      return { type: 'neg', arg: inner };
    }
    return parseAtom();
  }

  function parseAtom() {
    // Number
    if (/[0-9.]/.test(peek())) {
      let numStr = '';
      while (pos < s.length && /[0-9.eE+-]/.test(s[pos])) {
        // Handle negative exponent in scientific notation
        if ((s[pos] === '+' || s[pos] === '-') && numStr.length > 0 && !/[eE]/.test(numStr[numStr.length - 1])) break;
        numStr += s[pos++];
      }
      return { type: 'num', value: parseFloat(numStr) };
    }

    // Parenthesized expression
    if (peek() === '(') {
      consume('(');
      const inner = parseExpr();
      consume(')');
      return inner;
    }

    // Identifier (symbol or function)
    let name = '';
    while (pos < s.length && /[a-zA-Z_0-9]/.test(s[pos])) {
      name += s[pos++];
    }

    if (!name) throw new Error(`Unexpected character '${peek()}' at position ${pos} in "${input}"`);

    // Known constants
    if (name === 'pi' || name === 'PI') return { type: 'num', value: Math.PI };
    if (name === 'e' && peek() !== '(') return { type: 'num', value: Math.E };

    // Function call
    if (peek() === '(') {
      consume('(');
      const args = [];
      if (peek() !== ')') {
        args.push(parseExpr());
        while (peek() === ',') {
          pos++;
          args.push(parseExpr());
        }
      }
      consume(')');

      const fn = name.toLowerCase();

      // Normalize aliases
      if (fn === 'log' || fn === 'ln') return { type: 'log', arg: args[0] };
      if (fn === 'sqrt') return { type: 'pow', base: args[0], exponent: { type: 'num', value: 0.5 } };
      if (fn === 'abs') return { type: 'abs', arg: args[0] };

      if (UNARY_TRANSCENDENTAL.has(fn)) {
        return { type: fn, arg: args[0] };
      }

      if (fn === 'pow') {
        return { type: 'pow', base: args[0], exponent: args[1] };
      }

      // Pfaffian-not-EML functions
      if (PFAFFIAN_NOT_EML_R[fn] !== undefined) {
        return { type: fn, args };
      }

      throw new Error(`Unknown function '${name}' in "${input}"`);
    }

    // Plain symbol
    return { type: 'sym', name };
  }

  const result = parseExpr();
  if (pos !== s.length) throw new Error(`Unexpected trailing characters at position ${pos} in "${input}"`);
  return result;
}

// ─── Pfaffian chain order (total, deduplicated) ──────────────────────────────

function _chainKey(node) {
  if (node.type === 'num') return `num:${node.value}`;
  if (node.type === 'sym') return `sym:${node.name}`;
  const children = getChildren(node).map(_chainKey).join(',');
  return `${node.type}(${children})`;
}

function _collectChains(node, chains) {
  if (isAtom(node)) return;

  for (const child of getChildren(node)) {
    _collectChains(child, chains);
  }

  const t = node.type;

  if (t === 'exp' || t === 'log') {
    chains.add(_chainKey(node));
    return;
  }

  if (SIN_LIKE.has(t)) {
    const argKey = _chainKey(node.arg);
    chains.add(`sin(${argKey})`);
    chains.add(`cos(${argKey})`);
    return;
  }

  if (t === 'tan') {
    chains.add(_chainKey(node));
    return;
  }

  if (TANH_LIKE.has(t)) {
    chains.add(_chainKey(node));
    return;
  }

  if (HYPER_PAIR.has(t)) {
    const argKey = _chainKey(node.arg);
    chains.add(`exp(${argKey})`);
    chains.add(`exp(neg(${argKey}))`);
    return;
  }

  if (t === 'pow') {
    if (isIntegerExponent(node)) return;
    chains.add(_chainKey(node));
    return;
  }

  // PNE functions
  const pneR = PFAFFIAN_NOT_EML_R[t];
  if (pneR !== undefined) {
    const h = _chainKey(node);
    for (let i = 0; i < pneR; i++) {
      chains.add(`__pne_${t}_${i}_${h}`);
    }
  }
}

/**
 * Total Pfaffian chain order (Khovanskii convention).
 *
 * Counts distinct chain generators across the whole expression tree.
 *
 * @param {object} node - expression tree
 * @returns {number}
 */
export function pfaffian_r(node) {
  const chains = new Set();
  _collectChains(node, chains);
  return chains.size;
}

// ─── Max-path Pfaffian chain order ───────────────────────────────────────────

/**
 * Pfaffian chain order along the deepest root-to-leaf path.
 *
 * Add/Mul nodes take max over children (parallel composition).
 *
 * @param {object} node - expression tree
 * @returns {number}
 */
export function max_path_r(node) {
  if (isAtom(node)) return 0;

  const t = node.type;

  if (t === 'exp' || t === 'log') return 1 + max_path_r(node.arg);
  if (SIN_LIKE.has(t)) return 2 + max_path_r(node.arg);
  if (t === 'tan') return 1 + max_path_r(node.arg);
  if (TANH_LIKE.has(t)) return 1 + max_path_r(node.arg);
  if (HYPER_PAIR.has(t)) return 2 + max_path_r(node.arg);

  if (t === 'pow') {
    if (isIntegerExponent(node)) return max_path_r(node.base);
    return 1 + Math.max(max_path_r(node.base), max_path_r(node.exponent));
  }

  if (t === 'add' || t === 'mul' || t === 'div') {
    return Math.max(...(node.args || []).map(max_path_r), 0);
  }

  if (t === 'neg' || t === 'abs') return max_path_r(node.arg);

  // PNE
  const pneR = PFAFFIAN_NOT_EML_R[t];
  if (pneR !== undefined) {
    const childMax = Math.max(...getChildren(node).map(max_path_r), 0);
    return pneR + childMax;
  }

  return Math.max(...getChildren(node).map(max_path_r), 0);
}

// ─── EML depth (SuperBEST routing tree depth) ────────────────────────────────

function _isLeadPattern(node) {
  // log(c + exp(g)) → fusion, returns g
  if (node.type === 'log' && node.arg.type === 'add' && node.arg.args.length === 2) {
    const [a, b] = node.arg.args;
    if (isConstant(a) && b.type === 'exp') return b.arg;
    if (isConstant(b) && a.type === 'exp') return a.arg;
  }
  return null;
}

function _isSigmoidPattern(node) {
  // 1/(1 + exp(-g)) or pow(add(1, exp(g)), -1) → fusion, returns g.
  //
  // Mirrors Python's _is_sigmoid_pattern: extracts the minus sign from
  // the exponent so that sigmoid(-x) and sigmoid(x) both reduce to the
  // same inner_g (up to sign), giving identical depth.
  const extract = (g) => (g.type === 'neg' ? g.arg : g);

  if (node.type === 'pow' && node.exponent?.type === 'num' && node.exponent.value === -1) {
    const inner = node.base;
    if (inner.type === 'add' && inner.args.length === 2) {
      for (const arg of inner.args) {
        if (arg.type === 'exp') return extract(arg.arg);
      }
    }
  }
  // Backwards-compat for hand-built div trees: 1 / (1 + exp(g)).
  if (node.type === 'div' && node.args.length === 2) {
    const denom = node.args[1];
    if (denom.type === 'add' && denom.args.length === 2) {
      for (const arg of denom.args) {
        if (arg.type === 'exp') return extract(arg.arg);
      }
    }
  }
  return null;
}

function _emlDepth(node) {
  if (isAtom(node)) return 0;

  // F-family fusion patterns
  const leadG = _isLeadPattern(node);
  if (leadG !== null) return 1 + _emlDepth(leadG);

  const sigG = _isSigmoidPattern(node);
  if (sigG !== null) return 1 + _emlDepth(sigG);

  const t = node.type;

  if (t === 'exp' || t === 'log') return 1 + _emlDepth(node.arg);
  if (SIN_LIKE.has(t)) return 3 + _emlDepth(node.arg);
  if (t === 'tan') return 4 + _emlDepth(node.arg);
  if (TANH_LIKE.has(t)) return 1 + _emlDepth(node.arg);
  if (HYPER_PAIR.has(t)) return 1 + _emlDepth(node.arg);
  // neg(x) mirrors SymPy's Mul(-1, x) which adds one Mul level.
  // abs(x) mirrors SymPy's Abs class which falls through the generic
  // 1+max(children) rule.
  if (t === 'neg' || t === 'abs') return 1 + _emlDepth(node.arg);

  if (t === 'pow') {
    if (isIntegerExponent(node)) return 1 + _emlDepth(node.base);
    return 1 + Math.max(_emlDepth(node.base), _emlDepth(node.exponent));
  }

  if (t === 'add' || t === 'mul' || t === 'div') {
    return 1 + Math.max(...(node.args || []).map(_emlDepth), 0);
  }

  // PNE or unknown — mirror Python's generic fallthrough: 1 + max(children)
  // when there are children, 0 otherwise (matches sympy ``default=-1``
  // semantics: 1 + (-1) = 0 for childless leaves).
  const children = getChildren(node);
  if (children.length === 0) return 0;
  return 1 + Math.max(...children.map(_emlDepth));
}

/**
 * EML routing tree depth (SuperBEST model).
 *
 * @param {object} node - expression tree
 * @returns {number}
 */
export function eml_depth(node) {
  return _emlDepth(node);
}

// ─── Structural overhead ─────────────────────────────────────────────────────

/**
 * Count Add/Mul/positive-integer-Pow nodes along the deepest path.
 * These contribute to EML tree depth but have no Pfaffian chain analog.
 *
 * @param {object} node - expression tree
 * @returns {number}
 */
export function structural_overhead(node) {
  if (isAtom(node)) return 0;

  const t = node.type;
  const childMax = Math.max(...getChildren(node).map(structural_overhead), 0);

  if (t === 'add' || t === 'mul' || t === 'div') return 1 + childMax;
  if (t === 'pow' && isIntegerExponent(node) && node.exponent.value >= 0) {
    return 1 + structural_overhead(node.base);
  }
  // neg(x) mirrors SymPy's Mul(-1, x) — counts as a Mul for structural
  // overhead. abs(x) is a SymPy function (no Add/Mul level) and falls
  // through.
  if (t === 'neg') return 1 + structural_overhead(node.arg);

  return childMax;
}

// ─── Pfaffian-not-EML detection ──────────────────────────────────────────────

/**
 * Returns true if the expression contains any Pfaffian-but-not-EML primitive
 * (Bessel, Airy, Lambert W, erf, Gamma, etc.)
 *
 * @param {object} node - expression tree
 * @returns {boolean}
 */
export function is_pfaffian_not_eml(node) {
  if (isAtom(node)) return false;
  if (PFAFFIAN_NOT_EML_R[node.type] !== undefined) return true;
  return getChildren(node).some(is_pfaffian_not_eml);
}

// ─── Corrections along max path ──────────────────────────────────────────────

function _corrections(node) {
  if (isAtom(node)) return [0, 0, 0];

  // F-family fusion: log(c + exp(g))
  if (node.type === 'log' && node.arg?.type === 'add' && node.arg.args?.length === 2) {
    const [a, b] = node.arg.args;
    if (isConstant(a) && b.type === 'exp') {
      const sub = _corrections(b.arg);
      return [sub[0], sub[1], sub[2] + 1];
    }
    if (isConstant(b) && a.type === 'exp') {
      const sub = _corrections(a.arg);
      return [sub[0], sub[1], sub[2] + 1];
    }
  }

  // Sigmoid pattern: pow(add(..., exp(g)), -1)
  // Same minus-sign extraction as _isSigmoidPattern so sigmoid(-x) and
  // sigmoid(x) yield the same fused-correction count.
  if (node.type === 'pow' && node.exponent?.type === 'num' && node.exponent.value === -1) {
    const inner = node.base;
    if (inner?.type === 'add' && inner.args?.length === 2) {
      for (const arg of inner.args) {
        if (arg.type === 'exp') {
          const g = arg.arg.type === 'neg' ? arg.arg.arg : arg.arg;
          const sub = _corrections(g);
          return [sub[0], sub[1], sub[2] + 1];
        }
      }
    }
  }

  const t = node.type;

  if (SIN_LIKE.has(t)) {
    const sub = _corrections(node.arg);
    return [sub[0] + 1, sub[1], sub[2]];
  }

  if (t === 'tan') {
    const sub = _corrections(node.arg);
    return [sub[0], sub[1] + 1, sub[2]];
  }

  // For branching nodes, pick the child with highest net correction
  const children = getChildren(node);
  if (children.length === 0) return [0, 0, 0];

  let best = [0, 0, 0];
  let bestTotal = -1;
  for (const child of children) {
    const sub = _corrections(child);
    const total = sub[0] + sub[1] - sub[2];
    if (total > bestTotal) {
      best = sub;
      bestTotal = total;
    }
  }
  return best;
}

// ─── Main analyze function ───────────────────────────────────────────────────

/**
 * @typedef {Object} AnalyzeResult
 * @property {number} pfaffian_r - Total Pfaffian chain order
 * @property {number} max_path_r - Max-path chain order
 * @property {number} eml_depth - EML routing tree depth
 * @property {number} structural_overhead - Add/Mul/Pow overhead nodes
 * @property {{ c_osc: number, c_composite: number, delta_fused: number }} corrections
 * @property {number} predicted_depth - max_path_r + corrections + overhead
 * @property {boolean} is_pfaffian_not_eml - Contains non-EML primitives
 * @property {string} cost_class - "p{r}-d{depth}-w{overhead}-c{osc}" string
 */

/**
 * Analyze an expression and return its full Pfaffian profile.
 *
 * Accepts either an expression tree object or a string (which will be parsed).
 *
 * @param {object|string} expr - expression tree or parseable string
 * @returns {AnalyzeResult}
 *
 * @example
 * import { analyze } from 'monogate/cost';
 *
 * analyze('exp(x)');
 * // { pfaffian_r: 1, max_path_r: 1, eml_depth: 1,
 * //   cost_class: 'p1-d1-w0-c0', ... }
 *
 * analyze('sin(exp(x))');
 * // { pfaffian_r: 3, max_path_r: 3, eml_depth: 4,
 * //   cost_class: 'p3-d4-w0-c1', ... }
 */
export function analyze(expr) {
  const node = typeof expr === 'string' ? parse(expr) : expr;

  const r = pfaffian_r(node);
  const mr = max_path_r(node);
  const d = eml_depth(node);
  const so = structural_overhead(node);
  const [c_osc, c_composite, delta_fused] = _corrections(node);
  const predicted = mr + c_osc + c_composite - delta_fused + so;
  const pne = is_pfaffian_not_eml(node);

  // Cost-class fingerprint matches the Python eml-cost convention:
  // p<pfaffian_r>-d<eml_depth>-w<max_path_r>-c<correction_sum>
  // where correction_sum = c_osc + c_composite - delta_fused.
  const correction_sum = c_osc + c_composite - delta_fused;

  return {
    pfaffian_r: r,
    max_path_r: mr,
    eml_depth: d,
    structural_overhead: so,
    corrections: { c_osc, c_composite, delta_fused },
    predicted_depth: predicted,
    is_pfaffian_not_eml: pne,
    cost_class: `p${r}-d${d}-w${mr}-c${correction_sum}`,
  };
}

/**
 * Analyze a batch of expressions.
 *
 * @param {Array<object|string>} expressions
 * @returns {Array<AnalyzeResult>}
 */
export function analyze_batch(expressions) {
  return expressions.map(analyze);
}

/**
 * Compute distance between two profiles.
 * Weighted L2 metric satisfying identity, symmetry, and triangle inequality.
 *
 * Default weights: r=4 (chain order dominates), d=1, w=2, c=1.
 *
 * @param {AnalyzeResult} a
 * @param {AnalyzeResult} b
 * @param {{ w_r?: number, w_d?: number, w_w?: number, w_c?: number }} [weights]
 * @returns {number}
 */
export function distance(a, b, weights = {}) {
  const { w_r = 4, w_d = 1, w_w = 2, w_c = 1 } = weights;
  const dr = a.max_path_r - b.max_path_r;
  const dd = a.predicted_depth - b.predicted_depth;
  const dw = a.structural_overhead - b.structural_overhead;
  const dc = a.corrections.c_osc - b.corrections.c_osc;
  return Math.sqrt(w_r * dr * dr + w_d * dd * dd + w_w * dw * dw + w_c * dc * dc);
}

/**
 * Compare two profiles dimension by dimension.
 *
 * @param {AnalyzeResult} a
 * @param {AnalyzeResult} b
 * @returns {{ delta_r: number, delta_d: number, delta_w: number, delta_c: number, distance: number }}
 */
export function compare(a, b) {
  return {
    delta_r: a.max_path_r - b.max_path_r,
    delta_d: a.predicted_depth - b.predicted_depth,
    delta_w: a.structural_overhead - b.structural_overhead,
    delta_c: a.corrections.c_osc - b.corrections.c_osc,
    distance: distance(a, b),
  };
}

// ─── Float64-precision-loss predictor (port of eml-cost 0.7.0) ───────────────

/**
 * Float64 machine epsilon. The smallest meaningful detectable
 * mpmath_max_relerr in float64. Mirrors `eml_cost.FLOAT64_EPS`.
 */
export const FLOAT64_EPS = 2.220446049250313e-16;

/**
 * Coefficients shipped with eml-cost 0.7.0 (E-193 OLS fit on n=379
 * bench-300-domain expressions). Response: log10(mpmath_max_relerr)
 * floored at FLOAT64_EPS. 5-fold CV (seed=42): R^2 = +0.271 +/- 0.060,
 * residual log10 std = 0.772.
 *
 * Identical numerics to `eml_cost.predict_precision_loss._COEFS`.
 */
const _PRECISION_LOSS_COEFS = {
  intercept: -15.440556729015627,
  eml_depth: 0.33668813151183796,
  max_path_r: -0.1249378060199701,
  log_count_ops: 0.9442895772504774,
  log_tree_size: -1.3751259909585363,
  residual_log10_std: 0.7720847093601771,
  cv_r2_mean: 0.2711510788080426,
};

/**
 * Count operations in a tree, mirroring `sympy.count_ops`.
 *
 * Conventions:
 *   - Atoms (num, sym): 0 ops.
 *   - n-ary `add` / `mul`: contribute (k - 1) ops + recurse on children.
 *     This matches SymPy's binary-op accounting for n-ary nodes.
 *   - Unary functions, `pow`, `neg`: 1 op + recurse on children.
 *
 * The JS parser turns `a / b` into `mul(a, pow(b, -1))`, matching
 * SymPy's canonical form, so feature parity holds for division too.
 *
 * @param {object} node
 * @returns {number}
 */
export function count_ops(node) {
  if (isAtom(node)) return 0;
  const kids = getChildren(node);
  const childOps = kids.reduce((acc, c) => acc + count_ops(c), 0);
  if (node.type === 'add' || node.type === 'mul') {
    return (kids.length - 1) + childOps;
  }
  return 1 + childOps;
}

/**
 * Pre-order tree-size (count of every node, including atoms).
 *
 * Mirrors `sum(1 for _ in sympy.preorder_traversal(expr))`.
 *
 * @param {object} node
 * @returns {number}
 */
export function tree_size(node) {
  return 1 + getChildren(node).reduce((acc, c) => acc + tree_size(c), 0);
}

/**
 * @typedef {Object} PrecisionLossEstimate
 * @property {number} predicted_max_relerr - point prediction; floor at FLOAT64_EPS.
 * @property {number} predicted_digits_lost - decimal digits of float64 precision lost
 *   relative to a perfect 16-digit result (0 if the prediction is below eps).
 * @property {[number, number]} ci95 - 95% prediction interval [low, high] in relerr units.
 * @property {number} log10_relerr - raw log10(relerr) point prediction.
 * @property {number} log10_std - residual log10 standard deviation (~0.77).
 * @property {{ eml_depth: number, max_path_r: number, log_count_ops: number, log_tree_size: number }} features
 * @property {number} cv_r2 - held-out 5-fold CV R^2 of the model (~0.27).
 */

function _digits_lost(log10_relerr) {
  const log10_eps = Math.log10(FLOAT64_EPS);
  return Math.max(0, log10_relerr - log10_eps);
}

/**
 * Predict float64 vs mpmath relative error magnitude for an expression.
 *
 * Port of `eml_cost.predict_precision_loss` (0.7.0). Uses byte-identical
 * coefficients to the Python package; `count_ops` and `tree_size` are
 * implemented to mirror SymPy semantics so feature values match for
 * parsed expressions.
 *
 * @param {object|string} expr - expression tree or parseable string
 * @returns {PrecisionLossEstimate}
 *
 * @example
 * import { predict_precision_loss } from 'monogate/cost';
 *
 * const r = predict_precision_loss('exp(exp(x)) + sin(x**2)');
 * // r.predicted_max_relerr ~ 2.6e-15
 * // r.predicted_digits_lost ~ 1.07
 * // r.ci95 ~ [8e-17, 8e-14]
 *
 * Honest framing (mirrors the Python docstring):
 *   - Modest predictor (CV R^2 ~ 0.27, residual log10 std ~ 0.77).
 *     Use for rank-ordering and high-risk subtree surfacing, NOT
 *     for absolute precision claims.
 *   - NOT a form recommender — E-193 Phase 3 best-pick was 30% on
 *     algebraically-equivalent rewrite tests, well below the 70%
 *     product threshold; that recommender was deliberately not shipped.
 */
export function predict_precision_loss(expr) {
  const node = typeof expr === 'string' ? parse(expr) : expr;

  const features = {
    eml_depth: eml_depth(node),
    max_path_r: max_path_r(node),
    log_count_ops: Math.log10(count_ops(node) + 1),
    log_tree_size: Math.log10(tree_size(node) + 1),
  };

  const C = _PRECISION_LOSS_COEFS;
  const log10_relerr =
    C.intercept +
    C.eml_depth * features.eml_depth +
    C.max_path_r * features.max_path_r +
    C.log_count_ops * features.log_count_ops +
    C.log_tree_size * features.log_tree_size;

  const sigma = C.residual_log10_std;
  const predicted = Math.pow(10, log10_relerr);
  const low = Math.pow(10, log10_relerr - 1.96 * sigma);
  const high = Math.pow(10, log10_relerr + 1.96 * sigma);

  return {
    predicted_max_relerr: predicted,
    predicted_digits_lost: _digits_lost(log10_relerr),
    ci95: [low, high],
    log10_relerr,
    log10_std: sigma,
    features,
    cv_r2: C.cv_r2_mean,
  };
}

/**
 * Provenance for the shipped precision-loss model. Mirrors
 * `eml_cost.precision_loss_model_metadata()`.
 *
 * @returns {object}
 */
export function precision_loss_model_metadata() {
  return {
    n: 379,
    response: 'log10_mpmath_max_relerr',
    source: 'E193_numerical_stability/corpus_with_stability.csv',
    features: ['eml_depth', 'max_path_r', 'log_count_ops', 'log_tree_size'],
    session: 'E-193',
    cv_r2_mean: _PRECISION_LOSS_COEFS.cv_r2_mean,
    residual_log10_std: _PRECISION_LOSS_COEFS.residual_log10_std,
    relerr_floor: FLOAT64_EPS,
    headline_partial_r: 0.357,
    headline_partial_q: 1.6e-11,
    honest_note:
      'Modest predictor (CV R^2 ~ 0.27, residual log10 std ~ 0.77). ' +
      'Use for rank-ordering and high-risk subtree surfacing, NOT ' +
      'for absolute precision claims. NOT a form recommender — ' +
      'see E-193 Phase 3 (30% best-pick on form-sensitive rewrite ' +
      'tests). The form-rewrite recommender was deliberately not ' +
      'shipped.',
  };
}

// ─── Default export ──────────────────────────────────────────────────────────

export default {
  parse,
  analyze,
  analyze_batch,
  distance,
  compare,
  pfaffian_r,
  max_path_r,
  eml_depth,
  structural_overhead,
  is_pfaffian_not_eml,
  count_ops,
  tree_size,
  predict_precision_loss,
  precision_loss_model_metadata,
  FLOAT64_EPS,
  PFAFFIAN_NOT_EML_R,
};

export { PFAFFIAN_NOT_EML_R };
