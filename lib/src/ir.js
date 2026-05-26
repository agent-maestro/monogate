/**
 * monogate/ir — EML IR v1 normalization and replay packets.
 *
 * Research infrastructure for the EML IR Lowering Contract v1:
 * expression -> normalized DAG nodes -> guarded replay frames.
 *
 * This is not a compiler release, formal verification result, or public
 * SuperBEST savings claim.
 */

import { parse } from "./cost.js";

const SCHEMA = "monogate.eml_ir.v1";
const REPLAY_SCHEMA = "monogate.eml_ir.replay.v1";

const COMMUTATIVE = new Set(["add", "mul"]);
const PRIMITIVES = new Set([
  "input", "constant", "neg", "add", "sub", "mul", "div", "pow",
  "exp", "ln", "sqrt", "sin", "cos", "tanh",
]);

const TREE_COST = {
  input: 0,
  constant: 0,
  neg: 2,
  add: 2,
  sub: 2,
  mul: 2,
  div: 2,
  pow: 3,
  exp: 1,
  ln: 1,
  sqrt: 3,
  sin: 1,
  cos: 1,
  tanh: 1,
};

function stableStringify(value) {
  if (value === null || typeof value !== "object") return JSON.stringify(value);
  if (Array.isArray(value)) return `[${value.map(stableStringify).join(",")}]`;
  return `{${Object.keys(value).sort().map((key) => `${JSON.stringify(key)}:${stableStringify(value[key])}`).join(",")}}`;
}

function stableHash(value) {
  const text = typeof value === "string" ? value : stableStringify(value);
  let hash = 0xcbf29ce484222325n;
  const prime = 0x100000001b3n;
  for (let i = 0; i < text.length; i += 1) {
    hash ^= BigInt(text.charCodeAt(i));
    hash = BigInt.asUintN(64, hash * prime);
  }
  return `fnv1a64:${hash.toString(16).padStart(16, "0")}`;
}

function normalizeLiteral(value) {
  return Object.is(value, -0) ? 0 : value;
}

function opKind(node) {
  if (node.type === "num") return "constant";
  if (node.type === "sym") return "input";
  if (node.type === "log") return "ln";
  if (node.type === "pow" && node.exponent?.type === "num" && node.exponent.value === 0.5) return "sqrt";
  return node.type;
}

function childrenOf(node, kind) {
  if (kind === "constant" || kind === "input") return [];
  if (kind === "sqrt") return [node.base];
  if (node.arg) return [node.arg];
  if (node.args) return node.args;
  if (node.base) return [node.base, node.exponent];
  return [];
}

function literalOf(node, kind) {
  if (kind === "constant") return normalizeLiteral(node.value);
  if (kind === "input") return node.name;
  return null;
}

function domainAnnotations(kind, argIds) {
  if (kind === "ln") {
    return [{ kind: "requires_positive", arg: argIds[0], reason: "ln argument must be positive" }];
  }
  if (kind === "sqrt") {
    return [{ kind: "requires_nonnegative", arg: argIds[0], reason: "sqrt argument must be nonnegative" }];
  }
  if (kind === "div") {
    return [{ kind: "requires_nonzero", arg: argIds[1], reason: "division denominator must be nonzero" }];
  }
  if (kind === "pow") {
    return [{ kind: "domain_sensitive", args: argIds, reason: "pow domain depends on base and exponent" }];
  }
  return [];
}

function assertPrimitive(kind) {
  if (!PRIMITIVES.has(kind)) throw new Error(`Unsupported EML IR v1 primitive '${kind}'`);
}

function totalTreeCost(node) {
  const kind = opKind(node);
  assertPrimitive(kind);
  return TREE_COST[kind] + childrenOf(node, kind).reduce((sum, child) => sum + totalTreeCost(child), 0);
}

/**
 * Normalize a parseable expression or expression tree into shared DAG nodes.
 *
 * Node IDs are assigned in topological order. Structurally identical subtrees
 * are shared. For commutative operations, child order is canonicalized by
 * structural hash before reuse accounting.
 *
 * @param {string|object} expression
 * @returns {object}
 */
export function normalizeDag(expression) {
  const tree = typeof expression === "string" ? parse(expression) : expression;
  const nodes = [];
  const byKey = new Map();

  function visit(node) {
    const kind = opKind(node);
    assertPrimitive(kind);

    const childRecords = childrenOf(node, kind).map(visit);
    let args = childRecords.map((child) => child.id);
    let childHashes = childRecords.map((child) => child.structural_hash);

    if (COMMUTATIVE.has(kind)) {
      const sorted = childRecords
        .map((child) => ({ id: child.id, hash: child.structural_hash }))
        .sort((a, b) => a.hash.localeCompare(b.hash));
      args = sorted.map((child) => child.id);
      childHashes = sorted.map((child) => child.hash);
    }

    const literal = literalOf(node, kind);
    const structural = { op_kind: kind, args: childHashes, literal };
    const structural_hash = stableHash(structural);
    const key = stableStringify(structural);

    if (byKey.has(key)) return byKey.get(key);

    const id = `n${nodes.length}`;
    const irNode = {
      id,
      op_kind: kind,
      args,
      literal,
      structural_hash,
      domain_annotations: domainAnnotations(kind, args),
      tree_cost: TREE_COST[kind],
    };
    nodes.push(irNode);

    const record = { id, structural_hash };
    byKey.set(key, record);
    return record;
  }

  const rootRecord = visit(tree);
  const tree_cost = totalTreeCost(tree);
  const dag_cost = nodes.reduce((sum, node) => sum + node.tree_cost, 0);

  return {
    schema_version: SCHEMA,
    source: expression,
    root: rootRecord.id,
    nodes,
    tree_cost,
    dag_cost,
    boundaries: {
      internal_contract: "EML IR Lowering Contract v1",
      public_savings_claim: false,
      formal_verification_claim: false,
      compiler_release_claim: false,
    },
  };
}

