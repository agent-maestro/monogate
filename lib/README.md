# monogate

> A single binary operator that generates all elementary functions.

```
eml(x, y) = exp(x) − ln(y)
```

From this one operator and the constant `1`, every elementary arithmetic function can be constructed as a pure expression tree. Implementation of:

> **"All elementary functions from a single operator"**
> Andrzej Odrzywołek, Jagiellonian University
> [arXiv:2603.21852v2](https://arxiv.org/abs/2603.21852) · CC BY 4.0

Live explorer: **https://monogate.dev** (or your deployed URL)

---

## Install

**JavaScript / Node**
```bash
npm install monogate
```

**Python**
```bash
pip install monogate            # core only (no dependencies)
pip install "monogate[torch]"   # + PyTorch differentiable ops + EMLTree / EMLNetwork
```

## Usage

```js
import { op, exp, ln, add, mul, pow, E, ZERO } from "monogate";

// The core operator
op(1, 1);        // e        (exp(1) − ln(1))
op(1, op(op(1,1), 1));  // 0   (e − e = 0)

// Derived functions — all built from eml + 1
exp(3);          // e³
ln(Math.E);      // 1
add(2, 3);       // 5
mul(4, 5);       // 20
pow(2, 10);      // 1024
```

## API

All functions are pure and stateless. Domain constraints are noted — violating them produces `NaN` or `±Infinity`.

### Core

| Export | Formula | Nodes | Depth |
|--------|---------|-------|-------|
| `op(x, y)` | `exp(x) − ln(y)` | — | — |
| `E` | `op(1,1)` | 1 | 1 |
| `ZERO` | `op(1, op(op(1,1), 1))` | 3 | 3 |
| `NEG_ONE` | `op(ZERO, op(2,1))` | 5 | 4 |

### Elementary functions

| Export | Math | Domain | Nodes | Depth |
|--------|------|--------|-------|-------|
| `exp(x)` | eˣ | ℝ | 1 | 1 |
| `ln(x)` | ln x | x > 0 | 3 | 3 |
| `sub(x, y)` | x − y | x > 0 | 5 | 4 |
| `neg(y)` | −y | ℝ (two-regime) | 9 | 5 |
| `add(x, y)` | x + y | ℝ | 11 | 6 |
| `mul(x, y)` | x × y | x,y > 0 | 13 | 7 |
| `div(x, y)` | x / y | x,y > 0 | 15 | 8 |
| `pow(x, n)` | xⁿ | x > 0 | 15 | 8 |
| `recip(x)` | 1/x | x > 0 | 5 | 4 |

The **depth** ranking of elementary functions by EML tree depth is new to mathematics.

### `IDENTITIES`

An array of `{ name, emlForm, nodes, depth, status }` records — useful for building explorers or documentation.

## `monogate/cost` — Pfaffian cost analysis

Sub-path import (added in 1.2.0). Analyzes a symbolic expression and
returns its Pfaffian profile: chain order, EML routing depth, structural
overhead, oscillation/composite/fusion corrections, and a canonical
cost-class fingerprint string.

```js
import { analyze, parse, distance } from 'monogate/cost';

analyze('exp(sin(x))');
// { pfaffian_r: 3, max_path_r: 3, eml_depth: 4,
//   structural_overhead: 0,
//   corrections: { c_osc: 1, c_composite: 0, delta_fused: 0 },
//   predicted_depth: 4, is_pfaffian_not_eml: false,
//   cost_class: 'p3-d4-w3-c1' }

analyze('1/(1+exp(-x))').cost_class;   // 'p1-d2-w1-c0' — sigmoid, fused
analyze('log(1+exp(x))').cost_class;   // 'p2-d1-w2-c-1' — softplus, fused
analyze('x*(1+erf(x/sqrt(2)))/2');     // GELU exact, is_pfaffian_not_eml=true
```

The cost-class string follows the Python `eml-cost` convention:
`p<pfaffian_r>-d<eml_depth>-w<max_path_r>-c<correction_sum>` where
`correction_sum = c_osc + c_composite − delta_fused`. All 32
cross-checked test cases produce byte-identical fingerprints to the
Python `eml-cost` package.

Distance metric for clustering / equivalence-class lookup:

```js
import { analyze, distance, compare } from 'monogate/cost';

const a = analyze('1/(1+exp(-x))');                // sigmoid
const b = analyze('exp(x)/(1+exp(x))');            // also sigmoid
distance(a, b);                                    // weighted L2
compare(a, b);                                     // per-axis deltas
```

Reference: [arXiv:2603.21852](https://arxiv.org/abs/2603.21852) +
Khovanskii (1991) Pfaffian fewnomials.

### `predict_precision_loss(expr)` — float64 numerical-precision predictor

Added in 1.3.0. Port of Python `eml_cost.predict_precision_loss`
(eml-cost 0.7.0) — same regression coefficients fit on the E-193
bench-300-domain corpus (n=379, 5-fold CV R^2 = +0.27, residual log10
std = 0.77).

```js
import { predict_precision_loss, FLOAT64_EPS } from 'monogate/cost';

const r = predict_precision_loss('exp(exp(x)) + sin(x**2)');
r.predicted_max_relerr        // ~ 2.6e-15
r.predicted_digits_lost       // ~ 1.07 decimal digits lost vs perfect float64
r.ci95                        // [low, high] — wide, ~factor 30 either way
r.cv_r2                       // 0.271 (carried for honest reporting)
```

**Honest framing** (mirrors the Python docstring): modest predictor
for **rank-ordering and high-risk subtree surfacing**, NOT for
absolute precision claims. **Not a form recommender** — E-193 Phase 3
showed only 30% best-pick on algebraically-equivalent rewrite tests,
well below the 70% product threshold; that recommender was deliberately
not shipped. Do not use this to choose between
`1/(1+exp(-x))` and `tanh(x/2)/2 + 1/2`.

**Parity with Python:** 14 of 20 representative test cases produce
byte-identical predictions; the other 6 differ by up to ~10x because
SymPy's automatic canonicalizations (e.g. `Mul(1, Pow(x,-1)) → Pow(x,-1)`,
`Mul(-1, x) ↔ Neg(x)`, `sqrt → Pow(x, 1/2)`) shift count_ops or
tree_size on the JS-parsed literal tree. All cases stay well within
each other's 95% prediction interval.

## Open challenges

These functions have no known EML construction:

- **sin x** — no construction found
- **cos x** — no construction found
- **π** — no construction as a closed EML expression
- **i** (√−1) — open under strict principal-branch grammar. Under the extended-reals convention (`ln(0) = −∞`), i is constructible from `{1}` alone in K=75 nodes ([pveierland/eml-eval](https://github.com/pveierland/eml-eval)). These are different grammars, not contradictory results.

Pull requests welcome. If you crack one, open an issue — it's publishable.

## How it works

The grammar is just two production rules:

```
S → 1
S → eml(S, S)
```

Any expression built from this grammar computes some value. The paper proves that the specific compositions above equal the named functions exactly (not approximately). Floating-point errors are at machine epsilon (`< 1e-13`).

The `neg` function uses a two-regime construction to avoid overflow:
- **y ≤ 0**: tower formula via `exp(eʸ)` — stable because `eʸ ≤ 1`
- **y > 0**: shift formula — computes `exp(y+1)` instead of a tower

## License

MIT — see [LICENSE](./LICENSE). The underlying mathematics is CC BY 4.0 per the original paper.
