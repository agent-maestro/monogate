// BenchmarkTab.jsx — SuperBEST benchmark suite (E4)
// "Run All" to compute 25 preset savings. Shareable, reproducible.

import { useState, useMemo } from "react";
import { runBenchmarks, savings } from "../superbest.js";

const C = {
  bg: "#07080f", surface: "#0d0e1c", border: "#191b2e",
  text: "#cdd0e0", muted: "#4e5168", accent: "#e8a020",
  green: "#5ec47a", blue: "#6ab0f5", red: "#e05060",
};

const FAMILY_COLOR = {
  EXL: "#f59e0b", EDL: "#2dd4bf", EML: "#7c6ff7", EAL: "#5ec47a",
};

function SavingsBar({ pct, max = 100 }) {
  const col = pct >= 70 ? C.green : pct >= 40 ? C.accent : C.blue;
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
      <div style={{ flex: 1, height: 5, background: C.border, borderRadius: 3, overflow: "hidden" }}>
        <div style={{
          width: `${(pct / max) * 100}%`, height: "100%",
          background: col, borderRadius: 3,
          transition: "width 0.6s ease",
        }} />
      </div>
      <span style={{ fontSize: 10, color: col, minWidth: 34, textAlign: "right" }}>{pct}%</span>
    </div>
  );
}

