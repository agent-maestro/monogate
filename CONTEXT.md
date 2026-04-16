# monogate — Complete Project Context
> Single-document briefing for the full state of the project as of **v1.0.0**, April 2026.
> Branch: `master`. Tag: `v1.0.0`. PyPI: `pip install monogate==1.0.0`.
> arXiv: arXiv:2603.21852 (Odrzywołek 2026, CC BY 4.0).

---

## 1. Project Overview

**monogate** is a Python and JavaScript library built around a single algebraic discovery:
the binary operator

    eml(x, y) = exp(x) − ln(y),    constant = 1

generates every elementary function as a finite binary tree of identical nodes.
This was proved by Odrzywołek (2026, arXiv:2603.21852).

monogate provides:
- A symbolic computation engine that builds, evaluates, and rewrites EML expression trees.
- **BEST routing**: a hybrid dispatcher (EML/EDL/EXL) that cuts node count 52–74% and
  delivers up to 2.8× wall-clock speedup with zero accuracy loss.
- A PyTorch integration layer (`EMLLayer`) as a drop-in activation for SIREN, NeRF, PINN.
- Rust-accelerated kernels via PyO3 (5.9×) and a fused Python kernel (3.6×).
- An exhaustive symbolic search engine (N≤11, 281M trees).
- A gradient-free MCTS search module that avoids phantom-attractor traps.
- **15 special functions** pre-computed as CBEST/BEST expressions (`monogate.special`).
- **Symbolic regression leaderboard** over 10 Nguyen/Keijzer benchmarks (`monogate.leaderboard`).
- **Physics-Informed EML Networks** for 7 differential equations (`monogate.pinn`).
- **Certified interval arithmetic** through EML trees (`monogate.interval`).
- **SymPy interoperability**: to_sympy, from_sympy, latex_eml (`monogate.sympy_bridge`).
- **Streamlit web demo** — 5 interactive tabs, deployable to Streamlit Cloud (`streamlit_app.py`).
- **L∞ minimax approximation** framework with MCTS minimax objective (`monogate.minimax`).
- **CBEST physics identity catalog** — 7 PDE/ODE solutions, 4 exact 1-node CBEST (`monogate.physics`).
- **sklearn-compatible symbolic regressor** with MCTS/beam backend (`monogate.sklearn_wrapper`).
- **Neurosymbolic theorem prover** — 4-tier proof strategy (numerical/SymPy/certified/witness) (`monogate.prover`).
- **71-identity catalog** across 7 categories (`monogate.identities`).

**The central research question** monogate addresses:

> Can sin(x) be expressed exactly as a finite real-valued EML tree?

**Answer**: No. The Infinite Zeros Barrier theorem proves this for all N on structural
grounds. Empirical confirmation: 281,026,468 trees (N≤11), zero candidates. The
complex bypass Im(eml(ix,1)) = sin(x) recovers the function exactly in one node.

**Operator family:**

| Operator | Definition          | Constant | Complete? | Strength                         |
|----------|---------------------|----------|-----------|----------------------------------|
| EML      | exp(x) − ln(y)      | 1        | Yes       | Add, subtract                    |
| EDL      | exp(x) / ln(y)      | e        | Yes*      | Div (1 node), mul (7 nodes)      |
| EXL      | exp(x) · ln(y)      | 1        | No        | ln (1 node), pow (3 nodes), stability |
| EAL      | exp(x) + ln(y)      | 1        | No        | —                                |
| EMN      | ln(y) − exp(x)      | −∞       | No        | —                                |

\* EDL is complete over {×, ÷, pow, ln, exp} but **not** over the additive group (formally proved; see `docs/research/edl_completeness_proof.md`).

---

## 2. Full File Structure

