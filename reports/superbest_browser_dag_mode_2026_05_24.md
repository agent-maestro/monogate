# SuperBEST Browser DAG Mode

Date: 2026-05-24

Status: `EXPLORER_DAG_MODE_READY`

## What Changed

The Explorer benchmark tab now has two modes:

- `Tree SuperBEST`: the canonical row-cost view.
- `DAG SuperBEST`: an expression-level prototype view that highlights shared subexpressions.

The DAG view is intentionally narrow. It shows common-subexpression reuse on a fixed internal case set and does not change canonical SuperBEST row costs.

## Reviewer Notes

- Shared nodes are shown as blue chips in the benchmark table.
- `div_positive = 2n` remains the full positive-domain tree route.
- `mul_positive = 1n` remains positive-domain only.
- General-domain caveats remain visible in the methodology text.

## Boundary

- No canonical row table change.
- No new row optimality claim.
- No public theorem/proof/open-problem claim.
- No deploy or package publish.
