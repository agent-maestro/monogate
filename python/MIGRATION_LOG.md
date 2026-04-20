# Migration Log

## 2026-04-19 — BEST dispatch table moved to private config

### What moved

The `_make_best()` routing table in `monogate/core.py` previously contained
a readable Python dict mapping each arithmetic operation to its optimal base
operator (EML, EDL, EXL, DEML). That table is a patent candidate: it encodes
which operator minimizes node count for each operation, derived from research
sessions that are not yet public.

The full dispatch table has been moved out of `core.py` and into:

| File | Status | Purpose |
|------|--------|---------|
| `monogate/_routing_private.py` | **private** (gitignored) | Authoritative source — human-readable Python dict |
| `monogate/_routing.pkl` | **private** (gitignored) | Compiled binary built from `_routing_private.py` |
| `monogate/_routing_loader.py` | public | Loads routing from env var or binary at import time |
| `scripts/compile_routing.py` | public | Build script: private source → binary |

### How the public package loads routing

Priority order at `import monogate`:

1. **`MONOGATE_ROUTING` env var** — JSON string: `{"exp":"EML","ln":"EXL",...}`
2. **`monogate/_routing.pkl`** — compiled binary (present in PyPI wheels, absent from git)
3. **EML fallback** — `exp`, `ln`, `pow`, `mul`, `div`, `recip`, `neg`, `sub`, `add`
   all route to EML. Mathematically correct; not node-count optimal.

PyPI wheels include `_routing.pkl` via `pyproject.toml` package-data, so
`pip install monogate` gives the full optimized routing without any visible
source change.

### Tests changed

`tests/test_best_routing.py::TestRoutingTable` — removed the 9 per-operation
routing assertions (`assert BEST._routing["ln"] is EXL`, etc.). These assertions
encoded the private dispatch table in the public test suite. Replaced with
structural tests (all 9 ops present, repr, AttributeError on missing op).

All numerical accuracy tests are unchanged — they verify correctness of results,
not routing implementation.

### How to regenerate the binary after editing `_routing_private.py`

```bash
python scripts/compile_routing.py
```

Then rebuild the wheel before publishing to PyPI.

### Related audit

The `exp_neg → DEML` routing entry added in session R3 was **reverted** before
this migration (see git log). The pre-existing dispatch table entries (ln→EXL,
pow→EXL, mul→EDL, div→EDL, recip→EDL, neg→EDL) were already visible in the
public repo before this migration was applied — evaluate those separately if
needed. From this commit forward, no routing assignments appear in public source.