```
monogate/                          # repo root  (branch: master, tag: v1.0.0)
├── streamlit_app.py               # 5-tab Streamlit demo (Optimizer, Special Fns,
│                                  #   PINN, MCTS Explorer, Phantom Attractor)
├── requirements-streamlit.txt     # Streamlit Cloud deps (no torch required)
├── CONTEXT.md                     # this file — current project briefing
├── Makefile                       # make reproduce-n11, reproduce-all, paper, docker-*
├── Dockerfile                     # clean-room reproduce environment
├── python/                        # Python library (PyPI: monogate==1.0.0)
│   ├── monogate/                  # main package
│   │   ├── __init__.py            # public API re-exports, __version__ = "1.0.0"
│   │   ├── core.py                # op(), E, ZERO, NEG_ONE; all EML/EDL/EXL scalar ops;
│   │   │                          #   _NODE_COSTS table; IDENTITIES dict
│   │   ├── operators.py           # BEST, CBEST operator dispatch objects
│   │   ├── network.py             # EMLTree, EMLNetwork, HybridNetwork, fit()
│   │   ├── optimize.py            # best_optimize(), context_aware_best_optimize();
│   │   │                          #   OptimizeResult, OpMatch, BestRewriter
│   │   ├── torch_ops.py           # PyTorch tensor EML/EXL/EDL ops (softplus-safe)
│   │   ├── fused_rust.py          # get_best_activation(), FusedEMLActivation,
│   │   │                          #   RustFusedLayer, RUST_AVAILABLE, rust_info()
│   │   ├── complex_eval.py        # complex_eml_sin/cos/eval; Im(eml(ix,1))=sin(x)
│   │   ├── complex_best.py        # CBEST class; im(), re() helpers; node counts
│   │   ├── complex_search.py      # MCTS over complex EML grammar
│   │   ├── special.py             # CATALOG + 15 callables (sin_cb, cos_cb, erf_cb,
│   │   │                          #   j0_cb, ai_cb, lgamma_cb, digamma_cb, …)
│   │   ├── leaderboard.py         # PROBLEMS dict; run_leaderboard(),
│   │   │                          #   markdown_leaderboard(); LeaderboardEntry
│   │   ├── pinn.py                # EMLPINN, fit_pinn(), PINNResult; 7 equations:
│   │   │                          #   harmonic, burgers, heat, schrodinger,
│   │   │                          #   kdv_soliton, nls, lotka_volterra
│   │   ├── interval.py            # Interval, eml_interval(), eval_interval(),
│   │   │                          #   bound_expression()
│   │   ├── sympy_bridge.py        # to_sympy, from_sympy, simplify_eml, latex_eml,
│   │   │                          #   verify_identity (optional: pip install monogate[sympy])
│   │   ├── minimax.py             # MinimaxResult, minimax_eml(), minimax_survey();
│   │   │                          #   L∞ minimax approximation via MCTS objective='minimax'
│   │   ├── physics.py             # 7 PDE/ODE callables + PHYSICS_CATALOG;
│   │   │                          #   schrodinger_free_cb, potential_well_cb,
│   │   │                          #   nls_soliton_amplitude_cb, heat_kernel_cb,
│   │   │                          #   kdv_soliton_cb, wave_cos_cb, wave_sin_cb
│   │   ├── sklearn_wrapper.py     # EMLRegressor (sklearn BaseEstimator+RegressorMixin);
│   │   │                          #   fit, predict, get_formula, get_tree, get_params
│   │   ├── prover.py              # EMLProver, ProofResult, BenchmarkReport;
│   │   │                          #   4-tier proof: numerical→SymPy→interval→witness
│   │   ├── identities.py          # Identity dataclass; 71 identities in 7 categories:
│   │   │                          #   trig(17), hyperbolic(12), exponential(12),
│   │   │                          #   special(12), physics(7), eml_structural(6), open(5)
│   │   ├── validate.py            # monogate-validate CLI; challenge board validation
│   │   ├── torch/
│   │   │   ├── __init__.py        # exports EMLLayer, EMLActivation
│   │   │   └── eml_layer.py       # EMLLayer (nn.Module); mode='activation'|'tree';
│   │   │                          #   compiled=True; ONNX opset 17; torch.compile
│   │   ├── compile/
│   │   │   ├── __init__.py        # exports FusedEMLLayer, FusedEMLActivation
│   │   │   ├── fused.py           # FusedEMLActivation: vectorised bottom-up kernel
│   │   │   └── compiler.py        # compile_eml_layer(): torch.compile wrapper
│   │   ├── llm/
│   │   │   ├── __init__.py        # exports suggest_and_optimize
│   │   │   ├── optimizer.py       # LLM → BEST expression (mock/openai/groq/anthropic)
│   │   │   ├── prompts.py         # prompt templates
│   │   │   └── cli.py             # monogate-optimize CLI entry point
│   │   └── search/
│   │       ├── __init__.py        # exports mcts_search, beam_search, analyze_n11
│   │       ├── mcts.py            # mcts_search(), beam_search(); MCTSResult;
│   │       │                      #   UCB1 + 1/(1+MSE) reward; immutable tree dicts;
│   │       │                      #   objective='mse'|'minimax' support
│   │       ├── gpu_search.py      # GPU-accelerated search (PyTorch tensor eval)
│   │       ├── analyze_n11.py     # analyze_n11(): N=1–11 table; --html export
│   │       ├── sin_search_03.py   # N=9 exhaustive (parity filter)
│   │       ├── sin_search_04.py   # N=10 exhaustive (ProcessPoolExecutor)
│   │       └── sin_search_05.py   # N=11 exhaustive; vectorised NumPy; 323s
│   ├── tests/                     # 983 passing, 9 skipped, 0 failed (2026-04-16)
│   │   ├── test_core.py, test_network.py, test_optimize.py, test_search.py
│   │   ├── test_torch.py, test_compile.py, test_complex.py, test_eml_layer.py
│   │   ├── test_llm.py, test_complex_best.py, test_pinn.py
│   │   ├── test_minimax.py        # 27 tests: MinimaxResult, minimax_eml, minimax_survey
│   │   ├── test_physics.py        # 28 tests: all 7 callables + PHYSICS_CATALOG
│   │   ├── test_sklearn_wrapper.py # 24 tests: EMLRegressor fit/predict/score/API
│   │   ├── test_prover.py         # 78 tests: EMLProver, ProofResult, BenchmarkReport
│   │   └── (+ interval, sympy_bridge, special, leaderboard tests)
│   ├── experiments/
│   │   ├── gen_attractor_data.py       # 40 seeds × λ∈{0,0.005}, depth=3, 3000 steps
│   │   ├── gen_attractor_data_v2.py    # 20 seeds × 10 λ values; λ_crit=0.001 sweep
│   │   ├── attractor_phase_transition.json  # raw sweep results (used by Streamlit tab 5)
│   │   ├── attractor_data.json         # 40-seed attractor curves (used by explorer)
│   │   ├── plot_attractor_landscape.py # paper/figures/attractor_landscape.pdf
│   │   ├── experiment_12_siren.py      # EML-SIREN comparison
│   │   ├── research_02/03/04.py        # attractor, EDL completeness, tree search studies
│   │   ├── research_07_attractor_identity.py   # Phase 1: mpmath/PSLQ identity search
│   │   ├── research_07b_basin_geometry.py      # Phase 1: 2D basin heatmap
│   │   ├── research_08_physics_survey.py       # Phase 4: CBEST physics identity survey
│   │   └── srbench_runner.py           # Phase 5: EMLRegressor on Nguyen/Keijzer/Vladis.
│   ├── notebooks/
│   │   ├── eml_layer_siren_example.py
│   │   ├── siren_with_monogate.py      # EMLSirenNet vs SirenNet; PSNR comparison
│   │   ├── mcts_sin_approximation.py
│   │   ├── performance_kernels.py
│   │   ├── llm_optimizer_demo.py
│   │   ├── complex_special_functions.py   # Session 1 notebook
│   │   ├── pinn_eml_demo.py               # Session 4 notebook
│   │   ├── minimax_approximation.py       # Session 2 notebook
│   │   └── attractor_generalization.py    # attractor in Taylor/Padé/CF bases
│   ├── scripts/
│   │   ├── update_arxiv_id.py             # post-submission ID update
│   │   ├── update_leaderboard.py          # run leaderboard + save results/leaderboard.json
│   │   ├── update_srbench_leaderboard.py  # regenerate SRBENCH.md from srbench_results.json
│   │   └── reproduce_n11.py               # reproduce N=11 from sin_n11.json cache
│   ├── paper/
│   │   ├── preprint.tex                   # arXiv-ready LaTeX (authoritative)
│   │   ├── arxiv_submission_notes.md      # abstract ≤250w, categories, checklist
│   │   └── README.md                      # pdflatex build + arXiv upload (5 steps)
│   ├── docs/                              # MkDocs source
│   │   ├── research/
│   │   │   ├── phantom_attractors.md      # attractor investigation + identity search
│   │   │   ├── edl_completeness_proof.md  # formal proof: EDL additive incompleteness
│   │   │   └── minimax_approximation.md   # minimax EML theory + survey results
│   │   ├── guide/
│   │   │   ├── symbolic_regression.md     # EMLRegressor tutorial
│   │   │   └── pinn.md                    # PINN + physics survey guide
│   │   └── concepts/
│   │       ├── eml_universal_operator.md
│   │       └── best_routing.md
│   ├── results/
│   │   ├── sin_n11.json                   # N=11 search output
│   │   ├── leaderboard.json               # latest Nguyen/Keijzer leaderboard
│   │   ├── physics_identities_catalog.json # 7 PDE/ODE CBEST identity metadata
│   │   └── minimax_survey.json            # L∞ k-node survey results
│   ├── CHANGELOG.md                       # version history v0.1–v1.0.0
│   ├── PAPER.md                           # internal research notes (updated to v1.0.0)
│   ├── THEORY.md                          # formal theory: R1-R4 resolved, C3-C7 open
│   ├── SRBENCH.md                         # SRBench leaderboard table (EMLRegressor)
│   ├── RESULTS.md                         # N=1–11 table + near-miss gallery
│   ├── ANNOUNCEMENT.md                    # launch posts
│   ├── pyproject.toml                     # version="1.0.0"; extras: torch,llm,sympy,streamlit,dev
│   └── mkdocs.yml
├── explorer/                       # React/Vite SPA (monogate.dev, deployed on Vercel)
│   ├── src/App.jsx                  # tab router
│   └── src/components/             # OptimizeTab, AttractorViz, ResearchTab, LeaderboardTab
├── lib/                            # JS/npm package (monogate 0.2.0)
└── monogate-core/                  # Rust/PyO3 extension (5.9× speedup)
    ├── src/lib.rs                  # eval_eml_batch(); rayon parallel
    └── Cargo.toml
```

