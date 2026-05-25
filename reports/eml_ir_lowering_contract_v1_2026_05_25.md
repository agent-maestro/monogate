# EML IR Lowering Contract v1 Report

Date: 2026-05-25

Status: `INTERNAL_LOWERING_CONTRACT_V1_DRAFT`

## What Changed

The v1 lowering contract now names the shared boundary between the new Explorer IR beta, the complex field view, SuperBEST DAG experiments, and future Forge lowering work.

Artifacts:

- `docs/eml_ir_lowering_contract_v1_2026_05_25.md`
- `schemas/eml_ir_lowering_contract_v1.json`

## Key Decisions

- Stable node IDs use topological order.
- Structural reuse is based on normalized operation shape.
- `add` and `mul` should canonicalize child order for DAG reuse.
- Tree SuperBEST remains the public-safe headline cost.
- DAG SuperBEST remains internal until lowering semantics are reviewed.
- Field visualization is intuition-only and cannot validate lowering correctness.

## Boundary

No compiler behavior changed. No canonical SuperBEST row changed. No deploy, package publish, production marketplace update, safety certification, production-controller claim, hardware-backed evidence, or public theorem/proof/open-problem claim was made.