function replayHash(prev, frame) {
  const frameForHash = { ...frame };
  delete frameForHash.replay_hash;
  return stableHash({ previous: prev, frame: frameForHash });
}

/**
 * Emit a guarded replay packet for a normalized DAG or expression.
 *
 * @param {string|object} expressionOrDag
 * @returns {object}
 */
export function emitReplayPacket(expressionOrDag) {
  const dag = expressionOrDag?.schema_version === SCHEMA ? expressionOrDag : normalizeDag(expressionOrDag);
  const frames = [];
  let prev = "GENESIS";

  function push(frame) {
    const full = {
      schema_version: REPLAY_SCHEMA,
      frame_index: frames.length,
      frame_id: `irv1_${String(frames.length).padStart(4, "0")}`,
      replay_hash_prev: prev,
      ...frame,
    };
    full.replay_hash = replayHash(prev, full);
    prev = full.replay_hash;
    frames.push(full);
  }

  push({ lifecycle_state: "INIT", what_happened: "IR replay packet initialized." });
  push({
    lifecycle_state: "READY",
    root: dag.root,
    node_count: dag.nodes.length,
    tree_cost: dag.tree_cost,
    dag_cost: dag.dag_cost,
    what_happened: "Normalized DAG is ready for operation replay.",
  });

  for (const node of dag.nodes) {
    push({
      lifecycle_state: "RUNNING",
      node_id: node.id,
      op_kind: node.op_kind,
      args: node.args,
      literal: node.literal,
      structural_hash: node.structural_hash,
      domain_annotations: node.domain_annotations,
      guard_action: node.domain_annotations.length ? "ANNOTATE_DOMAIN" : "PASS",
      what_happened: node.domain_annotations.length
        ? `${node.op_kind} replayed with domain annotation.`
        : `${node.op_kind} replayed without domain annotation.`,
    });
  }

  push({ lifecycle_state: "END", what_happened: "All normalized DAG nodes replayed." });
  push({ lifecycle_state: "PARKED", what_happened: "Explicit terminal replay boundary." });

  return {
    schema_version: REPLAY_SCHEMA,
    lifecycle: ["INIT", "READY", "RUNNING", "END", "PARKED"],
    root: dag.root,
    tree_cost: dag.tree_cost,
    dag_cost: dag.dag_cost,
    frames,
    boundaries: dag.boundaries,
  };
}

/**
 * Validate the structural requirements of an EML IR replay packet.
 *
 * @param {object} packet
 * @returns {{ok: boolean, errors: string[]}}
 */
export function validateReplayPacket(packet) {
  const errors = [];
  if (packet.schema_version !== REPLAY_SCHEMA) errors.push("schema_version mismatch");
  if (!Array.isArray(packet.frames) || packet.frames.length < 5) errors.push("frames missing or too short");

  const states = packet.frames?.map((frame) => frame.lifecycle_state) ?? [];
  if (states[0] !== "INIT") errors.push("first frame must be INIT");
  if (states[1] !== "READY") errors.push("second frame must be READY");
  if (!states.includes("RUNNING")) errors.push("at least one RUNNING frame required");
  if (states[states.length - 2] !== "END") errors.push("penultimate frame must be END");
  if (states[states.length - 1] !== "PARKED") errors.push("last frame must be PARKED");

  let prev = "GENESIS";
  for (const [index, frame] of (packet.frames ?? []).entries()) {
    if (frame.frame_index !== index) errors.push(`frame ${index} has incorrect frame_index`);
    if (frame.replay_hash_prev !== prev) errors.push(`frame ${index} has incorrect replay_hash_prev`);
    const expected = replayHash(prev, frame);
    if (frame.replay_hash !== expected) errors.push(`frame ${index} has invalid replay_hash`);
    prev = frame.replay_hash;
    if (frame.lifecycle_state === "RUNNING" && !Array.isArray(frame.domain_annotations)) {
      errors.push(`RUNNING frame ${index} missing domain_annotations`);
    }
  }

  return { ok: errors.length === 0, errors };
}

export default {
  normalizeDag,
  emitReplayPacket,
  validateReplayPacket,
};