---

## 3. Feature Inventory

### `monogate.core`

| Name | Type | Signature | Description |
|------|------|-----------|-------------|
| `op` | function | `op(x, y) -> float` | `eml(x,y) = exp(x) - ln(y)` with softplus-safe ln |
| `E` | constant | `float = math.e` | EML/EXL neutral constant |
| `exp_eml`, `ln_eml` | function | scalar | exp/ln via EML (1, 3 nodes) |
| `sub_eml`, `neg_eml` | function | scalar | subtract, negate via EML (5, 9 nodes) |
| `add_eml`, `mul_eml` | function | scalar | add, multiply via EML (11, 13 nodes) |
| `div_eml`, `pow_eml`, `recip_eml` | function | scalar | divide, power, reciprocal via EML |
| `_NODE_COSTS` | dict | `{op: {family: int}}` | Per-operation node cost table |
| `IDENTITIES` | dict | `{name: str}` | Human-readable EML identities |

---

### `monogate.network`

| Name | Type | Signature | Description |
|------|------|-----------|-------------|
| `EMLTree` | class | `EMLTree(depth=3)` | Trainable complete binary EML tree; leaves are scalar `nn.Parameter` |
| `EMLNetwork` | class | `EMLNetwork(in_features, depth, op_func=None)` | Vectorised EML network |
| `HybridNetwork` | class | `HybridNetwork(in_features, depth)` | EXL inner + EML root |
| `fit` | function | `fit(model, target, steps, lr, lam, log_every) -> list[float]` | Adam training loop |

