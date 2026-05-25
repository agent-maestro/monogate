import model from "../data/eml_ir_inspector_model.json";
import polynomialEvidence from "../data/machlib_polynomial_evidence_internal_card.json";
import finiteZeroPacket from "../data/machlib_finite_zero_packet_internal_card.json";
import { useState } from "react";

const C = {
  bg: "#07080f",
  surface: "#0d0e1c",
  border: "#191b2e",
  text: "#cdd0e0",
  muted: "#6f738a",
  accent: "#e8a020",
  blue: "#6ab0f5",
  green: "#5ec47a",
  warn: "#f59e0b",
};

function Stat({ label, value, tone = C.accent }) {
  return (
    <div style={{ background: C.surface, border: `1px solid ${C.border}`, borderRadius: 8, padding: "12px 14px" }}>
      <div style={{ fontSize: 9, color: C.muted, textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: 4 }}>
        {label}
      </div>
      <div style={{ color: tone, fontSize: 18, fontWeight: 700, wordBreak: "break-word" }}>{value}</div>
    </div>
  );
}

function Chip({ children, tone = C.muted }) {
  return (
    <span style={{
      display: "inline-flex",
      alignItems: "center",
      border: `1px solid ${C.border}`,
      borderRadius: 999,
      padding: "3px 8px",
      color: tone,
      background: "rgba(255,255,255,0.025)",
      fontSize: 10,
      lineHeight: 1.5,
    }}>
      {children}
    </span>
  );
}

function MiniDag({ program }) {
  return (
    <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(150px,1fr))", gap: 8 }}>
      {program.nodes.map((node) => {
        const reused = node.reuse_count > 1;
        return (
          <div key={node.id} style={{
            border: `1px solid ${reused ? C.accent : C.border}`,
            background: reused ? "rgba(232,160,32,0.06)" : C.bg,
            borderRadius: 7,
            padding: 10,
            minHeight: 92,
          }}>
            <div style={{ display: "flex", justifyContent: "space-between", gap: 8, marginBottom: 5 }}>
              <strong style={{ color: C.text }}>{node.id}</strong>
              <span style={{ color: reused ? C.accent : C.muted, fontSize: 10 }}>
                {reused ? `${node.reuse_count}x` : node.kind}
              </span>
            </div>
            <div style={{ color: C.blue, fontSize: 10, wordBreak: "break-word", lineHeight: 1.5 }}>{node.source}</div>
            <div style={{ color: C.muted, fontSize: 9, marginTop: 6 }}>
              op={node.op ?? "none"} · args={node.args.length ? node.args.join(", ") : "none"}
            </div>
          </div>
        );
      })}
    </div>
  );
}

function Timeline({ program }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 7 }}>
      {program.timeline.map((frame) => {
        const guarded = frame.guard_action !== "PASS";
        return (
          <div key={frame.frame_id} style={{
            border: `1px solid ${guarded ? "rgba(245,158,11,0.45)" : C.border}`,
            background: guarded ? "rgba(245,158,11,0.055)" : C.bg,
            borderRadius: 7,
            padding: "9px 10px",
          }}>
            <div style={{ display: "flex", justifyContent: "space-between", gap: 8, flexWrap: "wrap" }}>
              <span style={{ color: frame.state === "PARKED" ? C.green : C.text, fontWeight: 700 }}>
                {frame.state}
              </span>
              <span style={{ color: guarded ? C.warn : C.green, fontSize: 10 }}>
                {frame.guard_action}
              </span>
            </div>
            <div style={{ color: C.muted, fontSize: 10, marginTop: 3 }}>
              tick {frame.tick} · {frame.kernel_id}
            </div>
            <div style={{ color: C.text, fontSize: 10, lineHeight: 1.6, marginTop: 6 }}>{frame.what_happened}</div>
            <div style={{ color: C.muted, fontSize: 9, marginTop: 6, wordBreak: "break-word" }}>
              {frame.replay_hash.slice(0, 32)}...
            </div>
          </div>
        );
      })}
    </div>
  );
}

