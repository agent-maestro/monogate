# EML-L2 Canonical Operator Tree Lab

Date: 2026-05-27
Status: `EML_CANONICAL_OPERATOR_TREE_CANDIDATE_PASS`
Visibility: internal candidate

## Scope

EML-L2 extends the language kernel with structural operator-tree views:

- surface AST: what the user wrote
- expanded AST: EML/softplus lowered into the existing expression vocabulary
- canonical AST: stable structural form with commutative add/mul sorting
- canonical hash: deterministic fingerprint over the canonical AST
- expansion tags: `eml` and `softplus` expansion markers

This is structural normalization only. It is not a semantic proof and does not
change compiler lowering.

## Generated Artifacts

- `python/results/eml_language_kernel/*_language_2026_05_27.json`
- `python/results/eml_language_kernel/eml_language_canonical_comparisons_2026_05_27.json`
- `reports/eml_language_kernel/eml_language_canonical_comparisons_2026_05_27.md`

## Canonical Comparisons

The generated comparison artifact checks five structural equivalences:

- `eml(x, y)` and `exp(x) - ln(y)`
- `softplus(x)` and `ln(1 + exp(x))`
- `eml(x, softplus(y))` and `exp(x) - ln(ln(1 + exp(y)))`
- `exp(a) + exp(b)` and `exp(b) + exp(a)`
- `x * y` and `y * x`

All five match by canonical hash.

## Boundary

- Canonical matching is structural normalization, not proof.
- No semantic equivalence theorem is claimed.
- No Forge/compiler behavior change.
- No public savings claim.
- No package publish or deploy.

## Validation

- `python python/scripts/eml_language_kernel.py --build-fixtures --strict`
- `python -m pytest -q python/tests/test_eml_language_kernel.py`

