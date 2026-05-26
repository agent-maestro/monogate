# EML IR v1 Replay Artifact

Date: 2026-05-26

Status: internal research artifact

## What Changed

`lib/src/ir.js` implements the first code-backed slice of the EML IR Lowering
Contract v1:

```text
expression -> normalized DAG nodes -> guarded replay frames
```

It exposes:

```js
import {
  normalizeDag,
  emitReplayPacket,
  validateReplayPacket,
} from "monogate/ir";
```

## Why It Matters

Before this artifact, the IR contract was prose. Now Monogate has a runnable
boundary object that can be shared by:

- Explorer visualizations;
- SuperBEST tree-vs-DAG experiments;
- future Forge lowering work;
- electronics-style replay evidence;
- future MachLib proof obligations.

This is deliberately not a public savings claim. The packet labels both
`tree_cost` and `dag_cost`, and the boundary flags mark:

```text
public_savings_claim: false
formal_verification_claim: false
compiler_release_claim: false
```

## Current Capabilities

- Parses existing `monogate/cost` expression strings.
- Assigns stable topological node IDs.
- Deduplicates structurally identical subexpressions.
- Canonicalizes `add` and `mul` child order for reuse accounting.
- Emits domain annotations for `ln`, `sqrt`, `div`, and `pow`.
- Emits lifecycle replay frames:

```text
INIT -> READY -> RUNNING -> END -> PARKED
```

- Hash-chains replay frames with stable local hashes.
- Validates replay lifecycle, hash chain, and RUNNING-frame annotations.

## Example

```js
const dag = normalizeDag("exp(x) + exp(x)");

dag.tree_cost; // 4
dag.dag_cost;  // 3
```

The repeated `exp(x)` subtree is one DAG node, but the artifact keeps the
tree-vs-DAG distinction explicit.

## Validation

```bash
cd lib
npm test
```

Current result:

```text
6 test files passed
434 tests passed
```

## Next Research Step

Connect this artifact to one visible Explorer panel:

```text
input expression -> DAG table -> replay packet -> field bridge
```

The important review gate is that Explorer must continue to describe the field
view as a visual intuition bridge, not a correctness validator.
