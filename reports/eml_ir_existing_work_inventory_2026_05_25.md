# EML Substrate Existing Work Inventory

Date: 2026-05-25

Status: `EXISTING_WORK_INVENTORY_COMPLETE`

This inventory was created before adding EML IR v0 so the implementation does not duplicate prior work.

## Reusable Existing Pieces

- `python/scripts/superbest_dag_lowering.py`
  Existing compiler-style expression lowering pass. It parses expressions, emits shared temporaries, and reports Tree SuperBEST vs DAG SuperBEST costs.

- `python/scripts/superbest_expression_frontier.py`
  Existing frontier case set for softmax, sigmoid, rational denominator, and polynomial basis reuse.

- `monogate-research/rfcs/eml_kernel_contract_v0`
  Existing kernel contract RFC and schema for EML kernel sidecars.

- `monogate-research/exploration/C266_eml_transpiler`
  Existing string-input EML transpiler prototype for Python, NumPy, and SymPy.

- `eml-cost/src/eml_cost/transpile.py`
  Existing SymPy-tree transpiler with executable source and verification snippets.

- `monogate-engine/docs/book/src/architecture-eml.md`
  Existing engine-side description of EML kernels as a source language for WGSL/Rust/proof obligations.

- `monogate-research/exploration/monogate_os_replay_frame_runtime_v0_2026_05_24`
  Existing replay frame runtime prototype.

## Gap Found

The missing piece was not another substrate essay. The missing executable bridge was:

```text
expression -> EML IR DAG -> SuperBEST Tree/DAG cost -> replay packet
```

That bridge now lives in `python/scripts/eml_ir_pipeline.py`.

## Boundary

This inventory and the EML IR v0 pass do not change Forge behavior, do not change canonical SuperBEST row costs, do not publish packages, and do not make public theorem/proof/open-problem claims.
