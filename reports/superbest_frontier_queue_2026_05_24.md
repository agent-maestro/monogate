# SuperBEST Frontier Queue

Date: 2026-05-24

Status: internal frontier queue ready.

This is a table-health and frontier-prioritization pass after the v5.3 surface reconciliation. It does not introduce new mathematical claims.

## Canonical State

- Canonical source: `python/monogate/superbest.py`
- Positive-domain headline: `14n / 80.8%` vs `73n` naive over the 10-op positive basket.
- General-domain headline: `16n / 74.2%` vs `62n` naive over the 8-op general basket.
- Drift guard command: `make superbest-check`

## Closed Or Stable Rows

- `exp`: stable primitive row.
- `ln`: stable positive-domain primitive with real-domain caveat.
- `neg`: stable 2n route.
- `add`: stable 2n route and strongest general-domain table highlight.
- `sub`: stable 2n route.
- `recip`: stable table row with strict real-domain caveat.
- `pow`: stable positive-base route; signed/general copy must keep caveat.
- `sqrt`: stable positive-domain route; not an all-real function.

## Ranked Frontier Queue

1. DAG/common-subexpression optimizer.
   The row table is close to saturated, but expression-level sharing produced extra savings in the DAG audit. Next action: prototype an optimizer that emits shared temporaries and compares tree versus DAG costs.

2. `div` accounting note.
   The table drift came partly from 1n shortcut language versus 2n full-tree accounting. Next action: create a row-level note that makes the full-tree policy explicit everywhere.

3. `mul` positive/general distinction.
   Positive `1n` and general `3n` are both useful, but browser and copy surfaces must never blur them into all-real 1n multiplication.

4. Browser code export caveat.
   The explorer cost tables are synced, but generated snippets are best treated as construction sketches unless upgraded to canonical examples.

5. `sin` / `cos` demo rows.
   Keep approximation/demo rows separate from the 10-op arithmetic headline. These rows are useful for demos, but they are not part of the canonical arithmetic-basket headline.

6. New frontier search.
   Defer new search until the drift check is adopted in CI/review practice. Once stable, search only rows with explicit open/domain-caveat status.

## Public-Safe Claims

- Positive 10-op headline: `14n / 80.8%`.
- General 8-op headline: `16n / 74.2%`.
- `mul`: positive `1n`, general `3n`, with domain separation.
- `div`: positive full tree `2n`, general `3n`, with accounting separation.

## Internal-Only Items

- Browser code export as proof evidence.
- Approximation rows for `sin` and `cos`.
- Any new row optimality search results until separately reviewed.
- Any statement that removes domain caveats from `ln`, `recip`, `pow`, `sqrt`, `mul`, or `div`.

## Next Development Step

Wire `make superbest-check` into the review habit first. After that, a focused browser cleanup should label construction snippets clearly and separate arithmetic-basket rows from approximation/demo rows.
