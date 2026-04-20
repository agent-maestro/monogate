# Changelog

All notable changes to the monogate project.

## [v4.6.0] — 2026-04-20

### New Theorems (T26–T28)
- **T26**: Forward direction — exp(+x) operators are exactly complete
- **T27**: Reverse direction — exp(−x) operators are incomplete (5 mechanisms: slope barrier, domain failure, domain collapse, dead constant, decay barrier)
- **T28**: LEX domain incompleteness — domain shrinks to ∅ under self-composition despite exp(+x)
- **T12 updated**: Completeness Trichotomy → Exponential Position Theorem (8/1/7 split)
- **T19**: Softplus = 1 LEAd node (ln(1+exp(x)) = LEAd(x,1))

### Completeness Census Complete
- 8 exactly complete operators: EML, EAL, EXL, EDL, EPL, LEAd, ELAd, ELSb
- 1 approximately complete: EMN
- 7 incomplete: DEML, DEMN, DEAL, DEXL, DEDL, DEPL, LEX
- Structural rule: exp(+x) without domain restriction ↔ exactly complete

### Theorem Catalog
- Expanded to T01–T28 (was T01–T07 in public catalog)
- All T08–T28 now in `challenge/app/theorems/page.tsx`
- New proof document: `python/paper/theorems/Sixteen_Operator_Census.tex`

### Blog
- New post: `completeness-characterization.md` — "Why exp(+x) Means Complete"
- `completeness-trichotomy.md` updated with forward reference to new result
- Post count: 30 (was 29)

### Infrastructure
- Site consistency audit: stale theorem counts updated (T01–T25 → T01–T28, 25→28)
- `challenge.monogate.dev` domain references fixed to `monogate.dev`
- README BEST routing table updated to SuperBEST FINAL (71.2%, was 52%)
- Mobile fix: one-operator page responsive h1 + flex-wrap cards

### Tests
- 1694 passing, 9 skipped

---

## [v4.5.0] — 2026-04-20

### SuperBEST FINAL Table
- **neg(x) = 2 nodes** via `exl(0, deml(x, 1))` for x > 0 (was 6n)
- **mul(x,y) = 3 nodes** via EXL (was 7n)
- **sub(x,y) = 3 nodes** via EML (was 5n)
- **add(x,y) = 3 nodes** via EAL for x > 0 (was 11n)
- Total: **21n vs 73n naive = 71.2% savings**, all proved optimal by exhaustive search

### Explorer (`monogate.dev/explorer`)
- **superbest.js** — browser-only engine: `TABLE`, `COSTS`, `EML_COSTS`, `FAMILY`, `exportCode()`, `runBenchmarks()`
- **BenchmarkTab** — 9th tab, 25 preset expressions, instant JS computation, CSV export
- **ExprTreeTab** — Optimize button, export-as-code (Python/JS/GLSL/HLSL/Rust/C), shareable URLs (`?tab=tree&expr=...`)
- **BestCalc** — updated 52% → 71.2% description
- **Tab count** — exactly 9: calc, verify, table, tree, best, sandbox, deml, attractor, benchmarks
- Removed `opt` tab (functionality absorbed into tree tab)
- `calc-engine.js` / `opt-engine.js` — SuperBEST FINAL costs updated

### Blog (`monogate.org/blog`)
- Fixed `eml-chaos.astro` — rewritten with proper Astro component syntax (was broken)
- Converted 12 blog posts from broken markdown-layout `.astro` → `.md`
- **13 new posts published:**
  - `geometry-costs` — 12 geometric primitives, 126n SuperBEST vs 345n naive, 63% savings
  - `eml-chaos` — strange attractors, bifurcation, Lyapunov landscape
  - `completeness-trichotomy` — EML/EMN/others: three completeness classes
  - `eml-negation` — negation in 2 nodes
  - `mul-gap-closed` — multiplication in 3 nodes
  - `eml-no-fixed-points` — EML self-map has no fixed points
  - `tight-zeros-bound` — 2^n − 1 zeros bound, tight
  - `pumping-lemma` — EML pumping lemma
  - `operator-zoo` — completeness classification of all 6 EML-family operators
  - `superbest-complete` — SuperBEST FINAL table, all entries optimal
  - `fourier-beats-taylor` — 100× node savings via Euler gateway
  - `eml-sound` — Timbre = EML node count
  - `eml-fractals` — EML Mandelbrot correspondence

### Theorem Catalog (`monogate.org/theorems`)
- Expanded from **7 → 25 theorems** (T01–T25)
- New: T08–T25 covering SuperBEST optimality, negation/mul/sub proofs, completeness trichotomy, geometry catalog, chaos results, Fourier dominance, i-constructibility impossibility
- Updated proposition list: P01–P06

### Navigation / URLs
- **`/play` → `/lab`** across all properties
  - `challenge/next.config.mjs`: redirect `/play` → `/lab`, rewrite `/lab` → games backend
  - Challenge app nav labels updated: "Play" → "Lab"
  - `LandingPage.jsx`: `games.monogate.dev` → `monogate.dev/lab`
- **Landing page**: theorem count 18 → 25
- **`what-best-routing-saves.astro`**: node count table updated, benchmarks link corrected

### Research Documentation
- `preprint_addendum_emn_mul_math.tex` — added:
  - Theorem neg2n (negation in 2 nodes)
  - SuperBEST FINAL remark (71.2% savings, all optimal)
  - Geometry Catalog section (Table~\ref{tab:geometry}, GEO-G1..G10)
- Fixed stale numbers: 65.8% → 71.2%, neg 6n → 2n

### Lab (`monogate.dev/lab`)
- `eml-synthesizer.jsx` — Auto-BEST toggle: shows SuperBEST node count vs naive (245× savings for harmonics)

---

## [v4.2.0] — 2026-04-19

- Challenge board: split Open/Resolved, proof boxes, hide submit form for closed challenges
- `/explorer` rewrite fixed (was looping to www)
- `/play` moved to `monogate.dev/play` via rewrite proxy
- Two-domain restructure: `monogate.dev` (tools) + `monogate.org` (research blog)
- Grounding sprint: one-operator page, blog index, private audit post

---

## [v0.2.0] — 2026-03-xx (PyPI)

- `pip install monogate` — Python library
- `EMLLayer`, `FusedEMLActivation`, `beam_search`, `mcts_search`
- SuperBEST routing: `BEST` mode dispatches each op to cheapest operator
- Rust kernel via PyO3 (`monogate-core/`)
- 1700+ tests

---

## [v0.1.0] — 2026-02-xx

- Initial release
- EML operator: `eml(x,y) = exp(x) - ln(y)`
- Paper: arXiv:2603.21852 (Odrzywołek 2026)
