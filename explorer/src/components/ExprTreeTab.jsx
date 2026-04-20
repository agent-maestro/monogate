// ExprTreeTab.jsx — expression tree visualizer with SuperBEST Optimize
// Optimize button, side-by-side comparison, export-as-code, shareable URL.

import { useState, useCallback, useMemo, useEffect } from "react";
import { buildAST, OP_SOURCE_BEST, NODE_COSTS, ParseError, evalExpr } from "../calc-engine.js";
import { exportCode, COSTS as SB_COSTS, EML_COSTS, savings as sbSavings } from "../superbest.js";

const C = {
  bg: "#07080f", surface: "#0d0e1c", border: "#191b2e",
  text: "#cdd0e0", muted: "#4e5168", accent: "#e8a020",
  green: "#5ec47a", blue: "#6ab0f5", red: "#e05060",
};

const FAMILY_COLOR = {
  EXL:  "#f59e0b",
  EDL:  "#2dd4bf",
  EML:  "#7c6ff7",
  EAL:  "#5ec47a",
  leaf: "#4e5168",
};

const FAMILY_BG = {
  EXL:  "rgba(245,158,11,0.12)",
  EDL:  "rgba(45,212,191,0.10)",
  EML:  "rgba(124,111,247,0.13)",
  EAL:  "rgba(94,196,122,0.10)",
  leaf: "rgba(78,81,104,0.13)",
};

const PRESETS = [
  "pow(x,3)",
  "mul(x,2)",
  "div(10,x)",
  "neg(x)",
  "sin(x)+cos(x)",
  "exp(-x)*sin(x)",
];

const EXPORT_LANGS = ["python", "js", "glsl", "hlsl", "rust", "c"];

// ── node helpers ──────────────────────────────────────────────────────────────

function opKey(node) {
  if (node.type === "call") return node.fn;
  return node.type;
}

function nodeFamily(node) {
  if (node.type === "num" || node.type === "var") return "leaf";
  return OP_SOURCE_BEST[opKey(node)] ?? "EML";
}

function nodeCost(node) {
  if (node.type === "num" || node.type === "var") return null;
  return NODE_COSTS.best[opKey(node)] ?? null;
}

function nodeLabel(node) {
  if (node.type === "var") return "x";
  if (node.type === "num") {
    const s = String(node.v);
    return s.length > 5 ? s.slice(0, 5) : s;
  }
  const SYM = { add: "+", sub: "−", mul: "×", div: "÷", pow: "^", neg: "−u" };
  if (node.type === "call") return node.fn;
  return SYM[node.type] ?? node.type;
}

function nodeChildren(node) {
  if (node.type === "num" || node.type === "var") return [];
  if (node.type === "neg") return [node.arg];
  if (node.type === "call") return node.arg2 ? [node.arg1, node.arg2] : [node.arg1];
  return [node.left, node.right];
}

// ── collect ops from AST ──────────────────────────────────────────────────────

function collectOps(ast) {
  const ops = {};
  function walk(node) {
    if (!node || node.type === "num" || node.type === "var") return;
    const k = opKey(node);
    ops[k] = (ops[k] ?? 0) + 1;
    nodeChildren(node).forEach(walk);
  }
  walk(ast);
  return ops;
}

// ── SVG layout ────────────────────────────────────────────────────────────────

const HGAP = 56;
const VGAP = 68;
const R    = 20;

function subtreeWidth(node) {
  const ch = nodeChildren(node);
  if (ch.length === 0) return 1;
  return ch.reduce((s, c) => s + subtreeWidth(c), 0);
}

function layout(root) {
  let idCounter = 0;
  const nodes = [], edges = [];

  function place(node, leftSlot, depth) {
    const id = idCounter++;
    const w  = subtreeWidth(node);
    const cx = (leftSlot + w / 2) * HGAP;
    const cy = depth * VGAP + R + 10;
    nodes.push({ node, cx, cy, id, family: nodeFamily(node), cost: nodeCost(node), label: nodeLabel(node) });
    let childLeft = leftSlot;
    for (const ch of nodeChildren(node)) {
      const chId = idCounter;
      place(ch, childLeft, depth + 1);
      edges.push({ parentId: id, childId: chId, x1: cx, y1: cy });
      childLeft += subtreeWidth(ch);
    }
  }

  place(root, 0, 0);

  const nodeById = Object.fromEntries(nodes.map(n => [n.id, n]));
  const edgesWithCoords = edges.map(e => ({
    ...e,
    x1: nodeById[e.parentId].cx, y1: nodeById[e.parentId].cy,
    x2: nodeById[e.childId]?.cx ?? 0, y2: nodeById[e.childId]?.cy ?? 0,
  }));

  const maxX = Math.max(...nodes.map(n => n.cx)) + R + 10;
  const maxY = Math.max(...nodes.map(n => n.cy)) + R + 10;
  return { nodes, edges: edgesWithCoords, width: Math.max(maxX, 200), height: Math.max(maxY, 100) };
}