---

### `monogate.optimize`

`best_optimize(expr_or_func) -> OptimizeResult`, `context_aware_best_optimize(...)`.
`OptimizeResult`: original, ops, total_best_nodes, total_eml_nodes, savings_pct, python_snippet.

---

### `monogate.search`

| Name | Signature | Description |
|------|-----------|-------------|
| `mcts_search(target_fn, probe_points, depth, n_simulations, seed, objective) -> MCTSResult` | function | MCTS; objective='mse'\|'minimax' |
| `beam_search(target_fn, probe_points, depth, width) -> MCTSResult` | function | Beam search (no seed kwarg) |
| `MCTSResult` | dataclass | best_tree, best_mse, best_formula, history, objective |

---

### `monogate.special`

15 pre-computed CBEST/BEST expressions. `CATALOG` dict maps name → `SpecialFnEntry`.

| Function | Nodes | Backend | Max error |
|----------|-------|---------|-----------|
| sin, cos | 1 | CBEST | 1e-15 |
| sinh, cosh | 9, 15 | BEST | 1e-14 |
| tanh, sech | 8, 16 | BEST | 1e-14 |
| erf | 5 | CBEST | 1.5e-2 |
| Fresnel S/C integrand | 2 | CBEST | 1e-15 |
| Bessel J₀, Airy Ai | 7, 9 | CBEST | 1e-4, 2e-3 |
| lgamma, digamma | 12, 14 | BEST | 1e-9, 1e-8 |

