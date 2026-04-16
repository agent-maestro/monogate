# Monogate Explorer

**Live:** https://explorer-taupe-five.vercel.app

An interactive explorer for the EML operator — a single binary function that generates all elementary arithmetic.

```
eml(x, y) = exp(x) − ln(y)
```

From this one operator and the constant `1`, every elementary function (exp, ln, addition, multiplication, trig via complex extension, and more) can be constructed as a pure expression tree.

Based on:
> **"All elementary functions from a single operator"**
> Andrzej Odrzywołek, Jagiellonian University, 2026
> [arXiv:2603.21852](https://arxiv.org/abs/2603.21852) · CC BY 4.0

---

## What's inside

**Verify tab** — pick any identity (eˣ, ln x, x+y, xⁿ, …), drag the slider, and watch the EML construction match the standard `Math.*` result in real time. Errors stay below 1e-13.

**Table tab** — every implemented function ranked by EML tree depth. This ranking of elementary functions by tree complexity is new to mathematics.

**Sandbox tab** — compose your own EML expression using `eml`, `exp`, `ln`, `neg`, `add`, `sub`, `mul`, `div`, `pow`, `recip`, and `x`. Sweep across a range instantly.

---

## Open challenges

These functions have no known EML construction using only the constant `1`:

| Function | Status |
|----------|--------|
| sin x | open |
| cos x | open |
| π | open |
| i (√−1) | open — *see note* |

> **Note on the complex extension:** Extending the grammar to complex numbers (`eml_c(x,y) = exp_c(x) − ln_c(y)`) produces `−iπ` in **11 nodes** from the single terminal `{1}` — the first non-real value reachable from one real constant. Under our grammar (strict principal-branch ln, `ln(0)` undefined), constructing `i` requires a second terminal (`2`), which then unlocks `π` and Euler's formula `exp(ix) = cos(x) + i·sin(x)` as a single EML expression.
>
> **Grammar note:** The table above reflects the *strict principal-branch* grammar where `ln(0)` is undefined. Under the *extended-reals* convention (`ln(0) = −∞`), as used in [pveierland/eml-eval](https://github.com/pveierland/eml-eval) and the original Odrzywołek paper, `i` IS constructible from `{1}` alone (K=75, depth=19, via `exp(ln(−1)/2)` where `2 = add(1,1)` is reachable through that convention's `neg`). The two results are not contradictory — they characterize different grammars. Whether `{1}` generates `i` under the strict grammar remains open. Pull requests welcome.

---

## Library

The underlying library is published separately as [`monogate`](https://www.npmjs.com/package/monogate):

```bash
npm install monogate
```

```js
import { op, add, mul, pow, E, ZERO } from "monogate";

op(1, 1);        // e
add(2, 3);       // 5
pow(2, 10);      // 1024
```

---

## Run locally

```bash
npm install
npm run dev
# → http://localhost:5173
```

## Tech

- [Vite](https://vitejs.dev/) + [React](https://react.dev/) 18
- No external UI dependencies — pure inline styles
- Deployed on [Vercel](https://vercel.com)

---

## License

MIT. The underlying mathematics is CC BY 4.0 per the original paper.
