# EML-L1 Language Kernel

Date: 2026-05-27
Status: `EML_LANGUAGE_KERNEL_CANDIDATE_PASS`
Visibility: internal candidate

## Scope

EML-L1 introduces a minimal EML-native language kernel. It is a front door for
guarded operator trees, not a compiler behavior change.

The kernel parses:

- `program`
- `family`
- `meaning`
- `input`
- `let`
- `guard`
- `return`

It normalizes:

- `softplus(x)` to `ln(1 + exp(x))`
- `eml(x, y)` to `exp(x) - ln(y)`
- `let` bindings into the returned expression

## Generated Artifacts

- `docs/eml_language_kernel_v0.md`
- `schemas/eml_language_kernel_v0.json`
- `python/scripts/eml_language_kernel.py`
- `python/fixtures/eml_language_programs/*.eml`
- `python/results/eml_language_kernel/*_language_2026_05_27.json`
- `python/results/eml_language_packets/*_expression_packet_2026_05_27.json`
- `reports/eml_language_kernel/*_language_kernel_2026_05_27.md`

## Fixture Set

- `softplus_pair_v0`
- `sigmoid_derivative_v0`
- `gaussian_energy_v0`
- `raw_eml_primitive_v0`
- `guarded_eml_softplus_v0`

## Result

The first three fixtures preserve the existing program IDs and lower into EML
Expression Packet v0, so the current packet builder, domain safety lens, proof
registry, and Explorer can consume them.

## Boundary

- No Forge/compiler behavior change.
- No public savings claim.
- No complete EML language semantics claim.
- No formal verification or theorem claim.
- No package publish or deploy.

## Validation

- `python python/scripts/eml_language_kernel.py --build-fixtures --strict`
- `python -m pytest -q python/tests/test_eml_language_kernel.py`