export default function EMLIRInspectorTab() {
  const programs = model.programs;
  const [selectedId, setSelectedId] = useState(model.best_program_id);
  const selected = programs.find((row) => row.program_id === selectedId) ?? programs[0];
  const best = selected;

  return (
    <div>
      <div style={{ marginBottom: 16 }}>
        <div style={{ display: "flex", justifyContent: "space-between", gap: 10, flexWrap: "wrap", alignItems: "baseline" }}>
          <div>
            <div style={{ fontSize: 14, fontWeight: 700, color: C.accent, marginBottom: 6 }}>
              EML IR Inspector
            </div>
            <div style={{ fontSize: 11, color: C.muted, lineHeight: 1.8, maxWidth: 680 }}>
              Prototype view of EML as inspectable bytecode: expression source, DAG sharing, replay timeline,
              guard annotations, and lowered code sketches.
            </div>
          </div>
          <Chip tone={C.warn}>INTERNAL / PROTOTYPE</Chip>
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(150px,1fr))", gap: 10, marginBottom: 14 }}>
        <Stat label="programs" value={model.program_count} />
        <Stat label="replay frames" value={model.total_replay_frames} tone={C.blue} />
        <Stat label="best fixture" value={model.best_program_id} tone={C.green} />
        <Stat label="extra DAG savings" value={model.best_extra_superbest_savings_nodes} tone={C.warn} />
      </div>

      <div style={{
        background: "rgba(245,158,11,0.06)",
        border: "1px solid rgba(245,158,11,0.36)",
        borderRadius: 8,
        padding: 12,
        color: C.muted,
        fontSize: 10,
        lineHeight: 1.7,
        marginBottom: 14,
      }}>
        Tree SuperBEST costs are the public-safe baseline. DAG/IR savings shown here are internal prototype evidence
        until the lowering contract and product copy are reviewed.
      </div>

      <div style={{
        display: "grid",
        gridTemplateColumns: "repeat(auto-fit,minmax(220px,1fr))",
        gap: 10,
        marginBottom: 14,
      }}>
        <a href="?tab=field" style={{
          background: C.surface,
          border: `1px solid ${C.border}`,
          borderRadius: 8,
          padding: 12,
          color: C.text,
          textDecoration: "none",
        }}>
          <div style={{ color: C.accent, fontSize: 11, fontWeight: 700, marginBottom: 5 }}>
            IR {"->"} Field bridge
          </div>
          <div style={{ color: C.muted, fontSize: 10, lineHeight: 1.7 }}>
            Open the complex field view to see the visual grammar behind EML slices such as eml(z, 1)
            and eml(z, z + 2).
          </div>
        </a>
        <div style={{
          background: C.surface,
          border: `1px solid ${C.border}`,
          borderRadius: 8,
          padding: 12,
          color: C.muted,
          fontSize: 10,
          lineHeight: 1.7,
        }}>
          <strong style={{ color: C.text }}>Example chooser:</strong> select a program below to inspect its DAG,
          replay timeline, and lowering sketch.
        </div>
      </div>

      <div style={{ background: C.surface, border: `1px solid ${C.border}`, borderRadius: 8, overflow: "hidden", marginBottom: 14 }}>
        <div style={{
          display: "grid",
          gridTemplateColumns: "minmax(160px,1.2fr) 1fr 80px 80px 90px",
          gap: 8,
          padding: "8px 12px",
          background: C.bg,
          color: C.muted,
          fontSize: 9,
          textTransform: "uppercase",
          letterSpacing: "0.06em",
        }}>
          <span>Program</span><span>Family</span><span>Tree</span><span>DAG</span><span>Extra</span>
        </div>
        {programs.map((program, index) => {
          const active = program.program_id === best.program_id;
          return (
          <button key={program.program_id} onClick={() => setSelectedId(program.program_id)} style={{
            display: "grid",
            gridTemplateColumns: "minmax(160px,1.2fr) 1fr 80px 80px 90px",
            gap: 8,
            padding: "9px 12px",
            borderTop: `1px solid ${C.border}`,
            borderLeft: "none",
            borderRight: "none",
            borderBottom: "none",
            width: "100%",
            cursor: "pointer",
            textAlign: "left",
            background: active ? "rgba(232,160,32,0.075)" : index % 2 ? "rgba(255,255,255,0.012)" : "transparent",
            fontSize: 10,
            alignItems: "center",
            fontFamily: "inherit",
          }}>
            <span style={{ color: active ? C.accent : C.text, wordBreak: "break-word" }}>{program.program_id}</span>
            <span style={{ color: C.muted }}>{program.family}</span>
            <span style={{ color: C.text }}>{program.tree_superbest_nodes}</span>
            <span style={{ color: C.blue }}>{program.dag_superbest_nodes}</span>
            <span style={{ color: program.extra_superbest_savings_nodes > 0 ? C.green : C.muted }}>
              {program.extra_superbest_savings_nodes}
            </span>
          </button>
          );
        })}
      </div>

      <div style={{ background: C.surface, border: `1px solid ${C.border}`, borderRadius: 8, padding: 14, marginBottom: 14 }}>
        <div style={{ display: "flex", justifyContent: "space-between", gap: 10, flexWrap: "wrap", marginBottom: 10 }}>
          <div>
            <div style={{ color: C.accent, fontSize: 13, fontWeight: 700 }}>{best.program_id}</div>
            <div style={{ color: C.muted, fontSize: 10, lineHeight: 1.7 }}>{best.why}</div>
          </div>
          <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
            <Chip>Tree {best.tree_superbest_nodes}</Chip>
            <Chip>DAG {best.dag_superbest_nodes}</Chip>
            <Chip tone={C.green}>Extra {best.extra_superbest_savings_nodes}</Chip>
            <Chip tone={C.blue}>{best.frame_count} frames</Chip>
          </div>
        </div>
        <div style={{ background: C.bg, border: `1px solid ${C.border}`, borderRadius: 6, padding: 10, color: C.blue, fontSize: 11, wordBreak: "break-word", marginBottom: 12 }}>
          {best.expression}
        </div>
        <div style={{ marginBottom: 10, display: "flex", gap: 6, flexWrap: "wrap" }}>
          {best.reused_nodes.map((node) => (
            <Chip key={node.id} tone={C.accent}>{node.id} {node.op ?? "input"} reused {node.reuse_count}x</Chip>
          ))}
        </div>
        <MiniDag program={best} />
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "minmax(260px, 1fr) minmax(260px, 1fr)", gap: 12 }}>
        <div style={{ background: C.surface, border: `1px solid ${C.border}`, borderRadius: 8, padding: 14 }}>
          <div style={{ color: C.text, fontSize: 12, fontWeight: 700, marginBottom: 10 }}>Replay Timeline</div>
          <Timeline program={best} />
        </div>
        <div style={{ background: C.surface, border: `1px solid ${C.border}`, borderRadius: 8, padding: 14 }}>
          <div style={{ color: C.text, fontSize: 12, fontWeight: 700, marginBottom: 10 }}>Lowered Python Sketch</div>
          <pre style={{
            whiteSpace: "pre-wrap",
            wordBreak: "break-word",
            margin: 0,
            background: C.bg,
            border: `1px solid ${C.border}`,
            borderRadius: 6,
            padding: 12,
            color: C.text,
            fontSize: 10,
            lineHeight: 1.6,
          }}>{best.lowering.python_source}</pre>
        </div>
      </div>

      <div style={{
        background: C.surface,
        border: `1px solid ${C.border}`,
        borderRadius: 8,
        padding: 14,
        marginTop: 14,
      }}>
        <div style={{ display: "flex", justifyContent: "space-between", gap: 10, flexWrap: "wrap", marginBottom: 10 }}>
          <div>
            <div style={{ color: C.accent, fontSize: 13, fontWeight: 700 }}>{polynomialEvidence.title}</div>
            <div style={{ color: C.muted, fontSize: 10, lineHeight: 1.7 }}>{polynomialEvidence.summary}</div>
          </div>
          <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
            <Chip tone={C.warn}>{polynomialEvidence.status}</Chip>
            <Chip tone={C.green}>{polynomialEvidence.fact_count} checked facts</Chip>
            <Chip tone={C.warn}>{polynomialEvidence.analytic_identity_theorem_status}</Chip>
          </div>
        </div>
        <div style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit,minmax(220px,1fr))",
          gap: 8,
        }}>
          {polynomialEvidence.facts.map((fact) => (
            <div key={fact.id} style={{
              background: C.bg,
              border: `1px solid ${C.border}`,
              borderRadius: 7,
              padding: 10,
            }}>
              <div style={{ color: C.green, fontSize: 10, fontWeight: 700, marginBottom: 5 }}>
                {fact.evidence_class}
              </div>
              <div style={{ color: C.text, fontSize: 11, fontWeight: 700, marginBottom: 5 }}>
                {fact.statement}
              </div>
              <div style={{ color: C.muted, fontSize: 10, lineHeight: 1.6, marginBottom: 6 }}>
                {fact.meaning}
              </div>
              <div style={{ color: C.blue, fontSize: 9, wordBreak: "break-word" }}>
                {fact.lean_name}
              </div>
            </div>
          ))}
        </div>
        <div style={{
          marginTop: 10,
          color: C.muted,
          fontSize: 10,
          lineHeight: 1.7,
        }}>
          Internal evidence only. This panel does not claim analytic continuation, infinite zero-set behavior,
          public theorem status, package publishing, or marketplace readiness.
        </div>
      </div>

      <div style={{
        background: C.surface,
        border: `1px solid ${C.border}`,
        borderRadius: 8,
        padding: 14,
        marginTop: 14,
      }}>
        <div style={{ display: "flex", justifyContent: "space-between", gap: 10, flexWrap: "wrap", marginBottom: 10 }}>
          <div>
            <div style={{ color: C.accent, fontSize: 13, fontWeight: 700 }}>{finiteZeroPacket.title}</div>
            <div style={{ color: C.muted, fontSize: 10, lineHeight: 1.7 }}>{finiteZeroPacket.summary}</div>
          </div>
          <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
            <Chip tone={C.warn}>{finiteZeroPacket.status}</Chip>
            <Chip tone={C.green}>{finiteZeroPacket.sample_count} root samples</Chip>
            <Chip tone={C.warn}>{finiteZeroPacket.next_research_gate}</Chip>
          </div>
        </div>
        <div style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit,minmax(220px,1fr))",
          gap: 8,
        }}>
          {finiteZeroPacket.samples.map((sample) => (
            <div key={sample.sample_id} style={{
              background: C.bg,
              border: `1px solid ${C.border}`,
              borderRadius: 7,
              padding: 10,
            }}>
              <div style={{ display: "flex", justifyContent: "space-between", gap: 8, flexWrap: "wrap", marginBottom: 5 }}>
                <span style={{ color: C.green, fontSize: 10, fontWeight: 700 }}>{sample.evidence_class}</span>
                <span style={{ color: C.accent, fontSize: 10 }}>root {sample.root_witness}</span>
              </div>
              <div style={{ color: C.blue, fontSize: 11, fontWeight: 700, marginBottom: 5, wordBreak: "break-word" }}>
                {sample.polynomial}
              </div>
              <div style={{ color: C.text, fontSize: 10, lineHeight: 1.6, marginBottom: 6 }}>
                {sample.statement}
              </div>
              <div style={{ color: C.muted, fontSize: 9, wordBreak: "break-word" }}>
                {sample.lean_name}
              </div>
            </div>
          ))}
        </div>
        <div style={{
          marginTop: 10,
          color: C.muted,
          fontSize: 10,
          lineHeight: 1.7,
        }}>
          This is a finite sample packet only. Degree/root-count reasoning is still a separate blocked feasibility gate.
        </div>
      </div>
    </div>
  );
}