---

### `monogate.minimax`

```python
minimax_eml(target_fn, n_nodes=3, domain=(-1,1), n_probe=200,
            n_simulations=2000, seed=None) -> MinimaxResult
minimax_survey(target_fn, node_counts=[1,3,5,7,9,11], domain, n_probe,
               n_simulations) -> list[dict]
```

`MinimaxResult` (frozen dataclass): `best_tree`, `best_formula`, `linf`, `l2`, `n_nodes`,
`domain`, `n_probe`, `elapsed_s`, `mcts_result`.

Survey dict keys: `n_nodes`, `depth`, `formula`, `linf`, `l2`, `elapsed_s`.

---

### `monogate.physics`

```python
schrodinger_free_cb(x, k=1.0, part='complex')  # exp(ikx); part='re'|'im'|'complex'
potential_well_cb(x, n=1, L=1.0)               # sin(nπx/L)
nls_soliton_amplitude_cb(x)                    # sech(x)
heat_kernel_cb(x, t=1.0)                       # raises ValueError for t≤0
kdv_soliton_cb(x, t=0.0, c=4.0)               # (c/2)sech²(√(c/4)(x-ct))
wave_cos_cb(x, k=1.0, omega=1.0, t=0.0)       # cos(kx-ωt)
wave_sin_cb(x, k=1.0, omega=1.0, t=0.0)       # sin(kx-ωt)
PHYSICS_CATALOG                                 # dict: 7 entries with metadata
```

`PHYSICS_CATALOG` entry keys: `equation`, `callable`, `formula`, `n_nodes`, `backend`,
`max_abs_error`, `notes`.

---

### `monogate.sklearn_wrapper`

```python
EMLRegressor(max_depth=5, n_simulations=5000, search_method='mcts',
             objective='mse', random_state=None)
# Methods: fit(X, y), predict(X), score(X, y), get_formula(), get_tree()
# Fitted attrs: tree_, formula_, best_score_, n_features_in_
# sklearn API: get_params(deep), set_params(**params)
```

Works without scikit-learn installed (stub base classes introspect `__init__` via `inspect.signature`).

---

### `monogate.prover`

```python
EMLProver(verbose=False, n_probe=500)
prover.prove(identity_str) -> ProofResult
prover.prove_batch(identities) -> list[ProofResult]
prover.benchmark() -> BenchmarkReport
```

Identity string format: `"sin(x)**2 + cos(x)**2 == 1"`.

`ProofResult` fields: `status` ('proved_exact'|'proved_certified'|'proved_numerical'|
'proved_witness'|'inconclusive'|'failed'), `confidence` (0–1), `max_residual`,
`lhs_formula`, `latex_proof`, `sympy_simplification`, `node_count`, `notes`.

`BenchmarkReport`: `results`, `summary()`, `to_json()`.

---

### `monogate.identities`

```python
from monogate.identities import (
    TRIG_IDENTITIES,        # 17 identities
    HYPERBOLIC_IDENTITIES,  # 12
    EXPONENTIAL_IDENTITIES, # 12
    SPECIAL_IDENTITIES,     # 12
    PHYSICS_IDENTITIES,     # 7
    # + EML_STRUCTURAL(6), OPEN_CHALLENGES(5)
    get_by_difficulty(difficulty),  # 'easy'|'medium'|'hard'|'research'
    get_by_category(category),      # filter by category string
)
```

`Identity` (frozen dataclass): `name`, `expression`, `latex`, `category`, `domain`,
`difficulty`, `notes`, `expected_method`.

---

### `monogate.pinn`

```python
EMLPINN(equation, backbone_depth, omega, nu, k, c, alpha, beta, lam_physics)
fit_pinn(model, x_data, y_data, x_phys, steps, lam_physics, log_every) -> PINNResult
```

Equations: `harmonic`, `burgers`, `heat`, `schrodinger`, `kdv_soliton`, `nls`, `lotka_volterra`.

---

### `monogate.interval`

```python
Interval(lo, hi)                        # frozen dataclass
eml_interval(a: Interval, b: Interval) -> Interval
eval_interval(tree, x_interval)
bound_expression(expr_str, x_lo, x_hi) -> Interval
```

---

### `monogate.sympy_bridge` *(optional: `pip install monogate[sympy]`)*