export default function BenchmarkTab() {
  const [ran, setRan] = useState(false);
  const [copied, setCopied] = useState(false);
  const results = useMemo(() => ran ? runBenchmarks() : [], [ran]);

  const avgSavings = useMemo(() => {
    if (!results.length) return null;
    const total = results.reduce((s, r) => s + r.savings, 0);
    return Math.round(total / results.length);
  }, [results]);

  const totalEml  = useMemo(() => results.reduce((s, r) => s + r.eml, 0), [results]);
  const totalBest = useMemo(() => results.reduce((s, r) => s + r.best, 0), [results]);
  const overallSavings = useMemo(() => savings(totalEml, totalBest), [totalEml, totalBest]);

  function copyResults() {
    const lines = [
      "SuperBEST Benchmark Results — monogate.dev",
      `Overall savings: ${overallSavings}% (${totalEml}n EML → ${totalBest}n SuperBEST)`,
      "",
      "Expression,EML nodes,SuperBEST nodes,Savings",
      ...results.map(r => `${r.label},${r.eml},${r.best},${r.savings}%`),
    ].join("\n");
    navigator.clipboard.writeText(lines).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2500);
    });
  }

  return (
    <div style={{ color: C.text }}>
      {/* Header */}
      <div style={{ marginBottom: 16 }}>
        <div style={{ fontSize: 13, fontWeight: 700, color: C.accent, marginBottom: 4 }}>
          SuperBEST Benchmark Suite
        </div>
        <div style={{ fontSize: 10, color: C.muted, lineHeight: 1.7 }}>
          Node counts for 25 standard expressions: pure EML single-operator vs SuperBEST routing.
          Numbers are exact (operator node counts, not timing). Reproducible on any machine.
        </div>
      </div>

      {/* Run button */}
      {!ran ? (
        <div style={{
          background: C.surface, border: `1px solid ${C.border}`,
          borderRadius: 10, padding: "40px 24px", textAlign: "center", marginBottom: 16,
        }}>
          <div style={{ fontSize: 28, marginBottom: 12, color: C.muted }}>▶</div>
          <button onClick={() => setRan(true)} style={{
            fontSize: 13, fontWeight: 700, padding: "12px 32px",
            background: "rgba(94,196,122,0.12)", border: `1px solid ${C.green}`,
            color: C.green, borderRadius: 6, cursor: "pointer", letterSpacing: "0.05em",
          }}>
            RUN ALL BENCHMARKS
          </button>
          <div style={{ fontSize: 9, color: C.muted, marginTop: 10 }}>
            25 expressions · instant · no network · fully reproducible
          </div>
        </div>
      ) : (
        <>
          {/* Summary card */}
          <div style={{
            background: "rgba(94,196,122,0.06)", border: "1px solid rgba(94,196,122,0.25)",
            borderRadius: 10, padding: "16px 20px", marginBottom: 16,
            display: "grid", gridTemplateColumns: "1fr 1fr 1fr 1fr", gap: 16,
          }}>
            {[
              { label: "Overall savings", value: `${overallSavings}%`, col: C.green },
              { label: "EML total nodes", value: `${totalEml}n`, col: C.muted },
              { label: "SuperBEST nodes", value: `${totalBest}n`, col: C.green },
              { label: "Avg savings", value: `${avgSavings}%`, col: C.accent },
            ].map(({ label, value, col }) => (
              <div key={label} style={{ textAlign: "center" }}>
                <div style={{ fontSize: 20, fontWeight: 700, color: col }}>{value}</div>
                <div style={{ fontSize: 9, color: C.muted, marginTop: 3 }}>{label}</div>
              </div>
            ))}
          </div>

          {/* Table */}
          <div style={{ background: C.surface, border: `1px solid ${C.border}`, borderRadius: 8, overflow: "hidden", marginBottom: 12 }}>
            <div style={{
              display: "grid", gridTemplateColumns: "2fr 70px 80px 1fr",
              padding: "8px 14px", borderBottom: `1px solid ${C.border}`,
              fontSize: 9, color: C.muted, textTransform: "uppercase", letterSpacing: "0.08em",
            }}>
              <span>Expression</span>
              <span style={{ textAlign: "right" }}>EML</span>
              <span style={{ textAlign: "right" }}>SuperBEST</span>
              <span style={{ paddingLeft: 8 }}>Savings</span>
            </div>
            {results.map((r, i) => (
              <div key={r.id} style={{
                display: "grid", gridTemplateColumns: "2fr 70px 80px 1fr",
                padding: "7px 14px",
                background: i % 2 === 0 ? "transparent" : "rgba(255,255,255,0.01)",
                borderBottom: i < results.length - 1 ? `1px solid ${C.border}` : "none",
                alignItems: "center",
              }}>
                <span style={{ fontSize: 11, color: C.text, fontFamily: "'Space Mono',monospace" }}>
                  {r.label}
                </span>
                <span style={{ fontSize: 11, color: C.muted, textAlign: "right" }}>{r.eml}n</span>
                <span style={{
                  fontSize: 11, color: r.savings > 0 ? C.green : C.muted, textAlign: "right",
                  fontWeight: r.savings > 50 ? 700 : 400,
                }}>
                  {r.best}n
                </span>
                <div style={{ paddingLeft: 8 }}>
                  <SavingsBar pct={r.savings} />
                </div>
              </div>
            ))}
          </div>

          {/* Actions */}
          <div style={{ display: "flex", gap: 8, justifyContent: "flex-end" }}>
            <button onClick={() => setRan(false)} style={{
              fontSize: 10, padding: "6px 14px", borderRadius: 4, cursor: "pointer",
              background: "transparent", border: `1px solid ${C.border}`, color: C.muted,
            }}>
              ↺ Reset
            </button>
            <button onClick={copyResults} style={{
              fontSize: 10, padding: "6px 14px", borderRadius: 4, cursor: "pointer",
              background: copied ? "rgba(94,196,122,0.12)" : "rgba(255,255,255,0.04)",
              border: `1px solid ${copied ? C.green : C.border}`,
              color: copied ? C.green : C.muted,
            }}>
              {copied ? "copied ✓" : "copy results (CSV)"}
            </button>
          </div>

          {/* Methodology */}
          <div style={{
            background: C.surface, border: `1px solid ${C.border}`, borderRadius: 8,
            padding: 14, marginTop: 12, fontSize: 9, color: C.muted, lineHeight: 1.8,
          }}>
            <span style={{ color: C.accent, fontWeight: 700 }}>Methodology:</span>{" "}
            Node counts are operator-graph sizes — the number of EML-family gate evaluations.
            EML baseline uses the single best operator per operation (pure EML, no routing).
            SuperBEST routes each operation to its optimal operator: EXL for mul/pow/neg, EML for exp/sub,
            EAL for add, EDL for div/recip. Numbers verified by exhaustive N-level search; see
            addendum_neg_optimality.md. All counts are exact integers, not estimates.
          </div>
        </>
      )}
    </div>
  );
}
