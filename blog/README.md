# monogate.org

Astro static site for monogate.org — research blog, theorem catalog, EML atlas, SuperBEST
routing table. Deployed to Cloudflare Pages (project `monogate-org`).

## Data flow — generated views, never hand-authored claims

`/theorems`, `/atlas`, and `/superbest` render directly from JSON in `src/data/` at build
time. There is no second, hand-typed copy of these facts anywhere in the `.astro` files —
that was the actual bug behind the 2026-07-22/23 audits (numbers and citations drifted
between pages, and between the pages and the actual Lean/Python sources, because there
was nowhere for them to disagree loudly).

| File | Feeds | Canonical for |
|---|---|---|
| `src/data/theorems.json` | `/theorems` | Every result in the catalog (theorems, propositions, conjectures, observations, definitions, speculation). |
| `src/data/atlas.json` | `/atlas` | Depth strata, 16-operator census, special-function depths, calculus costs, domain-catalog highlights, cost-theory tables. |
| `src/data/pfaffian-towers.json` | `/atlas` **and** `/superbest` | The 8 Pfaffian tower generators — one file, read by both pages, on purpose (see below). |
| `src/data/superbest.json` | `/superbest`, and joined into `/atlas`'s mini-table | Per-op SuperBEST node costs. Synced against `monogate/python/monogate/superbest.py` (a *different* repo) via `tools/superbest_canonical_audit.py` in `monogate-research` — see that repo for the regression guard on this specific file. |

**`/atlas`'s own SuperBEST mini-table does not store node counts.** `superbestDisplay` in
`atlas.json` only carries presentation metadata (operator family name, naive cost, a short
note) keyed by `op_key`; `atlas.astro` joins that against `superbest.json`'s `cost_positive`
at build time. If `superbest.json` changes, `/atlas` picks it up automatically — there's
nothing to keep in sync by hand.

**Why `pfaffian-towers.json` is shared, not duplicated:** it used to be two independent
copies (`atlas.astro`'s own array, and `superbest.json`'s `pfaffian_towers` key). They'd
each drifted from the actual verification source
(`monogate-research/exploration/E201_extended_atlas/`) and from each other — one said 42
total functions, the other said 33, the source said 35. Reconciled 2026-07-23. The old key
in `superbest.json` is left in place but unused (nothing else reads it) rather than deleted,
since deleting fields from a file another repo's tooling also touches is a bigger, separate
decision.

## Adding or correcting a result

Edit the relevant JSON file directly. Do not edit the numbers/prose inside the `.astro`
files — they're pure templates now and have no facts to edit.

- New theorem/proposition/conjecture/observation: add an entry to `src/data/theorems.json`'s
  `results` array. `id` must be unique; if you cite a Lean proof, `lean.file` and
  `lean.theorem` must actually exist in `monogate-lean/MonogateEML/` (the audit script
  checks this — see below).
- New atlas row: edit the relevant array in `src/data/atlas.json`. If it cites a `/theorems`
  id in its `proof`/`note` field, that id must exist (or be added to the
  `EXTERNAL_REF_ALLOWLIST` in `scripts/audit-citations.mjs`, with a one-line reason, if it's
  a legitimate pre-catalog reference that was never meant to become its own entry).

## Before every deploy

```sh
npm run audit    # cross-repo citation check (needs monogate-lean checked out as a sibling repo)
npm run build    # also re-checks referential integrity for theorems.json/atlas.json at build time
npm run predeploy  # both, in order — exits non-zero if either fails
```

`npm run audit` (`scripts/audit-citations.mjs`) checks what the Astro build alone can't,
because it reads files outside this repo:

1. Every `theorems.json` `deps`/`resolvedBy` id resolves (also checked at build time, in
   `theorems.astro`'s frontmatter — the build already fails loudly on this one, `npm run
   audit` re-checks it as belt-and-suspenders).
2. Every `theorems.json` Lean citation's file exists in `monogate-lean/MonogateEML/` **and**
   actually declares a `theorem`/`lemma` with the cited name. This is the check that would
   have caught T09's badge citing a file that was added, reverted, and never came back —
   found by running this exact script for the first time, 2026-07-23.
3. Every `atlas.json` citation that looks like a catalog id (`T\d+`, `O-\w+`, `ADD-T\d+`,
   etc.) resolves to a real `theorems.json` entry or the documented allowlist.
4. `atlas.json`'s `superbestDisplay` join against `superbest.json` resolves (also checked at
   build time in `atlas.astro`).
5. `pfaffian-towers.json`'s per-tower counts sum to its own `function_total`.

Set `MONOGATE_LEAN_PATH` if `monogate-lean` isn't checked out as a sibling of this repo's
parent directory (default: `../../monogate-lean` relative to `blog/`).

Exit code 0 = clean. This is not wired into CI (this repo has none — deploys are manual,
`wrangler pages deploy dist --project-name monogate-org --branch main`, from a box with
`monogate-lean` and this repo checked out side by side) — running `npm run predeploy` by
hand before every deploy is the actual enforcement mechanism right now. A real CI job that
runs this on every push would close that gap; not built yet.

## Commands

| Command | Action |
|---|---|
| `npm install` | Install dependencies |
| `npm run dev` | Local dev server at `localhost:4321` |
| `npm run build` | Build to `./dist/` (also runs the in-page referential-integrity checks) |
| `npm run audit` | Cross-repo citation check (`scripts/audit-citations.mjs`) |
| `npm run predeploy` | Both of the above, in order |
| `npm run preview` | Preview the build locally |

Deploy: `export NVM_DIR="$HOME/.nvm" && . "$NVM_DIR/nvm.sh" && nvm use 22` first — this box's
default shell `node` is too old for `wrangler`. Then `npx wrangler pages deploy dist
--project-name monogate-org --branch main --commit-dirty=true`.
