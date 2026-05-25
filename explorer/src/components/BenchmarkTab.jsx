// BenchmarkTab.jsx — SuperBEST benchmark suite (E4)
// "Run All" to compute 25 preset savings. Shareable, reproducible.

import { useState, useMemo } from "react";
import {
  DAG_BENCHMARKS,
  DAG_LOWERING_PRESETS,
  defaultDagLoweringPreset,
  lowerDagExpression,
  runBenchmarks,
  runDagBenchmarks,
  savings,
} from "../superbest.js";

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

function ModeButton({ active, children, onClick }) {
  return (
    <button onClick={onClick} style={{
      fontSize: 10, fontWeight: 700, padding: "8px 12px", borderRadius: 6,
      cursor: "pointer", border: `1px solid ${active ? C.accent : C.border}`,
      background: active ? "rgba(232,160,32,0.12)" : "rgba(255,255,255,0.03)",
      color: active ? C.accent : C.muted,
    }}>
      {children}
    </button>
  );
}

function SharedChip({ children }) {
  return (
    <span style={{
      display: "inline-block", fontSize: 9, padding: "3px 6px",
      borderRadius: 999, marginRight: 5, marginTop: 3,
      background: "rgba(106,176,245,0.10)", border: "1px solid rgba(106,176,245,0.24)",
      color: C.blue, fontFamily: "'Space Mono',monospace",
    }}>
      {children}
    </span>
  );
}

