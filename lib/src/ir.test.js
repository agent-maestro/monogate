import { describe, it, expect } from "vitest";
import {
  buildEvidencePacket,
  certifyLowering,
  checkSampledEquivalence,
  checkStructuralLowering,
  emitReplayPacket,
  evaluateDag,
  lowerDagToJS,
  lowerDagToPython,
  normalizeDag,
  researchStatusLevels,
  validateEvidencePacket,
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

  it("checks structural lowering coverage for every DAG node", () => {
    const structural = checkStructuralLowering("sin(x) + cos(y)");

    expect(structural.schema_version).toBe("monogate.eml_ir.structural_lowering.v1");
    expect(structural.structural_lowering_verified).toBe(true);
    expect(structural.verified_node_count).toBe(structural.node_count);
    expect(structural.boundaries.formal_verification_claim).toBe(false);
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
    expect(cert.structural.structural_lowering_verified).toBe(true);
    expect(cert.equivalence.behavioral_equivalence_sampled).toBe(true);
    expect(cert.boundaries.formal_verification_claim).toBe(false);
  });

  it("builds and validates a top-level evidence packet", () => {
    const packet = buildEvidencePacket("exp(x) + exp(x)", {
      samples: [{ x: 1 }, { x: 2 }],
    });
    const validation = validateEvidencePacket(packet);

    expect(packet.schema_version).toBe("monogate.eml_ir.evidence_packet.v1");
    expect(packet.packet_hash).toMatch(/^fnv1a64:/);
    expect(packet.research_status.labels).toEqual(["verified", "sampled", "prototype"]);
    expect(packet.boundaries.public_savings_claim).toBe(false);
    expect(validation.ok).toBe(true);
  });

  it("exposes public-safe research status levels", () => {
    const levels = researchStatusLevels();

    expect(levels.verified.public_ready).toBe(true);
    expect(levels.sampled.public_ready).toBe(false);
    expect(levels.prototype.public_ready).toBe(false);
    expect(levels.blocked.public_ready).toBe(false);
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
