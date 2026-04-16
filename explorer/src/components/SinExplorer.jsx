// explorer/src/components/SinExplorer.jsx
// Interactive sin(x) Taylor term explorer with SVG line chart.
// Extends the static 5-row table already in the "best" tab to 2–20 terms
// with a live chart and "→ Calc" navigation buttons.

import { useState, useMemo } from "react";
import { sin_best } from "../eml.js";

const C = {
  bg: "#07080f", surface: "#0d0e1c", border: "#191b2e",
  text: "#cdd0e0", muted: "#4e5168", accent: "#e8a020",
  blue: "#6ab0f5", green: "#5ec47a", red: "#e05060",
};

// ── Data ──────────────────────────────────────────────────────────────────────
// BEST(t) = 9*(t-1), EML(t) = 35*(t-1) — confirmed from existing "best" tab table.
// Max error: scan x ∈ (0, π] in 200 steps using actual sin_best(x, t).
function buildData() {
  return Array.from({ length: 19 }, (_, i) => {
    const t     = i + 2;
    const bestN = 9 * (t - 1);
    const emlN  = 35 * (t - 1);
    let   maxErr = 0;
    for (let j = 1; j <= 200; j++) {
      const x = j * Math.PI / 200;
      try {
        const err = Math.abs(sin_best(x, t) - Math.sin(x));
        if (isFinite(err)) maxErr = Math.max(maxErr, err);
      } catch { maxErr = Infinity; }
    }
    return { t, bestN, emlN, maxErr };
  });
}

// ── Chart constants ───────────────────────────────────────────────────────────
const W = 580, H = 220;
const PAD = { top: 16, right: 20, bottom: 36, left: 52 };
const CW = W - PAD.left - PAD.right;
const CH = H - PAD.top  - PAD.bottom;

function fmtErr(e) {
  if (!isFinite(e) || e === 0) return e === 0 ? "0" : "∞";
  const exp = Math.floor(Math.log10(e));
  const man = (e / Math.pow(10, exp)).toFixed(1);
  return man === "1.0" ? `1e${exp}` : `${man}e${exp}`;
}

