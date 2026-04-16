// explorer/src/components/ExprTreeTab.jsx
// Natural-math expression tree visualizer with BEST operator-family coloring.
// Distinct from the "tree" tab (which shows EML-syntax trees).

import { useState, useCallback, useMemo } from "react";
import { buildAST, OP_SOURCE_BEST, NODE_COSTS, ParseError, evalExpr } from "../calc-engine.js";

const C = {
  bg: "#07080f", surface: "#0d0e1c", border: "#191b2e",
  text: "#cdd0e0", muted: "#4e5168", accent: "#e8a020",
  green: "#5ec47a",
};

const FAMILY_COLOR = {
  EXL:  "#f59e0b",  // amber  — sin, cos, pow, ln, sqrt
  EDL:  "#2dd4bf",  // teal   — mul, div, neg, recip
  EML:  "#7c6ff7",  // indigo — add, sub, exp
  leaf: "#4e5168",  // gray   — num / var terminals
};

const FAMILY_BG = {
  EXL:  "rgba(245,158,11,0.12)",
  EDL:  "rgba(45,212,191,0.10)",
  EML:  "rgba(124,111,247,0.13)",
  leaf: "rgba(78,81,104,0.13)",
};

const PRESETS = [
  "sin(x)+cos(x)",
  "sin(x)*cos(x)",
  "pow(x,3)+2*x",
  "exp(-x)*sin(x)",
  "ln(x+1)/x",
];

// ── node helpers ─────────────────────────────────────────────────────────────

