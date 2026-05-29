# PCC-M6 Contract CI Guard

Date: 2026-05-29

Status: CI guard recorded.

PCC-M6 adds the proof-carrying artifact contract batch validator to the
existing EML Guard Contract GitHub workflow.

## Guarded Command

```bash
python python/scripts/proof_carrying_artifact_contract_validator.py --contracts-dir reports/proof_carrying_artifacts --strict
```

The workflow also runs the focused validator tests:

```bash
python/tests/test_proof_carrying_artifact_contract_validator.py
```

## Current Registry

- contracts: 3
- obligations: 36
- failed contracts: 0

## Boundary

- CI guard only.
- No Foundational PCC claim.
- No compiler correctness claim.
- No formal equivalence claim.
- No proof-strength claim.
- No public-readiness or production-readiness claim.