// ── Component ─────────────────────────────────────────────────────────────────
export default function SinExplorer({ onLoadCalc }) {
  const data    = useMemo(buildData, []);
  const [hover, setHover] = useState(null);  // terms index

  const maxNodes = data[data.length - 1].emlN;  // EML at 20 terms
  const minNodes = 0;

  // Map terms → SVG x, node count → SVG y
  const toX = (t) => PAD.left + ((t - 2) / 18) * CW;
  const toY = (n) => PAD.top + CH - ((n - minNodes) / (maxNodes - minNodes)) * CH;

  // Build SVG path strings
  const bestPath = data.map((d, i) => `${i === 0 ? "M" : "L"}${toX(d.t)},${toY(d.bestN)}`).join(" ");
  const emlPath  = data.map((d, i) => `${i === 0 ? "M" : "L"}${toX(d.t)},${toY(d.emlN)}`).join(" ");

  // t=13 marker x position
  const t13x = toX(13);
  const t8x  = toX(8);

  return (
    <div style={{ color: C.text }}>
      {/* Header */}
      <div style={{ fontSize: 10, color: C.muted, marginBottom: 16, lineHeight: 1.8 }}>
        Node count vs Taylor terms for{" "}
        <span style={{ color: C.accent }}>sin(x)</span>. BEST routing uses{" "}
        <span style={{ color: C.accent }}>pow_exl</span> (3n per power) vs 15n in pure EML —
        a <span style={{ color: C.green }}>74% reduction</span> that holds at every term count.
        At 13 terms, BEST reaches machine precision (6.5 × 10⁻¹⁵).
      </div>

      {/* SVG chart */}
      <div style={{ background: C.surface, border: `1px solid ${C.border}`, borderRadius: 8, padding: 12, marginBottom: 16 }}>
        <svg viewBox={`0 0 ${W} ${H}`} width="100%" style={{ display: "block", maxWidth: W }}>
          {/* Grid lines (horizontal) */}
          {[0, 175, 350, 525, 700].map(n => {
            const y = toY(n);
            if (y < PAD.top || y > PAD.top + CH) return null;
            return (
              <g key={n}>
                <line x1={PAD.left} y1={y} x2={PAD.left + CW} y2={y}
                  stroke="#191b2e" strokeWidth={1} />
                <text x={PAD.left - 6} y={y} textAnchor="end" dominantBaseline="middle"
                  fontSize={8} fill={C.muted} fontFamily="'Space Mono',monospace">{n}</text>
              </g>
            );
          })}

          {/* X axis labels */}
          {[2, 4, 6, 8, 10, 12, 14, 16, 18, 20].map(t => (
            <text key={t} x={toX(t)} y={PAD.top + CH + 14} textAnchor="middle"
              fontSize={8} fill={C.muted} fontFamily="'Space Mono',monospace">{t}</text>
          ))}

          {/* Axis labels */}
          <text x={PAD.left - 38} y={PAD.top + CH / 2} textAnchor="middle"
            fontSize={8} fill={C.muted} fontFamily="'Space Mono',monospace"
            transform={`rotate(-90, ${PAD.left - 38}, ${PAD.top + CH / 2})`}>
            nodes
          </text>
          <text x={PAD.left + CW / 2} y={H - 4} textAnchor="middle"
            fontSize={8} fill={C.muted} fontFamily="'Space Mono',monospace">
            Taylor terms
          </text>

          {/* t=8 marker */}
          <line x1={t8x} y1={PAD.top} x2={t8x} y2={PAD.top + CH}
            stroke={C.accent + "44"} strokeWidth={1} strokeDasharray="3,3" />
          <text x={t8x + 3} y={PAD.top + 10} fontSize={7} fill={C.accent + "88"}
            fontFamily="'Space Mono',monospace">default</text>

          {/* t=13 marker (machine ε) */}
          <line x1={t13x} y1={PAD.top} x2={t13x} y2={PAD.top + CH}
            stroke={C.green + "66"} strokeWidth={1} strokeDasharray="3,3" />
          <text x={t13x + 3} y={PAD.top + 10} fontSize={7} fill={C.green + "aa"}
            fontFamily="'Space Mono',monospace">machine ε</text>

          {/* EML line (back) */}
          <path d={emlPath} fill="none" stroke={C.muted} strokeWidth={1.5} opacity={0.5} />

          {/* BEST line (front) */}
          <path d={bestPath} fill="none" stroke={C.accent} strokeWidth={2} />

          {/* Data point circles */}
          {data.map((d) => {
            const bx = toX(d.t), by = toY(d.bestN);
            const ex = toX(d.t), ey = toY(d.emlN);
            const isHover = hover === d.t;
            return (
              <g key={d.t}>
                {/* EML point */}
                <circle cx={ex} cy={ey} r={isHover ? 5 : 3} fill={C.muted}
                  style={{ cursor: "pointer" }}
                  onMouseEnter={() => setHover(d.t)}
                  onMouseLeave={() => setHover(null)}>
                  <title>EML · {d.t} terms · {d.emlN} nodes · err≈{fmtErr(d.maxErr)}</title>
                </circle>
                {/* BEST point */}
                <circle cx={bx} cy={by} r={isHover ? 5 : 3} fill={C.accent}
                  style={{ cursor: "pointer" }}
                  onMouseEnter={() => setHover(d.t)}
                  onMouseLeave={() => setHover(null)}>
                  <title>BEST · {d.t} terms · {d.bestN} nodes · err≈{fmtErr(d.maxErr)}</title>
                </circle>
              </g>
            );
          })}

          {/* Hover tooltip */}
          {hover !== null && (() => {
            const d = data.find(r => r.t === hover);
            if (!d) return null;
            const hx = toX(d.t);
            const boxX = hx > PAD.left + CW * 0.6 ? hx - 115 : hx + 10;
            return (
              <g>
                <rect x={boxX} y={PAD.top + 20} width={110} height={58}
                  fill={C.surface} stroke={C.border} rx={4} />
                <text x={boxX + 8} y={PAD.top + 34} fontSize={9} fill={C.accent}
                  fontFamily="'Space Mono',monospace">{d.t} terms</text>
                <text x={boxX + 8} y={PAD.top + 47} fontSize={8} fill={C.text}
                  fontFamily="'Space Mono',monospace">BEST: {d.bestN}n</text>
                <text x={boxX + 8} y={PAD.top + 58} fontSize={8} fill={C.muted}
                  fontFamily="'Space Mono',monospace">EML:  {d.emlN}n</text>
                <text x={boxX + 8} y={PAD.top + 69} fontSize={8} fill={C.green}
                  fontFamily="'Space Mono',monospace">err ≈ {fmtErr(d.maxErr)}</text>
              </g>
            );
          })()}
        </svg>

        {/* Legend */}
        <div style={{ display: "flex", gap: 16, marginTop: 6, paddingLeft: PAD.left }}>
          <span style={{ fontSize: 9, color: C.accent, display: "flex", alignItems: "center", gap: 5 }}>
            <span style={{ width: 16, height: 2, background: C.accent, display: "inline-block" }} />
            BEST (9×(t−1) nodes)
          </span>
          <span style={{ fontSize: 9, color: C.muted, display: "flex", alignItems: "center", gap: 5 }}>
            <span style={{ width: 16, height: 2, background: C.muted, display: "inline-block", opacity: 0.5 }} />
            Pure EML (35×(t−1) nodes)
          </span>
        </div>
      </div>

      {/* Table */}
      <div style={{ background: C.surface, border: `1px solid ${C.border}`, borderRadius: 8, overflow: "hidden" }}>
        <div style={{
          display: "grid", gridTemplateColumns: "0.5fr 0.8fr 0.8fr 0.7fr 1fr 0.7fr",
          padding: "7px 14px", borderBottom: `1px solid ${C.border}`,
          fontSize: 9, color: C.muted, letterSpacing: "0.06em", textTransform: "uppercase",
        }}>
          {["Terms", "BEST (n)", "EML (n)", "Saving", "Max error", ""].map((h, i) => (
            <div key={i}>{h}</div>
          ))}
        </div>

        {data.map((d, i) => {
          const saving = Math.round((1 - d.bestN / d.emlN) * 100);
          const isDefault = d.t === 8;
          const isMachine = d.t === 13;
          const rowBg = isDefault
            ? "rgba(232,160,32,0.06)"
            : isMachine
            ? "rgba(94,196,122,0.06)"
            : i % 2 === 0 ? "transparent" : "rgba(255,255,255,0.012)";

          return (
            <div key={d.t} style={{
              display: "grid", gridTemplateColumns: "0.5fr 0.8fr 0.8fr 0.7fr 1fr 0.7fr",
              padding: "7px 14px", fontSize: 11, alignItems: "center",
              borderBottom: i < data.length - 1 ? `1px solid ${C.border}` : "none",
              background: rowBg,
            }}>
              <div style={{ color: isDefault ? C.accent : isMachine ? C.green : C.muted }}>
                {d.t}{isDefault ? " ★" : isMachine ? " ε" : ""}
              </div>
              <div style={{ color: C.accent }}>{d.bestN}</div>
              <div style={{ color: C.muted }}>{d.emlN}</div>
              <div style={{ color: C.green }}>−{saving}%</div>
              <div style={{ color: d.maxErr < 1e-12 ? C.green : d.maxErr < 1e-6 ? C.blue : C.muted, fontSize: 10 }}>
                {fmtErr(d.maxErr)}
              </div>
              <div>
                <button
                  onClick={() => onLoadCalc("sin(x)")}
                  style={{
                    fontSize: 9, padding: "3px 8px",
                    background: "rgba(232,160,32,0.10)",
                    border: `1px solid ${C.accent}44`,
                    color: C.accent, borderRadius: 3, cursor: "pointer",
                  }}
                >
                  → Calc
                </button>
              </div>
            </div>
          );
        })}
      </div>

      <div style={{ marginTop: 8, fontSize: 9, color: C.muted, lineHeight: 1.7 }}>
        ★ = default term count in BestCalc · ε = machine precision reached (6.5 × 10⁻¹⁵)
      </div>
    </div>
  );
}