// ── TreeSVG sub-component ─────────────────────────────────────────────────────

function TreeSVG({ tree, selected, onSelect, colorMode, subtreeIds }) {
  return (
    <div style={{ background: C.surface, border: `1px solid ${C.border}`, borderRadius: 8, padding: 12, overflowX: "auto" }}>
      <svg
        viewBox={`0 0 ${tree.width} ${tree.height}`}
        width={Math.min(tree.width, 620)}
        height={tree.height}
        style={{ display: "block", overflow: "visible" }}
      >
        {tree.edges.map((e, i) => {
          const inSub = subtreeIds?.has(e.parentId) && subtreeIds?.has(e.childId);
          return (
            <line key={i} x1={e.x1} y1={e.y1} x2={e.x2} y2={e.y2}
              stroke={inSub ? "#5ec47a" : "#2a2d44"} strokeWidth={inSub ? 2 : 1.5} />
          );
        })}
        {tree.nodes.map(n => {
          const isSelected = n.id === selected;
          const inSub = subtreeIds?.has(n.id);
          const family = colorMode === "best" ? n.family : "EML";
          const fill = FAMILY_BG[family] ?? FAMILY_BG.leaf;
          const stroke = isSelected ? "#5ec47a" : inSub ? FAMILY_COLOR[family] : (FAMILY_COLOR[family] ?? "#4e5168") + "88";
          const strokeW = isSelected ? 2.5 : inSub ? 2 : 1.5;
          const textCol = isSelected ? "#fff" : FAMILY_COLOR[family] ?? "#4e5168";
          return (
            <g key={n.id} style={{ cursor: "pointer" }} onClick={() => onSelect(n.id === selected ? null : n.id)}>
              <title>{`${opKey(n.node)} · ${n.family} · ${n.cost ?? "—"}n`}</title>
              <circle cx={n.cx} cy={n.cy} r={R} fill={fill} stroke={stroke} strokeWidth={strokeW} />
              <text x={n.cx} y={n.cy - 3} textAnchor="middle" dominantBaseline="middle"
                fontSize={n.label.length > 3 ? 8 : 10} fill={textCol}
                fontFamily="'Space Mono',monospace" fontWeight={isSelected ? 700 : 500}>
                {n.label}
              </text>
              {n.cost != null && (
                <text x={n.cx} y={n.cy + 10} textAnchor="middle" dominantBaseline="middle"
                  fontSize={7} fill={textCol + "99"} fontFamily="'Space Mono',monospace">
                  {n.cost}n
                </text>
              )}
            </g>
          );
        })}
      </svg>
    </div>
  );
}

// ── Export panel ──────────────────────────────────────────────────────────────

