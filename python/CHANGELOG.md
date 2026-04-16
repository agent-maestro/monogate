# Changelog

All notable changes to `monogate` are documented here.

---

## [0.7.0] — 2026-04-16

### Phase 5 — Sin Barrier Deep Search, Challenge Board v2, Compiled Core

**`monogate/search/sin_search_05.py` — N=11 Exhaustive Search**

- Vectorised NumPy batch evaluator: evaluates all 2^12 = 4,096 leaf assignments × 8
  probe points simultaneously per shape via a single bottom-up tree traversal.
  ~50–200× faster than the scalar Python evaluator in sin_search_04.
- Exact parity filter: tests all assignments (not just 64 samples), eliminating ~50% of
  shapes with zero false positives.
- Near-miss tracking: records the top-20 lowest-MSE assignments across all shapes/
  probings, enabling qualitative progress reporting even when no exact candidate exists.
- MCTS post-scan: after exhaustive search, runs MCTS to find the best approximation
  achievable by any finite EML tree (with `--mcts` or `--mcts-only`).
- N=12 dry-run: complexity estimate and time-budgeted partial run (`--n 12 --budget 300`).
- Result: **No EML tree equals sin(x) for any N ≤ 11**. Combined N≤11: ~281M trees.
- Exported: `monogate.search.run_exhaustive`, `run_mcts_approx`, `SearchResult`

**`monogate-core/` — Rust Compiled Core (PyO3)**

- New Rust crate in `monogate-core/` with PyO3 bindings.
- `eval_eml_batch(leaf_w, leaf_b, x, depth)` — fused bottom-up EML evaluation in Rust.
- `eval_best_batch(leaf_w, leaf_b, x, depth)` — BEST routing (EXL inner + EML root).
- Rayon parallel evaluation for batch sizes > 1,000.
- `benchmark_rust(n, depth)` — throughput in millions/sec.
- Sin-search helpers: `eval_tree_assignment`, `check_parity`, `parity_filter_stats`.
- Build: `cd monogate-core && pip install maturin && maturin develop --release`
- `monogate/fused_rust.py` — Python wrapper with graceful fallback to FusedEMLLayer.
- Estimated speedup: 50–200× over Python fused for depth=3–5 on large batches.

**`monogate/validate.py` — Challenge Board v2 Validator CLI**

- `validate_submission(submission, ...)` → `ValidationResult` with tier, points, node counts.
- Five tiers: exact (1e−12), tight (1e−8), medium (1e−5), approximate (1e−3), near_miss (5e−2).
- `monogate-validate submission.json` CLI entry point.
- `monogate-validate --list-problems` — shows all open problems and current best.
- GitHub Action `.github/workflows/validate-submission.yml` — auto-validates PR submissions
  and posts tier/MSE/node-count comment.

**`challenge/` — 10 Open Problems**

- `challenge/problems.json` v2: 10 problems incl. Lambert W₀, erf, Airy Ai, Bessel J₀,
  Poisson PINN residual, softplus exact, swish, exp(-x²).
- `challenge/leaderboard.json` — structured leaderboard with tier and per-problem stats.
- Drag-and-drop submission flow: copy template from LeaderboardTab → PR → auto-validation.

**Explorer — Two New Tabs**

- `LeaderboardTab.jsx` — Challenge Board v2 browser + leaderboard + submission template.
  Loads live data from `/challenge/problems.json` and `/challenge/leaderboard.json`.
- `ResearchTab.jsx` — Research Mode: sin barrier theorem, exhaustive search table through
  N=11, MCTS live search (connected to API if running, offline demo otherwise),
  near-miss approximation gallery, N=12 complexity estimate.

**`EMLLayer(compiled=True)` — Polish**

- `EMLLayer(..., compiled=True)` now uses `FusedEMLActivation` when `depth ≤ 3` and
  operator ∈ {EML, BEST}. Graceful fallback with warning for depth > 3.
- New `.compile()` method on `EMLLayer` (wraps with `compile_eml_layer`).
- `extra_repr` shows `fused=True` flag when compiled mode is active.

### Changed

- `monogate.__version__`: `0.6.0` → `0.7.0`
- `pyproject.toml`: version `0.7.0`, added `monogate-validate` CLI entry point
- `monogate.search.__init__`: exports `run_exhaustive`, `run_mcts_approx`, `SearchResult`
- `monogate.__init__`: exports `validate_submission`, `ValidationResult`, `load_problems`
- `mkdocs.yml`: added "Phase 5: Sin Barrier Deep Search" research page
- `explorer/src/App.jsx`: added `research` and `leaderboard` tabs
- `explorer/public/challenge/`: added `problems.json` + `leaderboard.json` static assets

---

## [0.6.0] — 2026-04-16

