import { useState, useEffect, useMemo } from "react";
import { layoutTree, bfsOrder } from "./eml_tree.js";

const HSPACE = 54;
const VSPACE = 80;
const R = 20; // node radius
const PAD = 28; // padding around tree edges

const COLORS = {
  eml: { fill: "#0d0e1c", stroke: "#e8a020" },
  lit: { fill: "#12142a", stroke: "#6ab0f5" },
  edge: "#2a2d4a",
  edgeRevealed: "#3a3d5a",
  label: { eml: "#e8a020", lit: "#6ab0f5" },
  counter: "#cdd0e0",
  dim: "#2a2d4a",
};

/**
 * Animated SVG renderer for EML expression trees.
 *
 * Props:
 *   root      — tree node from eml_tree.js
 *   animKey   — change this value to restart the animation
 */
export default function TreeViz({ root, animKey }) {
  const { coords, bfsNodes, width, height } = useMemo(() => {
    const c = layoutTree(root, HSPACE, VSPACE);
    const nodes = bfsOrder(root);
    const xs = [...c.values()].map((v) => v.x);
    const ys = [...c.values()].map((v) => v.y);
    const minX = Math.min(...xs);
    const maxX = Math.max(...xs);
    const maxY = Math.max(...ys);
    // Shift all coords so minX lands at PAD
    const shift = PAD - minX + R;
    for (const v of c.values()) v.x += shift;
    return {
      coords: c,
      bfsNodes: nodes,
      width: maxX - minX + 2 * PAD + 2 * R,
      height: maxY + 2 * PAD + 2 * R,
    };
  }, [root]);

  const total = bfsNodes.length;
  const [revealed, setRevealed] = useState(0);

  // Restart animation whenever animKey changes
  useEffect(() => {
    setRevealed(0);
  }, [animKey]);

  // Advance one node every 80ms
  useEffect(() => {
    if (revealed >= total) return;
    const t = setTimeout(() => setRevealed((r) => r + 1), 80);
    return () => clearTimeout(t);
  }, [revealed, total]);

  // Build a set of revealed node objects for O(1) lookup
  const revealedSet = useMemo(
    () => new Set(bfsNodes.slice(0, revealed)),
    [bfsNodes, revealed]
  );

  // Collect edges: [parentNode, childNode] pairs
  const edges = useMemo(() => {
    const result = [];
    for (const node of bfsNodes) {
      if (node.tag === "eml") {
        if (node.left) result.push([node, node.left]);
        if (node.right) result.push([node, node.right]);
      }
    }
    return result;
  }, [bfsNodes]);

  return (
    <svg
      viewBox={`0 0 ${width} ${height}`}
      width="100%"
      style={{ display: "block", maxHeight: "65vh", overflow: "visible" }}
      aria-label="EML expression tree"
    >
      {/* Edges — drawn behind nodes */}
      {edges.map(([parent, child], i) => {
        const p = coords.get(parent);
        const c = coords.get(child);
        const show = revealedSet.has(parent) && revealedSet.has(child);
        return (
          <line
            key={i}
            x1={p.x}
            y1={p.y}
            x2={c.x}
            y2={c.y}
            stroke={show ? COLORS.edgeRevealed : COLORS.dim}
            strokeWidth={show ? 1.5 : 0.5}
            strokeOpacity={show ? 1 : 0.15}
            style={{ transition: "stroke-opacity 0.15s, stroke-width 0.15s" }}
          />
        );
      })}

      {/* Nodes */}
      {bfsNodes.map((node, i) => {
        const { x, y } = coords.get(node);
        const isEml = node.tag === "eml";
        const show = revealedSet.has(node);
        const colors = isEml ? COLORS.eml : COLORS.lit;
        const label = isEml ? "eml" : node.label;
        const fontSize = isEml ? 9 : label.length > 3 ? 8 : 10;

        return (
          <g
            key={i}
            style={{
              opacity: show ? 1 : 0,
              transition: "opacity 0.15s",
            }}
          >
            <circle
              cx={x}
              cy={y}
              r={R}
              fill={colors.fill}
              stroke={colors.stroke}
              strokeWidth={1.5}
            />
            <text
              x={x}
              y={y}
              textAnchor="middle"
              dominantBaseline="central"
              fontSize={fontSize}
              fontFamily="Space Mono, monospace"
              fill={isEml ? COLORS.label.eml : COLORS.label.lit}
              style={{ userSelect: "none" }}
            >
              {label}
            </text>
          </g>
        );
      })}
    </svg>
  );
}