export default function BenchmarkTab() {
  const [ran, setRan] = useState(false);
  const [copied, setCopied] = useState(false);
  const [mode, setMode] = useState("tree");
  const [lowerInput, setLowerInput] = useState(defaultDagLoweringPreset().expression);
  const [codeLang, setCodeLang] = useState("python");
  const [copiedLowering, setCopiedLowering] = useState(false);
  const treeMode = mode === "tree";
  const results = useMemo(() => {
    if (!ran) return [];
    return treeMode ? runBenchmarks() : runDagBenchmarks();
  }, [ran, treeMode]);
  const lowered = useMemo(() => lowerDagExpression(lowerInput), [lowerInput]);

  const avgSavings = useMemo(() => {
    if (!results.length) return null;
    const total = results.reduce((s, r) => s + (treeMode ? r.savings : r.dagSavings), 0);
    return Math.round(total / results.length);
  }, [results, treeMode]);

  const totalEml = useMemo(() => results.reduce((s, r) => s + r.eml, 0), [results]);
  const totalBest = useMemo(
    () => results.reduce((s, r) => s + (treeMode ? r.best : r.treeBest), 0),
    [results, treeMode],
  );
  const totalDag = useMemo(
    () => results.reduce((s, r) => s + (treeMode ? 0 : r.dagBest), 0),
    [results, treeMode],
  );
  const totalExtraDag = useMemo(
    () => results.reduce((s, r) => s + (treeMode ? 0 : r.extraDagSavings), 0),
    [results, treeMode],
  );
  const overallSavings = useMemo(
    () => savings(totalEml, treeMode ? totalBest : totalDag),
    [totalEml, totalBest, totalDag, treeMode],
  );

  function copyResults() {
    const lines = [
      "SuperBEST Benchmark Results — monogate.dev",
      `Mode: ${treeMode ? "Tree SuperBEST" : "DAG SuperBEST"}`,
      `Overall savings: ${overallSavings}% (${totalEml}n EML → ${treeMode ? totalBest : totalDag}n SuperBEST)`,
      "",
      treeMode ? "Expression,EML nodes,SuperBEST nodes,Savings" : "Expression,EML nodes,Tree SuperBEST,DAG SuperBEST,Extra DAG savings",
      ...results.map(r => treeMode
        ? `${r.label},${r.eml},${r.best},${r.savings}%`
        : `${r.label},${r.eml},${r.treeBest},${r.dagBest},${r.extraDagSavings}`),
    ].join("\n");
    navigator.clipboard.writeText(lines).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2500);
    });
  }

  function copyLoweredSource() {
    const source = codeLang === "python" ? lowered.pythonSource : lowered.javascriptSource;
    if (!source) return;
    navigator.clipboard.writeText(source).then(() => {
      setCopiedLowering(true);
      setTimeout(() => setCopiedLowering(false), 2500);
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
          Node counts for standard expressions. Tree mode shows canonical row routing;
          DAG mode shows expression-level shared subexpressions. Numbers are operator counts,
          not timing estimates.
        </div>
      </div>

      <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginBottom: 12 }}>
        <ModeButton active={treeMode} onClick={() => setMode("tree")}>Tree SuperBEST</ModeButton>
        <ModeButton active={!treeMode} onClick={() => setMode("dag")}>DAG SuperBEST</ModeButton>
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
            {treeMode ? "25 tree expressions" : `${DAG_BENCHMARKS.length} DAG-sharing cases`} · instant · no network · reproducible
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
              { label: treeMode ? "Overall savings" : "DAG savings", value: `${overallSavings}%`, col: C.green },
              { label: "EML total nodes", value: `${totalEml}n`, col: C.muted },
              { label: treeMode ? "SuperBEST nodes" : "Tree SuperBEST", value: `${totalBest}n`, col: treeMode ? C.green : C.muted },
              { label: treeMode ? "Avg savings" : "Extra DAG saved", value: treeMode ? `${avgSavings}%` : `${totalExtraDag}n`, col: C.accent },
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
              display: "grid", gridTemplateColumns: treeMode ? "2fr 70px 80px 1fr" : "2fr 62px 72px 72px 1.7fr",
              padding: "8px 14px", borderBottom: `1px solid ${C.border}`,
              fontSize: 9, color: C.muted, textTransform: "uppercase", letterSpacing: "0.08em",
            }}>
              <span>Expression</span>
              <span style={{ textAlign: "right" }}>EML</span>
              <span style={{ textAlign: "right" }}>{treeMode ? "SuperBEST" : "Tree"}</span>
              <span style={{ textAlign: treeMode ? "left" : "right", paddingLeft: treeMode ? 8 : 0 }}>
                {treeMode ? "Savings" : "DAG"}
              </span>
              {!treeMode && <span style={{ paddingLeft: 8 }}>Shared nodes</span>}
            </div>
            {results.map((r, i) => (
              <div key={r.id} style={{
                display: "grid", gridTemplateColumns: treeMode ? "2fr 70px 80px 1fr" : "2fr 62px 72px 72px 1.7fr",
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
                  fontSize: 11, color: (treeMode ? r.savings : r.treeSavings) > 0 ? C.green : C.muted, textAlign: "right",
                  fontWeight: (treeMode ? r.savings : r.treeSavings) > 50 ? 700 : 400,
                }}>
                  {treeMode ? r.best : r.treeBest}n
                </span>
                {treeMode ? (
                  <div style={{ paddingLeft: 8 }}>
                    <SavingsBar pct={r.savings} />
                  </div>
                ) : (
                  <>
                    <span style={{ fontSize: 11, color: C.green, textAlign: "right", fontWeight: 700 }}>
                      {r.dagBest}n
                    </span>
                    <div style={{ paddingLeft: 8, minHeight: 23 }}>
                      {r.shared.length ? r.shared.map(s => <SharedChip key={s}>{s}</SharedChip>) : (
                        <span style={{ fontSize: 9, color: C.muted }}>no repeated subexpression</span>
                      )}
                    </div>
                  </>
                )}
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

          {!treeMode && (
            <div style={{
              background: C.surface, border: `1px solid ${C.border}`, borderRadius: 8,
              padding: 14, marginTop: 12, marginBottom: 12,
            }}>
              <div style={{ display: "flex", justifyContent: "space-between", gap: 12, flexWrap: "wrap", marginBottom: 10 }}>
                <div>
                  <div style={{ fontSize: 12, fontWeight: 700, color: C.accent, marginBottom: 4 }}>
                    DAG Lowering Playground
                  </div>
                  <div style={{ fontSize: 9, color: C.muted, lineHeight: 1.6, maxWidth: 720 }}>
                    Paste or pick a known expression fixture to see shared temporaries before cost
                    reporting. The browser demo uses static lowering fixtures; arbitrary parsing
                    stays in the Python CLI.
                  </div>
                </div>
                <div style={{ fontSize: 9, color: C.blue, fontFamily: "'Space Mono',monospace", alignSelf: "flex-start" }}>
                  python/scripts/superbest_dag_lowering.py
                </div>
              </div>

              <textarea
                value={lowerInput}
                onChange={(event) => setLowerInput(event.target.value)}
                rows={3}
                spellCheck={false}
                style={{
                  width: "100%", resize: "vertical", boxSizing: "border-box",
                  background: "#080a13", border: `1px solid ${C.border}`, borderRadius: 6,
                  color: C.text, padding: 10, fontSize: 10, lineHeight: 1.5,
                  fontFamily: "'Space Mono',monospace", marginBottom: 8,
                }}
              />

              <div style={{ display: "flex", gap: 6, flexWrap: "wrap", marginBottom: 12 }}>
                {DAG_LOWERING_PRESETS.map(preset => (
                  <button
                    key={preset.id}
                    onClick={() => setLowerInput(preset.expression)}
                    style={{
                      fontSize: 9, padding: "5px 8px", borderRadius: 5, cursor: "pointer",
                      background: lowered.id === preset.id ? "rgba(106,176,245,0.12)" : "rgba(255,255,255,0.03)",
                      border: `1px solid ${lowered.id === preset.id ? C.blue : C.border}`,
                      color: lowered.id === preset.id ? C.blue : C.muted,
                    }}
                  >
                    {preset.label}
                  </button>
                ))}
              </div>

              {lowered.status === "LOWERED_PRESET" ? (
                <>
                  <div style={{
                    display: "grid", gridTemplateColumns: "repeat(4, minmax(0, 1fr))",
                    gap: 8, marginBottom: 12,
                  }}>
                    {[
                      { label: "Tree BEST", value: `${lowered.treeSuperbestNodes}n`, color: C.muted },
                      { label: "DAG BEST", value: `${lowered.dagSuperbestNodes}n`, color: C.green },
                      { label: "Extra saved", value: `${lowered.extraSuperbestSavingsNodes}n`, color: C.accent },
                      { label: "Temps", value: lowered.temporaryCount, color: C.blue },
                    ].map(item => (
                      <div key={item.label} style={{
                        border: `1px solid ${C.border}`, borderRadius: 6, padding: "10px 8px",
                        background: "rgba(255,255,255,0.02)", textAlign: "center",
                      }}>
                        <div style={{ fontSize: 16, fontWeight: 700, color: item.color }}>{item.value}</div>
                        <div style={{ fontSize: 8, color: C.muted, marginTop: 3, textTransform: "uppercase" }}>{item.label}</div>
                      </div>
                    ))}
                  </div>

                  <div style={{ display: "grid", gridTemplateColumns: "1.05fr 1.2fr", gap: 12 }}>
                    <div style={{ minWidth: 0 }}>
                      <div style={{ fontSize: 9, color: C.accent, fontWeight: 700, marginBottom: 6 }}>
                        Shared temporary plan
                      </div>
                      <div style={{ border: `1px solid ${C.border}`, borderRadius: 6, overflow: "hidden" }}>
                        {lowered.temporaries.map((temp, index) => (
                          <div key={temp.temp} style={{
                            display: "grid", gridTemplateColumns: "44px 1fr 56px",
                            gap: 8, alignItems: "center", padding: "6px 8px",
                            borderBottom: index < lowered.temporaries.length - 1 ? `1px solid ${C.border}` : "none",
                            background: index % 2 === 0 ? "rgba(255,255,255,0.01)" : "transparent",
                          }}>
                            <span style={{ fontSize: 10, color: C.blue, fontFamily: "'Space Mono',monospace" }}>
                              {temp.temp}
                            </span>
                            <span style={{
                              fontSize: 9, color: C.text, fontFamily: "'Space Mono',monospace",
                              overflowWrap: "anywhere",
                            }}>
                              {temp.source}
                            </span>
                            <span style={{ fontSize: 8, color: C.muted, textAlign: "right" }}>
                              reuse {temp.reuseCount}
                            </span>
                          </div>
                        ))}
                      </div>
                      <div style={{ fontSize: 9, color: C.muted, lineHeight: 1.6, marginTop: 8 }}>
                        {lowered.note}
                      </div>
                    </div>

                    <div style={{ minWidth: 0 }}>
                      <div style={{ display: "flex", justifyContent: "space-between", gap: 8, marginBottom: 6 }}>
                        <div style={{ fontSize: 9, color: C.accent, fontWeight: 700 }}>Lowered code export</div>
                        <div style={{ display: "flex", gap: 5 }}>
                          <ModeButton active={codeLang === "python"} onClick={() => setCodeLang("python")}>Python</ModeButton>
                          <ModeButton active={codeLang === "javascript"} onClick={() => setCodeLang("javascript")}>JS</ModeButton>
                        </div>
                      </div>
                      <pre style={{
                        margin: 0, minHeight: 190, maxHeight: 260, overflow: "auto",
                        background: "#06070d", border: `1px solid ${C.border}`, borderRadius: 6,
                        color: C.text, padding: 10, fontSize: 9, lineHeight: 1.55,
                      }}>
                        {codeLang === "python" ? lowered.pythonSource : lowered.javascriptSource}
                      </pre>
                      <div style={{ display: "flex", justifyContent: "space-between", gap: 8, marginTop: 8 }}>
                        <span style={{ fontSize: 8, color: C.muted, lineHeight: 1.5 }}>
                          Canonical row costs are unchanged; this is expression-level sharing.
                        </span>
                        <button onClick={copyLoweredSource} style={{
                          fontSize: 10, padding: "6px 10px", borderRadius: 4, cursor: "pointer",
                          background: copiedLowering ? "rgba(94,196,122,0.12)" : "rgba(255,255,255,0.04)",
                          border: `1px solid ${copiedLowering ? C.green : C.border}`,
                          color: copiedLowering ? C.green : C.muted,
                          whiteSpace: "nowrap",
                        }}>
                          {copiedLowering ? "copied ✓" : "copy code"}
                        </button>
                      </div>
                    </div>
                  </div>
                </>
              ) : (
                <div style={{
                  border: `1px solid rgba(232,160,32,0.28)`, borderRadius: 6,
                  background: "rgba(232,160,32,0.06)", color: C.accent,
                  padding: 10, fontSize: 9, lineHeight: 1.7,
                }}>
                  {lowered.message} CLI path:{" "}
                  <span style={{ fontFamily: "'Space Mono',monospace" }}>
                    PYTHONPATH=python python python/scripts/superbest_dag_lowering.py "&lt;expr&gt;"
                  </span>
                </div>
              )}
            </div>
          )}

          {/* Methodology */}
          <div style={{
            background: C.surface, border: `1px solid ${C.border}`, borderRadius: 8,
            padding: 14, marginTop: 12, fontSize: 9, color: C.muted, lineHeight: 1.8,
          }}>
            <span style={{ color: C.accent, fontWeight: 700 }}>Methodology:</span>{" "}
            Node counts are operator-graph sizes — the number of EML-family gate evaluations.
            EML baseline uses the single best operator per operation (pure EML, no routing).
            SuperBEST routes each operation to its canonical v5.3 construction: exp/ln stay 1n,
            add/sub/neg are 2n guarded mixed routes, mul/pow/sqrt/recip are 1n positive-domain routes,
            and div is 2n in the full positive-domain tree. All displayed costs are integer node counts,
            not timing estimates. DAG mode is expression-level sharing only: it does not change canonical
            row costs. div_positive = 2n full tree; mul_positive = 1n positive-domain only; general-domain
            caveats remain in force.
          </div>
        </>
      )}
    </div>
  );
}
