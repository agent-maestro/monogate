import { describe, it, expect } from "vitest";
import { emitReplayPacket, normalizeDag, validateReplayPacket } from "./ir.js";

describe("EML IR v1 normalization", () => {
  it("deduplicates structurally identical subexpressions", () => {
    const dag = normalizeDag("exp(x) + exp(x)");

    const expNodes = dag.nodes.filter((node) => node.op_kind === "exp");
    expect(expNodes).toHaveLength(1);
    expect(dag.tree_cost).toBe(4);
    expect(dag.dag_cost).toBe(3);
    expect(dag.boundaries.public_savings_claim).toBe(false);
  });

  it("canonicalizes commutative child order", () => {
    const left = normalizeDag("x + y");
    const right = normalizeDag("y + x");

    expect(left.nodes.at(-1).structural_hash).toBe(right.nodes.at(-1).structural_hash);
  });

  it("annotates domain-sensitive primitives", () => {
    const dag = normalizeDag("ln(x) + sqrt(y)");
    const annotations = dag.nodes.flatMap((node) => node.domain_annotations);

    expect(annotations.map((item) => item.kind)).toEqual([
      "requires_positive",
      "requires_nonnegative",
    ]);
  });
});

describe("EML IR v1 replay packet", () => {
  it("emits a valid hash-chained lifecycle packet", () => {
    const packet = emitReplayPacket("exp(x) + exp(x)");
    const validation = validateReplayPacket(packet);

    expect(validation.ok).toBe(true);
    expect(packet.frames[0].lifecycle_state).toBe("INIT");
    expect(packet.frames[1].lifecycle_state).toBe("READY");
    expect(packet.frames.at(-1).lifecycle_state).toBe("PARKED");
  });

  it("fails validation when a replay hash is modified", () => {
    const packet = emitReplayPacket("ln(x)");
    packet.frames[2].replay_hash = "fnv1a64:broken";

    const validation = validateReplayPacket(packet);
    expect(validation.ok).toBe(false);
    expect(validation.errors.some((error) => error.includes("invalid replay_hash"))).toBe(true);
  });
});