### Added

**`monogate.compile` — Performance kernels**

- `FusedEMLActivation(depth, operator)` — manually inlines the EML expression
  tree as a flat bottom-up vectorized computation over `(n_leaves, N)` tensors.
  No Python recursion; single broadcast multiply for all leaf evaluations.
  - Depth 1–3, operators EML and BEST
  - 1.5–3.6× faster than `EMLActivation` on CPU at typical batch sizes
  - Depth 4+ raises `ValueError` (Numerical Overflow Barrier documented)
- `FusedEMLLayer(in, out, depth, operator)` — drop-in for `EMLLayer(mode='activation')`.
  - 1.2–2.8× faster training step than `EMLLayer` in SIREN-style networks
  - Full `state_dict()` round-trip; ONNX-exportable
  - `.compile()` convenience method → `torch.compile` wrapper
- `compile_eml_layer(layer, mode, backend)` — `torch.compile` wrapper with
  graceful fallback for platforms without Inductor (Windows/Python 3.14)
- `to_torchscript(layer, method)` — TorchScript export via trace/script
- `benchmark_layer(*layers, batch_sizes, ...)` → `BenchmarkTable` — timing harness
  with `print_table()` and `as_dict()` output

**`monogate.llm` — LLM-assisted optimizer**

- `suggest_and_optimize(prompt, target_func, provider, ...)` → `LLMOptimizeResult`
  - Providers: `mock` (no key), `openai`, `groq`, `anthropic`
  - Sends structured prompt → LLM suggests math expression → BEST-optimized
  - Optional `run_mcts=True` adds gradient-free MCTS search
  - `result.print_summary()` — formatted human-readable output
  - `result.code` — copy-paste `f = lambda x: BEST.*` snippet
- `LLMOptimizeResult` dataclass with all fields
- `SUPPORTED_PROVIDERS` tuple
- `monogate-optimize` CLI entry point (installed by `pip install monogate`)
  - `monogate-optimize "sigmoid function"`
  - `monogate-optimize --provider openai "GELU activation"`
  - `monogate-optimize --mcts "exp(-x^2)"`

**Notebooks & benchmarks**

- `notebooks/performance_kernels.py` — measures activation throughput,
  layer throughput, training step timing; actual numbers on hardware
- `notebooks/llm_optimizer_demo.py` — LLM optimizer walkthrough with
  mock/OpenAI/Groq/Anthropic provider support
- `benchmarks/kernel_benchmarks.py` — full benchmark suite with JSON output

**Tests**

- `tests/test_compile.py` — 41 tests: FusedEMLActivation, FusedEMLLayer,
  compile wrapper, TorchScript, BenchmarkTable
- `tests/test_llm.py` — 40 tests: mock provider, expression analysis,
  BEST rewriting, CLI, integration tests (skip without API keys)
- Total: **593 passing, 8 skipped**

### Changed

- `monogate.__version__`: `0.5.0` → `0.6.0`
- `pyproject.toml`: added `[llm]` optional deps group, `[docs]` group,
  `monogate-optimize` CLI script entry point
- `monogate.__init__`: exports `FusedEMLActivation`, `FusedEMLLayer`,
  `compile_eml_layer`, `suggest_and_optimize`, `LLMOptimizeResult`
- `explorer/src/components/LandingPage.jsx`: added performance benchmark
  section with real numbers from CPU timing

---

## [0.5.0] — 2026-04-16

### Added

**`monogate.torch` — Differentiable EML layers for PyTorch**

- `EMLActivation(depth, operator)` — element-wise EML activation (drop-in for `torch.sin`, `F.gelu`, etc.)
  - Fully vectorized via `EMLNetwork(in_features=1)` backbone — no Python loops
  - Shapes preserved; all operators supported: `EML`, `EDL`, `EXL`, `BEST`
- `EMLLayer(in_features, out_features, depth, operator, mode)` — complete learnable layer
  - `mode='activation'`: `nn.Linear(in, out)` + shared `EMLActivation`
  - `mode='tree'`: `out_features` independent EML trees with linear leaves (interpretable)
  - `.formula()` — human-readable EML expression string / list
  - `.n_eml_nodes` — node count property
  - `state_dict()` / `load_state_dict()` round-trip
  - ONNX export (opset 14; all ops are ONNX-native)
- `compare_to_native(layer, native_name)` — prints node-count comparison vs sin/cos/GELU
- Notebook: `notebooks/eml_layer_siren_example.py` — SIREN with EMLLayer activation

**`monogate.complex_eval` — Complex-domain EML**