```python
to_sympy(tree)          # EML tree dict → SymPy expression
from_sympy(expr)        # SymPy → EML tree (best-effort)
simplify_eml(tree)      # to_sympy + sympy.simplify()
latex_eml(tree)         # LaTeX string via sympy.latex()
verify_identity(t1, t2) # symbolic equality check
```

---

## 4. Research Results

### N=1–11 Exhaustive Search

Complete enumeration of EML trees with terminals {1, x}, parity filter applied (sin is odd).
Total: **281,026,468 trees** evaluated. Zero candidates at tolerances 1e-4, 1e-6, 1e-9.
N=11 runtime: **323 seconds** on a single CPU (vectorised NumPy batch evaluator).

**The Infinite Zeros Barrier:**
> *No finite real-valued EML tree with terminals {1, x} equals sin(x) for all x ∈ R.*

Proof: sin(x) has zeros at {kπ : k ∈ Z}. Every finite EML tree is real-analytic with
finitely many zeros. Contradiction. Extends to cos(x), Bessel J₀, Airy Ai, etc.

**Complex bypass:** `Im(eml(ix, 1)) = Im(exp(ix)) = sin(x)`. One node. Machine precision.

### Phantom Attractor

- Depth-3 EMLTree, Adam, lr=5e-3, 3000 steps, 40 seeds targeting π
- λ=0: **0/40** reach π; all converge to **≈3.169642** (MSE~9×10⁻⁴)
- λ=0.001 (λ_crit): **20/20** reach π (sharp phase transition)
- λ=0.005: **40/40** reach π (MSE < 1e-8)
- Attractor ≈3.169642 tested against π, e, ln(k), √k, small rationals, PSLQ — **novel constant** (no known closed form found)
- Phenomenon is EML-topology-specific (not present in Taylor/Padé/CF bases)

### CBEST Physics Survey

| Equation | Solution | Nodes | Backend | Exact? |
|----------|----------|-------|---------|--------|
| Free-particle Schrödinger | exp(ikx) | 1 | CBEST | Yes |
| Infinite square well | sin(nπx/L) | 1 | CBEST | Yes |
| Wave equation (cos) | cos(kx−ωt) | 1 | CBEST | Yes |
| Wave equation (sin) | sin(kx−ωt) | 1 | CBEST | Yes |
| NLS bright soliton | sech(x) | 2 | BEST | Yes |
| Heat fundamental | exp(−x²/4t)/√(4πt) | 4 | BEST | Yes |
| KdV 1-soliton | (c/2)sech²(√(c/4)(x−ct)) | 18 | BEST | ~yes |

### EDL Additive Incompleteness (Proved)

Formal proof via structural induction + Lindemann-Weierstrass (see `docs/research/edl_completeness_proof.md`):
- **Lemma:** Every EDL tree evaluates to a product/quotient of exp/ln terms (multiplicative).
- **Theorem:** Addition of two independent reals is unreachable in any finite EDL tree.
- **Corollary:** EDL is complete over {×, ÷, pow, ln, exp} but not the additive group.
- **Empirical:** N≤6 exhaustive search (196 trees from terminal {e}) confirms zero additive combinations.

---

## 5. Benchmarks

### EMLLayer Performance (depth=2, 256→256, batch=1024, CPU)

| Backend | ms/step | Speedup |
|---------|---------|---------|
| Standard (recursive Python) | 8.3 | 1× |
| FusedEMLActivation | 2.3 | **3.6×** |
| FusedEMLActivation + torch.compile | 1.9 | **4.4×** |
| Rust (monogate-core) | 1.4 | **5.9×** |

### BEST Routing Wall-Clock

| Workload | Savings | Speedup |
|----------|---------|---------|
| sin/cos Taylor (TinyMLP) | 74% | **2.8×** |
| Polynomial x⁴+x³+x² | 54% | **2.1×** |
| GELU (Transformer FFN) | 18% | 0.93× |

Crossover threshold: ~20% node savings.

---

## 6. Version History

### v1.0.0 (2026-04-16) — current

**Phases 1–6 complete. 983 tests passing.**

