# SuperBEST DAG Savings Audit

Date: 2026-05-24

Status: `SUPERBEST_DAG_SAVINGS_AUDIT_COMPLETE`

This audit looks for expression-level savings from common-subexpression sharing. It does not change the canonical row-level SuperBEST table.

## Summary

- Cases audited: 8
- Max extra SuperBEST DAG savings: 9 nodes
- Average extra SuperBEST DAG savings: 3.75 nodes
- Best case: `softmax_three_terms`

## Results

| Case | Family | Tree BEST | DAG BEST | Extra DAG Savings | Tree EML | DAG BEST vs Tree EML |
|---|---:|---:|---:|---:|---:|---:|
| repeat_exp_pair | repeated_exp | 4 | 3 | 1 | 13 | 76.9% |
| shared_exp_ln_square | shared_subexpression | 9 | 5 | 4 | 43 | 88.4% |
| sigmoid_reuse | activation | 19 | 11 | 8 | 93 | 88.2% |
| softmax_three_terms | softmax | 22 | 13 | 9 | 93 | 86.0% |
| rational_repeated_denominator | rational | 13 | 11 | 2 | 75 | 85.3% |
| polynomial_repeated_square | polynomial | 9 | 7 | 2 | 87 | 92.0% |
| gelu_inner_sketch | activation | 16 | 16 | 0 | 109 | 85.3% |
| log_ratio_shared_shift | log_rational | 13 | 9 | 4 | 77 | 88.3% |

## Interpretation

The next practical savings likely come from DAG-aware expression optimization, not from changing the saturated row table. Repeated denominators, repeated `exp` terms, and reused polynomial powers are the cleanest targets.

## Boundaries

- No canonical row cost changed.
- No new row optimality claim is made.
- No public theorem/proof/open-problem claim is made.
- `sin`, `cos`, and activation sketches remain internal/demo rows unless separately reviewed.