function opKey(node) {
  if (node.type === "call") return node.fn;
  return node.type;  // add, sub, mul, div, pow, neg
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

// ── SVG layout ───────────────────────────────────────────────────────────────

const HGAP = 56;  // horizontal slot width
const VGAP = 68;  // vertical level height
const R    = 20;  // node radius

function subtreeWidth(node) {
  const ch = nodeChildren(node);
  if (ch.length === 0) return 1;
  return ch.reduce((s, c) => s + subtreeWidth(c), 0);
}

// Returns { nodes: [{node,cx,cy,id}], edges: [{x1,y1,x2,y2,childId}] }
function layout(root) {
  let idCounter = 0;
  const nodes = [];
  const edges = [];

  function place(node, leftSlot, depth) {
    const id = idCounter++;
    const w  = subtreeWidth(node);
    const cx = (leftSlot + w / 2) * HGAP;
    const cy = depth * VGAP + R + 10;

    nodes.push({ node, cx, cy, id, family: nodeFamily(node), cost: nodeCost(node), label: nodeLabel(node) });

    let childLeft = leftSlot;
    for (const ch of nodeChildren(node)) {
      const chW  = subtreeWidth(ch);
      const chId = idCounter;  // will be assigned next call
      place(ch, childLeft, depth + 1);
      const chNode = nodes[nodes.length - 1 - (nodeChildren(ch).length > 0 ? 0 : 0)];
      // we pushed ch just after this loop step; find it by id
      edges.push({ parentId: id, childId: chId, x1: cx, y1: cy });
      childLeft += chW;
    }
  }

  place(root, 0, 0);

  // Fill in edge y2/x2 from nodes array
  const nodeById = Object.fromEntries(nodes.map(n => [n.id, n]));
  const edgesWithCoords = edges.map(e => ({
    ...e,
    x1: nodeById[e.parentId].cx,
    y1: nodeById[e.parentId].cy,
    x2: nodeById[e.childId]?.cx ?? 0,
    y2: nodeById[e.childId]?.cy ?? 0,
  }));

  const maxX = Math.max(...nodes.map(n => n.cx)) + R + 10;
  const maxY = Math.max(...nodes.map(n => n.cy)) + R + 10;

  return { nodes, edges: edgesWithCoords, width: Math.max(maxX, 200), height: Math.max(maxY, 100) };
}

// ── component ─────────────────────────────────────────────────────────────────

export default function ExprTreeTab() {
  const [expr,     setExpr]     = useState("sin(x)+cos(x)");
  const [input,    setInput]    = useState("sin(x)+cos(x)");
  const [selected, setSelected] = useState(null);   // selected node id
  const [colorMode, setColorMode] = useState("best"); // "best" | "mono"
  const [error,    setError]    = useState(null);

  const ast = useMemo(() => {
    try {
      setError(null);
      return buildAST(expr);
    } catch (e) {
      setError(e.message ?? "Parse error");
      return null;
    }
  }, [expr]);

  const tree = useMemo(() => ast ? layout(ast) : null, [ast]);

  // Collect all descendant ids of a node (for subtree highlight)
  const subtreeIds = useMemo(() => {
    if (!tree || selected === null) return new Set();
    const nodeById = Object.fromEntries(tree.nodes.map(n => [n.id, n]));
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

  const selectedNode = tree?.nodes.find(n => n.id === selected) ?? null;

  // Node stats
  const stats = useMemo(() => {
    if (!expr.trim()) return null;
    const best = evalExpr(expr, 1.0, "best");
    const eml  = evalExpr(expr, 1.0, "eml");
    if (!best || best.error) return null;
    return {
      bestNodes: best.totalNodes,
      emlNodes:  eml?.totalNodes ?? null,
      savings:   eml?.totalNodes ? Math.round((1 - best.totalNodes / eml.totalNodes) * 100) : null,
    };
  }, [expr]);

  const build = useCallback(() => {
    setSelected(null);
    setExpr(input.trim());
  }, [input]);

  const loadPreset = useCallback((p) => {
    setInput(p);
    setSelected(null);
    setExpr(p);
  }, []);

  return (
    <div style={{ color: C.text }}>
      {/* Header */}
      <div style={{ fontSize: 10, color: C.muted, marginBottom: 14, lineHeight: 1.8 }}>
        Type a math expression and see its{" "}
        <span style={{ color: C.accent }}>expression tree</span>.
        In BEST mode, nodes are colored by which operator family handles each operation.
        Click any node to highlight its subtree.
      </div>

      {/* Preset + input row */}
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
            placeholder="e.g. sin(x)+cos(x)"
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
          }}>
            BUILD
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
        <div style={{ display: "grid", gridTemplateColumns: "1fr 260px", gap: 12 }}>
          {/* SVG panel */}
          <div>
            {/* Stats + mode toggle */}
            <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 10 }}>
              {stats && (
                <>
                  <span style={{ fontSize: 11, color: C.muted }}>
                    BEST: <span style={{ color: C.accent }}>{stats.bestNodes}n</span>
                  </span>
                  {stats.emlNodes && (
                    <span style={{ fontSize: 11, color: C.muted }}>
                      EML: <span style={{ color: C.muted }}>{stats.emlNodes}n</span>
                    </span>
                  )}
                  {stats.savings > 0 && (
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

            {/* SVG */}
            <div style={{ background: C.surface, border: `1px solid ${C.border}`, borderRadius: 8, padding: 12, overflowX: "auto" }}>
              <svg
                viewBox={`0 0 ${tree.width} ${tree.height}`}
                width={Math.min(tree.width, 700)}
                height={tree.height}
                style={{ display: "block", overflow: "visible" }}
              >
                {/* Edges */}
                {tree.edges.map((e, i) => {
                  const inSub = subtreeIds.has(e.parentId) && subtreeIds.has(e.childId);
                  return (
                    <line key={i}
                      x1={e.x1} y1={e.y1} x2={e.x2} y2={e.y2}
                      stroke={inSub ? "#5ec47a" : "#2a2d44"} strokeWidth={inSub ? 2 : 1.5}
                    />
                  );
                })}

                {/* Nodes */}
                {tree.nodes.map(n => {
                  const isSelected = n.id === selected;
                  const inSub = subtreeIds.has(n.id);
                  const family = colorMode === "best" ? n.family : "EML";
                  const fill = FAMILY_BG[family];
                  const stroke = isSelected ? "#5ec47a" : inSub ? FAMILY_COLOR[family] : FAMILY_COLOR[family] + "88";
                  const strokeW = isSelected ? 2.5 : inSub ? 2 : 1.5;
                  const textCol = isSelected ? "#fff" : FAMILY_COLOR[family];

                  const costStr = n.cost != null ? `${n.cost}n` : "";
                  const titleText = n.family === "leaf"
                    ? (n.node.type === "var" ? "variable x" : `literal ${n.node.v}`)
                    : `${opKey(n.node)} · ${n.family} · ${n.cost}n`;

                  return (
                    <g key={n.id} style={{ cursor: "pointer" }}
                      onClick={() => setSelected(n.id === selected ? null : n.id)}>
                      <title>{titleText}</title>
                      <circle cx={n.cx} cy={n.cy} r={R} fill={fill} stroke={stroke} strokeWidth={strokeW} />
                      <text x={n.cx} y={n.cy - 3} textAnchor="middle" dominantBaseline="middle"
                        fontSize={n.label.length > 3 ? 8 : 10} fill={textCol}
                        fontFamily="'Space Mono',monospace" fontWeight={isSelected ? 700 : 500}>
                        {n.label}
                      </text>
                      {costStr && (
                        <text x={n.cx} y={n.cy + 10} textAnchor="middle" dominantBaseline="middle"
                          fontSize={7} fill={textCol + "99"} fontFamily="'Space Mono',monospace">
                          {costStr}
                        </text>
                      )}
                    </g>
                  );
                })}
              </svg>
            </div>

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
            {/* Selected node info */}
            <div style={{ background: C.surface, border: `1px solid ${C.border}`, borderRadius: 8, padding: 14 }}>
              <div style={{ fontSize: 9, color: C.muted, textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: 10 }}>
                Node Inspector
              </div>
              {selectedNode ? (
                <>
                  <div style={{ fontSize: 18, fontWeight: 700, color: FAMILY_COLOR[selectedNode.family], marginBottom: 6 }}>
                    {selectedNode.label}
                  </div>
                  <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8 }}>
                    {[
                      { label: "family", value: selectedNode.family },
                      { label: "cost", value: selectedNode.cost != null ? `${selectedNode.cost} nodes` : "—" },
                      { label: "type", value: selectedNode.node.type },
                      { label: "subtree ids", value: `${subtreeIds.size}` },
                    ].map(({ label, value }) => (
                      <div key={label} style={{ background: C.bg, borderRadius: 5, padding: "6px 8px" }}>
                        <div style={{ fontSize: 8, color: C.muted, marginBottom: 3 }}>{label}</div>
                        <div style={{ fontSize: 11, color: C.text }}>{value}</div>
                      </div>
                    ))}
                  </div>
                  <div style={{ marginTop: 10, fontSize: 9, color: C.muted }}>
                    Subtree is highlighted in green.
                    Click again to deselect.
                  </div>
                </>
              ) : (
                <div style={{ fontSize: 10, color: C.muted }}>
                  Click any node to inspect it and highlight its subtree.
                </div>
              )}
            </div>

            {/* Operator family legend detail */}
            <div style={{ background: C.surface, border: `1px solid ${C.border}`, borderRadius: 8, padding: 14 }}>
              <div style={{ fontSize: 9, color: C.muted, textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: 10 }}>
                BEST Routing
              </div>
              {[
                { family: "EXL", ops: "sin, cos, pow, ln, sqrt", note: "exp×log gate" },
                { family: "EDL", ops: "mul, div, neg, recip",    note: "exp÷log gate" },
                { family: "EML", ops: "add, sub, exp",           note: "exp−log gate (base)" },
              ].map(({ family, ops, note }) => (
                <div key={family} style={{
                  display: "flex", alignItems: "flex-start", gap: 8, marginBottom: 8,
                }}>
                  <span style={{
                    width: 28, fontSize: 9, fontWeight: 700, color: FAMILY_COLOR[family],
                    background: FAMILY_BG[family], border: `1px solid ${FAMILY_COLOR[family]}44`,
                    borderRadius: 3, padding: "2px 4px", textAlign: "center", flexShrink: 0,
                  }}>
                    {family}
                  </span>
                  <div>
                    <div style={{ fontSize: 10, color: C.text }}>{ops}</div>
                    <div style={{ fontSize: 8, color: C.muted }}>{note}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Empty state */}
      {!tree && !error && (
        <div style={{
          background: C.surface, border: `1px solid ${C.border}`,
          borderRadius: 8, padding: "40px 16px", textAlign: "center",
        }}>
          <div style={{ fontSize: 11, color: C.muted }}>
            Type a math expression above and press BUILD.
          </div>
          <div style={{ marginTop: 8, fontSize: 9, color: C.muted }}>
            Try: <span style={{ color: C.accent }}>sin(x)+cos(x)</span>
          </div>
        </div>
      )}
    </div>
  );
}
