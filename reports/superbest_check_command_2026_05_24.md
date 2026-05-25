# SuperBEST Check Command

Date: 2026-05-24

The repo now has a single SuperBEST drift check:

```bash
make superbest-check
```

It runs:

1. `python python/scripts/sync_superbest_canonical.py --strict`
2. focused SuperBEST and CapCard regression tests
3. `npm ci && npm run build` inside `explorer/`

This is the preferred validation path after any change to:

- `python/monogate/superbest.py`
- `blog/src/data/superbest.json`
- `python/results/superbest_v5_table.json`
- capability-card JSON surfaces
- Explorer SuperBEST cost tables or copy

## Explorer Build Environment

The previous blocker was `vite: not found`. The Explorer has a dedicated lockfile, so the reproducible local fix is:

```bash
cd explorer
npm ci
npm run build
```

or from the repo root:

```bash
make explorer-build
```

## Boundary

This check does not publish packages, deploy the Explorer, update a marketplace, or introduce new public claims.
