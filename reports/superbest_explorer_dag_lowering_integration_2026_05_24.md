# SuperBEST Explorer DAG Lowering Integration

Date: 2026-05-24

Status: `LOCAL_EXPLORER_DAG_LOWERING_INTEGRATED`

## Summary

The Explorer now includes a DAG lowering playground inside DAG SuperBEST mode. It lets reviewers paste or select known expression fixtures, inspect shared temporaries, compare Tree BEST vs DAG BEST node counts, and export lowered Python or JavaScript code.

The browser implementation is intentionally fixture-backed. Arbitrary expression parsing remains in the Python CLI:

```bash
PYTHONPATH=python python python/scripts/superbest_dag_lowering.py "<expr>"
```

## Included Fixtures

- `3-logit attention softmax`: 46n Tree BEST to 20n DAG BEST, 26 extra nodes saved.
- `sigmoid value + derivative`: 26n Tree BEST to 12n DAG BEST, 14 extra nodes saved.
- `exp(x) + exp(x)`: 4n Tree BEST to 3n DAG BEST, 1 extra node saved.
- `single softmax term`: 10n Tree BEST to 9n DAG BEST, 1 extra node saved.

## Boundary

- Canonical row costs did not change.
- This is expression-level DAG sharing only.
- This is not a new primitive optimality claim.
- No deploy, package publish, marketplace modification, token handling, hardware action, PETAL/API upload, or Hugging Face upload was performed.
