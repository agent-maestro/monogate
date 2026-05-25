# SuperBEST DAG Optimizer Prototype

Date: 2026-05-24

Status: `SUPERBEST_DAG_OPTIMIZER_PROTOTYPE_READY`

This prototype emits shared temporaries for repeated subexpressions. It is an expression-level optimizer sketch, not a row-level SuperBEST table change.

## Summary

- Cases optimized: 8
- Best case: `softmax_three_terms`
- Max extra SuperBEST DAG savings: 9 nodes

## Cases

| Case | Tree BEST | DAG BEST | Extra DAG Savings | Shared Nodes |
|---|---:|---:|---:|---:|
| repeat_exp_pair | 4 | 3 | 1 | 1 |
| shared_exp_ln_square | 9 | 5 | 4 | 3 |
| sigmoid_reuse | 19 | 11 | 8 | 3 |
| softmax_three_terms | 22 | 13 | 9 | 5 |
| rational_repeated_denominator | 13 | 11 | 2 | 1 |
| polynomial_repeated_square | 9 | 7 | 2 | 1 |
| gelu_inner_sketch | 16 | 16 | 0 | 0 |
| log_ratio_shared_shift | 13 | 9 | 4 | 1 |

## Example Snippet

```python
from monogate import BEST

def optimized_expr(x):
    """DAG-aware SuperBEST sketch; expression-level sharing only."""
    _t0 = BEST.exp(x)  # shared exp, reused 2x
    return (_t0 + _t0)
```

## Boundaries

- Expression-level sharing only.
- No canonical row costs changed.
- No new row optimality claim.
- No public theorem/proof/open-problem claim.