function ExportPanel({ expr, ast }) {
  const [lang, setLang] = useState("python");
  const [copied, setCopied] = useState(false);

  // Detect primary op in AST (first non-trivial op)
  const primaryOp = useMemo(() => {
    if (!ast) return null;
    const k = opKey(ast);
    if (k === "num" || k === "var") return null;
    return k;
  }, [ast]);

  const code = useMemo(() => {
    if (!primaryOp) return `// Type an expression above and click BUILD, then OPTIMIZE.\n// Supported operations: mul, sub, neg, div, pow, add, ln, exp, recip`;
    return exportCode(primaryOp, lang);
  }, [primaryOp, lang]);

  function copy() {
    navigator.clipboard.writeText(code).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  }

  return (
    <div style={{ background: C.surface, border: `1px solid ${C.border}`, borderRadius: 8, padding: 14, marginTop: 12 }}>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 10 }}>
        <span style={{ fontSize: 9, color: C.muted, textTransform: "uppercase", letterSpacing: "0.08em" }}>
          Export as Code
        </span>
        <div style={{ display: "flex", gap: 4, flexWrap: "wrap" }}>
          {EXPORT_LANGS.map(l => (
            <button key={l} onClick={() => setLang(l)} style={{
              fontSize: 9, padding: "2px 8px", borderRadius: 3,
              background: lang === l ? "rgba(232,160,32,0.15)" : "transparent",
              border: `1px solid ${lang === l ? C.accent : C.border}`,
              color: lang === l ? C.accent : C.muted, cursor: "pointer",
            }}>{l}</button>
          ))}
          <button onClick={copy} style={{
            fontSize: 9, padding: "2px 10px", borderRadius: 3, marginLeft: 4,
            background: copied ? "rgba(94,196,122,0.15)" : "rgba(255,255,255,0.04)",
            border: `1px solid ${copied ? C.green : C.border}`,
            color: copied ? C.green : C.muted, cursor: "pointer",
          }}>
            {copied ? "copied ✓" : "copy"}
          </button>
        </div>
      </div>
      <pre style={{
        background: C.bg, border: `1px solid ${C.border}`, borderRadius: 6,
        padding: "10px 12px", fontSize: 9, color: C.text, overflowX: "auto",
        margin: 0, lineHeight: 1.7, fontFamily: "'Space Mono', monospace",
        maxHeight: 220, overflowY: "auto",
      }}>
        {code}
      </pre>
      <div style={{ fontSize: 8, color: C.muted, marginTop: 6 }}>
        Drop-in production code. Domain restriction shown in comments where applicable.
        Patent covers the routing method; this code is free to use.
      </div>
    </div>
  );
}

// ── Main component ────────────────────────────────────────────────────────────

