# SuperBEST DAG Lowering Pass

Date: 2026-05-24

Status: `SUPERBEST_DAG_LOWERING_PASS_READY`

This is the first compiler-style lowering pass for expression-level SuperBEST DAG sharing. It emits dependency-ordered temporaries before reporting DAG costs or exporting code.

## Summary

- Cases lowered: 9
- Best case: `attention_three_logits_three_outputs`
- Max extra SuperBEST DAG savings: 26 nodes

## Ranked Lowerings

| Rank | Case | Temps | Tree BEST | DAG BEST | Extra DAG Savings |
|---:|---|---:|---:|---:|---:|
| 1 | `attention_three_logits_three_outputs` | 8 | 46 | 20 | 26 |
| 2 | `attention_three_logits_two_outputs` | 8 | 30 | 16 | 14 |
| 3 | `sigmoid_value_and_derivative` | 4 | 26 | 12 | 14 |
| 4 | `attention_two_logits_two_outputs` | 5 | 22 | 12 | 10 |
| 5 | `logistic_loss_pair` | 4 | 21 | 11 | 10 |
| 6 | `rational_shifted_basis` | 1 | 22 | 14 | 8 |
| 7 | `rational_three_terms_shared_den` | 1 | 22 | 16 | 6 |
| 8 | `polynomial_basis_degree5` | 2 | 16 | 10 | 6 |
| 9 | `poly_features_shared_square_cube` | 2 | 14 | 10 | 4 |

## Best Lowered Python Sketch

```python
from monogate import BEST

def lowered_expr(k1, k2, k3, q):
    """SuperBEST DAG-lowered expression; shared temporaries first."""
    _t5 = (k1 * q)
    _t6 = (k2 * q)
    _t7 = (k3 * q)
    _t2 = BEST.exp(_t5)
    _t3 = BEST.exp(_t6)
    _t4 = BEST.exp(_t7)
    _t1 = (_t2 + _t3)
    _t0 = (_t1 + _t4)
    return ((BEST.div(_t2, _t0) + BEST.div(_t3, _t0)) + BEST.div(_t4, _t0))
```

## Boundary

- Expression-level lowering only.
- No canonical row costs changed.
- No new row optimality claim.
- No package publish or deploy.
