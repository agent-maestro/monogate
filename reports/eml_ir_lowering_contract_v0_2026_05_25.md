# EML IR Lowering Contract v0 Report

Date: 2026-05-25

Status: `INTERNAL_LOWERING_CONTRACT_DRAFT`

## Result

The EML IR lowering contract now exists as both a human-readable
contract and a JSON schema:

- `docs/eml_ir_lowering_contract_v0_2026_05_25.md`
- `schemas/eml_ir_lowering_contract_v0.json`

The contract names the v0 primitive set, deterministic DAG node
ordering, Tree-vs-DAG semantics, replay lifecycle, validity gates, and
public-copy boundary.

## Why It Matters

The EML IR Inspector makes the artifact visible. The lowering contract
makes it harder for the artifact to drift into an unreviewed compiler or
public-savings claim.

## Boundary

- Internal draft only.
- No compiler behavior changed.
- No canonical SuperBEST row table changed.
- No package publish.
- No deploy.
- No production marketplace modification.
- No public theorem/proof/open-problem claim.