- **monogate.minimax**: `MinimaxResult`, `minimax_eml()`, `minimax_survey()` — L∞ MCTS approximation
- **monogate.physics**: 7 PDE/ODE callables, `PHYSICS_CATALOG`; 4 of 7 = 1-node CBEST exact
- **monogate.sklearn_wrapper**: `EMLRegressor` (sklearn-compatible); MCTS/beam backend
- **monogate.prover**: `EMLProver`, `ProofResult`, `BenchmarkReport`; 4-tier proof strategy
- **monogate.identities**: 71-identity catalog, 7 categories, difficulty tiers
- **Research:** phantom attractor identity investigation; EDL additive incompleteness formally proved; CBEST physics survey; neurosymbolic prover architecture
- **Docs:** THEORY.md (R1-R4 resolved, C3-C7 open), SRBENCH.md, docs/concepts/, docs/outreach/
- PyPI: `pip install monogate==1.0.0`

### v0.12.0 (2026-04-16)

- `streamlit_app.py`: 5-tab Streamlit demo
- `requirements-streamlit.txt`: Streamlit Cloud deps
- `[streamlit]` optional dep group in `pyproject.toml`

### v0.11.0 (Sessions 2+4+5)

- `monogate.leaderboard`: 10 Nguyen/Keijzer problems; GitHub Actions daily refresh
- `monogate.pinn` extended: Schrödinger, KdV, NLS, Lotka-Volterra; exp(ikx)=1 CBEST node
- `monogate.interval`: certified interval arithmetic
- `monogate.sympy_bridge`: SymPy interop (`[sympy]` extra)
- `attractor_generalization.py`: phantom attractor confirmed EML-topology-specific
- 913 tests passing

### v0.10.0 (Session 1)

- `monogate.special`: 15 CBEST/BEST expressions; CATALOG; SpecialFnEntry
- `monogate.complex_best`: CBEST class; im/re helpers
- `monogate.complex_search`: MCTS over complex EML grammar
- Key identity: `fresnel_s_integrand(x) = Im(eml(i·πx²/2, 1))` — 2 nodes, exact

---

## 7. Open Problems

| # | Problem | Status |
|---|---------|--------|
| C3 | Phantom attractor ≈3.169642 exact identity | Open — likely novel constant |
| C4 | λ_crit formula as function of depth | Open |
| C5 | N=12 exhaustive search | Open — needs GPU (~$15-50) |
| C6 | CBEST completeness — which analytic functions admit k-node CBEST? | Open |
| C7 | EMLNetwork convergence — does training converge to minimax-optimal trees? | Open |

Resolved: R1 (EML completeness), R2 (Infinite Zeros Barrier), R3 (Complex bypass), R4 (EDL additive incompleteness).

### Challenge Board (monogate.dev/board)

| Problem | Status |
|---------|--------|
| sin(x) real-domain | open — Barrier theorem rules out; complex: Im(eml(ix,1)) exact |
| Lambert W₀(x) | open — near-miss MSE~0.012 |
| Airy Ai(x) | open — Barrier corollary applies |

---

## 8. Deployment

| Service | URL / Command | Notes |
|---------|--------------|-------|
| PyPI | `pip install monogate==1.0.0` | Live |
| arXiv | arXiv:2603.21852 | Odrzywołek 2026, CC BY 4.0 |
| Explorer | monogate.dev | Vercel, branch master |
| API | https://monogate-api.fly.dev | fly.io, wraps best_optimize() |
| Streamlit | streamlit run streamlit_app.py | Streamlit Cloud, branch phase9-arxiv-live |
| flyctl | ~/.fly/bin/flyctl.exe | Windows path |

---

## 9. Paper Status

**arXiv preprint:** arXiv:2603.21852 (Odrzywołek 2026, reference paper).
**Working notes paper:** `python/PAPER.md` (v1.0.0, documents all implementations).
**LaTeX preprint:** `python/paper/preprint.tex` — builds with `pdflatex preprint.tex` (twice).

**Five Contributions (preprint):**
1. BEST hybrid routing (52%/74% savings, 2.8× speedup)
2. Phantom attractors (λ_crit=0.001 phase transition)
3. Infinite Zeros Barrier + N=11 exhaustive search
4. Performance kernels (FusedEML 3.6×, Rust 5.9×)
5. PyTorch integration (EMLLayer, ONNX, two modes)

**v1.0.0 additional contributions (documented in PAPER.md §10–14):**
- Minimax EML approximation framework
- CBEST physics identity survey
- sklearn-compatible EMLRegressor / SRBench
- Neurosymbolic theorem prover (4-tier)
- 71-identity catalog

---

*Generated for monogate v1.0.0 — April 2026*
*Branch: `master` · Tag: `v1.0.0` · 983 tests passing*
