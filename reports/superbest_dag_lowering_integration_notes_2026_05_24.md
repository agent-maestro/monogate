# SuperBEST DAG Lowering Integration Notes

Date: 2026-05-24

Status: `INTERNAL_INTEGRATION_NOTES_READY`

## What Now Exists

`python/scripts/superbest_dag_lowering.py` is the first compiler-style lowering pass for expression-level SuperBEST DAG savings. It parses expressions, identifies repeated subexpressions, emits dependency-ordered temporaries, reports Tree SuperBEST versus DAG SuperBEST costs, and exports Python/JavaScript sketches.

## Integration Target

The next code path should place DAG lowering before:

- cost reporting;
- code export;
- Explorer DAG display;
- future compiler/lowering integrations.

The canonical row table should stay unchanged. DAG lowering is a graph optimization over expressions, not a new primitive-row claim.

## Boundary

- Expression-level only.
- No canonical row costs changed.
- No new row optimality claim.
- No package publish.
- No deploy.