- `eml_complex(a, b)` — complex EML operator using `cmath` principal branch
- `eval_complex(node, x)` — tree evaluation with terminals `'x'`, `'ix'`, `'i'`, numeric
- `euler_path_node()` — tree dict for `eml(ix, 1)` (the Euler path)
- `sin_via_euler(x)` — exact `sin(x)` = `Im(eml(ix, 1))`, one node, machine precision
- `cos_via_euler(x)` — exact `cos(x)` = `Re(eml(ix, 1))`
- `score_complex_projection(node, probe_x, probe_y, projection)` — MSE of Im/Re part
- `formula_complex(node)` — formula string with complex terminal rendering
- `COMPLEX_TERMINALS` — extended terminal set `[1.0, 'x', 'ix', 'i']`

**`monogate.search` — MCTS and Beam Search**

- `mcts_search(target_fn, ...)` — Monte-Carlo Tree Search over EML grammar
  - UCB1 selection, random rollout completion, `1/(1+MSE)` reward
  - `n_rollouts` parameter: parallel rollouts via `ThreadPoolExecutor`
  - Returns `MCTSResult(best_tree, best_mse, best_formula, history, elapsed_s)`
- `beam_search(target_fn, ...)` — systematic beam search (top-`width` candidates per level)
  - Returns `BeamResult(best_tree, best_mse, best_formula, n_levels, elapsed_s)`
- Notebook: `notebooks/mcts_sin_approximation.py`

**Research: N=10 exhaustive search**

- `experiments/sin_search_04.py` — extends search to N=10 (34M trees, ~19s)
- Combined N≤10: **40,239,012 EML trees**, zero sin candidates at any tolerance
- 45.5% parity pruning for N=10 shapes

**Research: phase transition refinement**

- `experiments/gen_attractor_data_v2.py` — 10-lambda sweep, λ_crit = 0.001
- Depth=4 documented as Numerical Overflow Barrier (structural, not hyperparameter)

**Documentation**

- MkDocs site: `mkdocs.yml` + `docs/` (Home, Installation, 4 guides, 3 research pages, 6 API pages)
- `paper/preprint.tex` — arXiv-ready LaTeX (8 sections, full bibliography)
- `PAPER.md` — updated with N=10 results, depth=4 barrier, λ_crit, MCTS section

**Tests**

- `tests/test_eml_layer.py` — 68 tests: shapes, operators, gradients, serialization, ONNX
- `tests/test_complex.py` — 36 tests: Euler path, Pythagorean identity, Barrier bypass
- Total: **512 passing, 4 skipped** (ONNX skips without `onnx` package)

### Changed

- `monogate.__version__`: `0.4.0` → `0.5.0`
- `monogate.__init__` exports `EMLActivation`, `EMLLayer` (try/import, no mandatory torch)
- `monogate.__init__` exports all `complex_eval` symbols unconditionally (no torch dependency)

---

## [0.4.0] — 2026-04-15

### Added

- `monogate.search.mcts_search` — MCTS over EML grammar (initial version)
- `monogate.search.beam_search` — beam search over EML grammar
- `experiments/sin_search_03.py` — N=9 exhaustive search (parity pruning, parallel)
- `experiments/gen_attractor_data.py` — 40-seed attractor trajectory generator
- Explorer: Attractor Lab tab (`AttractorViz.jsx`) with animated convergence
- Explorer: offline JS optimizer enhancements (`opt-engine.js` — PyTorch/NumPy patterns)
- Explorer: BEST toggle, node breakdown table, copyable snippet in `OptimizeTab.jsx`

### Changed

- `monogate.__version__`: `0.3.3` → `0.4.0`
- `explorer/package.json`: `0.1.0` → `0.2.0`

---

## [0.3.3] — 2026-04-10

### Fixed

- `best_optimize` BEST operations now return `float` instead of `complex` (#bug)
- Fixed phantom attractor test: expected value corrected for `softplus` right-child transformation

---

## [0.3.1] — 2026-04-05

### Added

- NeRF optimizer (`optimize_nerf`)
- SIREN tab in explorer
- Research scripts (attractor analysis, operator zoo)
- PyPI release

---

## [0.2.0] — 2026-03-20

### Added

- `monogate.network`: `EMLNetwork`, `HybridNetwork`, `EMLTree`, `fit()`
- `monogate.torch_ops`: differentiable tensor operations
- Explorer: BEST tab, SIREN tab
- `monogate.optimize`: `best_optimize`, `OptimizeResult`, `BestRewriter`
- Challenge board (`challenge/`)

---

## [0.1.0] — 2026-03-01

### Added

- Initial release
- `monogate.core`: EML operator, EML/EDL/EXL/EAL/EMN families, BEST routing
- `monogate.operators`: operator registry, comparison table
- JavaScript package (`lib/`)
- Interactive explorer (`explorer/`) — basic viz, sin tab, calculator