export default function ExprTreeTab() {
  // Read initial expr from URL params
  const initExpr = (() => {
    const p = new URLSearchParams(window.location.search);
    return p.get("expr") ?? "pow(x,3)";
  })();

  const [expr,       setExpr]       = useState(initExpr);
  const [input,      setInput]      = useState(initExpr);
  const [selected,   setSelected]   = useState(null);
  const [colorMode,  setColorMode]  = useState("best");
  const [error,      setError]      = useState(null);
  const [optimized,  setOptimized]  = useState(false);
  const [showExport, setShowExport] = useState(false);
  const [urlCopied,  setUrlCopied]  = useState(false);

  const ast = useMemo(() => {
    try { setError(null); return buildAST(expr); }
    catch (e) { setError(e.message ?? "Parse error"); return null; }
  }, [expr]);

  const tree = useMemo(() => ast ? layout(ast) : null, [ast]);

  const subtreeIds = useMemo(() => {
    if (!tree || selected === null) return new Set();
    const edgesByParent = {};
    for (const e of tree.edges) {
      if (!edgesByParent[e.parentId]) edgesByParent[e.parentId] = [];
      edgesByParent[e.parentId].push(e.childId);
    }
    const ids = new Set();
    const queue = [selected];
    while (queue.length) {
      const id = queue.shift();
      ids.add(id);
      for (const ch of (edgesByParent[id] ?? [])) queue.push(ch);
    }
    return ids;
  }, [tree, selected]);

  const stats = useMemo(() => {
    if (!expr.trim() || !ast) return null;
    const ops = collectOps(ast);
    let bestTotal = 0, emlTotal = 0;
    for (const [op, count] of Object.entries(ops)) {
      bestTotal += (SB_COSTS[op] ?? 1) * count;
      emlTotal  += (EML_COSTS[op] ?? 1) * count;
    }
    return { bestNodes: bestTotal, emlNodes: emlTotal, savings: sbSavings(emlTotal, bestTotal) };
  }, [expr, ast]);

  const build = useCallback(() => {
    setSelected(null);
    setOptimized(false);
    setExpr(input.trim());
  }, [input]);

  const loadPreset = useCallback((p) => {
    setInput(p); setSelected(null); setOptimized(false); setExpr(p);
  }, []);

  function handleOptimize() {
    setOptimized(true);
    setShowExport(true);
  }

  function copyShareUrl() {
    const url = `${window.location.origin}/explorer?tab=tree&expr=${encodeURIComponent(expr)}`;
    navigator.clipboard.writeText(url).then(() => {
      setUrlCopied(true);
      setTimeout(() => setUrlCopied(false), 2000);
    });
  }

  return (
    <div style={{ color: C.text }}>
      {/* Header */}
      <div style={{ fontSize: 10, color: C.muted, marginBottom: 14, lineHeight: 1.8 }}>
        Type a math expression and see its{" "}
        <span style={{ color: C.accent }}>expression tree</span>.
        Nodes are colored by SuperBEST operator family. Click{" "}
        <span style={{ color: C.green }}>OPTIMIZE</span> to see the savings.
      </div>

      {/* Input area */}
      <div style={{ background: C.surface, border: `1px solid ${C.border}`, borderRadius: 8, padding: 16, marginBottom: 12 }}>
        <div style={{ display: "flex", gap: 6, flexWrap: "wrap", marginBottom: 12 }}>
          {PRESETS.map(p => (
            <button key={p} onClick={() => loadPreset(p)} style={{
              fontSize: 10, padding: "4px 10px",
              background: expr === p ? "rgba(232,160,32,0.12)" : "rgba(255,255,255,0.04)",
              border: `1px solid ${expr === p ? C.accent : C.border}`,
              color: expr === p ? C.accent : C.muted, borderRadius: 4, cursor: "pointer",
            }}>{p}</button>
          ))}
        </div>
        <div style={{ display: "flex", gap: 8 }}>
          <input
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => e.key === "Enter" && build()}
            placeholder="e.g. pow(x,3)"
            style={{
              flex: 1, background: C.bg, border: `1px solid ${C.border}`,
              borderRadius: 4, color: C.accent, padding: "9px 12px",
              fontSize: 13, fontFamily: "'Space Mono',monospace",
            }}
          />
          <button onClick={build} style={{
            padding: "9px 20px", fontSize: 11, fontWeight: 700,
            background: "rgba(232,160,32,0.15)", border: `1px solid ${C.accent}`,
            color: C.accent, borderRadius: 4, letterSpacing: "0.04em", cursor: "pointer",
          }}>BUILD</button>
          <button onClick={handleOptimize} disabled={!ast} style={{
            padding: "9px 20px", fontSize: 11, fontWeight: 700,
            background: optimized ? "rgba(94,196,122,0.15)" : "rgba(94,196,122,0.08)",
            border: `1px solid ${optimized ? C.green : "rgba(94,196,122,0.4)"}`,
            color: optimized ? C.green : "rgba(94,196,122,0.7)",
            borderRadius: 4, letterSpacing: "0.04em", cursor: ast ? "pointer" : "default",
            opacity: ast ? 1 : 0.4,
          }}>
            {optimized ? "OPTIMIZED ✓" : "OPTIMIZE"}
          </button>
        </div>
      </div>

      {/* Error */}
      {error && (
        <div style={{
          background: "rgba(224,80,96,0.08)", border: "1px solid #e05060",
          borderRadius: 6, padding: "10px 14px", marginBottom: 12,
          fontSize: 11, color: "#e05060",
        }}>
          {error}
        </div>
      )}

      {tree && !error && (
        <>
          {/* SuperBEST badge (shown after optimize) */}
          {optimized && stats && (
            <div style={{
              display: "flex", alignItems: "center", justifyContent: "space-between",
              background: "rgba(94,196,122,0.07)", border: "1px solid rgba(94,196,122,0.25)",
              borderRadius: 8, padding: "10px 14px", marginBottom: 12,
            }}>
              <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                <span style={{
                  fontSize: 10, fontWeight: 700, color: C.green,
                  background: "rgba(94,196,122,0.15)", border: "1px solid rgba(94,196,122,0.3)",
                  borderRadius: 10, padding: "2px 10px",
                }}>SuperBEST</span>
                <span style={{ fontSize: 12, color: C.text }}>
                  <span style={{ color: C.muted }}>{stats.emlNodes}n EML</span>
                  {" → "}
                  <span style={{ color: C.green, fontWeight: 700 }}>{stats.bestNodes}n SuperBEST</span>
                  {stats.savings > 0 && (
                    <span style={{ marginLeft: 8, fontSize: 10, color: C.green }}>
                      {stats.savings}% fewer nodes
                    </span>
                  )}
                </span>
              </div>
              <div style={{ display: "flex", gap: 6 }}>
                <button onClick={() => setShowExport(v => !v)} style={{
                  fontSize: 9, padding: "4px 10px", borderRadius: 4, cursor: "pointer",
                  background: showExport ? "rgba(106,176,245,0.15)" : "transparent",
                  border: `1px solid ${showExport ? C.blue : C.border}`,
                  color: showExport ? C.blue : C.muted,
                }}>
                  {showExport ? "hide export" : "export code"}
                </button>
                <button onClick={copyShareUrl} style={{
                  fontSize: 9, padding: "4px 10px", borderRadius: 4, cursor: "pointer",
                  background: urlCopied ? "rgba(94,196,122,0.15)" : "transparent",
                  border: `1px solid ${urlCopied ? C.green : C.border}`,
                  color: urlCopied ? C.green : C.muted,
                }}>
                  {urlCopied ? "link copied ✓" : "share link"}
                </button>
              </div>
            </div>
          )}

          <div style={{ display: "grid", gridTemplateColumns: "1fr 260px", gap: 12 }}>
            {/* SVG panel */}
            <div>
              {/* Stats + mode toggle */}
              <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 10 }}>
                {stats && (
                  <>
                    <span style={{ fontSize: 11, color: C.muted }}>
                      SuperBEST: <span style={{ color: C.accent }}>{stats.bestNodes}n</span>
                    </span>
                    <span style={{ fontSize: 11, color: C.muted }}>
                      EML: <span style={{ color: C.muted }}>{stats.emlNodes}n</span>
                    </span>
                    {stats.savings > 0 && !optimized && (
                      <span style={{
                        fontSize: 10, background: "rgba(94,196,122,0.12)",
                        border: "1px solid rgba(94,196,122,0.3)", color: C.green,
                        borderRadius: 10, padding: "2px 8px",
                      }}>
                        {stats.savings}% fewer nodes
                      </span>
                    )}
                  </>
                )}
                <div style={{ marginLeft: "auto", display: "flex", gap: 6 }}>
                  {["best", "mono"].map(m => (
                    <button key={m} onClick={() => setColorMode(m)} style={{
                      fontSize: 10, padding: "3px 10px",
                      background: colorMode === m ? "rgba(232,160,32,0.12)" : "transparent",
                      border: `1px solid ${colorMode === m ? C.accent : C.border}`,
                      color: colorMode === m ? C.accent : C.muted,
                      borderRadius: 4, cursor: "pointer",
                    }}>
                      {m === "best" ? "BEST color" : "mono"}
                    </button>
                  ))}
                </div>
              </div>

              {/* Tree label */}
              {optimized && (
                <div style={{ fontSize: 9, color: C.muted, marginBottom: 4, textTransform: "uppercase", letterSpacing: "0.06em" }}>
                  SuperBEST routing — operator families shown by color
                </div>
              )}

              <TreeSVG
                tree={tree}
                selected={selected}
                onSelect={setSelected}
                colorMode={colorMode}
                subtreeIds={subtreeIds}
              />

              {/* Legend */}
              <div style={{ display: "flex", gap: 14, marginTop: 8, flexWrap: "wrap" }}>
                {Object.entries(FAMILY_COLOR).map(([k, col]) => (
                  <span key={k} style={{ fontSize: 9, color: C.muted, display: "flex", alignItems: "center", gap: 5 }}>
                    <span style={{ width: 10, height: 10, borderRadius: "50%", background: col, display: "inline-block" }} />
                    {k === "leaf" ? "terminal" : k}
                  </span>
                ))}
              </div>
            </div>

            {/* Info panel */}
            <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
              {/* Node inspector */}
              <div style={{ background: C.surface, border: `1px solid ${C.border}`, borderRadius: 8, padding: 14 }}>
                <div style={{ fontSize: 9, color: C.muted, textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: 10 }}>
                  Node Inspector
                </div>
                {selected !== null && tree ? (() => {
                  const selNode = tree.nodes.find(n => n.id === selected);
                  return selNode ? (
                    <>
                      <div style={{ fontSize: 18, fontWeight: 700, color: FAMILY_COLOR[selNode.family] ?? C.muted, marginBottom: 6 }}>
                        {selNode.label}
                      </div>
                      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8 }}>
                        {[
                          { label: "family", value: selNode.family },
                          { label: "cost", value: selNode.cost != null ? `${selNode.cost} nodes` : "—" },
                          { label: "type", value: selNode.node.type },
                          { label: "subtree", value: `${subtreeIds.size} nodes` },
                        ].map(({ label, value }) => (
                          <div key={label} style={{ background: C.bg, borderRadius: 5, padding: "6px 8px" }}>
                            <div style={{ fontSize: 8, color: C.muted, marginBottom: 3 }}>{label}</div>
                            <div style={{ fontSize: 11, color: C.text }}>{value}</div>
                          </div>
                        ))}
                      </div>
                      <div style={{ marginTop: 10, fontSize: 9, color: C.muted }}>
                        Subtree highlighted in green. Click again to deselect.
                      </div>
                    </>
                  ) : null;
                })() : (
                  <div style={{ fontSize: 10, color: C.muted }}>
                    Click any node to inspect it and highlight its subtree.
                  </div>
                )}
              </div>

              {/* BEST routing table */}
              <div style={{ background: C.surface, border: `1px solid ${C.border}`, borderRadius: 8, padding: 14 }}>
                <div style={{ fontSize: 9, color: C.muted, textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: 10 }}>
                  SuperBEST Routing
                </div>
                {[
                  { family: "EXL", ops: "ln, pow, mul, neg, sqrt, sin, cos", note: "exp×log — 1–3n" },
                  { family: "EML", ops: "exp, sub",                          note: "exp−log — 1–3n" },
                  { family: "EAL", ops: "add",                                note: "exp+log — 3n" },
                  { family: "EDL", ops: "div, recip",                         note: "exp÷log — 1–2n" },
                ].map(({ family, ops, note }) => (
                  <div key={family} style={{ display: "flex", alignItems: "flex-start", gap: 8, marginBottom: 8 }}>
                    <span style={{
                      width: 28, fontSize: 9, fontWeight: 700, color: FAMILY_COLOR[family],
                      background: FAMILY_BG[family], border: `1px solid ${FAMILY_COLOR[family]}44`,
                      borderRadius: 3, padding: "2px 4px", textAlign: "center", flexShrink: 0,
                    }}>{family}</span>
                    <div>
                      <div style={{ fontSize: 10, color: C.text }}>{ops}</div>
                      <div style={{ fontSize: 8, color: C.muted }}>{note}</div>
                    </div>
                  </div>
                ))}
              </div>

              {/* Savings summary (when optimized) */}
              {optimized && stats && stats.savings > 0 && (
                <div style={{
                  background: "rgba(94,196,122,0.06)", border: "1px solid rgba(94,196,122,0.2)",
                  borderRadius: 8, padding: 14,
                }}>
                  <div style={{ fontSize: 9, color: C.green, textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: 8 }}>
                    Savings Detail
                  </div>
                  {(() => {
                    const ops = collectOps(ast);
                    return Object.entries(ops).map(([op, cnt]) => {
                      const eml = (EML_COSTS[op] ?? 1) * cnt;
                      const best = (SB_COSTS[op] ?? 1) * cnt;
                      const pct = sbSavings(eml, best);
                      return (
                        <div key={op} style={{ display: "flex", justifyContent: "space-between", marginBottom: 4 }}>
                          <span style={{ fontSize: 9, color: C.muted }}>{op}×{cnt}</span>
                          <span style={{ fontSize: 9 }}>
                            <span style={{ color: C.muted }}>{eml}n</span>
                            {" → "}
                            <span style={{ color: C.green }}>{best}n</span>
                            {pct > 0 && <span style={{ color: C.green, marginLeft: 4 }}>−{pct}%</span>}
                          </span>
                        </div>
                      );
                    });
                  })()}
                </div>
              )}
            </div>
          </div>

          {/* Export panel */}
          {showExport && <ExportPanel expr={expr} ast={ast} />}
        </>
      )}

      {!tree && !error && (
        <div style={{
          background: C.surface, border: `1px solid ${C.border}`,
          borderRadius: 8, padding: "40px 16px", textAlign: "center",
        }}>
          <div style={{ fontSize: 11, color: C.muted }}>
            Type a math expression above and press <span style={{ color: C.accent }}>BUILD</span>.
          </div>
          <div style={{ marginTop: 8, fontSize: 9, color: C.muted }}>
            Then press <span style={{ color: C.green }}>OPTIMIZE</span> to see SuperBEST routing.
          </div>
        </div>
      )}
    </div>
  );
}
