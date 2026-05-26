import { describe, it, expect } from "vitest";
import {
  certifyLowering,
  checkSampledEquivalence,
  emitReplayPacket,
  evaluateDag,
  lowerDagToJS,
  lowerDagToPython,
  normalizeDag,
  validateReplayPacket,
} from "./ir.js";

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

describe("EML IR v1 lowering", () => {
  it("lowers a shared DAG to JavaScript and Python sketches", () => {
    const dag = normalizeDag("exp(x) + exp(x)");
    const js = lowerDagToJS(dag);
    const python = lowerDagToPython(dag);

    expect(js.source).toContain("function lowered(x)");
    expect(js.source).toContain("Math.exp");
    expect(python.source).toContain("def lowered(x):");
    expect(python.source).toContain("math.exp");
  });

  it("evaluates DAGs directly on samples", () => {
    expect(evaluateDag("exp(x) + exp(x)", { x: 1 })).toBeCloseTo(2 * Math.E);
  });

  it("checks sampled equivalence between interpreter and lowered JS", () => {
    const evidence = checkSampledEquivalence("exp(x) / exp(y)", {
      samples: [
        { x: 1, y: 2 },
        { x: 2, y: 1 },
      ],
    });

    expect(evidence.behavioral_equivalence_sampled).toBe(true);
    expect(evidence.max_abs_error).toBeLessThanOrEqual(1e-12);
    expect(evidence.rows).toHaveLength(2);
  });

  it("builds a lowering certificate with replay and evidence boundaries", () => {
    const cert = certifyLowering("ln(x) + sqrt(y)", {
      samples: [
        { x: 1, y: 4 },
        { x: Math.E, y: 9 },
      ],
    });

    expect(cert.replay.frames.at(-1).lifecycle_state).toBe("PARKED");
    expect(cert.lowering.javascript.source).toContain("Math.log");
    expect(cert.lowering.python.source).toContain("math.sqrt");
    expect(cert.equivalence.behavioral_equivalence_sampled).toBe(true);
    expect(cert.boundaries.formal_verification_claim).toBe(false);
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
