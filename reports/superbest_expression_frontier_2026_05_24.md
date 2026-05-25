# SuperBEST Expression Frontier

Date: 2026-05-24

Status: `SUPERBEST_EXPRESSION_FRONTIER_COMPLETE`

This is an expression-level DAG savings exploration. It does not change canonical SuperBEST row costs.

## Headline

- Cases explored: 9
- Best case: `attention_three_logits_three_outputs`
- Max extra DAG savings over Tree SuperBEST: 26 nodes
- Best DAG-vs-tree-EML savings: 93.4%

## Family Summary

| Family | Best Case | Max Extra DAG Savings | Note |
|---|---|---:|---|
| polynomial_basis_reuse | `polynomial_basis_degree5` | 6 | Useful compiler-lowering target for x^2/x^3 style basis reuse. |
| rational_shared_denominator | `rational_shifted_basis` | 8 | Good frontier for repeated denominators; savings are smaller than softmax but common in real formulas. |
| sigmoid_logistic | `sigmoid_value_and_derivative` | 14 | Strong frontier when the sigmoid value, exp(-x), or 1+exp(-x) is consumed more than once. |
| softmax_attention | `attention_three_logits_three_outputs` | 26 | Highest-value frontier. Repeated exp(logit) and normalizer reuse compound quickly as outputs increase. |

## Ranked Cases

| Rank | Case | Family | Tree BEST | DAG BEST | Extra DAG Savings | DAG vs Tree EML |
|---:|---|---|---:|---:|---:|---:|
| 1 | `attention_three_logits_three_outputs` | softmax_attention | 46 | 20 | 26 | 93.4% |
| 2 | `attention_three_logits_two_outputs` | softmax_attention | 30 | 16 | 14 | 91.9% |
| 3 | `sigmoid_value_and_derivative` | sigmoid_logistic | 26 | 12 | 14 | 91.2% |
| 4 | `attention_two_logits_two_outputs` | softmax_attention | 22 | 12 | 10 | 91.8% |
| 5 | `logistic_loss_pair` | sigmoid_logistic | 21 | 11 | 10 | 90.8% |
| 6 | `rational_shifted_basis` | rational_shared_denominator | 22 | 14 | 8 | 88.9% |
| 7 | `rational_three_terms_shared_den` | rational_shared_denominator | 22 | 16 | 6 | 86.0% |
| 8 | `polynomial_basis_degree5` | polynomial_basis_reuse | 16 | 10 | 6 | 93.9% |
| 9 | `poly_features_shared_square_cube` | polynomial_basis_reuse | 14 | 10 | 4 | 92.7% |

## Compiler Integration Finding

The strongest next savings path is a DAG lowering pass before cost reporting and code export. The pass should identify common subexpressions, emit shared temporaries, and then compute SuperBEST costs on the shared graph.

## Boundary

- Expression-level sharing only.
- No canonical row table changed.
- No new row optimality claim.
- No public theorem/proof/open-problem claim.
